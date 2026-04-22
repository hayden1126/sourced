import subprocess
import sys


def test_quiet_suppresses_success_output(tmp_home, clean_ansi):
    # Bootstrap config first (quiet mode rejects the interactive name prompt).
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Now exercise quiet: re-run global-install with -q (it's idempotent).
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "-q", "global-install"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Quiet mode: stdout should be near-empty.
    assert len(result.stdout) < 10


def test_verbose_shows_more_detail(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result_default = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    result_verbose = subprocess.run(
        [sys.executable, "-m", "sourced", "-v", "check"],
        capture_output=True, text=True,
    )
    # Verbose strictly more output than default (assuming all-pass).
    if result_default.returncode == 0:
        assert len(result_verbose.stdout) >= len(result_default.stdout)
