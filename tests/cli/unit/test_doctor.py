"""Unit tests for the doctor diagnostic functions.

Each function takes injectable inputs (a claude_home path, a package dir, a cwd,
a conda prefix, a PATH string) so the failure paths are driven directly without
touching the real environment.
"""
from pathlib import Path

from sourced.commands import doctor


# ----- check_claude_health -----

def _seed_claude_home(root: Path) -> Path:
    """A fully-populated ~/.claude/ (every expected subdir non-empty + config)."""
    home = root / ".claude"
    for sub in doctor.EXPECTED_SUBDIRS:
        d = home / sub
        d.mkdir(parents=True)
        (d / "placeholder").write_text("x", encoding="utf-8")
    (home / "sourced.config").write_text("SOURCED_USER=x\n", encoding="utf-8")
    return home


def test_health_all_present_passes(tmp_path):
    home = _seed_claude_home(tmp_path)
    results = doctor.check_claude_health(claude_home=home)
    assert all(r.status == "pass" for r in results)


def test_health_missing_home_fails(tmp_path):
    results = doctor.check_claude_health(claude_home=tmp_path / "nope")
    assert len(results) == 1
    assert results[0].status == "fail"
    assert "does not exist" in results[0].detail
    assert "global-install" in results[0].fix


def test_health_flags_empty_dir_as_wipe(tmp_path):
    home = _seed_claude_home(tmp_path)
    # Empty out one subdir to simulate a partial wipe.
    for child in (home / "agents").iterdir():
        child.unlink()
    results = doctor.check_claude_health(claude_home=home)
    agents = next(r for r in results if r.name == "~/.claude/agents/")
    assert agents.status == "warn"
    assert "empty" in agents.detail
    assert "global-install" in agents.fix


def test_health_flags_missing_dir(tmp_path):
    home = _seed_claude_home(tmp_path)
    import shutil
    shutil.rmtree(home / "skills")
    results = doctor.check_claude_health(claude_home=home)
    skills = next(r for r in results if r.name == "~/.claude/skills/")
    assert skills.status == "fail"
    assert "missing" in skills.detail


def test_health_flags_missing_config(tmp_path):
    home = _seed_claude_home(tmp_path)
    (home / "sourced.config").unlink()
    results = doctor.check_claude_health(claude_home=home)
    cfg = next(r for r in results if r.name == "sourced.config")
    assert cfg.status == "warn"
    assert "global-install" in cfg.fix


# ----- check_editable_install -----

def _make_checkout(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir()
    (root / "src" / "sourced").mkdir(parents=True)
    return root


def test_editable_stale_path_warns(tmp_path):
    new = _make_checkout(tmp_path / "code-sourced")
    old_pkg = tmp_path / "old-sourced" / "src" / "sourced"  # need not exist on disk
    results = doctor.check_editable_install(pkg_dir=old_pkg, cwd=new)
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "stale" in results[0].detail
    assert str(new) in results[0].detail
    assert "pip install -e ." in results[0].fix


def test_editable_current_passes(tmp_path):
    checkout = _make_checkout(tmp_path / "sourced")
    pkg = checkout / "src" / "sourced"
    results = doctor.check_editable_install(pkg_dir=pkg, cwd=checkout)
    assert results[0].status == "pass"
    assert "current" in results[0].detail


def test_editable_wheel_install_skips(tmp_path):
    # Package dir not under a src/ parent → a wheel/site-packages install.
    pkg = tmp_path / "site-packages" / "sourced"
    results = doctor.check_editable_install(pkg_dir=pkg, cwd=tmp_path)
    assert results[0].status == "skip"
    assert "wheel" in results[0].detail or "site-packages" in results[0].detail


def test_editable_not_in_checkout_skips(tmp_path):
    pkg = tmp_path / "somewhere" / "src" / "sourced"
    results = doctor.check_editable_install(pkg_dir=pkg, cwd=tmp_path / "unrelated")
    assert results[0].status == "skip"
    assert "nothing to compare" in results[0].detail


# ----- check_conda_poisoning -----

def test_conda_interpreter_inside_prefix_warns():
    results = doctor.check_conda_poisoning(
        conda_prefix="/opt/conda/envs/foo",
        executable="/opt/conda/envs/foo/bin/python",
    )
    assert len(results) == 1
    assert results[0].status == "warn"
    assert "conda deactivate" in results[0].fix


def test_conda_interpreter_outside_prefix_skips():
    results = doctor.check_conda_poisoning(
        conda_prefix="/opt/conda/envs/foo",
        executable="/usr/bin/python3",
    )
    assert results[0].status == "skip"


def test_conda_unset_yields_no_rows():
    assert doctor.check_conda_poisoning(conda_prefix="", executable="/usr/bin/python3") == []


# ----- check_path_shadowing -----

def test_path_shadowing_names_winner(tmp_path):
    first = tmp_path / "a"
    second = tmp_path / "b"
    for d in (first, second):
        d.mkdir()
        (d / "sourced").write_text("#!/bin/sh\n", encoding="utf-8")
    results = doctor.check_path_shadowing(path_env=f"{first}:{second}")
    assert len(results) == 1
    assert results[0].status == "warn"
    assert str(first / "sourced") in results[0].detail
    assert str(second / "sourced") in results[0].detail


def test_path_single_entry_yields_no_rows(tmp_path):
    d = tmp_path / "a"
    d.mkdir()
    (d / "sourced").write_text("#!/bin/sh\n", encoding="utf-8")
    assert doctor.check_path_shadowing(path_env=str(d)) == []
