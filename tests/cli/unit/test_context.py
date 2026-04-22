from sourced.context import Context


def test_default_context():
    ctx = Context()
    assert ctx.dry_run is False
    assert ctx.verbose == 0
    assert ctx.quiet is False
    assert ctx.color == "auto"
    assert ctx.strict is False


def test_context_is_frozen():
    import dataclasses
    ctx = Context()
    try:
        ctx.dry_run = True
    except dataclasses.FrozenInstanceError:
        return
    raise AssertionError("Context should be frozen")


def test_context_explicit_values():
    ctx = Context(dry_run=True, verbose=2, quiet=False, color="never", strict=True)
    assert ctx.dry_run is True
    assert ctx.verbose == 2
    assert ctx.color == "never"
    assert ctx.strict is True
