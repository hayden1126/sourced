"""Parity test: for each common flag set, install.sh and the CLI should produce
the same set of files in the project + ~/.claude/. Documented diffs (.sourced.bak,
sourced.config format) are filtered.
"""
import os
import subprocess
import sys
from pathlib import Path
import pytest


def _file_set(root: Path, *, exclude_suffixes: tuple[str, ...] = (".sourced.bak",)) -> set[str]:
    out = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        if any(rel.endswith(suf) for suf in exclude_suffixes):
            continue
        out.add(rel)
    return out


@pytest.mark.parametrize("flags", [
    ["--brief", "p1"],
    ["--brief", "p1", "--voice", "casual"],
    ["--brief", "p1", "--style", "mla9"],
    ["--brief", "p1", "--type", "annotated-bib"],
])
def test_install_file_set_matches(flags, tmp_path, repo_with_legacy_paths):
    """For each flag combination, install.sh and the CLI should produce equivalent
    file sets (modulo documented diffs)."""
    pythonpath = str(Path(__file__).resolve().parents[3] / "src")
    base_env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "PYTHONPATH": pythonpath}

    # ---- install.sh side ----
    home_a = tmp_path / "home_a"; home_a.mkdir()
    proj_a = tmp_path / "proj_a"; proj_a.mkdir()
    env_a = {**base_env, "HOME": str(home_a)}
    a_global = subprocess.run(
        ["bash", str(repo_with_legacy_paths / "install.sh"), "--global-only"],
        input="TestUser\n", capture_output=True, text=True, env=env_a,
    )
    assert a_global.returncode == 0, f"install.sh --global-only failed: {a_global.stderr}"
    a_install = subprocess.run(
        ["bash", str(repo_with_legacy_paths / "install.sh")] + flags,
        capture_output=True, text=True, cwd=proj_a, env=env_a,
    )
    assert a_install.returncode == 0, f"install.sh install failed: {a_install.stderr}"

    # ---- CLI side ----
    home_b = tmp_path / "home_b"; home_b.mkdir()
    proj_b = tmp_path / "proj_b"; proj_b.mkdir()
    env_b = {**base_env, "HOME": str(home_b)}
    b_global = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env_b,
    )
    assert b_global.returncode == 0, f"sourced global-install failed: {b_global.stderr}"
    b_install = subprocess.run(
        [sys.executable, "-m", "sourced", "install"] + flags,
        capture_output=True, text=True, cwd=proj_b, env=env_b,
    )
    assert b_install.returncode == 0, f"sourced install failed: {b_install.stderr}"

    # ---- Diff project file sets ----
    set_a = _file_set(proj_a)
    set_b = _file_set(proj_b)
    diff_a_only = set_a - set_b
    diff_b_only = set_b - set_a
    assert not diff_a_only, f"install.sh wrote files CLI didn't: {diff_a_only}"
    assert not diff_b_only, f"CLI wrote files install.sh didn't: {diff_b_only}"

    # ---- Diff ~/.claude/ file sets (excluding sourced.config — content format
    # is a documented diff per spec §8.3) ----
    claude_a = home_a / ".claude"
    claude_b = home_b / ".claude"
    set_ca = _file_set(claude_a) - {"sourced.config"}
    set_cb = _file_set(claude_b) - {"sourced.config"}
    assert set_ca == set_cb, (
        f"~/.claude/ diff:\n"
        f"  install.sh-only: {set_ca - set_cb}\n"
        f"  CLI-only: {set_cb - set_ca}"
    )
