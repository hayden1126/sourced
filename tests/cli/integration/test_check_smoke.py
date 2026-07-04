import subprocess
import sys


def test_sourced_version_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--version"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.startswith("sourced ")
    # Dev and CI both run the suite from an editable checkout with git on
    # PATH (ci.yml: pip install -e .[test], fetch-depth 0), so the live
    # checkout marker must survive end to end.
    assert "(checkout " in result.stdout


def test_sourced_check_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # Exit 0 if all prereqs present; 4 if any missing. Either is "runs cleanly."
    assert result.returncode in (0, 4)
    assert "Prerequisites" in result.stdout or "passing" in result.stdout
