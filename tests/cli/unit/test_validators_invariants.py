"""Unit tests for validators/invariants.py (I1, I3-I9; I2/I10 dormant)."""
import pytest

from sourced.validators import invariants as inv
from sourced.validators.invariants import (
    check_i1_mode_body_presence,
    check_i2_overlay_scope,
    check_i3_canonical_id_integrity,
    check_i4_manifest_syntax,
    check_i5_forcing_artifact_reachability,
    check_i6_user_addition_markers,
    check_i7_precedence_ordering,
    check_i8_mode_body_compliance,
    check_i9_size_limits,
    parse_registry,
    parse_gate_table,
    parse_forcing_artifacts,
    parse_precedence_rules,
    parse_canonical_ids,
    run_all_invariants,
    ALLOWED_OVERLAY_PATCH_SECTIONS,
)


MINIMAL_REGISTRY_BLOCK = """\
## 7. Modes (dispatch manifest)

### 7.1 Mode registry

| Mode | Body | Project types | Auto-enters from |
|------|------|---------------|-------------------|
| collaborative | inline (§7.7) | all | session start |
| research | `docs/modes/research.md` | all | §3 self-correction |

### 7.4 Mode-to-mode gates

| Transition | Gate condition | Forcing artifact |
|------------|----------------|-------------------|
| refining → writing | audit clean | §4 audit list |

### 7.5 Forcing artifacts

- **§4 audit list.** One row per citation audited.

### 7.6 Precedence and canonical §10 IDs

1. **Rule one.** body.
2. **Rule two.** body.

- `em-dashes` — em-dash pattern.
"""


# ----- parsing helpers -----

def test_parse_registry_extracts_rows():
    rows = parse_registry(MINIMAL_REGISTRY_BLOCK)
    assert len(rows) == 2
    assert rows[0]["Mode"] == "collaborative"
    assert rows[1]["Mode"] == "research"
    assert "docs/modes/research.md" in rows[1]["Body"]


def test_parse_gate_table_extracts_rows():
    gates = parse_gate_table(MINIMAL_REGISTRY_BLOCK)
    assert len(gates) == 1
    assert gates[0]["Transition"] == "refining → writing"
    assert gates[0]["Forcing artifact"] == "§4 audit list"


def test_parse_forcing_artifacts_extracts_names():
    artifacts = parse_forcing_artifacts(MINIMAL_REGISTRY_BLOCK)
    assert artifacts == ["§4 audit list"]


def test_parse_precedence_rules_preserves_order():
    rules = parse_precedence_rules(MINIMAL_REGISTRY_BLOCK)
    assert rules == [(1, "Rule one"), (2, "Rule two")]


def test_parse_canonical_ids_extracts_ids():
    ids = parse_canonical_ids(MINIMAL_REGISTRY_BLOCK)
    assert ids == ["em-dashes"]


# ----- I1 mode body presence -----

def test_i1_passes_on_shipped_bundle():
    findings = check_i1_mode_body_presence(inv._load_bundled_template())
    assert findings == []


def test_i1_fails_when_non_inline_body_missing():
    fake = MINIMAL_REGISTRY_BLOCK.replace(
        "`docs/modes/research.md`",
        "`docs/modes/nonexistent-mode.md`",
    )
    findings = check_i1_mode_body_presence(fake)
    assert len(findings) == 1
    assert findings[0].rule == "I1"
    assert "nonexistent-mode.md" in findings[0].message


def test_i1_tolerates_inline_body_marker():
    findings = check_i1_mode_body_presence(MINIMAL_REGISTRY_BLOCK)
    # `collaborative` is `inline` — no finding expected for it; only `research`
    # is non-inline and its body file does not exist in this synthetic fixture.
    assert all("collaborative" not in f.location for f in findings)


# ----- I2 overlay scope -----

def test_i2_passes_on_shipped_bundle():
    """Shipped annotated-bib overlay patches only base-manifest sections."""
    findings = check_i2_overlay_scope(inv._load_bundled_template())
    assert findings == []


def test_i2_fails_on_unknown_patch_section(tmp_path, monkeypatch):
    """An overlay that patches a section outside §§7.1-7.6 fails I2."""
    # Build a synthetic bundle with a malformed overlay.
    fake_claude_d = tmp_path / "CLAUDE.d"
    fake_claude_d.mkdir()
    (fake_claude_d / "README.md").write_text("drop-in pattern docs")
    (fake_claude_d / "99-malformed.md").write_text(
        "# Malformed overlay\n\n"
        "## Patches to §99 Nonexistent section\n\n"
        "- Remove: something\n"
    )

    # Point bundled_path at the fake bundle for "templates/CLAUDE.d".
    from contextlib import contextmanager
    @contextmanager
    def fake_bundled_path(subpath):
        if subpath == "templates/CLAUDE.d":
            yield fake_claude_d
        else:
            # Fall through to real implementation for other paths.
            from sourced.render import bundled_path as real
            with real(subpath) as p:
                yield p

    monkeypatch.setattr(inv, "bundled_path", fake_bundled_path)

    findings = check_i2_overlay_scope(inv._load_bundled_template())
    assert any("99 Nonexistent section" in f.message for f in findings)


def test_i2_dormant_when_no_overlays(tmp_path, monkeypatch):
    """I2 reports no findings when the bundle ships no overlays."""
    fake_empty = tmp_path / "CLAUDE.d"
    fake_empty.mkdir()

    from contextlib import contextmanager
    @contextmanager
    def fake_bundled_path(subpath):
        if subpath == "templates/CLAUDE.d":
            yield fake_empty
        else:
            from sourced.render import bundled_path as real
            with real(subpath) as p:
                yield p

    monkeypatch.setattr(inv, "bundled_path", fake_bundled_path)

    findings = check_i2_overlay_scope(inv._load_bundled_template())
    assert findings == []


