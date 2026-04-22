"""~/.claude/sourced.config — user-global settings (currently just user name).

Format matches install.sh exactly:
    SOURCED_USER=<bash-quoted value>

install.sh writes via `printf '%q'`. We write via `shlex.quote()`, which
produces a different but equivalent bash-source-compatible quoting (single
quotes vs backslash escapes — bash sources both). We read via `shlex.split()`,
which correctly handles bash-style backslash escapes AND POSIX single-quoting,
so it round-trips with both writers.

Empty/missing values are normalized to None on read so callers don't need to
distinguish "absent" from "blank".
"""
from __future__ import annotations
import shlex
from pathlib import Path


_KEY = "SOURCED_USER"


def config_path() -> Path:
    return Path.home() / ".claude" / "sourced.config"


def load_user_name() -> str | None:
    p = config_path()
    if not p.exists():
        return None
    prefix = f"{_KEY}="
    for line in p.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith(prefix):
            continue
        rhs = stripped[len(prefix):]
        try:
            tokens = shlex.split(rhs, posix=True)
        except ValueError:
            return None
        if not tokens or not tokens[0]:
            return None
        return tokens[0]
    return None


def save_user_name(name: str) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"{_KEY}={shlex.quote(name)}\n", encoding="utf-8")
