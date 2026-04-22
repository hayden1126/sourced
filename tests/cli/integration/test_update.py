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
