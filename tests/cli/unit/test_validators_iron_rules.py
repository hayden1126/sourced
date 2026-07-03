from sourced.validators.iron_rules import extract_iron_rules, normalize_rule, validate


def test_extract_iron_rules_section():
    skeleton = (
        "# Voice\n\n"
        "## Iron rules\n\n"
        "- No em dashes.\n"
        "- Never use 'utilize' when 'use' fits.\n\n"
        "## Other section\n"
        "- Not iron.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("em dashes" in r.lower() for r in rules)
    assert any("utilize" in r.lower() for r in rules)
    assert all("Not iron" not in r for r in rules)


def test_extract_includes_ai_tells_section():
    skeleton = (
        "## AI-tells\n\n"
        "- Don't say 'in this way'.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("in this way" in r for r in rules)


def test_extract_includes_generation_signatures_section():
    skeleton = (
        "## Generation signatures\n\n"
        "- No 'not X but Y' constructions.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("not X but Y" in r for r in rules)


def test_extract_includes_iron_token_lines():
    skeleton = (
        "## Random section\n\n"
        "Some prose here. [iron] This sentence is iron.\n"
    )
    rules = extract_iron_rules(skeleton)
    assert any("iron" in r.lower() for r in rules)


def test_normalize_lowercase():
    assert "no em dashes" in normalize_rule("- No EM Dashes!")


def test_normalize_strips_trailing_punctuation():
    assert normalize_rule("Rule.") == normalize_rule("Rule!") == normalize_rule("Rule?")


def test_normalize_collapses_whitespace():
    assert normalize_rule("a   b\tc") == normalize_rule("a b c")


def test_validate_passes_when_all_rules_present():
    skeleton = "## Iron rules\n- No em dashes.\n- No utilize.\n"
    voice = (
        "voice prose\n"
        "remember: no em dashes.\n"
        "and absolutely no utilize.\n"
    )
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert findings == []


def test_validate_finds_missing_rules():
    skeleton = "## Iron rules\n- No em dashes.\n- No utilize.\n"
    voice = "voice prose without the rule.\n"
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert len(findings) == 2
    assert all(f.rule == "iron-rule-missing" for f in findings)
    assert all(f.severity == "error" for f in findings)


def test_validate_returns_no_findings_when_skeleton_has_no_iron_rules():
    """Empty iron-rules section → no requirements → no findings."""
    skeleton = "## Iron rules\n\n## Other\n- whatever\n"
    voice = "anything goes\n"
    findings = validate(skeleton=skeleton, candidate=voice, voice_name="academic")
    assert findings == []


def test_validate_self_validation_short_circuit():
    """Skeleton == candidate must return [] (the skeleton's own iron-rule lines
    contain the rule text trivially)."""
    skeleton = "## Iron rules\n- No em dashes.\n"
    findings = validate(skeleton=skeleton, candidate=skeleton, voice_name="academic")
    assert findings == []


def test_validate_never_raises_on_garbage_input():
    findings = validate(skeleton="", candidate="", voice_name="x")
    assert findings == []
