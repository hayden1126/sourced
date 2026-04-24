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
        "## 7. Modes\n\n"
        "### 7.6 Precedence and canonical §10 IDs\n\n"
        "Precedence rules...\n\n"
        "**Canonical §10 IDs (source of truth).**\n\n"
        "- `em-dashes` — em-dash appositives.\n"
        "- `not-x-but-y` — contrastive pivots.\n"
        "- `ornamental-triads` — rhythmic lists.\n\n"
        "### 7.7 Inline mode bodies\n"
        "- `something-else` — should not be picked up.\n"
    )
    ids = extract_canonical_ids(claude_md)
    assert "em-dashes" in ids
    assert "not-x-but-y" in ids
    assert "ornamental-triads" in ids
    # something-else is in 7.7, not 7.6 — must not appear.
    assert "something-else" not in ids


def test_validate_passes_when_all_exemption_ids_canonical():
    claude_md = (
        "### 7.6 Precedence and canonical §10 IDs\n\n"
        "- `em-dashes` — em-dash appositives.\n"
        "- `not-x-but-y` — contrastive pivots.\n"
    )
    voice = "## §10 exemptions\n- em-dashes\n- not-x-but-y\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_finds_unknown_exemption_id():
    claude_md = (
        "### 7.6 Precedence and canonical §10 IDs\n\n"
        "- `em-dashes` — em-dash appositives.\n"
    )
    voice = "## §10 exemptions\n- em-dashes\n- typo-id\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert len(findings) == 1
    assert findings[0].rule == "exemption-unknown-id"
    assert "typo-id" in findings[0].message


def test_validate_no_section_no_findings():
    """Voice with no §10 exemptions section → nothing to validate."""
    claude_md = (
        "### 7.6 Precedence and canonical §10 IDs\n\n"
        "- `em-dashes` — em-dash appositives.\n"
    )
    voice = "no exemptions section\n"
    findings = validate(voice=voice, claude_md=claude_md, voice_name="academic")
    assert findings == []


def test_validate_never_raises_on_garbage():
    findings = validate(voice="", claude_md="", voice_name="x")
    assert findings == []


def test_extract_voice_exemptions_rejects_h3_section():
    """Regression guard: phase-3 promoted §10 exemptions from H3 (nested under
    ## Iron rules) to H2 (its own top-level section). A skeleton or voice file
    that still uses ### §10 exemptions must NOT have its bullets silently picked
    up — the section must use H2."""
    voice = (
        "## Iron rules\n\n"
        "Iron rule prose.\n\n"
        "### §10 exemptions\n\n"
        "- em-dash-allowed: legacy H3 placement.\n"
        "- not-x-but-y: legacy H3 placement.\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == [], "H3 §10 exemptions section must not be picked up"


def test_extract_voice_exemptions_picks_up_h2_after_iron_rules():
    """H2 §10 exemptions following H2 Iron rules is the canonical phase-3
    layout. Confirm bullets are extracted from the H2 section, not from
    Iron rules' bulleted prose."""
    voice = (
        "## Iron rules\n\n"
        "Iron rule prose with no canonical-id bullets.\n\n"
        "## §10 exemptions\n\n"
        "- throat-clearing-openers: light corpus use earns its place.\n"
        "- ornamental-triads: grounded triads, not rhythmic flourish.\n"
    )
    ids = extract_voice_exemptions(voice)
    assert ids == ["throat-clearing-openers", "ornamental-triads"]
