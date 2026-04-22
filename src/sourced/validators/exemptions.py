"""§10 exemption syntax validation. POST-render.

Voice files may exempt themselves from specific §10 Never-list rules via:
    ## §10 exemptions

    - em-dash-allowed: explanation
    - not-x-but-y: explanation

Canonical ids come from CLAUDE.md's `### Never (rewrite on sight)` section,
where each rule carries `[id: <id>]`. This validator checks that every
exemption id in the voice resolves to a canonical id; typos are caught.
"""
from __future__ import annotations
import re

from . import Finding


_VOICE_EXEMPTION_SECTION_RE = re.compile(r"^## §10 exemptions(\s|$)")
_OTHER_SECTION_RE = re.compile(r"^## ")
_BULLET_ID_RE = re.compile(r"^- ([a-z0-9-]+)(\s|:|$)")

_NEVER_SECTION_RE = re.compile(r"^### Never \(rewrite on sight\)(\s|$)")
_OTHER_HASH3_SECTION_RE = re.compile(r"^### ")
_ID_TOKEN_RE = re.compile(r"\[id:\s*([a-z0-9-]+)\s*\]")


def extract_voice_exemptions(voice_text: str) -> list[str]:
    """Return ids declared under ## §10 exemptions. Free-prose bullets ignored."""
    ids: list[str] = []
    in_section = False
    for line in voice_text.splitlines():
        if _VOICE_EXEMPTION_SECTION_RE.match(line):
            in_section = True
            continue
        if _OTHER_SECTION_RE.match(line) and in_section:
            in_section = False
            continue
        if in_section:
            m = _BULLET_ID_RE.match(line)
            if m:
                ids.append(m.group(1))
    return ids


def extract_canonical_ids(claude_md_text: str) -> list[str]:
    """Return ids declared in CLAUDE.md's ### Never (rewrite on sight) section."""
    ids: list[str] = []
    in_section = False
    for line in claude_md_text.splitlines():
        if _NEVER_SECTION_RE.match(line):
            in_section = True
            continue
        if _OTHER_HASH3_SECTION_RE.match(line) and in_section:
            in_section = False
            continue
        if in_section:
            ids.extend(_ID_TOKEN_RE.findall(line))
    return ids


def validate(voice: str, claude_md: str, voice_name: str) -> list[Finding]:
    """Each exemption id in the voice must match a canonical id from CLAUDE.md."""
    declared = extract_voice_exemptions(voice)
    if not declared:
        return []
    canonical = set(extract_canonical_ids(claude_md))
    findings: list[Finding] = []
    for d in declared:
        if d not in canonical:
            findings.append(Finding(
                rule="exemption-unknown-id",
                location=f"voice '{voice_name}' ## §10 exemptions",
                severity="error",
                message=f"exemption id {d!r} does not match any canonical id in CLAUDE.md §10 Never list.",
                fix_hint=(
                    "either fix the typo in the voice file, or add the rule to "
                    "CLAUDE.md's `### Never (rewrite on sight)` section with an [id: ...] tag."
                ),
            ))
    return findings
