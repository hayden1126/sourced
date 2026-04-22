"""File-tree mirroring. shutil.copytree wrapper.

dirs_exist_ok=True matches install.sh's intent: overwrite per-file, never delete.
copy_function=shutil.copy2 preserves mtimes (so npm install doesn't re-run
on mirrored skill dirs).
symlinks=True future-proofs: if a bundled tree ever contains symlinks they
preserve as links, not materialize.
"""
from __future__ import annotations
import shutil
from pathlib import Path


def mirror_tree(src: Path, dest: Path, *, dry_run: bool = False) -> None:
    """Mirror src → dest. If dry_run is True, returns immediately without writing;
    the caller is responsible for printing 'would mirror' output.
    Caller passes a real filesystem src (not a Traversable);
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
