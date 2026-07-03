# Per-project directory restructure: group project files into `config/`, `sources/`, `samples/`, `failures/`

**Status:** Shipped 2026-04-24 via PR #26 · **Date:** 2026-04-24 · **Target:** Phase 4 of the `sourced` CLI line · **Author:** {{USER}} + agent (see conversation thread `phase4-directory-restructure`)

---

## 1. Problem

A `sourced` project directory accumulates files at the top level as the writer works through 3+ essays, reports, or papers. The current flat layout stacks three disjoint file categories into one namespace:

- **Sourced-managed configuration**: `CLAUDE.md`, `voice.md`, `style.md`, `CLAUDE.d/`, `docs/`
- **Per-draft workflow artifacts**: `<draft>.brief.md`, `<draft>.md`, `<draft>.citations.json`, `<draft>.gdocs.md`, `<draft>.pandoc.md`, `<draft>.bib.json`, `<draft>.pdf`, `<draft>_outline.md`, `<draft>_plan.md`
- **User-uploaded inputs**: source PDFs, writing samples for voice extraction, AI-vs-edit pairs for failure-pattern mining

A live example: `/home/hayden/writing/` (one writer, one active project) currently has 26 top-level entries — 3 source PDFs, a `my_writing/` subdir of samples, a `failures_dir/` of AI/edit pairs, two drafts with all their siblings, scratch markdown files, and the sourced-managed config. Finding `report_3.brief.md` means scanning past three PDFs and five `.sourced.bak` files.

The hidden cost is category confusion: users don't immediately know that `voice.md` is sourced-managed (switched via the CLI) while `report_3_v2.md` is their prose, or that `report_3.citations.json` is a machine-written log while `report_3.brief.md` is hand-authored. A directory layout that separates these categories makes the CLI's ownership boundary legible.

This work is ergonomics, not a core-value change. It does not add a new mode, a new gate, or a new schema. It regroups files and wires migration.

## 2. Design decisions (locked)

**D1. Four top-level subdirectories + root for prose.** `config/` holds sourced-switchable configuration (voice, style) and per-draft hand-authored config (briefs). `sources/` holds machine-written citation logs and user-uploaded primary/secondary sources. `samples/` and `failures/` are voice-extractor inputs. Drafts and their formatting siblings stay at root because `[writing mode]` and `[formatting mode]` emit sibling files and writers expect them together. `CLAUDE.md`, `CLAUDE.d/`, `docs/`, and `.claude/` stay at root (Claude Code conventions).

**D2. Auto-migrate on `sourced update`, not fallback-read.** The ROADMAP entry proposed a one-release fallback-read runway (mode bodies reading both flat and subdir paths). Rejected. Dual-path references in 10+ mode bodies / agents / docs would encode ~200 path-string pairs that must stay coherent for a full release cycle; every new mode body or agent prompt written during that cycle has to remember to write both paths or quietly break flat-layout projects. Auto-migrate on `sourced update` follows the phase-1→phase-2 precedent already in `project.py` (`detect_phase1_layout` + `migrate_phase1_to_phase2`). Mode bodies reference one path each.

Trade-off accepted: users who upgrade `sourced` but invoke an agent before running `sourced update` see a "voice.md missing — run sourced update" halt. The halt is recoverable, names the fix, and is a single-shot event per project rather than ongoing documentation tax.

**D3. Working-artifact homes migrate too.** `.claude/briefs/working.brief.md` moves to `config/working.brief.md`. `.claude/citations/working.citations.json` moves to `sources/working.citations.json`. `.claude/citations/working.<finder-id>.json` dispatch shards stay in `.claude/citations/` (ephemeral infra, not writer-facing). This makes the pre-draft → post-draft transition a single `rename` (in the same directory) instead of a cross-directory move.

