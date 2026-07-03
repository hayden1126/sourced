"""Well-formedness guard for the emitter reference fixtures.

The fixtures are reference material an LLM follows (see README.md), not
executable specs. This file only catches accidental corruption: missing
files, invalid JSON, or CSL-JSON entries without the fields pandoc requires.
"""
import json
from pathlib import Path

import pytest

EMITTER_DIR = Path(__file__).parent
CASES = sorted(p.name for p in EMITTER_DIR.iterdir() if p.is_dir() and not p.name.startswith("__"))


@pytest.mark.parametrize("case", CASES)
def test_fixture_wellformed(case):
    case_dir = EMITTER_DIR / case
    input_path = case_dir / "input.citations.json"
    expected_path = case_dir / "expected.bib.json"
    assert input_path.is_file(), f"{case}: missing input.citations.json"
    assert expected_path.is_file(), f"{case}: missing expected.bib.json"
    json.loads(input_path.read_text())
    expected = json.loads(expected_path.read_text())
    assert isinstance(expected, list), f"{case}: expected.bib.json must be a CSL-JSON list"
    assert expected, f"{case}: expected.bib.json is empty"
    for entry in expected:
        missing = {"id", "type"} - entry.keys()
        assert not missing, f"{case}: CSL-JSON entry missing {sorted(missing)}: {entry}"
