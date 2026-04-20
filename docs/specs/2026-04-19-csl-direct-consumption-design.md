# CSL direct consumption: shift rendering ownership to pandoc + CSL

- **Date:** 2026-04-19
- **Status:** Shipped 2026-04-19 via PRs #1-5 (see `~/.claude/projects/-home-hayden-sourced/memory/project_csl_architecture_shift.md` for the full PR list).
- **Scope:** Pipeline rewrite + slim schema + retroactive migration of 5 shipped styles
- **Out of scope:** Tier-2 style rollout (captured under Follow-up)

## 1. Problem

The 5 shipped style files duplicate rendering rules that CSL files already encode:

| Style | Lines |
|-------|-------|
| apa7 | 192 |
| chicago17-ad | 406 |
| chicago17-nb | 350 |
| ieee | 286 |
| mla9 | 331 |

Each `style.md` carries §Inline citations (per-author-count rendering), §References list (entry formats per source type), §Numbering rules, §Footnote citations — all of which `pandoc --citeproc` reads from a CSL file and renders precisely. github.com/citation-style-language/styles hosts 10k+ community-maintained CSL files. The duplication creates a fabrication surface (model hallucinating a rule that conflicts with CSL) and multiplies per-style authoring time (~30-60 min under the current schema).

Today, only the `word` target flows through pandoc+CSL. `google-docs` and `plain-markdown` render directly from the citation log using hardcoded rules in `style.md`.

## 2. Decisions

### 2.1 Unified pipeline (all targets → pandoc + CSL)

All three paste targets (`word`, `google-docs`, `plain-markdown`) invoke `pandoc --citeproc --bibliography=<draft>.bib.json --csl=<csl>` for rendering. Pandoc becomes a hard dependency of the tool, not just of the `word` target.

### 2.2 Slim, curated schema (~60-80 lines per style)

`style.md` retains only material CSL does not encode: identity/provenance, document layout, paste-target expression rules, special tokens. Rendering-rule sections are removed.

### 2.3 CSL is vendored, not fetched

CSL files ship vendored under `templates/styles/<name>/`. `install.sh` never fetches at install time. Upstream refresh is a manual, audited action.

### 2.4 Block-quote threshold lives upstream

