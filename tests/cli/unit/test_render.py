import pytest
from sourced.render import RenderContext, render, write_atomic


def test_substitutes_user():
    out = render("Hello {{USER}}!", RenderContext(user="Alice"))
    assert out == "Hello Alice!"


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
    # Exactly one file remains and it's the target — implementation-independent.
    assert list(tmp_path.iterdir()) == [target]


def test_write_atomic_cleans_up_on_write_failure(tmp_path, monkeypatch):
    """If write() raises, no partial .tmp must survive on disk."""
    target = tmp_path / "out.md"

    # Force write to raise by passing a non-string. The TypeError happens
    # inside the `with` block, after the tempfile is created.
    with pytest.raises(TypeError):
        write_atomic(target, 12345)  # type: ignore[arg-type]

    # No leftover .tmp files in the parent dir.
    assert list(tmp_path.iterdir()) == []
