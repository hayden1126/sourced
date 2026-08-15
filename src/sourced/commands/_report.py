"""Shared diagnostic-report primitives for `check` and `doctor`.

Both commands present findings brew-doctor style: a one-line `Name: N/M passing`
when a section is all-pass and not verbose, an expanded per-row list (✓ / ! / ✗ / ·
plus optional detail and a `→ fix:` line) whenever the section has any problem or
under -v, nothing under --quiet. This module is the single source for that shape so
the two commands never drift in presentation.

Status vocabulary: pass / warn / fail, plus skip for a check that verified nothing
(not-applicable in this environment). skip rows are shown only under -v and never
counted toward the N/M-passing summary. `fix` carries the remediation as a separate
field so it renders on its own line rather than being concatenated into `detail`.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from ..ui import ok, err, warn, bold, path_str


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Literal["pass", "fail", "warn", "skip"]
    detail: str | None = None
    fix: str | None = None


def print_section(name: str, results: list[CheckResult], use_color: bool, verbose: int) -> None:
    if not results:
        return
    # A warning is a problem: expand the section for any fail OR warn, so a
    # warn-only section is never silently collapsed to "N/M passing".
    problems = [r for r in results if r.status in ("fail", "warn")]
    countable = [r for r in results if r.status != "skip"]
    pass_count = sum(1 for r in results if r.status == "pass")
    if verbose >= 1 or problems:
        print(bold(f"{name}:", use_color))
        for r in results:
            # pass/skip rows are noise unless the user asked for the full dump.
            if r.status in ("pass", "skip") and verbose < 1:
                continue
            if r.status == "pass":
                marker = ok("✓", use_color)
            elif r.status == "warn":
                marker = warn("!", use_color)
            elif r.status == "fail":
                marker = err("✗", use_color)
            else:  # skip
                marker = path_str("·", use_color)
            detail = f" — {r.detail}" if r.detail else ""
            print(f"  {marker} {r.name}{detail}")
            if r.fix:
                print(f"      {path_str('→ fix:', use_color)} {r.fix}")
    else:
        print(f"{bold(name + ':', use_color)} {pass_count}/{len(countable)} passing")