def test_allowed_overlay_patch_sections_covers_76_range():
    """Sanity check the allowed-sections set matches spec §§7.1-7.6."""
    expected_prefixes = {"7.1", "7.2", "7.3", "7.4", "7.5", "7.6"}
    actual_prefixes = {s.split(" ")[0] for s in ALLOWED_OVERLAY_PATCH_SECTIONS}
    assert actual_prefixes == expected_prefixes


# ----- I3 canonical ID integrity (integration — uses real writing.md) -----

def test_i3_passes_on_shipped_bundle():
    findings = check_i3_canonical_id_integrity(inv._load_bundled_template())
    assert findings == []


# ----- I4 manifest syntactic validity -----

def test_i4_passes_on_shipped_bundle():
    findings = check_i4_manifest_syntax(inv._load_bundled_template())
    assert findings == []


def test_i4_fails_on_missing_registry_columns():
    broken = MINIMAL_REGISTRY_BLOCK.replace(
        "| Mode | Body | Project types | Auto-enters from |",
        "| Mode | Body | ProjTypes |",  # renamed columns
    ).replace(
        "|------|------|---------------|-------------------|",
        "|------|------|-----------|",
    ).replace(
        "| collaborative | inline (§7.7) | all | session start |",
        "| collaborative | inline (§7.7) | all |",
    ).replace(
        "| research | `docs/modes/research.md` | all | §3 self-correction |",
        "| research | `docs/modes/research.md` | all |",
    )
    findings = check_i4_manifest_syntax(broken)
    assert any("columns" in f.message for f in findings)


# ----- I5 forcing-artifact reachability -----

def test_i5_passes_on_shipped_bundle():
    findings = check_i5_forcing_artifact_reachability(inv._load_bundled_template())
    assert findings == []


def test_i5_fails_on_orphan_artifact():
    orphaned = MINIMAL_REGISTRY_BLOCK.replace(
        "- **§4 audit list.** One row per citation audited.",
        "- **Orphan artifact that matches nothing whatsoever.** body.",
    )
    findings = check_i5_forcing_artifact_reachability(orphaned)
    # Synthetic fixture has no real mode bodies to reach; expect the orphan to
    # fire unless root-level rules mention it (they don't).
    assert any("Orphan artifact" in f.message for f in findings)


# ----- I6 user-addition markers -----

def test_i6_passes_on_shipped_bundle():
    findings = check_i6_user_addition_markers(inv._load_bundled_template())
    assert findings == []


def test_i6_fails_on_unclosed_marker():
    broken = (
        MINIMAL_REGISTRY_BLOCK
        + "\n<!-- sourced:user-addition start -->\n(missing end)\n"
    )
    findings = check_i6_user_addition_markers(broken)
    assert len(findings) == 1
    assert "unclosed" in findings[0].message.lower()


# ----- I7 precedence ordering -----

def test_i7_passes_on_shipped_bundle():
    findings = check_i7_precedence_ordering(inv._load_bundled_template())
    assert findings == []


def test_i7_fails_on_duplicate_rank():
    broken = MINIMAL_REGISTRY_BLOCK.replace(
        "2. **Rule two.** body.",
        "1. **Rule two duplicate rank.** body.",
    )
    findings = check_i7_precedence_ordering(broken)
    assert any("duplicates" in f.message for f in findings)


def test_i7_fails_on_out_of_order_ranks():
    broken = MINIMAL_REGISTRY_BLOCK.replace(
        "1. **Rule one.** body.\n2. **Rule two.** body.",
        "2. **Rule two.** body.\n1. **Rule one.** body.",
    )
    findings = check_i7_precedence_ordering(broken)
    assert any("ascending" in f.message for f in findings)


# ----- I8 mode body template compliance -----

def test_i8_passes_on_shipped_bundle():
    findings = check_i8_mode_body_compliance(inv._load_bundled_template())
    assert findings == []


# ----- I9 size limits -----

def test_i9_passes_on_shipped_bundle():
    findings = check_i9_size_limits(inv._load_bundled_template())
    assert findings == []


def test_i9_fails_on_overlong_registry_row():
    long_auto_enters = " plus some extra text to push this past 150 characters without being useful"
    overlong = MINIMAL_REGISTRY_BLOCK.replace(
        "| research | `docs/modes/research.md` | all | §3 self-correction |",
        f"| research | `docs/modes/research.md` | all | §3 self-correction{long_auto_enters} |",
    )
    findings = check_i9_size_limits(overlong)
    assert any("registry row" in f.location and "research" in f.location for f in findings)


# ----- aggregator -----

def test_run_all_invariants_returns_tuples():
    results = run_all_invariants()
    rule_ids = [r for r, _ in results]
    # Commits 3 + 4 ship I1-I9. I10 is not yet in the shipped list.
    assert rule_ids == ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9"]
    # Every finding list is iterable.
    for _, findings in results:
        assert isinstance(findings, list)


def test_run_all_invariants_passes_on_shipped_bundle():
    """The shipped template + mode bodies must satisfy every invariant commit 3 covers."""
    results = run_all_invariants()
    for rule_id, findings in results:
        assert findings == [], (
            f"{rule_id} failed on shipped bundle: "
            + "; ".join(f"[{f.location}] {f.message}" for f in findings)
        )
