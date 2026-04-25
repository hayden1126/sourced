"""Integration test: fresh sourced install renders directly into phase-4 subdir layout.

voice.md + style.md + <brief>.brief.md land in config/; sources/, samples/,
failures/ are created empty; nothing flat at root (negative assertions).
"""
import subprocess
import sys


def _setup_globals(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_renders_phase4_layout(tmp_home, tmp_project, clean_ansi):
    """Fresh sourced install should render directly into phase-4 subdir layout."""
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install",
         "--project", str(tmp_project),
         "--voice", "academic",
         "--style", "apa7",
         "--type", "essay",
         "--brief", "myproj"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    # CLAUDE.md stays at root.
    assert (tmp_project / "CLAUDE.md").exists()

    # voice.md, style.md, brief land in config/.
    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "config" / "style.md").exists()
    assert (tmp_project / "config" / "myproj.brief.md").exists()

    # Data subdirs created empty (no .gitkeep).
    assert (tmp_project / "sources").is_dir()
    assert (tmp_project / "samples").is_dir()
    assert (tmp_project / "failures").is_dir()

    # Negative: nothing flat at root.
    assert not (tmp_project / "voice.md").exists()
    assert not (tmp_project / "style.md").exists()
    assert not (tmp_project / "myproj.brief.md").exists()


def test_install_phase4_no_brief_skips_brief_file(tmp_home, tmp_project, clean_ansi):
    """Install without --brief should not create any brief file in config/."""
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install",
         "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "config" / "style.md").exists()
    # No brief file anywhere.
    assert not list((tmp_project / "config").glob("*.brief.md"))


def test_install_phase4_subdirs_idempotent(tmp_home, tmp_project, clean_ansi):
    """Running install twice (with --force) must not error on pre-existing subdirs."""
    _setup_globals(tmp_home)
    cmd = [sys.executable, "-m", "sourced", "install",
           "--project", str(tmp_project)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    result = subprocess.run(
        cmd + ["--force"], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "sources").is_dir()
