import subprocess
import sys


def test_install_dry_run_writes_no_files(tmp_home, tmp_project, clean_ansi):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "install",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert not (tmp_project / "CLAUDE.md").exists()
    assert not (tmp_project / "config" / "voice.md").exists()
    # Dry-run must not create the phase-4 subdirs either (regression guard for
    # the install.py mkdir-before-dry-run-guard bug fixed in this PR).
    assert not (tmp_project / "config").exists()
    assert not (tmp_project / "sources").exists()
    assert not (tmp_project / "samples").exists()
    assert not (tmp_project / "failures").exists()


def test_install_dry_run_runs_validators(tmp_home, tmp_project, clean_ansi):
    """Dry-run should still surface validation errors before user runs for real."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    # Corrupt a voice — dry-run should error on the validation, not just succeed.
    voice = tmp_home / ".claude" / "voice" / "academic.md"
    voice.write_text("(no iron rules here)\n")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "install",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 4  # ValidationError
    assert "iron" in result.stderr.lower()
