"""sourced install — render per-project files."""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import UsageError, ProjectError
from ..project import write_project_type, write_bak_sibling, deploy_docs_tree
from ..render import write_atomic
from ..ui import bold, path_str, should_color
from . import _pipeline


def run(
    ctx: Context,
    *,
    project: str | None = None,
    voice: str = "academic",
    style: str = "apa7",
    project_type: str = "essay",
    brief: str | None = None,
    force: bool = False,
) -> int:
    use_color = should_color(ctx.color, sys.stdout)
    target = Path(project).resolve() if project else Path.cwd()
    if not target.exists():
        raise ProjectError(f"target directory does not exist: {target}")

    user = _pipeline.ensure_user_name(ctx)

    # Render all texts up front (validators run; raises ValidationError on failure
    # BEFORE any write happens — atomicity at the orchestration layer).
    claude_md = _pipeline.render_claude_md(user, ctx)
    voice_md = _pipeline.render_voice(voice, user, ctx)
    style_md = _pipeline.render_style(style, user, ctx)
    brief_md = _pipeline.render_brief(brief, user, project_type, ctx) if brief else None

    targets: list[tuple[Path, str]] = [
        (target / "CLAUDE.md", claude_md),
        (target / "voice.md", voice_md),
        (target / "style.md", style_md),
    ]
    if brief:
        targets.append((target / f"{brief}.brief.md", brief_md))

    # Existence check (unless --force)
    existing = [p for p, _ in targets if p.exists()]
    if existing and not force:
        names = ", ".join(p.name for p in existing)
        raise UsageError(
            f"refusing to overwrite existing files: {names}. "
            f"Pass --force to overwrite, or `sourced update` to refresh the managed block."
        )

    if ctx.dry_run:
        if not ctx.quiet:
            print("DRY RUN — no files will be written.")
            for p, _ in targets:
                action = "would overwrite" if p.exists() else "would write"
                print(f"  {action} {path_str(str(p), use_color)}")
        return 0

    # Migration-day .sourced.bak fallback for any existing file.
    for p, _ in targets:
        if p.exists():
            write_bak_sibling(p)

    for p, content in targets:
        write_atomic(p, content)
        if not ctx.quiet:
            print(f"  wrote {path_str(str(p), use_color)}")

    # Deploy bundled docs/ tree (mode bodies + subagent docs).
    # No-op if the bundle carries no docs/ (pre-phase-2 bundle).
    docs_written = deploy_docs_tree(target)
    if docs_written and not ctx.quiet:
        print(f"  deployed {len(docs_written)} file(s) under {path_str(str(target / 'docs'), use_color)}")

    # Project-type marker.
    write_project_type(target, project_type)
    if not ctx.quiet:
        print(f"\n{bold('Done.', use_color)} project={target}, voice={voice}, style={style}, type={project_type}")
    return 0
