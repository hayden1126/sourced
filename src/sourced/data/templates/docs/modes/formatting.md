# [formatting mode]

## Overview

Formatting converts source prose carrying Pandoc citation IDs into a fully-rendered document for a specific paste target. Rendering belongs to `pandoc --citeproc` plus the style's vendored CSL file; this mode owns the pre-flight, the invocation, the warning triage, and the post-pandoc pass. Source prose and the citation log are read-only throughout (one narrow carve-out: staleness re-verify in step 2 may update `retrieved_at` and `source.authors`). This is the terminal stage of the pipeline.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "format this" / "render this" / "paste this" / "format for X" (see manifest §7.2). The paste target must be named in the invocation or supplied immediately after asking — formatting does not begin without a target.
- **Gate satisfied.** The editing → formatting handoff gate has passed: revision report clean, §4 audit list clean, citation-payload re-read list clean, voice audit surface-scan report emitted, and {{USER}} has confirmed the prose is ready. Do not enter on your own judgment that editing looks "done."

**Do not enter when:**
- The draft has not been through `[editing mode]` with a confirmed handoff. Formatting without the upstream gate is a gate violation.
- No paste target has been named. If {{USER}} says "format this" without a target, ask: "Which paste target? Supported targets are listed in `config/style.md §Paste target expression rules`."
- `config/style.md` is missing. Stop and ask {{USER}} to run `sourced switch style <name>` rather than guessing rules. Do not attempt to infer a style.
- The voice audit surface-scan report has not been emitted in the editing handoff turn. Per manifest §7.4, editing → formatting requires revision report clean + §4 audit list clean + citation-payload re-read list clean + voice audit surface-scan report emitted + paste target named; a handoff without the report is an incomplete gate. Ask {{USER}} to complete the editing handoff before entering formatting.

**Announcement rule.** The first output of every formatting entry names the target: `Switching to [formatting mode for <target>].` (e.g., `Switching to [formatting mode for google-docs].`).

## Iron Law

```
┌──────────────────────────────────────────────────────────────┐
│  NO TERMINAL OUTPUT WITHOUT PRE-FLIGHT PASS (ALL 6 CHECKS)   │
│  NO SOURCE PROSE MODIFICATION — OUTPUT GOES TO SIBLING FILES  │
│  NO STYLE IMPROVISATION — STYLE IS FIXED BY style.md          │
└──────────────────────────────────────────────────────────────┘
```

Skipping pre-flight ships a rendered document that may contain unresolved verification debt, stale bylines, or inline quotes that should be block-formatted. Modifying source prose during formatting defeats the round-trip discipline the pipeline relies on. Improvising style decisions (inline citation shape, hanging-indent rules, reference list ordering) produces output that diverges from the author's declared style on the next re-run.

## Steps

### Entry

1. **Announce entry.** First output of the turn: `Switching to [formatting mode for <target>].` Name the target verbatim. Then in one clause: "formatting `<draft>` for `<target>`".

   Read `config/style.md` in full on every entry. Verify `§Style identity.CSL provenance.file` resolves to a CSL file at `~/.claude/style/<style>/<csl-filename>`. If the CSL file is missing, halt: "CSL file not found at `<path>`. Run `sourced switch style <name>` to reinstall." Do not proceed.

   Also load the citation log (`sources/<draft>.citations.json`). The log is read-only except for staleness carve-outs in step 2.

### Pre-flight (gate to terminal output)

