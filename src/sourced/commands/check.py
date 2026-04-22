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
