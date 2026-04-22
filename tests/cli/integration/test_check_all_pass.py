import subprocess
import sys


def test_check_passes_after_global_install(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # If prereqs are present (the dev/CI machine), exit 0; else exit 4 because
    # the prereq check failed (not ~/.claude/).
    assert result.returncode in (0, 4), result.stderr
    if result.returncode == 0:
        assert "passing" in result.stdout
