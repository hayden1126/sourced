"""Output formatting: color, error printing, summaries.
Single source of truth for ANSI codes; nothing else touches them.
"""
from __future__ import annotations
import os
import sys
from typing import IO, Literal

# 8 standard ANSI colors. No 256-color, no truecolor.
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def should_color(color_pref: Literal["auto", "always", "never"], stream: IO) -> bool:
    """Decide whether to emit ANSI codes to a stream.

    Precedence: --color=always > NO_COLOR env > --color=never > auto (on if stream is a TTY, else off).
    """
    if color_pref == "always":
        return True
    if os.environ.get("NO_COLOR"):
        return False
    if color_pref == "never":
        return False
    return stream.isatty()


def _wrap(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def ok(text: str, use_color: bool = True) -> str:
    return _wrap(text, _GREEN, use_color)


def warn(text: str, use_color: bool = True) -> str:
    return _wrap(text, _YELLOW, use_color)


def err(text: str, use_color: bool = True) -> str:
    return _wrap(text, _RED, use_color)


def path_str(text: str, use_color: bool = True) -> str:
    return _wrap(text, _CYAN, use_color)


def bold(text: str, use_color: bool = True) -> str:
    return _wrap(text, _BOLD, use_color)


def print_error(exc, use_color: bool, stream: IO = sys.stderr) -> None:
    """Print a SourcedError as the canonical two-line stderr format.
    For ValidationError, inline the findings list.
    """
    from .errors import ValidationError
    msg = str(exc)
    print(f"sourced: {err(msg, use_color)}", file=stream)
    if isinstance(exc, ValidationError):
        for f in exc.findings:
            sev = err(f.severity, use_color) if f.severity == "error" else warn(f.severity, use_color)
            print(f"  [{sev}] {f.rule} at {path_str(f.location, use_color)}: {f.message}", file=stream)
            if f.fix_hint:
                print(f"    hint: {f.fix_hint}", file=stream)


def print_unexpected(exc, stream: IO = sys.stderr) -> None:
    """Pip-style graceful catch-all for unhandled exceptions."""
    name = type(exc).__name__
    print(
        f"sourced: unexpected error ({name}: {exc}). "
        "Rerun with -vv or set SOURCED_DEBUG=1 to see the traceback.",
        file=stream,
    )
