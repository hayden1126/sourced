"""Shared pytest fixtures for sourced CLI tests."""
import os
from pathlib import Path

import pytest


@pytest.fixture
def tmp_home(tmp_path, monkeypatch):
    """Redirect HOME to a fresh tmp dir.

    Also exports PYTHONPATH pointing at src/ so subprocesses (which inherit
    the monkeypatched HOME and therefore lose the user-site editable .pth
    file) can still import sourced.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    src = str(Path(__file__).parent.parent / "src")
    existing = os.environ.get("PYTHONPATH", "")
    monkeypatch.setenv("PYTHONPATH", f"{src}:{existing}" if existing else src)
    return home


@pytest.fixture
def tmp_project(tmp_path):
    """A fresh tmp dir as the project PWD."""
    proj = tmp_path / "project"
    proj.mkdir()
    return proj


@pytest.fixture
def clean_ansi(monkeypatch):
    """Disable color for deterministic stdout assertions."""
    monkeypatch.setenv("NO_COLOR", "1")
