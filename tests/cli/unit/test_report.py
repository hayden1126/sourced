"""Unit tests for the shared diagnostic-report primitive.

Colour is disabled via the clean_ansi fixture so stdout assertions are on plain
text. verbose=0 is the default human view; verbose>=1 is the full dump.
"""
from sourced.commands._report import CheckResult, print_section


def test_warn_only_section_is_not_collapsed(capsys, clean_ansi):
    # A section with a warning but no failure must expand at default verbosity,
    # not collapse to "N/M passing" and hide the warning.
    results = [
        CheckResult("thing-a", "pass"),
        CheckResult("thing-b", "warn", "something is off"),
    ]
    print_section("Section", results, use_color=False, verbose=0)
    out = capsys.readouterr().out
    assert "something is off" in out
    assert "passing" not in out  # did not collapse


def test_all_pass_section_collapses(capsys, clean_ansi):
    results = [CheckResult("a", "pass"), CheckResult("b", "pass")]
    print_section("Section", results, use_color=False, verbose=0)
    out = capsys.readouterr().out
    assert "Section: 2/2 passing" in out


def test_skip_hidden_at_default_shown_verbose(capsys, clean_ansi):
    results = [CheckResult("a", "pass"), CheckResult("b", "skip", "n/a here")]
    # Default: skip hidden, section collapses, and skip excluded from the count.
    print_section("Section", results, use_color=False, verbose=0)
    out = capsys.readouterr().out
    assert "1/1 passing" in out  # skip not counted
    assert "n/a here" not in out
    # Verbose: skip row shown.
    print_section("Section", results, use_color=False, verbose=1)
    out = capsys.readouterr().out
    assert "n/a here" in out


def test_fix_rendered_on_its_own_line(capsys, clean_ansi):
    results = [CheckResult("broken", "fail", "it is broken", fix="run the fixer")]
    print_section("Section", results, use_color=False, verbose=0)
    out = capsys.readouterr().out
    assert "it is broken" in out
    assert "fix: run the fixer" in out
    # fix is a separate line, not concatenated into the detail line.
    lines = [ln for ln in out.splitlines() if "broken" in ln]
    assert all("run the fixer" not in ln for ln in lines)
