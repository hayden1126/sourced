"""argparse root + subcommand dispatch + top-level error→exit-code mapping.

This is the ONLY module that touches argparse. Subcommand modules (commands/*.py)
accept plain Python args, not argparse.Namespace.
"""
from __future__ import annotations
import argparse
import os
import sys
from typing import NoReturn

from . import __version__
from .context import Context
from .errors import SourcedError
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

    # check (PR 1 has the prereq-only version; PR 4 expands)
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
    if args.subcommand == "check":
        from .commands import check
        return check.run(ctx, project=args.project)
    # No subcommand → print help and exit 2 (argparse-style usage error).
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
