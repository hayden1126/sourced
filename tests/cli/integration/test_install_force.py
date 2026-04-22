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
