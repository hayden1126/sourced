import os
import time
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

    assert not dest.exists()


def test_mirror_tree_preserves_mtime(tmp_path):
    """copy2 preserves mtimes — needed so npm install doesn't re-run."""
    src = tmp_path / "src"
    src.mkdir()
    f = src / "a.txt"
    f.write_text("alpha")
    old_mtime = time.time() - 86400  # 1 day ago
    os.utime(f, (old_mtime, old_mtime))
    dest = tmp_path / "dest"

    mirror_tree(src, dest, dry_run=False)

    copied_mtime = (dest / "a.txt").stat().st_mtime
    assert abs(copied_mtime - old_mtime) < 2  # within rounding
