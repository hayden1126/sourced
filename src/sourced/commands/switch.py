"""sourced switch voice|style <name> — swap voice/style on existing project."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import ProjectError, UsageError
from ..project import write_bak_sibling
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(ctx: Context, *, kind: str, name: str, project: str | None = None) -> int:
    if kind not in ("voice", "style"):
        raise UsageError(f"unknown switch kind: {kind!r}; expected 'voice' or 'style'.")

    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    md_name = "voice.md" if kind == "voice" else "style.md"
    md_path = target / md_name

    if not md_path.exists():
        raise ProjectError(
            f"no {md_name} at {md_path}; this doesn't look like a sourced project. "
            f"Run `sourced install --project {target} --force --{kind} {name}` "
            f"to recreate from scratch."
        )

    user = _pipeline.ensure_user_name(ctx)

    if kind == "voice":
        new_text = _pipeline.render_voice(name, user, ctx)
    else:
        new_text = _pipeline.render_style(name, user, ctx)

    if ctx.dry_run:
        if not ctx.quiet:
            print(f"DRY RUN — would refresh {path_str(str(md_path), use_color)} "
                  f"({kind}={name}).")
        return 0

    write_bak_sibling(md_path)
    write_atomic(md_path, new_text)
    if not ctx.quiet:
        print(f"{bold('Switched', use_color)} {kind} → {name} at {path_str(str(md_path), use_color)}")
    return 0
