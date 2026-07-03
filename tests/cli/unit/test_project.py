import pytest
from sourced.project import (
    read_project_type, write_project_type,
    read_voice_marker, read_style_marker,
    extract_managed_block, replace_managed_block,
    write_bak_sibling,
    parse_user_additions, merge_managed_block, MIGRATED_ADDITIONS_HEADING,
    detect_phase1_layout, deploy_docs_tree, migrate_phase1_to_phase2,
    PHASE1_BAK_NAME,
    detect_phase3_layout, migrate_phase3_to_phase4,
)
from sourced.errors import ProjectError


# ----- project type marker -----

def test_project_type_default_when_marker_absent(tmp_project):
    assert read_project_type(tmp_project) == "essay"


def test_project_type_reads_marker(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_strips_whitespace_and_crlf(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("annotated-bib\r\n")
    assert read_project_type(tmp_project) == "annotated-bib"


def test_project_type_empty_marker_treated_as_essay(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("   \n")
    assert read_project_type(tmp_project) == "essay"


def test_write_project_type_essay_no_marker(tmp_project):
    """Essay default writes no marker (legacy-safe)."""
    write_project_type(tmp_project, "essay")
    assert not (tmp_project / ".sourced-project-type").exists()


def test_write_project_type_annotated_writes_marker(tmp_project):
    write_project_type(tmp_project, "annotated-bib")
    assert (tmp_project / ".sourced-project-type").read_text().strip() == "annotated-bib"


def test_project_type_unknown_value_raises(tmp_project):
    (tmp_project / ".sourced-project-type").write_text("unknown-type\n")
    with pytest.raises(ProjectError, match="unknown"):
        read_project_type(tmp_project)


# ----- voice / style markers -----

def test_read_voice_marker_finds_quoted_form(tmp_project):
    (tmp_project / "voice.md").write_text(
        "<!-- sourced:voice=academic -->\n# Voice rules\n"
    )
    assert read_voice_marker(tmp_project / "voice.md") == "academic"


def test_read_voice_marker_returns_none_when_missing(tmp_project):
    (tmp_project / "voice.md").write_text("# No marker\nplain content\n")
    assert read_voice_marker(tmp_project / "voice.md") is None


def test_read_style_marker_works_similarly(tmp_project):
    (tmp_project / "style.md").write_text("<!-- sourced:style=apa7 -->\n")
    assert read_style_marker(tmp_project / "style.md") == "apa7"


def test_read_voice_marker_ignores_body_match(tmp_project):
    """install.sh restricts to line 1; body mentions of the marker must NOT match."""
    (tmp_project / "voice.md").write_text(
        "# Voice rules\n"
        "this voice is more formal than\n"
        "<!-- sourced:voice=casual -->\n"
        "...even though casual is mentioned above.\n"
    )
    assert read_voice_marker(tmp_project / "voice.md") is None


def test_read_voice_marker_rejects_invalid_chars(tmp_project):
    """install.sh's regex restricts to [a-zA-Z0-9_-]; a name with spaces or
    special chars must NOT match."""
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=bad name -->\n")
    assert read_voice_marker(tmp_project / "voice.md") is None


# ----- managed-block sentinels (column-0 strict) -----

def test_extract_managed_block_finds_pair():
    text = (
        "before\n"
        "<!-- sourced:begin managed -->\n"
        "managed line 1\n"
        "managed line 2\n"
        "<!-- sourced:end managed -->\n"
        "after\n"
    )
    block = extract_managed_block(text)
    assert "managed line 1" in block
    assert "managed line 2" in block
    assert "before" not in block
    assert "after" not in block


def test_extract_managed_block_rejects_indented_sentinel():
    """The strict column-0 regex must not match an indented sentinel
    (legitimate prose documenting the sentinel system)."""
    text = (
        "  - <!-- sourced:begin managed -->\n"
        "managed?\n"
        "  - <!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError):
        extract_managed_block(text)


def test_extract_managed_block_rejects_missing_sentinels():
    with pytest.raises(ProjectError, match="begin"):
        extract_managed_block("no sentinels here\n")


def test_extract_managed_block_rejects_double_begin():
    text = (
        "<!-- sourced:begin managed -->\n"
        "first\n"
        "<!-- sourced:begin managed -->\n"
        "<!-- sourced:end managed -->\n"
    )
    with pytest.raises(ProjectError, match="multiple"):
        extract_managed_block(text)


def test_replace_managed_block_preserves_outside():
    original = (
        "USER PROSE BEFORE\n"
        "<!-- sourced:begin managed -->\n"
        "old managed\n"
        "<!-- sourced:end managed -->\n"
        "USER PROSE AFTER\n"
    )
    new_managed = "fresh managed content"
    out = replace_managed_block(original, new_managed)
    assert "USER PROSE BEFORE\n" in out
    assert "USER PROSE AFTER\n" in out
    assert "fresh managed content" in out
    assert "old managed" not in out


def test_replace_managed_block_with_empty_new_managed():
    """Replacing with empty content must not introduce spurious blank lines."""
    original = (
        "<!-- sourced:begin managed -->\n"
        "old content\n"
        "<!-- sourced:end managed -->\n"
    )
    out = replace_managed_block(original, "")
    assert out == (
        "<!-- sourced:begin managed -->\n"
        "<!-- sourced:end managed -->\n"
    )


def test_extract_managed_block_handles_empty():
    """An immediate begin->end with nothing between is a legal degenerate case."""
    text = "<!-- sourced:begin managed -->\n<!-- sourced:end managed -->\n"
    assert extract_managed_block(text) == ""


def test_replace_managed_block_raises_on_missing_sentinels():
    with pytest.raises(ProjectError, match="malformed"):
        replace_managed_block("no sentinels here\n", "x")


# ----- .sourced.bak rollback fallback -----

def test_write_bak_sibling_creates_bak(tmp_project):
    f = tmp_project / "CLAUDE.md"
    f.write_text("original")
    write_bak_sibling(f)
    assert (tmp_project / "CLAUDE.md.sourced.bak").read_text() == "original"


def test_write_bak_sibling_no_op_when_target_missing(tmp_project):
    f = tmp_project / "CLAUDE.md"
    write_bak_sibling(f)  # should not raise
    assert not (tmp_project / "CLAUDE.md.sourced.bak").exists()


# ----- user-addition region parsing (phase 2 spec §7) -----

def test_parse_user_additions_empty_when_no_markers():
    text = "## §1\nsome framework prose\n## §2\nmore prose\n"
    assert parse_user_additions(text) == []


def test_parse_user_additions_finds_single_region_under_section():
    text = (
        "## §7\n"
        "### 7.1 Mode registry\n"
        "| collaborative | inline | all | session start |\n"
        "\n"
        "<!-- sourced:user-addition start -->\n"
        "| debugging | docs/modes/debugging.md | all | explicit trigger |\n"
        "<!-- sourced:user-addition end -->\n"
    )
    regions = parse_user_additions(text)
    assert len(regions) == 1
    assert regions[0].section_heading == "§7"
    assert "debugging" in regions[0].content
    assert regions[0].content.startswith("<!-- sourced:user-addition start -->")
    assert regions[0].content.endswith("<!-- sourced:user-addition end -->")


def test_parse_user_additions_multiple_regions_across_sections():
    text = (
        "## §3\n"
        "<!-- sourced:user-addition start -->\n"
        "custom §3 note\n"
        "<!-- sourced:user-addition end -->\n"
        "## §10\n"
        "<!-- sourced:user-addition start -->\n"
        "custom §10 note\n"
        "<!-- sourced:user-addition end -->\n"
    )
    regions = parse_user_additions(text)
    assert len(regions) == 2
    assert regions[0].section_heading == "§3"
    assert "custom §3 note" in regions[0].content
    assert regions[1].section_heading == "§10"
    assert "custom §10 note" in regions[1].content


def test_parse_user_additions_region_before_any_section_has_none_heading():
    text = (
        "<!-- sourced:user-addition start -->\n"
        "preamble-level custom note\n"
        "<!-- sourced:user-addition end -->\n"
        "## §1\nframework prose\n"
    )
    regions = parse_user_additions(text)
    assert len(regions) == 1
    assert regions[0].section_heading is None


def test_parse_user_additions_rejects_unclosed_start():
    text = (
        "## §7\n"
        "<!-- sourced:user-addition start -->\n"
        "custom content\n"
        "(no end marker)\n"
    )
    with pytest.raises(ProjectError, match="unclosed"):
        parse_user_additions(text)


def test_parse_user_additions_rejects_orphan_end():
    text = (
        "## §7\n"
        "some prose\n"
        "<!-- sourced:user-addition end -->\n"
    )
    with pytest.raises(ProjectError, match="without a preceding"):
        parse_user_additions(text)


def test_parse_user_additions_rejects_nested_start():
    text = (
        "## §7\n"
        "<!-- sourced:user-addition start -->\n"
        "<!-- sourced:user-addition start -->\n"
        "<!-- sourced:user-addition end -->\n"
    )
    with pytest.raises(ProjectError, match="nested"):
        parse_user_additions(text)


def test_parse_user_additions_ignores_indented_markers():
    """Column-0 strict: indented markers (legitimate prose) must not be parsed as regions."""
    text = (
        "## §7\n"
        "documentation text: wrap hand-added sections in\n"
        "  <!-- sourced:user-addition start -->\n"
        "  ...custom content...\n"
        "  <!-- sourced:user-addition end -->\n"
        "markers to preserve them.\n"
    )
    assert parse_user_additions(text) == []


# ----- merge_managed_block -----

def test_merge_managed_block_preserves_region_under_matching_section():
    old_managed = (
        "## §1\nframework §1\n\n"
        "## §7\nframework §7\n"
        "<!-- sourced:user-addition start -->\n"
        "custom content\n"
        "<!-- sourced:user-addition end -->\n"
    )
    fresh_managed = (
        "## §1\nframework §1\n\n"
        "## §7\nframework §7\n"
    )
    merged, warnings = merge_managed_block(old_managed, fresh_managed)
    assert "custom content" in merged
    assert "<!-- sourced:user-addition start -->" in merged
    assert "<!-- sourced:user-addition end -->" in merged
    # Region placed under §7 section, not somewhere else.
    s7_idx = merged.index("## §7")
    # If there's a §8 or something after §7, custom content should land before it.
    assert merged.index("custom content") > s7_idx


def test_merge_managed_block_no_regions_returns_fresh_verbatim():
    old = "## §1\nold framework\n"
    fresh = "## §1\nfresh framework (changed)\n"
    merged, warnings = merge_managed_block(old, fresh)
    # Fresh wins.
    assert "fresh framework (changed)" in merged
    assert "old framework" not in merged
    # Drift warning fires because framework content differs.
    assert any("drifted" in w for w in warnings)


def test_merge_managed_block_identical_no_warnings():
    text = "## §1\nidentical framework\n"
    merged, warnings = merge_managed_block(text, text)
    assert merged == text
    assert warnings == []


def test_merge_managed_block_fresh_framework_wins_over_old():
    """Writer edited framework content directly (no user-addition wrapper);
    fresh wins and a warning is surfaced."""
    old = "## §1\nwriter edited this framework prose\n"
    fresh = "## §1\nfresh framework prose from template\n"
    merged, warnings = merge_managed_block(old, fresh)
    assert "fresh framework prose from template" in merged
    assert "writer edited this framework prose" not in merged
    assert len(warnings) >= 1
    assert any("drift" in w.lower() for w in warnings)


def test_merge_managed_block_orphaned_region_migrates_to_custom_section():
    """If fresh removed the section containing a user-addition, migrate region
    to a 'Custom additions (migrated)' section appended at end."""
    old = (
        "## §1\nframework\n"
        "## §99 Legacy\n"
        "<!-- sourced:user-addition start -->\n"
        "custom legacy note\n"
        "<!-- sourced:user-addition end -->\n"
    )
    fresh = "## §1\nframework\n"
    merged, warnings = merge_managed_block(old, fresh)
    assert MIGRATED_ADDITIONS_HEADING in merged
    assert "custom legacy note" in merged
    assert any("no matching" in w for w in warnings)


def test_merge_managed_block_malformed_markers_raises():
    old = "## §7\n<!-- sourced:user-addition start -->\nunclosed\n"
    fresh = "## §7\nfresh\n"
    with pytest.raises(ProjectError):
        merge_managed_block(old, fresh)


# ----- phase-1 → phase-2 migration -----

def test_detect_phase1_layout_true_when_docs_modes_missing(tmp_project, monkeypatch):
    """Requires bundled templates/docs/modes/ to exist. In development the
    repo ships it; test passes only when the bundle is present."""
    (tmp_project / "CLAUDE.md").write_text("monolithic")
    # docs/modes/ does NOT exist in tmp_project.
    assert (tmp_project / "docs" / "modes").exists() is False
    # detect_phase1 returns True iff bundled docs/modes/ is present.
    # In this repo's checkout it is; if the test is run on a minimal install
    # without the bundle, skip.
    from sourced.project import _bundled_docs_modes_present
    if not _bundled_docs_modes_present():
        pytest.skip("bundled templates/docs/modes/ not present in this install")
    assert detect_phase1_layout(tmp_project) is True


def test_detect_phase1_layout_false_when_claude_md_missing(tmp_project):
    """No CLAUDE.md → not a phase-1 project (or not a sourced project at all)."""
    assert detect_phase1_layout(tmp_project) is False


def test_detect_phase1_layout_false_when_docs_modes_already_present(tmp_project):
    (tmp_project / "CLAUDE.md").write_text("phase 2 layout")
    (tmp_project / "docs" / "modes").mkdir(parents=True)
    assert detect_phase1_layout(tmp_project) is False


def test_deploy_docs_tree_copies_bundled_files(tmp_project):
    from sourced.project import _bundled_docs_modes_present
    if not _bundled_docs_modes_present():
        pytest.skip("bundled templates/docs/modes/ not present")
    written = deploy_docs_tree(tmp_project)
    assert len(written) > 0
    # At least the canonical mode bodies should land.
    assert (tmp_project / "docs" / "modes" / "editing.md").exists()
    assert (tmp_project / "docs" / "modes" / "research.md").exists()


def test_migrate_phase1_to_phase2_renames_old_and_deploys(tmp_project):
    from sourced.project import _bundled_docs_modes_present
    if not _bundled_docs_modes_present():
        pytest.skip("bundled templates/docs/modes/ not present")
    old_content = "# Monolithic phase-1 CLAUDE.md\n...lots of content..."
    (tmp_project / "CLAUDE.md").write_text(old_content)
    fresh = "# Phase-2 manifest\n...new content..."
    notes = migrate_phase1_to_phase2(tmp_project, fresh)
    assert (tmp_project / PHASE1_BAK_NAME).read_text() == old_content
    assert (tmp_project / "CLAUDE.md").read_text() == fresh
    assert (tmp_project / "docs" / "modes").exists()
    assert any("migrated" in n for n in notes)
    assert any("docs/" in n for n in notes)


def test_migrate_phase1_preserves_existing_bak(tmp_project):
    """If .phase1.bak already exists (second run), don't clobber it."""
    from sourced.project import _bundled_docs_modes_present
    if not _bundled_docs_modes_present():
        pytest.skip("bundled templates/docs/modes/ not present")
    existing_bak = "first migration backup"
    (tmp_project / PHASE1_BAK_NAME).write_text(existing_bak)
    (tmp_project / "CLAUDE.md").write_text("current state")
    notes = migrate_phase1_to_phase2(tmp_project, "fresh")
    # Old bak untouched.
    assert (tmp_project / PHASE1_BAK_NAME).read_text() == existing_bak
    assert any("already exists" in n for n in notes)


# ----- phase-3 → phase-4 migration detection -----

def test_detect_phase3_layout_true_when_voice_at_root(tmp_project):
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    assert detect_phase3_layout(tmp_project) is True


def test_detect_phase3_layout_false_when_config_voice_exists(tmp_project):
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    (tmp_project / "config").mkdir()
    (tmp_project / "config" / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    assert detect_phase3_layout(tmp_project) is False


def test_detect_phase3_layout_false_when_no_voice(tmp_project):
    assert detect_phase3_layout(tmp_project) is False


def test_detect_phase3_layout_false_when_voice_lacks_marker(tmp_project):
    """F31: a root voice.md without the sourced:voice marker is hand-authored,
    not a phase-3 sourced project. detect must not announce migration for it."""
    (tmp_project / "voice.md").write_text("hand-authored notes, no sourced marker\n")
    assert detect_phase3_layout(tmp_project) is False


# ----- phase-3 → phase-4 migration: core file moves -----

def test_migrate_phase3_to_phase4_moves_core_files(tmp_project):
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\nrules\n")
    (tmp_project / "voice.md.sourced.bak").write_text("bak")
    (tmp_project / "style.md").write_text("<!-- sourced:style=apa7 -->\nrules\n")
    (tmp_project / "report.brief.md").write_text("brief")
    (tmp_project / "report.citations.json").write_text("[]")

    notes = migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "config" / "voice.md").read_text().startswith("<!-- sourced:voice=academic -->")
    assert (tmp_project / "config" / "voice.md.sourced.bak").read_text() == "bak"
    assert (tmp_project / "config" / "style.md").exists()
    assert (tmp_project / "config" / "report.brief.md").exists()
    assert (tmp_project / "sources" / "report.citations.json").exists()
    assert not (tmp_project / "voice.md").exists()
    assert not (tmp_project / "style.md").exists()
    assert len(notes) >= 4  # at least one note per moved file


# ----- phase-3 → phase-4 migration: unmarked-voice preservation -----

def test_migrate_phase3_preserves_unmarked_voice(tmp_project):
    (tmp_project / "voice.md").write_text("# Hand-authored voice, no marker\n")

    notes = migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "voice.md").exists()  # not moved
    assert not (tmp_project / "config" / "voice.md").exists()
    assert any("not moved" in n for n in notes)


def test_migrate_phase3_preserves_unmarked_style(tmp_project):
    (tmp_project / "style.md").write_text("# Hand-authored style, no marker\n")

    notes = migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "style.md").exists()  # not moved
    assert not (tmp_project / "config" / "style.md").exists()
    assert any("not moved" in n for n in notes)


def test_migrate_phase3_recovers_orphan_voice_bak(tmp_project):
    """Bak siblings move on re-run even if primary already migrated.

    Models the partial-crash scenario where step 1 renamed voice.md but
    crashed before moving voice.md.sourced.bak.
    """
    (tmp_project / "config").mkdir()
    (tmp_project / "config" / "voice.md").write_text("<!-- sourced:voice=academic -->\nrules\n")
    (tmp_project / "voice.md.sourced.bak").write_text("orphan bak")

    migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "config" / "voice.md.sourced.bak").read_text() == "orphan bak"
    assert not (tmp_project / "voice.md.sourced.bak").exists()


def test_migrate_phase3_handles_working_brief_collision(tmp_project):
    """If a root-level working.brief.md and a .claude/briefs/working.brief.md
    both exist, step 3 moves the root copy first; step 5 must NOT overwrite."""
    (tmp_project / "working.brief.md").write_text("from root")
    briefs = tmp_project / ".claude" / "briefs"
    briefs.mkdir(parents=True)
    (briefs / "working.brief.md").write_text("from .claude/briefs")

    notes = migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "config" / "working.brief.md").read_text() == "from root"
    # .claude/briefs/working.brief.md NOT moved (would have overwritten)
    assert (briefs / "working.brief.md").read_text() == "from .claude/briefs"
    assert any("NOT moved — resolve manually" in n for n in notes)


