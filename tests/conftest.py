"""Shared pytest fixtures for sourced CLI tests."""
import pytest


@pytest.fixture
def tmp_home(tmp_path, monkeypatch):
    """Redirect HOME to a fresh tmp dir."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
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
