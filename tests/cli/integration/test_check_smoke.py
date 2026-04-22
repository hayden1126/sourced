import subprocess
import sys


def test_sourced_version_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "sourced" in result.stdout


def test_sourced_check_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # Exit 0 if all prereqs present; 4 if any missing. Either is "runs cleanly."
    assert result.returncode in (0, 4)
    assert "Prerequisites" in result.stdout or "passing" in result.stdout
