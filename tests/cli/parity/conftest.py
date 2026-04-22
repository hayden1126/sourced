"""Parity test setup: reconstruct the pre-PR-3 top-level template layout via
symlinks so install.sh can run after the data relocation.

In the old layout (which install.sh's paths still expect):
  templates/voices/, templates/styles/, templates/filters/, templates/CLAUDE.md
  agents/, citations/, skills/

After PR 3, the data tree lives at src/sourced/data/ with filters/ promoted
to data/filters/. The symlinks below stitch the old paths back together inside
a tmp dir.
"""
from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "src" / "sourced" / "data"


@pytest.fixture
def repo_with_legacy_paths(tmp_path):
    """Make a working copy of the repo with the pre-PR-3 top-level layout.
    Symlinks each leaf to its current data/ location. Yields the working-copy root."""
    work = tmp_path / "work"
    work.mkdir()

    # Copy install.sh itself (not symlinked — install.sh derives REPO_DIR from
    # its own path; a symlink would point REPO_DIR back at the real repo).
    import shutil
    shutil.copy2(REPO_ROOT / "install.sh", work / "install.sh")

    # Reconstruct templates/ as a real dir with selectively-symlinked subtree.
    (work / "templates").mkdir()
    (work / "templates" / "voices").symlink_to(DATA_ROOT / "templates" / "voices")
    (work / "templates" / "styles").symlink_to(DATA_ROOT / "templates" / "styles")
    # Filters lived at templates/filters/ pre-PR-3; promoted to data/filters/.
    (work / "templates" / "filters").symlink_to(DATA_ROOT / "filters")
    # Top-level template files.
    for f in ("CLAUDE.md", "brief.template.md", "brief.template.annotated-bib.md"):
        (work / "templates" / f).symlink_to(DATA_ROOT / "templates" / f)

    # Other top-level dirs map directly.
    for sub in ("agents", "citations", "skills"):
        (work / sub).symlink_to(DATA_ROOT / sub)

    yield work
