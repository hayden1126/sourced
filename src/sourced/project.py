"""Per-project state: project-type marker, voice/style markers, managed-block sentinels.

Distinct from config.py (user-global). Different lifecycle, different fixtures.
"""
from __future__ import annotations
import re
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
