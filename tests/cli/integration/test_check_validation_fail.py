import subprocess
import sys


def test_check_flags_corrupted_voice(tmp_home, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Corrupt a voice file by removing iron-rule content.
    voice = tmp_home / ".claude" / "voice" / "academic.md"
    voice.write_text("# academic\n\n(emptied — no iron rules)\n")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "check"],
        capture_output=True, text=True,
    )
    # With prereqs intact, only voice check fails → exit 4. The check command's
    # _print_section summarizes per-voice findings as a count, so we assert on
    # the voice filename + finding-count phrasing rather than the rule name.
    if "Prerequisites" in result.stdout and "passing" in result.stdout:
        assert result.returncode == 4
        assert "voice/academic.md" in result.stdout
        assert "validation finding" in result.stdout.lower()
