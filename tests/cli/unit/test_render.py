import pytest
from sourced.render import RenderContext, render


def test_substitutes_user():
    out = render("Hello {{USER}}!", RenderContext(user="Alice"))
    assert out == "Hello Alice!"


def test_substitutes_voice_when_present():
    out = render("voice={{VOICE}}", RenderContext(user="A", voice_name="academic"))
    assert out == "voice=academic"


def test_voice_token_kept_when_voice_name_none():
    out = render("voice={{VOICE}}", RenderContext(user="A"))
    assert out == "voice={{VOICE}}"


def test_substitutes_style_when_present():
    out = render("style={{STYLE}}", RenderContext(user="A", style_name="apa7"))
    assert out == "style=apa7"


def test_unknown_token_kept_verbatim():
    out = render("hello {{UNKNOWN}}", RenderContext(user="A"))
    assert out == "hello {{UNKNOWN}}"


def test_handles_user_with_special_chars():
    """User name like 'O'Brien' or 'A & B' must not break substitution."""
    out = render("by {{USER}}", RenderContext(user="O'Brien & Co."))
    assert out == "by O'Brien & Co."


def test_render_is_pure_no_io(tmp_path, monkeypatch):
    """render() must not touch the filesystem."""
    out = render("noop", RenderContext(user="A"))
    assert out == "noop"
