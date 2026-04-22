"""Typed exceptions for sourced. cli.main maps each subclass to an exit code."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .validators import Finding


class SourcedError(Exception):
    """Base; subclass to override exit_code."""
    exit_code: int = 1


class UsageError(SourcedError):
    """Bad flag combination or invocation. Matches argparse's native exit 2."""
    exit_code = 2


class PrereqError(SourcedError):
    """Missing tool on PATH (pdftotext/pandoc/etc.)."""
    exit_code = 3


class ValidationError(SourcedError):
    """Validator findings prevented orchestration. Carries the Finding list."""
    exit_code = 4

    def __init__(self, msg: str, findings: list["Finding"]) -> None:
        assert findings, "ValidationError requires at least one finding"
        super().__init__(msg)
        self.findings = findings


class ProjectError(SourcedError):
    """Project state broken: missing dir, corrupted marker, malformed sentinels."""
    exit_code = 5


class RenderError(SourcedError):
    """Malformed template; substitution failed."""
    exit_code = 6


class ExternalToolError(SourcedError):
    """External tool (pandoc/git/etc.) exited non-zero."""
    exit_code = 7


class ValidatorCrashError(SourcedError):
    """Validator itself crashed (a bug in the validator). EX_SOFTWARE."""
    exit_code = 70
