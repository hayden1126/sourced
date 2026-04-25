import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--style", "apa7"],
        capture_output=True, text=True, check=True,
    )


def test_switch_style_updates_marker(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "switch", "style", "mla9",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "<!-- sourced:style=mla9 -->" in (tmp_project / "config" / "style.md").read_text()
