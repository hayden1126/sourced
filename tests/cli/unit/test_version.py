import subprocess
from pathlib import Path

import pytest

import sourced
from sourced.cli import _git_checkout_state, _version_string

REPO_ROOT = Path(sourced.__file__).resolve().parents[2]


def test_checkout_state_matches_git_describe():
    if not (REPO_ROOT / ".git").exists():
        pytest.skip("not running from a git checkout")
    expected = subprocess.run(
        ["git", "describe", "--tags", "--always", "--dirty"],
        capture_output=True, text=True, check=True, timeout=5, cwd=REPO_ROOT,
    ).stdout.strip()
    assert _git_checkout_state() == expected


def test_version_string_appends_checkout_state():
    if not (REPO_ROOT / ".git").exists():
        pytest.skip("not running from a git checkout")
    out = _version_string()
    assert out.startswith(f"sourced {sourced.__version__}")
    assert "(checkout " in out


def test_no_git_binary_falls_back(monkeypatch):
    monkeypatch.setattr("sourced.cli.shutil.which", lambda _name: None)
    assert _git_checkout_state() is None
    assert _version_string() == f"sourced {sourced.__version__}"


def test_git_failure_falls_back(monkeypatch):
    def boom(*args, **kwargs):
        raise subprocess.SubprocessError("git exploded")

    monkeypatch.setattr("sourced.cli.subprocess.run", boom)
    assert _git_checkout_state() is None
    assert _version_string() == f"sourced {sourced.__version__}"


def test_wheel_layout_falls_back(monkeypatch, tmp_path):
    # Simulate a site-packages install: package dir not under src/, no .git.
    fake_pkg = tmp_path / "site-packages" / "sourced"
    fake_pkg.mkdir(parents=True)
    monkeypatch.setattr("sourced.cli.__file__", str(fake_pkg / "cli.py"))
    assert _git_checkout_state() is None
