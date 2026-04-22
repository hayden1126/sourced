"""~/.claude/sourced.config — user-global settings (currently just user name).

Format matches install.sh exactly: USER_NAME="<value>" on its own line.
We accept a few variants on read (quoted/unquoted, trailing whitespace) but
write the canonical form for round-trip with the legacy install.sh tag.
"""
from __future__ import annotations
import re
from pathlib import Path


def config_path() -> Path:
    return Path.home() / ".claude" / "sourced.config"


_USER_NAME_RE = re.compile(r'^\s*USER_NAME=(?:"([^"]*)"|(\S+))\s*$')


def load_user_name() -> str | None:
    p = config_path()
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        m = _USER_NAME_RE.match(line)
        if m:
            return m.group(1) if m.group(1) is not None else m.group(2)
    return None


def save_user_name(name: str) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    # Escape any embedded double-quote (rare; defensive).
    safe = name.replace('"', r'\"')
    p.write_text(f'USER_NAME="{safe}"\n', encoding="utf-8")
