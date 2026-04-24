"""§10 exemption syntax validation. POST-render.

Voice files may exempt themselves from specific §10 Never-list rules via:
    ## §10 exemptions

    - em-dashes: explanation
    - not-x-but-y: explanation

Canonical ids come from CLAUDE.md's `### 7.6 Precedence and canonical §10 IDs`
subsection, where each ID is a leading-backticked bullet (e.g.,
``- `em-dashes` — em-dash appositives, interruptions, ranges.``). I3 enforces
round-trip between §7.6 and writing.md `[id:]` tags, so §7.6 is the source of
truth for this validator's canonical set. This validator checks that every
exemption id in the voice resolves to a canonical id; typos are caught.
"""
from __future__ import annotations
import re

from . import Finding


_VOICE_EXEMPTION_SECTION_RE = re.compile(r"^## §10 exemptions(\s|$)")
_OTHER_SECTION_RE = re.compile(r"^## ")
_BULLET_ID_RE = re.compile(r"^- ([a-z0-9-]+)(\s|:|$)")

# §7.6 canonical-ID bullet shape: leading dash, backticked id, em-dash, prose.
# Mirrors invariants.py CANONICAL_ID_BULLET_RE so the two validators agree.
_CANONICAL_SUBSECTION_RE = re.compile(
    r"^### 7\.6 Precedence and canonical §10 IDs(\s|$)"
)
_OTHER_HASH3_SECTION_RE = re.compile(r"^### ")
_OTHER_HASH2_SECTION_RE = re.compile(r"^## ")
_CANONICAL_BULLET_RE = re.compile(r"^- `([a-z][a-z0-9-]*)`")


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
    """Return ids declared in CLAUDE.md's §7.6 canonical-ID list."""
    ids: list[str] = []
    in_section = False
    for line in claude_md_text.splitlines():
        if _CANONICAL_SUBSECTION_RE.match(line):
            in_section = True
            continue
        # Subsection ends at next ### or ##.
        if (_OTHER_HASH3_SECTION_RE.match(line) or _OTHER_HASH2_SECTION_RE.match(line)) and in_section:
            in_section = False
            continue
        if in_section:
            m = _CANONICAL_BULLET_RE.match(line)
            if m:
                ids.append(m.group(1))
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
                message=f"exemption id {d!r} does not match any canonical id in CLAUDE.md §7.6.",
                fix_hint=(
                    "either fix the typo in the voice file, or add the id to "
                    "CLAUDE.md's `### 7.6 Precedence and canonical §10 IDs` "
                    "and a matching `[id: ...]` tag in writing.md §Never-list (round-trip enforced by I3)."
                ),
            ))
    return findings
