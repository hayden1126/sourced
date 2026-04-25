import subprocess
import sys


def _setup_globals(tmp_home):
    """Helper: prerun global-install so per-project install has voice/style libraries."""
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_creates_per_project_files(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_project / "CLAUDE.md").exists()
    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "config" / "style.md").exists()


def test_install_voice_marker_present(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--voice", "casual"],
        capture_output=True, text=True, check=True,
    )
    assert "<!-- sourced:voice=casual -->" in (tmp_project / "config" / "voice.md").read_text()


def test_install_style_marker_present(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--style", "mla9"],
        capture_output=True, text=True, check=True,
    )
    assert "<!-- sourced:style=mla9 -->" in (tmp_project / "config" / "style.md").read_text()


def test_install_brief_creates_brief_file(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--brief", "my_paper"],
        capture_output=True, text=True, check=True,
    )
    assert (tmp_project / "config" / "my_paper.brief.md").exists()


def test_install_user_substituted(tmp_home, tmp_project, clean_ansi):
    """{{USER}} in CLAUDE.md template gets replaced with the configured name."""
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    text = (tmp_project / "CLAUDE.md").read_text()
    assert "{{USER}}" not in text, "{{USER}} token not substituted"
    assert "TestUser" in text


def test_install_errors_when_files_exist_without_force(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    (tmp_project / "CLAUDE.md").write_text("user content")
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "exist" in result.stderr.lower() or "force" in result.stderr.lower()
