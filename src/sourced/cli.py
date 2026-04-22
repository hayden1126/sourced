"""argparse root + subcommand dispatch + top-level error→exit-code mapping.

This is the ONLY module that touches argparse. Subcommand modules accept
plain Python args, not argparse.Namespace.
"""
from __future__ import annotations
import argparse
import os
import sys
from typing import NoReturn

from . import __version__
from .context import Context
from .errors import SourcedError, UsageError
from .ui import print_error, print_unexpected, should_color


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sourced", description="sourced framework CLI")
    p.add_argument("--version", action="version", version=f"sourced {__version__}")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    p.add_argument("--no-color", action="store_const", const="never", dest="color")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--strict", action="store_true")

    sub = p.add_subparsers(dest="subcommand", metavar="<subcommand>")

    # install
    p_install = sub.add_parser("install", help="install per-project files in PWD or --project")
    p_install.add_argument("--project", help="target project directory (default: PWD)")
    p_install.add_argument("--voice", default="academic")
    p_install.add_argument("--style", default="apa7")
    p_install.add_argument("--type", dest="project_type",
                           choices=["essay", "annotated-bib"], default="essay")
    p_install.add_argument("--brief", help="also create <name>.brief.md")
    p_install.add_argument("--force", action="store_true")

    # global-install
    p_gi = sub.add_parser("global-install", help="install/refresh ~/.claude/ files")
    p_gi.add_argument("--force", action="store_true")

    # new
    p_new = sub.add_parser("new", help="create project dir + brief + install")
    p_new.add_argument("project_name", help="project directory to create")
    p_new.add_argument("--voice", default="academic")
    p_new.add_argument("--style", default="apa7")
    p_new.add_argument("--type", dest="project_type",
                       choices=["essay", "annotated-bib"], default="essay")
    p_new.add_argument("--brief", help="brief filename (default: <project_name>)")
    p_new.add_argument("--force", action="store_true")

    # update
    p_update = sub.add_parser("update", help="refresh managed block of CLAUDE.md")
    p_update.add_argument("--project", help="target project directory (default: PWD)")
    p_update.add_argument("--force", action="store_true")

    # switch
    p_switch = sub.add_parser("switch", help="swap voice or style on existing project")
    switch_sub = p_switch.add_subparsers(dest="switch_kind", metavar="<voice|style>", required=True)
    p_sv = switch_sub.add_parser("voice", help="swap voice")
    p_sv.add_argument("name", help="library voice name")
    p_sv.add_argument("--project", help="target project directory (default: PWD)")
    p_ss = switch_sub.add_parser("style", help="swap style")
    p_ss.add_argument("name", help="library style name")
    p_ss.add_argument("--project", help="target project directory (default: PWD)")

    # check
    p_check = sub.add_parser("check", help="diagnose prereqs + ~/.claude/ health")
    p_check.add_argument("--project", help="also check this project directory")

    return p


def _ctx_from_args(args: argparse.Namespace) -> Context:
    return Context(
        dry_run=args.dry_run,
        verbose=args.verbose,
        quiet=args.quiet,
        color=args.color,
        strict=args.strict,
    )


def _dispatch(args: argparse.Namespace) -> int:
    ctx = _ctx_from_args(args)
    sub = args.subcommand

    if sub == "install":
        from .commands import install
        return install.run(
            ctx, project=args.project, voice=args.voice, style=args.style,
            project_type=args.project_type, brief=args.brief, force=args.force,
        )
    if sub == "global-install":
        from .commands import global_install
        return global_install.run(ctx, force=args.force)
    if sub == "new":
        from .commands import new
        return new.run(
            ctx, project_name=args.project_name, voice=args.voice, style=args.style,
            project_type=args.project_type, brief=args.brief, force=args.force,
        )
    if sub == "update":
        from .commands import update
        return update.run(ctx, project=args.project, force=args.force)
    if sub == "switch":
        from .commands import switch
        return switch.run(ctx, kind=args.switch_kind, name=args.name, project=args.project)
    if sub == "check":
        from .commands import check
        return check.run(ctx, project=args.project)

    # No subcommand → print help, exit 2.
    _build_parser().print_help(sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> NoReturn:
    parser = _build_parser()
    args = parser.parse_args(argv)
    use_color = should_color(args.color, sys.stderr)

    try:
        sys.exit(_dispatch(args))
    except SourcedError as e:
        print_error(e, use_color)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        debug = os.environ.get("SOURCED_DEBUG") or args.verbose >= 2
        if debug:
            raise
        print_unexpected(e)
        sys.exit(70)
