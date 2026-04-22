"""Shared install pipeline used by install, global_install, and new.

The reviewers' canary: if install.py and global_install.py 80%-copy-paste,
behavior diverges silently (one validates, the other doesn't; one logs, the
other doesn't). This module is the single source of truth.

Pipeline shape (per spec §5.3):

  1. config.load_user_name()                          → str
  2. read_template(subpath)                           → str
  2.5 validators.validate_template(template)          → list[Finding] (PRE-render)
  3. render(template, ctx)                            → str
  4. validators.validate_rendered(rendered)           → list[Finding] (POST-render)
  5. raise ValidationError on errors / on warnings under --strict
  6. dry-run: print diff, return
  7. write_atomic OR mirror_tree
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..context import Context
from ..config import load_user_name, save_user_name
from ..errors import ValidationError, ProjectError
from ..render import RenderContext, read_template, bundled_path, render, write_atomic
from ..mirror import mirror_tree
from ..validators import Finding
from ..validators import csl as csl_validator
from ..validators import iron_rules as iron_rules_validator
from ..validators import exemptions as exemptions_validator


CLAUDE_HOME = Path.home() / ".claude"


def ensure_user_name(ctx: Context) -> str:
    """Read user name from ~/.claude/sourced.config; prompt + save if missing."""
    name = load_user_name()
    if name:
        return name
    if ctx.quiet:
        # Can't prompt in quiet mode.
        raise ProjectError(
            "no user name set in ~/.claude/sourced.config; can't prompt under --quiet. "
            "Run `sourced global-install` interactively first."
        )
    print("First time setup — what's your name? (used in rendered templates)")
    name = input("Name: ").strip()
    if not name:
        raise ProjectError("no name provided.")
    save_user_name(name)
    return name


def install_global(ctx: Context, *, force: bool = False) -> dict:
    """Mirror bundled data into ~/.claude/. Returns counts dict for ui."""
    counts = {"mirrored": 0, "skipped_dirs": 0}

    # Subdirs that map directly:
    for subdir in ("agents", "citations", "skills", "filters"):
        with bundled_path(subdir) as src:
            dest = CLAUDE_HOME / subdir
            if ctx.dry_run:
                # count files for the summary
                file_count = sum(1 for _ in Path(src).rglob("*") if Path(_).is_file())
                counts["mirrored"] += file_count
            else:
                mirror_tree(Path(src), dest, dry_run=False)
                counts["mirrored"] += sum(1 for _ in dest.rglob("*") if _.is_file())

    # Brief templates to ~/.claude/templates/ (install.sh-parity: only the two
    # brief templates land here; voices and styles go to their canonical
    # ~/.claude/voice/ and ~/.claude/style/ locations below).
    templates_dest = CLAUDE_HOME / "templates"
    if not ctx.dry_run:
        templates_dest.mkdir(parents=True, exist_ok=True)
    for brief_name in ("brief.template.md", "brief.template.annotated-bib.md"):
        with bundled_path(f"templates/{brief_name}") as src:
            target = templates_dest / brief_name
            if ctx.dry_run:
                counts["mirrored"] += 1
            else:
                target.write_text(Path(src).read_text(encoding="utf-8"), encoding="utf-8")
                counts["mirrored"] += 1

    # Voice library: bundled templates/voices/*.md → ~/.claude/voice/<name>.md
    # Note: install.sh treats these as templates the per-project step substitutes
    # against; the library copy is unrendered.
    voice_dest = CLAUDE_HOME / "voice"
    style_dest = CLAUDE_HOME / "style"
    if not ctx.dry_run:
        voice_dest.mkdir(parents=True, exist_ok=True)
        style_dest.mkdir(parents=True, exist_ok=True)

    with bundled_path("templates/voices") as voices_src:
        for voice_file in Path(voices_src).glob("*.md"):
            target = voice_dest / voice_file.name
            if ctx.dry_run:
                counts["mirrored"] += 1
            else:
                target.write_text(voice_file.read_text(encoding="utf-8"), encoding="utf-8")
                counts["mirrored"] += 1

    with bundled_path("templates/styles") as styles_src:
        # Top-level style.md files
        for style_file in Path(styles_src).glob("*.md"):
            target = style_dest / style_file.name
            if ctx.dry_run:
                counts["mirrored"] += 1
            else:
                target.write_text(style_file.read_text(encoding="utf-8"), encoding="utf-8")
                counts["mirrored"] += 1
        # Per-style asset directories
        for style_assets in Path(styles_src).iterdir():
            if not style_assets.is_dir():
                continue
            asset_dest = style_dest / style_assets.name
            if ctx.dry_run:
                counts["mirrored"] += sum(1 for _ in style_assets.rglob("*") if _.is_file())
            else:
                mirror_tree(style_assets, asset_dest, dry_run=False)

    return counts


def render_voice(name: str, user: str, ctx: Context) -> str:
    """Render a voice library file into a per-project voice.md.

    Reads ~/.claude/voice/<name>.md (the library — already mirrored by global-install),
    validates the installed file against the bundled skeleton (same pattern as
    commands.check; falls back to self-check for user-derived voices that have no
    shipped skeleton), prepends the marker line, substitutes {{USER}}, returns the
    rendered text.
    """
    src = CLAUDE_HOME / "voice" / f"{name}.md"
    if not src.exists():
        raise ProjectError(
            f"voice '{name}' not installed at {src}. "
            f"Run `sourced global-install` first, or pass --voice <existing>."
        )
    skeleton_text = src.read_text(encoding="utf-8")

    # POST-render validation: read CLAUDE.md template for canonical ids.
    claude_md_template = read_template("templates/CLAUDE.md")

    # Validate the installed voice against the bundled skeleton; fall back to
    # self-check for user-derived voices with no shipped skeleton.
    try:
        bundled_skeleton = read_template(f"templates/voices/{name}.md")
    except FileNotFoundError:
        bundled_skeleton = skeleton_text

    rendered_body = render(skeleton_text, RenderContext(user=user))
    findings = []
    findings.extend(iron_rules_validator.validate(
        skeleton=bundled_skeleton, candidate=skeleton_text, voice_name=name,
    ))
    findings.extend(exemptions_validator.validate(
        voice=skeleton_text, claude_md=claude_md_template, voice_name=name,
    ))
    _maybe_raise(findings, ctx)

    return f"<!-- sourced:voice={name} -->\n\n{rendered_body}"


def render_style(name: str, user: str, ctx: Context) -> str:
    """Render a style library file into a per-project style.md."""
    src = CLAUDE_HOME / "style" / f"{name}.md"
    if not src.exists():
        raise ProjectError(
            f"style '{name}' not installed at {src}. "
            f"Run `sourced global-install` first, or pass --style <existing>."
        )
    style_text = src.read_text(encoding="utf-8")
    rendered_body = render(style_text, RenderContext(user=user))
    return f"<!-- sourced:style={name} -->\n\n{rendered_body}"


def render_claude_md(user: str, ctx: Context) -> str:
    """Render the per-project CLAUDE.md."""
    template = read_template("templates/CLAUDE.md")
    return render(template, RenderContext(user=user))


def render_brief(name: str, user: str, project_type: str, ctx: Context) -> str:
    """Render the brief template matching project_type."""
    if project_type == "annotated-bib":
        template = read_template("templates/brief.template.annotated-bib.md")
    else:
        template = read_template("templates/brief.template.md")
    return render(template, RenderContext(user=user))


def _maybe_raise(findings: list[Finding], ctx: Context) -> None:
    """Per spec §5.3 step 5: errors always raise; warnings raise only under --strict."""
    if not findings:
        return
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    if errors:
        raise ValidationError(
            f"{len(errors)} validation error(s)", findings=errors + warnings,
        )
    if warnings and ctx.strict:
        raise ValidationError(
            f"{len(warnings)} warning(s) promoted to error under --strict",
            findings=warnings,
        )
