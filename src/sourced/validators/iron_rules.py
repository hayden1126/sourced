"""Iron-rule validation. POST-render: checks rendered voice file content.

A voice skeleton declares a set of iron rules under ## Iron rules, ## AI-tells,
or ## Generation signatures, plus any line marked with [iron]. Every such rule
must appear (normalized substring match) in the rendered voice library file.

This is the caller-side layer of iron-rule defense-in-depth (spec §9). install.sh
also runs the same check at render time as a mandatory backstop.
"""
from __future__ import annotations
import re

from . import Finding


# Section headers that mark iron-rule blocks. Match `## Iron rules` (and AI-tells,
# Generation signatures) with optional trailing whitespace, no other text on the line.
_IRON_SECTION_RE = re.compile(
    r"^## (Iron rules|AI-tells|Generation signatures)(\s|$)"
)
_OTHER_SECTION_RE = re.compile(r"^## ")
_IRON_TOKEN = "[iron]"


def extract_iron_rules(text: str) -> list[str]:
    """Return non-empty rule lines from iron sections + any [iron]-tagged lines."""
    rules: list[str] = []
    in_iron = False
    for line in text.splitlines():
        if _IRON_SECTION_RE.match(line):
            in_iron = True
            continue
        if _OTHER_SECTION_RE.match(line) and in_iron:
            in_iron = False
            # don't `continue` — fall through so [iron] lines in non-iron sections still get picked
        if in_iron and line.strip():
            rules.append(line)
    # Also pick up [iron]-tagged lines anywhere in the file.
    for line in text.splitlines():
        if _IRON_TOKEN in line and line not in rules:
            rules.append(line)
    return rules


def normalize_rule(s: str) -> str:
    """Lowercase, collapse whitespace, strip leading list marker + trailing sentence-final punct.

    Superset of install.sh's normalize_rule: additionally strips a leading markdown
    list marker (``-``, ``*``, or ``•`` followed by whitespace) so a rule extracted
    from a bulleted ``## Iron rules`` section matches a candidate that mentions the
    rule in plain prose. install.sh-compliant voices (which preserve bullets) remain
    accepted.
    """
    out = s.lower()
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"^[-*•]\s+", "", out)
    out = re.sub(r"[.!?]+$", "", out)
    return out


def _normalize_candidate(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def validate(skeleton: str, candidate: str, voice_name: str) -> list[Finding]:
    """Verify every iron rule from skeleton appears (normalized substring) in candidate."""
    iron_rules = extract_iron_rules(skeleton)
    if not iron_rules:
        return []
    candidate_norm = _normalize_candidate(candidate)
    findings: list[Finding] = []
    for raw in iron_rules:
        normalized = normalize_rule(raw)
        if not normalized:
            continue
        if normalized not in candidate_norm:
            findings.append(Finding(
                rule="iron-rule-missing",
                location=f"voice '{voice_name}'",
                severity="error",
                message=f"iron rule missing from rendered voice: {raw.strip()!r}",
                fix_hint=(
                    "if voice-extractor dropped or reworded this rule, regenerate the voice "
                    "with overwrite: true and re-run sourced install."
                ),
            ))
    return findings