**D4. Sourced does not auto-move user-authored files.** Source PDFs, `.txt` reference material, user-named subdirs (`my_writing/`, `posters/`, `failures_dir/`) stay where the user placed them. Migration prints a one-line hint enumerating candidates. Guessing which `.pdf` at root is a citation source vs. a formatting reference vs. a paste-back of a rendered draft is error-prone; suffix-based detection works for sourced-owned suffixes (`.brief.md`, `.citations.json`) but does not generalize.

**D5. Voice-extractor dispatch defaults `samples_dir` and `failures_dir` to `<project>/samples/` and `<project>/failures/`.** Current behavior requires absolute paths in every dispatch. New behavior: passing `omit` resolves to the project-root default. Callers who want a different location still pass an absolute path. Phase-3 preflight rejection categories (`missing-samples-dir`, `malformed-failures-dir`) keep their meaning — empty or absent defaults still fail preflight.

**D6. I11 prevents flat-path regressions in shipped templates.** New invariant scans bundled `templates/**/*.md` + `data/agents/**/*.md` + `data/citations/schema.md` for flat-path patterns (unprefixed `` `voice.md` ``, `` `style.md` ``, `` `<draft>.citations.json` ``, `` `<draft>.brief.md` `` etc.). Allowlist for marker lines, file-tree diagrams in `sourced-helper.md`, and explicit documentation of the migration itself.

**D7. No consolidation of per-draft citation logs.** The current `<draft>.citations.json` naming (one log per draft, same source cited across two drafts lives in two logs) stays. Cross-draft log consolidation is a separate ROADMAP entry (`### Cross-project citation reuse`) and out of scope here. This spec only moves `<draft>.citations.json` into `sources/`; it does not rename or merge logs.

**D8. `.gitkeep`-free empty subdirs.** `samples/` and `failures/` are created empty by `sourced new` / `sourced install`. No `.gitkeep` files ship. If the user's git drops empty dirs on push, the next `sourced update` recreates them idempotently. Shipping `.gitkeep` adds a sourced-authored file users will wonder about; the cost of recreation is a no-op `mkdir`.

## 3. Target layout

```
project/
├── CLAUDE.md                              # Claude Code reads from root
├── CLAUDE.d/                              # overlay infra (unchanged)
│   ├── README.md
│   └── *.md                               # project-type overlays
├── docs/                                  # shipped mode bodies (unchanged)
│   ├── modes/
│   │   ├── research.md, plan.md, outlining.md, refining.md,
│   │   ├── writing.md, editing.md, formatting.md,
│   │   ├── annotated-bib.md, finetuning.md
│   └── voice-extractor.md                 # dispatch doc for the subagent
├── config/
│   ├── voice.md                           # line 1: <!-- sourced:voice=<name> -->
│   ├── voice.md.sourced.bak               # backup, siblings primary
│   ├── style.md                           # line 1: <!-- sourced:style=<name> -->
│   ├── style.md.sourced.bak
│   ├── <draft>.brief.md                   # one per draft
│   └── working.brief.md                   # pre-draft brief (at most one)
├── sources/
│   ├── <draft>.citations.json             # one per draft
│   ├── working.citations.json             # pre-draft main log (at most one)
│   └── *.pdf, *.txt, *.md                 # user-managed; not auto-moved
├── samples/                               # voice-extractor samples_dir default
├── failures/                              # voice-extractor failures_dir default
├── .claude/
│   └── citations/
│       └── working.<finder-id>.json       # dispatch-shard infra (unchanged)
└── <draft>.md                             # drafts
    <draft>.gdocs.md, <draft>.pandoc.md    # formatting-mode siblings
    <draft>.bib.json, <draft>.pdf          # formatting-mode siblings
    <draft>_outline.md, <draft>_plan.md    # outlining/plan artifacts
```

