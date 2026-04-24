"""Per-project state: project-type marker, voice/style markers, managed-block sentinels.

Distinct from config.py (user-global). Different lifecycle, different fixtures.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .errors import ProjectError

ProjectType = Literal["essay", "annotated-bib"]

# Sentinel parsing: column-0 strict per spec §5.5 (closes cycle-3 F28).
# install.sh's awk matched anywhere on the line, leading to silent corruption
# when the sentinel string appeared in user prose. The CLI is stricter.
BEGIN_RE = re.compile(r"^<!-- sourced:begin managed -->$", re.MULTILINE)
END_RE = re.compile(r"^<!-- sourced:end managed -->$", re.MULTILINE)

# Voice / style first-line markers — STRICT line-1-only matching to mirror
# install.sh's `sed -n '1s/^<!-- sourced:voice=\([a-zA-Z0-9_-]*\) -->$/\1/p'`.
# Loose matching against the full file text would silently mis-read if the
# marker string appeared in body prose (e.g., "this voice is more formal than
# `casual`").
VOICE_MARKER_RE = re.compile(r"^<!-- sourced:voice=([a-zA-Z0-9_-]+) -->$")
STYLE_MARKER_RE = re.compile(r"^<!-- sourced:style=([a-zA-Z0-9_-]+) -->$")


# ----- project type marker -----

def project_type_marker_path(project_dir: Path) -> Path:
    return project_dir / ".sourced-project-type"


def read_project_type(project_dir: Path) -> ProjectType:
    """Returns 'essay' if marker absent, empty, or whitespace-only (legacy default).
    Returns the trimmed value otherwise. Tolerates CRLF.
    """
    p = project_type_marker_path(project_dir)
    if not p.exists():
        return "essay"
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return "essay"
    if raw not in ("essay", "annotated-bib"):
        raise ProjectError(
            f".sourced-project-type contains unknown value {raw!r}; "
            f"expected 'essay' or 'annotated-bib'."
        )
    return raw  # type: ignore[return-value]


def write_project_type(project_dir: Path, kind: ProjectType) -> None:
    """Essay writes no marker (legacy-safe default).
    Non-essay types write the marker file."""
    p = project_type_marker_path(project_dir)
    if kind == "essay":
        p.unlink(missing_ok=True)
        return
    p.write_text(f"{kind}\n", encoding="utf-8")


# ----- voice / style markers -----

def _read_first_line(p: Path) -> str:
    """Read just the first line, trimmed of trailing newline. Empty string if file empty."""
    return p.read_text(encoding="utf-8").partition("\n")[0]


def read_voice_marker(voice_md: Path) -> str | None:
    if not voice_md.exists():
        return None
    m = VOICE_MARKER_RE.match(_read_first_line(voice_md))
    return m.group(1) if m else None


def read_style_marker(style_md: Path) -> str | None:
    if not style_md.exists():
        return None
    m = STYLE_MARKER_RE.match(_read_first_line(style_md))
    return m.group(1) if m else None


# ----- managed-block sentinels -----

def extract_managed_block(text: str) -> str:
    """Return the text between BEGIN and END sentinels (exclusive).
    Raises ProjectError if zero or >1 begin/end found."""
    begins = list(BEGIN_RE.finditer(text))
    ends = list(END_RE.finditer(text))
    if len(begins) == 0:
        raise ProjectError(
            "no <!-- sourced:begin managed --> sentinel at column 0; "
            "the file may not be a sourced-rendered CLAUDE.md, or the sentinel "
            "is indented (which the CLI's strict matcher rejects per spec §5.5)."
        )
    if len(ends) == 0:
        raise ProjectError(
            "begin sentinel found but no matching <!-- sourced:end managed --> sentinel."
        )
    if len(begins) > 1:
        raise ProjectError("multiple begin sentinels at column 0 in CLAUDE.md.")
    if len(ends) > 1:
        raise ProjectError("multiple end sentinels at column 0 in CLAUDE.md.")
    start = begins[0].end() + 1  # +1 to skip the trailing \n
    finish = ends[0].start()
    return text[start:finish]


def replace_managed_block(text: str, new_managed: str) -> str:
    """Replace the managed block (between sentinels) with new_managed.
    Sentinels themselves are kept; new_managed is the content between them."""
    begins = list(BEGIN_RE.finditer(text))
    ends = list(END_RE.finditer(text))
    if len(begins) != 1 or len(ends) != 1:
        # Defensive — extract_managed_block would have already raised.
        raise ProjectError("malformed sentinels; cannot replace managed block.")
    before = text[: begins[0].end()]
    after = text[ends[0].start() :]
    if new_managed and not new_managed.endswith("\n"):
        new_managed += "\n"
    return f"{before}\n{new_managed}{after}"


# ----- .sourced.bak rollback fallback (spec §5.7) -----

def bak_path(target: Path) -> Path:
    return target.with_suffix(target.suffix + ".sourced.bak")


def write_bak_sibling(target: Path) -> None:
    """Copy target to <target>.sourced.bak before mutation. No-op if target missing."""
    if not target.exists():
        return
    bak = bak_path(target)
    bak.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")


# ----- user-addition regions (phase 2 spec §7) -----

# Column-0 strict, matching the existing sentinel discipline.
USER_ADDITION_START_RE = re.compile(r"^<!-- sourced:user-addition start -->$")
USER_ADDITION_END_RE = re.compile(r"^<!-- sourced:user-addition end -->$")
# `^## ` at column 0, capturing the heading text (excluding the `## ` prefix).
# Matches only top-level `##` headings; `### ` subsections are intentionally
# NOT captured (phase-2 OQ3 resolution: section-header diff at `##` granularity).
SECTION_HEADING_RE = re.compile(r"^## (.+)$")


@dataclass(frozen=True)
class UserAddition:
    """A `<!-- sourced:user-addition start --> ... end -->` region preserved
    verbatim across `sourced update`.

    Attributes:
      section_heading: The `## ` heading containing the region's start marker,
        or None if the region appears before any `## ` heading.
      content: Verbatim text between the start and end markers, inclusive of
        both marker lines. Line endings preserved.
    """

    section_heading: str | None
    content: str


def parse_user_additions(text: str) -> list[UserAddition]:
    """Scan managed-block text for user-addition regions.

    Each region is attributed to the `## ` section containing its start marker;
    regions before the first `## ` heading carry `section_heading=None`.
    A region whose end marker appears under a different section than its start
    is still attributed to the start section.

    Phase-2 limit: markers are matched at column 0 regardless of surrounding
    fenced code blocks. Writers should not place the marker syntax inside a
    ```` ``` ```` fence; `sourced check` I6 will catch any mismatch in phase 3.

    Raises ProjectError on: unclosed start (no matching end), orphan end (no
    prior start), nested start (second start before first closed).
    """
    lines = text.split("\n")

    current_section: str | None = None
    region_start_idx: int | None = None
    region_start_section: str | None = None
    regions: list[UserAddition] = []

    for i, line in enumerate(lines):
        if region_start_idx is None:
            if USER_ADDITION_START_RE.match(line):
                region_start_idx = i
                region_start_section = current_section
            elif USER_ADDITION_END_RE.match(line):
                raise ProjectError(
                    f"line {i + 1}: <!-- sourced:user-addition end --> without a preceding "
                    f"<!-- sourced:user-addition start --> marker."
                )
            else:
                m = SECTION_HEADING_RE.match(line)
                if m:
                    current_section = m.group(1).strip()
        else:
            if USER_ADDITION_START_RE.match(line):
                raise ProjectError(
                    f"line {i + 1}: nested <!-- sourced:user-addition start --> without "
                    f"closing the region opened at line {region_start_idx + 1}."
                )
            if USER_ADDITION_END_RE.match(line):
                region_lines = lines[region_start_idx : i + 1]
                regions.append(
                    UserAddition(
                        section_heading=region_start_section,
                        content="\n".join(region_lines),
                    )
                )
                region_start_idx = None
                region_start_section = None

    if region_start_idx is not None:
        raise ProjectError(
            f"unclosed <!-- sourced:user-addition start --> marker at line "
            f"{region_start_idx + 1}; expected a matching end marker."
        )

    return regions


def _split_sections(text: str) -> list[tuple[str | None, list[str]]]:
    """Split text into (heading, body_lines) pairs.

    Preamble before the first `## ` heading has heading=None. Each section's
    body_lines INCLUDES the heading line itself, so reassembly is just
    `"\\n".join(body_lines)` per section.
    """
    result: list[tuple[str | None, list[str]]] = []
    current_heading: str | None = None
    current_body: list[str] = []
    for line in text.split("\n"):
        m = SECTION_HEADING_RE.match(line)
        if m:
            if current_body or current_heading is not None:
                result.append((current_heading, current_body))
            current_heading = m.group(1).strip()
            current_body = [line]
        else:
            current_body.append(line)
    if current_body or current_heading is not None:
        result.append((current_heading, current_body))
    return result


def _strip_user_additions(text: str) -> str:
    """Return text with all user-addition regions removed. Used to compare
    framework-content drift between old and fresh managed blocks."""
    result_lines: list[str] = []
    in_region = False
    for line in text.split("\n"):
        if USER_ADDITION_START_RE.match(line):
            in_region = True
            continue
        if USER_ADDITION_END_RE.match(line):
            in_region = False
            continue
        if not in_region:
            result_lines.append(line)
    return "\n".join(result_lines)


MIGRATED_ADDITIONS_HEADING = "Custom additions (migrated)"


def merge_managed_block(old_managed: str, fresh_managed: str) -> tuple[str, list[str]]:
    """Merge old user-addition regions into a fresh managed block.

    Fresh-template framework content always wins outside user-addition markers.
    User-addition regions from the old block are re-inserted at the end of
    their matching `## ` section in the fresh block. Regions whose section
    no longer exists in fresh are migrated to a "Custom additions (migrated)"
    section appended at the end.

    Returns (merged_text, warnings). Warnings are human-readable strings for
    surface to {{USER}} by `sourced update`; empty list when no warnings fire.

    Raises ProjectError if old_managed has malformed user-addition markers
    (unclosed, orphan, nested). See `parse_user_additions`.
    """
    warnings: list[str] = []
    additions = parse_user_additions(old_managed)

    if not additions:
        # No user-additions: fresh replaces old wholesale. Detect framework drift.
        _append_drift_warning(old_managed, fresh_managed, warnings)
        return fresh_managed, warnings

    fresh_sections = _split_sections(fresh_managed)
    fresh_section_index: dict[str, int] = {
        heading: idx for idx, (heading, _) in enumerate(fresh_sections) if heading is not None
    }

    orphaned: list[UserAddition] = []
    for add in additions:
        if add.section_heading is not None and add.section_heading in fresh_section_index:
            idx = fresh_section_index[add.section_heading]
            heading, body = fresh_sections[idx]
            # Drop trailing blanks from section body, then append region with a blank separator.
            while body and body[-1].strip() == "":
                body = body[:-1]
            body.append("")  # blank line separator
            body.extend(add.content.split("\n"))
            fresh_sections[idx] = (heading, body)
        else:
            orphaned.append(add)
            target = (
                f"§{add.section_heading!r}" if add.section_heading is not None else "preamble"
            )
            warnings.append(
                f"user-addition region originally under {target} has no matching "
                f"§ in fresh template; migrated to §'{MIGRATED_ADDITIONS_HEADING}'."
            )

    if orphaned:
        stash_lines: list[str] = ["", f"## {MIGRATED_ADDITIONS_HEADING}", ""]
        for add in orphaned:
            stash_lines.extend(add.content.split("\n"))
            stash_lines.append("")
        fresh_sections.append((MIGRATED_ADDITIONS_HEADING, stash_lines))

    merged_lines: list[str] = []
    for _, body in fresh_sections:
        merged_lines.extend(body)
    merged = "\n".join(merged_lines)
    # Preserve trailing newline if fresh had one.
    if fresh_managed.endswith("\n") and not merged.endswith("\n"):
        merged += "\n"

    _append_drift_warning(old_managed, fresh_managed, warnings)

    return merged, warnings


def _append_drift_warning(old_managed: str, fresh_managed: str, warnings: list[str]) -> None:
    """If old (stripped of user-additions) differs from fresh, surface one warning."""
    old_framework = _strip_user_additions(old_managed).strip()
    fresh_framework = fresh_managed.strip()
    if old_framework == fresh_framework:
        return
    old_headings = [m.group(1).strip() for m in SECTION_HEADING_RE.finditer(old_framework)]
    fresh_headings = [m.group(1).strip() for m in SECTION_HEADING_RE.finditer(fresh_framework)]
    removed = [h for h in old_headings if h not in fresh_headings]
    added = [h for h in fresh_headings if h not in old_headings]
    parts = []
    if removed:
        parts.append(f"removed from fresh: {', '.join(repr(h) for h in removed)}")
    if added:
        parts.append(f"added in fresh: {', '.join(repr(h) for h in added)}")
    detail = "; ".join(parts) if parts else "framework content differs outside user-addition markers"
    warnings.append(
        f"old managed block drifted from fresh template ({detail}). "
        f"Fresh wins; .sourced.bak preserves your old file for manual recovery."
    )


# ----- phase-1 → phase-2 migration (spec §9) -----

PHASE1_BAK_NAME = "CLAUDE.md.phase1.bak"


def detect_phase1_layout(project_root: Path) -> bool:
    """Return True when the project looks like phase-1 (monolithic CLAUDE.md,
    no `docs/modes/`) AND the bundled templates carry a `docs/modes/` tree
    to migrate to. Returns False if already migrated or if phase 2 hasn't
    shipped a docs tree in the current bundle."""
    claude_md = project_root / "CLAUDE.md"
    docs_modes = project_root / "docs" / "modes"
    if not claude_md.exists():
        return False
    if docs_modes.exists():
        return False
    return _bundled_docs_modes_present()


def _bundled_docs_modes_present() -> bool:
    """Internal: does the installed bundle carry templates/docs/modes with any files?"""
    # Lazy import to avoid circular (render imports project).
    from .render import bundled_path

    try:
        with bundled_path("templates/docs/modes") as src:
            p = Path(src)
            if not p.exists():
                return False
            return any(f.is_file() for f in p.iterdir())
    except (FileNotFoundError, ModuleNotFoundError):
        return False


def deploy_docs_tree(project_root: Path) -> list[Path]:
    """Copy bundled templates/docs/ to `<project_root>/docs/`.

    Mirrors the tree (creates subdirs as needed), overwriting files if present.
    Returns the list of files written. No-op if the bundle carries no docs/.
    """
    from .render import bundled_path
    from .mirror import mirror_tree

    written: list[Path] = []
    try:
        with bundled_path("templates/docs") as src:
            src_path = Path(src)
            if not src_path.exists():
                return written
            dest = project_root / "docs"
            mirror_tree(src_path, dest, dry_run=False)
            for f in dest.rglob("*"):
                if f.is_file():
                    written.append(f)
    except (FileNotFoundError, ModuleNotFoundError):
        pass
    return written


# Overlay filename template: `20-project-type-<type>.md` per CLAUDE.d README's
# naming convention.
def _overlay_name_for_project_type(project_type: str) -> str:
    return f"20-project-type-{project_type}.md"


def deploy_overlays(project_root: Path, project_type: ProjectType) -> list[Path]:
    """Copy bundled CLAUDE.d/ drop-ins to `<project_root>/CLAUDE.d/`.

    Always deploys README.md (the drop-in pattern explanation). Additionally
    deploys the `20-project-type-<type>.md` overlay when `project_type` is
    non-default (anything other than `essay`). Essay projects get the README
    only; the base manifest is already complete for essays.

    Writer-authored overlays in the `10-local-*` band are preserved across
    calls: only files shipped in the bundle are overwritten.

    Returns the list of files written. No-op on the README / overlay if the
    bundle carries no CLAUDE.d/ tree.
    """
    from .render import bundled_path

    written: list[Path] = []
    dest_dir = project_root / "CLAUDE.d"
    dest_dir.mkdir(exist_ok=True)

    shipped_names = ["README.md"]
    if project_type != "essay":
        shipped_names.append(_overlay_name_for_project_type(project_type))

    try:
        with bundled_path("templates/CLAUDE.d") as src:
            src_path = Path(src)
            if not src_path.exists():
                return written
            for name in shipped_names:
                src_file = src_path / name
                if not src_file.exists():
                    continue
                dest_file = dest_dir / name
                dest_file.write_text(src_file.read_text(encoding="utf-8"), encoding="utf-8")
                written.append(dest_file)
    except (FileNotFoundError, ModuleNotFoundError):
        pass
    return written


def migrate_phase1_to_phase2(project_root: Path, fresh_claude_md: str) -> list[str]:
    """Atomic migration for a phase-1 project.

    Steps:
      1. Rename existing CLAUDE.md to CLAUDE.md.phase1.bak (or leave existing
         .phase1.bak alone if one is already present).
      2. Write the fresh rendered CLAUDE.md.
      3. Deploy the bundled docs/ tree.

    Returns a list of human-readable notes surfaced to {{USER}} by `sourced update`.
    Does not handle voice.md / style.md — those are refreshed by the caller.
    """
    notes: list[str] = []
    old_path = project_root / "CLAUDE.md"
    bak_path_ = project_root / PHASE1_BAK_NAME

    if bak_path_.exists():
        notes.append(
            f"{PHASE1_BAK_NAME} already exists; leaving untouched and proceeding with a fresh render."
        )
    else:
        bak_path_.write_text(old_path.read_text(encoding="utf-8"), encoding="utf-8")
        notes.append(
            f"migrated phase-1 CLAUDE.md → {PHASE1_BAK_NAME}; rollback available via "
            f"`mv {PHASE1_BAK_NAME} CLAUDE.md` until the next release cycle."
        )

    old_path.write_text(fresh_claude_md, encoding="utf-8")

    files = deploy_docs_tree(project_root)
    if files:
        notes.append(f"deployed {len(files)} file(s) under docs/ (mode bodies + supporting docs).")

    return notes
