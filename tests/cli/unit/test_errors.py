import pytest
from sourced.errors import (
    SourcedError, UsageError, PrereqError, ValidationError,
    ProjectError, RenderError, ExternalToolError, ValidatorCrashError,
)
from sourced.validators import Finding


def test_base_exit_code():
    e = SourcedError("nope")
    assert e.exit_code == 1


def test_subclass_exit_codes():
    assert UsageError("x").exit_code == 2
    assert PrereqError("x").exit_code == 3
    assert ProjectError("x").exit_code == 5
    assert RenderError("x").exit_code == 6
    assert ExternalToolError("x").exit_code == 7
    assert ValidatorCrashError("x").exit_code == 70


def test_validation_error_requires_findings():
    finding = Finding(
        rule="some-rule",
        location="some/path:1",
        severity="error",
        message="something broke",
    )
    e = ValidationError("nope", findings=[finding])
    assert e.exit_code == 4
    assert e.findings == [finding]


def test_validation_error_rejects_empty_findings():
    with pytest.raises(AssertionError):
        ValidationError("nope", findings=[])
