"""Binding canary: iter_managed_files() must enumerate exactly what global-install
writes to ~/.claude/.

doctor's mirror-currency check trusts iter_managed_files() as the ground truth of
"what sourced installed." If install_global ever writes a file the enumeration omits
(or drops one it still lists), the two silently diverge and doctor mis-reports. This
test runs a real global-install and compares the on-disk file set to the enumeration,
so a change to one without the other fails loudly.
"""
import os
import subprocess
import sys

from sourced.commands._pipeline import iter_managed_files

# Files global-install writes that are user state, not bundle-mirrored content.
_NON_MANAGED = {"sourced.config"}


def _installed_relpaths(claude_home):
    return {
        str(p.relative_to(claude_home).as_posix())
        for p in claude_home.rglob("*")
        if p.is_file()
    } - _NON_MANAGED


def test_iter_managed_files_matches_global_install(tmp_home):
    env = {
        "HOME": str(tmp_home),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "NO_COLOR": "1",
    }
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, result.stderr

    on_disk = _installed_relpaths(tmp_home / ".claude")
    enumerated = {relpath for relpath, _ in iter_managed_files()}

    assert on_disk == enumerated, (
        "iter_managed_files() drifted from install_global.\n"
        f"  only on disk: {sorted(on_disk - enumerated)}\n"
        f"  only enumerated: {sorted(enumerated - on_disk)}"
    )


def test_iter_managed_files_content_matches_bundle(tmp_home):
    """The bytes iter_managed_files() yields are what actually lands on disk."""
    env = {
        "HOME": str(tmp_home),
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "NO_COLOR": "1",
    }
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    claude = tmp_home / ".claude"
    for relpath, data in iter_managed_files():
        assert (claude / relpath).read_bytes() == data, relpath
