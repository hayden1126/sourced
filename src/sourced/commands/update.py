"""sourced update — refresh managed block of CLAUDE.md + voice.md + style.md."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import ProjectError
from ..project import (
    extract_managed_block,
    replace_managed_block,
    read_voice_marker,
    read_style_marker,
    write_bak_sibling,
)
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(ctx: Context, *, project: str | None = None, force: bool = False) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    claude_md_path = target / "CLAUDE.md"

    if not claude_md_path.exists():
        raise ProjectError(
            f"no CLAUDE.md at {claude_md_path}; nothing to update. "
            f"Use `sourced install --project {target}` to render fresh."
        )

    user = _pipeline.ensure_user_name(ctx)

    # Build the new CLAUDE.md.
    if force:
        new_claude = _pipeline.render_claude_md(user, ctx)
    else:
        # Refresh only the managed block.
        old_text = claude_md_path.read_text(encoding="utf-8")
        # Validate sentinels (raises ProjectError if malformed — F28 strictness).
        extract_managed_block(old_text)  # raises if bad

        # Render fresh CLAUDE.md, extract its managed block, splice into old.
        fresh_full = _pipeline.render_claude_md(user, ctx)
        fresh_managed = extract_managed_block(fresh_full)
        new_claude = replace_managed_block(old_text, fresh_managed)

    # Voice / style refresh: re-render from currently-installed library.
    voice_path = target / "voice.md"
    style_path = target / "style.md"
    voice_name = read_voice_marker(voice_path)
    style_name = read_style_marker(style_path)
    new_voice = _pipeline.render_voice(voice_name, user, ctx) if voice_name else None
    new_style = _pipeline.render_style(style_name, user, ctx) if style_name else None

    if ctx.dry_run:
        if not ctx.quiet:
            print("DRY RUN — no files will be written.")
            print(f"  would refresh {path_str(str(claude_md_path), use_color)}")
            if new_voice:
                print(f"  would refresh {path_str(str(voice_path), use_color)}")
            if new_style:
                print(f"  would refresh {path_str(str(style_path), use_color)}")
        return 0

    # Migration-day .sourced.bak fallback before mutating.
    write_bak_sibling(claude_md_path)
    if new_voice and voice_path.exists():
        write_bak_sibling(voice_path)
    if new_style and style_path.exists():
        write_bak_sibling(style_path)

    write_atomic(claude_md_path, new_claude)
    if new_voice:
        write_atomic(voice_path, new_voice)
    if new_style:
        write_atomic(style_path, new_style)

    if not ctx.quiet:
        print(f"\n{bold('Updated.', use_color)} project={target}")
    return 0
