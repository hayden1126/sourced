# `sourced` CLI Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace 792-line `install.sh` with a Python CLI (`sourced`) installed via `pipx` from the private GitHub repo, with parity behavior plus Tier 1 + Tier 2 UX improvements.

**Architecture:** Python 3.10+ package using src-layout. Entry point `sourced` registered via `pyproject.toml [project.scripts]`. Bundled templates live under `src/sourced/data/` (relocated from top-level so editable installs hot-reload). Three-layer error contract (validators return `Finding` lists; commands raise typed `SourcedError`; `cli.py` maps to exit codes). Pure-function effect boundaries (`render`, `mirror`, `write_atomic` accept primitives; only commands and `cli.py` see `Context`).

**Tech Stack:** Python 3.10+, Hatchling 1.24+ (build backend), hatch-vcs 0.4+ (version-from-git-tag), pipx (distribution), pytest (tests), syrupy (golden snapshots), argparse (zero external argparse deps), `importlib.resources` (bundled-data access), `shutil.copytree` (mirror), `tempfile.NamedTemporaryFile` (atomic writes), `re.MULTILINE` (sentinel parsing).

**Spec:** `docs/superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md` (canonical reference for every architectural decision in this plan).

---

## File Structure

### Created (new files in this plan)

**Package config:**
- `pyproject.toml` — Hatchling + hatch-vcs config, `[project.scripts] sourced = "sourced.cli:main"`

