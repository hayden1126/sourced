"""Context dataclass — flows from cli.py to commands. NOT module globals."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Context:
    """Runtime context resolved from CLI flags + env. Pass explicitly to commands."""
    dry_run: bool = False
    verbose: int = 0           # action='count': 0 = default, 1 = -v, 2+ = -vv
    quiet: bool = False
    color: Literal["auto", "always", "never"] = "auto"
    strict: bool = False
