import pytest
from sourced.validators.exemptions import (
    extract_voice_exemptions,
    extract_canonical_ids,
    validate,
)


def test_extract_voice_exemptions_finds_bullets():
    voice = (
        "## §10 exemptions\n\n"
        "- em-dash-allowed: this voice uses em dashes for parenthetical asides.\n"
        "- not-x-but-y: present tense; corpus shows.\n\n"
        "## Other\n"
        "- not-an-exemption\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == ["em-dash-allowed", "not-x-but-y"]


def test_extract_voice_exemptions_ignores_prose_bullets():
    """A bullet whose first token isn't [a-z0-9-]+ is prose; don't count it."""
    voice = (
        "## §10 exemptions\n\n"
        "- em-dash-allowed\n"
        "- This is a free-prose explanation, not an exemption id.\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == ["em-dash-allowed"]


def test_extract_voice_exemptions_returns_empty_when_section_absent():
    voice = "# Some voice\n\n## Iron rules\n- foo\n"
    assert extract_voice_exemptions(voice) == []


def test_extract_canonical_ids_from_claude_md():
    claude_md = (
        "## 10. Generation signatures\n\n"
        "### Never (rewrite on sight)\n\n"
        "- **Em dashes**. [id: em-dash-allowed]\n"
        "- **'Not X but Y' pivots**. [id: not-x-but-y]\n\n"
        "### Watch for density\n"
        "- **Other [id: density-foo]**\n"
    )
    ids = extract_canonical_ids(claude_md)
    assert "em-dash-allowed" in ids
    assert "not-x-but-y" in ids
    # density-foo is in a different section — should not appear.
    assert "density-foo" not in ids


def test_validate_passes_when_all_exemption_ids_canonical():
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n- **Y**. [id: bar]\n"
    voice = "## §10 exemptions\n- foo\n- bar\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_finds_unknown_exemption_id():
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n"
    voice = "## §10 exemptions\n- foo\n- typo-id\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert len(findings) == 1
    assert findings[0].rule == "exemption-unknown-id"
    assert "typo-id" in findings[0].message


def test_validate_no_section_no_findings():
    """Voice with no §10 exemptions section → nothing to validate."""
    claude_md = "### Never (rewrite on sight)\n- **X**. [id: foo]\n"
    voice = "no exemptions section\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_never_raises_on_garbage():
    findings = validate(voice="", claude_md="", voice_name="x")
    assert findings == []
