"""Golden-snapshot tests: render every shipped template against a canonical
RenderContext and snapshot the output. Catches silent template drift.

Run `pytest tests/cli/golden/ --snapshot-update` to regenerate snapshots
intentionally."""
import pytest
from sourced.render import RenderContext, read_template, render


CANONICAL = RenderContext(user="TestUser")


def test_claude_md_essay(snapshot):
    text = read_template("templates/CLAUDE.md")
    assert render(text, CANONICAL) == snapshot


def test_brief_essay(snapshot):
    text = read_template("templates/brief.template.md")
    assert render(text, CANONICAL) == snapshot


def test_brief_annotated_bib(snapshot):
    text = read_template("templates/brief.template.annotated-bib.md")
    assert render(text, CANONICAL) == snapshot


@pytest.mark.parametrize("name", ["academic", "casual", "hybrid", "journalistic", "narrative", "technical"])
def test_voice(name, snapshot):
    text = read_template(f"templates/voices/{name}.md")
    assert render(text, CANONICAL) == snapshot


@pytest.mark.parametrize("name", ["apa7", "chicago17-ad", "chicago17-nb", "ieee", "mla9"])
def test_style(name, snapshot):
    text = read_template(f"templates/styles/{name}.md")
    assert render(text, CANONICAL) == snapshot
