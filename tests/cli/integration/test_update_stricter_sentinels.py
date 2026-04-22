import subprocess
import sys


def _bootstrap(tmp_home, tmp_project):
    subprocess.run(
        [sys.executable, "-m", "sourced", "global-install"],
        input="TestUser\n", capture_output=True, text=True, check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "sourced", "install", "--project", str(tmp_project)],
        capture_output=True, text=True, check=True,
    )


def test_update_rejects_indented_sentinel(tmp_home, tmp_project, clean_ansi):
    """F28 fix: indented sentinels are not real sentinels."""
    _bootstrap(tmp_home, tmp_project)
    claude = tmp_project / "CLAUDE.md"
    # Replace one of the column-0 sentinels with an indented copy.
    text = claude.read_text()
    text = text.replace(
        "<!-- sourced:begin managed -->",
        "  - <!-- sourced:begin managed -->",  # indented under a list bullet (legitimate prose)
        1,
    )
    claude.write_text(text)
    result = subprocess.run(
        [sys.executable, "-m", "sourced", "update", "--project", str(tmp_project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 5, result.stderr  # ProjectError
    assert "sentinel" in result.stderr.lower()
