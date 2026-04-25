# Per-project directory restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Group project files into `config/`, `sources/`, `samples/`, `failures/` subdirectories with auto-migration on `sourced update`, eliminating top-level clutter as writers accumulate drafts and source material.

**Architecture:** Template bodies are rewritten to reference subdir-prefixed paths. `project.py` gains phase-3→phase-4 detect + migrate primitives mirroring the phase-1→phase-2 precedent. `commands/update.py` wires migration in. `commands/install.py` + `commands/new.py` scaffold directly to subdir paths. A new invariant I11 scans bundled templates for flat-path regressions.

**Tech Stack:** Python 3.11+, pytest, syrupy (snapshot testing), pathlib, re/regex.

**Spec:** `docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md`. All task decisions cross-reference spec sections (D1–D8, §§3–13).

**Branch:** `phase4-directory-restructure` (already off `origin/main` at 24e9845, spec commit 26e5f5c).

**Checkpoint:** After Task 5 (I11 invariant shipped), pause for a `/audit` pass on the branch before proceeding to integration tests. See "Checkpoint: audit" step in Task 5.

---

## Task 1: Rewrite flat-path references in shipped templates

**Files:**
- Modify: `src/sourced/data/templates/CLAUDE.md`
- Modify: `src/sourced/data/templates/docs/modes/plan.md`
- Modify: `src/sourced/data/templates/docs/modes/outlining.md`
- Modify: `src/sourced/data/templates/docs/modes/refining.md`
- Modify: `src/sourced/data/templates/docs/modes/writing.md`
- Modify: `src/sourced/data/templates/docs/modes/editing.md`
- Modify: `src/sourced/data/templates/docs/modes/formatting.md`
- Modify: `src/sourced/data/templates/docs/modes/annotated-bib.md`
- Modify: `src/sourced/data/templates/docs/voice-extractor.md`
- Modify: `src/sourced/data/templates/brief.template.annotated-bib.md`
- Modify: `src/sourced/data/agents/sourced-helper.md`
- Modify: `src/sourced/data/agents/voice-extractor.md`
- Modify: `src/sourced/data/agents/prose-drafter.md`
- Modify: `src/sourced/data/citations/schema.md`
- Modify: `tests/cli/golden/__snapshots__/test_render_golden.ambr` (via `--snapshot-update`)

### Rewrite patterns (applied in every file)

Per spec §6.1. Only rewrite paths; do not rewrite marker-line self-references or file-tree ASCII diagrams.

- `` `voice.md` `` → `` `config/voice.md` ``
- `` `style.md` `` → `` `config/style.md` ``
- `` `<draft>.citations.json` `` → `` `sources/<draft>.citations.json` ``
- `` `<draft-filename>.citations.json` `` → `` `sources/<draft-filename>.citations.json` ``
- `` `<draft>.brief.md` `` → `` `config/<draft>.brief.md` ``
- `` `<draft-name>.brief.md` `` → `` `config/<draft-name>.brief.md` ``
- `` `<name>.brief.md` `` → `` `config/<name>.brief.md` ``
- `` `.claude/briefs/working.brief.md` `` → `` `config/working.brief.md` ``
- `` `.claude/citations/working.citations.json` `` → `` `sources/working.citations.json` ``

**Do NOT rewrite:**
- Marker lines: `<!-- sourced:voice=<name> -->`, `<!-- sourced:style=<name> -->`
- `.claude/citations/working.<finder-id>.json` — dispatch-shard infra, unchanged (spec D3)
- `~/.claude/voice/<name>.md`, `~/.claude/style/<name>/<csl>.csl` — library paths, unchanged
- File-tree ASCII diagrams in `agents/sourced-helper.md` (leading `├──`/`│`/`└──` chars) — those are documentation of the rendered layout, rewrite them to show the new layout rather than swapping ref strings

- [ ] **Step 1.1: Rewrite `templates/CLAUDE.md`**

Refs live in §6 (brief paths ~L158–L171), §8 (citation log paths ~L359), §9 (voice.md pointer ~L382), §11 (style.md pointer ~L406–L412). 13 flat-path refs total. Apply patterns above. Also update §9's `voice-extractor` file reference from `~/.claude/voice/<voice_name>.md` (this is a library path, stays unchanged).

- [ ] **Step 1.2: Rewrite `templates/docs/modes/plan.md`**

One ref at L22 (`<draft-name>.brief.md`). Wrap in `config/`.

- [ ] **Step 1.3: Rewrite `templates/docs/modes/outlining.md`**

9 refs: L11, L32, L34, L43, L65, L76, L84, L94, L126. Patterns: `voice.md` → `config/voice.md`; `<draft>.citations.json` → `sources/<draft>.citations.json`; `.claude/citations/working.citations.json` → `sources/working.citations.json`.

- [ ] **Step 1.4: Rewrite `templates/docs/modes/refining.md`**

3 refs: L114, L176 (both `voice.md` → `config/voice.md`); L41 (`<draft>.citations.json` + `.claude/citations/working.citations.json`).

- [ ] **Step 1.5: Rewrite `templates/docs/modes/writing.md`**

~32 refs — largest file. Lines to check (phase-3 shipped these): L19, L37, L46, L50, L52, L69, L109, L111, L113, L115, L117, L136, L139, L142, L145, L198, L209 (and any others matching patterns). `voice.md` → `config/voice.md`; `<draft>.citations.json` → `sources/<draft>.citations.json`.

- [ ] **Step 1.6: Rewrite `templates/docs/modes/editing.md`**

~20 refs. Same patterns. Pay attention to L44 (citation log load path) and L62 (brief path).

- [ ] **Step 1.7: Rewrite `templates/docs/modes/formatting.md`**

~19 refs. Pattern: `style.md` → `config/style.md`; `<draft>.citations.json` → `sources/<draft>.citations.json`. Lines L15–L16, L27, L39, L41, L63, L99, L108, L139, L160, L177, L188, L191, L197, L205, L253, L256–L258.

