"""sourced new <project-name> — sugar for: mkdir + cd + install --brief."""
from __future__ import annotations
from pathlib import Path

from ..context import Context
from ..errors import UsageError
from . import install


def run(
    ctx: Context,
    *,
    project_name: str,
    voice: str = "academic",
    style: str = "apa7",
    project_type: str = "essay",
    brief: str | None = None,
    force: bool = False,
) -> int:
    target = Path.cwd() / project_name

    if target.exists() and not force and any(target.iterdir()):
        raise UsageError(
            f"directory {target} already exists and is non-empty. "
            f"Pass --force, or use `sourced install --project {target}` to render into "
            f"the existing dir."
        )

    target.mkdir(parents=True, exist_ok=True)

    # Brief defaults to project_name
    brief_name = brief if brief else project_name

    return install.run(
        ctx,
        project=str(target),
        voice=voice,
        style=style,
        project_type=project_type,
        brief=brief_name,
        force=force,
    )
