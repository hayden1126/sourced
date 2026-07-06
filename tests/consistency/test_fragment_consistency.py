"""Option-C consistency test for issue #34 (template duplication without an include
mechanism). Each duplicated fragment or shared fact has one source of truth in
``registry.py``; these tests assert every mirror still matches, so drift fails CI.

Failure messages name the drifted file and show a diff hint so the fix is one edit,
not an investigation. Add new clusters by extending the registry lists, not this file.
"""
from __future__ import annotations

import difflib
import re

import pytest

from tests.consistency import registry as reg


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + ln for ln in text.splitlines()) or prefix + "(empty)"


def _closest_window(haystack: str, needle: str) -> str:
    """Best-matching same-length-ish window of ``haystack`` for a diff hint."""
    matcher = difflib.SequenceMatcher(None, haystack, needle)
    a, _b, _size = matcher.find_longest_match(0, len(haystack), 0, len(needle))
    lo = max(0, a - 20)
    hi = min(len(haystack), a + len(needle) + 20)
    return haystack[lo:hi]


def _rel(path) -> str:
    return str(path.relative_to(reg.REPO_ROOT))


# ----- verbatim prose fragments -----

_FRAGMENT_CASES = [
    pytest.param(f.name, f.canonical, m, id=f"{f.name}::{_rel(m)}")
    for f in reg.FRAGMENTS
    for m in f.mirrors
]


@pytest.mark.parametrize("name, canonical, mirror", _FRAGMENT_CASES)
def test_fragment_mirror_matches(name, canonical, mirror):
    text = mirror.read_text(encoding="utf-8")
    if canonical not in text:
        pytest.fail(
            f"[{name}] {_rel(mirror)} does not contain the canonical fragment verbatim.\n"
            f"Expected verbatim:\n{_indent(canonical)}\n"
            f"Nearest text in the mirror:\n{_indent(_closest_window(text, canonical))}\n"
            f"Fix: restore the canonical text in {_rel(mirror)}. If the change is "
            f"intentional, update registry entry '{name}' and every mirror together."
        )


# ----- byte-identical whole files -----

_IDENTICAL_CASES = [
    pytest.param(g.name, g.files, id=g.name) for g in reg.IDENTICAL_FILES
]


@pytest.mark.parametrize("name, files", _IDENTICAL_CASES)
def test_identical_files(name, files):
    canonical_path = files[0]
    canonical = canonical_path.read_text(encoding="utf-8")
    for other in files[1:]:
        other_text = other.read_text(encoding="utf-8")
        if other_text != canonical:
            diff = "".join(
                difflib.unified_diff(
                    canonical.splitlines(keepends=True),
                    other_text.splitlines(keepends=True),
                    fromfile=_rel(canonical_path),
                    tofile=_rel(other),
                )
            )
            pytest.fail(
                f"[{name}] {_rel(other)} has drifted from {_rel(canonical_path)}.\n"
                f"{diff}\n"
                f"Fix: make {_rel(other)} identical to {_rel(canonical_path)}."
            )


# ----- derived counts -----

def _count_param(entry, mirror):
    marks = (
        (pytest.mark.xfail(reason=entry.xfail, strict=True),) if entry.xfail else ()
    )
    return pytest.param(
        entry, mirror, marks=marks,
        id=f"{entry.name}::{_rel(mirror.path)}::{mirror.pattern}",
    )


_COUNT_CASES = [
    _count_param(entry, mirror)
    for entry in reg.DERIVED_COUNTS
    for mirror in entry.mirrors
]


@pytest.mark.parametrize("entry, mirror", _COUNT_CASES)
def test_derived_count_matches(entry, mirror):
    text = mirror.path.read_text(encoding="utf-8")
    captures = re.findall(mirror.pattern, text)
    assert captures, (
        f"[{entry.name}] pattern {mirror.pattern!r} matched nothing in "
        f"{_rel(mirror.path)}; the phrasing changed. Update the pattern in registry "
        f"entry '{entry.name}'."
    )
    for token in captures:
        found = reg.parse_count(token)
        if found != entry.expected:
            pytest.fail(
                f"[{entry.name}] {_rel(mirror.path)} states {token!r} (= {found}) but "
                f"the on-disk ground truth is {entry.expected} "
                f"(counted from {entry.describe}).\n"
                f"Fix: update the count in {_rel(mirror.path)} to {entry.expected}."
            )


# ----- derived name sets -----

_SET_CASES = [
    pytest.param(entry, mirror, id=f"{entry.name}::{_rel(mirror)}")
    for entry in reg.DERIVED_SETS
    for mirror in entry.mirrors
]


@pytest.mark.parametrize("entry, mirror", _SET_CASES)
def test_derived_set_present(entry, mirror):
    text = mirror.read_text(encoding="utf-8")
    missing = [
        member
        for member in entry.expected
        if not re.search(rf"\b{re.escape(member)}\b", text)
    ]
    if missing:
        pytest.fail(
            f"[{entry.name}] {_rel(mirror)} does not name {missing} "
            f"(disk set = {list(entry.expected)}, from {entry.describe}).\n"
            f"Fix: add the missing name(s) to the list in {_rel(mirror)}, or update the "
            f"registry entry '{entry.name}' if the shipped set really changed."
        )
