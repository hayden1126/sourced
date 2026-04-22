import os
import sys
import pytest
from sourced.ui import should_color, ok, err, warn, path_str


def test_should_color_no_color_env(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert should_color(color_pref="auto", stream=sys.stdout) is False


def test_should_color_explicit_never(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert should_color(color_pref="never", stream=sys.stdout) is False


def test_should_color_explicit_always(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert should_color(color_pref="always", stream=sys.stdout) is True


def test_should_color_auto_non_tty(monkeypatch, tmp_path):
    monkeypatch.delenv("NO_COLOR", raising=False)
    f = open(tmp_path / "out.txt", "w")
    try:
        assert should_color(color_pref="auto", stream=f) is False
    finally:
        f.close()


def test_ok_with_color():
    assert "\033[32m" in ok("done", use_color=True)


def test_ok_without_color():
    assert ok("done", use_color=False) == "done"


def test_err_with_color():
    assert "\033[31m" in err("oops", use_color=True)


def test_warn_with_color():
    assert "\033[33m" in warn("careful", use_color=True)


def test_path_str_with_color():
    assert "\033[36m" in path_str("/tmp/x", use_color=True)
