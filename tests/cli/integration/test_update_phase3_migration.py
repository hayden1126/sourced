"""Integration test: sourced update auto-migrates phase-3 layout to phase-4."""
import subprocess
import sys


def _bootstrap_phase3(tmp_home, tmp_project):
    """Seed a phase-4 install, then mutate back to phase-3 flat layout."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install",
         "--project", str(tmp_project), "--brief", "report"],
        capture_output=True, text=True, check=True,
    )
    # Mutate to phase-3: move config/* back to root.
    config = tmp_project / "config"
    (config / "voice.md").rename(tmp_project / "voice.md")
    (config / "style.md").rename(tmp_project / "style.md")
    (config / "report.brief.md").rename(tmp_project / "report.brief.md")
    config.rmdir()  # empty after the moves
    # Add a citations.json at root to verify it migrates too.
    (tmp_project / "report.citations.json").write_text("[]")


def test_update_migrates_phase3_to_phase4(tmp_home, tmp_project, clean_ansi):
    """Running update on a phase-3 layout project migrates it to phase-4 subdirs."""
    _bootstrap_phase3(tmp_home, tmp_project)

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )

    # Assert phase-4 layout present
    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "config" / "style.md").exists()
    assert (tmp_project / "config" / "report.brief.md").exists()
    assert (tmp_project / "sources" / "report.citations.json").exists()
    # Root no longer has the migrated files
    assert not (tmp_project / "voice.md").exists()
    assert not (tmp_project / "style.md").exists()
    assert not (tmp_project / "report.brief.md").exists()
    assert not (tmp_project / "report.citations.json").exists()
    # Empty dirs created
    assert (tmp_project / "samples").is_dir()
    assert (tmp_project / "failures").is_dir()


def test_update_phase3_dry_run_announces_migration(tmp_home, tmp_project, clean_ansi):
    """Dry-run should announce the migration without performing it."""
    _bootstrap_phase3(tmp_home, tmp_project)

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--dry-run", "update",
         "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    # Dry-run must announce phase-3 migration
    assert "phase-3" in result.stdout.lower(), (
        f"Expected 'phase-3' in dry-run stdout; got:\n{result.stdout}"
    )
    # Files NOT moved (dry-run is side-effect-free)
    assert (tmp_project / "voice.md").exists()
    assert not (tmp_project / "config" / "voice.md").exists()


def test_update_phase3_force_skips_migration(tmp_home, tmp_project, clean_ansi):
    """`sourced update --force` is a re-render escape hatch and must NOT
    trigger the phase-3 → phase-4 migration. Files stay at root for force-runs."""
    _bootstrap_phase3(tmp_home, tmp_project)

    subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--force",
         "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    # Force re-renders CLAUDE.md but leaves layout alone — files stay at root
    assert (tmp_project / "voice.md").exists()
    assert (tmp_project / "style.md").exists()
    assert not (tmp_project / "config" / "voice.md").exists()
    assert not (tmp_project / "config" / "style.md").exists()


def test_update_phase3_force_refreshes_root_voice_and_style(tmp_home, tmp_project, clean_ansi):
    """`sourced update --force` on a phase-3 project must refresh voice/style
    at root (not silently no-op because the code reads from config/)."""
    _bootstrap_phase3(tmp_home, tmp_project)

    # Truncate the root files to just their markers — re-render must fill them in.
    voice = tmp_project / "voice.md"
    style = tmp_project / "style.md"
    voice.write_text("<!-- sourced:voice=academic -->\n")
    style.write_text("<!-- sourced:style=apa7 -->\n")

    subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--force",
         "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )

    # Both files should now be fully re-rendered (markers preserved + body restored).
    assert voice.read_text().startswith("<!-- sourced:voice=academic -->")
    assert len(voice.read_text()) > 100, "voice.md was not refreshed"
    assert style.read_text().startswith("<!-- sourced:style=apa7 -->")
    assert len(style.read_text()) > 100, "style.md was not refreshed"