# ----- phase-3 → phase-4 migration: working-artifact migration -----

def test_migrate_phase3_moves_working_brief(tmp_project):
    briefs = tmp_project / ".claude" / "briefs"
    briefs.mkdir(parents=True)
    (briefs / "working.brief.md").write_text("working brief")

    migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "config" / "working.brief.md").read_text() == "working brief"
    assert not briefs.exists()  # empty dir removed


def test_migrate_phase3_moves_working_log_preserves_shards_dir(tmp_project):
    citations = tmp_project / ".claude" / "citations"
    citations.mkdir(parents=True)
    (citations / "working.citations.json").write_text("[]")
    (citations / "working.finder-a.json").write_text("[]")  # shard — stays

    migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "sources" / "working.citations.json").exists()
    assert citations.exists()  # NOT removed — shards live here
    assert (citations / "working.finder-a.json").exists()


# ----- phase-3 → phase-4 migration: idempotence -----

def test_migrate_phase3_idempotent(tmp_project):
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")

    notes_1 = migrate_phase3_to_phase4(tmp_project)
    notes_2 = migrate_phase3_to_phase4(tmp_project)  # re-run

    assert (tmp_project / "config" / "voice.md").exists()
    assert not (tmp_project / "voice.md").exists()
    # Second run is a no-op on source side; hint lines may repeat but files unchanged
    _ = notes_1, notes_2  # both runs succeed without raising


# ----- phase-3 → phase-4 migration: candidate-hint emission -----

def test_migrate_phase3_emits_candidate_hints(tmp_project):
    (tmp_project / "Smith2020.pdf").write_bytes(b"%PDF")
    (tmp_project / "my_writing").mkdir()
    (tmp_project / "failures_dir").mkdir()

    notes = migrate_phase3_to_phase4(tmp_project)

    assert any("candidate source file" in n for n in notes)
    assert any("my_writing" in n for n in notes)
    assert any("failures_dir" in n for n in notes)
