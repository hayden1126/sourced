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
    assert (new_dir / "config" / "voice.md").exists()
    assert (new_dir / "config" / "style.md").exists()
    # Brief defaults to project name — lands in config/
    assert (new_dir / "config" / "my-paper.brief.md").exists()


def test_new_with_explicit_brief_name(tmp_home, tmp_path, clean_ansi):
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "new", "my-paper", "--brief", "alt_name"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "my-paper" / "config" / "alt_name.brief.md").exists()


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