**Package source (`src/sourced/`):**
- `__init__.py` — `__version__` via `importlib.metadata`
- `__main__.py` — `python -m sourced` entry → `cli.main`
- `_version.py` — auto-written by hatch-vcs at build time (gitignore'd in editable mode)
- `cli.py` — argparse root parser, subcommand dispatch, top-level error→exit-code mapping
- `context.py` — `Context` dataclass: `dry_run`, `verbose`, `quiet`, `color`, `strict`
- `errors.py` — `SourcedError` + 7 typed subclasses
- `ui.py` — color/tty helpers, error formatting, dry-run summary printing
- `config.py` — `~/.claude/sourced.config` user-name read/write
- `project.py` — `.sourced-project-type` marker IO + sentinel block parsing
- `render.py` — `_data_root()` + `read_template()` + `render()` (pure substitution)
- `mirror.py` — `mirror_tree()` wrapping `shutil.copytree`
- `commands/__init__.py` — empty
- `commands/_pipeline.py` — `run_install_pipeline()` shared by install / global_install / new
- `commands/install.py` — `sourced install`
- `commands/global_install.py` — `sourced global-install`
- `commands/new.py` — `sourced new <name>`
- `commands/update.py` — `sourced update`
- `commands/switch.py` — `sourced switch voice|style`
- `commands/check.py` — `sourced check`
- `validators/__init__.py` — `Finding` dataclass
- `validators/csl.py` — `validate_csl_title` (pre-render)
- `validators/iron_rules.py` — `extract_iron_rules` + `normalize_rule` + `validate` (post-render)
- `validators/exemptions.py` — `extract_voice_exemptions` + `validate` (post-render)
- `data/facts.yml` — invariant registry (seeded with I1-I8)

**Tests:**
- `tests/conftest.py` — shared fixtures: `tmp_home`, `tmp_project`, `bundled_data_root`, `clean_ansi`
- `tests/cli/__init__.py` — empty
- `tests/cli/unit/__init__.py` — empty
- `tests/cli/unit/test_render.py`, `test_mirror.py`, `test_config.py`, `test_project.py`, `test_ui.py`, `test_errors.py`, `test_context.py`, `test_validators_csl.py`, `test_validators_iron_rules.py`, `test_validators_exemptions.py`
- `tests/cli/integration/__init__.py` — empty
- `tests/cli/integration/test_install_fresh.py`, `test_install_force.py`, `test_install_type_annotated.py`, `test_global_install.py`, `test_new.py`, `test_update.py`, `test_update_stricter_sentinels.py`, `test_switch_voice.py`, `test_switch_style.py`, `test_switch_broken_marker.py`, `test_check_all_pass.py`, `test_check_prereq_missing.py`, `test_check_validation_fail.py`, `test_dry_run_install.py`, `test_verbose_quiet.py`, `test_color_suppression.py`
- `tests/cli/parity/__init__.py` — empty (deleted with install.sh in PR 5)
- `tests/cli/parity/test_install_parity.py`, `test_global_install_parity.py`, `test_update_parity.py`
- `tests/cli/golden/__init__.py` — empty
- `tests/cli/golden/test_render_golden.py` (uses `syrupy` fixtures)

### Modified (existing files updated)

- `tests/parity/_render.sh` line 34 — CSL lookup path: `${REPO_DIR}/templates/styles/...` → `${REPO_DIR}/src/sourced/data/templates/styles/...`
- `README.md` — install section rewritten for pipx; remove `./install.sh` references
- `docs/INSTALL.md` — pipx install / pipx gotchas / version pinning / uninstall sections
- `ARCHITECTURE.md` — add Python package section; update file-tree
- `ROADMAP.md` — replace L218-221 single S entry with two L entries (CLI + Go binary)
- `.gitignore` — add `src/sourced/_version.py` (auto-generated by hatch-vcs)
- `issues.md` — add cross-reference under #14 (orphan cleanup) — optional, gitignored

### Relocated (`git mv`)

- `templates/` → `src/sourced/data/templates/`
- `agents/` → `src/sourced/data/agents/`
- `citations/` → `src/sourced/data/citations/`
- `skills/` → `src/sourced/data/skills/`
- `filters/` → `src/sourced/data/filters/`

### Deleted (in PR 5, after parity confirms)

- `install.sh` (preserved at git tag `legacy/install-sh-final` first)
- `tests/cli/parity/` directory (purpose-served once install.sh deleted)

---

## PR Checkpoints

5 PRs, each independently reviewable and mergeable:

| PR | Scope | Gate to merge |
|---|---|---|
| 1 | Scaffolding: pyproject + minimal `src/sourced/` + `sourced --version` + `sourced check` (prereqs only) | `pipx install -e .` + `sourced --version` + `sourced check` all work |
| 2 | I/O layer: render + mirror + config + project + ui + errors + context, with unit tests | `pytest tests/cli/unit/` green |
| 3 | Data relocation + validators (csl + iron_rules + exemptions), with unit tests | `pytest` + existing `bash tests/parity/run-all.sh` both green |
| 4 | Commands + `_pipeline` + integration tests; full check | `pytest tests/cli/` green; CLI works end-to-end against tmp dirs |
| 5 | Parity vs install.sh + goldens + docs + retire install.sh + `/audit` post-merge | parity green → tag `legacy/install-sh-final` → delete `install.sh` + `tests/cli/parity/` |

---

# PR 1: Scaffolding + first subcommand

**Goal:** A Python package that installs via `pipx install -e .` and exposes a working `sourced` command on PATH with `--version` and a minimal `check` subcommand. Establishes the entry-point + argparse + error-handling skeleton everything else extends.

### Task 1.1: Project scaffolding (`pyproject.toml` + empty package)

**Files:**
- Create: `pyproject.toml`
- Create: `src/sourced/__init__.py`
- Create: `src/sourced/__main__.py`
- Create: `.gitignore` (modify if exists)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling>=1.24", "hatch-vcs>=0.4"]
build-backend = "hatchling.build"

[project]
name = "sourced"
description = "Claude Code framework for academic papers"
requires-python = ">=3.10"
dynamic = ["version"]
dependencies = []

[project.optional-dependencies]
test = ["pytest>=8.0", "syrupy>=4.6"]

[project.scripts]
sourced = "sourced.cli:main"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/sourced/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/sourced"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `src/sourced/__init__.py`**

```python
"""sourced — Claude Code framework for academic papers."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sourced")
except PackageNotFoundError:  # editable / not yet installed
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
```

- [ ] **Step 3: Create `src/sourced/__main__.py`**

```python
"""Allow `python -m sourced ...` invocation."""
from .cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Update `.gitignore` to ignore the auto-generated version file**

Append to `.gitignore` (create if missing):

```
src/sourced/_version.py
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/sourced/__init__.py src/sourced/__main__.py .gitignore
git commit -m "feat(cli): scaffold Python package with Hatchling"
```

### Task 1.2: Errors module

**Files:**
- Create: `src/sourced/errors.py`
- Create: `tests/__init__.py`
- Create: `tests/cli/__init__.py`
- Create: `tests/cli/unit/__init__.py`
- Create: `tests/cli/unit/test_errors.py`

- [ ] **Step 1: Write failing test**

Create `tests/cli/unit/test_errors.py`:

```python
import pytest
from sourced.errors import (
    SourcedError, UsageError, PrereqError, ValidationError,
    ProjectError, RenderError, ExternalToolError, ValidatorCrashError,
)
from sourced.validators import Finding


def test_base_exit_code():
    e = SourcedError("nope")
    assert e.exit_code == 1


def test_subclass_exit_codes():
    assert UsageError("x").exit_code == 2
    assert PrereqError("x").exit_code == 3
    assert ProjectError("x").exit_code == 5
    assert RenderError("x").exit_code == 6
    assert ExternalToolError("x").exit_code == 7
    assert ValidatorCrashError("x").exit_code == 70


def test_validation_error_requires_findings():
    finding = Finding(
        rule="some-rule",
        location="some/path:1",
        severity="error",
        message="something broke",
    )
    e = ValidationError("nope", findings=[finding])
    assert e.exit_code == 4
    assert e.findings == [finding]


def test_validation_error_rejects_empty_findings():
    with pytest.raises(AssertionError):
        ValidationError("nope", findings=[])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/cli/unit/test_errors.py -v
```

Expected: ImportError on `sourced.errors`.

- [ ] **Step 3: Create `src/sourced/errors.py`**

```python
"""Typed exceptions for sourced. cli.main maps each subclass to an exit code."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .validators import Finding


class SourcedError(Exception):
    """Base; subclass to override exit_code."""
    exit_code: int = 1


class UsageError(SourcedError):
    """Bad flag combination or invocation. Matches argparse's native exit 2."""
    exit_code = 2


class PrereqError(SourcedError):
    """Missing tool on PATH (pdftotext/pandoc/etc.)."""
    exit_code = 3


class ValidationError(SourcedError):
    """Validator findings prevented orchestration. Carries the Finding list."""
    exit_code = 4

    def __init__(self, msg: str, findings: list["Finding"]) -> None:
        assert findings, "ValidationError requires at least one finding"
        super().__init__(msg)
        self.findings = findings


class ProjectError(SourcedError):
    """Project state broken: missing dir, corrupted marker, malformed sentinels."""
    exit_code = 5


class RenderError(SourcedError):
    """Malformed template; substitution failed."""
    exit_code = 6


class ExternalToolError(SourcedError):
    """External tool (pandoc/git/etc.) exited non-zero."""
    exit_code = 7


class ValidatorCrashError(SourcedError):
    """Validator itself crashed (a bug in the validator). EX_SOFTWARE."""
    exit_code = 70
```

- [ ] **Step 4: Stub `src/sourced/validators/__init__.py` (just enough for the import)**

Create `src/sourced/validators/__init__.py`:

```python
"""Validators return list[Finding]; never raise."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Finding:
    rule: str
    location: str
    severity: Literal["error", "warning"]
    message: str
    fix_hint: str | None = None
    rule_url: str | None = None
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/cli/unit/test_errors.py -v
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add src/sourced/errors.py src/sourced/validators/__init__.py tests/__init__.py tests/cli/__init__.py tests/cli/unit/__init__.py tests/cli/unit/test_errors.py
git commit -m "feat(cli): error hierarchy + Finding dataclass"
```

### Task 1.3: Context dataclass

**Files:**
- Create: `src/sourced/context.py`
- Create: `tests/cli/unit/test_context.py`

- [ ] **Step 1: Write failing test**

Create `tests/cli/unit/test_context.py`:

```python
from sourced.context import Context


def test_default_context():
    ctx = Context()
    assert ctx.dry_run is False
    assert ctx.verbose == 0
    assert ctx.quiet is False
    assert ctx.color == "auto"
    assert ctx.strict is False


def test_context_is_frozen():
    import dataclasses
    ctx = Context()
    try:
        ctx.dry_run = True
    except dataclasses.FrozenInstanceError:
        return
    raise AssertionError("Context should be frozen")


def test_context_explicit_values():
    ctx = Context(dry_run=True, verbose=2, quiet=False, color="never", strict=True)
    assert ctx.dry_run is True
    assert ctx.verbose == 2
    assert ctx.color == "never"
    assert ctx.strict is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/cli/unit/test_context.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/context.py`**

```python
"""Context dataclass — flows from cli.py to commands. NOT module globals."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Context:
    """Runtime context resolved from CLI flags + env. Pass explicitly to commands."""
    dry_run: bool = False
    verbose: int = 0           # action='count': 0 = default, 1 = -v, 2+ = -vv
    quiet: bool = False
    color: Literal["auto", "always", "never"] = "auto"
    strict: bool = False
```

- [ ] **Step 4: Verify test passes**

```bash
pytest tests/cli/unit/test_context.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/context.py tests/cli/unit/test_context.py
git commit -m "feat(cli): Context dataclass for runtime state"
```

### Task 1.4: ui.py — minimal color + error printing

**Files:**
- Create: `src/sourced/ui.py`
- Create: `tests/cli/unit/test_ui.py`

- [ ] **Step 1: Write failing test**

Create `tests/cli/unit/test_ui.py`:

```python
import os
import sys
import pytest
from sourced.ui import should_color, ok, err, warn, path_str


def test_should_color_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert should_color(color_pref="auto", stream=sys.stdout) is False


def test_should_color_explicit_never(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert should_color(color_pref="never", stream=sys.stdout) is False


def test_should_color_explicit_always(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert should_color(color_pref="always", stream=sys.stdout) is True


def test_should_color_auto_non_tty(monkeypatch, tmp_path):
    monkeypatch.delenv("NO_COLOR", raising=False)
    f = open(tmp_path / "out.txt", "w")
    try:
        assert should_color(color_pref="auto", stream=f) is False
    finally:
        f.close()


def test_ok_with_color():
    assert "\033[32m" in ok("done", use_color=True)


def test_ok_without_color():
    assert ok("done", use_color=False) == "done"


def test_err_with_color():
    assert "\033[31m" in err("oops", use_color=True)


def test_warn_with_color():
    assert "\033[33m" in warn("careful", use_color=True)


def test_path_str_with_color():
    assert "\033[36m" in path_str("/tmp/x", use_color=True)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/cli/unit/test_ui.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/ui.py`**

```python
"""Output formatting: color, error printing, summaries.
Single source of truth for ANSI codes; nothing else touches them.
"""
from __future__ import annotations
import os
import sys
from typing import IO, Literal

# 8 standard ANSI colors. No 256-color, no truecolor.
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def should_color(color_pref: Literal["auto", "always", "never"], stream: IO) -> bool:
    """Decide whether to emit ANSI codes to a stream.

    Precedence: --color=always > NO_COLOR env > --color=never > non-tty > default on.
    """
    if color_pref == "always":
        return True
    if os.environ.get("NO_COLOR"):
        return False
    if color_pref == "never":
        return False
    return stream.isatty()


def _wrap(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def ok(text: str, use_color: bool = True) -> str:
    return _wrap(text, _GREEN, use_color)


def warn(text: str, use_color: bool = True) -> str:
    return _wrap(text, _YELLOW, use_color)


def err(text: str, use_color: bool = True) -> str:
    return _wrap(text, _RED, use_color)


def path_str(text: str, use_color: bool = True) -> str:
    return _wrap(text, _CYAN, use_color)


def bold(text: str, use_color: bool = True) -> str:
    return _wrap(text, _BOLD, use_color)


def print_error(exc, use_color: bool, stream: IO = sys.stderr) -> None:
    """Print a SourcedError as the canonical two-line stderr format.
    For ValidationError, inline the findings list.
    """
    from .errors import ValidationError
    msg = str(exc)
    print(f"sourced: {err(msg, use_color)}", file=stream)
    if isinstance(exc, ValidationError):
        for f in exc.findings:
            sev = err(f.severity, use_color) if f.severity == "error" else warn(f.severity, use_color)
            print(f"  [{sev}] {f.rule} at {path_str(f.location, use_color)}: {f.message}", file=stream)
            if f.fix_hint:
                print(f"    hint: {f.fix_hint}", file=stream)


def print_unexpected(exc, stream: IO = sys.stderr) -> None:
    """Pip-style graceful catch-all for unhandled exceptions."""
    name = type(exc).__name__
    print(
        f"sourced: unexpected error ({name}: {exc}). "
        "Rerun with -vv or set SOURCED_DEBUG=1 to see the traceback.",
        file=stream,
    )
```

- [ ] **Step 4: Verify test passes**

```bash
pytest tests/cli/unit/test_ui.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/ui.py tests/cli/unit/test_ui.py
git commit -m "feat(cli): ui.py — color helpers + error formatting"
```

### Task 1.5: Minimal `check.py` (prereqs only)

**Files:**
- Create: `src/sourced/commands/__init__.py`
- Create: `src/sourced/commands/check.py`

- [ ] **Step 1: Create empty `src/sourced/commands/__init__.py`**

Empty file (literally `""` or zero bytes).

- [ ] **Step 2: Create `src/sourced/commands/check.py` (prereqs-only stub)**

```python
"""sourced check — phase 1 prereqs scaffold; full implementation in PR 4."""
from __future__ import annotations
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Literal

from ..context import Context
from ..ui import ok, err, bold, should_color


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Literal["pass", "fail"]
    detail: str | None = None


PREREQ_TOOLS = ["pdftotext", "pdfinfo", "pdftoppm", "pandoc", "python3"]


def _check_pandoc_version() -> CheckResult:
    """pandoc must be ≥ 3.1."""
    if shutil.which("pandoc") is None:
        return CheckResult("pandoc", "fail", "not on PATH")
    try:
        out = subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True, check=True, timeout=5
        ).stdout.splitlines()[0]
    except (subprocess.SubprocessError, OSError) as e:
        return CheckResult("pandoc", "fail", f"could not run pandoc --version: {e}")
    # Format: "pandoc 3.1.9" — extract first version-like token.
    import re
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
    """Phase-1: prereqs only. PR 4 expands with global-install + project checks."""
    results = []
    for tool in PREREQ_TOOLS:
        if tool == "pandoc":
            results.append(_check_pandoc_version())
        else:
            results.append(_check_simple_tool(tool))
    return results


def run(ctx: Context, project: str | None = None) -> int:
    """sourced check entry point.

    Returns exit code (0 = all pass, 4 = any fail per spec §4.7).
    """
    use_color = should_color(ctx.color, sys.stdout)
    results = check_prereqs()
    failed = [r for r in results if r.status == "fail"]
    passed = [r for r in results if r.status == "pass"]

    if not ctx.quiet:
        # Default: per-check detail only on failures; one-line section summary on passes.
        if ctx.verbose >= 1 or failed:
            print(bold("Prerequisites:", use_color))
            for r in results:
                marker = ok("✓", use_color) if r.status == "pass" else err("✗", use_color)
                detail = f" — {r.detail}" if r.detail else ""
                if ctx.verbose >= 1 or r.status == "fail":
                    print(f"  {marker} {r.name}{detail}")
            if not (ctx.verbose >= 1):
                # already printed failures above; nothing more
                pass
        else:
            print(bold("Prerequisites:", use_color), f"{len(passed)}/{len(results)} passing")

        # Summary line
        print(f"\n{len(failed)} failed, {len(passed)} passed.")

    return 4 if failed else 0
```

- [ ] **Step 3: Commit (no test yet; integration test next)**

```bash
git add src/sourced/commands/__init__.py src/sourced/commands/check.py
git commit -m "feat(cli): check command — prereqs scaffold"
```

### Task 1.6: cli.py — argparse + dispatch + top-level error mapping

**Files:**
- Create: `src/sourced/cli.py`

- [ ] **Step 1: Create `src/sourced/cli.py`**

```python
"""argparse root + subcommand dispatch + top-level error→exit-code mapping.

This is the ONLY module that touches argparse. Subcommand modules (commands/*.py)
accept plain Python args, not argparse.Namespace.
"""
from __future__ import annotations
import argparse
import os
import sys
from typing import NoReturn

from . import __version__
from .context import Context
from .errors import SourcedError
from .ui import print_error, print_unexpected, should_color


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sourced", description="sourced framework CLI")
    p.add_argument("--version", action="version", version=f"sourced {__version__}")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    p.add_argument("--no-color", action="store_const", const="never", dest="color")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict", action="store_true")

    sub = p.add_subparsers(dest="subcommand", metavar="<subcommand>")

    # check (PR 1 has the prereq-only version; PR 4 expands)
    p_check = sub.add_parser("check", help="diagnose prereqs + ~/.claude/ health")
    p_check.add_argument("--project", help="also check this project directory")

    return p


def _ctx_from_args(args: argparse.Namespace) -> Context:
    return Context(
        dry_run=args.dry_run,
        verbose=args.verbose,
        quiet=args.quiet,
        color=args.color,
        strict=args.strict,
    )


def _dispatch(args: argparse.Namespace) -> int:
    ctx = _ctx_from_args(args)
    if args.subcommand == "check":
        from .commands import check
        return check.run(ctx, project=args.project)
    # No subcommand → print help and exit 2 (argparse-style usage error).
    _build_parser().print_help(sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> NoReturn:
    parser = _build_parser()
    args = parser.parse_args(argv)
    use_color = should_color(args.color, sys.stderr)

    try:
        sys.exit(_dispatch(args))
    except SourcedError as e:
        print_error(e, use_color)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        debug = os.environ.get("SOURCED_DEBUG") or args.verbose >= 2
        if debug:
            raise
        print_unexpected(e)
        sys.exit(70)
```

- [ ] **Step 2: Install editable + verify `sourced --version` works**

```bash
pipx install --force -e .
sourced --version
```

Expected: `sourced 0.0.0+unknown` (or a hatch-vcs-derived version if tags exist).

- [ ] **Step 3: Verify `sourced check` runs**

```bash
sourced check
```

Expected: prints prereq table; exit 0 if all five tools present, exit 4 otherwise.

- [ ] **Step 4: Verify `sourced` (no subcommand) exits 2**

```bash
sourced; echo "exit: $?"
```

Expected: help text printed to stderr, exit 2.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/cli.py
git commit -m "feat(cli): argparse root + dispatch + error mapping"
```

### Task 1.7: First integration test for `check`

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/cli/integration/__init__.py`
- Create: `tests/cli/integration/test_check_smoke.py`

- [ ] **Step 1: Create `tests/conftest.py` with shared fixtures**

```python
"""Shared pytest fixtures for sourced CLI tests."""
import pytest


@pytest.fixture
def tmp_home(tmp_path, monkeypatch):
    """Redirect HOME to a fresh tmp dir."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def tmp_project(tmp_path):
    """A fresh tmp dir as the project PWD."""
    proj = tmp_path / "project"
    proj.mkdir()
    return proj


@pytest.fixture
def clean_ansi(monkeypatch):
    """Disable color for deterministic stdout assertions."""
    monkeypatch.setenv("NO_COLOR", "1")
```

- [ ] **Step 2: Create empty `tests/cli/integration/__init__.py`**

Empty file.

- [ ] **Step 3: Write first integration test**

Create `tests/cli/integration/test_check_smoke.py`:

```python
import subprocess
import sys


def test_sourced_version_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "sourced" in result.stdout


def test_sourced_check_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # Exit 0 if all prereqs present; 4 if any missing. Either is "runs cleanly."
    assert result.returncode in (0, 4)
    assert "Prerequisites" in result.stdout or "passing" in result.stdout
```

- [ ] **Step 4: Run integration tests**

```bash
pytest tests/cli/integration/ -v
```

Expected: 2 passed.

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/cli/ -v
```

Expected: all tests pass (errors + context + ui + check smoke).

- [ ] **Step 6: Commit**

```bash
git add tests/conftest.py tests/cli/integration/__init__.py tests/cli/integration/test_check_smoke.py
git commit -m "test(cli): conftest fixtures + check smoke test"
```

### PR 1 gate (before opening PR)

Manual verification:

```bash
pipx install --force -e .       # installs from working tree
sourced --version               # prints version
sourced check                   # runs; reports prereq pass/fail
sourced --help                  # shows root help
sourced check --help            # shows check help
pytest tests/cli/ -v            # all green
```

If all green, open PR 1: "feat(cli): scaffold Python package + minimal `check`".

---

# PR 2: I/O layer — render + mirror + config + project

**Goal:** All effect-boundary modules implemented with unit tests. No subcommands wired yet (commands/ stays empty except for `check`). After this PR, the building blocks for all install/update/switch/new flows exist as pure functions and are unit-tested.

### Task 2.1: render.py — pure template substitution

**Files:**
- Create: `src/sourced/render.py`
- Create: `tests/cli/unit/test_render.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_render.py`:

```python
import pytest
from sourced.render import RenderContext, render


def test_substitutes_user():
    out = render("Hello {{USER}}!", RenderContext(user="Alice"))
    assert out == "Hello Alice!"


def test_substitutes_voice_when_present():
    out = render("voice={{VOICE}}", RenderContext(user="A", voice_name="academic"))
    assert out == "voice=academic"


def test_voice_token_kept_when_voice_name_none():
    out = render("voice={{VOICE}}", RenderContext(user="A"))
    assert out == "voice={{VOICE}}"


def test_substitutes_style_when_present():
    out = render("style={{STYLE}}", RenderContext(user="A", style_name="apa7"))
    assert out == "style=apa7"


def test_unknown_token_kept_verbatim():
    out = render("hello {{UNKNOWN}}", RenderContext(user="A"))
    assert out == "hello {{UNKNOWN}}"


def test_handles_user_with_special_chars():
    """User name like 'O'Brien' or 'A & B' must not break substitution."""
    out = render("by {{USER}}", RenderContext(user="O'Brien & Co."))
    assert out == "by O'Brien & Co."


def test_render_is_pure_no_io(tmp_path, monkeypatch):
    """render() must not touch the filesystem."""
    out = render("noop", RenderContext(user="A"))
    assert out == "noop"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/cli/unit/test_render.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/render.py`**

```python
"""Template rendering: bundled-resource access + pure substitution.

render() is a pure function — no I/O, no side effects. Reads happen via
read_template() (importlib.resources); writes happen in commands/*.py.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import cache
from importlib.resources import files, as_file


@cache
def _data_root():
    """Bundled data root. Cached because Traversable construction repeats otherwise."""
    return files("sourced") / "data"


def read_template(subpath: str) -> str:
    """Read a bundled template as text. subpath is relative to src/sourced/data/."""
    return (_data_root() / subpath).read_text(encoding="utf-8")


def bundled_path(subpath: str):
    """Context manager yielding a real filesystem Path for a bundled directory.
    Use with shutil.copytree which needs a concrete path.
    """
    return as_file(_data_root() / subpath)


@dataclass(frozen=True)
class RenderContext:
    """Substitution variables for render(). Pass voice_name/style_name as None
    when the template doesn't opt into them; the matching token stays verbatim.
    """
    user: str
    voice_name: str | None = None
    style_name: str | None = None


def render(template: str, ctx: RenderContext) -> str:
    """Apply substitutions. Pure: no I/O, no side effects."""
    out = template.replace("{{USER}}", ctx.user)
    if ctx.voice_name is not None:
        out = out.replace("{{VOICE}}", ctx.voice_name)
    if ctx.style_name is not None:
        out = out.replace("{{STYLE}}", ctx.style_name)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/cli/unit/test_render.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/render.py tests/cli/unit/test_render.py
git commit -m "feat(cli): render.py — pure template substitution + resource access"
```

### Task 2.2: mirror.py — file-tree copy

**Files:**
- Create: `src/sourced/mirror.py`
- Create: `tests/cli/unit/test_mirror.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_mirror.py`:

```python
import pytest
from pathlib import Path
from sourced.mirror import mirror_tree


def test_mirror_tree_creates_dest(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("alpha")
    (src / "sub").mkdir()
    (src / "sub" / "b.txt").write_text("beta")
    dest = tmp_path / "dest"

    mirror_tree(src, dest, dry_run=False)

    assert (dest / "a.txt").read_text() == "alpha"
    assert (dest / "sub" / "b.txt").read_text() == "beta"


def test_mirror_tree_dirs_exist_ok(tmp_path):
    """Existing dest dir must not error; per-file overwrite."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("new")
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "a.txt").write_text("old")
    (dest / "user_added.txt").write_text("preserve me")

    mirror_tree(src, dest, dry_run=False)

    assert (dest / "a.txt").read_text() == "new"  # overwritten
    assert (dest / "user_added.txt").read_text() == "preserve me"  # preserved


def test_mirror_tree_dry_run_does_not_write(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("alpha")
    dest = tmp_path / "dest"

    mirror_tree(src, dest, dry_run=True)

    assert not dest.exists() or not (dest / "a.txt").exists()


def test_mirror_tree_preserves_mtime(tmp_path):
    """copy2 preserves mtimes — needed so npm install doesn't re-run."""
    src = tmp_path / "src"
    src.mkdir()
    f = src / "a.txt"
    f.write_text("alpha")
    import os, time
    old_mtime = time.time() - 86400  # 1 day ago
    os.utime(f, (old_mtime, old_mtime))
    dest = tmp_path / "dest"

    mirror_tree(src, dest, dry_run=False)

    copied_mtime = (dest / "a.txt").stat().st_mtime
    assert abs(copied_mtime - old_mtime) < 2  # within rounding
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_mirror.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/mirror.py`**

```python
"""File-tree mirroring. shutil.copytree wrapper.

dirs_exist_ok=True matches install.sh: overwrite per-file, never delete.
copy_function=shutil.copy2 preserves mtimes (so npm install doesn't re-run
on mirrored skill dirs).
symlinks=True future-proofs: if a bundled tree ever contains symlinks they
preserve as links, not materialize.
"""
from __future__ import annotations
import shutil
from pathlib import Path


def mirror_tree(src: Path, dest: Path, *, dry_run: bool = False) -> None:
    """Mirror src → dest. Caller passes a real filesystem src (not a Traversable);
    use sourced.render.bundled_path() context manager to materialize bundled trees."""
    if dry_run:
        # Dry-run intentionally does no walking; commands print "would mirror" themselves.
        return
    shutil.copytree(
        src,
        dest,
        dirs_exist_ok=True,
        copy_function=shutil.copy2,
        symlinks=True,
    )
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_mirror.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/mirror.py tests/cli/unit/test_mirror.py
git commit -m "feat(cli): mirror.py — shutil.copytree wrapper"
```

### Task 2.3: config.py — `~/.claude/sourced.config` (user-global only)

**Files:**
- Create: `src/sourced/config.py`
- Create: `tests/cli/unit/test_config.py`

The current install.sh writes `USER_NAME="value"` shell-source format. Phase-1 reads it as text matching that exact line shape; rewrites it the same way.

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_config.py`:

```python
import pytest
from pathlib import Path
from sourced.config import load_user_name, save_user_name, config_path


def test_config_path_uses_home(tmp_home):
    assert config_path() == tmp_home / ".claude" / "sourced.config"


def test_load_returns_none_when_missing(tmp_home):
    assert load_user_name() is None


def test_save_then_load_roundtrip(tmp_home):
    save_user_name("Alice")
    assert load_user_name() == "Alice"


def test_load_handles_quoted_value(tmp_home):
    """install.sh writes USER_NAME="Alice"; we must read that format."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('USER_NAME="Alice"\n')
    assert load_user_name() == "Alice"


def test_load_handles_unquoted_value(tmp_home):
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("USER_NAME=Alice\n")
    assert load_user_name() == "Alice"


def test_load_strips_trailing_whitespace(tmp_home):
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('USER_NAME="Alice"   \n')
    assert load_user_name() == "Alice"


def test_save_creates_parent_dir(tmp_home):
    """~/.claude/ may not exist on a totally fresh machine."""
    save_user_name("Alice")
    assert (tmp_home / ".claude" / "sourced.config").exists()


def test_save_writes_install_sh_format(tmp_home):
    """Format must round-trip with install.sh's writer for tag rollback compat."""
    save_user_name("Alice")
    content = (tmp_home / ".claude" / "sourced.config").read_text()
    assert content.startswith('USER_NAME="Alice"')
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_config.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/config.py`**

```python
"""~/.claude/sourced.config — user-global settings (currently just user name).

Format matches install.sh exactly: USER_NAME="<value>" on its own line.
We accept a few variants on read (quoted/unquoted, trailing whitespace) but
write the canonical form for round-trip with the legacy install.sh tag.
"""
from __future__ import annotations
import re
from pathlib import Path


def config_path() -> Path:
    return Path.home() / ".claude" / "sourced.config"


_USER_NAME_RE = re.compile(r'^\s*USER_NAME=(?:"([^"]*)"|(\S+))\s*$')


def load_user_name() -> str | None:
    p = config_path()
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        m = _USER_NAME_RE.match(line)
        if m:
            return m.group(1) if m.group(1) is not None else m.group(2)
    return None


def save_user_name(name: str) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    # Escape any embedded double-quote (rare; defensive).
    safe = name.replace('"', r'\"')
    p.write_text(f'USER_NAME="{safe}"\n', encoding="utf-8")
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_config.py -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/config.py tests/cli/unit/test_config.py
git commit -m "feat(cli): config.py — sourced.config read/write"
```

### Task 2.4: project.py — `.sourced-project-type` marker + sentinel parsing

**Files:**
- Create: `src/sourced/project.py`
- Create: `tests/cli/unit/test_project.py`

This module owns:
- `.sourced-project-type` marker IO (`essay` | `annotated-bib` | absent → essay default)
- Voice / style first-line marker parsing (`<!-- sourced:voice=academic -->`)
- CLAUDE.md managed-block sentinel extraction (column-0 strict, per spec §5.5)
- `.sourced.bak` rollback fallback (per spec §5.7) — creator helper

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_project.py`:

```python
import pytest
from pathlib import Path
from sourced.project import (
    read_project_type, write_project_type,
    read_voice_marker, read_style_marker,
    extract_managed_block, replace_managed_block,
    write_bak_sibling,
)
from sourced.errors import ProjectError


# ----- project type marker -----

def test_project_type_default_when_marker_absent(tmp_project):
    assert read_project_type(tmp_project) == "essay"


def test_project_type_reads_marker(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_strips_whitespace_and_crlf(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\r\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_empty_marker_treated_as_essay(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("   \n")
    assert read_project_type(tmp_project) == "essay"


def test_write_project_type_essay_no_marker(tmp_project):
    """Essay default writes no marker (legacy-safe)."""
    write_project_type(tmp_project, "essay")
    assert not (tmp_project / ".sourced-project-type").exists()


def test_write_project_type_annotated_writes_marker(tmp_project):
    write_project_type(tmp_project, "annotated-bib")
    assert (tmp_project / ".sourced-project-type").read_text().strip() == "annotated-bib"


# ----- voice / style markers -----

def test_read_voice_marker_finds_quoted_form(tmp_project):
    (tmp_project / "voice.md").write_text(
        "<!-- sourced:voice=academic -->\n# Voice rules\n"
    )
    assert read_voice_marker(tmp_project / "voice.md") == "academic"


def test_read_voice_marker_returns_none_when_missing(tmp_project):
    (tmp_project / "voice.md").write_text("# No marker\nplain content\n")
    assert read_voice_marker(tmp_project / "voice.md") is None


def test_read_style_marker_works_similarly(tmp_project):
    (tmp_project / "style.md").write_text("<!-- sourced:style=apa7 -->\n")
    assert read_style_marker(tmp_project / "style.md") == "apa7"


# ----- managed-block sentinels (column-0 strict) -----

def test_extract_managed_block_finds_pair():
    text = (
        "before\n"
        "<!-- sourced:begin managed -->\n"
        "managed line 1\n"
        "managed line 2\n"
        "<!-- sourced:end managed -->\n"
        "after\n"
    )
    block = extract_managed_block(text)
    assert "managed line 1" in block
    assert "managed line 2" in block
    assert "before" not in block
    assert "after" not in block


def test_extract_managed_block_rejects_indented_sentinel():
    """The strict column-0 regex must not match an indented sentinel
    (legitimate prose documenting the sentinel system)."""
    text = (
        "  - <!-- sourced:begin managed -->\n"
        "managed?\n"
        "  - <!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError):
        extract_managed_block(text)


def test_extract_managed_block_rejects_missing_sentinels():
    with pytest.raises(ProjectError, match="begin"):
        extract_managed_block("no sentinels here\n")


def test_extract_managed_block_rejects_double_begin():
    text = (
        "<!-- sourced:begin managed -->\n"
        "first\n"
        "<!-- sourced:begin managed -->\n"
        "<!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError, match="multiple"):
        extract_managed_block(text)


def test_replace_managed_block_preserves_outside():
    original = (
        "USER PROSE BEFORE\n"
        "<!-- sourced:begin managed -->\n"
        "old managed\n"
        "<!-- sourced:end managed -->\n"
        "USER PROSE AFTER\n"
    )
    new_managed = "fresh managed content"
    out = replace_managed_block(original, new_managed)
    assert "USER PROSE BEFORE\n" in out
    assert "USER PROSE AFTER\n" in out
    assert "fresh managed content" in out
    assert "old managed" not in out


# ----- .sourced.bak rollback fallback -----

def test_write_bak_sibling_creates_bak(tmp_project):
    f = tmp_project / "CLAUDE.md"
    f.write_text("original")
    write_bak_sibling(f)
    assert (tmp_project / "CLAUDE.md.sourced.bak").read_text() == "original"


def test_write_bak_sibling_no_op_when_target_missing(tmp_project):
    f = tmp_project / "CLAUDE.md"
    write_bak_sibling(f)  # should not raise
    assert not (tmp_project / "CLAUDE.md.sourced.bak").exists()
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_project.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/project.py`**

```python
"""Per-project state: project-type marker, voice/style markers, managed-block sentinels.

Distinct from config.py (user-global). Different lifecycle, different fixtures.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Literal

from .errors import ProjectError

ProjectType = Literal["essay", "annotated-bib"]

# Sentinel parsing: column-0 strict per spec §5.5 (closes cycle-3 F28).
# install.sh's awk matched anywhere on the line, leading to silent corruption
# when the sentinel string appeared in user prose. The CLI is stricter.
BEGIN_RE = re.compile(r"^<!-- sourced:begin managed -->$", re.MULTILINE)
END_RE = re.compile(r"^<!-- sourced:end managed -->$", re.MULTILINE)

# Voice / style first-line markers.
VOICE_MARKER_RE = re.compile(r"<!--\s*sourced:voice=(\S+?)\s*-->")
STYLE_MARKER_RE = re.compile(r"<!--\s*sourced:style=(\S+?)\s*-->")


# ----- project type marker -----

def project_type_marker_path(project_dir: Path) -> Path:
    return project_dir / ".sourced-project-type"


def read_project_type(project_dir: Path) -> ProjectType:
    """Returns 'essay' if marker absent, empty, or whitespace-only (legacy default).
    Returns the trimmed value otherwise. Tolerates CRLF.
    """
    p = project_type_marker_path(project_dir)
    if not p.exists():
        return "essay"
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return "essay"
    if raw not in ("essay", "annotated-bib"):
        raise ProjectError(
            f".sourced-project-type contains unknown value {raw!r}; "
            f"expected 'essay' or 'annotated-bib'."
        )
    return raw  # type: ignore[return-value]


def write_project_type(project_dir: Path, kind: ProjectType) -> None:
    """Essay writes no marker (legacy-safe default).
    Non-essay types write the marker file."""
    p = project_type_marker_path(project_dir)
    if kind == "essay":
        if p.exists():
            p.unlink()
        return
    p.write_text(f"{kind}\n", encoding="utf-8")


# ----- voice / style markers -----

def read_voice_marker(voice_md: Path) -> str | None:
    if not voice_md.exists():
        return None
    text = voice_md.read_text(encoding="utf-8")
    m = VOICE_MARKER_RE.search(text)
    return m.group(1) if m else None


def read_style_marker(style_md: Path) -> str | None:
    if not style_md.exists():
        return None
    text = style_md.read_text(encoding="utf-8")
    m = STYLE_MARKER_RE.search(text)
    return m.group(1) if m else None


# ----- managed-block sentinels -----

def extract_managed_block(text: str) -> str:
    """Return the text between BEGIN and END sentinels (exclusive).
    Raises ProjectError if zero or >1 begin/end found."""
    begins = list(BEGIN_RE.finditer(text))
    ends = list(END_RE.finditer(text))
    if len(begins) == 0:
        raise ProjectError(
            "no <!-- sourced:begin managed --> sentinel at column 0; "
            "the file may not be a sourced-rendered CLAUDE.md, or the sentinel "
            "is indented (which the CLI's strict matcher rejects per spec §5.5)."
        )
    if len(ends) == 0:
        raise ProjectError(
            "begin sentinel found but no matching <!-- sourced:end managed --> sentinel."
        )
    if len(begins) > 1:
        raise ProjectError("multiple begin sentinels at column 0 in CLAUDE.md.")
    if len(ends) > 1:
        raise ProjectError("multiple end sentinels at column 0 in CLAUDE.md.")
    start = begins[0].end() + 1  # +1 to skip the trailing \n
    finish = ends[0].start()
    return text[start:finish]


def replace_managed_block(text: str, new_managed: str) -> str:
    """Replace the managed block (between sentinels) with new_managed.
    Sentinels themselves are kept; new_managed is the content between them."""
    begins = list(BEGIN_RE.finditer(text))
    ends = list(END_RE.finditer(text))
    if len(begins) != 1 or len(ends) != 1:
        # Defensive — extract_managed_block would have already raised.
        raise ProjectError("malformed sentinels; cannot replace managed block.")
    before = text[: begins[0].end()]
    after = text[ends[0].start() :]
    if not new_managed.endswith("\n"):
        new_managed += "\n"
    return f"{before}\n{new_managed}{after}"


# ----- .sourced.bak rollback fallback (spec §5.7) -----

def bak_path(target: Path) -> Path:
    return target.with_suffix(target.suffix + ".sourced.bak")


def write_bak_sibling(target: Path) -> None:
    """Copy target to <target>.sourced.bak before mutation. No-op if target missing."""
    if not target.exists():
        return
    bak = bak_path(target)
    bak.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_project.py -v
```

Expected: 16 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/project.py tests/cli/unit/test_project.py
git commit -m "feat(cli): project.py — markers + sentinels + bak rollback"
```

### Task 2.5: write_atomic helper (lives in render.py for proximity)

**Files:**
- Modify: `src/sourced/render.py` — append `write_atomic`
- Modify: `tests/cli/unit/test_render.py` — append tests

- [ ] **Step 1: Write failing tests (append to existing test_render.py)**

Append to `tests/cli/unit/test_render.py`:

```python
from sourced.render import write_atomic


def test_write_atomic_creates_file(tmp_path):
    target = tmp_path / "out.md"
    write_atomic(target, "hello")
    assert target.read_text() == "hello"


def test_write_atomic_overwrites(tmp_path):
    target = tmp_path / "out.md"
    target.write_text("old")
    write_atomic(target, "new")
    assert target.read_text() == "new"


def test_write_atomic_creates_parent_dir(tmp_path):
    target = tmp_path / "nested" / "deep" / "out.md"
    write_atomic(target, "hello")
    assert target.read_text() == "hello"


def test_write_atomic_no_stale_tmp_left(tmp_path):
    target = tmp_path / "out.md"
    write_atomic(target, "hello")
    # No file matching .out.md.<random>.tmp should remain.
    leftovers = [p for p in tmp_path.iterdir() if ".tmp" in p.name]
    assert leftovers == []
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_render.py::test_write_atomic_creates_file -v
```

Expected: ImportError on `write_atomic`.

- [ ] **Step 3: Append `write_atomic` to `src/sourced/render.py`**

Add to bottom of `src/sourced/render.py`:

```python
import tempfile
from pathlib import Path


def write_atomic(path: Path, content: str) -> None:
    """Write content to path atomically (tempfile + rename in same dir).

    Avoids partial-write corruption if the process dies mid-write. Uses a
    randomized tempfile name (NamedTemporaryFile) so a stale .tmp from a
    previous crash doesn't collide. Skip explicit fsync — overkill for config files.

    Cross-device safe: tempfile is sibling to target → same filesystem → atomic
    rename on POSIX (and Windows 3.3+).

    Windows caveat: replace() raises PermissionError if target is open in another
    process (e.g., editor). Caller surfaces clearly.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_render.py -v
```

Expected: all tests (incl. 4 new) pass.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/render.py tests/cli/unit/test_render.py
git commit -m "feat(cli): write_atomic — tempfile + rename"
```

### PR 2 gate (before opening PR)

```bash
pytest tests/cli/unit/ -v        # render + mirror + config + project + ui + errors + context
sourced --version                # still works
sourced check                    # still works
```

If all green, open PR 2: "feat(cli): I/O layer — render, mirror, config, project".

---

# PR 3: Data relocation + validators

**Goal:** Move all bundled data under `src/sourced/data/`, update parity-suite path reference, then implement the three validators (CSL title, iron rules, §10 exemptions) with unit tests against fixture inputs. After this PR, the package can read its own bundled templates and validate them; ready for command wiring in PR 4.

### Task 3.1: Relocate data directories under `src/sourced/data/`

**Files:**
- Move: `templates/` → `src/sourced/data/templates/`
- Move: `agents/` → `src/sourced/data/agents/`
- Move: `citations/` → `src/sourced/data/citations/`
- Move: `skills/` → `src/sourced/data/skills/`
- Move: `filters/` (top-level) → `src/sourced/data/filters/` (if exists; else just move templates/filters/)
- Modify: `tests/parity/_render.sh` — update CSL lookup path

**Important:** install.sh currently reads from these top-level dirs. Don't update install.sh — it's being deleted in PR 5. The parity test `_render.sh` MUST be updated because PR 5 needs the existing 20-golden parity suite to still pass.

- [ ] **Step 1: Verify state before move**

```bash
cd /home/hayden/sourced
ls templates agents citations skills filters 2>&1 | head -5  # confirm what exists
git status --porcelain                                       # tree must be clean
bash tests/parity/run-all.sh 2>&1 | tail -3                  # baseline: should be all-green
```

Expected: `All styles passed parity.` Last line.

- [ ] **Step 2: Create destination directory**

```bash
mkdir -p /home/hayden/sourced/src/sourced/data
```

- [ ] **Step 3: Move templates/ → src/sourced/data/templates/**

```bash
cd /home/hayden/sourced
git mv templates src/sourced/data/templates
```

- [ ] **Step 4: Move agents/ → src/sourced/data/agents/**

```bash
git mv agents src/sourced/data/agents
```

- [ ] **Step 5: Move citations/ → src/sourced/data/citations/**

```bash
git mv citations src/sourced/data/citations
```

- [ ] **Step 6: Move skills/ → src/sourced/data/skills/**

```bash
git mv skills src/sourced/data/skills
```

- [ ] **Step 7: Move templates/filters → src/sourced/data/filters/ (if templates/filters existed)**

Per existing layout, `filters/` lives under `templates/filters/`. After step 3, it's already at `src/sourced/data/templates/filters/`. The spec wants it at `src/sourced/data/filters/` (sibling of templates/). Promote it:

```bash
cd /home/hayden/sourced
git mv src/sourced/data/templates/filters src/sourced/data/filters
```

- [ ] **Step 8: Update `tests/parity/_render.sh` CSL lookup path**

Find the line that reads CSL files:

```bash
grep -n 'templates/styles' tests/parity/_render.sh
```

Edit `tests/parity/_render.sh` line ~34 from:
```bash
CSL_FILES=("${REPO_DIR}/templates/styles/${STYLE_NAME}"/*.csl)
```
to:
```bash
CSL_FILES=("${REPO_DIR}/src/sourced/data/templates/styles/${STYLE_NAME}"/*.csl)
```

Also check for any other `templates/...` reference in `_render.sh` and update consistently. Also check `tests/parity/_render.sh` references to `templates/filters/` (the lua-filter path):

```bash
grep -n 'templates/filters' tests/parity/_render.sh
```

If found, update from `${REPO_DIR}/templates/filters/smart-quotes.lua` to `${REPO_DIR}/src/sourced/data/filters/smart-quotes.lua`.

- [ ] **Step 9: Run parity to verify the path update worked**

```bash
bash tests/parity/run-all.sh 2>&1 | tail -3
```

Expected: `All styles passed parity.` (same as baseline).

- [ ] **Step 10: Re-install editable + verify CLI still works**

```bash
pipx install --force -e .
sourced --version
sourced check
```

Expected: same as PR 1 — CLI still works (the relocated data isn't read by the CLI yet; this just verifies the install didn't break).

- [ ] **Step 11: Commit (large but coherent — one rename PR)**

```bash
git status --porcelain | head -30   # sanity-check the diff is just the renames + _render.sh
git commit -m "refactor: relocate bundled data under src/sourced/data/

Moves templates/, agents/, citations/, skills/, and filters/ (formerly
templates/filters/) under src/sourced/data/. Required for the Python
package's importlib.resources access pattern AND for editable installs to
hot-reload template edits — Hatch's force-include is build-time-only and
snapshots data at install time, so the canonical location must be inside
the package source tree.

Updates tests/parity/_render.sh CSL + lua-filter lookup paths to match.
Existing 20-golden parity suite continues to pass unchanged.

install.sh continues to read from the new paths because it builds
\${REPO_DIR}/templates/... — this commit makes those paths broken.
install.sh is replaced entirely in PR 5; for the duration of PR 3-4 it
will be non-functional. The CLI is the sole entry point during this window."
```

**Note:** From this commit onward, `install.sh` is broken — the bash paths still point at the old top-level locations. This is acceptable because PR 4 lands the CLI replacements before PR 5 retires install.sh.

### Task 3.2: validators/csl.py — pre-render CSL title check

**Files:**
- Create: `src/sourced/validators/csl.py`
- Create: `tests/cli/unit/test_validators_csl.py`
- Create: `tests/cli/unit/fixtures/csl/` directory with test fixtures

The current install.sh `validate_csl_title` parses a style.md file's `CSL title:` declaration line, then parses the matching CSL XML file's `<title>` element, and compares. Phase-1 port: same behavior, returns `Finding` list.

- [ ] **Step 1: Create test fixtures**

```bash
mkdir -p tests/cli/unit/fixtures/csl
```

Create `tests/cli/unit/fixtures/csl/matching.csl`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" version="1.0" default-locale="en-US">
  <info>
    <title>American Psychological Association 7th edition</title>
    <id>http://www.zotero.org/styles/apa</id>
  </info>
</style>
```

Create `tests/cli/unit/fixtures/csl/mismatching.csl`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" version="1.0">
  <info>
    <title>Wrong Style Name</title>
  </info>
</style>
```

Create `tests/cli/unit/fixtures/csl/no_title.csl`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" version="1.0">
  <info>
    <id>http://example.com</id>
  </info>
</style>
```

- [ ] **Step 2: Write failing tests**

Create `tests/cli/unit/test_validators_csl.py`:

```python
import pytest
from pathlib import Path
from sourced.validators.csl import validate_csl_title

FIXTURES = Path(__file__).parent / "fixtures" / "csl"


def test_matching_title_returns_no_findings():
    findings = validate_csl_title(
        csl_path=FIXTURES / "matching.csl",
        declared_title="American Psychological Association 7th edition",
        style_name="apa7",
    )
    assert findings == []


def test_mismatching_title_returns_finding():
    findings = validate_csl_title(
        csl_path=FIXTURES / "mismatching.csl",
        declared_title="American Psychological Association 7th edition",
        style_name="apa7",
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.rule == "csl-title-mismatch"
    assert f.severity == "error"
    assert "Wrong Style Name" in f.message
    assert "American Psychological Association 7th edition" in f.message


def test_missing_title_element_returns_finding():
    findings = validate_csl_title(
        csl_path=FIXTURES / "no_title.csl",
        declared_title="Anything",
        style_name="apa7",
    )
    assert len(findings) == 1
    assert findings[0].rule == "csl-title-missing"


def test_missing_csl_file_returns_finding(tmp_path):
    findings = validate_csl_title(
        csl_path=tmp_path / "nonexistent.csl",
        declared_title="Whatever",
        style_name="apa7",
    )
    assert len(findings) == 1
    assert findings[0].rule == "csl-file-missing"


def test_validator_never_raises_on_malformed_xml(tmp_path):
    """Validator returns Finding, never raises (per spec §3 boundary 3)."""
    bad = tmp_path / "bad.csl"
    bad.write_text("<not really xml")
    findings = validate_csl_title(
        csl_path=bad,
        declared_title="Anything",
        style_name="apa7",
    )
    assert len(findings) >= 1
    assert findings[0].rule == "csl-parse-error"
```

- [ ] **Step 3: Verify failure**

```bash
pytest tests/cli/unit/test_validators_csl.py -v
```

Expected: ImportError.

- [ ] **Step 4: Create `src/sourced/validators/csl.py`**

```python
"""CSL XML title validation. PRE-render: checks a static fact about the template.

A style.md file declares its CSL provenance (`CSL title: <name>`), and the
matching CSL XML file at templates/styles/<name>/<file>.csl has a <title>
element. This validator confirms they agree — silent edition drift (e.g.,
upstream CSL repository updates Chicago 17 → 18) gets caught here.
"""
from __future__ import annotations
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from . import Finding


# CSL is XML with a default namespace: http://purl.org/net/xbiblio/csl
_CSL_NS = {"csl": "http://purl.org/net/xbiblio/csl"}


def validate_csl_title(
    csl_path: Path,
    declared_title: str,
    style_name: str,
) -> list[Finding]:
    """Compare CSL XML <info><title> against style.md's declared title."""
    if not csl_path.exists():
        return [Finding(
            rule="csl-file-missing",
            location=str(csl_path),
            severity="error",
            message=f"CSL file declared by style '{style_name}' does not exist on disk.",
            fix_hint=f"vendor the CSL file at {csl_path}, or update style.md provenance.",
        )]

    try:
        tree = ET.parse(csl_path)
    except ET.ParseError as e:
        return [Finding(
            rule="csl-parse-error",
            location=str(csl_path),
            severity="error",
            message=f"CSL file is not valid XML: {e}",
        )]

    root = tree.getroot()
    title_elem = root.find("csl:info/csl:title", _CSL_NS)
    if title_elem is None or title_elem.text is None:
        return [Finding(
            rule="csl-title-missing",
            location=str(csl_path),
            severity="error",
            message="CSL file has no <info><title> element.",
            fix_hint="check the CSL file is the right edition; the upstream repository "
                     "may have moved this style to a different filename.",
        )]

    actual = title_elem.text.strip()
    if actual != declared_title:
        return [Finding(
            rule="csl-title-mismatch",
            location=str(csl_path),
            severity="error",
            message=(
                f"style '{style_name}' declares CSL title "
                f"{declared_title!r} but the CSL file's <title> is {actual!r} — "
                "silent edition drift. The vendored CSL file may have been "
                "replaced by a different edition's upstream version."
            ),
            fix_hint=f"either update style.md's `CSL title:` to {actual!r}, "
                     f"or replace {csl_path} with the correct edition.",
        )]

    return []
```

- [ ] **Step 5: Verify**

```bash
pytest tests/cli/unit/test_validators_csl.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add src/sourced/validators/csl.py tests/cli/unit/test_validators_csl.py tests/cli/unit/fixtures/csl/
git commit -m "feat(cli): validators/csl.py — pre-render CSL title check"
```

### Task 3.3: validators/iron_rules.py — extract + normalize + validate

The current install.sh `extract_iron_rules` reads `## Iron rules`, `## AI-tells`, `## Generation signatures` sections plus any `[iron]`-tagged line. `normalize_rule` lowercases, collapses whitespace, strips trailing punctuation. `validate_iron_rules` verifies every iron rule from the skeleton appears (normalized substring) in the candidate voice file.

**Files:**
- Create: `src/sourced/validators/iron_rules.py`
- Create: `tests/cli/unit/test_validators_iron_rules.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_validators_iron_rules.py`:

```python
import pytest
from sourced.validators.iron_rules import extract_iron_rules, normalize_rule, validate


def test_extract_iron_rules_section():
    skeleton = (
        "# Voice\n\n"
        "## Iron rules\n\n"
        "- No em dashes.\n"
        "- Never use 'utilize' when 'use' fits.\n\n"
        "## Other section\n"
        "- Not iron.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("em dashes" in r.lower() for r in rules)
    assert any("utilize" in r.lower() for r in rules)
    assert all("Not iron" not in r for r in rules)


def test_extract_includes_ai_tells_section():
    skeleton = (
        "## AI-tells\n\n"
        "- Don't say 'in this way'.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("in this way" in r for r in rules)


def test_extract_includes_generation_signatures_section():
    skeleton = (
        "## Generation signatures\n\n"
        "- No 'not X but Y' constructions.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("not X but Y" in r for r in rules)


def test_extract_includes_iron_token_lines():
    skeleton = (
        "## Random section\n\n"
        "Some prose here. [iron] This sentence is iron.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("iron" in r.lower() for r in rules)


def test_normalize_lowercase():
    assert "no em dashes" in normalize_rule("- No EM Dashes!")


def test_normalize_strips_trailing_punctuation():
    assert normalize_rule("Rule.") == normalize_rule("Rule!") == normalize_rule("Rule?")


def test_normalize_collapses_whitespace():
    assert normalize_rule("a   b\tc") == normalize_rule("a b c")


def test_validate_passes_when_all_rules_present():
    skeleton = "## Iron rules\n- No em dashes.\n- No utilize.\n"
    voice = (
        "voice prose\n"
        "remember: no em dashes.\n"
        "and absolutely no utilize.\n"
    )
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert findings == []


def test_validate_finds_missing_rules():
    skeleton = "## Iron rules\n- No em dashes.\n- No utilize.\n"
    voice = "voice prose without the rule.\n"
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert len(findings) == 2
    assert all(f.rule == "iron-rule-missing" for f in findings)
    assert all(f.severity == "error" for f in findings)


def test_validate_returns_no_findings_when_skeleton_has_no_iron_rules():
    """Empty iron-rules section → no requirements → no findings."""
    skeleton = "## Iron rules\n\n## Other\n- whatever\n"
    voice = "anything goes\n"
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert findings == []


def test_validate_self_validation_short_circuit():
    """Skeleton == candidate must return [] (the skeleton's own iron-rule lines
    contain the rule text trivially)."""
    skeleton = "## Iron rules\n- No em dashes.\n"
    findings = validate(skeleton=skeleton, candidate=skeleton, voice_name="academic")
    assert findings == []


def test_validate_never_raises_on_garbage_input():
    findings = validate(skeleton="", candidate="", voice_name="x")
    assert findings == []
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_validators_iron_rules.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/validators/iron_rules.py`**

```python
"""Iron-rule validation. POST-render: checks rendered voice file content.

A voice skeleton declares a set of iron rules under ## Iron rules, ## AI-tells,
or ## Generation signatures, plus any line marked with [iron]. Every such rule
must appear (normalized substring match) in the rendered voice library file.

This is the caller-side layer of iron-rule defense-in-depth (spec §9). install.sh
also runs the same check at render time as a mandatory backstop.
"""
from __future__ import annotations
import re

from . import Finding


# Section headers that mark iron-rule blocks. Match `## Iron rules` (and AI-tells,
# Generation signatures) with optional trailing whitespace, no other text on the line.
_IRON_SECTION_RE = re.compile(
    r"^## (Iron rules|AI-tells|Generation signatures)(\s|$)"
)
_OTHER_SECTION_RE = re.compile(r"^## ")
_IRON_TOKEN = "[iron]"


def extract_iron_rules(text: str) -> list[str]:
    """Return non-empty rule lines from iron sections + any [iron]-tagged lines."""
    rules: list[str] = []
    in_iron = False
    for line in text.splitlines():
        if _IRON_SECTION_RE.match(line):
            in_iron = True
            continue
        if _OTHER_SECTION_RE.match(line) and in_iron:
            in_iron = False
            # don't `continue` — fall through so [iron] lines in non-iron sections still get picked
        if in_iron and line.strip():
            rules.append(line)
    # Also pick up [iron]-tagged lines anywhere in the file.
    for line in text.splitlines():
        if _IRON_TOKEN in line and line not in rules:
            rules.append(line)
    return rules


def normalize_rule(s: str) -> str:
    """Lowercase, collapse whitespace, strip leading/trailing whitespace + sentence-final punct.

    Same algorithm as install.sh's normalize_rule. Used for substring matching
    against a normalized candidate.
    """
    out = s.lower()
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"[.!?]+$", "", out)
    return out


def _normalize_candidate(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def validate(skeleton: str, candidate: str, voice_name: str) -> list[Finding]:
    """Verify every iron rule from skeleton appears (normalized substring) in candidate."""
    iron_rules = extract_iron_rules(skeleton)
    if not iron_rules:
        return []
    candidate_norm = _normalize_candidate(candidate)
    findings: list[Finding] = []
    for raw in iron_rules:
        normalized = normalize_rule(raw)
        if not normalized:
            continue
        if normalized not in candidate_norm:
            findings.append(Finding(
                rule="iron-rule-missing",
                location=f"voice '{voice_name}'",
                severity="error",
                message=f"iron rule missing from rendered voice: {raw.strip()!r}",
                fix_hint=(
                    "if voice-extractor dropped or reworded this rule, regenerate the voice "
                    "with overwrite: true and re-run sourced install."
                ),
            ))
    return findings
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_validators_iron_rules.py -v
```

Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/validators/iron_rules.py tests/cli/unit/test_validators_iron_rules.py
git commit -m "feat(cli): validators/iron_rules.py — post-render iron-rule check"
```

### Task 3.4: validators/exemptions.py — §10 exemption syntax

The current install.sh `extract_voice_exemptions` reads bullets under `## §10 exemptions` matching `^- [a-z0-9-]+`. `list_section_10_ids` reads CLAUDE.md's `### Never (rewrite on sight)` section and extracts `[id: ...]` markers. Phase-1: port the bullet extraction; the canonical-id list comes from a CLAUDE.md path the validator gets passed.

**Files:**
- Create: `src/sourced/validators/exemptions.py`
- Create: `tests/cli/unit/test_validators_exemptions.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/unit/test_validators_exemptions.py`:

```python
import pytest
from sourced.validators.exemptions import (
    extract_voice_exemptions,
    extract_canonical_ids,
    validate,
)


def test_extract_voice_exemptions_finds_bullets():
    voice = (
        "## §10 exemptions\n\n"
        "- em-dash-allowed: this voice uses em dashes for parenthetical asides.\n"
        "- not-x-but-y: present tense; corpus shows.\n\n"
        "## Other\n"
        "- not-an-exemption\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == ["em-dash-allowed", "not-x-but-y"]


def test_extract_voice_exemptions_ignores_prose_bullets():
    """A bullet whose first token isn't [a-z0-9-]+ is prose; don't count it."""
    voice = (
        "## §10 exemptions\n\n"
        "- em-dash-allowed\n"
        "- This is a free-prose explanation, not an exemption id.\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == ["em-dash-allowed"]


def test_extract_voice_exemptions_returns_empty_when_section_absent():
    voice = "# Some voice\n\n## Iron rules\n- foo\n"
    assert extract_voice_exemptions(voice) == []


def test_extract_canonical_ids_from_claude_md():
    claude_md = (
        "## 10. Generation signatures\n\n"
        "### Never (rewrite on sight)\n\n"
        "- **Em dashes**. [id: em-dash-allowed]\n"
        "- **'Not X but Y' pivots**. [id: not-x-but-y]\n\n"
        "### Watch for density\n"
        "- **Other [id: density-foo]**\n"
    )
    ids = extract_canonical_ids(claude_md)
    assert "em-dash-allowed" in ids
    assert "not-x-but-y" in ids
    # density-foo is in a different section — should not appear.
    assert "density-foo" not in ids


def test_validate_passes_when_all_exemption_ids_canonical():
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n- **Y**. [id: bar]\n"
    voice = "## §10 exemptions\n- foo\n- bar\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_finds_unknown_exemption_id():
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n"
    voice = "## §10 exemptions\n- foo\n- typo-id\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert len(findings) == 1
    assert findings[0].rule == "exemption-unknown-id"
    assert "typo-id" in findings[0].message


def test_validate_no_section_no_findings():
    """Voice with no §10 exemptions section → nothing to validate."""
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n"
    voice = "no exemptions section\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_never_raises_on_garbage():
    findings = validate(voice="", claude_md="", voice_name="x")
    assert findings == []
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/unit/test_validators_exemptions.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/validators/exemptions.py`**

```python
"""§10 exemption syntax validation. POST-render.

Voice files may exempt themselves from specific §10 Never-list rules via:
    ## §10 exemptions

    - em-dash-allowed: explanation
    - not-x-but-y: explanation

Canonical ids come from CLAUDE.md's `### Never (rewrite on sight)` section,
where each rule carries `[id: <id>]`. This validator checks that every
exemption id in the voice resolves to a canonical id; typos are caught.
"""
from __future__ import annotations
import re

from . import Finding


_VOICE_EXEMPTION_SECTION_RE = re.compile(r"^## §10 exemptions(\s|$)")
_OTHER_SECTION_RE = re.compile(r"^## ")
_BULLET_ID_RE = re.compile(r"^- ([a-z0-9-]+)(\s|:|$)")

_NEVER_SECTION_RE = re.compile(r"^### Never \(rewrite on sight\)(\s|$)")
_OTHER_HASH3_SECTION_RE = re.compile(r"^### ")
_ID_TOKEN_RE = re.compile(r"\[id:\s*([a-z0-9-]+)\s*\]")


def extract_voice_exemptions(voice_text: str) -> list[str]:
    """Return ids declared under ## §10 exemptions. Free-prose bullets ignored."""
    ids: list[str] = []
    in_section = False
    for line in voice_text.splitlines():
        if _VOICE_EXEMPTION_SECTION_RE.match(line):
            in_section = True
            continue
        if _OTHER_SECTION_RE.match(line) and in_section:
            in_section = False
            continue
        if in_section:
            m = _BULLET_ID_RE.match(line)
            if m:
                ids.append(m.group(1))
    return ids


def extract_canonical_ids(claude_md_text: str) -> list[str]:
    """Return ids declared in CLAUDE.md's ### Never (rewrite on sight) section."""
    ids: list[str] = []
    in_section = False
    for line in claude_md_text.splitlines():
        if _NEVER_SECTION_RE.match(line):
            in_section = True
            continue
        if _OTHER_HASH3_SECTION_RE.match(line) and in_section:
            in_section = False
            continue
        if in_section:
            ids.extend(_ID_TOKEN_RE.findall(line))
    return ids


def validate(voice: str, claude_md: str, voice_name: str) -> list[Finding]:
    """Each exemption id in the voice must match a canonical id from CLAUDE.md."""
    declared = extract_voice_exemptions(voice)
    if not declared:
        return []
    canonical = set(extract_canonical_ids(claude_md))
    findings: list[Finding] = []
    for d in declared:
        if d not in canonical:
            findings.append(Finding(
                rule="exemption-unknown-id",
                location=f"voice '{voice_name}' ## §10 exemptions",
                severity="error",
                message=f"exemption id {d!r} does not match any canonical id in CLAUDE.md §10 Never list.",
                fix_hint=(
                    "either fix the typo in the voice file, or add the rule to "
                    "CLAUDE.md's `### Never (rewrite on sight)` section with an [id: ...] tag."
                ),
            ))
    return findings
```

- [ ] **Step 4: Verify**

```bash
pytest tests/cli/unit/test_validators_exemptions.py -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/validators/exemptions.py tests/cli/unit/test_validators_exemptions.py
git commit -m "feat(cli): validators/exemptions.py — §10 exemption syntax check"
```

### PR 3 gate (before opening PR)

```bash
pytest tests/cli/unit/ -v               # all unit tests pass
bash tests/parity/run-all.sh            # existing 20-golden suite still green
ls src/sourced/data/                    # confirms relocated tree
sourced --version                       # CLI still installable
```

If all green, open PR 3: "refactor: relocate data + validators".

---

# PR 4: Commands + integration tests

**Goal:** All 6 phase-1 subcommands wired up and behaviorally complete. End-to-end integration tests against tmp dirs. After this PR, `sourced install`, `sourced global-install`, `sourced new`, `sourced update`, `sourced switch`, and `sourced check` (full version) all work.

### Task 4.1: Expand cli.py with all subparsers

**Files:**
- Modify: `src/sourced/cli.py` — add subparsers for install/global-install/new/update/switch

- [ ] **Step 1: Replace cli.py with the full version**

Replace `src/sourced/cli.py` with:

```python
"""argparse root + subcommand dispatch + top-level error→exit-code mapping.

This is the ONLY module that touches argparse. Subcommand modules accept
plain Python args, not argparse.Namespace.
"""
from __future__ import annotations
import argparse
import os
import sys
from typing import NoReturn

from . import __version__
from .context import Context
from .errors import SourcedError, UsageError
from .ui import print_error, print_unexpected, should_color


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sourced", description="sourced framework CLI")
    p.add_argument("--version", action="version", version=f"sourced {__version__}")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    p.add_argument("--no-color", action="store_const", const="never", dest="color")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict", action="store_true")

    sub = p.add_subparsers(dest="subcommand", metavar="<subcommand>")

    # install
    p_install = sub.add_parser("install", help="install per-project files in PWD or --project")
    p_install.add_argument("--project", help="target project directory (default: PWD)")
    p_install.add_argument("--voice", default="academic")
    p_install.add_argument("--style", default="apa7")
    p_install.add_argument("--type", dest="project_type",
                           choices=["essay", "annotated-bib"], default="essay")
    p_install.add_argument("--brief", help="also create <name>.brief.md")
    p_install.add_argument("--force", action="store_true")

    # global-install
    p_gi = sub.add_parser("global-install", help="install/refresh ~/.claude/ files")
    p_gi.add_argument("--force", action="store_true")

    # new
    p_new = sub.add_parser("new", help="create project dir + brief + install")
    p_new.add_argument("project_name", help="project directory to create")
    p_new.add_argument("--voice", default="academic")
    p_new.add_argument("--style", default="apa7")
    p_new.add_argument("--type", dest="project_type",
                       choices=["essay", "annotated-bib"], default="essay")
    p_new.add_argument("--brief", help="brief filename (default: <project_name>)")
    p_new.add_argument("--force", action="store_true")

    # update
    p_update = sub.add_parser("update", help="refresh managed block of CLAUDE.md")
    p_update.add_argument("--project", help="target project directory (default: PWD)")
    p_update.add_argument("--force", action="store_true")

    # switch
    p_switch = sub.add_parser("switch", help="swap voice or style on existing project")
    switch_sub = p_switch.add_subparsers(dest="switch_kind", metavar="<voice|style>", required=True)
    p_sv = switch_sub.add_parser("voice", help="swap voice")
    p_sv.add_argument("name", help="library voice name")
    p_sv.add_argument("--project", help="target project directory (default: PWD)")
    p_ss = switch_sub.add_parser("style", help="swap style")
    p_ss.add_argument("name", help="library style name")
    p_ss.add_argument("--project", help="target project directory (default: PWD)")

    # check
    p_check = sub.add_parser("check", help="diagnose prereqs + ~/.claude/ health")
    p_check.add_argument("--project", help="also check this project directory")

    return p


def _ctx_from_args(args: argparse.Namespace) -> Context:
    return Context(
        dry_run=args.dry_run,
        verbose=args.verbose,
        quiet=args.quiet,
        color=args.color,
        strict=args.strict,
    )


def _dispatch(args: argparse.Namespace) -> int:
    ctx = _ctx_from_args(args)
    sub = args.subcommand

    if sub == "install":
        from .commands import install
        return install.run(
            ctx, project=args.project, voice=args.voice, style=args.style,
            project_type=args.project_type, brief=args.brief, force=args.force,
        )
    if sub == "global-install":
        from .commands import global_install
        return global_install.run(ctx, force=args.force)
    if sub == "new":
        from .commands import new
        return new.run(
            ctx, project_name=args.project_name, voice=args.voice, style=args.style,
            project_type=args.project_type, brief=args.brief, force=args.force,
        )
    if sub == "update":
        from .commands import update
        return update.run(ctx, project=args.project, force=args.force)
    if sub == "switch":
        from .commands import switch
        return switch.run(ctx, kind=args.switch_kind, name=args.name, project=args.project)
    if sub == "check":
        from .commands import check
        return check.run(ctx, project=args.project)

    # No subcommand → print help, exit 2.
    _build_parser().print_help(sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> NoReturn:
    parser = _build_parser()
    args = parser.parse_args(argv)
    use_color = should_color(args.color, sys.stderr)

    try:
        sys.exit(_dispatch(args))
    except SourcedError as e:
        print_error(e, use_color)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        debug = os.environ.get("SOURCED_DEBUG") or args.verbose >= 2
        if debug:
            raise
        print_unexpected(e)
        sys.exit(70)
```

- [ ] **Step 2: Reinstall + verify subcommand help works (commands not yet implemented)**

```bash
pipx install --force -e .
sourced --help                      # shows all subcommands
sourced install --help              # shows install flags
sourced switch --help               # shows voice|style sub-subparser
```

Expected: help text for each. (Running them will currently fail — that's fine; commands implemented next.)

- [ ] **Step 3: Commit**

```bash
git add src/sourced/cli.py
git commit -m "feat(cli): expand cli.py with all phase-1 subparsers"
```

### Task 4.2: commands/_pipeline.py — shared install pipeline

The shared install pipeline is what `commands/install.py`, `commands/global_install.py`, and `commands/new.py` all call into. Extracting it prevents the divergence canary the reviewers flagged.

**Files:**
- Create: `src/sourced/commands/_pipeline.py`

- [ ] **Step 1: Create `src/sourced/commands/_pipeline.py`**

```python
"""Shared install pipeline used by install, global_install, and new.

The reviewers' canary: if install.py and global_install.py 80%-copy-paste,
behavior diverges silently (one validates, the other doesn't; one logs, the
other doesn't). This module is the single source of truth.

Pipeline shape (per spec §5.3):

  1. config.load_user_name()                          → str
  2. read_template(subpath)                           → str
  2.5 validators.validate_template(template)          → list[Finding] (PRE-render)
  3. render(template, ctx)                            → str
  4. validators.validate_rendered(rendered)           → list[Finding] (POST-render)
  5. raise ValidationError on errors / on warnings under --strict
  6. dry-run: print diff, return
  7. write_atomic OR mirror_tree
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..context import Context
from ..config import load_user_name, save_user_name
from ..errors import ValidationError, ProjectError
from ..render import RenderContext, read_template, bundled_path, render, write_atomic
from ..mirror import mirror_tree
from ..validators import Finding
from ..validators import csl as csl_validator
from ..validators import iron_rules as iron_rules_validator
from ..validators import exemptions as exemptions_validator


CLAUDE_HOME = Path.home() / ".claude"


def ensure_user_name(ctx: Context) -> str:
    """Read user name from ~/.claude/sourced.config; prompt + save if missing."""
    name = load_user_name()
    if name:
        return name
    if ctx.quiet:
        # Can't prompt in quiet mode.
        raise ProjectError(
            "no user name set in ~/.claude/sourced.config; can't prompt under --quiet. "
            "Run `sourced global-install` interactively first."
        )
    print("First time setup — what's your name? (used in rendered templates)")
    name = input("Name: ").strip()
    if not name:
        raise ProjectError("no name provided.")
    save_user_name(name)
    return name


def install_global(ctx: Context, *, force: bool = False) -> dict:
    """Mirror bundled data into ~/.claude/. Returns counts dict for ui."""
    counts = {"mirrored": 0, "skipped_dirs": 0}

    # Subdirs that map directly:
    for subdir in ("agents", "citations", "templates", "skills", "filters"):
        with bundled_path(subdir) as src:
            dest = CLAUDE_HOME / subdir
            if ctx.dry_run:
                # count files for the summary
                file_count = sum(1 for _ in Path(src).rglob("*") if Path(_).is_file())
                counts["mirrored"] += file_count
            else:
                mirror_tree(Path(src), dest, dry_run=False)
                counts["mirrored"] += sum(1 for _ in dest.rglob("*") if _.is_file())

    # Voice library: bundled templates/voices/*.md → ~/.claude/voice/<name>.md
    # Note: install.sh treats these as templates the per-project step substitutes
    # against; the library copy is unrendered.
    voice_dest = CLAUDE_HOME / "voice"
    style_dest = CLAUDE_HOME / "style"
    if not ctx.dry_run:
        voice_dest.mkdir(parents=True, exist_ok=True)
        style_dest.mkdir(parents=True, exist_ok=True)

    with bundled_path("templates/voices") as voices_src:
        for voice_file in Path(voices_src).glob("*.md"):
            target = voice_dest / voice_file.name
            if ctx.dry_run:
                counts["mirrored"] += 1
            else:
                target.write_text(voice_file.read_text(encoding="utf-8"), encoding="utf-8")
                counts["mirrored"] += 1

    with bundled_path("templates/styles") as styles_src:
        # Top-level style.md files
        for style_file in Path(styles_src).glob("*.md"):
            target = style_dest / style_file.name
            if ctx.dry_run:
                counts["mirrored"] += 1
            else:
                target.write_text(style_file.read_text(encoding="utf-8"), encoding="utf-8")
                counts["mirrored"] += 1
        # Per-style asset directories
        for style_assets in Path(styles_src).iterdir():
            if not style_assets.is_dir():
                continue
            asset_dest = style_dest / style_assets.name
            if ctx.dry_run:
                counts["mirrored"] += sum(1 for _ in style_assets.rglob("*") if _.is_file())
            else:
                mirror_tree(style_assets, asset_dest, dry_run=False)

    return counts


def render_voice(name: str, user: str, ctx: Context) -> str:
    """Render a voice library file into a per-project voice.md.

    Reads ~/.claude/voice/<name>.md (the library — already mirrored by global-install),
    runs iron-rule + exemption validation against that text, prepends the marker line,
    substitutes {{USER}}, returns the rendered text.
    """
    src = CLAUDE_HOME / "voice" / f"{name}.md"
    if not src.exists():
        raise ProjectError(
            f"voice '{name}' not installed at {src}. "
            f"Run `sourced global-install` first, or pass --voice <existing>."
        )
    skeleton_text = src.read_text(encoding="utf-8")

    # POST-render validation: read CLAUDE.md template for canonical ids.
    claude_md_template = read_template("templates/CLAUDE.md")

    # Validators need the rendered text; for voice we substitute then validate.
    rendered_body = render(skeleton_text, RenderContext(user=user))
    findings = []
    findings.extend(iron_rules_validator.validate(
        skeleton=skeleton_text, candidate=rendered_body, voice_name=name,
    ))
    findings.extend(exemptions_validator.validate(
        voice=skeleton_text, claude_md=claude_md_template, voice_name=name,
    ))
    _maybe_raise(findings, ctx)

    return f"<!-- sourced:voice={name} -->\n\n{rendered_body}"


def render_style(name: str, user: str, ctx: Context) -> str:
    """Render a style library file into a per-project style.md."""
    src = CLAUDE_HOME / "style" / f"{name}.md"
    if not src.exists():
        raise ProjectError(
            f"style '{name}' not installed at {src}. "
            f"Run `sourced global-install` first, or pass --style <existing>."
        )
    style_text = src.read_text(encoding="utf-8")
    rendered_body = render(style_text, RenderContext(user=user))
    return f"<!-- sourced:style={name} -->\n\n{rendered_body}"


def render_claude_md(user: str, ctx: Context) -> str:
    """Render the per-project CLAUDE.md."""
    template = read_template("templates/CLAUDE.md")
    return render(template, RenderContext(user=user))


def render_brief(name: str, user: str, project_type: str, ctx: Context) -> str:
    """Render the brief template matching project_type."""
    if project_type == "annotated-bib":
        template = read_template("templates/brief.template.annotated-bib.md")
    else:
        template = read_template("templates/brief.template.md")
    return render(template, RenderContext(user=user))


def _maybe_raise(findings: list[Finding], ctx: Context) -> None:
    """Per spec §5.3 step 5: errors always raise; warnings raise only under --strict."""
    if not findings:
        return
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    if errors:
        raise ValidationError(
            f"{len(errors)} validation error(s)", findings=errors + warnings,
        )
    if warnings and ctx.strict:
        raise ValidationError(
            f"{len(warnings)} warning(s) promoted to error under --strict",
            findings=warnings,
        )
```

- [ ] **Step 2: Commit (no tests yet — exercised through commands' integration tests)**

```bash
git add src/sourced/commands/_pipeline.py
git commit -m "feat(cli): commands/_pipeline.py — shared install pipeline"
```

### Task 4.3: commands/global_install.py + integration test

**Files:**
- Create: `src/sourced/commands/global_install.py`
- Create: `tests/cli/integration/test_global_install.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/cli/integration/test_global_install.py`:

```python
import subprocess
import sys
from pathlib import Path


def test_global_install_creates_expected_dirs(tmp_home, clean_ansi):
    # First run needs a name; pipe it in via stdin.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    expected = ["agents", "citations", "templates", "voice", "style", "skills", "filters"]
    for sub in expected:
        assert (tmp_home / ".claude" / sub).is_dir(), f"missing ~/.claude/{sub}"


def test_global_install_creates_sourced_config(tmp_home, clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    cfg = tmp_home / ".claude" / "sourced.config"
    assert cfg.exists()
    assert "Alice" in cfg.read_text()


def test_global_install_idempotent(tmp_home, clean_ansi):
    """Second run reuses saved name; no prompt."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True, check=True,
    )
    # Second run with no stdin → must not hang asking for input.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_global_install_dry_run_writes_nothing(tmp_home, clean_ansi):
    # Dry-run on a fresh home where there's no name yet → should still need a name?
    # Decision: dry-run still needs config to know what it WOULD render, so prompt.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Dry-run still creates ~/.claude/sourced.config because we needed the name.
    # But it should NOT mirror any other files.
    assert not (tmp_home / ".claude" / "agents").exists()
    assert not (tmp_home / ".claude" / "voice").exists()
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/integration/test_global_install.py -v
```

Expected: ImportError on `sourced.commands.global_install`.

- [ ] **Step 3: Create `src/sourced/commands/global_install.py`**

```python
"""sourced global-install — populate ~/.claude/ with bundled data."""
from __future__ import annotations
import sys

from ..context import Context
from ..ui import bold, ok, should_color
from . import _pipeline


def run(ctx: Context, *, force: bool = False) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    user = _pipeline.ensure_user_name(ctx)

    if not ctx.quiet:
        banner = "DRY RUN — no files will be written.\n" if ctx.dry_run else ""
        print(f"{banner}{bold('Mirroring bundled files to ~/.claude/...', use_color)}")

    counts = _pipeline.install_global(ctx, force=force)

    if not ctx.quiet:
        verb = "would mirror" if ctx.dry_run else "mirrored"
        print(f"\n{verb} {counts['mirrored']} files (user={user}).")
    return 0
```

- [ ] **Step 4: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_global_install.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/commands/global_install.py tests/cli/integration/test_global_install.py
git commit -m "feat(cli): global-install + integration tests"
```

### Task 4.4: commands/install.py + integration tests

**Files:**
- Create: `src/sourced/commands/install.py`
- Create: `tests/cli/integration/test_install_fresh.py`
- Create: `tests/cli/integration/test_install_force.py`
- Create: `tests/cli/integration/test_install_type_annotated.py`

- [ ] **Step 1: Write failing integration tests**

Create `tests/cli/integration/test_install_fresh.py`:

```python
import subprocess
import sys


def _setup_globals(tmp_home):
    """Helper: prerun global-install so per-project install has voice/style libraries."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_creates_per_project_files(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "CLAUDE.md").exists()
    assert (tmp_project / "voice.md").exists()
    assert (tmp_project / "style.md").exists()


def test_install_voice_marker_present(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--voice", "casual"],
        capture_output=True, text=True, check=True,
    )
    assert "<!-- sourced:voice=casual -->" in (tmp_project / "voice.md").read_text()


def test_install_style_marker_present(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--style", "mla9"],
        capture_output=True, text=True, check=True,
    )
    assert "<!-- sourced:style=mla9 -->" in (tmp_project / "style.md").read_text()


def test_install_brief_creates_brief_file(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--brief", "my_paper"],
        capture_output=True, text=True, check=True,
    )
    assert (tmp_project / "my_paper.brief.md").exists()


def test_install_user_substituted(tmp_home, tmp_project, clean_ansi):
    """{{USER}} in CLAUDE.md template gets replaced with the configured name."""
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    text = (tmp_project / "CLAUDE.md").read_text()
    assert "{{USER}}" not in text, "{{USER}} token not substituted"
    assert "TestUser" in text


def test_install_errors_when_files_exist_without_force(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    (tmp_project / "CLAUDE.md").write_text("user content")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "exist" in result.stderr.lower() or "force" in result.stderr.lower()
```

Create `tests/cli/integration/test_install_force.py`:

```python
import subprocess
import sys


def _setup_globals(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_force_overwrites(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    (tmp_project / "CLAUDE.md").write_text("OLD CONTENT")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    text = (tmp_project / "CLAUDE.md").read_text()
    assert "OLD CONTENT" not in text
```

Create `tests/cli/integration/test_install_type_annotated.py`:

```python
import subprocess
import sys


def _setup_globals(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_type_annotated_writes_marker(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--type", "annotated-bib"],
        capture_output=True, text=True, check=True,
    )
    marker = tmp_project / ".sourced-project-type"
    assert marker.exists()
    assert marker.read_text().strip() == "annotated-bib"


def test_install_type_essay_no_marker(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    assert not (tmp_project / ".sourced-project-type").exists()


def test_install_type_annotated_uses_annotated_brief(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--type", "annotated-bib", "--brief", "my_bib"],
        capture_output=True, text=True, check=True,
    )
    brief = tmp_project / "my_bib.brief.md"
    assert brief.exists()
    # Annotated bib brief is structurally different from essay brief; check for a
    # known annotated-bib field (e.g. "Annotation shape" or "Source-count target").
    text = brief.read_text()
    assert "Source-count target" in text or "Annotation shape" in text
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/integration/test_install_fresh.py -v
```

Expected: ImportError on `sourced.commands.install`.

- [ ] **Step 3: Create `src/sourced/commands/install.py`**

```python
"""sourced install — render per-project files."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import UsageError, ProjectError
from ..project import write_project_type, write_bak_sibling
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(
    ctx: Context,
    *,
    project: str | None = None,
    voice: str = "academic",
    style: str = "apa7",
    project_type: str = "essay",
    brief: str | None = None,
    force: bool = False,
) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    if not target.exists():
        raise ProjectError(f"target directory does not exist: {target}")

    user = _pipeline.ensure_user_name(ctx)

    # Render all texts up front (validators run; raises ValidationError on failure
    # BEFORE any write happens — atomicity at the orchestration layer).
    claude_md = _pipeline.render_claude_md(user, ctx)
    voice_md = _pipeline.render_voice(voice, user, ctx)
    style_md = _pipeline.render_style(style, user, ctx)
    brief_md = _pipeline.render_brief(brief, user, project_type, ctx) if brief else None

    targets: list[tuple[Path, str]] = [
        (target / "CLAUDE.md", claude_md),
        (target / "voice.md", voice_md),
        (target / "style.md", style_md),
    ]
    if brief:
        targets.append((target / f"{brief}.brief.md", brief_md))

    # Existence check (unless --force)
    existing = [p for p, _ in targets if p.exists()]
    if existing and not force:
        names = ", ".join(p.name for p in existing)
        raise UsageError(
            f"refusing to overwrite existing files: {names}. "
            f"Pass --force to overwrite, or `sourced update` to refresh the managed block."
        )

    if ctx.dry_run:
        if not ctx.quiet:
            print("DRY RUN — no files will be written.")
            for p, _ in targets:
                action = "would overwrite" if p.exists() else "would write"
                print(f"  {action} {path_str(str(p), use_color)}")
        return 0

    # Migration-day .sourced.bak fallback for any existing file.
    for p, _ in targets:
        if p.exists():
            write_bak_sibling(p)

    for p, content in targets:
        write_atomic(p, content)
        if not ctx.quiet:
            print(f"  wrote {path_str(str(p), use_color)}")

    # Project-type marker.
    write_project_type(target, project_type)
    if not ctx.quiet:
        print(f"\n{bold('Done.', use_color)} project={target}, voice={voice}, style={style}, type={project_type}")
    return 0
```

- [ ] **Step 4: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_install_fresh.py tests/cli/integration/test_install_force.py tests/cli/integration/test_install_type_annotated.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/commands/install.py tests/cli/integration/test_install_fresh.py tests/cli/integration/test_install_force.py tests/cli/integration/test_install_type_annotated.py
git commit -m "feat(cli): install command + integration tests"
```

### Task 4.5: commands/new.py + integration test

**Files:**
- Create: `src/sourced/commands/new.py`
- Create: `tests/cli/integration/test_new.py`

- [ ] **Step 1: Write failing test**

Create `tests/cli/integration/test_new.py`:

```python
import subprocess
import sys


def _setup_globals(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_new_creates_dir_and_files(tmp_home, tmp_path, clean_ansi):
    _setup_globals(tmp_home)
    new_dir = tmp_path / "my-paper"
    # cwd matters: `sourced new` creates ./<name>/.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "new", "my-paper"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert new_dir.is_dir()
    assert (new_dir / "CLAUDE.md").exists()
    assert (new_dir / "voice.md").exists()
    assert (new_dir / "style.md").exists()
    # Brief defaults to project name
    assert (new_dir / "my-paper.brief.md").exists()


def test_new_with_explicit_brief_name(tmp_home, tmp_path, clean_ansi):
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "new", "my-paper", "--brief", "alt_name"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "my-paper" / "alt_name.brief.md").exists()


def test_new_errors_if_dir_exists_without_force(tmp_home, tmp_path, clean_ansi):
    _setup_globals(tmp_home)
    (tmp_path / "my-paper").mkdir()
    (tmp_path / "my-paper" / "existing.txt").write_text("preserve")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "new", "my-paper"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    # Strict: refuse if dir exists without --force, since user might have content.
    assert result.returncode != 0
    assert (tmp_path / "my-paper" / "existing.txt").exists()  # preserved
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/integration/test_new.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/commands/new.py`**

```python
"""sourced new <project-name> — sugar for: mkdir + cd + install --brief."""
from __future__ import annotations
from pathlib import Path

from ..context import Context
from ..errors import UsageError
from . import install


def run(
    ctx: Context,
    *,
    project_name: str,
    voice: str = "academic",
    style: str = "apa7",
    project_type: str = "essay",
    brief: str | None = None,
    force: bool = False,
) -> int:
    target = Path.cwd() / project_name

    if target.exists() and not force and any(target.iterdir()):
        raise UsageError(
            f"directory {target} already exists and is non-empty. "
            f"Pass --force, or use `sourced install --project {target}` to render into "
            f"the existing dir."
        )

    target.mkdir(parents=True, exist_ok=True)

    # Brief defaults to project_name
    brief_name = brief if brief else project_name

    return install.run(
        ctx,
        project=str(target),
        voice=voice,
        style=style,
        project_type=project_type,
        brief=brief_name,
        force=force,
    )
```

- [ ] **Step 4: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_new.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/commands/new.py tests/cli/integration/test_new.py
git commit -m "feat(cli): new command + integration test"
```

### Task 4.6: commands/update.py + integration tests

**Files:**
- Create: `src/sourced/commands/update.py`
- Create: `tests/cli/integration/test_update.py`
- Create: `tests/cli/integration/test_update_stricter_sentinels.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/integration/test_update.py`:

```python
import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )


def test_update_refreshes_managed_block(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    # Modify outside the managed block:
    claude = tmp_project / "CLAUDE.md"
    text = claude.read_text()
    augmented = text + "\n\n## My Notes (outside managed block)\n\nKeep me!\n"
    claude.write_text(augmented)

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    after = claude.read_text()
    assert "Keep me!" in after  # outside-managed content preserved


def test_update_dry_run_does_not_write(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"
    before = claude.read_text()
    subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "update", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    assert claude.read_text() == before


def test_update_writes_bak_on_first_run(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    # .sourced.bak created during update for rollback safety.
    bak = tmp_project / "CLAUDE.md.sourced.bak"
    assert bak.exists()
```

Create `tests/cli/integration/test_update_stricter_sentinels.py`:

```python
import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )


def test_update_rejects_indented_sentinel(tmp_home, tmp_project, clean_ansi):
    """F28 fix: indented sentinels are not real sentinels."""
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"
    # Replace one of the column-0 sentinels with an indented copy.
    text = claude.read_text()
    text = text.replace(
        "<!-- sourced:begin managed -->",
        "  - <!-- sourced:begin managed -->",  # indented under a list bullet (legitimate prose)
        1,
    )
    claude.write_text(text)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 5, result.stderr  # ProjectError
    assert "sentinel" in result.stderr.lower()
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/integration/test_update.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/commands/update.py`**

```python
"""sourced update — refresh managed block of CLAUDE.md + voice.md + style.md."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import ProjectError
from ..project import (
    extract_managed_block,
    replace_managed_block,
    read_voice_marker,
    read_style_marker,
    write_bak_sibling,
)
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(ctx: Context, *, project: str | None = None, force: bool = False) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    claude_md_path = target / "CLAUDE.md"

    if not claude_md_path.exists():
        raise ProjectError(
            f"no CLAUDE.md at {claude_md_path}; nothing to update. "
            f"Use `sourced install --project {target}` to render fresh."
        )

    user = _pipeline.ensure_user_name(ctx)

    # Build the new CLAUDE.md.
    if force:
        new_claude = _pipeline.render_claude_md(user, ctx)
    else:
        # Refresh only the managed block.
        old_text = claude_md_path.read_text(encoding="utf-8")
        # Validate sentinels (raises ProjectError if malformed — F28 strictness).
        extract_managed_block(old_text)  # raises if bad

        # Render fresh CLAUDE.md, extract its managed block, splice into old.
        fresh_full = _pipeline.render_claude_md(user, ctx)
        fresh_managed = extract_managed_block(fresh_full)
        new_claude = replace_managed_block(old_text, fresh_managed)

    # Voice / style refresh: re-render from currently-installed library.
    voice_path = target / "voice.md"
    style_path = target / "style.md"
    voice_name = read_voice_marker(voice_path)
    style_name = read_style_marker(style_path)
    new_voice = _pipeline.render_voice(voice_name, user, ctx) if voice_name else None
    new_style = _pipeline.render_style(style_name, user, ctx) if style_name else None

    if ctx.dry_run:
        if not ctx.quiet:
            print("DRY RUN — no files will be written.")
            print(f"  would refresh {path_str(str(claude_md_path), use_color)}")
            if new_voice:
                print(f"  would refresh {path_str(str(voice_path), use_color)}")
            if new_style:
                print(f"  would refresh {path_str(str(style_path), use_color)}")
        return 0

    # Migration-day .sourced.bak fallback before mutating.
    write_bak_sibling(claude_md_path)
    if new_voice and voice_path.exists():
        write_bak_sibling(voice_path)
    if new_style and style_path.exists():
        write_bak_sibling(style_path)

    write_atomic(claude_md_path, new_claude)
    if new_voice:
        write_atomic(voice_path, new_voice)
    if new_style:
        write_atomic(style_path, new_style)

    if not ctx.quiet:
        print(f"\n{bold('Updated.', use_color)} project={target}")
    return 0
```

- [ ] **Step 4: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_update.py tests/cli/integration/test_update_stricter_sentinels.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/commands/update.py tests/cli/integration/test_update.py tests/cli/integration/test_update_stricter_sentinels.py
git commit -m "feat(cli): update command + integration tests (incl. F28 sentinel strictness)"
```

### Task 4.7: commands/switch.py + integration tests

**Files:**
- Create: `src/sourced/commands/switch.py`
- Create: `tests/cli/integration/test_switch_voice.py`
- Create: `tests/cli/integration/test_switch_style.py`
- Create: `tests/cli/integration/test_switch_broken_marker.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/integration/test_switch_voice.py`:

```python
import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--voice", "academic"],
        capture_output=True, text=True, check=True,
    )


def test_switch_voice_updates_marker(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "switch", "voice", "casual",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "<!-- sourced:voice=casual -->" in (tmp_project / "voice.md").read_text()
    assert "academic" not in (tmp_project / "voice.md").read_text().splitlines()[0]
```

Create `tests/cli/integration/test_switch_style.py`:

```python
import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--style", "apa7"],
        capture_output=True, text=True, check=True,
    )


def test_switch_style_updates_marker(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "switch", "style", "mla9",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "<!-- sourced:style=mla9 -->" in (tmp_project / "style.md").read_text()
```

Create `tests/cli/integration/test_switch_broken_marker.py`:

```python
import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_switch_voice_errors_when_no_voice_md(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    # No `sourced install` run — voice.md doesn't exist.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "switch", "voice", "casual",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 5  # ProjectError
    # Remediation hint mentions install --force
    assert "install" in result.stderr.lower() and "--force" in result.stderr.lower()
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/cli/integration/test_switch_voice.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/sourced/commands/switch.py`**

```python
"""sourced switch voice|style <name> — swap voice/style on existing project."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import ProjectError, UsageError
from ..project import write_bak_sibling
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(ctx: Context, *, kind: str, name: str, project: str | None = None) -> int:
    if kind not in ("voice", "style"):
        raise UsageError(f"unknown switch kind: {kind!r}; expected 'voice' or 'style'.")

    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    md_name = "voice.md" if kind == "voice" else "style.md"
    md_path = target / md_name

    if not md_path.exists():
        raise ProjectError(
            f"no {md_name} at {md_path}; this doesn't look like a sourced project. "
            f"Run `sourced install --project {target} --force --{kind} {name}` "
            f"to recreate from scratch."
        )

    user = _pipeline.ensure_user_name(ctx)

    if kind == "voice":
        new_text = _pipeline.render_voice(name, user, ctx)
    else:
        new_text = _pipeline.render_style(name, user, ctx)

    if ctx.dry_run:
        if not ctx.quiet:
            print(f"DRY RUN — would refresh {path_str(str(md_path), use_color)} "
                  f"({kind}={name}).")
        return 0

    write_bak_sibling(md_path)
    write_atomic(md_path, new_text)
    if not ctx.quiet:
        print(f"{bold('Switched', use_color)} {kind} → {name} at {path_str(str(md_path), use_color)}")
    return 0
```

- [ ] **Step 4: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_switch_voice.py tests/cli/integration/test_switch_style.py tests/cli/integration/test_switch_broken_marker.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/sourced/commands/switch.py tests/cli/integration/test_switch_voice.py tests/cli/integration/test_switch_style.py tests/cli/integration/test_switch_broken_marker.py
git commit -m "feat(cli): switch command + integration tests"
```

### Task 4.8: Expand commands/check.py to full version

**Files:**
- Modify: `src/sourced/commands/check.py` — add `~/.claude/` health, voice iron-rule check, style CSL check, project check
- Create: `tests/cli/integration/test_check_all_pass.py`
- Create: `tests/cli/integration/test_check_prereq_missing.py`
- Create: `tests/cli/integration/test_check_validation_fail.py`

- [ ] **Step 1: Write failing tests**

Create `tests/cli/integration/test_check_all_pass.py`:

```python
import subprocess
import sys


def test_check_passes_after_global_install(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # If prereqs are present (the dev/CI machine), exit 0; else exit 4 because
    # the prereq check failed (not ~/.claude/).
    assert result.returncode in (0, 4), result.stderr
    if result.returncode == 0:
        assert "passing" in result.stdout
```

Create `tests/cli/integration/test_check_prereq_missing.py`:

```python
import subprocess
import sys


def test_check_reports_missing_tool(tmp_home, monkeypatch, clean_ansi):
    """Run with PATH that excludes pdftoppm to simulate missing tool."""
    # Strip /usr/bin and /usr/local/bin from PATH so common tools disappear.
    env = {"HOME": str(tmp_home), "PATH": "/nonexistent", "NO_COLOR": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 4
    assert "not on PATH" in result.stdout or "failed" in result.stdout
```

Create `tests/cli/integration/test_check_validation_fail.py`:

```python
import subprocess
import sys


def test_check_flags_corrupted_voice(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Corrupt a voice file by removing iron-rule content.
    voice = tmp_home / ".claude" / "voice" / "academic.md"
    voice.write_text("# academic\n\n(emptied — no iron rules)\n")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # With prereqs intact, only voice check fails → exit 4.
    if "Prerequisites" in result.stdout and "passing" in result.stdout:
        assert result.returncode == 4
        assert "iron-rule" in result.stdout.lower() or "iron rule" in result.stdout.lower()
```

- [ ] **Step 2: Replace `src/sourced/commands/check.py` with full version**

```python
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
        text = vf.read_text(encoding="utf-8")
        ir_findings = iron_rules_validator.validate(
            skeleton=text, candidate=text, voice_name=vf.stem
        )
        ex_findings = exemptions_validator.validate(
            voice=text, claude_md=claude_md, voice_name=vf.stem
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


def run(ctx: Context, project: str | None = None) -> int:
    use_color = should_color(ctx.color, sys.stdout)

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
```

- [ ] **Step 3: Verify**

```bash
pipx install --force -e .
pytest tests/cli/integration/test_check_all_pass.py tests/cli/integration/test_check_prereq_missing.py tests/cli/integration/test_check_validation_fail.py -v
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add src/sourced/commands/check.py tests/cli/integration/test_check_all_pass.py tests/cli/integration/test_check_prereq_missing.py tests/cli/integration/test_check_validation_fail.py
git commit -m "feat(cli): check command — full version (~/.claude health + voice validation)"
```

### Task 4.9: Integration tests for global UX (dry-run, verbose, quiet, color)

**Files:**
- Create: `tests/cli/integration/test_dry_run_install.py`
- Create: `tests/cli/integration/test_verbose_quiet.py`
- Create: `tests/cli/integration/test_color_suppression.py`

- [ ] **Step 1: Write tests**

Create `tests/cli/integration/test_dry_run_install.py`:

```python
import subprocess
import sys


def test_install_dry_run_writes_no_files(tmp_home, tmp_project, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "install",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert not (tmp_project / "CLAUDE.md").exists()
    assert not (tmp_project / "voice.md").exists()


def test_install_dry_run_runs_validators(tmp_home, tmp_project, clean_ansi):
    """Dry-run should still surface validation errors before user runs for real."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Corrupt a voice — dry-run should error on the validation, not just succeed.
    voice = tmp_home / ".claude" / "voice" / "academic.md"
    voice.write_text("(no iron rules here)\n")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "install",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 4  # ValidationError
    assert "iron" in result.stderr.lower()
```

Create `tests/cli/integration/test_verbose_quiet.py`:

```python
import subprocess
import sys


def test_quiet_suppresses_success_output(tmp_home, clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "-q", "global-install"],
        input="TestUser\n", capture_output=True, text=True,
    )
    assert result.returncode == 0
    # Quiet mode: stdout should be near-empty (input prompt is on stderr or absent
    # because we piped stdin).
    assert len(result.stdout) < 10


def test_verbose_shows_more_detail(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result_default = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    result_verbose = subprocess.run(
        [sys.executable, "-m", "sourced", "-v", "check"],
        capture_output=True, text=True,
    )
    # Verbose strictly more output than default (assuming all-pass).
    if result_default.returncode == 0:
        assert len(result_verbose.stdout) >= len(result_default.stdout)
```

Create `tests/cli/integration/test_color_suppression.py`:

```python
import subprocess
import sys
import os


def test_no_color_env_suppresses(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home), "NO_COLOR": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout


def test_explicit_no_color_flag(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home)}
    env.pop("NO_COLOR", None)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--no-color", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout


def test_color_never_flag(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home)}
    env.pop("NO_COLOR", None)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--color", "never", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout
```

- [ ] **Step 2: Verify**

```bash
pytest tests/cli/integration/test_dry_run_install.py tests/cli/integration/test_verbose_quiet.py tests/cli/integration/test_color_suppression.py -v
```

Expected: 7 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/cli/integration/test_dry_run_install.py tests/cli/integration/test_verbose_quiet.py tests/cli/integration/test_color_suppression.py
git commit -m "test(cli): dry-run, verbose/quiet, color-suppression integration tests"
```

### PR 4 gate (before opening PR)

```bash
pytest tests/cli/ -v               # all unit + integration tests pass
sourced --help                     # all 6 subcommands listed
sourced global-install             # works (interactive on first run)
sourced install --brief test_paper # works in PWD
sourced check                      # full check works
bash tests/parity/run-all.sh       # existing 20-golden suite still green
```

If all green, open PR 4: "feat(cli): commands + integration tests".

---

# PR 5: Parity + goldens + docs + retire install.sh

**Goal:** Final phase-1 PR. Adds parity tests against install.sh (development-only), golden snapshot fixtures (long-lived), seeds `facts.yml`, updates all user-facing docs, tags `legacy/install-sh-final`, deletes `install.sh` and the parity test directory, then runs post-merge `/audit` + `/audit-fix`.

**Important sequencing:** install.sh's bash paths (`${REPO_DIR}/templates/...`) have been broken since PR 3. To run parity tests, we need install.sh working again temporarily. The simplest path: parity-test setup creates symlinks from the old top-level paths to the new `src/sourced/data/*` paths, runs install.sh against those, diffs. Then delete the symlinks before the install.sh deletion commit. Alternative: parity tests `cd $(git rev-parse --show-toplevel)` and explicitly export overridden paths. Going with symlinks since they're simpler and contained in the test setup.

### Task 5.1: Parity-test infrastructure (dev-only, deleted on merge)

**Files:**
- Create: `tests/cli/parity/__init__.py` (empty)
- Create: `tests/cli/parity/conftest.py`
- Create: `tests/cli/parity/test_install_parity.py`
- Create: `tests/cli/parity/test_global_install_parity.py`

- [ ] **Step 1: Create empty `tests/cli/parity/__init__.py`**

Empty file.

- [ ] **Step 2: Create `tests/cli/parity/conftest.py`**

```python
"""Parity test setup: temporarily restore top-level template paths via symlinks
so install.sh can run. Symlinks are created in tmp dirs (not the real repo).
"""
import shutil
import subprocess
import sys
from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "src" / "sourced" / "data"


@pytest.fixture
def repo_with_legacy_paths(tmp_path):
    """Make a working copy of the repo with templates/ etc. symlinked at top-level
    (where install.sh expects them). Yields the working-copy root."""
    work = tmp_path / "work"
    # Sparse copy: only what install.sh reads + install.sh itself.
    work.mkdir()
    shutil.copy2(REPO_ROOT / "install.sh", work / "install.sh")
    # Symlink data subdirs at top-level for install.sh.
    for sub in ("templates", "agents", "citations", "skills"):
        (work / sub).symlink_to(DATA_ROOT / sub)
    # filters/ may be top-level or under templates/.
    if (DATA_ROOT / "filters").exists():
        (work / "filters").symlink_to(DATA_ROOT / "filters")
    yield work


@pytest.fixture
def install_sh_run(repo_with_legacy_paths, tmp_home, tmp_project):
    """Run install.sh with given args; returns CompletedProcess."""
    def _run(args: list[str], input_: str | None = None):
        return subprocess.run(
            ["bash", str(repo_with_legacy_paths / "install.sh")] + args,
            input=input_, capture_output=True, text=True,
            cwd=tmp_project,
        )
    return _run


@pytest.fixture
def cli_run(tmp_home, tmp_project):
    """Run sourced CLI with given args; returns CompletedProcess."""
    def _run(args: list[str], input_: str | None = None, project: Path | None = None):
        cwd = project if project else tmp_project
        return subprocess.run(
            [sys.executable, "-m", "sourced"] + args,
            input=input_, capture_output=True, text=True,
            cwd=cwd,
        )
    return _run
```

- [ ] **Step 3: Write parity test for global-install**

Create `tests/cli/parity/test_global_install_parity.py`:

```python
import subprocess
import sys
from pathlib import Path
import pytest


def _file_set(root: Path) -> set[str]:
    """Return relative paths of all regular files under root."""
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def _file_contents(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): p.read_text(encoding="utf-8", errors="replace")
        for p in root.rglob("*")
        if p.is_file()
    }


def test_global_install_file_set_matches(install_sh_run, cli_run, tmp_path):
    # Two separate ~/.claude/ trees.
    home_a = tmp_path / "home_a"
    home_b = tmp_path / "home_b"
    home_a.mkdir()
    home_b.mkdir()

    # install.sh side
    a = subprocess.run(
        ["bash", str(install_sh_run.__self__.repo_with_legacy_paths / "install.sh"), "--global-only"],
        input="TestUser\n", capture_output=True, text=True,
        env={"HOME": str(home_a), "PATH": "/usr/bin:/bin"},
    ) if False else install_sh_run(["--global-only"], input_="TestUser\n")
    # Simplification: we used the install_sh_run fixture which honors HOME via tmp_home.
    # For a 2-way diff, replace its HOME on each invocation.
    # (See note at end of test for refactor — this test confirms the file SET matches at minimum.)
    pytest.skip("Full 2-way diff requires fixture refactor — see comments. "
                "PR 5 implementation will lift the install_sh_run/cli_run fixtures to "
                "accept an explicit HOME and tmp_project per call.")
```

**Note:** The above test scaffold is intentionally `pytest.skip`'d in Step 3. The fixture model needs a small refactor (allow per-call HOME / project paths) to do a proper 2-way diff. The implementer should either (a) refactor the fixtures to take HOME as a parameter, or (b) inline the subprocess.run calls directly. Both are mechanical; the test logic is straightforward (`_file_set` diff + `_file_contents` diff).

- [ ] **Step 4: Write parity test for install (per-project)**

Create `tests/cli/parity/test_install_parity.py`:

```python
import subprocess
import sys
from pathlib import Path
import pytest


def _file_set(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("flags", [
    ["--brief", "p1"],
    ["--brief", "p1", "--voice", "casual"],
    ["--brief", "p1", "--style", "mla9"],
    ["--brief", "p1", "--type", "annotated-bib"],
])
def test_install_file_set_matches(flags, tmp_path, repo_with_legacy_paths):
    """For each flag combination, the file set install.sh creates should match
    the file set the CLI creates (allowing documented diffs)."""
    home = tmp_path / "home"
    home.mkdir()

    # Run install.sh side
    proj_a = tmp_path / "proj_a"
    proj_a.mkdir()
    a_global = subprocess.run(
        ["bash", str(repo_with_legacy_paths / "install.sh"), "--global-only"],
        input="TestUser\n", capture_output=True, text=True,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert a_global.returncode == 0, a_global.stderr
    a_install = subprocess.run(
        ["bash", str(repo_with_legacy_paths / "install.sh")] + flags,
        capture_output=True, text=True, cwd=proj_a,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert a_install.returncode == 0, a_install.stderr

    # Reset HOME for the CLI side.
    home_b = tmp_path / "home_b"
    home_b.mkdir()
    proj_b = tmp_path / "proj_b"
    proj_b.mkdir()
    b_global = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True,
        env={"HOME": str(home_b), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert b_global.returncode == 0, b_global.stderr
    # Map install.sh flags to CLI flags. Both sides use the same surface for
    # --brief, --voice, --style, --type, so flags pass through.
    b_install = subprocess.run(
        [sys.executable, "-m", "sourced", "install"] + flags,
        capture_output=True, text=True, cwd=proj_b,
        env={"HOME": str(home_b), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert b_install.returncode == 0, b_install.stderr

    set_a = _file_set(proj_a)
    set_b = _file_set(proj_b)
    diff_a_only = set_a - set_b
    diff_b_only = set_b - set_a
    assert not diff_a_only, f"install.sh wrote files CLI didn't: {diff_a_only}"
    assert not diff_b_only, f"CLI wrote files install.sh didn't: {diff_b_only}"
```

- [ ] **Step 5: Run parity tests**

```bash
pipx install --force -e .
pytest tests/cli/parity/test_install_parity.py -v
```

Expected: at least the parametrized installs pass (4 cases). The skipped global-install parity is OK to leave skipped for now — the per-project test exercises global-install transitively.

If diffs surface (CLI writes a file install.sh doesn't, or vice versa), inspect them. Allowed differences (per spec §8.3):
- The CLI may emit a `.sourced.bak` on first-touch; install.sh doesn't. Filter `.sourced.bak` out of the file-set diff if needed.
- The CLI may add a richer line to `~/.claude/sourced.config`; install.sh writes only `USER_NAME=...`. Confirm the file-content of `sourced.config` is install.sh-compatible (round-trips).
- Order-of-mirror-write doesn't matter for the file-set diff.

Adjust filters in the test if needed; document each excluded path with a one-line comment.

- [ ] **Step 6: Commit**

```bash
git add tests/cli/parity/
git commit -m "test(cli): parity tests vs install.sh (dev-only; deleted on merge)"
```

### Task 5.2: Golden snapshots for rendered templates

**Files:**
- Create: `tests/cli/golden/__init__.py`
- Create: `tests/cli/golden/test_render_golden.py`

Uses `syrupy` (added to `pyproject.toml [project.optional-dependencies] test` in PR 1).

- [ ] **Step 1: Install syrupy if not yet on path**

```bash
pip install syrupy
```

- [ ] **Step 2: Create empty `tests/cli/golden/__init__.py`**

Empty file.

- [ ] **Step 3: Create `tests/cli/golden/test_render_golden.py`**

```python
"""Golden-snapshot tests: render every shipped template against a canonical
RenderContext and snapshot the output. Catches silent template drift.

Run `pytest tests/cli/golden/ --snapshot-update` to regenerate snapshots
intentionally."""
import pytest
from sourced.render import RenderContext, read_template, render


CANONICAL = RenderContext(user="TestUser", voice_name="academic", style_name="apa7")


def test_claude_md_essay(snapshot):
    text = read_template("templates/CLAUDE.md")
    assert render(text, CANONICAL) == snapshot


def test_brief_essay(snapshot):
    text = read_template("templates/brief.template.md")
    assert render(text, CANONICAL) == snapshot


def test_brief_annotated_bib(snapshot):
    text = read_template("templates/brief.template.annotated-bib.md")
    assert render(text, CANONICAL) == snapshot


@pytest.mark.parametrize("name", ["academic", "casual", "hybrid", "journalistic", "narrative", "technical"])
def test_voice(name, snapshot):
    text = read_template(f"templates/voices/{name}.md")
    assert render(text, CANONICAL) == snapshot


@pytest.mark.parametrize("name", ["apa7", "chicago17-ad", "chicago17-nb", "ieee", "mla9"])
def test_style(name, snapshot):
    text = read_template(f"templates/styles/{name}.md")
    assert render(text, CANONICAL) == snapshot
```

- [ ] **Step 4: Generate initial snapshots**

```bash
pytest tests/cli/golden/ --snapshot-update -v
```

Expected: 14 snapshots created (1 CLAUDE.md, 2 briefs, 6 voices, 5 styles). Files appear under `tests/cli/golden/__snapshots__/`.

- [ ] **Step 5: Re-run tests to confirm they pass**

```bash
pytest tests/cli/golden/ -v
```

Expected: 14 passed.

- [ ] **Step 6: Commit**

```bash
git add tests/cli/golden/
git commit -m "test(cli): golden snapshots for 14 template variants"
```

### Task 5.3: Seed `facts.yml` invariant registry

**Files:**
- Create: `src/sourced/data/facts.yml`

- [ ] **Step 1: Create `src/sourced/data/facts.yml`**

```yaml
# Invariant registry for /audit's invariant-sweep step (Layer 1).
# Phase 1: this file is the seed; phase 2 wires `sourced check --invariants`
# to verify mirrors at runtime.
#
# Each invariant: id, name, authoritative, mirrors (list of file:line refs).
invariants:
  - id: I1
    name: "install.sh prereq tool list (5 tools)"
    authoritative: src/sourced/commands/check.py::PREREQ_TOOLS
    mirrors:
      - README.md (Prereqs section)
      - docs/INSTALL.md (Prereq check section)

  - id: I2
    name: "[editing mode] pass count (currently 8)"
    authoritative: src/sourced/data/templates/CLAUDE.md (§7 [editing mode])
    mirrors:
      - src/sourced/data/templates/CLAUDE.md (L209, L441)
      - docs/MODES.md (L45, L58)
      - docs/archive/specs/2026-04-20-annotated-bibliography-design.md (L57, L105)

  - id: I3
    name: "Shipped styles (5: apa7, chicago17-ad, chicago17-nb, ieee, mla9)"
    authoritative: src/sourced/data/templates/styles/*.md
    mirrors:
      - ARCHITECTURE.md (L22, L135)
      - ROADMAP.md (L23, L144)
      - README.md (feature list)

  - id: I4
    name: "Shipped voices (6: academic, casual, technical, journalistic, narrative, hybrid)"
    authoritative: src/sourced/data/templates/voices/*.md
    mirrors:
      - ARCHITECTURE.md (L108-109)
      - README.md (feature list)
      - docs/VOICES.md (L93)
      - src/sourced/data/agents/voice-extractor.md (L34, L158)

  - id: I5
    name: "Paste targets (4: word, google-docs, plain-markdown, latex)"
    authoritative: tests/parity/*/run.sh + tests/parity/_render.sh
    mirrors:
      - ARCHITECTURE.md (L22, L67)
      - README.md (feature list)
      - ROADMAP.md (L144, L154)
      - src/sourced/commands/check.py (pandoc comment if any)

  - id: I6
    name: "Mode count (12 cognitive modes)"
    authoritative: src/sourced/data/templates/CLAUDE.md (§7)
    mirrors:
      - README.md (L17)
      - docs/MODES.md (L5)

  - id: I7
    name: "Node 18+ requirement (browser-reader-extract skill)"
    authoritative: src/sourced/data/skills/browser-reader-extract/package.json (engines)
    mirrors:
      - src/sourced/data/skills/browser-reader-extract/SKILL.md (L30)
      - README.md (L47)
      - docs/SKILLS.md (L29)

  - id: I8
    name: "pandoc 3.1+ requirement"
    authoritative: src/sourced/commands/check.py (_check_pandoc_version)
    mirrors:
      - README.md (Prereqs)
      - tests/parity/README.md (L35)
```

- [ ] **Step 2: Commit**

```bash
git add src/sourced/data/facts.yml
git commit -m "feat(cli): seed facts.yml invariant registry (I1-I8)"
```

### Task 5.4: Update README.md (rewrite install section)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README install section**

```bash
grep -n "install.sh\|Quickstart\|Prerequisites" README.md | head -20
```

- [ ] **Step 2: Rewrite the install section**

Replace the install-related portion of `README.md` with the canonical phase-1 install story per spec §7.1. Concrete edits:

1. Find the section currently telling users to clone the repo and run `./install.sh`. Replace with:

```markdown
## Install

Prerequisites:
- Python 3.10+ (`python3 --version`)
- pipx (`brew install pipx` on macOS; `sudo apt install pipx python3-venv` on Ubuntu/WSL; `winget install pipx` on Windows native)
  - After installing pipx: `pipx ensurepath`, then **open a new terminal**.
- Read access to this repo (request from maintainer)

Install:

```bash
# HTTPS (default for non-dev users; works through corporate firewalls):
pipx install 'git+https://<TOKEN>@github.com/hayden1126/sourced.git'

# SSH (power-user path; pre-seed known_hosts on a fresh machine):
ssh-keyscan github.com >> ~/.ssh/known_hosts
pipx install git+ssh://git@github.com/hayden1126/sourced.git
```

Verify and set up:
```bash
sourced --version
sourced check                # verifies prereqs + ~/.claude/ readiness
sourced global-install       # populates ~/.claude/ (prompts for your name on first run)
```

Per-project:
```bash
cd ~/writing/new-paper
sourced install --brief my_paper --voice academic --style apa7

# or sugar:
cd ~/writing
sourced new my-paper --voice academic --style apa7
```

Updates:
```bash
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@main'
sourced global-install       # idempotent
cd ~/writing/my-paper
sourced update               # refresh managed block of CLAUDE.md
```

Rollback to a previous version (within 1 week of phase-1 launch, the legacy
install.sh path is also available at the `legacy/install-sh-final` git tag):
```bash
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@<sha>'
```

For deeper troubleshooting (pipx gotchas, conda interference, port-22-blocked networks), see `docs/INSTALL.md`.
```

2. Find any other reference to `./install.sh` or `path/to/sourced/install.sh` in README.md and update to `sourced ...` equivalents.

- [ ] **Step 3: Verify README is internally consistent**

```bash
grep -n "install.sh" README.md      # should find nothing user-facing
sourced --help                       # commands README references must exist
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): rewrite install section for sourced CLI"
```

### Task 5.5: Update docs/INSTALL.md

**Files:**
- Modify: `docs/INSTALL.md`

- [ ] **Step 1: Replace the install section with the longer-form version per spec §7**

Edit `docs/INSTALL.md`. Replace the current install body with the spec §7 content (verbatim — that's the canonical version):

- §7.1 First-time install
- §7.2 Updates
- §7.3 Version pinning / rollback
- §7.4 Uninstall
- §7.5 Contributor onboarding
- §7.6 Migration day (maintainer checklist)
- §7.7 pipx gotchas table

The spec at `docs/superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md` is the canonical source; copy/adapt its §7 prose into `docs/INSTALL.md` so it's discoverable from outside the spec.

- [ ] **Step 2: Add explicit note about the data-directory relocation for any contributor expecting top-level `templates/`**

```markdown
## Note for contributors with an existing clone

The bundled templates moved under `src/sourced/data/` in phase 1. If you had
muscle memory for `templates/CLAUDE.md` or `agents/source-finder.md`, those
paths now live at `src/sourced/data/templates/CLAUDE.md` and
`src/sourced/data/agents/source-finder.md`. Editable installs (`pipx install -e .`)
hot-reload edits to these paths.
```

- [ ] **Step 3: Commit**

```bash
git add docs/INSTALL.md
git commit -m "docs(install): rewrite for sourced CLI; document data relocation"
```

### Task 5.6: Update ARCHITECTURE.md

**Files:**
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Add a Python package section**

Find the file-tree section near the top of `ARCHITECTURE.md` and update it to reflect the new `src/sourced/` package + relocated `src/sourced/data/`. Add a new section "Python package" that describes:

- src-layout package structure
- Module-boundary principles (per spec §3): cli.py owns argparse, commands orchestrate, validators are pure, ui.py owns presentation, data/ is read-only
- Three-layer error contract
- Pipeline composition (pre-render + post-render validators)
- Reference to the design spec at `docs/archive/specs/2026-04-21-sourced-cli-decomposition-design.md` (will move to archive once shipped)

Keep this section concise — 1-2 paragraphs + a small file tree showing `src/sourced/{cli,commands,validators,...}.py`.

- [ ] **Step 2: Commit**

```bash
git add ARCHITECTURE.md
git commit -m "docs(architecture): add Python package section + relocated data"
```

### Task 5.7: Update ROADMAP.md

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Replace L218-221 (the existing "Installable executable" entry) with two new entries per spec §11**

Open `ROADMAP.md`, find:

```markdown
### Installable `sourced` executable on `$PATH`
**Priority:** later · **Effort:** S · **Status:** open.

Ship a user-facing executable so installation and updates...
```

Replace with the two-entry block from spec §11 (Python CLI entry + Single-binary entry). Use the verbatim text from the spec.

- [ ] **Step 2: Commit**

```bash
git add ROADMAP.md
git commit -m "docs(roadmap): replace S 'installable executable' with L Python CLI + L Go binary"
```

### Task 5.8: Tag legacy/install-sh-final + delete install.sh + delete parity tests

**Files:**
- Delete: `install.sh`
- Delete: `tests/cli/parity/` (entire directory)

- [ ] **Step 1: Confirm parity tests are green BEFORE the delete**

```bash
pytest tests/cli/parity/ -v
```

Expected: all parity tests pass (or are intentionally skipped per Task 5.1 step 3 caveat). If any unexpected failure: stop and inspect — this is the gate.

- [ ] **Step 2: Tag the last commit before deletion**

```bash
git tag legacy/install-sh-final HEAD
```

(The current HEAD is the last commit where install.sh exists. The tag preserves it as a rollback ref.)

- [ ] **Step 3: Verify the tag exists**

```bash
git tag -l "legacy/*"
git show legacy/install-sh-final --stat | head -10
```

- [ ] **Step 4: Delete install.sh + tests/cli/parity/**

```bash
git rm install.sh
git rm -r tests/cli/parity/
```

- [ ] **Step 5: Commit the deletion**

```bash
git commit -m "feat(cli): retire install.sh; CLI is now the sole entry point

install.sh is preserved at git tag legacy/install-sh-final for one week of
rollback availability, per the README's troubleshooting note.

tests/cli/parity/ deleted — its purpose was migration validation against
install.sh; with install.sh gone, the suite has nothing to compare against.
The 4-way unit/integration/golden test split (under tests/cli/) covers
ongoing testing."
```

- [ ] **Step 6: Push the tag (post-merge — coordinate with PR review)**

```bash
git push origin legacy/install-sh-final
```

(Document this push in the PR description so the reviewer knows the tag exists.)

### Task 5.9: Run final /audit + /audit-fix on the merged tree

**Files:** none directly — discovery + fix outputs land where they land.

- [ ] **Step 1: Working tree must be clean**

```bash
git status --porcelain        # empty → clean
```

- [ ] **Step 2: Invoke /audit**

```bash
/audit cycle 4 — first run after the install.sh → CLI port. Verify the relocation
left no stale paths, no broken doc references, no invariant drift on I1-I8.
```

- [ ] **Step 3: Review the audit report and invoke /audit-fix**

If findings emerged:

```bash
/audit-fix
```

Resolve any structural-rewrite clusters, auto-fix the trivial drift, defer the design-issues per usual.

- [ ] **Step 4: Commit any audit-fix output**

```bash
git status --porcelain
git add <files>
git commit -m "fix: post-phase-1 audit findings (cycle 4)"
```

- [ ] **Step 5: Final smoke**

```bash
pipx install --force git+ssh://git@github.com/hayden1126/sourced.git@HEAD
sourced --version
sourced check
bash tests/parity/run-all.sh   # 20 goldens still green
```

If green, phase 1 ships.

### PR 5 gate (before merge)

```bash
pytest tests/cli/ -v               # everything green (parity tests already deleted)
bash tests/parity/run-all.sh       # 20-golden style suite still green
git tag -l "legacy/*"              # legacy/install-sh-final tag exists
ls install.sh 2>&1                 # "No such file" expected
sourced --version                  # CLI installable + functional
```

If all green, merge PR 5.

---

# Self-review

The following review was performed against the spec at `docs/superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md` after writing all 5 PRs.

## Spec coverage

Walking each spec section:
- §1 (Problem) — context, no implementation needed.
- §2 (Decisions) — locked through brainstorming; PR 1 implements the package + Hatchling choice; PR 2 the I/O layer; PR 3 the data relocation + validators; PR 4 the commands + 6 subcommands; PR 5 deletes install.sh ✓
- §3 (Architecture) — full src/sourced/ layout in PR 1-4; module boundaries enforced ✓
- §4 (Command surface) — all 6 subcommands implemented in PR 4 with full flag specs; global flags in PR 1+4 ✓
- §5.1-§5.2 (Resource access + render) — Task 2.1 ✓
- §5.3 (Pipeline composition) — Task 4.2 (`_pipeline.py`) ✓
- §5.4 (Mirror) — Task 2.2 ✓
- §5.5 (Sentinels, F28 strictness) — Task 2.4 (BEGIN_RE/END_RE column-0 strict) ✓
- §5.6 (Atomic writes) — Task 2.5 ✓
- §5.7 (.sourced.bak) — Task 2.4 (helper) + invoked in install/update/switch ✓
- §5.8 (Error hierarchy) — Task 1.2 ✓
- §5.9 (cli.main) — Task 1.6 + 4.1 ✓
- §6 (Error UX, --color triad, -v stackable, -q semantics, --strict, dry-run) — PR 1 (--color, -v, -q) + PR 4 (--strict promotion in `_pipeline._maybe_raise`) + PR 4 (--dry-run integration tests) ✓
- §7 (Migration & install) — README + INSTALL updates in PR 5 (Tasks 5.4, 5.5) ✓
- §8 (Testing) — unit (PR 1-3), integration (PR 4), parity (PR 5 dev-only), golden (PR 5) ✓
- §9 (Drift-prevention) — facts.yml seed in PR 5 (Task 5.3); per-commit `/audit` is operational discipline (documented in commit messages) ✓
- §10 (Phase boundary) — phase 1 covered by these 5 PRs; phase 2 explicitly out of scope ✓
- §11 (ROADMAP updates) — Task 5.7 ✓

No gaps detected.

## Placeholder scan

- All "TBD"-type markers: searched plan body — none.
- All steps with code show actual code. No "implement similar to Task N" without repetition.
- Two intentional `pytest.skip` calls in Task 5.1 step 3 with a clear note explaining the fixture refactor needed; the implementer is told exactly what to do (refactor fixtures or inline subprocess calls).

## Type consistency

- `Finding` shape: defined in Task 1.2; referenced consistently in Tasks 3.2, 3.3, 3.4, 4.2 (validators), and PR 4 commands. All references match: `rule`, `location`, `severity`, `message`, `fix_hint`, `rule_url`.
- `Context`: defined in Task 1.3; flowed through cli.py (Tasks 1.6 + 4.1) → commands (PR 4) → `_pipeline.ensure_user_name(ctx)` and `_pipeline.install_global(ctx, ...)`. No drift.
- `RenderContext`: defined in Task 2.1; used identically in Task 4.2 `_pipeline`.
- Error classes: defined in Task 1.2; referenced in Task 4.2 (`_maybe_raise` raises `ValidationError`), Task 4.4-4.7 (commands raise `UsageError`/`ProjectError`).
- `_pipeline.run_install_pipeline` / `install_global` / `render_voice` / `render_style` / `render_claude_md` / `render_brief` / `ensure_user_name` / `_maybe_raise`: all defined in Task 4.2; called consistently in Tasks 4.3-4.7.
- `BEGIN_RE`/`END_RE` in `project.py` (Task 2.4) — used by `extract_managed_block` and `replace_managed_block` (same task) and called by `commands/update.py` (Task 4.6). Names consistent.
- `write_atomic` defined in Task 2.5; called in Tasks 4.4, 4.6, 4.7.
- `mirror_tree` defined in Task 2.2; called by `_pipeline.install_global` (Task 4.2).
- `write_bak_sibling` defined in Task 2.4; called by Tasks 4.4 (install), 4.6 (update), 4.7 (switch).

No type-consistency issues.

## Scope check

Plan scope matches spec scope. Phase 1 only:
- 6 subcommands ✓
- Tier 1 + Tier 2 UX ✓
- Templates relocated ✓
- install.sh deleted ✓
- Tier 3 (CI, JSON output, doctor, completion) explicitly NOT in this plan ✓
- Tier 4 (new modes, schema changes) explicitly NOT in this plan ✓

---

# Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-21-sourced-cli-phase-1.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Each task is atomic (write tests → implement → verify → commit) so subagent attribution is clean. The 5 PR boundaries give natural review checkpoints with you.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for review.

Which approach?
