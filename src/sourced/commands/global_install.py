"""sourced global-install — populate ~/.claude/ with bundled data."""
from __future__ import annotations
import sys

from ..context import Context
from ..ui import bold, should_color
from . import _pipeline


def run(ctx: Context, *, force: bool = False) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    user = _pipeline.ensure_user_name(ctx)

    if not ctx.quiet:
        banner = "DRY RUN — no files will be written.\n" if ctx.dry_run else ""
        print(f"{banner}{bold('Mirroring bundled files to ~/.claude/...', use_color)}")

    counts = _pipeline.install_global(ctx, force=force)

    if not ctx.quiet:
        verb = "would mirror" if ctx.dry_run else "mirrored"
        print(f"\n{verb} {counts['mirrored']} files (user={user}).")
    return 0
