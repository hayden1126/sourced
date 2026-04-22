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