**Migration preview (Hayden's `/home/hayden/writing/` project, before → after):**

| Before (root) | After |
|---|---|
| `voice.md`, `voice.md.sourced.bak` | `config/voice.md`, `config/voice.md.sourced.bak` |
| `style.md`, `style.md.sourced.bak` | `config/style.md`, `config/style.md.sourced.bak` |
| `report_3.brief.md` | `config/report_3.brief.md` |
| `report_3.citations.json` | `sources/report_3.citations.json` |
| `report_3_v2.bib.json` | (stays at root — formatting-mode output) |
| `Goddard-*.pdf`, `Grinnell-*.pdf`, `Moore-*.pdf` | (stays at root; hint prints candidates for manual move to `sources/`) |
| `my_writing/` | (stays; hint prints `samples/` as new default) |
| `failures_dir/` | (stays; hint prints `failures/` as new default) |

## 4. Migration mechanics

### 4.1 Detection

New function `project.detect_phase3_layout(root: Path) -> bool`:

```python
def detect_phase3_layout(root: Path) -> bool:
    """Phase-3 layout: voice.md at root + no config/voice.md."""
    return (root / "voice.md").exists() and not (root / "config" / "voice.md").exists()
```

Name chosen for symmetry with the existing `detect_phase1_layout` — we detect "the layout as it existed in phase 3" at migration time.

### 4.2 Migration function

New function `project.migrate_phase3_to_phase4(root: Path) -> list[str]`:

```python
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
    # (2) style.md (marker-gated) + bak siblings
    # (3) *.brief.md at root (suffix-based, sourced owns the suffix)
    # (4) *.citations.json at root (suffix-based)
    # (5) .claude/briefs/working.brief.md → config/working.brief.md; rmdir briefs/
    # (6) .claude/citations/working.citations.json → sources/working.citations.json
    #     (shards working.<finder-id>.json stay in place)
    # (7) hint lines: root-level *.pdf / *.txt candidates, my_writing/, failures_dir/

    return notes
```

Steps in detail:

1. **voice.md + bak siblings.** Guard: `(root / "voice.md").exists()` AND first-line match on `<!-- sourced:voice=<name> -->`. Move `voice.md` → `config/voice.md`. Move `voice.md.sourced.bak` if present → `config/voice.md.sourced.bak`. If the marker fails to match, skip with a note: "voice.md at root lacks sourced:voice= marker; not moved (hand-authored?)".
2. **style.md + bak siblings.** Same pattern with `<!-- sourced:style=<name> -->`.
3. **`*.brief.md` at root.** Glob `root.glob("*.brief.md")`. Every match moves to `config/`. No marker check: `.brief.md` is a sourced-owned suffix. User misnames are rare and recoverable by hand.
4. **`*.citations.json` at root.** Glob and move to `sources/`. Suffix is sourced-owned.
5. **Pre-draft working brief.** If `.claude/briefs/working.brief.md` exists, move to `config/working.brief.md`. If `.claude/briefs/` is then empty, `rmdir` it.
6. **Pre-draft working log.** If `.claude/citations/working.citations.json` exists, move to `sources/working.citations.json`. Do NOT remove `.claude/citations/` — `working.<finder-id>.json` shards live there during parallel source-finder dispatch.
7. **Hint lines (not moves).** If any `*.pdf` or `*.txt` files exist at root, emit: `"Found N candidate source file(s) at root (<names>). Move into sources/ if these back citations."` If `my_writing/` exists, emit: `"Directory my_writing/ detected; voice-extractor now defaults samples_dir to samples/."` Same for `failures_dir/`.

### 4.3 Crash behavior

Each move is a single `Path.rename` (atomic on same filesystem). If step N fails, steps 1..N-1 are done and steps N+1..7 have not started. Re-running `sourced update` re-enters the migration; every gate is source-existence-based, so completed steps no-op. Partial states are recoverable without manual intervention.

### 4.4 Wire-up in `commands/update.py`

Analogous to the existing phase-1 wire-up at lines 52–57 + 100–101:

```python
is_phase3 = detect_phase3_layout(target)  # alongside is_phase1

if is_phase3 and not force:
    # After render_claude_md + voice/style refresh, before deploy_docs_tree
    migration_notes = migrate_phase3_to_phase4(target)
```

The order matters: migrate first (moves files into their phase-4 positions), then deploy docs/ and CLAUDE.d/ overlays. Fresh-render path (`--force` or `is_phase1`) skips the phase-3 migration because there are no phase-3 files to move.

### 4.5 Dry-run

Existing `ctx.dry_run` flag flows through. In dry-run mode, `migrate_phase3_to_phase4` prints the moves it *would* make without executing rename calls. Standard pattern from existing `update.py` dry-run handling.

## 5. Scaffold changes

### 5.1 `commands/install.py`

Current `install.py` writes to root paths:

```python
(target / "voice.md", voice_md),
(target / "style.md", style_md),
# ...
targets.append((target / f"{brief}.brief.md", brief_md))
```

New paths:

```python
config = target / "config"
config.mkdir(exist_ok=True)
(config / "voice.md", voice_md),
(config / "style.md", style_md),
# ...
targets.append((config / f"{brief}.brief.md", brief_md))
```

Plus: create `sources/`, `samples/`, `failures/` as empty dirs (`mkdir(exist_ok=True)` — idempotent on re-install).

### 5.2 `commands/new.py`

No direct change; `new.py` delegates to `install.run`. Layout flows from install.py's updates.

## 6. Template rewrites

All flat-path references in shipped templates route through subdir paths. File-by-file scope:

| File | Current flat-path refs (count) | Rewrite |
|---|---|---|
| `templates/CLAUDE.md` | 13 | §§6, 9, 11 pointers + §7.1/7.2/§10 paths |
| `templates/docs/modes/writing.md` | ~32 | every `voice.md` → `config/voice.md`; `<draft>.citations.json` → `sources/<draft>.citations.json` |
| `templates/docs/modes/editing.md` | ~20 | same patterns |
| `templates/docs/modes/formatting.md` | ~19 | every `style.md` → `config/style.md`; `<draft>.citations.json` → `sources/<draft>.citations.json` |
| `templates/docs/modes/outlining.md` | 9 | `voice.md`, `<draft>.citations.json` |
| `templates/docs/modes/annotated-bib.md` | 9 | `voice.md`, `style.md`, `<draft>.brief.md`, `<draft>.citations.json` |
| `templates/docs/modes/refining.md` | 3 | `voice.md`, `<draft>.citations.json` |
| `templates/docs/modes/plan.md` | 1 | `<draft>.brief.md` → `config/<draft>.brief.md` |
| `templates/docs/voice-extractor.md` | 3 + default | `voice.md` refs; new `samples_dir` default |
| `templates/brief.template.annotated-bib.md` | 1 | `voice.md` |
| `data/agents/sourced-helper.md` | scattered | file-tree diagram + §2 command table |
| `data/agents/voice-extractor.md` | 0 path refs; semantic change | `samples_dir: omit` → default `<project>/samples/` |
| `data/agents/prose-drafter.md` | 2 mentions | voice.md mentions in inlined-payload context; rewrite path language |
| `data/agents/source-finder.md` | 0 (stays) | writes to `.claude/citations/working.<finder-id>.json` — unchanged |
| `data/citations/schema.md` | 2 | `<draft>.citations.json` → `sources/<draft>.citations.json`; `.claude/citations/working.citations.json` → `sources/working.citations.json` |

### 6.1 Rewrite pattern

Rewrites are done file-by-file as prose edits (not a mechanical sed pass). I11 (§8) catches regressions post-edit. The patterns:

- `` `voice.md` `` → `` `config/voice.md` ``
- `` `style.md` `` → `` `config/style.md` ``
- `` `<draft>.citations.json` `` → `` `sources/<draft>.citations.json` ``
- `` `<draft-filename>.citations.json` `` → `` `sources/<draft-filename>.citations.json` ``
- `` `<draft>.brief.md` `` → `` `config/<draft>.brief.md` ``
- `` `<draft-name>.brief.md` `` → `` `config/<draft-name>.brief.md` ``
- `` `<name>.brief.md` `` → `` `config/<name>.brief.md` ``
- `` `.claude/briefs/working.brief.md` `` → `` `config/working.brief.md` ``
- `` `.claude/citations/working.citations.json` `` → `` `sources/working.citations.json` ``

Retained as-is (`.claude/citations/` hides dispatch-shard infra): `.claude/citations/working.<finder-id>.json` references in `agents/source-finder.md`, `citations/schema.md`.

### 6.2 Path-agnostic subagents (no rewrite)

`source-finder.md` writes to `.claude/citations/working.<finder-id>.json` — shard path, unchanged.

`prose-drafter.md` receives voice content (`voice_rules`, `worked_paragraphs`, `cut_patterns`) inlined as a dispatch payload, not as file paths. The voice-path change lands in `writing.md` Phase 2's "Read `config/voice.md`" step, not in the subagent. The subagent's own prose mentions "the project's `voice.md`" in the inlined-payload documentation — those mentions get the `config/` prefix.

## 7. Voice-extractor dispatch default

### 7.1 Dispatch template change

`templates/docs/voice-extractor.md`:

```
samples_dir: <absolute path to samples, or "omit" to default to <project>/samples/>
failures_dir: <absolute path to AI-vs-edit pairs, or "omit" to default to <project>/failures/ if non-empty>
```

Dispatcher (`[collaborative mode]`) resolves `omit` to the project-root default before passing to the subagent. The subagent sees only absolute paths — its `samples_dir` contract is unchanged.

### 7.2 Subagent preflight (`agents/voice-extractor.md`)

Preflight already halts with `missing-samples-dir` when `samples_dir` is absent or unreadable. Unchanged. What changes: the dispatcher no longer passes absolute paths by default (it resolves `<project>/samples/` and passes that absolute path). Empty `<project>/samples/` (mkdir'd but no files) yields `under-sample` rejection per existing step-6 logic — not `missing-samples-dir`. Fine: the rejection category matches the actual failure mode.

### 7.3 Phase-3 caveat

Phase-3 (PR #25) shipped the dispatch template unchanged. Phase-4 supersedes it; the dispatch-template-doc rewrite is part of phase-4's commit-1 template rewrites.

## 8. I11 — no flat-path references in shipped templates

### 8.1 Check

`validators/invariants.py` gains `check_i11_no_flat_paths(claude_md: str) -> list[Finding]`. Scans:

- `templates/CLAUDE.md`
- every `templates/docs/modes/*.md`
- `templates/docs/voice-extractor.md`
- `templates/brief.template*.md`
- `data/agents/*.md`
- `data/citations/schema.md`

Regex patterns (each fires if matched OUTSIDE the allowlist):

- `` `voice\.md` `` not preceded by `config/` or `~/.claude/voice/` (library paths)
- `` `style\.md` `` not preceded by `config/` or `~/.claude/style/`
- `` `(<draft>|<draft-name>|<name>|<draft-filename>)\.citations\.json` `` not preceded by `sources/`
- `` `(<draft>|<draft-name>|<name>)\.brief\.md` `` not preceded by `config/`
- `` `\.claude/briefs/working\.brief\.md` `` (entire path; anything still pointing at the old location is a miss)
- `` `\.claude/citations/working\.citations\.json` `` (same — `working.<finder-id>.json` shards are fine)

### 8.2 Allowlist

Lines exempt from I11 scans:

- Marker-line self-references: `<!-- sourced:voice=<name> -->` and `<!-- sourced:style=<name> -->`
- File-tree ASCII diagrams in `agents/sourced-helper.md` documenting the layout (detected by leading `├──` / `│` / `└──` characters)
- Migration documentation that discusses old paths explicitly: any line containing the phrase `phase-3 layout` or `phase-4 migration`
- This spec file itself (not scanned — lives under `docs/superpowers/specs/`, out of I11's target glob)

### 8.3 Registration

Add `("I11", check_i11_no_flat_paths)` to `INVARIANT_CHECKERS` list in `invariants.py`. `sourced check --invariants` picks it up through the existing aggregator.

## 9. Tests

### 9.1 Unit tests

- **`tests/unit/test_project_phase4.py`** (new file):
  - `test_detect_phase3_layout_true_on_flat` — fixture with `voice.md` at root, no `config/`.
  - `test_detect_phase3_layout_false_on_subdir` — fixture with `config/voice.md`.
  - `test_detect_phase3_layout_false_on_unmanaged` — fixture with no `voice.md` anywhere.
  - `test_migrate_phase3_to_phase4_moves_core_files` — fixture with voice.md, style.md, report.brief.md, report.citations.json at root → all land in config/ or sources/.
  - `test_migrate_phase3_to_phase4_preserves_unmarked_voice` — fixture with a `voice.md` lacking the marker → stays at root, note emitted.
  - `test_migrate_phase3_to_phase4_handles_working_artifacts` — fixture with `.claude/briefs/working.brief.md` and `.claude/citations/working.citations.json` → both moved; `.claude/briefs/` removed; `.claude/citations/` preserved.
  - `test_migrate_phase3_to_phase4_idempotent` — re-run on a partially-migrated dir no-ops cleanly.
  - `test_migrate_phase3_to_phase4_prints_hint_on_candidates` — fixture with `root/some.pdf` + `root/my_writing/` → note list mentions both.

- **`tests/unit/test_invariants.py::test_i11_flat_paths`** (extension):
  - Positive fixture: a bundled-template with `` `config/voice.md` `` — I11 passes.
  - Negative fixture: inject a template with bare `` `voice.md` `` — I11 emits a finding.
  - Allowlist fixture: marker line — I11 no-ops.

### 9.2 Integration tests

- **`tests/integration/test_new_phase4_layout.py`**:
  - Run `sourced new tmp-project --voice=academic --style=apa7 --brief=foo`.
  - Assert: `config/voice.md`, `config/style.md`, `config/foo.brief.md` exist.
  - Assert: `sources/`, `samples/`, `failures/` exist as empty dirs.
  - Assert: CLAUDE.md exists at root, docs/ and CLAUDE.d/ at root (unchanged from phase 2).

- **`tests/integration/test_update_migration.py`**:
  - Setup: build a tmp phase-3-layout project (voice.md at root, etc.) by hand.
  - Run: `sourced update --project tmp-project`.
  - Assert: post-update layout matches phase-4 target.
  - Assert: migration notes printed.

### 9.3 Golden snapshot regeneration

- `tests/cli/golden/test_render_golden.ambr` — snapshots of rendered CLAUDE.md change because §6, §8, §9, §11 reference `config/voice.md` / `config/style.md` / `sources/<draft>.citations.json` / `config/<draft>.brief.md`. Regenerate with `pytest --snapshot-update tests/cli/golden/`.

### 9.4 Live-project smoke test (manual, pre-merge)

- Copy `/home/hayden/writing/` to `/tmp/writing-phase4-test/`.
- Run `sourced update --dry-run --project /tmp/writing-phase4-test/`.
- Review the planned moves. Confirm: voice.md → config/voice.md, report_3.brief.md → config/report_3.brief.md, report_3.citations.json → sources/report_3.citations.json, PDFs untouched.
- Run `sourced update --project /tmp/writing-phase4-test/` (no dry-run).
- Inspect resulting layout.
- Run `sourced check --project /tmp/writing-phase4-test/`. Confirm green.

## 10. Rollout plan

One PR against `main` with commits matching phase-2 / phase-3 cadence:

1. **Template rewrites** (`CLAUDE.md`, `docs/modes/*.md`, `docs/voice-extractor.md`, `brief.template*.md`, `agents/*.md`, `citations/schema.md`). Flat paths become subdir-prefixed paths everywhere user-facing. `pytest` green after.
2. **Migration primitives** (`project.py`): `detect_phase3_layout`, `migrate_phase3_to_phase4`. Unit tests from §9.1 ship with this commit.
3. **Scaffold changes** (`commands/install.py`, `commands/new.py`): render directly to subdir paths, mkdir empty siblings.
4. **Update wire-up** (`commands/update.py`): call `migrate_phase3_to_phase4` when `detect_phase3_layout` returns true. Integration tests from §9.2 ship with this commit.
5. **I11 invariant** (`validators/invariants.py`): new check + allowlist + registration.
6. **Voice-extractor dispatch defaults**: `docs/voice-extractor.md` dispatch template doc update; `agents/voice-extractor.md` semantic note on `omit` defaults.
7. **Tests + golden regen**: unit + integration + snapshot updates.
8. **Documentation flips**: `ROADMAP.md` entry → `SHIPPED 2026-04-XX via PR #X`; `docs/specs/` entry cross-link; memory updated.

Verification between commits: `pytest` green, `sourced check --invariants` green, `sourced check` green on a rendered fresh project.

## 11. Non-goals

- **Auto-moving user-authored files.** Source PDFs, user-named sample dirs, scratch `.md`/`.txt` files stay where the user put them. Migration prints hints, not moves.
- **Cross-draft citation-log consolidation.** Separate ROADMAP entry (`### Cross-project citation reuse`, ROADMAP L315). This spec moves `<draft>.citations.json` into `sources/` but does not merge logs.
- **Per-draft outlines / plans into subdirs.** `<draft>_outline.md` and `<draft>_plan.md` stay at root because they're draft-paired artifacts in active use. Moving them to `config/` would split related files across two directories.
- **`docs/` or `CLAUDE.d/` relocation.** Shipped infra, not user-facing clutter. Stays at root (Claude Code + sourced-loader conventions).
- **Fallback-read runway.** Rejected in D2.
- **`.gitkeep` marker files.** Rejected in D8.

## 12. Open questions

None load-bearing. Two that surfaced during brainstorming and were resolved:

- **Q (resolved).** Should `samples/` and `failures/` both exist, or is `samples/` alone enough? → Both (D1, phase-3 added `failures_dir` input).
- **Q (resolved).** Do working-brief and working-log move out of `.claude/`? → Yes (D3, symmetry pays off at draft creation).

## 13. Departures from the ROADMAP entry

For traceability against `ROADMAP.md` L286–L313:

| ROADMAP proposed | Spec decision | Why |
|---|---|---|
| `samples/` only | `samples/` + `failures/` siblings | ROADMAP predates phase-3's `failures_dir` addition (D1) |
| Fallback-read runway for one release | Auto-migrate on `sourced update` | Reuses phase-1→phase-2 precedent; avoids ~200 dual-path strings (D2) |
| `<name>.brief.md` under `config/` | Same, plus `working.brief.md` under `config/` | ROADMAP silent on working-brief; symmetry (D3) |
| `sources/` holds `<draft>.citations.json` + PDFs | Same, plus `working.citations.json` from `.claude/` | Symmetry (D3) |
| `install.sh` creates subdirs | `install.py` creates subdirs | install.sh retired in phase 1 (terminology adjustment only) |
| "Next release: print `sourced migrate` hint" | No separate `sourced migrate` subcommand | Auto-migration happens inside `sourced update`; no separate subcommand needed (D2) |

## 14. Appendix: evidence trail

- Conversation: `phase4-directory-restructure` (this thread)
- ROADMAP entry: `ROADMAP.md` L286–L313 (pre-phase-3, pre-Python-CLI)
- Phase-2 precedent: `src/sourced/project.py::detect_phase1_layout`, `migrate_phase1_to_phase2`; `commands/update.py::52-57, 100-101`
- Phase-3 voice-extractor inputs: `agents/voice-extractor.md::22-32` (samples_dir + failures_dir)
- Live layout reference: `/home/hayden/writing/` (26 top-level entries as of 2026-04-24)
- Flat-path reference audit: 106+ matches across 10 files (see §6 table)
- I1–I10 invariant precedent: `validators/invariants.py` (phase-2 spec §8)
