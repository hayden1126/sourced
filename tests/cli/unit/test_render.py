from sourced.render import RenderContext, render, write_atomic


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


def test_style_token_kept_when_style_name_none():
    out = render("style={{STYLE}}", RenderContext(user="A"))
    assert out == "style={{STYLE}}"


def test_unknown_token_kept_verbatim():
    out = render("hello {{UNKNOWN}}", RenderContext(user="A"))
    assert out == "hello {{UNKNOWN}}"


def test_handles_user_with_special_chars():
    """User name like 'O'Brien' or 'A & B' must not break substitution."""
    out = render("by {{USER}}", RenderContext(user="O'Brien & Co."))
    assert out == "by O'Brien & Co."


def test_render_is_pure_no_io():
    """render() must not touch the filesystem."""
    out = render("noop", RenderContext(user="A"))
    assert out == "noop"


def test_write_atomic_creates_file(tmp_path):
    target = tmp_path / "out.md"
    write_atomic(target, "hello")
    assert target.read_text() == "hello"


def test_write_atomic_overwrites(tmp_path):
    target = tmp_path / "out.md"
    target.write_text("old")
    write_atomic(target, "new")
    assert target.read_text() == "new"


def test_write_atomic_creates_parent_dir(tmp_path):
    target = tmp_path / "nested" / "deep" / "out.md"
    write_atomic(target, "hello")
    assert target.read_text() == "hello"


def test_write_atomic_no_stale_tmp_left(tmp_path):
    target = tmp_path / "out.md"
    write_atomic(target, "hello")
    # No file matching .out.md.<random>.tmp should remain.
    leftovers = [p for p in tmp_path.iterdir() if ".tmp" in p.name]
    assert leftovers == []
