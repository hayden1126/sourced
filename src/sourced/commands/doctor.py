"""sourced doctor — interactive deeper diagnostics for a broken setup.

Where `check` ships one-line surface warnings for CI / scripting, `doctor` is
the troubleshooting command: it deepens each surface warning into a specific,
actionable finding and prints the exact remediation command. It is strictly
read-only — it never mutates ~/.claude/, re-runs global-install, or deletes
anything. Every problem row carries a `Fix:` clause the user can copy-paste.

v1 scope (lean): prerequisites, ~/.claude/ health + wipe detection, the
editable-install stale-path check (issue #61's mechanism), conda poisoning, and
PATH shadowing. Orphan-file detection and stale-mirror content-diffing are the
deferred v2 follow-up; both need an ownership model to separate user-authored
voices/config from sourced-managed files, which lean v1 does not build.

Each problem row carries a structured `fix` (rendered on its own line), never a
mutation. Warnings are advisory (exit 0) unless the user passes --strict, which
escalates them to a hard failure for CI. Checks that verify nothing in this
environment (a wheel install, a harmless conda env) report `skip`, not `pass`.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

from ..context import Context
from ..ui import ok, should_color
from ._report import CheckResult, print_section
from . import check


EXPECTED_SUBDIRS = ("agents", "citations", "voice", "style", "skills", "filters")


def _claude_home() -> Path:
    return Path.home() / ".claude"


def check_claude_health(claude_home: Path | None = None) -> list[CheckResult]:
    """Deepen check's directory-presence test into wipe detection.

    check only flags a *missing* subdir. doctor also flags subdirs that exist
    but are empty (a partial install or an interrupted wipe recovery) and a
    missing sourced.config — the exact state the 2026-07-03 ~/.claude wipe left
    behind, which was reconstructed by hand for lack of a diagnostic naming it.
    """
    home = claude_home if claude_home is not None else _claude_home()
    if not home.exists():
        return [CheckResult(
            "~/.claude/", "fail",
            "does not exist; the global surface is missing",
            fix="sourced global-install",
        )]

    results: list[CheckResult] = []
    for sub in EXPECTED_SUBDIRS:
        d = home / sub
        if not d.is_dir():
            results.append(CheckResult(
                f"~/.claude/{sub}/", "fail", "missing",
                fix="sourced global-install",
            ))
        elif not any(d.iterdir()):
            results.append(CheckResult(
                f"~/.claude/{sub}/", "warn",
                "present but empty (partial install or interrupted wipe recovery)",
                fix="sourced global-install",
            ))
        else:
            results.append(CheckResult(f"~/.claude/{sub}/", "pass"))

    cfg = home / "sourced.config"
    if cfg.exists():
        results.append(CheckResult("sourced.config", "pass"))
    else:
        results.append(CheckResult(
            "sourced.config", "warn",
            f"user name unset (no {cfg})",
            fix="sourced global-install (prompts for it)",
        ))
    return results


def _cwd_checkout(cwd: Path) -> Path | None:
    """Nearest ancestor of cwd that looks like a sourced src-layout checkout."""
    for d in (cwd, *cwd.parents):
        if (d / ".git").exists() and (d / "src" / "sourced").is_dir():
            return d
    return None


def check_editable_install(pkg_dir: Path | None = None, cwd: Path | None = None) -> list[CheckResult]:
    """Detect a stale editable-install path (issue #61's mechanism).

    An editable install pins the `sourced` package to the checkout it was
    installed from via a .pth / finder. When that checkout is later moved, the
    pin points at the old path while the user works in the new one, so the
    running code and inspected sources diverge silently (the live symptom behind
    the spurious test_i10 failure noted in STATUS). This compares where the
    package actually loaded from against the checkout the user is standing in.
    """
    pkg = pkg_dir if pkg_dir is not None else Path(__file__).resolve().parents[1]
    if pkg.parent.name != "src":
        return [CheckResult(
            "editable install", "skip",
            "installed from a wheel / site-packages; no editable path to check",
        )]

    loaded_root = pkg.parent.parent
    here = cwd if cwd is not None else Path.cwd()
    cwd_checkout = _cwd_checkout(here)
    if cwd_checkout is None:
        return [CheckResult(
            "editable install", "skip",
            f"loads from {loaded_root}; not run from inside a checkout, nothing to compare",
        )]

    if cwd_checkout.resolve() != loaded_root.resolve():
        return [CheckResult(
            "editable install path", "warn",
            f"sourced imports from {loaded_root}, but you are in checkout {cwd_checkout}; "
            f"the editable .pth is stale",
            fix=f"pip install -e . from {cwd_checkout}, or run ~/hq/pending-cc-migration.sh",
        )]
    return [CheckResult("editable install path", "pass", f"current ({loaded_root})")]


def check_conda_poisoning(conda_prefix: str | None = None, executable: str | None = None) -> list[CheckResult]:
    """Deepen check's CONDA_PREFIX warning.

    check warns whenever CONDA_PREFIX is set, which over-fires: an active conda
    env is harmless unless the running sourced interpreter actually lives inside
    it (the pipx-under-conda case, where pipx grabbed the wrong python). This
    checks the interpreter's real location.
    """
    prefix = conda_prefix if conda_prefix is not None else os.environ.get("CONDA_PREFIX")
    exe = executable if executable is not None else sys.executable
    if not prefix:
        return []

    try:
        inside = Path(exe).resolve().is_relative_to(Path(prefix).resolve())
    except (ValueError, OSError):
        inside = False

    if inside:
        return [CheckResult(
            "conda environment", "warn",
            f"sourced runs under the conda interpreter at {exe} (inside CONDA_PREFIX={prefix}); "
            f"pipx likely used the wrong python",
            fix="conda deactivate && pipx install --force sourced",
        )]
    return [CheckResult(
        "conda environment", "skip",
        f"CONDA_PREFIX set but sourced runs from {exe}, outside it",
    )]


def check_path_shadowing(path_env: str | None = None) -> list[CheckResult]:
    """Deepen check's PATH-duplicate warning: name the winner and the shadowed."""
    raw = path_env if path_env is not None else os.environ.get("PATH", "")
    found: list[Path] = []
    for d in raw.split(os.pathsep):
        if not d:
            continue
        candidate = Path(d) / "sourced"
        if candidate.exists():
            found.append(candidate)
    if len(found) <= 1:
        return []

    winner = found[0]
    shadowed = [str(p) for p in found[1:]]
    return [CheckResult(
        "PATH duplicates", "warn",
        f"{len(found)} `sourced` on PATH; `{winner}` wins, shadowing {shadowed}",
        fix="remove the extra entry point(s) or reorder PATH",
    )]


def run(ctx: Context) -> int:
    use_color = should_color(ctx.color, sys.stdout)

    sections: list[tuple[str, list[CheckResult]]] = [
        ("Prerequisites", check.check_prereqs()),
        ("~/.claude/ writable", check.check_claude_writable()),
        ("~/.claude/ health", check_claude_health()),
        ("Editable install", check_editable_install()),
    ]
    hygiene = check_conda_poisoning() + check_path_shadowing()
    if hygiene:
        sections.append(("Environment", hygiene))

    all_results = [r for _, results in sections for r in results]
    failed = [r for r in all_results if r.status == "fail"]
    warned = [r for r in all_results if r.status == "warn"]
    passed = [r for r in all_results if r.status == "pass"]

    if not ctx.quiet:
        for name, results in sections:
            print_section(name, results, use_color, ctx.verbose)
        if failed or warned:
            print(f"\n{len(failed)} failed, {len(warned)} warnings, {len(passed)} passed.")
        else:
            print(f"\n{ok('No issues found.', use_color)} {len(passed)} checks passed.")

    # Warnings are advisory (exit 0); --strict escalates them to a hard failure,
    # reusing the same flag the install pipeline uses to promote warnings.
    return 4 if failed or (ctx.strict and warned) else 0