2. **Run all six checks.** Pre-flight checks 1–4 halt on first failure. Checks 5 (stale `retrieved_at`) and 6 (inline-quote threshold) are COLLECT-FIRST: run both to completion, emit the stale-entries grouped report AND the inline-quote-threshold list in the same turn, then halt on whichever (or both) requires user action. Halting on check 5 alone without emitting the check 6 list is a gate violation — the inline-quote-threshold list is a forcing artifact regardless of other halts.

   **Check 1 — `[VERIFY: ...]` tokens.** Scan source prose for any `[VERIFY: ...]` token. Each is unresolved verification debt. Halt; list every token with its line. Ask {{USER}} to resolve via `[research mode]` and return to `[editing mode]` before re-formatting.

   **Check 2 — `[UNSOURCED]` tokens.** Scan for `[UNSOURCED]` anywhere in source prose. Each is a claim with no source. Halt; list instances. Ask {{USER}} to source or cut the claim in `[editing mode]`.

   **Check 3 — Rendered citation strings.** Scan source prose (including inside block quotes) for rendered citation strings: `(Smith, 2010)`, `Smith (2010)`, `[1]`, and similar patterns. These should have been converted to Pandoc IDs in `[editing mode]` pass 1. Halt on any hit; list each instance with its line. Ask {{USER}}: convert in place or return to `[editing mode]`? Converting in place requires verifying each against the log — do not convert silently. If {{USER}} elects to return to editing, surface the count and lines in the handoff note.

   **Check 4 — Unresolved citation IDs.** For every `[@id]`, `@id`, or `[@id, p. N]` in source prose, confirm the id resolves to an entry in the citation log. Halt on any miss; surface unresolved IDs by line.

   **Check 5 — Stale `retrieved_at`.** For every id referenced in source prose, check `retrieved_at` per `~/.claude/citations/schema.md §Staleness`. Collect every stale or missing entry before surfacing any. Do not prompt one-by-one. Emit one grouped report: each row carries `{id, retrieved_at or "missing", source URL, reference count in prose}`. Per-entry choices offered to {{USER}}:

   - **Re-fetch and re-verify** (preferred for web sources): switch to `[research mode]`, re-verify byline and cited passage, update `retrieved_at` (and `source.authors` if byline changed), return here. Note the update in the step 8 report.
   - **Accept as-is** (acceptable for stable DOIs where the source is unlikely to have changed): hold for this format pass only. Does not carry to future sessions.
   - **Treat as gap, return to `[editing mode]`**: close formatting, surface the gap.

   Offer shortcut options alongside the per-entry list: "re-fetch all" / "accept all" / mixed. Halt on any stale entry until {{USER}} resolves the full grouped report.

   **Check 6 — Inline quote threshold.** Read `§Document layout.Block quotes` in the active `config/style.md`.

   - If that subsection is absent OR declares `Threshold: none`, skip this check entirely. The style prescribes no threshold; any inline-quote shape is acceptable. When skipped under this absent-subsection rule, explicitly note in the step 8 report that "inline-quote threshold check skipped: `config/style.md`'s `§Document layout.Block quotes` declares no threshold." No forcing artifact is produced for this check under the skip rule — that is the only permitted path to a missing list. When the subsection is present and declares a threshold, the list is always emitted (empty or non-empty); silence is not a substitute.
   - Otherwise, read the declared threshold value (e.g., "40 words", "4 lines"). Walk source prose, identify all quotation-marked spans. For each, estimate word count. Flag every span that plausibly meets or exceeds the threshold.

   **Emit `### Inline quote threshold hits` as a forcing artifact**, regardless of hit count:

   ```
   ### Inline quote threshold hits

   | paragraph_ref | quote_word_count | threshold | @id (if attached) |
   |---------------|-----------------|-----------|-------------------|
   ```

   Empty table required on zero hits. A pre-flight pass that does not produce this list has not run. Any non-empty list halts: surface the list and refuse to continue. {{USER}} returns to `[editing mode]` to convert the flagged inline quotes to block quotes. Formatting does not rewrite prose.

### Pre-pandoc pass

3. **Copy source prose to `<draft>.pandoc.md`.** Collapse per-instance citation IDs in the copy: apply the regex `<author>-<year>-\d{3}` → `<author>-<year>` to all citation references in the copied file. Source `<draft>.md` is NEVER modified. The copy is the only file that changes in this step.

### Emit bibliography

