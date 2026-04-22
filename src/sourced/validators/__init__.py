"""Validators return list[Finding]; never raise."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Finding:
    rule: str
    location: str
    severity: Literal["error", "warning"]
    message: str
    fix_hint: str | None = None
    rule_url: str | None = None
