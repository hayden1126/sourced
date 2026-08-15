import os
import subprocess
import sys


def _bootstrap(tmp_home):
    """global-install into a tmp HOME, returning the env for further doctor runs."""
    env = {
        "HOME": str(tmp_home),
        "PATH": os.environ.get("PATH", ""),
        "NO_COLOR": "1",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    return env


def test_sourced_doctor_runs(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "doctor"],
        capture_output=True, text=True,
    )
    # Exit 0 when nothing is broken, 4 when a hard breakage is found. Either is
    # "runs cleanly." doctor is read-only, so it never mutates on the way there.
    assert result.returncode in (0, 4)
    assert "Prerequisites" in result.stdout or "~/.claude/" in result.stdout
    # The summary footer is always printed unless --quiet.
    assert "passed." in result.stdout


def test_sourced_doctor_quiet_is_silent(clean_ansi):
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--quiet", "doctor"],
        capture_output=True, text=True,
    )
    assert result.returncode in (0, 4)
    assert result.stdout == ""


def test_strict_escalates_a_warning_to_failure(tmp_home, clean_ansi):
    # A healthy install with one emptied subdir yields a warning (wipe detection)
    # but no hard failure: plain doctor exits 0, --strict exits 4.
    env = _bootstrap(tmp_home)
    agents = tmp_home / ".claude" / "agents"
    for child in agents.iterdir():
        child.unlink()  # leave the dir present but empty

    plain = subprocess.run(
        [sys.executable, "-m", "sourced", "doctor"],
        capture_output=True, text=True, env=env,
    )
    assert plain.returncode == 0
    assert "present but empty" in plain.stdout

    strict = subprocess.run(
        [sys.executable, "-m", "sourced", "--strict", "doctor"],
        capture_output=True, text=True, env=env,
    )
    assert strict.returncode == 4


def test_mirror_currency_flags_a_deleted_managed_file(tmp_home, clean_ansi):
    # A fresh install is mirror-current; deleting one shipped file surfaces it as
    # a missing-managed-file warning (not a hard failure).
    env = _bootstrap(tmp_home)
    clean = subprocess.run(
        [sys.executable, "-m", "sourced", "doctor"],
        capture_output=True, text=True, env=env,
    )
    assert "differ from the bundle" not in clean.stdout
    assert "not installed" not in clean.stdout

    (tmp_home / ".claude" / "filters" / "smart-quotes.lua").unlink()
    after = subprocess.run(
        [sys.executable, "-m", "sourced", "doctor"],
        capture_output=True, text=True, env=env,
    )
    assert after.returncode == 0  # advisory
    assert "not installed" in after.stdout
    assert "smart-quotes.lua" in after.stdout
