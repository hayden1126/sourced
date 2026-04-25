import subprocess
import sys


def _setup_globals(tmp_home):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )


def test_install_type_annotated_writes_marker(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--type", "annotated-bib"],
        capture_output=True, text=True, check=True,
    )
    marker = tmp_project / ".sourced-project-type"
    assert marker.exists()
    assert marker.read_text().strip() == "annotated-bib"


def test_install_type_essay_no_marker(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )
    assert not (tmp_project / ".sourced-project-type").exists()


def test_install_type_annotated_uses_annotated_brief(tmp_home, tmp_project, clean_ansi):
    _setup_globals(tmp_home)
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project),
         "--type", "annotated-bib", "--brief", "my_bib"],
        capture_output=True, text=True, check=True,
    )
    brief = tmp_project / "config" / "my_bib.brief.md"
    assert brief.exists()
    # Annotated bib brief is structurally different from essay brief; check for a
    # known annotated-bib field (e.g. "Annotation shape" or "Source-count target").
    text = brief.read_text()
    assert "Source-count target" in text or "Annotation shape" in text