4. **Emit CSL-JSON bibliography to `<draft>.bib.json`.** Follow `~/.claude/citations/csl-json-emitter.md` in full. Rules:

   - One entry per unique source, keyed to the collapsed id (post-step-3 form).
   - Filter to ids actually referenced in source prose; dead log entries are not emitted.
   - Tolerable emitter warnings (per the emitter spec's §Source-type inference rules: the rule-5 fallback and the rule-0 explicit-type warnings) are collected for the step 8 report but do not halt.

### Pandoc invocation

5. **Invoke pandoc.** Base invocation shape:

   ```
   pandoc <flags> --bibliography=<draft>.bib.json --csl=<csl-path> --metadata reference-section-title=<list-heading> -o <output> <draft>.pandoc.md
   ```

   `<flags>` comes from `config/style.md §Paste target expression rules.<target>.pandoc flags`. `<list-heading>` is the `- List heading:` value from `config/style.md §Style identity` (e.g., `References`, `Bibliography`, `Works Cited`); pandoc emits this heading itself ahead of the `::: {#refs}` fenced div, so source `.md` ends at the last body paragraph and never carries a hand-authored `# References` / `# Bibliography` / `# Works Cited` line. Multi-word headings need shell quoting at the call site (e.g., `--metadata "reference-section-title=Works Cited"`). A surviving hand-authored heading in source prose is a legacy-draft regression caught by `[editing mode]`'s pass-1 scan.

   Per-target output path:

   | Target | Output file |
   |--------|------------|
   | `word` | `<draft>.docx` |
   | `google-docs` | `<draft>.gdocs.md` |
   | `plain-markdown` | `<draft>.plain.md` |
   | `latex` | `<draft>.tex` |

   **word target:** Check `§Paste target expression rules.word.reference.docx:` bullet in `config/style.md`. If a path is declared AND the file exists at `~/.claude/style/<path>`, add `--reference-doc=<absolute-path>`. If declared but absent, proceed without the flag and record "reference.docx fallback: `<path>` not found; using pandoc default layout" as a tolerable warning for the step 8 report. If no path declared, no flag.

   **latex target:** Read `§Paste target expression rules.latex.template.tex:` bullet. The template is required (unlike reference.docx which has a fallback). Resolve the declared relative path to `~/.claude/style/<path>` and add `--template=<absolute-path>`. If declared but absent, halt: "template.tex missing: `<path>` — install is broken. Run `sourced switch style <name>`." No fallback.

   **google-docs and plain-markdown targets:** Check `§Paste target expression rules.<target>.lua-filter:` bullet. If declared AND the file exists at `~/.claude/filters/<name>`, add `--lua-filter=<absolute-path>`. If declared but absent, halt: "lua-filter missing: `<name>` — install is broken." If the bullet is absent, no filter.

### Pandoc exit handling

6. **Handle pandoc exit and stderr.**

   - **Non-zero exit:** halt. Surface stderr in full. Do not write output.
   - **Exit 0, stderr empty:** proceed to step 7.
   - **Exit 0, stderr non-empty:** classify each warning per the table below.

   **Citeproc warning classification:**

   | Warning pattern | Classification | Action |
   |-----------------|---------------|--------|
   | `reference not found` / `citation [@id] not resolved` | Blocking | Halt before writing output. |
   | `missing field: type` on a CSL-JSON entry | Blocking | Halt. CSL `type` drives rendering; fix the emitter inference path, do not let the default fire silently. |
   | `ambiguous citation: ... matches N items` | Blocking | Halt. The emitter's id-collapse produced a collision; fix the emitter or the log entry. |
   | `missing field: DOI` / `missing field: URL` on applicable types | Tolerable | Surface in step 8 report. |
   | `missing field: publisher-place` / other optional fields | Tolerable | Surface in step 8 report. |
   | `unrecognized element` / similar CSL-parse warning | Blocking | Halt. CSL file is suspect. |

   Blocking warnings halt before writing the output file. Tolerable warnings are collected and surfaced in the step 8 report; they do not halt.

### Post-pandoc pass

7. **Apply post-pandoc transforms and paste-time instructions.**

   Read `§Paste target expression rules.<target>.Post-pandoc transforms` from the active `config/style.md`. Two transform shapes, identified by whether the declaration carries a backticked shell command:

   - **Command pipe:** backticked shell command present. Execute as a shell pipe: read the output file on stdin, write transformed content on stdout, overwrite the file atomically. Pure text-layer edits; no citation-log context required.
   - **Agent walk:** no backticked command (typically a reference into `§Style identity.On-demand references`). Execute in the agent loop per the description. The classical-abbreviations rewrite for chicago17 is the reference example: walk the rendered output; for each bibliography entry and (for NB) each footnote body, read back to the CSL-JSON entry that produced it; if the entry's `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column.

   Within a single target, run all command-pipe transforms first, then agent-walk transforms. The walker then operates on already-cleaned output.

   Prepend paste-time instructions from `config/style.md §Paste target expression rules.<target>.Paste-time instructions` to the output file. Each instruction is a single line prefixed with `<!-- paste-time: -->`.

### Report

8. **Report to {{USER}}.** One paragraph covering: source file, target, output sibling file, citations resolved, unique References entries, staleness handled (re-fetched / accepted / gap, with ids named), tolerable pandoc or emitter warnings, paste-time instructions {{USER}} must apply manually (e.g., "apply hanging indent in Google Docs after pasting"). If the staleness carve-out fired (step 2 re-verify updated `retrieved_at` or `source.authors`), name each updated entry. Do not summarize the prose itself.

## Citeproc Warning Classification

The full table lives in step 6 above. Quick lookup: blocking warnings (halt before output) are `reference not found`, `missing field: type`, `ambiguous citation`, and `unrecognized element`. Tolerable warnings (surface in report) are `missing field: DOI`, `missing field: URL`, and `missing field: publisher-place` / other optional fields.

## What This Mode Does NOT Do

- **Edit prose.** Voice rules, claim revisions, citation re-attribution, block-quote conversion: all belong upstream in `[editing mode]` or earlier. Formatting does not rewrite prose.
- **Add or modify citation log entries** (read-only). One carve-out: when {{USER}} chooses "re-fetch and re-verify" on a stale entry in step 2, update that entry's `retrieved_at` (and `source.authors` if the byline has changed) before rendering. Note the update in the step 8 report.
- **Choose a style.** Style is fixed by `config/style.md`. Switching requires `sourced switch style <name>` and re-running formatting.
- **Branch on Shape.** Shape is audit metadata in the slim schema; pandoc+CSL owns Shape-specific rendering. The procedure above is uniform across author-date, author-page, footnote, numeric-sequence, and numeric-alpha styles.

## Re-running Formatting

Re-running is cheap and idempotent. Style change: re-run on the same source after `sourced switch style <name>`. Different targets (google-docs and plain-markdown both needed): run formatting twice with different target declarations; each writes its own sibling file. Source `.md` and citation log are unchanged modulo the staleness carve-out.

## Red Flags

- *"The pre-flight is a formality — I'll do a quick scan rather than running all six checks."* — No. Six checks, in full, every time. A partial pre-flight is not a pre-flight. The inline-quote-threshold list must be emitted even when you are confident there are no hits.
- *"The inline-quote-threshold list is empty, so I'll skip emitting it."* — No. Empty list required. Absent list means the check didn't run.
- *"This `[VERIFY: ...]` token looks minor — I'll render around it."* — No. Every `[VERIFY: ...]` halts. There is no "minor" debt.
- *"The stale entry is a DOI-backed source — it definitely hasn't changed, I'll skip the report."* — Surface it in the grouped report and let {{USER}} choose "accept as-is." Your confidence is not the decision.
- *"One stale entry surfaced — I'll ask about it, then ask about the next."* — No. Collect all stale entries first. One grouped report, then {{USER}} resolves the whole set.
- *"The pandoc warning says `missing field: DOI` — I'll just ignore it."* — Tolerable, not ignorable. Surface in the step 8 report.
- *"The ambiguous-citation warning means pandoc still rendered something — output looks fine, I'll proceed."* — No. Ambiguous citation is blocking. Halt before writing output.
- *"I'll modify the source prose to fix the inline quote threshold hit."* — No. Return to `[editing mode]`. Formatting does not rewrite prose.
- *"`config/style.md` is cached from last session — I'll work from memory."* — Re-read `config/style.md` in full on every entry. Do not work from memory.
- *"{{USER}} seems ready, the editing looked clean — I'll skip the formal gate check."* — Enter only after a confirmed editing handoff with all four forcing artifacts. "Looked clean" is not a gate.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "Pre-flight check 3 is redundant — `[editing mode]` pass 1 already cleared rendered citations." | Editing pass 1 catches them if the pass ran correctly. Pre-flight check 3 is the backstop for when editing slipped or the draft was touched after editing. Run it. |
| "The stale `retrieved_at` is only a few days old — it's practically fresh." | Schema.md §Staleness sets the threshold. "Practically fresh" is your estimate, not the schema's. Surface the entry and let {{USER}} choose. |
| "The block-quote threshold check is LLM-judgment, so I'll eyeball it and skip the list." | The list is the forcing artifact for the formatting pre-flight gate (manifest §7.5). Eyeballing without emitting the list means the gate has not been satisfied, regardless of what you saw. |
| "Reference.docx is missing but the Word output is fine with the default layout." | Proceed without the flag (that's the documented fallback), but record the fallback warning in the step 8 report. Silent omission hides install state from {{USER}}. |
| "Switching styles mid-session is easier than re-running — I'll just pick the right CSL and keep going." | Style is fixed by `config/style.md`. Mid-session style substitution produces output that diverges from the declared style on every future re-run. Use `sourced switch style <name>` and re-run. |
| "The emitter produced tolerable warnings — not worth cluttering the report." | Tolerable warnings go in the report. They are tolerable in the sense that they do not halt; they are not tolerable in the sense of being silently dropped. |
| "The user already reviewed the prose in editing — pre-flight checks 1 and 2 are ceremonial." | Editing and formatting operate on different copies of the prose. A `[VERIFY: ...]` token introduced between editing and formatting — or present in a section editing didn't touch — would be missed. Pre-flight is not redundant with editing; it is the formatting gate. |
| "I can infer the style from the citation log's reference strings." | Citation log entries carry Pandoc IDs, not rendered reference strings. Style is not inferable from the log; read `config/style.md`. |

## Quick Reference

```
ENTRY:   Switching to [formatting mode for <target>].
         Read config/style.md in full. Verify CSL file on disk. Load citation log.

PRE-FLIGHT (halt on any failure):
  1. [VERIFY: ...] tokens   → halt; list all.
  2. [UNSOURCED] tokens     → halt; list all.
  3. Rendered citations     → halt; list all; ask convert or return to editing.
  4. Unresolved IDs         → halt; surface by line.
  5. Stale retrieved_at     → collect ALL stale entries first; grouped report; per-entry choices.
  6. Inline quote threshold → read threshold from config/style.md §Document layout.Block quotes.
                              Emit ### Inline quote threshold hits table (required; empty table
                              on zero hits). Non-empty list halts.

STEP 3:  Copy to <draft>.pandoc.md. Collapse IDs (regex: <author>-<year>-\d{3} → <author>-<year>).
         Source <draft>.md NEVER modified.

STEP 4:  Emit CSL-JSON to <draft>.bib.json. Per emitter spec. Filter to referenced IDs only.

STEP 5:  pandoc <flags> --bibliography=<draft>.bib.json --csl=<csl-path> \
                --metadata reference-section-title=<list-heading> -o <output> <draft>.pandoc.md
         <list-heading>: from config/style.md §Style identity (- List heading:). Quote multi-word
                         values: --metadata "reference-section-title=Works Cited".
         word:          check reference.docx bullet; add flag if file exists; fallback warning if absent.
         latex:         template REQUIRED; halt if absent.
         google-docs / plain-markdown: lua-filter if declared; halt if declared but absent.

STEP 6:  Exit 0 + empty stderr → proceed.
         Non-zero exit → halt; surface stderr in full.
         Exit 0 + stderr → classify each warning. Blocking: halt. Tolerable: collect for report.

STEP 7:  Post-pandoc transforms: command-pipes first, agent-walks second.
         Prepend paste-time instructions (<!-- paste-time: --> prefix).

STEP 8:  One-paragraph report: source, target, output, citations resolved, refs entries,
         staleness handled, tolerable warnings, paste-time instructions.

FORCING ARTIFACT (pre-flight):
  Inline-quote-threshold list (### Inline quote threshold hits). Required. Empty table on zero hits.
```

## Exit Gates

**Allowed transitions (from formatting):**
- Formatting is the terminal stage. On successful step 8 report, the session typically returns to `[collaborative mode]` for review or next steps. No formal mode announcement is required for returning to collaborative unless {{USER}} directs otherwise.
- After the step 8 report, {{USER}} may invoke the `staged-reader-review` skill from `[collaborative mode]` on the rendered output: blind persona readers read it section by section, and the review lands as `<draft>.reader-review.md` per the skill's artifact schema. Recommended before a multi-section draft leaves {{USER}}'s hands. The review never self-triggers and does not block formatting; formatting stays the terminal pipeline stage.
- → `[editing mode]` when {{USER}} chooses to return to editing (inline quote hits, rendered-citation conversion, structural prose fix needed). Announce `Switching to [editing mode].`
- → `[research mode]` when step 2 stale-entry resolution requires re-fetch and re-verify for one or more entries. Announce `Switching to [research mode] (invoked from [formatting mode]).` Return to formatting after re-verify completes.

**Forbidden transitions:**
- Formatting does not self-advance. It emits output and reports; the next mode decision belongs to {{USER}}.
- → `[writing mode]` / `[refining mode]` / `[outlining mode]` / `[plan mode]` direct. These are upstream modes; reaching them from formatting implies a scope-level problem that routes through `[collaborative mode]` first.
- → `[finetuning mode]` direct. Prose substitution after formatting produces a sibling file that is out of sync with source prose. Return to `[editing mode]` for any prose change, then re-format.

## See also

- `CLAUDE.md §7.2` — explicit triggers (source of truth for "format this" / "render this" / "paste this" / "format for X").
- `CLAUDE.md §7.3` — stale-byline-at-format-time implicit trigger (procedure is this file, step 2 check 5).
- `CLAUDE.md §7.4` — mode-to-mode gate table; editing → formatting gate and formatting → (terminal) gate.
- `CLAUDE.md §7.5` — forcing artifact definitions: inline-quote-threshold list.
- `CLAUDE.md §7.6` — precedence rules; §4 verbatim governs block-quote handling inside formatting (delegate to pandoc+CSL; do not rewrite block-quoted spans).
- `CLAUDE.md §8` — citation log three-moment model; Moment 3 is this mode.
- `CLAUDE.md §11` — style pointer; `config/style.md` is the authority on CSL provenance, paste-target rules, and post-pandoc transforms.
- `docs/modes/editing.md` — predecessor mode; emits the four forcing artifacts that gate editing → formatting (revision report, §4 audit list, citation-payload re-read list, voice audit surface-scan report).
- `docs/modes/research.md` — target for stale-entry re-verify dispatches from step 2.
- `config/style.md §Style identity.CSL provenance.file` — CSL file path; verified at step 1.
- `config/style.md §Document layout.Block quotes` — threshold value read by pre-flight check 6.
- `config/style.md §Paste target expression rules.<target>` — pandoc flags, per-target file path rules, lua-filter, post-pandoc transforms, paste-time instructions.
- `~/.claude/citations/schema.md §Staleness` — staleness threshold applied in pre-flight check 5.
- `~/.claude/citations/csl-json-emitter.md` — emitter specification followed in step 4.
