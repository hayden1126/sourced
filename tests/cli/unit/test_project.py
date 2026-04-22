import pytest
from sourced.project import (
    read_project_type, write_project_type,
    read_voice_marker, read_style_marker,
    extract_managed_block, replace_managed_block,
    write_bak_sibling,
)
from sourced.errors import ProjectError


# ----- project type marker -----

def test_project_type_default_when_marker_absent(tmp_project):
    assert read_project_type(tmp_project) == "essay"


def test_project_type_reads_marker(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_strips_whitespace_and_crlf(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\r\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_empty_marker_treated_as_essay(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("   \n")
    assert read_project_type(tmp_project) == "essay"


def test_write_project_type_essay_no_marker(tmp_project):
    """Essay default writes no marker (legacy-safe)."""
    write_project_type(tmp_project, "essay")
    assert not (tmp_project / ".sourced-project-type").exists()


def test_write_project_type_annotated_writes_marker(tmp_project):
    write_project_type(tmp_project, "annotated-bib")
    assert (tmp_project / ".sourced-project-type").read_text().strip() == "annotated-bib"


def test_project_type_unknown_value_raises(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("unknown-type\n")
    with pytest.raises(ProjectError, match="unknown"):
        read_project_type(tmp_project)


# ----- voice / style markers -----

def test_read_voice_marker_finds_quoted_form(tmp_project):
    (tmp_project / "voice.md").write_text(
        "<!-- sourced:voice=academic -->\n# Voice rules\n"
    )
    assert read_voice_marker(tmp_project / "voice.md") == "academic"


def test_read_voice_marker_returns_none_when_missing(tmp_project):
    (tmp_project / "voice.md").write_text("# No marker\nplain content\n")
    assert read_voice_marker(tmp_project / "voice.md") is None


def test_read_style_marker_works_similarly(tmp_project):
    (tmp_project / "style.md").write_text("<!-- sourced:style=apa7 -->\n")
    assert read_style_marker(tmp_project / "style.md") == "apa7"


def test_read_voice_marker_ignores_body_match(tmp_project):
    """install.sh restricts to line 1; body mentions of the marker must NOT match."""
    (tmp_project / "voice.md").write_text(
        "# Voice rules\n"
        "this voice is more formal than\n"
        "<!-- sourced:voice=casual -->\n"
        "...even though casual is mentioned above.\n"
    )
    assert read_voice_marker(tmp_project / "voice.md") is None


def test_read_voice_marker_rejects_invalid_chars(tmp_project):
    """install.sh's regex restricts to [a-zA-Z0-9_-]; a name with spaces or
    special chars must NOT match."""
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=bad name -->\n")
    assert read_voice_marker(tmp_project / "voice.md") is None


# ----- managed-block sentinels (column-0 strict) -----

def test_extract_managed_block_finds_pair():
    text = (
        "before\n"
        "<!-- sourced:begin managed -->\n"
        "managed line 1\n"
        "managed line 2\n"
        "<!-- sourced:end managed -->\n"
        "after\n"
    )
    block = extract_managed_block(text)
    assert "managed line 1" in block
    assert "managed line 2" in block
    assert "before" not in block
    assert "after" not in block


def test_extract_managed_block_rejects_indented_sentinel():
    """The strict column-0 regex must not match an indented sentinel
    (legitimate prose documenting the sentinel system)."""
    text = (
        "  - <!-- sourced:begin managed -->\n"
        "managed?\n"
        "  - <!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError):
        extract_managed_block(text)


def test_extract_managed_block_rejects_missing_sentinels():
    with pytest.raises(ProjectError, match="begin"):
        extract_managed_block("no sentinels here\n")


def test_extract_managed_block_rejects_double_begin():
    text = (
        "<!-- sourced:begin managed -->\n"
        "first\n"
        "<!-- sourced:begin managed -->\n"
        "<!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError, match="multiple"):
        extract_managed_block(text)


def test_replace_managed_block_preserves_outside():
    original = (
        "USER PROSE BEFORE\n"
        "<!-- sourced:begin managed -->\n"
        "old managed\n"
        "<!-- sourced:end managed -->\n"
        "USER PROSE AFTER\n"
    )
    new_managed = "fresh managed content"
    out = replace_managed_block(original, new_managed)
    assert "USER PROSE BEFORE\n" in out
    assert "USER PROSE AFTER\n" in out
    assert "fresh managed content" in out
    assert "old managed" not in out


def test_replace_managed_block_with_empty_new_managed():
    """Replacing with empty content must not introduce spurious blank lines."""
    original = (
        "<!-- sourced:begin managed -->\n"
        "old content\n"
        "<!-- sourced:end managed -->\n"
    )
    out = replace_managed_block(original, "")
    assert out == (
        "<!-- sourced:begin managed -->\n"
        "<!-- sourced:end managed -->\n"
    )


def test_extract_managed_block_handles_empty():
    """An immediate begin->end with nothing between is a legal degenerate case."""
    text = "<!-- sourced:begin managed -->\n<!-- sourced:end managed -->\n"
    assert extract_managed_block(text) == ""


def test_replace_managed_block_raises_on_missing_sentinels():
    with pytest.raises(ProjectError, match="malformed"):
        replace_managed_block("no sentinels here\n", "x")


# ----- .sourced.bak rollback fallback -----

def test_write_bak_sibling_creates_bak(tmp_project):
    f = tmp_project / "CLAUDE.md"
    f.write_text("original")
    write_bak_sibling(f)
    assert (tmp_project / "CLAUDE.md.sourced.bak").read_text() == "original"


def test_write_bak_sibling_no_op_when_target_missing(tmp_project):
    f = tmp_project / "CLAUDE.md"
    write_bak_sibling(f)  # should not raise
    assert not (tmp_project / "CLAUDE.md.sourced.bak").exists()