Prose-level block-quote conversion (e.g., MLA's 4-lines-of-prose rule) is an `[editing mode]` responsibility, not a `[formatting mode]` transform. `[formatting mode]` *verifies* threshold compliance in its pre-flight and halts if an inline over-threshold direct quote is still present in source prose — it does not rewrite prose. This preserves §8's invariant that source prose is never modified by the formatter.

### 2.5 Shape field is audit-only going forward

`§Style identity.Shape:` stays in the slim schema as audit metadata. §7 no longer branches on it. `install.sh` does not read it. Future tooling may; for now it is informational.

## 3. Slim `style.md` schema

Fixed-structure file, ~60-80 lines. Section names are addressable:

```
# Style: <name>

## Style identity
- Name:                   # full human-readable style name and edition
- Shape:                  # author-date | author-page | footnote | numeric-sequence | numeric-alpha (audit-only)
- In-text marker:         # parenthetical | bracket-number | superscript | footnote (audit-only)
- List heading:           # runtime heading text for the References section (References | Works Cited | Bibliography | Reference List)
- Authority:              # human-readable citation to the authoritative publication (style guide edition)
- Default for:            # typical disciplines / venues
- Source consulted:       # URLs + access dates (audit trail)
- CSL provenance:
  - file:                 # relative path under templates/styles/<name>/
  - source:               # github.com/citation-style-language/styles
  - fetched:              # YYYY-MM-DD
  - CSL title:            # full text of the CSL file's <title> element (cross-checked at install time)
- On-demand references:   # See §3.3 below. Most styles carry "(none)".
- Last reviewed:          # YYYY-MM-DD

## Document layout
Rules CSL does not encode. One subsection per layout category the style specifies:
- Fonts, sizes, line spacing
- Margins
- Heading hierarchy (markdown → destination interpretation)
- Title block
- Page numbering / running header
- Block quotes: threshold (if any) that [editing mode] must enforce upstream. The formatter verifies only.

## Paste target expression rules
Per-target post-pandoc behavior. One subsection per supported target.

### google-docs
- pandoc flags: --citeproc --wrap=none -t markdown-smart --reference-links=false [other]
- Paste-time instructions: [list of one-line strings prepended to the output file]
- Any additional post-pandoc transforms

### plain-markdown
- pandoc flags: --citeproc --wrap=preserve -t markdown [other]
- Transforms: typically none (pass-through)

### word
- pandoc flags: --citeproc [--reference-doc=<path>]
- reference.docx: relative path under templates/styles/<name>/ or "none — pandoc default layout as fallback"

## Special tokens
- [VERIFY: ...] and [UNSOURCED] are format-time blockers per CLAUDE.md §7. Most styles copy the standard block.
```

### 3.1 What is gone

Removed from style.md (now owned by CSL + pandoc):
- §Inline citations — per-author-count rendering rules
- §References list / §Reference list / §Bibliography — entry formats per source type, sort order
- §Footnote citations — full-form / short-form / ibid. rules
- §Numbering rules — assignment, resets, range-collapsing

### 3.2 What remains load-bearing

- `List heading:` — the formatter uses it to locate pandoc's rendered References section for target-specific post-processing (paste-time instruction strings).
- `CSL provenance → CSL title:` — cross-checked at install time against the CSL file's `<title>` element to catch shipped-wrong-file.
- `§Document layout` — not in CSL; needed for reference.docx authoring and for paste-time instruction strings.
- `§Paste target expression rules → pandoc flags` — authoritative for how pandoc is invoked per target.

### 3.3 On-demand references post-processing hook

`§Style identity.On-demand references` lists sidecar tables the formatter consults conditionally. Currently shipped: chicago17-ad's classical-abbreviations. The field specifies:
- Sidecar file path
- When the post-pandoc hook fires (which target, which shape of match)
- What the hook does (algorithm reference — see §6 of this spec)

Styles with no sidecar specify `(none)`.

## 4. New CLAUDE.md §7 [formatting mode] procedure

Structural rewrite. Shape-branch dispatch in the old step 3 is gone.

1. **Read slim `style.md` + citation log.** Halt if `style.md` is missing.
2. **Pre-flight.** Halt on any of: `[VERIFY: ...]` in source prose; `[UNSOURCED]` in source prose; rendered citation strings (e.g., `(Smith, 2010)`) in source prose; citation IDs that don't resolve against the log; stale `retrieved_at` per schema.md staleness (grouped prompt, as today); **inline direct quotes in source prose whose length exceeds the block-quote threshold declared in `§Document layout.Block quotes`** (surface and refuse; user returns to `[editing mode]` to resolve). The threshold check is an LLM judgment, same as other pre-flight checks that walk prose; it reads the style's threshold value (e.g., "40 words" / "4 lines") and flags inline spans wrapped in quotation marks that plausibly exceed it. Not a deterministic detector — just a heuristic halt. Verify `style.md.CSL provenance.file` exists on disk before step 5 — halt with a clear error if not.
3. **Pre-pandoc pass.** Copy source prose to `<draft>.pandoc.md`; collapse per-instance citation IDs (regex `<author>-<year>-\d{3}` → `<author>-<year>`) in the copy. Source `<draft>.md` is never modified.
4. **Emit CSL-JSON bibliography** from the citation log to `<draft>.bib.json`. One entry per unique source (dedupe by collapsed id). Mapping specified in §7 of this spec.
5. **Invoke pandoc.** Read flags from `style.md.§Paste target expression rules.<target>.pandoc flags`. Per-target `-o` routes output:
   - `word` → `<draft>.docx`
   - `google-docs` → `<draft>.gdocs.md`
   - `plain-markdown` → `<draft>.plain.md`
6. **Handle pandoc stderr and exit code.**
   - Non-zero exit: halt; surface stderr in full.
   - Exit 0 with stderr non-empty: classify warnings per §4.1 below. Blocking warnings halt; tolerable warnings pass through to the step-8 report.
7. **Post-pandoc pass.**
   - Apply `§Style identity.On-demand references` transforms (e.g., classical-abbreviations rewrite per §6 of this spec).
   - Prepend paste-time instruction strings from `§Paste target expression rules.<target>.Paste-time instructions` to the output file.
8. **Report.** One paragraph: source file, target, output sibling file, citations resolved, unique References entries, stale `retrieved_at` handled (re-fetched / accepted / gap), any blocking-halt detail, tolerable pandoc warnings surfaced, paste-time instructions.

### 4.1 Citeproc warning classification

Citeproc emits warnings to stderr without affecting exit code. Policy:

| Warning pattern | Classification | Action |
|-----------------|----------------|--------|
| "reference not found" / "citation [@id] not resolved" | Blocking | Halt before writing output |
| "missing field: type" on an entry in the emitted CSL-JSON | Blocking | Halt — CSL `type` drives rendering; fix the emitter inference, don't let the default fire silently |
| "missing field: DOI" / "missing field: URL" on applicable types | Tolerable | Surface in report |
| "missing field: publisher-place" / other optional fields | Tolerable | Surface in report |
| "unrecognized element" in CSL | Blocking | Halt — CSL file is suspect |

## 5. Classical-abbreviations post-pandoc rewrite algorithm

Applies only to styles whose `§Style identity.On-demand references` declares the hook (currently chicago17-ad, and by convention mla9 when a classical text is cited).

Algorithm:

1. Parse the post-pandoc output to locate rendered citation spans. Strategy:
   - Footnote-shape targets (NB): walk `[^N]:` body blocks at end of document; each block corresponds to one citation instance whose CSL-JSON entry is identifiable by the footnote's N-to-id map built in the pre-pandoc pass.
   - Parenthetical and numeric shapes: walk each Bibliography/References entry (one entry per CSL-JSON id). For each, the rendered string is the span to rewrite; the CSL-JSON entry is the one that produced that list position.
2. Read back to the CSL-JSON entry that produced the span (via the index/id in step 1) to check authorship and title metadata directly — do not rely on regex over rendered text.
3. If the CSL-JSON entry's `author[].family` matches an author in the sidecar's classical-author allowlist, apply the rewrite per the sidecar's format column (e.g., `Plato, *Republic*, 514a` → `Plato, *Rep.* 514a`). Else pass the span through unchanged.
4. The allowlist key is `author.family` *from CSL-JSON*, not a substring match on rendered text — this disambiguates classical "Plato" from a modern author who happens to share the surname.

The sidecar file format stays as today (author → abbreviated title mapping table). The slim style.md carries only a pointer and the hook specification.

## 6. CSL-JSON bibliography emission

New work, not previously implemented. Maps citation log entries (schema at `citations/schema.md`) to CSL-JSON objects.

| Log field | CSL-JSON field | Notes |
|-----------|----------------|-------|
| `id` (collapsed: `<author>-<year>`) | `id` | Key used by pandoc to resolve `@id` references. |
| `source.authors` (array of `"Lastname, First"` strings) | `author` (array of `{family, given}` objects) | Parser splits on first comma. Corporate authors (no comma) map to `{literal: "Name"}`. |
| `source.year` | `issued.date-parts: [[YEAR]]` | Integer. `n.d.` case: omit `issued` entirely; CSL handles absence. |
| `source.title` | `title` | String. |
| `source.publication` | Depends on inferred `type` — see below | Free-form in log; split heuristically. |
| `source.volume_issue_pages` | `volume`, `issue`, `page` | Parse the existing format `42(3), 12-34`. |
| `source.doi_or_url` | `DOI` (if `doi.org` URL), else `URL` | Strip `https://doi.org/` prefix when writing `DOI`. |

### 6.1 Source-type inference

The log has no `type` field today. Inference heuristic (deterministic, ordered):

1. If `source.volume_issue_pages` is non-empty AND `source.publication` does not start with `"Book"` or contain `"edited by"` → `article-journal`.
2. If `source.publication` starts with `"Book"` → `book`.
3. If `source.publication` contains `"edited by"` or begins with `"In "` (APA-style "In Editor (Ed.), Book" pattern) → `chapter`.
4. Else if `source.doi_or_url` is a URL (not a `doi.org` link) and none of the above match → `webpage`.
5. Else default to `article-journal` AND surface a tolerable-warning naming the entry and the fallback (so the user can fix the log entry rather than trusting a wrong type).

CSL type is load-bearing — an article-journal entry and a book entry render very differently. The heuristic is best-effort. Future work: add an optional `source.type` field to the log schema (non-breaking) to let the user override inference when the heuristic is wrong. Not in this spec.

### 6.2 When the emitter is implemented

As its own PR before any schema migration. See §8 migration plan.

## 7. Parity harness (golden-file)

**Not** a diff of "current renderer" vs. "new renderer." Current renderer is LLM-in-the-loop — non-deterministic — so an old-vs-new diff generates noise that swamps signal.

Instead: golden-file diff of pandoc+CSL output against a hand-authored expected output.

**Scope of what the harness tests.** The pandoc+CSL middle of §7 (steps 4-5), with deterministic inputs. It does NOT test the LLM-driven pre-flight (step 2), the LLM-driven threshold check, or the LLM-driven post-pandoc classical-abbreviations rewrite (step 7). Those are validated by the LLM reading this spec and applying it; that is how every other procedure in the tool is validated today.

Structure, under `tests/parity/<style>/`:
- `fixture.pandoc.md` — hand-authored collapsed markdown (output of what step 3 would produce on a representative fixture draft). Contains `[@<author>-<year>]`, `@<author>-<year>`, `[@id, p. N]`, etc., with mixed citation patterns: 1-author, 2-author, 3+ author, group, no-author, no-date, multi-citation, page-locator, (for footnote styles) a short-form re-cite, (for styles with sidecar) a classical citation.
- `fixture.bib.json` — hand-authored CSL-JSON bibliography. Reviewed once against the expected emitter output for the fixture's log.
- `golden/<target>.md` (or `golden/<target>.docx` for word) — hand-authored expected output, built from the style's authoritative reference (IEEE sample paper, Chicago NB sample paper, MLA Style Center example) and the style's CSL file.
- `run.sh` — invokes `pandoc --citeproc --bibliography=fixture.bib.json --csl=<csl> -o actual/<target>.<ext> fixture.pandoc.md` for each target, diffs `actual/` against `golden/`. Acceptance: empty diff, or diff within a tolerated-diff allowlist (trailing newline, `--wrap` line breaks — never ordering, never punctuation, never bibliography entry content). Use `-t markdown-citations` for the markdown targets — plain `-t markdown` round-trips citation syntax verbatim and suppresses the bibliography, producing a trivially-passing diff.

Run manually per style during migration PRs. Not a CI gate in this spec (CI would require pandoc + citeproc in the CI environment — separate decision).

**Emitter parity** (separate test.) The CSL-JSON emitter itself (§6) also needs per-source-type fixtures under `tests/emitter/`: a small citation log + a hand-authored expected `.bib.json`. Shipped in PR0.5.

## 8. Migration plan

Four PRs. Names are prefixes only; actual PR titles are the author's call.

### PR0.5 — CSL-JSON emitter
- Publish §6's log → CSL-JSON mapping as an addressable specification (new section in `citations/schema.md`, or new file under `citations/`). The tool's procedures are LLM-followed today; the emitter is a specification the LLM reads and applies during `[formatting mode]`, not a compiled module.
- Ship `tests/emitter/` fixtures covering each inferred source type (`article-journal`, `book`, `chapter`, `webpage`).
- Exercise the fallback-warning path in the fixtures.
- No schema changes (to style.md), no §7 changes yet. Existing `word`-target CSL-JSON emission follows the new specification starting from this PR.

### PR1 — Parity harness scaffolding
- `tests/parity/` directory, `run.sh` runner.
- One golden file per current shipped-style × target combination (15 goldens: 5 styles × 3 targets).
- Goldens authored against authoritative references.
- No schema changes, no §7 changes yet.

### PR2a — Prep: slim §Document layout + On-demand references across all 5 styles
- Pre-slim *only* the sections §7 needs to read during the transition: `§Document layout` (including new `Block quotes` subsection where applicable), `§Style identity.On-demand references`.
- Leaves old rendering-rule sections in place untouched.
- No §7 changes. After this PR, all 5 style.md files have the §Document layout and On-demand references shape the new §7 expects.

### PR2 — §7 rewrite + slim NB, IEEE, MLA9
- Rewrite CLAUDE.md §7 to the 8-step procedure in §4 of this spec.
- Install.sh gets pandoc version check (§9).
- Migrate chicago17-nb, ieee, mla9 fully to slim schema (slim identity + layout + paste-target + special-tokens only).
- Parity harness (PR1 + PR2a goldens) must pass for NB, IEEE, MLA on all targets before merge.
- Leaves apa7 and chicago17-ad carrying dead-weight old rendering-rule sections until PR3. §7 reads only the slim sections from all style.md files; it does not read §Inline citations / §References list / §Footnote citations / §Numbering rules from any style.md, including un-slimmed ones. The dead-weight sections are harmless during this window.
- Update STYLES.md to reflect the new schema and the dead-weight window.

**Pilot styles: Chicago 17 NB + IEEE + MLA 9.**
- NB exercises footnotes, short-form, classical-abbreviations sidecar.
- IEEE exercises numeric-sequence first-appearance assignment, range collapsing.
- MLA exercises author-page (locator in place of year) + block-quote threshold verification.

### PR3 — Slim apa7 and chicago17-ad
- Pure content work. Remove the dead-weight old rendering-rule sections from apa7.md and chicago17-ad.md. No §7 changes.
- Parity harness must pass for both on all targets.
- Update STYLES.md to remove the dead-weight-window note.

## 9. install.sh changes

1. **Pandoc pre-flight.** Before writing any project files:
   - Run `pandoc --version`, parse the first line's version token.
   - Require >= 3.1.
   - On missing or too-old: halt with per-OS install hints:
     - macOS: `brew install pandoc`
     - Debian/Ubuntu 22.04 or older (including WSL): Ubuntu apt ships 2.9.x; install from `https://github.com/jgm/pandoc/releases` or `cabal install pandoc`. Ubuntu 24.04+ apt is fine.
     - Windows: `winget install pandoc` or the installer from the releases page.
2. **CSL title cross-check.** For the style being installed:
   - Parse the shipped CSL file's root `<title>` element under `<info>`. Use `python3` (already required elsewhere in the tool) with `xml.etree.ElementTree`; do not grep.
   - Cross-check against `style.md.CSL provenance.CSL title:`. Mismatch halts with a message naming both strings.

## 10. Accepted residual risks

Called out explicitly so a future reader knows these were seen and deprioritized, not missed.

1. **Per-target pandoc flags duplicated across 5+ styles.** A pandoc CLI flag rename forces a multi-file sweep. Accepted; if duplication bites, a follow-up can introduce a shared snippet that style.md references.
2. **Vendored CSL drift from upstream.** CSL files in the upstream repo receive editorial updates that our vendored copies don't track. No auto-refresh. Accepted for now; a future `install.sh --refresh-csl` is a possibility.
3. **Source-type inference heuristic is best-effort.** A future `source.type` field in the log schema is the clean fix. Not in this spec.
4. **Pandoc becomes a hard dep for users who only paste into Google Docs.** User-visible regression from today's soft-fail-for-word-only story. Accepted; will be documented in release notes.
5. **Parity harness is manual-run, not CI-gated.** CI-gating requires pandoc in the CI environment — a separate decision. Manual-run is sufficient for the migration PRs.

## 11. Follow-up work (out of this spec)

Once the shift has landed (PR3 merged, all 5 shipped styles on the slim schema, §7 rewritten), the tier-2 roadmap becomes mechanical:

- Ship Vancouver, AMA, Harvard, ACM, ACS, Turabian 9, CSE, MHRA — one slim style.md + vendored CSL per style.
- Per-style effort target: ~15 minutes.
- No new architectural decisions required.

A separate spec for the tier-2 rollout is not planned; the work is a straightforward sequence of per-style PRs.
