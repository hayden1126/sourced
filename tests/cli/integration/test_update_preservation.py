"""Phase-2 integration tests for `sourced update`: user-addition preservation,
phase-1 migration, drift warnings, --force passthrough."""
import subprocess
import sys
from pathlib import Path


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )


def _inject_user_addition(claude_md_path: Path, region: str) -> None:
    """Insert a user-addition region inside the managed block, right before
    the end sentinel."""
    text = claude_md_path.read_text(encoding="utf-8")
    end_sentinel = "<!-- sourced:end managed -->"
    idx = text.index(end_sentinel)
    augmented = text[:idx] + region + "\n" + text[idx:]
    claude_md_path.write_text(augmented, encoding="utf-8")


def test_update_preserves_user_addition_across_refresh(tmp_home, tmp_project, clean_ansi):
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"

    # Inject a user-addition region under §7 (Modes).
    region = (
        "\n<!-- sourced:user-addition start -->\n"
        "### Custom mode\n\n"
        "| debugging | docs/modes/debugging.md | all | explicit trigger |\n"
        "<!-- sourced:user-addition end -->"
    )
    _inject_user_addition(claude, region)

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    after = claude.read_text(encoding="utf-8")
    # User-addition region preserved verbatim.
    assert "<!-- sourced:user-addition start -->" in after
    assert "<!-- sourced:user-addition end -->" in after
    assert "debugging" in after
    assert "docs/modes/debugging.md" in after


def test_update_force_discards_user_additions(tmp_home, tmp_project, clean_ansi):
    """--force path retains discard-everything behavior (escape hatch)."""
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"

    region = (
        "\n<!-- sourced:user-addition start -->\n"
        "DISCARD-ME-MARKER\n"
        "<!-- sourced:user-addition end -->"
    )
    _inject_user_addition(claude, region)

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project), "--force"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    after = claude.read_text(encoding="utf-8")
    assert "DISCARD-ME-MARKER" not in after


def test_update_surfaces_drift_warning_on_framework_edit(tmp_home, tmp_project, clean_ansi):
    """Writer edited framework prose directly (no user-addition wrapper);
    fresh wins and a warning is surfaced."""
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"

    text = claude.read_text(encoding="utf-8")
    # Pick a stable framework line that ships in the managed block.
    # Use a phrase from §1 which is resident post-split.
    drifted = text.replace(
        "You are a [working partner]",
        "You are a [working partner] -- writer edited this line",
        1,
    )
    assert drifted != text, "fixture line not found; update test"
    claude.write_text(drifted, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    after = claude.read_text(encoding="utf-8")
    # Fresh framework wins — writer's edit is gone.
    assert "writer edited this line" not in after
    # .sourced.bak preserves old state for recovery.
    assert (tmp_project / "CLAUDE.md.sourced.bak").exists()
    # Warning surfaced in stdout.
    assert "WARNING" in result.stdout or "drift" in result.stdout.lower()


def test_update_deploys_docs_tree_on_first_run_after_upgrade(tmp_home, tmp_project, clean_ansi):
    """After install (which now deploys docs/), sourced update keeps them in sync."""
    _bootstrap(tmp_home, tmp_project)
    # Fresh install should have deployed docs/ already (phase-2 behavior).
    assert (tmp_project / "docs" / "modes" / "editing.md").exists()
    # Delete one file to simulate drift, then update.
    (tmp_project / "docs" / "modes" / "editing.md").unlink()
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Update re-deployed the missing file.
    assert (tmp_project / "docs" / "modes" / "editing.md").exists()


def test_update_phase1_migration(tmp_home, tmp_project, clean_ansi):
    """Simulate phase-1 state: CLAUDE.md exists, docs/modes/ does NOT.
    sourced update should rename old CLAUDE.md to .phase1.bak, deploy fresh
    layout, and create docs/ tree."""
    _bootstrap(tmp_home, tmp_project)
    # Tear down phase-2 state to simulate a phase-1 project.
    import shutil
    shutil.rmtree(tmp_project / "docs", ignore_errors=True)
    # Replace CLAUDE.md with a phase-1-shaped minimal stub (preserves sentinels).
    phase1_stub = (
        "# CLAUDE.md (phase-1 monolith stub)\n"
        "<!-- sourced:begin managed -->\n"
        "legacy phase-1 inline mode bodies...\n"
        "<!-- sourced:end managed -->\n"
    )
    (tmp_project / "CLAUDE.md").write_text(phase1_stub, encoding="utf-8")
    # Clean up the .sourced.bak from bootstrap so we can verify migration's own bak.
    bak = tmp_project / "CLAUDE.md.sourced.bak"
    if bak.exists():
        bak.unlink()

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # .phase1.bak preserves the old monolith verbatim.
    phase1_bak = tmp_project / "CLAUDE.md.phase1.bak"
    assert phase1_bak.exists()
    assert phase1_bak.read_text(encoding="utf-8") == phase1_stub
    # Fresh CLAUDE.md landed.
    new_claude = (tmp_project / "CLAUDE.md").read_text(encoding="utf-8")
    assert "phase-1 monolith stub" not in new_claude
    # docs/ tree deployed.
    assert (tmp_project / "docs" / "modes" / "editing.md").exists()


def test_update_phase1_migration_preserves_existing_phase1_bak(tmp_home, tmp_project, clean_ansi):
    """Second phase-1 migration run must not clobber an existing .phase1.bak."""
    _bootstrap(tmp_home, tmp_project)
    import shutil
    shutil.rmtree(tmp_project / "docs", ignore_errors=True)
    (tmp_project / "CLAUDE.md").write_text(
        "<!-- sourced:begin managed -->\nlegacy\n<!-- sourced:end managed -->\n",
        encoding="utf-8",
    )
    # Pre-existing backup from a previous migration attempt.
    preserved_bak_content = "EARLIER BACKUP — DO NOT OVERWRITE"
    (tmp_project / "CLAUDE.md.phase1.bak").write_text(preserved_bak_content, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # The earlier backup is intact.
    assert (tmp_project / "CLAUDE.md.phase1.bak").read_text(encoding="utf-8") == preserved_bak_content


def test_update_unclosed_user_addition_raises(tmp_home, tmp_project, clean_ansi):
    """Malformed user-addition markers (unclosed start) must fail update with
    a clear error, not silently corrupt."""
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    end_sentinel = "<!-- sourced:end managed -->"
    idx = text.index(end_sentinel)
    malformed = (
        text[:idx]
        + "\n<!-- sourced:user-addition start -->\n(missing end marker)\n"
        + text[idx:]
    )
    claude.write_text(malformed, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    # Error surfaced, not a crash.
    combined = (result.stdout + result.stderr).lower()
    assert "unclosed" in combined or "user-addition" in combined
