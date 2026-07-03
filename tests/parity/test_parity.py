"""Pytest wrapper for the parity harness: every shipped style x paste target.

All render and diff logic lives in _render.sh; this file parametrizes it and
surfaces failures. Goldens are byte-compared pandoc output, so results are
pinned to the pandoc version in PANDOC_VERSION (see README.md for the
upgrade policy).
"""
import shutil
import subprocess
import warnings
from pathlib import Path

import pytest

PARITY_DIR = Path(__file__).parent
RENDER = PARITY_DIR / "_render.sh"
PINNED_PANDOC = (PARITY_DIR / "PANDOC_VERSION").read_text().strip()

STYLES = sorted(p.parent.name for p in PARITY_DIR.glob("*/fixture.pandoc.md"))

# (target, output ext, extra pandoc args). -t markdown-citations forces
# citeproc to render citations into the markdown writer's output; plain
# -t markdown would round-trip [@id] unchanged and drop the bibliography,
# making the harness trivially-passing.
TARGETS = [
    ("plain-markdown", "md", ["--wrap=preserve", "-t", "markdown-citations-header_attributes-smart"]),
    ("google-docs", "md", ["--wrap=none", "-t", "markdown-citations-header_attributes-smart"]),
    ("word", "docx.md", ["-t", "markdown-citations"]),
    ("latex", "tex", ["-t", "latex"]),
]

pytestmark = [
    pytest.mark.parity,
    pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not on PATH"),
]


@pytest.fixture(scope="session", autouse=True)
def _warn_on_pandoc_drift():
    """Warn (never skip) when local pandoc differs from the golden pin."""
    if shutil.which("pandoc") is None:
        return
    first_line = subprocess.run(
        ["pandoc", "--version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    installed = first_line.removeprefix("pandoc ").strip()
    if installed != PINNED_PANDOC:
        warnings.warn(
            f"local pandoc is {installed}; goldens are pinned to {PINNED_PANDOC} "
            "(tests/parity/PANDOC_VERSION). Golden diffs may be pandoc drift, "
            "not regressions."
        )


@pytest.mark.parametrize("target,ext,flags", TARGETS, ids=[t[0] for t in TARGETS])
@pytest.mark.parametrize("style", STYLES)
def test_parity(style, target, ext, flags):
    result = subprocess.run(
        ["bash", str(RENDER), str(PARITY_DIR / style), target, ext, *flags],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"[{style}] {target} parity failure (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