- [ ] **Step 1.8: Rewrite `templates/docs/modes/annotated-bib.md`**

9 refs. L16 (voice.md + style.md + `<name>.brief.md`), L35, L37, L39, L41 (citation log), L59, L108, L133, L145. Apply patterns.

- [ ] **Step 1.9: Rewrite `templates/docs/voice-extractor.md` + add `omit` default**

Three jobs:

1. Update the "When to read this file" preamble's refs (L80–L81).
2. In the **Dispatch procedure** block (L9–L17), change:
   - `samples_dir: <absolute path to a directory containing the writing samples>` → `samples_dir: <absolute path to a directory containing the writing samples, or "omit" to default to <project>/samples/>`
   - `failures_dir: <absolute path to a directory of AI-vs-edit pairs, or "omit">` → `failures_dir: <absolute path to a directory of AI-vs-edit pairs, or "omit" to default to <project>/failures/ if non-empty>`
3. Add a paragraph after the dispatch block explaining that `omit` on `samples_dir` / `failures_dir` is resolved by the dispatcher to the project-root default before the subagent sees it. Cite spec §7.

- [ ] **Step 1.10: Rewrite `templates/brief.template.annotated-bib.md`**

One ref at L46 (`voice.md`). Wrap in `config/`.

- [ ] **Step 1.11: Rewrite `data/agents/sourced-helper.md` (file-tree diagram + prose)**

Two zones of work:

1. The file-tree diagram (around L38–L45 in current shipped copy): rewrite to the phase-4 layout (`config/voice.md`, `config/style.md`, `sources/<draft>.citations.json`, plus new `sources/`, `samples/`, `failures/` entries). Use the diagram from spec §3.
2. The command table (L23, L25, L26): update descriptions that mention where `voice.md`/`style.md`/`<brief>.brief.md` land.
3. §2 allowed-verbs section (L86): update "Edit `CLAUDE.md`, `voice.md`, ..." → "Edit `CLAUDE.md`, `config/voice.md`, ..."

- [ ] **Step 1.12: Rewrite `data/agents/voice-extractor.md` (semantic update)**

No path rewrites (the agent writes to `~/.claude/voice/<name>.md`, a library path). Add one paragraph to `## Inputs` §`samples_dir` clarifying: "The dispatcher may pass the absolute path of `<project>/samples/` when `samples_dir: omit` appears in the dispatch template; from the subagent's perspective this is just an absolute path." Same for `failures_dir`.

- [ ] **Step 1.13: Rewrite `data/agents/prose-drafter.md`**

Two mentions of `voice.md` (L31–L34 and L197). These are inside documentation describing what the subagent's inlined-payload comes from (`voice_rules`, `worked_paragraphs`, `cut_patterns` are extracted from `voice.md`). Rewrite the mentions from `voice.md` → `config/voice.md` so the documentation reflects where the parent reads from. The subagent receives content inlined, not a path — no behavioral change.

- [ ] **Step 1.14: Rewrite `data/citations/schema.md`**

Two refs (L3, L175): `<draft>.citations.json` → `sources/<draft>.citations.json`; `.claude/citations/working.citations.json` → `sources/working.citations.json`. Preserve `.claude/citations/` mentions that specifically discuss shard infrastructure (line 175 mentions both; keep the shard-infra phrasing, rewrite only the main-log phrasing).

- [ ] **Step 1.15: Run the test suite to surface regressions**

Run: `cd /home/hayden/sourced && pytest tests/cli/unit/ -x`
Expected: some golden snapshot tests may diff (path strings changed). Unit tests should still pass because they test structural parsing, not rendered path text.

- [ ] **Step 1.16: Regenerate golden snapshots**

Run: `cd /home/hayden/sourced && pytest tests/cli/golden/ --snapshot-update`

Inspect `tests/cli/golden/__snapshots__/test_render_golden.ambr` diff — every change should be a path-string swap (`voice.md` → `config/voice.md`, etc.), nothing structural. If any non-path-string changes show up, debug before committing.

- [ ] **Step 1.17: Run the full test suite once more**

Run: `cd /home/hayden/sourced && pytest tests/`
Expected: all green.

- [ ] **Step 1.18: Run the existing invariants check**

Run: `cd /home/hayden/sourced && python -m sourced check --invariants`
Expected: I1–I10 all pass. This confirms the manifest structure wasn't damaged by rewrites.

- [ ] **Step 1.19: Commit**

```bash
git add src/sourced/data/templates/ src/sourced/data/agents/ src/sourced/data/citations/schema.md tests/cli/golden/__snapshots__/
git commit -m "$(cat <<'EOF'
feat(templates): route mode/agent refs through config/ + sources/ subdir paths

Phase-4 template rewrites. Every flat-path reference (voice.md, style.md,
<draft>.citations.json, <draft>.brief.md) in shipped templates + agents
now carries the config/ or sources/ prefix. Dispatch-shard paths
(.claude/citations/working.<finder-id>.json) and library paths
(~/.claude/voice/<name>.md) unchanged.

Also adds voice-extractor dispatch default: samples_dir: omit resolves to
<project>/samples/, failures_dir: omit resolves to <project>/failures/ if
non-empty (spec §7, D5).

Golden snapshot regenerated; I1-I10 green.
EOF
)"
```

---

## Task 2: Migration primitives in `project.py` (TDD)

**Files:**
- Modify: `src/sourced/project.py` — add `detect_phase3_layout`, `migrate_phase3_to_phase4`
- Modify: `tests/cli/unit/test_project.py` — add fixtures + tests

### Implementation reference

Spec §4.1–4.3. Functions live alongside existing `detect_phase1_layout` / `migrate_phase1_to_phase2` (naming mirror).

