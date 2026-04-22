import subprocess
import sys
import os


def test_no_color_env_suppresses(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home), "NO_COLOR": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout


def test_explicit_no_color_flag(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home)}
    env.pop("NO_COLOR", None)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--no-color", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout


def test_color_never_flag(tmp_home):
    env = {**os.environ, "HOME": str(tmp_home)}
    env.pop("NO_COLOR", None)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "--color", "never", "global-install"],
        input="TestUser\n", capture_output=True, text=True, env=env,
    )
    assert "\033[" not in result.stdout
