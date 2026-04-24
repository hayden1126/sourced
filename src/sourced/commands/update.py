"""sourced update — refresh managed block of CLAUDE.md + voice.md + style.md.

Phase-2 upgrade: preserves `<!-- sourced:user-addition start/end -->` regions
inside the managed block, migrates phase-1 projects to the new layout, and
surfaces framework-drift warnings. `--force` remains the escape hatch.
"""
from __future__ import annotations
import sys
from pathlib import Path

from ..context import Context
from ..errors import ProjectError
from ..project import (
    extract_managed_block,
    replace_managed_block,
    merge_managed_block,
    detect_phase1_layout,
    migrate_phase1_to_phase2,
    deploy_docs_tree,
    deploy_overlays,
    read_project_type,
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

    # Phase-1 detection: monolithic CLAUDE.md with no docs/modes/ sibling.
    is_phase1 = detect_phase1_layout(target)

    warnings: list[str] = []
    migration_notes: list[str] = []

    if force:
        new_claude = _pipeline.render_claude_md(user, ctx)
    elif is_phase1:
        # Migration path: rename old CLAUDE.md to .phase1.bak, deploy fresh layout.
        # Skip merge — the monolithic managed block does not map onto the phase-2
        # section-header surface, so a structural diff would produce noise.
        new_claude = _pipeline.render_claude_md(user, ctx)
        # Migration happens post-write guard below (dry-run must not mutate).
    else:
        # Standard managed-block refresh with user-addition preservation.
        old_text = claude_md_path.read_text(encoding="utf-8")
        extract_managed_block(old_text)  # sentinel validation; raises if malformed

        fresh_full = _pipeline.render_claude_md(user, ctx)
        fresh_managed = extract_managed_block(fresh_full)
        old_managed = extract_managed_block(old_text)

        merged_managed, warnings = merge_managed_block(old_managed, fresh_managed)
        new_claude = replace_managed_block(old_text, merged_managed)

    # Voice / style refresh from currently-installed library.
    voice_path = target / "voice.md"
    style_path = target / "style.md"
    voice_name = read_voice_marker(voice_path)
    style_name = read_style_marker(style_path)
    new_voice = _pipeline.render_voice(voice_name, user, ctx) if voice_name else None
    new_style = _pipeline.render_style(style_name, user, ctx) if style_name else None

    if ctx.dry_run:
        if not ctx.quiet:
            print("DRY RUN — no files will be written.")
            if is_phase1:
                print(f"  would migrate phase-1 CLAUDE.md → CLAUDE.md.phase1.bak at {path_str(str(target), use_color)}")
                print(f"  would deploy docs/ tree under {path_str(str(target / 'docs'), use_color)}")
            print(f"  would refresh {path_str(str(claude_md_path), use_color)}")
            if new_voice:
                print(f"  would refresh {path_str(str(voice_path), use_color)}")
            if new_style:
                print(f"  would refresh {path_str(str(style_path), use_color)}")
            for w in warnings:
                print(f"  WARNING: {w}")
        return 0

    # Atomic-ish ordering: backups → writes → docs deploy.
    write_bak_sibling(claude_md_path)
    if new_voice and voice_path.exists():
        write_bak_sibling(voice_path)
    if new_style and style_path.exists():
        write_bak_sibling(style_path)

    if is_phase1 and not force:
        migration_notes = migrate_phase1_to_phase2(target, new_claude)
    else:
        write_atomic(claude_md_path, new_claude)
        # Keep docs/ in sync with the bundle on every update (idempotent).
        docs_written = deploy_docs_tree(target)
        if docs_written and not ctx.quiet:
            print(f"  refreshed {len(docs_written)} file(s) under {path_str(str(target / 'docs'), use_color)}")

    # Keep CLAUDE.d/ overlays in sync with the bundle (idempotent). Reads the
    # project-type marker to decide which overlay to deploy.
    project_type = read_project_type(target)
    overlays_written = deploy_overlays(target, project_type)
    if overlays_written and not ctx.quiet:
        print(f"  refreshed {len(overlays_written)} overlay(s) under {path_str(str(target / 'CLAUDE.d'), use_color)}")

    if new_voice:
        write_atomic(voice_path, new_voice)
    if new_style:
        write_atomic(style_path, new_style)

    if not ctx.quiet:
        for note in migration_notes:
            print(f"  {note}")
        for w in warnings:
            print(f"  WARNING: {w}")
        print(f"\n{bold('Updated.', use_color)} project={target}")
    return 0
