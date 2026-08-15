# Editing context-scaling (Path 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `[editing mode]` so its passes run per-section in a fresh `section-editor` subagent (local passes) plus one thin whole-draft global pass, so editing context stays bounded on long papers.

**Architecture:** Keep the ten passes and the four forcing-artifact names exactly; change only each pass's scope (per-section local vs whole-draft-prose global) and where it runs (a new `section-editor` subagent that mirrors `prose-drafter`, vs the parent's global pass). Local passes are fed one section's prose plus only that section's citation entries fetched by id; the global pass runs on concatenated prose with citation payloads stripped. The four named artifacts are assembled from the per-section local runs plus the global pass and surfaced at the editing to formatting handoff.

**Tech Stack:** Markdown mode bodies and agent prompts under `src/sourced/data/`; Python consistency suite (`tests/consistency/`) and invariants (`src/sourced/validators/invariants.py`); syrupy golden snapshots (`tests/cli/golden/`); pytest, ruff.

**Spec:** `docs/archive/specs/2026-08-15-editing-context-scaling-design.md`

## Global Constraints

- Preserve the ten `**Pass N` labels in `editing.md` (the `editing-passes` DerivedCount counts them against `docs/MODES.md`'s "N-pass audit" phrasing).
- Keep the four forcing-artifact name-strings verbatim everywhere: `revision report`, `§4 audit list`, `citation-payload re-read list`, `voice audit surface-scan report` (invariant I5 matches them by bolded substring).
- `editing.md` keeps its six required sections in order (Overview, When to Use, Steps, Red Flags, Rationalizations, Exit Gates) plus the Iron Law box (invariant I8).
- `agents/section-editor.md`: reference files by full path only (`config/voice.md`, `sources/<draft>.citations.json`), never bare filenames (invariant I11 scans `agents/*.md`). Frontmatter: `tools: "Read, Glob, Grep"`, `model: sonnet`, `omitClaudeMd: true`, `name: section-editor`.
- Manifest §7 block stays under 200 lines; each §7.1 registry row stays under 150 chars (invariant I9).
- writing-voice on all prose: no em dashes (use commas, parentheses, or colons).
- Commit per task. Never push without explicit approval. No commit into vault (not applicable here).
- Per-task and final gate: `python3 -m pytest -q`, `ruff check src tests`, `python3 -m sourced check --invariants` (expect 11/11). Regenerate the golden snapshot only in the task that changes the shipped `CLAUDE.md`.

---

### Task 1: Add a `shipped-agent-names` consistency guard

Installs a CI guard that the shipped agent roster (globbed from disk) is named in README, ARCHITECTURE, and INSTALL. It passes green now (four agents already named); it goes red in Task 2 when `section-editor` is added but not yet documented, which is the red-green driver for the registration work.

**Files:**
- Modify: `tests/consistency/registry.py`
- Test: `tests/consistency/test_fragment_consistency.py` (existing runner; no change)

**Interfaces:**
- Produces: a `DerivedSet("shipped-agent-names", ...)` entry in `DERIVED_SETS`.

- [ ] **Step 1: Read the existing DerivedSet pattern.** Open `tests/consistency/registry.py` and read the `shipped-skill-names` and `shipped-voice-names` DerivedSet entries plus the disk-glob helper they use (the map noted DERIVED_SETS at lines 319-351 and helpers near the counts). Match that shape exactly: a name, a disk-derived set (glob `AGENTS / "*.md"` basenames without extension), and the tuple of docs that must each contain every name.

- [ ] **Step 2: Add the guard.** Add to `DERIVED_SETS` a `DerivedSet("shipped-agent-names", <agent basenames globbed from the agents dir>, (README, ARCHITECTURE, INSTALL))`, using the module's existing path constants (find how `VOICES`/`STYLES` dirs are referenced and add an `AGENTS` equivalent if one is not already present). The doc tuple is the three files the map lists as naming agents: `README.md`, `ARCHITECTURE.md`, `docs/INSTALL.md`.

- [ ] **Step 3: Run it, expect PASS.** Run: `python3 -m pytest tests/consistency/ -q`. Expected: PASS (the four current agents `prose-drafter`, `source-finder`, `sourced-helper`, `voice-extractor` are already named in all three docs). If it fails, a pre-existing doc gap exists; fix the doc mention (do not weaken the guard) and re-run.

- [ ] **Step 4: Commit.**

```bash
git add tests/consistency/registry.py
git commit -m "test(consistency): guard the shipped agent roster across README/ARCHITECTURE/INSTALL"
```

---

### Task 2: Create the `section-editor` agent and register it

**Files:**
- Create: `src/sourced/data/agents/section-editor.md`
- Modify: `README.md` (line ~7, count and roster), `ARCHITECTURE.md` (Subagents table, ~lines 111-114), `docs/INSTALL.md` (install table ~189-192 and file-tree ~255-258)
- Test: `tests/consistency/` (the Task 1 guard)

**Interfaces:**
- Consumes: the `prose-drafter` frontmatter and dispatch contract as the template.
- Produces: a `section-editor` agent that takes a section's prose plus that section's citation entries and returns edited prose plus the local slices of the four forcing artifacts in the exact row grammar `[editing mode]` expects.

- [ ] **Step 1: Confirm the guard is green, then write the agent.** Create `src/sourced/data/agents/section-editor.md` mirroring `prose-drafter.md`'s structure, with this contract (author full prose at implementation; the contract below is binding):
  - Frontmatter: `name: section-editor`, a `description` naming it as dispatched by `academic-researcher` from inside `[editing mode]` to run the local (section-scoped) passes on one drafted section, `tools: "Read, Glob, Grep"`, `model: sonnet`, `omitClaudeMd: true`.
  - Purpose: run the local passes on one section against that section's own citations, returning edited prose plus the section's rows for the forcing artifacts. It does not run global (cross-section) checks, does not switch modes, does not fetch sources, does not write files.
  - Inputs (inlined by the parent, mirroring prose-drafter): `section_label`, `register_mode`, `section_prose` (the drafted prose to edit), `citation_entries` (full records for only the `@id`s in this section, same fields prose-drafter receives), `voice_rules` (register-filtered), `worked_paragraphs`, `cut_patterns`, `never_list`, `boundary_context` (`prev_section_last_sentence`, `next_section_first_sentence`, the section's outline slot). Absent optional fields use the literal `omit`.
  - Local passes to run (from the spec's classification): Pass 1 id validation for ids in the section; Pass 2 the citation-payload re-read list and the §4 audit list for this section's citations; Pass 3 partial-entry recheck for partials cited here; Pass 4 grammar; Pass 5 paste-artifact and punctuation lists (proper-noun consistency is split: within-section here, cross-section in the global pass); Pass 8 quote-density; the per-paragraph parts of Pass 0 (0b, 0c, 0d, 0e), Pass 6 (§10), Pass 7 (cut patterns), Pass 9 (voice).
  - Output contract: the edited section prose, then the section's forcing-artifact rows in the exact grammar `editing.md` defines (the citation-payload re-read list rows, the §4 audit-list rows, the Pass 0 revision-report rows for the per-paragraph sub-checks, and the per-section proofread and voice lists), then a `### Flags` block. The row grammar must be byte-identical to `editing.md`'s specification (no invariant parses it, so the mode body is the only guard; copy the canonical row shapes).
  - Reference every file by full path (I11).
  - Include the six-part self-contained-operation note prose-drafter carries (why `omitClaudeMd` is safe: all rules inlined).

- [ ] **Step 2: Run the guard, expect RED.** Run: `python3 -m pytest tests/consistency/ -q`. Expected: FAIL on `shipped-agent-names` (disk now has five agents; docs name four).

- [ ] **Step 3: Register in the three docs.**
  - `README.md` line ~7: change "Four subagents" to "Five subagents" and add `section-editor` to the roster sentence.
  - `ARCHITECTURE.md` Subagents table (~lines 111-114): add a row `| section-editor | academic-researcher during [editing mode] | runs the section-scoped (local) editing passes on one drafted section | No. |` (match the table's existing columns and the "writes to log?" answer format).
  - `docs/INSTALL.md`: add a `section-editor` row to the install table (~189-192) and a `section-editor.md` line to the file-tree diagram (~255-258), matching the existing rows.

- [ ] **Step 4: Run the guard and invariants, expect GREEN.** Run: `python3 -m pytest tests/consistency/ -q` (expect PASS) and `python3 -m sourced check --invariants` (expect 11/11; I11 now scans `section-editor.md` for flat paths, so fix any bare filename it flags).

- [ ] **Step 5: Commit.**

```bash
git add src/sourced/data/agents/section-editor.md README.md ARCHITECTURE.md docs/INSTALL.md
git commit -m "feat(agents): add section-editor for section-scoped editing passes"
```

---

### Task 3: Rewrite `editing.md` into per-section local dispatch plus a thin global pass

The core change. Preserve the ten `**Pass N` labels, the four artifact names, the six required sections, and the Iron Law. Change scope and add the dispatch loop and global pass.

**Files:**
- Modify: `src/sourced/data/templates/docs/modes/editing.md`
- Test: `tests/consistency/` (editing-passes count), `sourced check --invariants` (I5, I8, I11)

**Interfaces:**
- Consumes: the `section-editor` contract (Task 2) and the writing.md Phase 2 dispatch pattern.
- Produces: an editing mode body whose Steps section dispatches `section-editor` per section for local passes, runs one global pass, and assembles the four named artifacts at handoff.

- [ ] **Step 1: Update the Overview.** Keep the "ten discrete passes" sentence. Add one sentence: the passes now run per section in a `section-editor` subagent for the local (section-scoped) passes, plus one thin whole-draft global pass for the cross-section checks; the four forcing artifacts are assembled from the per-section runs plus the global pass and surfaced at handoff. Do not change the artifact-name list.

- [ ] **Step 2: Retag each of the ten passes local or global.** In the "ten passes" section, add a one-line scope tag to each pass heading (e.g. `**Pass 4 — Grammar.** [local]`), per the spec's classification. For the mixed passes (0, 5, 6, 7, 9) tag the per-paragraph part `[local]` and add a sentence that the cross-section part (Pass 0a purpose, cross-section proper-noun consistency in Pass 5, terminology/definition-order and argument-threading for Pass 6/7/9's whole-draft concerns) runs in the global pass. Do not delete or renumber any pass; do not remove any list.

- [ ] **Step 3: Add the per-section dispatch loop to the Steps section.** After the structural-deviation check (step 5) and before the pass descriptions, insert a step that dispatches one `section-editor` per section via the `Agent` tool (mirroring writing.md Phase 2 step 14): construct the bundle (section prose, `citation_entries` fetched by `@id` from `sources/<draft>.citations.json` for only that section's ids, register-filtered `voice_rules`, `worked_paragraphs`, `cut_patterns`, `never_list`, `boundary_context`); on return, run the parent's independent per-sentence audit (mirroring writing.md step 15, emitting a `parent-audit:` line), stitch the edited prose into the draft file, and collect the section's forcing-artifact rows. Write the step prose out in full, including the dispatch bundle field list and the `Tool: Agent (subagent)` line.

- [ ] **Step 4: Add the thin global pass step.** After all sections have run locally, insert a global-pass step: build a thin whole-draft view (concatenate section prose, keep `@id` markers, drop the quote payloads) plus a running skeleton (one-line section summary per section, a term list keyed to defining section). Run the global checks: Pass 0a purpose/thesis, cross-section proper-noun consistency, terminology consistency, definition-before-use order, section-boundary seams, and argument threading across non-adjacent sections. It re-reads a section's full text only when it flags a specific seam. Its findings feed the consolidated artifacts. Write this step out in full.

- [ ] **Step 5: Update the Iron Law box and handoff to say the artifacts are consolidated.** In the Iron Law box and the handoff/Exit-Gates prose, state that the four named artifacts are assembled from the per-section local runs plus the global pass and emitted as one consolidated set in the handoff turn. Keep the four names verbatim. Do not weaken the gate (still zero unresolved flagged/fidelity-drift rows).

- [ ] **Step 6: Run the gate.** Run: `python3 -m pytest tests/consistency/ -q` (the `editing-passes` count must still be 10; if it broke, a `**Pass N` label was lost), `python3 -m sourced check --invariants` (11/11: I5 names intact, I8 six sections in order, I11 n/a for mode bodies), and `ruff check src tests`. Fix any failure before committing.

- [ ] **Step 7: Structural read-through.** Re-read the rewritten `editing.md` end to end: confirm the six required sections are present in order, the ten passes are all present and tagged, the dispatch loop and global pass are coherent, and no em dashes were introduced.

- [ ] **Step 8: Commit.**

```bash
git add src/sourced/data/templates/docs/modes/editing.md
git commit -m "feat(editing): section-scoped local passes plus one thin global pass"
```

---

### Task 4: Update manifest §7.5 emitter phrasing and regenerate the golden snapshot

**Files:**
- Modify: `src/sourced/data/templates/CLAUDE.md` (§7.5 forcing-artifact definitions, ~lines 290-295)
- Modify: `tests/cli/golden/__snapshots__/test_render_golden.ambr` (regenerated)
- Test: `sourced check --invariants` (I5, I9), `tests/cli/golden/`

- [ ] **Step 1: Edit the four §7.5 definitions.** For each of the four artifacts, update only the "Emitted by ... Pass N" clause to note per-section local emission plus global-pass consolidation (for example, the revision report is "assembled from each section's local Pass 0 sub-checks plus the global pass"). Keep the bolded name-string first-token-through-first-period verbatim (I5 parses that). Keep the wording tight so §7 stays under 200 lines.

- [ ] **Step 2: Check invariants.** Run: `python3 -m sourced check --invariants`. Expected: 11/11 (I5 names intact; I9 §7 under 200 lines). If I9 fails, tighten the phrasing.

- [ ] **Step 3: Regenerate the golden.** Run: `python3 -m pytest tests/cli/golden/ --snapshot-update`. Then `git diff tests/cli/golden/__snapshots__/test_render_golden.ambr` and confirm the diff is only the §7.5 lines you changed. If anything else moved, investigate before proceeding.

- [ ] **Step 4: Full pytest.** Run: `python3 -m pytest -q`. Expected: all pass.

- [ ] **Step 5: Commit.**

```bash
git add src/sourced/data/templates/CLAUDE.md tests/cli/golden/__snapshots__/test_render_golden.ambr
git commit -m "docs(manifest): §7.5 artifacts emitted per-section plus global pass; regen golden"
```

---

### Task 5: End-to-end verification and STATUS update

**Files:**
- Modify: `STATUS.md`

- [ ] **Step 1: Full gate.** Run: `python3 -m pytest -q`, `ruff check src tests`, `python3 -m sourced check --invariants`. All green.

- [ ] **Step 2: Real-artifact dispatch test.** Using the finished project at `~/writing/cross-sex-empathy`: pick one section of `cross-sex-empathy.md`, gather its `@id`s, fetch those entries from `sources/cross-sex-empathy.citations.json`, and construct a `section-editor` dispatch bundle for that section. Dispatch it (Agent tool). Confirm: (a) the bundle holds only that section's prose plus its own citation entries (not the whole log), (b) the return carries the edited prose plus the section's forcing-artifact rows in the correct grammar, (c) the bundle size is bounded (target roughly 25K to 30K tokens for a section, versus the whole-log ~23K-plus-draft the old mode co-located). Record the measured size.

- [ ] **Step 3: Update STATUS.md.** Set the next-step pointer to reflect Path 1 shipped on branch `editing-section-scoped` (or in flight if not merged), with the spec and this plan referenced, and note Paths 2-3 logged in ROADMAP. Follow the existing STATUS format (dated bullet, In flight / Next sections).

- [ ] **Step 4: Commit.**

```bash
git add STATUS.md
git commit -m "docs(status): Path 1 (section-scoped editing) verified; next = merge or Path-2 trigger"
```

## Self-review notes

- Spec coverage: Task 2 builds the `section-editor` (spec §The section-editor subagent); Task 3 builds the dispatch loop, global pass, and pass classification (spec §Pass classification, §The thin global pass, §Design invariant); Task 4 handles the manifest §7.5 integration (spec §Integration points); Tasks 1-2 handle agent registration; Task 5 is the end-to-end proof (spec §Testing). Compaction placement (spec) is guidance, not a code change, so no task; it is recorded in the spec for future reference.
- The pass-count invariant is protected by the Global Constraint to preserve ten `**Pass N` labels and verified in Task 3 Step 6.
- The four artifact names are protected by the Global Constraint and verified by I5 in Tasks 3 and 4.
