"""Canonical-fragment registry for the template-duplication consistency test (issue #34).

The bundle and docs copy prose fragments and shared facts across many files with no
include mechanism, so a shared-fact edit has to touch every copy by hand. This registry
is the single source of truth for each duplicated fragment: either the canonical text
itself, or a designated canonical file the text is extracted from, plus the list of
mirror locations that must match it. ``test_fragment_consistency.py`` turns any drift
between mirrors into a CI failure.

To extend: add one entry to the relevant list below. No test code changes needed.

- FRAGMENTS: verbatim prose (and version strings) every mirror must contain.
- IDENTICAL_FILES: whole files that must stay byte-for-byte identical.
- DERIVED_COUNTS: a number counted from disk, asserted against the number each doc states.
- DERIVED_SETS: a set of names counted from disk, asserted present in each doc that lists them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Everything is anchored at the repo root computed from this file's location, NOT via
# ``importlib.resources.files("sourced")``. The package may be editable-installed from a
# different checkout (e.g. when running inside a git worktree), so files("sourced") can
# resolve to the wrong tree. Repo-root anchoring always reads the tree the tests live in.
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA = REPO_ROOT / "src" / "sourced" / "data"
TEMPLATES = DATA / "templates"
VOICES = TEMPLATES / "voices"
STYLES = TEMPLATES / "styles"
AGENTS = DATA / "agents"
SKILLS = DATA / "skills"
DOCS = REPO_ROOT / "docs"

STYLE_NAMES = ("apa7", "chicago17-ad", "chicago17-nb", "ieee", "mla9")
VOICE_NAMES = ("academic", "casual", "hybrid", "journalistic", "narrative", "technical")

STYLE_FILES = tuple(STYLES / f"{n}.md" for n in STYLE_NAMES)
VOICE_FILES = tuple(VOICES / f"{n}.md" for n in VOICE_NAMES)

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}


def parse_count(token: str) -> int:
    """Parse a count written as digits ('5') or a number word ('Five')."""
    t = token.strip().lower()
    if t.isdigit():
        return int(t)
    if t in _NUMBER_WORDS:
        return _NUMBER_WORDS[t]
    raise ValueError(f"unparseable count token {token!r}")


def block(path: Path, heading: str) -> str:
    """Return the '## heading' block (heading line through the line before the next
    '## ' heading or EOF), stripped. Raises if the heading is absent."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.strip() == f"## {heading}"), None)
    if start is None:
        raise ValueError(f"'## {heading}' not found in {path}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "".join(lines[start:end]).strip()


def line_containing(path: Path, needle: str) -> str:
    """Return the single stripped line in ``path`` that contains ``needle``."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if needle in line:
            return line.strip()
    raise ValueError(f"no line containing {needle!r} in {path}")


# ----- ground-truth derivers (count/enumerate the real thing on disk) -----

def count_styles() -> int:
    return len(list(STYLES.glob("*.md")))


def count_voices() -> int:
    return len(list(VOICES.glob("*.md")))


def count_paste_targets() -> int:
    # One golden file per paste target, per style. apa7 is representative.
    return sum(1 for _ in (REPO_ROOT / "tests" / "parity" / "apa7" / "golden").iterdir())


def count_modes() -> int:
    """Count data rows in the §7.1 mode registry table of the shipped CLAUDE.md."""
    text = (TEMPLATES / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"### 7\.1 Mode registry\n(.*?)\n### 7\.2", text, re.S)
    if not m:
        raise ValueError("§7.1 Mode registry table not found in templates/CLAUDE.md")
    # Data rows begin '| <lowercase mode name>'; skip the header ('| Mode') and separator.
    return sum(1 for ln in m.group(1).splitlines() if re.match(r"\|\s*[a-z]", ln))


def count_editing_passes() -> int:
    """Count distinct numbered passes ('**Pass N') in the canonical editing.md body."""
    text = (TEMPLATES / "docs" / "modes" / "editing.md").read_text(encoding="utf-8")
    return len({int(n) for n in re.findall(r"\*\*Pass (\d+)", text)})


def skill_names() -> tuple[str, ...]:
    """Basenames of the shipped skill directories."""
    return tuple(sorted(d.name for d in SKILLS.iterdir() if d.is_dir()))


def node_min_version() -> str:
    """Minimum Node version declared in the skill's package.json engines field."""
    pkg = (SKILLS / "browser-reader-extract" / "package.json").read_text(encoding="utf-8")
    m = re.search(r'"node"\s*:\s*">=?\s*(\d+)', pkg)
    if not m:
        raise ValueError("engines.node not found in browser-reader-extract/package.json")
    return m.group(1)


def pandoc_min_version() -> str:
    """major.minor of the pinned pandoc version in tests/parity/PANDOC_VERSION."""
    pinned = (REPO_ROOT / "tests" / "parity" / "PANDOC_VERSION").read_text(encoding="utf-8")
    m = re.search(r"(\d+\.\d+)", pinned)
    if not m:
        raise ValueError("no version in tests/parity/PANDOC_VERSION")
    return m.group(1)


# ----- entry types -----

@dataclass(frozen=True)
class Fragment:
    """A verbatim text fragment every mirror file must contain."""
    name: str
    canonical: str
    mirrors: tuple[Path, ...]


@dataclass(frozen=True)
class IdenticalFiles:
    """A set of files that must stay byte-for-byte identical."""
    name: str
    files: tuple[Path, ...]


@dataclass(frozen=True)
class CountMirror:
    """A doc location that states a count. ``pattern`` has one capture group = the number."""
    path: Path
    pattern: str


@dataclass(frozen=True)
class DerivedCount:
    """A count derived from disk, compared against the number each mirror states."""
    name: str
    expected: int
    describe: str
    mirrors: tuple[CountMirror, ...]
    xfail: str | None = None  # set to a reason string when the mirror is known to be stale


@dataclass(frozen=True)
class DerivedSet:
    """A set of names derived from disk; each mirror must name every member."""
    name: str
    expected: tuple[str, ...]
    describe: str
    mirrors: tuple[Path, ...]


# ----- prose fragments (verbatim-contains) -----

FRAGMENTS: tuple[Fragment, ...] = (
    # --- style bundle (5 shipped styles) ---
    Fragment(
        "style-special-tokens-block",
        block(STYLES / "apa7.md", "Special tokens"),
        STYLE_FILES,
    ),
    Fragment(
        "style-opening-head-sentence",
        "This file is the per-project style reference read by "
        "`[formatting mode]` (CLAUDE.md §7).",
        STYLE_FILES,
    ),
    Fragment(
        "style-opening-tail-sentence",
        "This file specifies only what pandoc+CSL does not encode: document layout, "
        "paste-target flags, post-pandoc hooks, and special-token policy.",
        STYLE_FILES,
    ),
    Fragment(
        "style-latex-compile-instruction",
        line_containing(STYLES / "apa7.md", "Compile with `pdflatex"),
        STYLE_FILES,
    ),
    Fragment(
        # The head of the smart-quotes filter note diverges in apa7 (it inserts a
        # `(e.g., *Ma'heo'o*)` example); only this shared tail is guarded verbatim.
        "style-smart-quotes-filter-tail",
        "while letting pandoc's `-smart` writer curl English apostrophes and quotes "
        "outside italics. `[formatting mode]` resolves the name to "
        "`~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the "
        "pandoc invocation.",
        STYLE_FILES,
    ),
    # --- voice skeletons (6 shipped voices) ---
    Fragment(
        "voice-iron-rules-preamble",
        block(VOICES / "academic.md", "Iron rules"),
        VOICE_FILES,
    ),
    Fragment(
        "voice-section-10-exemptions",
        block(VOICES / "academic.md", "§10 exemptions"),
        VOICE_FILES,
    ),
    Fragment(
        "voice-read-in-full-instruction",
        line_containing(VOICES / "academic.md", "Read this file in full"),
        VOICE_FILES,
    ),
    # --- version facts (derived from the source of truth, mirrored in docs) ---
    Fragment(
        "node-min-version",
        f"Node {node_min_version()}",
        (
            SKILLS / "browser-reader-extract" / "SKILL.md",
            REPO_ROOT / "README.md",
            DOCS / "SKILLS.md",
        ),
    ),
    Fragment(
        "pandoc-min-version",
        f"{pandoc_min_version()}+",
        (REPO_ROOT / "README.md",),
    ),
)


# ----- whole-file duplicates (byte-identical) -----

IDENTICAL_FILES: tuple[IdenticalFiles, ...] = (
    IdenticalFiles(
        "classical-abbreviations",
        tuple(STYLES / n / "classical-abbreviations.md"
              for n in ("chicago17-ad", "chicago17-nb", "mla9")),
    ),
)


# ----- fact counts (derived from disk, asserted against doc text) -----

ARCH = REPO_ROOT / "ARCHITECTURE.md"
ROADMAP = REPO_ROOT / "ROADMAP.md"
README = REPO_ROOT / "README.md"

DERIVED_COUNTS: tuple[DerivedCount, ...] = (
    DerivedCount(
        "shipped-styles",
        count_styles(),
        "src/sourced/data/templates/styles/*.md",
        (
            CountMirror(ARCH, r"(\w+) shipped slim styles"),
            CountMirror(ARCH, r"(\w+) styles × \d+ paste targets"),
            CountMirror(ROADMAP, r"[Aa]ll (\w+) styles"),
            CountMirror(README, r"(\w+) styles ship"),
        ),
    ),
    DerivedCount(
        "shipped-voices",
        count_voices(),
        "src/sourced/data/templates/voices/*.md",
        (
            CountMirror(ARCH, r"(\w+) shipped voices"),
            CountMirror(README, r"(\w+) shipped register skeletons"),
        ),
    ),
    DerivedCount(
        "paste-targets",
        count_paste_targets(),
        "tests/parity/apa7/golden/* (one golden per paste target)",
        (
            CountMirror(README, r"across (\w+) paste targets"),
            CountMirror(ARCH, r"× (\w+) paste targets"),
            CountMirror(ARCH, r"all (\w+) paste targets"),
            CountMirror(ROADMAP, r"all (\w+) paste targets"),
        ),
    ),
    DerivedCount(
        "cognitive-modes",
        count_modes(),
        "§7.1 mode registry rows in templates/CLAUDE.md",
        (
            CountMirror(README, r"(\w+) cognitive modes"),
            CountMirror(DOCS / "MODES.md", r"(\w+) cognitive modes"),
        ),
    ),
    DerivedCount(
        "editing-passes",
        count_editing_passes(),
        "distinct numbered passes in templates/docs/modes/editing.md",
        (CountMirror(DOCS / "MODES.md", r"(\w+)-pass audit"),),
    ),
)


# ----- name sets (derived from disk, asserted present in each list) -----

DERIVED_SETS: tuple[DerivedSet, ...] = (
    DerivedSet(
        "shipped-voice-names",
        VOICE_NAMES,
        "src/sourced/data/templates/voices/*.md basenames",
        (
            AGENTS / "voice-extractor.md",
            ARCH,
            README,
            DOCS / "VOICES.md",
        ),
    ),
    DerivedSet(
        "shipped-style-names",
        STYLE_NAMES,
        "src/sourced/data/templates/styles/*.md basenames",
        (
            ARCH,
            ROADMAP,
        ),
    ),
    DerivedSet(
        "shipped-skill-names",
        skill_names(),
        "src/sourced/data/skills/* directory names",
        (
            DOCS / "SKILLS.md",
            DOCS / "INSTALL.md",
            README,
            ARCH,
        ),
    ),
)
