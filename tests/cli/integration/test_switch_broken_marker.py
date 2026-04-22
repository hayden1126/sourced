import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_switch_voice_errors_when_no_voice_md(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    # No `sourced install` run — voice.md doesn't exist.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "switch", "voice", "casual",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 5  # ProjectError
    # Remediation hint mentions install --force
    assert "install" in result.stderr.lower() and "--force" in result.stderr.lower()