```python
# project.py additions

def detect_phase3_layout(root: Path) -> bool:
    """Phase-3 layout: voice.md at root + no config/voice.md."""
    return (root / "voice.md").exists() and not (root / "config" / "voice.md").exists()


def migrate_phase3_to_phase4(root: Path) -> list[str]:
    """Move flat-layout files into phase-4 subdirs. Returns migration notes.

    Each move is an atomic rename (same filesystem). Idempotent on re-run:
    every step gates on source existence.
    """
    notes: list[str] = []
    config = root / "config"
    sources = root / "sources"
    samples = root / "samples"
    failures = root / "failures"
    for d in (config, sources, samples, failures):
        d.mkdir(exist_ok=True)

    # (1) voice.md (marker-gated) + bak siblings
    v = root / "voice.md"
    if v.exists() and read_voice_marker(v) is not None:
        v.rename(config / "voice.md")
        notes.append("moved voice.md → config/voice.md")
        for bak_name in ("voice.md.sourced.bak", "voice.md.phase1.bak"):
            bak = root / bak_name
            if bak.exists():
                bak.rename(config / bak_name)
    elif v.exists():
        notes.append("voice.md at root lacks sourced:voice= marker; not moved (hand-authored?)")

    # (2) style.md (marker-gated) + bak siblings
    s = root / "style.md"
    if s.exists() and read_style_marker(s) is not None:
        s.rename(config / "style.md")
        notes.append("moved style.md → config/style.md")
        for bak_name in ("style.md.sourced.bak",):
            bak = root / bak_name
            if bak.exists():
                bak.rename(config / bak_name)
    elif s.exists():
        notes.append("style.md at root lacks sourced:style= marker; not moved (hand-authored?)")

    # (3) *.brief.md at root → config/
    for brief in sorted(root.glob("*.brief.md")):
        brief.rename(config / brief.name)
        notes.append(f"moved {brief.name} → config/{brief.name}")

    # (4) *.citations.json at root → sources/
    for log in sorted(root.glob("*.citations.json")):
        log.rename(sources / log.name)
        notes.append(f"moved {log.name} → sources/{log.name}")

    # (5) .claude/briefs/working.brief.md → config/working.brief.md
    briefs_dir = root / ".claude" / "briefs"
    wb = briefs_dir / "working.brief.md"
    if wb.exists():
        wb.rename(config / "working.brief.md")
        notes.append("moved .claude/briefs/working.brief.md → config/working.brief.md")
    if briefs_dir.exists() and not any(briefs_dir.iterdir()):
        briefs_dir.rmdir()

    # (6) .claude/citations/working.citations.json → sources/working.citations.json
    wl = root / ".claude" / "citations" / "working.citations.json"
    if wl.exists():
        wl.rename(sources / "working.citations.json")
        notes.append("moved .claude/citations/working.citations.json → sources/working.citations.json")
    # Do NOT remove .claude/citations/ — shards live there.

    # (7) Hint lines (not moves)
    pdfs = sorted(root.glob("*.pdf"))
    txts = sorted(root.glob("*.txt"))
    candidates = [p.name for p in pdfs + txts if "bak" not in p.name]
    if candidates:
        notes.append(
            f"Found {len(candidates)} candidate source file(s) at root "
            f"({', '.join(candidates[:5])}{'…' if len(candidates) > 5 else ''}). "
            f"Move into sources/ if these back citations."
        )
    if (root / "my_writing").is_dir():
        notes.append("Directory my_writing/ detected; voice-extractor now defaults samples_dir to samples/.")
    if (root / "failures_dir").is_dir():
        notes.append("Directory failures_dir/ detected; voice-extractor now defaults failures_dir to failures/.")

    return notes
```

- [ ] **Step 2.1: Write the failing tests for `detect_phase3_layout`**

Add to `tests/cli/unit/test_project.py`:

```python
# --- phase-3 → phase-4 migration detection ---

def test_detect_phase3_layout_true_when_voice_at_root(tmp_project):
    from sourced.project import detect_phase3_layout
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    assert detect_phase3_layout(tmp_project) is True


def test_detect_phase3_layout_false_when_config_voice_exists(tmp_project):
    from sourced.project import detect_phase3_layout
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    (tmp_project / "config").mkdir()
    (tmp_project / "config" / "voice.md").write_text("<!-- sourced:voice=academic -->\n")
    assert detect_phase3_layout(tmp_project) is False


def test_detect_phase3_layout_false_when_no_voice(tmp_project):
    from sourced.project import detect_phase3_layout
    assert detect_phase3_layout(tmp_project) is False
```

- [ ] **Step 2.2: Run tests, expect ImportError**

Run: `pytest tests/cli/unit/test_project.py -k detect_phase3 -v`
Expected: FAIL with `ImportError: cannot import name 'detect_phase3_layout'`.

- [ ] **Step 2.3: Implement `detect_phase3_layout`**

Add near `detect_phase1_layout` in `src/sourced/project.py`:

```python
def detect_phase3_layout(root: Path) -> bool:
    """Phase-3 layout: voice.md at root + no config/voice.md."""
    return (root / "voice.md").exists() and not (root / "config" / "voice.md").exists()
```

- [ ] **Step 2.4: Run detect tests**

Run: `pytest tests/cli/unit/test_project.py -k detect_phase3 -v`
Expected: PASS (all 3).

- [ ] **Step 2.5: Write failing test for core-file migration**

Add to `tests/cli/unit/test_project.py`:

```python
def test_migrate_phase3_to_phase4_moves_core_files(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
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
```

- [ ] **Step 2.6: Run, expect ImportError / NameError**

Run: `pytest tests/cli/unit/test_project.py -k migrate_phase3 -v`
Expected: FAIL with import error.

- [ ] **Step 2.7: Implement `migrate_phase3_to_phase4` (full)**

