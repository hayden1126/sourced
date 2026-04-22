"""Template rendering: bundled-resource access + pure substitution.

render() is a pure function — no I/O, no side effects. Reads happen via
read_template() (importlib.resources); writes happen in commands/*.py.
"""
from __future__ import annotations
import contextlib
import pathlib
import tempfile
from dataclasses import dataclass
from functools import cache
from importlib.resources import files, as_file
from pathlib import Path


@cache
def _data_root():
    """Bundled data root. Cached for stable reference identity across callers."""
    return files("sourced") / "data"


def read_template(subpath: str) -> str:
    """Read a bundled template as text. subpath is relative to src/sourced/data/."""
    return (_data_root() / subpath).read_text(encoding="utf-8")


def bundled_path(subpath: str) -> contextlib.AbstractContextManager[pathlib.Path]:
    """Context manager yielding a real filesystem Path for a bundled directory.
    Use with shutil.copytree which needs a concrete path.
    """
    return as_file(_data_root() / subpath)


@dataclass(frozen=True)
class RenderContext:
    """Substitution variables for render(). Pass voice_name/style_name as None
    when the template doesn't opt into them; the matching token stays verbatim.
    """
    user: str
    voice_name: str | None = None
    style_name: str | None = None


def render(template: str, ctx: RenderContext) -> str:
    """Apply substitutions. Pure: no I/O, no side effects."""
    out = template.replace("{{USER}}", ctx.user)
    if ctx.voice_name is not None:
        out = out.replace("{{VOICE}}", ctx.voice_name)
    if ctx.style_name is not None:
        out = out.replace("{{STYLE}}", ctx.style_name)
    return out


def write_atomic(path: Path, content: str) -> None:
    """Write content to path atomically (tempfile + rename in same dir).

    Avoids partial-write corruption if the process dies mid-write. Uses a
    randomized tempfile name (NamedTemporaryFile) so a stale .tmp from a
    previous crash doesn't collide. Skip explicit fsync — overkill for config files.

    Cross-device safe: tempfile is sibling to target → same filesystem → atomic
    rename on POSIX (and Windows 3.3+).

    Windows caveat: replace() raises PermissionError if target is open in another
    process (e.g., editor). Caller surfaces clearly.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
