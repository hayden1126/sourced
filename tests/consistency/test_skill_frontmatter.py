"""Shipped-skill frontmatter checks. Every ``src/sourced/data/skills/<name>/`` directory
must ship a SKILL.md whose frontmatter parses, whose ``name:`` equals the directory name
(Claude Code discovers skills by frontmatter), and whose ``description:`` is non-empty.
Companion to the ``shipped-skill-names`` derived set in ``registry.py``: that entry keeps
the docs honest about which skills ship; this file keeps the skill files themselves sane.
"""
from __future__ import annotations

import re

import pytest

from tests.consistency import registry as reg

_SKILL_DIRS = sorted(d for d in reg.SKILLS.iterdir() if d.is_dir())


def _frontmatter_fields(text: str) -> dict[str, str] | None:
    """Parse the leading ``---`` block into a key->value dict; None if absent."""
    m = re.match(r"---\r?\n(.*?)\r?\n---(\r?\n|$)", text, re.S)
    if not m:
        return None
    return {
        k.strip(): v.strip()
        for k, v in (ln.split(":", 1) for ln in m.group(1).splitlines() if ":" in ln)
    }


@pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=lambda d: d.name)
def test_skill_frontmatter(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    assert skill_md.is_file(), f"skills/{skill_dir.name}/ ships no SKILL.md"
    fields = _frontmatter_fields(skill_md.read_text(encoding="utf-8"))
    assert fields is not None, f"skills/{skill_dir.name}/SKILL.md has no frontmatter block"
    assert fields.get("name") == skill_dir.name, (
        f"skills/{skill_dir.name}/SKILL.md frontmatter name is {fields.get('name')!r}; "
        f"it must equal the directory name for Claude Code discovery"
    )
    assert fields.get("description"), (
        f"skills/{skill_dir.name}/SKILL.md frontmatter description is missing or empty"
    )