Paste the implementation from the reference block above into `src/sourced/project.py`, positioned after `migrate_phase1_to_phase2`. Also export both new names from the module (they'll be imported as `from sourced.project import ...`). Update `tests/cli/unit/test_project.py`'s existing import block to include both new names (if using explicit imports; otherwise they're lazily imported inside tests).

- [ ] **Step 2.8: Run core-file test**

Run: `pytest tests/cli/unit/test_project.py::test_migrate_phase3_to_phase4_moves_core_files -v`
Expected: PASS.

- [ ] **Step 2.9: Write test for unmarked-voice preservation**

```python
def test_migrate_phase3_preserves_unmarked_voice(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
    (tmp_project / "voice.md").write_text("# Hand-authored voice, no marker\n")

    notes = migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "voice.md").exists()  # not moved
    assert not (tmp_project / "config" / "voice.md").exists()
    assert any("not moved" in n for n in notes)
```

- [ ] **Step 2.10: Run, expect PASS (implementation already handles marker gate)**

Run: `pytest tests/cli/unit/test_project.py::test_migrate_phase3_preserves_unmarked_voice -v`
Expected: PASS. If FAIL, step 2.7's implementation missed the `read_voice_marker` gate.

- [ ] **Step 2.11: Write tests for working-artifact migration**

```python
def test_migrate_phase3_moves_working_brief(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
    briefs = tmp_project / ".claude" / "briefs"
    briefs.mkdir(parents=True)
    (briefs / "working.brief.md").write_text("working brief")

    migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "config" / "working.brief.md").read_text() == "working brief"
    assert not briefs.exists()  # empty dir removed


def test_migrate_phase3_moves_working_log_preserves_shards_dir(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
    citations = tmp_project / ".claude" / "citations"
    citations.mkdir(parents=True)
    (citations / "working.citations.json").write_text("[]")
    (citations / "working.finder-a.json").write_text("[]")  # shard — stays

    migrate_phase3_to_phase4(tmp_project)

    assert (tmp_project / "sources" / "working.citations.json").exists()
    assert citations.exists()  # NOT removed — shards live here
    assert (citations / "working.finder-a.json").exists()
```

- [ ] **Step 2.12: Run working-artifact tests**

Run: `pytest tests/cli/unit/test_project.py -k migrate_phase3_moves_working -v`
Expected: PASS (both).

- [ ] **Step 2.13: Write test for idempotence**

```python
def test_migrate_phase3_idempotent(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
    (tmp_project / "voice.md").write_text("<!-- sourced:voice=academic -->\n")

    notes_1 = migrate_phase3_to_phase4(tmp_project)
    notes_2 = migrate_phase3_to_phase4(tmp_project)  # re-run

    assert (tmp_project / "config" / "voice.md").exists()
    assert not (tmp_project / "voice.md").exists()
    # Second run is a no-op on source side; hint lines may repeat but files unchanged
```

- [ ] **Step 2.14: Run idempotence test**

Run: `pytest tests/cli/unit/test_project.py::test_migrate_phase3_idempotent -v`
Expected: PASS (each step gates on source existence, so re-run no-ops).

- [ ] **Step 2.15: Write test for candidate-hint emission**

```python
def test_migrate_phase3_emits_candidate_hints(tmp_project):
    from sourced.project import migrate_phase3_to_phase4
    (tmp_project / "Smith2020.pdf").write_bytes(b"%PDF")
    (tmp_project / "my_writing").mkdir()
    (tmp_project / "failures_dir").mkdir()

    notes = migrate_phase3_to_phase4(tmp_project)

    assert any("candidate source file" in n for n in notes)
    assert any("my_writing" in n for n in notes)
    assert any("failures_dir" in n for n in notes)
```

- [ ] **Step 2.16: Run candidate-hint test**

Run: `pytest tests/cli/unit/test_project.py::test_migrate_phase3_emits_candidate_hints -v`
Expected: PASS.

- [ ] **Step 2.17: Run the full `test_project.py` suite**

Run: `pytest tests/cli/unit/test_project.py -v`
Expected: all PASS.

- [ ] **Step 2.18: Commit**

```bash
git add src/sourced/project.py tests/cli/unit/test_project.py
git commit -m "$(cat <<'EOF'
feat(project): detect_phase3_layout + migrate_phase3_to_phase4 primitives

Mirror the phase-1→phase-2 precedent for the phase-3→phase-4 layout shift.
Marker-gated voice/style moves; suffix-based brief/log moves;
.claude/briefs/ cleanup; .claude/citations/ preserved for dispatch shards.
Hint lines for user-uploaded PDFs and user-named sample dirs.
Idempotent on re-run. Spec §4.
EOF
)"
```

---

## Task 3: Scaffold phase-4 layout in `install.py` / `new.py`

**Files:**
- Modify: `src/sourced/commands/install.py`
- Modify: `tests/cli/integration/test_dry_run_install.py` (or a new integration test)

### Reference

Current `install.py` write sites (approximate — inspect to confirm line numbers):

```python
targets = [
    (target / "CLAUDE.md", claude_md),
    (target / "voice.md", voice_md),
    (target / "style.md", style_md),
]
if brief:
    targets.append((target / f"{brief}.brief.md", brief_md))
```

Replace with:

```python
config = target / "config"
config.mkdir(exist_ok=True)
for subdir in ("sources", "samples", "failures"):
    (target / subdir).mkdir(exist_ok=True)

targets = [
    (target / "CLAUDE.md", claude_md),
    (config / "voice.md", voice_md),
    (config / "style.md", style_md),
]
if brief:
    targets.append((config / f"{brief}.brief.md", brief_md))
```

- [ ] **Step 3.1: Write failing integration test for phase-4 scaffold**

Create `tests/cli/integration/test_new_phase4_scaffold.py`:

```python
"""Integration test: `sourced new` creates phase-4 layout."""
from pathlib import Path
import subprocess
import sys


def test_sourced_new_creates_phase4_layout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [sys.executable, "-m", "sourced", "new", "myproj",
         "--voice", "academic", "--style", "apa7", "--brief", "myproj"],
        check=True, env={"HOME": str(tmp_path), **_passthrough_env()},
    )
    root = tmp_path / "myproj"
    assert (root / "CLAUDE.md").exists()
    assert (root / "config" / "voice.md").exists()
    assert (root / "config" / "style.md").exists()
    assert (root / "config" / "myproj.brief.md").exists()
    assert (root / "sources").is_dir()
    assert (root / "samples").is_dir()
    assert (root / "failures").is_dir()
    # flat-path assertions (negative): no voice.md at root
    assert not (root / "voice.md").exists()
    assert not (root / "style.md").exists()


def _passthrough_env():
    import os
    return {k: v for k, v in os.environ.items() if k in ("PATH", "PYTHONPATH")}
```

Note: this test calls the CLI as a subprocess, which requires `sourced global-install` to have deployed library files under `$HOME/.claude/` during test setup. If `global-install` isn't a test-harness step already, check `conftest.py` for how other integration tests get their library context — you may need to adapt by invoking the Python entry point directly with `sourced.commands.new.run(...)` and mock library paths. Look at `tests/cli/integration/test_dry_run_install.py` for the pattern.

- [ ] **Step 3.2: Run, expect FAIL**

Run: `pytest tests/cli/integration/test_new_phase4_scaffold.py -v`
Expected: FAIL because install.py still writes to root.

- [ ] **Step 3.3: Modify `install.py` to write to config/ paths**

Inspect the current `install.py` write-targets block (near L38–L45 per earlier grep). Replace with the block from the "Reference" section above.

- [ ] **Step 3.4: Run integration test**

Run: `pytest tests/cli/integration/test_new_phase4_scaffold.py -v`
Expected: PASS.

- [ ] **Step 3.5: Run existing install tests — none should regress**

Run: `pytest tests/cli/integration/test_dry_run_install.py -v`
Expected: PASS. If FAIL, the dry-run integration test has flat-path assertions that need updating to phase-4 paths.

- [ ] **Step 3.6: Run the full integration suite**

Run: `pytest tests/cli/integration/ -v`
Expected: PASS. Fix any stale flat-path assertions in existing tests.

- [ ] **Step 3.7: Commit**

```bash
git add src/sourced/commands/install.py tests/cli/integration/
git commit -m "$(cat <<'EOF'
feat(cli): install scaffold writes directly to phase-4 subdir layout

voice.md, style.md, <brief>.brief.md render into config/;
sources/, samples/, failures/ mkdir'd empty (no .gitkeep).
New integration test validates fresh-scaffold layout. Spec §5.
EOF
)"
```

---

## Task 4: Wire migration into `sourced update`

**Files:**
- Modify: `src/sourced/commands/update.py`
- Create or extend: `tests/cli/integration/test_update_phase3_migration.py`

### Reference

Current `update.py` phase-1 wire-up is the template (`commands/update.py:44–101`). Phase-4 addition:

```python
# after: is_phase1 = detect_phase1_layout(target)
is_phase3 = detect_phase3_layout(target)
# ...
# Later in the function, after voice/style refresh but before deploy_docs_tree:
if is_phase3 and not force and not ctx.dry_run:
    migration_notes.extend(migrate_phase3_to_phase4(target))
```

Also add dry-run printout when `is_phase3 and ctx.dry_run`.

Import additions at top of `update.py`:

```python
from ..project import (
    # ... existing imports ...
    detect_phase3_layout,
    migrate_phase3_to_phase4,
)
```

- [ ] **Step 4.1: Write failing integration test**

Create `tests/cli/integration/test_update_phase3_migration.py`:

```python
"""Integration test: `sourced update` migrates a phase-3 project to phase-4."""
from pathlib import Path
from sourced.context import Context
from sourced.commands import update
from sourced.project import write_project_type


def _seed_phase3_project(root: Path) -> None:
    """Build a minimal phase-3-shaped project in `root`."""
    # Claude Code + modes already deployed (phase-2 state)
    # ... call a helper or inline: render CLAUDE.md, create docs/modes/, etc.
    # Simplest: run sourced install first to get phase-4 state, then mutate to phase-3.
    # For this test, directly write the flat-layout marker files.
    (root / "CLAUDE.md").write_text("<!-- sourced:begin managed -->\n# dummy\n<!-- sourced:end managed -->")
    (root / "voice.md").write_text("<!-- sourced:voice=academic -->\nrules\n")
    (root / "style.md").write_text("<!-- sourced:style=apa7 -->\nrules\n")
    (root / "report.brief.md").write_text("brief")
    (root / "report.citations.json").write_text("[]")


def test_update_migrates_phase3_to_phase4(tmp_project, minimal_ctx):
    _seed_phase3_project(tmp_project)

    update.run(minimal_ctx, project=str(tmp_project))

    assert (tmp_project / "config" / "voice.md").exists()
    assert (tmp_project / "config" / "style.md").exists()
    assert (tmp_project / "config" / "report.brief.md").exists()
    assert (tmp_project / "sources" / "report.citations.json").exists()
    assert not (tmp_project / "voice.md").exists()
    assert (tmp_project / "samples").is_dir()
    assert (tmp_project / "failures").is_dir()
```

`minimal_ctx` is a Context fixture — check `tests/cli/integration/conftest.py` or `tests/cli/unit/fixtures/` for the existing pattern; use it if present, otherwise construct a minimal Context inline:

```python
from sourced.context import Context
@pytest.fixture
def minimal_ctx():
    return Context(dry_run=False, force=False, quiet=True, color="never")
```

- [ ] **Step 4.2: Run, expect FAIL**

Run: `pytest tests/cli/integration/test_update_phase3_migration.py -v`
Expected: FAIL — phase-3 files remain at root because `update.py` doesn't detect them yet.

- [ ] **Step 4.3: Add phase-3 detection and migration in `update.py`**

Open `src/sourced/commands/update.py`. Add the import for `detect_phase3_layout, migrate_phase3_to_phase4`. After the existing `is_phase1 = detect_phase1_layout(target)` line, add `is_phase3 = detect_phase3_layout(target)`.

In the non-force branch, after the voice/style refresh block (around L117–L119) but before `deploy_docs_tree`, add:

```python
if is_phase3 and not ctx.dry_run:
    migration_notes.extend(migrate_phase3_to_phase4(target))
```

Also add a dry-run message near the existing dry-run printouts (L78–L91):

```python
if is_phase3:
    print(f"  would migrate phase-3 layout to phase-4 subdirs at {path_str(str(target), use_color)}")
```

- [ ] **Step 4.4: Run integration test**

Run: `pytest tests/cli/integration/test_update_phase3_migration.py -v`
Expected: PASS.

- [ ] **Step 4.5: Run full integration suite**

Run: `pytest tests/cli/integration/ -v`
Expected: PASS.

- [ ] **Step 4.6: Live dry-run smoke test against `/home/hayden/writing/`**

Copy first so nothing gets mutated:

```bash
cp -r /home/hayden/writing /tmp/writing-phase4-dry
cd /home/hayden/sourced
python -m sourced update --dry-run --project /tmp/writing-phase4-dry
```

Expected output: "would migrate phase-3 layout…" plus planned moves. Inspect the printed notes; confirm voice.md/style.md/report_3.brief.md/report_3.citations.json are all scheduled to move into config/ or sources/.

- [ ] **Step 4.7: Commit**

```bash
git add src/sourced/commands/update.py tests/cli/integration/test_update_phase3_migration.py
git commit -m "$(cat <<'EOF'
feat(cli): sourced update auto-migrates phase-3 layout to phase-4 subdirs

Detects voice.md-at-root-without-config/ and moves flat-layout files into
config/ + sources/. Idempotent, dry-run aware, follows phase-1→phase-2
precedent. Spec §4.4, D2.
EOF
)"
```

---

## Task 5: I11 invariant — no flat-path references in shipped templates

**Files:**
- Modify: `src/sourced/validators/invariants.py`
- Modify: `tests/cli/unit/test_validators_invariants.py`

### Reference

Spec §8.1 describes the regex + allowlist. Implementation sketch:

```python
# In validators/invariants.py

# Glob-safe paths to scan. Paths are relative to `src/sourced/data/`.
I11_SCAN_TARGETS = (
    "templates/CLAUDE.md",
    "templates/docs/modes/*.md",
    "templates/docs/voice-extractor.md",
    "templates/brief.template.md",
    "templates/brief.template.annotated-bib.md",
    "agents/*.md",
    "citations/schema.md",
)

# Flat-path patterns: each tuple is (regex, human-readable-rule, fix-hint).
# Patterns are negated-lookbehind for allowed prefixes.
FLAT_PATH_RULES = (
    (r"(?<!/)\bvoice\.md\b", "flat voice.md reference", "prefix with `config/`"),
    (r"(?<!/)\bstyle\.md\b", "flat style.md reference", "prefix with `config/`"),
    (r"(?<!sources/)<draft[^>]*>\.citations\.json", "flat <draft>.citations.json reference", "prefix with `sources/`"),
    (r"(?<!config/)<(?:draft|name)[^>]*>\.brief\.md", "flat <draft>.brief.md reference", "prefix with `config/`"),
    (r"\.claude/briefs/working\.brief\.md", "obsolete .claude/briefs/ ref", "rewrite to `config/working.brief.md`"),
    # `.claude/citations/working.citations.json` — but NOT `.claude/citations/working.<id>.json` shards
    (r"\.claude/citations/working\.citations\.json", "obsolete .claude/citations/ main-log ref", "rewrite to `sources/working.citations.json`"),
)

# Lines (substring match) exempt from scanning — marker self-references and
# layout diagrams.
I11_LINE_ALLOWLIST_SUBSTRINGS = (
    "<!-- sourced:voice=",
    "<!-- sourced:style=",
    "phase-3 layout",
    "phase-4 migration",
)

def _i11_line_exempt(line: str) -> bool:
    s = line.lstrip()
    # ASCII file-tree diagram lines
    if s.startswith("├──") or s.startswith("│") or s.startswith("└──"):
        return True
    return any(marker in line for marker in I11_LINE_ALLOWLIST_SUBSTRINGS)


def check_i11_no_flat_paths(claude_md: str) -> list[Finding]:
    """Scan bundled templates for flat-path references that phase-4 migrated."""
    findings: list[Finding] = []
    import re as _re
    for glob in I11_SCAN_TARGETS:
        try:
            with bundled_path("data") as base:
                base_path = Path(base)
                for target in base_path.glob(glob):
                    if not target.is_file():
                        continue
                    rel = target.relative_to(base_path)
                    for lineno, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
                        if _i11_line_exempt(line):
                            continue
                        for regex, rule, fix in FLAT_PATH_RULES:
                            if _re.search(regex, line):
                                findings.append(Finding(
                                    rule="I11",
                                    location=f"{rel}:{lineno}",
                                    severity="error",
                                    message=f"{rule}: {line.strip()[:100]}",
                                    fix_hint=fix,
                                ))
        except (FileNotFoundError, ModuleNotFoundError):
            continue
    return findings
```

Note: `bundled_path("data")` may not exist — check `src/sourced/render.py` for the exact bundled-resource helper. It might be `bundled_path("templates")` and friends. Adapt paths accordingly.

- [ ] **Step 5.1: Write failing unit tests with synthetic fixtures**

Add to `tests/cli/unit/test_validators_invariants.py`:

```python
# --- I11: no flat-path references ---

def test_i11_detects_bare_voice_md():
    """A line with `voice.md` (no config/ prefix) triggers I11."""
    from sourced.validators.invariants import FLAT_PATH_RULES, _i11_line_exempt
    import re as _re
    line = "Read `voice.md` on every mode entry."
    assert not _i11_line_exempt(line)
    matches = [r for r, _, _ in FLAT_PATH_RULES if _re.search(r, line)]
    assert matches, "expected voice.md pattern to match"


def test_i11_allows_config_prefix():
    from sourced.validators.invariants import FLAT_PATH_RULES
    import re as _re
    line = "Read `config/voice.md` on every mode entry."
    matches = [r for r, _, _ in FLAT_PATH_RULES if _re.search(r, line)]
    assert not matches


def test_i11_exempts_marker_line():
    from sourced.validators.invariants import _i11_line_exempt
    assert _i11_line_exempt("<!-- sourced:voice=academic -->")


def test_i11_exempts_file_tree_diagram():
    from sourced.validators.invariants import _i11_line_exempt
    assert _i11_line_exempt("├── voice.md")
    assert _i11_line_exempt("│   └── voice.md")


def test_i11_full_check_passes_on_shipped_templates():
    """After phase-4 template rewrites land, I11 is green on shipped bundle."""
    from sourced.validators.invariants import check_i11_no_flat_paths
    findings = check_i11_no_flat_paths("")  # claude_md arg unused by this check
    assert findings == [], f"I11 should be green post-rewrite; got {findings}"
```

- [ ] **Step 5.2: Run, expect ImportError / NameError**

Run: `pytest tests/cli/unit/test_validators_invariants.py -k i11 -v`
Expected: FAIL with import error (check_i11_no_flat_paths, FLAT_PATH_RULES, _i11_line_exempt not defined).

- [ ] **Step 5.3: Implement I11 in `validators/invariants.py`**

Paste the implementation from the Reference block above into `validators/invariants.py`. Position near I10 (end of file, before the aggregator).

If `bundled_path` signature doesn't match — inspect `src/sourced/render.py` for the exact shape. The check may need to call it per-subpath (`bundled_path("templates")`, `bundled_path("agents")`, `bundled_path("citations")` separately) and combine.

- [ ] **Step 5.4: Register I11 in `INVARIANT_CHECKERS`**

Near the end of `validators/invariants.py`:

```python
INVARIANT_CHECKERS = [
    ("I1", check_i1_mode_body_presence),
    ("I2", check_i2_overlay_scope),
    ("I3", check_i3_canonical_id_integrity),
    ("I4", check_i4_manifest_syntax),
    ("I5", check_i5_forcing_artifact_reachability),
    ("I6", check_i6_user_addition_markers),
    ("I7", check_i7_precedence_ordering),
    ("I8", check_i8_mode_body_compliance),
    ("I9", check_i9_size_limits),
    ("I10", check_i10_cache_discipline),
    ("I11", check_i11_no_flat_paths),  # <-- add this line
]
```

- [ ] **Step 5.5: Run I11 unit tests**

Run: `pytest tests/cli/unit/test_validators_invariants.py -k i11 -v`
Expected: PASS (all 5).

- [ ] **Step 5.6: Run `sourced check --invariants` against shipped bundle**

Run: `cd /home/hayden/sourced && python -m sourced check --invariants`
Expected: I1–I11 all PASS. If I11 fails, inspect the findings — they should point to any residual flat paths in Task 1's rewrites, which need a follow-up edit to the relevant template file(s).

- [ ] **Step 5.7: Run the full test suite**

Run: `pytest tests/`
Expected: all PASS.

- [ ] **Step 5.8: Commit**

```bash
git add src/sourced/validators/invariants.py tests/cli/unit/test_validators_invariants.py
git commit -m "$(cat <<'EOF'
feat(cli): I11 invariant — no flat-path references in shipped templates

Regex scan over templates/**/*.md + agents/*.md + citations/schema.md
for bare voice.md / style.md / <draft>.citations.json / <draft>.brief.md
references (any without the config/ or sources/ prefix). Allowlist for
marker lines and file-tree diagrams. Spec §8.
EOF
)"
```

- [ ] **Step 5.9: CHECKPOINT — run `/audit`**

Run the `/audit` skill on the current branch to get three parallel read-only audits (agent definitions, shipped infrastructure, doc coherence). Surface any findings to {{USER}} before proceeding to Task 6.

Command: invoke the `audit` skill via the Skill tool in the current session.

Gate: do not proceed to Task 6 until the audit findings are reviewed and any blockers resolved.

---

## Task 6: Integration tests + live smoke + ROADMAP/memory flips

**Files:**
- Modify: `ROADMAP.md`
- Modify: `docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md` (status flip)
- Modify (optional): `/home/hayden/.claude/projects/-home-hayden-sourced/memory/MEMORY.md` + project memory file
- Live test: `/tmp/writing-phase4-live/`

- [ ] **Step 6.1: Live smoke test on a real project copy**

```bash
cp -r /home/hayden/writing /tmp/writing-phase4-live
cd /home/hayden/sourced
python -m sourced update --project /tmp/writing-phase4-live
```

Then inspect:

```bash
ls /tmp/writing-phase4-live/
ls /tmp/writing-phase4-live/config/
ls /tmp/writing-phase4-live/sources/
```

Expected:
- Root no longer has `voice.md`, `style.md`, `report_3.brief.md`, `report_3.citations.json`, `report_3_v2.bib.json` (wait — `.bib.json` stays at root; only `.citations.json` moves).
- `config/` has `voice.md`, `style.md`, `report_3.brief.md`.
- `sources/` has `report_3.citations.json`.
- `samples/`, `failures/` exist as empty dirs.
- Source PDFs (Goddard, Grinnell, Moore) still at root (not auto-moved).
- `my_writing/`, `failures_dir/`, `posters/` still at root (not auto-moved).
- Notes printed to stdout mention the PDF candidates and `my_writing/`/`failures_dir/` hints.

- [ ] **Step 6.2: Run `sourced check --invariants` on the migrated project**

```bash
python -m sourced check --project /tmp/writing-phase4-live --invariants
```

Expected: all I1–I11 PASS. This validates the full pipeline end-to-end (install + migrate + structural integrity).

- [ ] **Step 6.3: Flip ROADMAP entry to SHIPPED**

Edit `ROADMAP.md` L286:

Change:

```
### Per-project directory restructure
**Priority:** later · **Effort:** M · **Status:** open.
```

To (fill the date and PR number after opening the PR — leave placeholders as-is here, will be patched in the PR-creation step):

```
### Per-project directory restructure
**Priority:** later · **Effort:** M · **Status:** SHIPPED 2026-04-XX via PR #N.
```

Add a one-paragraph "Shipped" note summarizing departures from the original entry (reference spec §13). Move the detailed description to an "original proposal" subsection or leave it and add the "Shipped" paragraph above.

- [ ] **Step 6.4: Flip spec status to shipped**

Edit `docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md` line 3:

Change: `**Status:** draft · **Date:** 2026-04-24 · ...`
To: `**Status:** shipped · **Date:** 2026-04-24 · **Shipped:** 2026-04-XX via PR #N · ...`

- [ ] **Step 6.5: Commit**

```bash
git add ROADMAP.md docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md
git commit -m "$(cat <<'EOF'
docs: flip phase-4 directory restructure to SHIPPED

Live smoke test on /home/hayden/writing/ confirmed migration works on
a real project. All I1-I11 green post-migration.
EOF
)"
```

- [ ] **Step 6.6: Update auto-memory**

Write a new project memory entry summarizing phase-4 ship:

```markdown
---
name: Phase 4 per-project directory restructure
description: SHIPPED 2026-04-XX via PR #N; config/sources/samples/failures subdirs; auto-migrate on sourced update; I11 invariant shipped
type: project
---

Phase-4 per-project directory restructure shipped 2026-04-XX via PR #N.

Layout: CLAUDE.md at root; voice/style/brief under config/; citation
logs + user-uploaded sources under sources/; voice-extractor inputs
under samples/ and failures/; .claude/citations/ retained for
dispatch shards; drafts + formatting siblings at root.

Migration: auto on sourced update (rejected ROADMAP's fallback-read
runway; followed phase-1→phase-2 precedent). I11 invariant added to
prevent flat-path regressions in shipped templates.

Spec: docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md
```

Add pointer to `MEMORY.md`. Commit memory changes (separate PR or as part of the spec ship — user preference).

---

## Task 7: Open PR

- [ ] **Step 7.1: Push branch**

```bash
git push -u origin phase4-directory-restructure
```

- [ ] **Step 7.2: Run `gh pr create`**

```bash
gh pr create --base main --title "feat: phase-4 per-project directory restructure" --body "$(cat <<'EOF'
## Summary
- Groups project files into `config/`, `sources/`, `samples/`, `failures/` subdirectories to reduce top-level clutter as writers accumulate drafts and source material.
- Auto-migrates phase-3 layouts on `sourced update` (rejected the ROADMAP's fallback-read runway; followed the phase-1→phase-2 precedent).
- New I11 invariant guards against flat-path regressions in shipped templates.

See design spec: `docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md`.

## Test plan
- [x] Unit: `detect_phase3_layout` (3 cases) + `migrate_phase3_to_phase4` (core files, unmarked voice, working artifacts, idempotence, candidate hints) — 8 tests in `tests/cli/unit/test_project.py`
- [x] Unit: I11 invariant positive/negative fixtures + full shipped-bundle scan — 5 tests in `tests/cli/unit/test_validators_invariants.py`
- [x] Integration: `sourced new` creates phase-4 scaffold — `tests/cli/integration/test_new_phase4_scaffold.py`
- [x] Integration: `sourced update` migrates phase-3 → phase-4 — `tests/cli/integration/test_update_phase3_migration.py`
- [x] Golden: CLAUDE.md + every mode body snapshot regenerated
- [x] `sourced check --invariants` — all I1-I11 green on shipped bundle
- [x] Live smoke: `/home/hayden/writing/` dry-run + real migration, post-migration `sourced check --invariants` green
- [ ] Reviewer: manual spot-check of a non-Hayden project (if one exists) to confirm migration mechanics don't leak author-specific assumptions
EOF
)"
```

Update the PR-URL note, then fill PR number into ROADMAP + spec header (Task 6 steps 6.3–6.4 left placeholders).

- [ ] **Step 7.3: Amend or push a follow-up commit to fill the PR number**

```bash
# In ROADMAP.md and the spec header, replace "2026-04-XX" with today's date and "PR #N" with the actual number.
git add ROADMAP.md docs/superpowers/specs/2026-04-24-per-project-directory-restructure-design.md
git commit -m "docs: fill PR number in ROADMAP + spec header"
git push
```

---

## Self-review checklist

Before marking the plan done, verify:

- [ ] Every spec §2 decision (D1–D8) is covered by at least one task. Trace:
  - D1 (layout): Task 1 (templates show new paths), Task 3 (scaffold creates new dirs)
  - D2 (auto-migrate): Task 2 (primitives), Task 4 (wire-up)
  - D3 (working-artifacts): Task 2 steps 2.11–2.12
  - D4 (no auto-move user files): Task 2 step 2.15 (hint-only)
  - D5 (voice-extractor defaults): Task 1 steps 1.9 + 1.12
  - D6 (I11): Task 5
  - D7 (no log consolidation): explicitly not in any task — handled by omission
  - D8 (no .gitkeep): Task 3 step 3.3 (bare mkdir)
- [ ] Every §9 test is in the plan:
  - §9.1 unit tests → Task 2 + Task 5
  - §9.2 integration tests → Task 3 + Task 4
  - §9.3 golden regen → Task 1 step 1.16
  - §9.4 live smoke → Task 6 step 6.1
- [ ] Every §10 commit (1–8) maps to a task (some merged):
  - Spec commits 1+6 → Task 1 (templates + voice-extractor dispatch default bundled)
  - Spec commit 2 → Task 2
  - Spec commit 3 → Task 3
  - Spec commit 4 → Task 4
  - Spec commit 5 → Task 5
  - Spec commit 7 → subsumed into Task 1 + Task 6 (test+regen+smoke)
  - Spec commit 8 → Task 6
- [ ] No TBDs, placeholders, or "see X in another task" handoffs that aren't self-contained.
- [ ] Audit checkpoint (Task 5 step 5.9) inserted at the right moment: after the invariant ships, before the cosmetic/ROADMAP-flip work.
