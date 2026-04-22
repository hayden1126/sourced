import pytest
from pathlib import Path
from sourced.validators.csl import validate_csl_title

FIXTURES = Path(__file__).parent / "fixtures" / "csl"


def test_matching_title_returns_no_findings():
    findings = validate_csl_title(
        csl_path=FIXTURES / "matching.csl",
        declared_title="American Psychological Association 7th edition",
        style_name="apa7",
    )
    assert findings == []


def test_mismatching_title_returns_finding():
    findings = validate_csl_title(
        csl_path=FIXTURES / "mismatching.csl",
        declared_title="American Psychological Association 7th edition",
        style_name="apa7",
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.rule == "csl-title-mismatch"
    assert f.severity == "error"
    assert "Wrong Style Name" in f.message
    assert "American Psychological Association 7th edition" in f.message


def test_missing_title_element_returns_finding():
    findings = validate_csl_title(
        csl_path=FIXTURES / "no_title.csl",
        declared_title="Anything",
        style_name="apa7",
    )
    assert len(findings) == 1
    assert findings[0].rule == "csl-title-missing"


def test_missing_csl_file_returns_finding(tmp_path):
    findings = validate_csl_title(
        csl_path=tmp_path / "nonexistent.csl",
        declared_title="Whatever",
        style_name="apa7",
    )
    assert len(findings) == 1
    assert findings[0].rule == "csl-file-missing"


def test_validator_never_raises_on_malformed_xml(tmp_path):
    """Validator returns Finding, never raises (per spec §3 boundary 3)."""
    bad = tmp_path / "bad.csl"
    bad.write_text("<not really xml")
    findings = validate_csl_title(
        csl_path=bad,
        declared_title="Anything",
        style_name="apa7",
    )
    assert len(findings) >= 1
    assert findings[0].rule == "csl-parse-error"
