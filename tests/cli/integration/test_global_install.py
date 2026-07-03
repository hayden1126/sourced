import subprocess
import sys


def test_global_install_creates_expected_dirs(tmp_home, clean_ansi):
    # First run needs a name; pipe it in via stdin.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    expected = ["agents", "citations", "templates", "voice", "style", "skills", "filters"]
    for sub in expected:
        assert (tmp_home / ".claude" / sub).is_dir(), f"missing ~/.claude/{sub}"


def test_global_install_creates_sourced_config(tmp_home, clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    cfg = tmp_home / ".claude" / "sourced.config"
    assert cfg.exists()
    assert "Alice" in cfg.read_text()


def test_global_install_idempotent(tmp_home, clean_ansi):
    """Second run reuses saved name; no prompt."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="Alice\n", capture_output=True, text=True, check=True,
    )
    # Second run with no stdin → must not hang asking for input.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_global_install_dry_run_writes_nothing(tmp_home, clean_ansi):
    # Dry-run on a fresh home where there's no name yet → should still need a name?
    # Decision: dry-run still needs config to know what it WOULD render, so prompt.
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "global-install"],
        input="Alice\n", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Dry-run still creates ~/.claude/sourced.config because we needed the name.
    # But it should NOT mirror any other files.
    assert not (tmp_home / ".claude" / "agents").exists()
    assert not (tmp_home / ".claude" / "voice").exists()
