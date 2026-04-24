"""sourced check — diagnose prereqs + ~/.claude/ health + project state."""
from __future__ import annotations
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..context import Context
from ..render import read_template
from ..ui import ok, err, bold, warn, should_color
from ..validators import iron_rules as iron_rules_validator
from ..validators import exemptions as exemptions_validator
from ..validators import invariants as invariants_validator


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Literal["pass", "fail", "warn"]
    detail: str | None = None


PREREQ_TOOLS = ["pdftotext", "pdfinfo", "pdftoppm", "pandoc", "python3"]
CLAUDE_HOME = Path.home() / ".claude"


def _check_pandoc_version() -> CheckResult:
    if shutil.which("pandoc") is None:
        return CheckResult("pandoc", "fail", "not on PATH")
    try:
        out = subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True, check=True, timeout=5
        ).stdout.splitlines()[0]
    except (subprocess.SubprocessError, OSError) as e:
        return CheckResult("pandoc", "fail", f"could not run pandoc --version: {e}")
    m = re.search(r"(\d+)\.(\d+)(?:\.\d+)?", out)
    if not m:
        return CheckResult("pandoc", "fail", f"unparseable version line: {out!r}")
    major, minor = int(m.group(1)), int(m.group(2))
    if (major, minor) < (3, 1):
        return CheckResult("pandoc", "fail", f"detected {major}.{minor}; need ≥ 3.1")
    return CheckResult("pandoc", "pass", f"{major}.{minor}")


def _check_simple_tool(name: str) -> CheckResult:
    if shutil.which(name) is None:
        return CheckResult(name, "fail", "not on PATH")
    return CheckResult(name, "pass")


def check_prereqs() -> list[CheckResult]:
    results = []
    for tool in PREREQ_TOOLS:
        if tool == "pandoc":
            results.append(_check_pandoc_version())
        else:
            results.append(_check_simple_tool(tool))
    return results


def check_claude_writable() -> list[CheckResult]:
    if not CLAUDE_HOME.exists():
        return [CheckResult("~/.claude/ writable", "fail", "directory does not exist")]
    if not os.access(CLAUDE_HOME, os.W_OK):
        return [CheckResult("~/.claude/ writable", "fail", "not writable")]
    return [CheckResult("~/.claude/ writable", "pass")]


def check_global_install() -> list[CheckResult]:
    results = []
    for sub in ("agents", "citations", "voice", "style", "skills", "filters"):
        d = CLAUDE_HOME / sub
        if d.is_dir():
            results.append(CheckResult(f"~/.claude/{sub}/", "pass"))
        else:
            results.append(CheckResult(f"~/.claude/{sub}/", "fail", "missing"))
    return results


def check_voice_iron_rules() -> list[CheckResult]:
    voice_dir = CLAUDE_HOME / "voice"
    if not voice_dir.is_dir():
        return []
    results = []
    try:
        claude_md = read_template("templates/CLAUDE.md")
    except FileNotFoundError:
        return [CheckResult("voice iron-rule check", "fail", "could not load CLAUDE.md template")]
    for vf in sorted(voice_dir.glob("*.md")):
        installed_text = vf.read_text(encoding="utf-8")
        try:
            skeleton_text = read_template(f"templates/voices/{vf.name}")
        except FileNotFoundError:
            # User-derived voice with no shipped skeleton → fall back to self-check.
            skeleton_text = installed_text
        ir_findings = iron_rules_validator.validate(
            skeleton=skeleton_text, candidate=installed_text, voice_name=vf.stem,
        )
        ex_findings = exemptions_validator.validate(
            voice=installed_text, claude_md=claude_md, voice_name=vf.stem,
        )
        all_findings = ir_findings + ex_findings
        if all_findings:
            results.append(CheckResult(
                f"voice/{vf.name}",
                "fail",
                f"{len(all_findings)} validation finding(s)",
            ))
        else:
            results.append(CheckResult(f"voice/{vf.name}", "pass"))
    return results


def check_conda_env_warning() -> list[CheckResult]:
    if os.environ.get("CONDA_PREFIX"):
        return [CheckResult(
            "conda environment",
            "warn",
            "CONDA_PREFIX is set; pipx may have used the wrong python interpreter. "
            "If sourced misbehaves, try `conda deactivate && pipx install --force ...`.",
        )]
    return []


def check_path_duplicates() -> list[CheckResult]:
    found = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(d) / "sourced"
        if candidate.exists():
            found.append(str(candidate))
    if len(found) > 1:
        return [CheckResult(
            "PATH duplicates",
            "warn",
            f"multiple `sourced` on PATH: {found}. The first listed wins.",
        )]
    return []


def _print_section(name: str, results: list[CheckResult], use_color: bool, verbose: int) -> None:
    failed = [r for r in results if r.status == "fail"]
    if not results:
        return
    pass_count = sum(1 for r in results if r.status == "pass")
    if verbose >= 1 or failed:
        print(bold(f"{name}:", use_color))
        for r in results:
            if r.status == "pass":
                marker = ok("✓", use_color)
            elif r.status == "warn":
                marker = warn("!", use_color)
            else:
                marker = err("✗", use_color)
            detail = f" — {r.detail}" if r.detail else ""
            if verbose >= 1 or r.status != "pass":
                print(f"  {marker} {r.name}{detail}")
    else:
        print(f"{bold(name + ':', use_color)} {pass_count}/{len(results)} passing")


def check_invariants() -> list[CheckResult]:
    """Run the manifest-structural invariants I1-I10 (I2 and I10 dormant until
    their prerequisites land; see validators/invariants.py module docstring).
    Each invariant surfaces as its own CheckResult row."""
    results = []
    for rule_id, findings in invariants_validator.run_all_invariants():
        if not findings:
            results.append(CheckResult(rule_id, "pass"))
            continue
        detail = "; ".join(
            f"[{f.location}] {f.message}" for f in findings
        )
        # Errors fail the check; warnings degrade to warn status.
        has_error = any(f.severity == "error" for f in findings)
        status: Literal["pass", "fail", "warn"] = "fail" if has_error else "warn"
        results.append(CheckResult(rule_id, status, detail))
    return results


def run(ctx: Context, project: str | None = None, invariants: bool = False) -> int:
    use_color = should_color(ctx.color, sys.stdout)

    if invariants:
        results = check_invariants()
        if not ctx.quiet:
            _print_section("Invariants (I1-I9, I10 dormant)", results, use_color, ctx.verbose)
            failed = [r for r in results if r.status == "fail"]
            passed = [r for r in results if r.status == "pass"]
            print(f"\n{len(failed)} failed, {len(passed)} passed.")
        return 4 if any(r.status == "fail" for r in results) else 0

    sections: list[tuple[str, list[CheckResult]]] = [
        ("Prerequisites", check_prereqs()),
        ("~/.claude/ writable", check_claude_writable()),
        ("Global install", check_global_install()),
        ("Voices", check_voice_iron_rules()),
    ]
    warnings = check_conda_env_warning() + check_path_duplicates()
    if warnings:
        sections.append(("Environment", warnings))

    all_results = [r for _, results in sections for r in results]
    failed = [r for r in all_results if r.status == "fail"]
    passed = [r for r in all_results if r.status == "pass"]

    if not ctx.quiet:
        for name, results in sections:
            _print_section(name, results, use_color, ctx.verbose)
        print(f"\n{len(failed)} failed, {len(passed)} passed.")

    return 4 if failed else 0
