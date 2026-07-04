"""argparse root + subcommand dispatch + top-level error→exit-code mapping.

This is the ONLY module that touches argparse. Subcommand modules accept
plain Python args, not argparse.Namespace.
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from . import __version__
from .context import Context
from .errors import SourcedError
from .ui import print_error, print_unexpected, should_color


def _git_checkout_state() -> str | None:
    """Live git state when running from an editable install inside the checkout.

    Returns raw ``git describe --tags --always --dirty`` output (today a bare
    short SHA; ``-dirty`` when the tree has uncommitted changes), or None when
    this is not a src-layout checkout or git is unavailable. None means the
    caller shows only the frozen install-time metadata, same as before #61.
    """
    pkg = Path(__file__).resolve().parent
    if pkg.parent.name != "src":  # wheel / site-packages install
        return None
    root = pkg.parent.parent
    if not (root / ".git").exists():  # .git is a file in worktrees
        return None
    if shutil.which("git") is None:
        return None
    try:
        out = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            capture_output=True, text=True, check=True, timeout=5, cwd=root,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    return out or None


def _version_string() -> str:
    state = _git_checkout_state()
    if state is None:
        return f"sourced {__version__}"
    return f"sourced {__version__} (checkout {state})"


class _LazyVersionAction(argparse.Action):
    """Like action="version", but the string is computed only when invoked.

    Keeps the git subprocess off the hot path: normal subcommands never pay
    for it, and a broken git can never break them.
    """

    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:
        kwargs.setdefault("help", "show program's version number and exit")
        super().__init__(
            option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        print(_version_string())
        parser.exit()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sourced", description="sourced framework CLI")
    p.add_argument("--version", action=_LazyVersionAction)
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
    p_check.add_argument(
        "--invariants",
        action="store_true",
        help="run structural invariants I1-I11 against the bundled template + shipped mode bodies",
    )

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
        return check.run(ctx, project=args.project, invariants=args.invariants)

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
        debug_env = os.environ.get("SOURCED_DEBUG", "").lower()
        debug = debug_env not in ("", "0", "false", "no") or args.verbose >= 2
        if debug:
            raise
        print_unexpected(e)
        sys.exit(70)
