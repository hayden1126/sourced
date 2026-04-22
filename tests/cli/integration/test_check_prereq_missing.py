import os
import subprocess
import sys


def test_check_reports_missing_tool(tmp_home, monkeypatch, clean_ansi):
    """Run with PATH that excludes pdftoppm to simulate missing tool."""
    # Strip /usr/bin and /usr/local/bin from PATH so common tools disappear.
    # Inherit PYTHONPATH from the conftest tmp_home fixture so the subprocess
    # can still import sourced when HOME is monkeypatched.
    env = {
        "HOME": str(tmp_home),
        "PATH": "/nonexistent",
        "NO_COLOR": "1",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 4
    assert "not on PATH" in result.stdout or "failed" in result.stdout
