"""Integration tests for `sourced check --invariants`."""
import subprocess
import sys


def test_check_invariants_passes_on_shipped_bundle(tmp_home, clean_ansi):
    """Shipped bundle must satisfy every invariant commit 3 covers."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "-v", "check", "--invariants"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    # Verbose output lists each invariant id separately.
    for rule_id in ("I1", "I3", "I4", "I5", "I6", "I7", "I8", "I9"):
        assert rule_id in result.stdout


def test_check_invariants_exits_4_on_any_failure(tmp_home, monkeypatch):
    """A single invariant error must fail the command with exit 4 (same as
    existing sourced check failure contract)."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Monkeypatch the bundled template to inject a broken invariant (unclosed
    # user-addition marker). Mutating the source bundle directly avoids needing
    # a separate fixture directory.
    import sourced
    from pathlib import Path
    template_path = (
        Path(sourced.__file__).parent / "data" / "templates" / "CLAUDE.md"
    )
    original = template_path.read_text(encoding="utf-8")
    try:
        template_path.write_text(
            original.rstrip("\n")
            + "\n<!-- sourced:user-addition start -->\n(missing end)\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-m", "sourced", "check", "--invariants"],
            capture_output=True, text=True,
        )
        assert result.returncode == 4
        assert "I6" in result.stdout
    finally:
        template_path.write_text(original, encoding="utf-8")


def test_check_without_invariants_flag_runs_prereqs(tmp_home, clean_ansi):
    """Default `sourced check` (no flag) still runs the prereq/health path."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # Exit code depends on the environment's tool availability; we just verify
    # the non-invariant code path ran (prereq section in output) and no invariant
    # output leaked in.
    assert "Prerequisites" in result.stdout or "Global install" in result.stdout
    assert "Invariants" not in result.stdout
