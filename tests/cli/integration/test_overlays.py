"""CLAUDE.d/ overlay deployment + refresh integration tests (phase 2 commit 4)."""
import subprocess
import sys


def _global_install(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_essay_deploys_readme_only(tmp_home, tmp_project, clean_ansi):
    """Default (essay) project gets CLAUDE.d/README.md and no project-type overlay."""
    _global_install(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "CLAUDE.d" / "README.md").exists()
    # Essay projects get no project-type overlay (base manifest is sufficient).
    essay_overlay = tmp_project / "CLAUDE.d" / "20-project-type-essay.md"
    annotated_overlay = tmp_project / "CLAUDE.d" / "20-project-type-annotated-bib.md"
    assert not essay_overlay.exists()
    assert not annotated_overlay.exists()


def test_install_annotated_bib_deploys_overlay(tmp_home, tmp_project, clean_ansi):
    """`--type annotated-bib` deploys the matching overlay + README."""
    _global_install(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install",
         "--project", str(tmp_project),
         "--type", "annotated-bib"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "CLAUDE.d" / "README.md").exists()
    overlay = tmp_project / "CLAUDE.d" / "20-project-type-annotated-bib.md"
    assert overlay.exists()
    overlay_text = overlay.read_text(encoding="utf-8")
    # Overlay patches base-manifest sections the spec §3 designates.
    assert "Patches to §7.1 Mode registry" in overlay_text
    assert "outlining" in overlay_text  # essay-only mode removed
    assert "refining" in overlay_text
    assert "writing" in overlay_text


def test_update_refreshes_overlays_idempotently(tmp_home, tmp_project, clean_ansi):
    """After install, sourced update re-deploys overlays (idempotent)."""
    _global_install(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install",
         "--project", str(tmp_project),
         "--type", "annotated-bib"],
        capture_output=True, text=True, check=True,
    )
    overlay = tmp_project / "CLAUDE.d" / "20-project-type-annotated-bib.md"
    # Delete overlay to simulate drift, then update.
    overlay.unlink()

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Overlay re-deployed.
    assert overlay.exists()


def test_update_preserves_writer_authored_local_overlays(tmp_home, tmp_project, clean_ansi):
    """Writer-authored 10-local-* overlays are not overwritten by update."""
    _global_install(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    # Writer authors a local overlay.
    local = tmp_project / "CLAUDE.d" / "10-local-custom.md"
    local.write_text("# Local writer overlay\nhand-authored content\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    # Local overlay untouched.
    assert local.exists()
    assert "hand-authored content" in local.read_text(encoding="utf-8")


def test_check_invariants_passes_on_shipped_overlays(tmp_home, clean_ansi):
    """The shipped annotated-bib overlay satisfies I2."""
    _global_install(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "-v", "check", "--invariants"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    # I2 now reports explicitly (no longer dormant).
    assert "I2" in result.stdout
    # No "dormant" label; commit 4 activates I2.
    # (I10 remains dormant — check the header line.)
    header_line = next(l for l in result.stdout.splitlines() if "Invariants" in l)
    assert "I10 dormant" in header_line
