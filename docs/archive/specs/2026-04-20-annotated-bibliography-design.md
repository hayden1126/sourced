# Annotated bibliography: ship a new research deliverable project type

- **Date:** 2026-04-20
- **Status:** Shipped 2026-04-20. Phase 1+2 complete (project-type fork, brief template, `[annotated-bib mode]`, per-style render variants, editing-mode subset); phase 3 open per `ROADMAP.md`.
- **Scope:** Add `annotated-bib` as a `sourced` project type. New brief template, new `[annotated-bib mode]`, one new optional schema field, per-style paste-target variants for all 5 shipped styles (apa7, chicago17-ad, chicago17-nb, mla9, ieee).
- **Out of scope:** PRISMA screening stages, per-source quality-scoring rubrics beyond the 4-beat evaluation, cross-project citation dedup, alternative output media (slide decks, interactive web). Systematic-review functionality belongs to a separate ROADMAP entry.

## 1. Problem

`sourced` today ships one deliverable shape: the argumentative essay. Users who want an annotated bibliography — as a standalone class assignment, a pre-writing literature survey, or an advisor-facing reading report — have no supported path. Hand-assembling annotations from a filled citation log throws away the verification discipline, the style rendering, and the mode-gate sequence that are the project's point.

The ROADMAP entry under *Document types → Annotated bibliography* (`next · S · open`) has carried this since early in the repo's life. The `S` sizing assumed a thin formatting variant on top of an existing essay's log. Design work clarified that the feature actually needs a project-type fork: the input is a topic (not an essay's sub-topic decomposition), the output is reader-facing (not a working aid for a draft), and topic-specificity enforcement is load-bearing — a vague topic produces a useless bib. Resized `M`.

Brainstorming (2026-04-20) converged on a hybrid between a new project type and a new paste target: fork the brief and mode graph where the deliverables genuinely differ, reuse the research + CSL-render pipeline everywhere else.

## 2. Decisions

### 2.1 Shape: new project type, not new mode inside the essay flow

Essay projects flow `plan → outlining → refining → writing → editing → formatting`. A bib project does not need `outlining / refining / writing` — there is no prose argument to structure, stress-test, or write. Running an `[annotated-bib mode]` alongside `[writing mode]` in one project (option B from brainstorming) violates the "one cognitive mode active at a time" invariant from `templates/CLAUDE.md §7` and splits two deliverables across one working directory.

A project-type fork at install time is cleaner: `install.sh --brief my_bib --type annotated-bib` writes a different brief template and marks the project as bib-type. Essay installs are unaffected. One project, one deliverable shape.

### 2.2 Reuse, don't fork, the research+format pipeline

Source-finder dispatch, the citation log schema, the CSL direct-consumption rendering pipeline (shipped 2026-04-19), and the §3/§4 verification discipline apply identically to bib projects. What the pipeline renders and what the research feeds changes per-type; the pipeline itself doesn't.

Per-type changes: brief template; mode graph (collapses four modes into one); per-entry annotation prompt; per-style render variant at the formatting stage. Unchanged: source-finder's contract, schema (except one new optional field), §3 verification rules, dispatch/shard/merge protocol, `pandoc --citeproc` rendering machinery, per-style CSL files.

### 2.3 Schema extension: one optional field

Add one optional string field to citation log entries, documented in `citations/schema.md` under `## Additions` as a schema-defined optional field:

```json
"annotation": "150–250 word style-agnostic prose populated during [annotated-bib mode] phase 3. Absent on essay-project entries."
```

Backward-compatible with existing essay-project logs. Essay-mode code never reads or populates it; bib-mode code requires it on every entry before compilation.

### 2.4 Mode graph

Essay project (unchanged):

```
collaborative → plan → outlining → refining → writing → editing → formatting
```

Annotated-bib project:

```
collaborative → plan → research → annotated-bib → editing → formatting
```

- `[plan mode]` in a bib project runs **facet decomposition** (3–6 angles of the one topic) instead of argument mapping. Strategy-propose-and-gate structure unchanged; what gets planned differs.
- `[research mode]` runs structurally unchanged: parallel source-finder dispatch, shard merge, reject/verified reporting. Dispatch template differs in two fields (§2.5 phase 2).
- `[annotated-bib mode]` (new) writes per-entry annotations and compiles the draft.
- `[editing mode]` runs a subset of its eight passes (§2.6).
- `[formatting mode for <style>-annotated-bib]` renders (§2.8).

`[outlining / refining / writing]` are unreachable in bib projects. `templates/CLAUDE.md §7` gets a brief project-type preamble naming which modes apply.

### 2.5 Mode responsibilities across the bib flow

Each mode in the bib flow owns a distinct slice. Describing them together here so the gate transitions are visible at a glance; the official definitions land in `templates/CLAUDE.md §7`.

**`[plan mode]` in bib projects.** Two responsibilities in order.

*Topic specificity gate.* Before any dispatch, read the brief's *Topic* and *Scope statement* sections and test: could a stranger, given only those sections, predict with better than coin-flip accuracy whether a specific candidate source qualifies?

Failure modes that trigger the gate: one-word topics (`climate change`, `AI ethics`, `postcolonialism`); scope statements that are synonyms of the topic; in-scope bullets that name whole fields rather than cuts through them; absent out-of-scope bullets.

On gate failure, do not auto-narrow. Surface 3–5 candidate narrowings drawn from the topic's actual sub-literature, each with a one-line rationale identifying which facet of the user's topic it lives in. User picks one, proposes an alternative, or rewrites scope. Gate re-fires if the next round is still too broad. Ungated advance is a protocol violation. Silence ≠ approval on this gate; "looks fine" is approval.

*Facet decomposition.* With topic narrow and scope clear, decompose into 3–6 facets — distinct angles of the one topic, not supporting arguments (there is no argument). Example: topic "workplace burnout in early-career trainee physicians (2015–2025)" → facets (a) prevalence and measurement, (b) structural drivers, (c) interventions and evaluation, (d) demographic variation, (e) comparison to analogous professions. Facets are exhaustive within scope, mutually distinct; overlap is normal, double-counting is not.

Present the facet list with per-facet rationale and wait. User may edit, merge, or add facets. Gate: do not advance to `[research mode]` until facets are approved.

**`[research mode]` differences in bib projects.** Structurally unchanged (parallel source-finder dispatch, shard/merge per `citations/schema.md §Parallel dispatch shards`). Dispatch template differs from essay dispatch in two fields:

- `Supporting claim or question:` → `Facet coverage: <what this facet of the topic encompasses>`
- `Paper context:` carries the scope statement verbatim from the brief, so finders reject out-of-scope candidates on the same criteria the user wrote

Per-facet entry target: `brief.target_entries / facet_count`, rounded up, bounded by the brief's per-facet cap. One finder per facet; all facets dispatched in parallel.

Merge report surfaces entries per facet, gaps, rejections worth naming. User decides whether to dispatch a second round (different facet cut, broader date range, paste-manual paywalled strong candidates) or advance.

**`[annotated-bib mode]` (new).** Two responsibilities in order.

*Per-entry annotation.* For each entry in the merged log (verification status `verified` or `partial`), generate a 150–250 word annotation using the prompt in §2.7. Annotations are grounded only in the log entry's fields plus the brief's topic and scope — no source re-read. Write to the entry's `annotation` field. §3 verification is inherited from logging time; annotation does not re-open it.

*Draft compile.* Emit `<draft>.md` as one block per entry:

```
### [@<id>]

<annotation prose>
```

Order: alphabetical by first-author surname (default) or thematic-by-facet (optional). For thematic order, facet headers (`##`) sit above each block group.

**Handoff gate to `[editing mode]`.** "Compilation complete, {N} entries annotated. Ready to edit, or more compilation work?" Gate discipline per existing modes; silence ≠ approval.

### 2.6 Editing mode subset for bib projects

The eight-pass `[editing mode]` audit in `templates/CLAUDE.md §7` assumes prose. In bib projects, three passes apply differently:

| Pass | Apply to bib? | Reason |
|---|---|---|
| 1. ID validation | yes | `[@id]` tokens still need to resolve |
| 2. §4 citation audit | yes (adapted) | scope/attribution/byline/inference per annotation; synthesis only where an annotation cross-references another entry |
| 3. Partial-entry recheck | yes | unchanged |
| 4. Grammar | yes | applies to annotation prose |
| 5. Proofreading | yes | proper-noun, paste-artifact, and punctuation lists apply per annotation |
| 6. §10 AI-tell | yes | Never-list applies to annotation prose |
| 7. Quote-density | no | paragraph-level metric; annotations are blocks |
| 8. Voice audit | partial | §9 iron rules apply; paragraph-flow and pacing metrics across annotations do not |

`templates/CLAUDE.md §7` gets a bib-project addendum naming which passes apply. No new passes added.

### 2.7 Per-entry annotation prompt

Four-beat prompt, grounded only in the log entry's fields plus the brief's topic and scope sections. Target 150–250 words.

1. **Paraphrased summary (40–60%)** — what the source argues, shows, or demonstrates, drawn from `context_description` + `surrounding_context`. Preserve every qualifier in `exact_quote` (hedges, conditions, populations, periods). Preserve second-order attribution ("Smith, reviewing Jones (2010), argues …"). Do not extend past what the fields support; flag gaps rather than filling.
2. **Relevance to the bibliography's topic (20–30%)** — which in-scope bullet does this speak to, which boundary case does it illuminate. Specific, not generic. Thin relevance stated as thin; padding is a failure mode.
3. **Location of key quotable material (10–20%)** — `location` field verbatim ("p. 42", "§3.2", "chapter 4, pp. 118–124"). Quote at most one short phrase from `exact_quote` if a specific formulation is the reason to cite this source; otherwise paraphrase. Do not quote `surrounding_context` — that field is verification-only.
4. **Brief evaluation (10–20%)** — one strength, one limit relative to this bibliography's topic. Strengths drawable from fields: methodological clarity in `context_description`, scope breadth shown in `exact_quote`. Don't invent evaluative claims beyond what fields support; pick a different dimension or omit with flag.

Constraints:

- §10 applies. Never-list absolute; density list budgeted per annotation (not cumulative across the bib).
- `voice.md` iron rules apply; cadence and flow rules don't translate to per-entry blocks.
- Style-agnostic prose. Do not render `(Smith, 2010)` inline. Cross-references to other entries use `[@id]`.
- `verification_status: "partial"` entries: relevance and evaluation beats must stay inside the `exact_quote` span or be dropped with flag.
- No fabricated page numbers, section references, or quotes.

When a required beat cannot be grounded, stop and surface the gap to {{USER}}. Name the insufficient field and what the entry would need. Do not fill from outside the log.

### 2.8 Formatting mode variants per style

Each shipped style gets one new paste-target variant. Five new targets total:

| Style | New target | Bibliography entry shape | Annotation block shape |
|---|---|---|---|
| apa7 | `apa7-annotated-bib` | APA 7th-ed References entry, hanging-indent | indented paragraph(s) below entry, flush with hanging-indent start |
| chicago17-ad | `chicago17-ad-annotated-bib` | Chicago author-date Reference List entry | indented paragraph(s) below entry |
| chicago17-nb | `chicago17-nb-annotated-bib` | Chicago Bibliography entry (not note form) | indented paragraph(s) below entry |
| mla9 | `mla9-annotated-bib` | MLA Works Cited entry | flush-left paragraph block below entry |
| ieee | `ieee-annotated-bib` | Bracket-numbered references entry | indented paragraph(s) below entry |

Pandoc recipe per target reuses the existing `pandoc --citeproc --csl <csl> --bibliography <draft>.csl.json` machinery (per the CSL direct-consumption spec). The annotation text lives in the citation log's `annotation` field; the paste-target rendering reads it per entry and emits it as a paragraph block following the rendered bibliography entry. For the LaTeX targets, each style's existing `template.tex` gets a minor `CSLReferences` adjustment so the annotation block sits immediately below each rendered entry.

Each `templates/styles/<name>/style.md` gets a new `### <name>-annotated-bib` subsection under `## Paste target expression rules` carrying the pandoc recipe and the annotation-block layout rule for that style.

### 2.9 Install-time changes

- `install.sh --type annotated-bib` renders `templates/brief.template.annotated-bib.md` instead of the essay brief and writes a `.sourced-project-type` marker file at project root with value `annotated-bib`.
- `templates/CLAUDE.md §7` gets a project-type preamble that reads the marker and declares which modes are reachable.
- Existing essay installs are unaffected; absence of the marker = essay project (legacy-safe).
- `--type` defaults to `essay` when omitted.

## 3. Brief template fields

File: `templates/brief.template.annotated-bib.md`.

Each field includes one-line "good example" and "too-vague example" inline callouts so users self-correct at intake before the mode's specificity gate fires. Field list:

- **Assignment** — verbatim prompt, rubric, or `self-directed`
- **Topic** — one-sentence statement + one-sentence why-for-this-reader
- **Scope statement** — in-scope bullets (2–4, concrete: populations, periods, methods, frames, geographies), out-of-scope bullets (2–4, tempting-but-wrong territory named explicitly), boundary cases (edge cases to flag rather than silently include/exclude)
- **Source-count target** — target entries (typical 8–20), floor (mode warns below), per-facet cap (max entries from any one facet; `none` acceptable)
- **Source constraints** — date range, source types accepted (default excludes trade press, blogs, dissertations unless named), disciplines in bounds, sources to avoid, languages (default English-only)
- **Annotation shape** — length per entry (default 150–250), required beats (default: all four from §2.7), voice source (`default` or `voice.md`)
- **Deadline** — date or `none`
- **Autonomy level** — low / medium / high, per `templates/CLAUDE.md §6`

The brief omits fields that don't apply to bibs: no thesis, no research question, no length-in-words (derived from entries × per-entry length), no outline structure.

## 4. Ease-of-use discipline

The approval constraint was "easy and intuitive for users." Decisions serving that constraint:

- **Project type at install time.** One flag (`--type annotated-bib`); no post-install editing to switch shape.
- **Brief fields carry inline examples.** Every specificity-sensitive field has a "good vs too-vague" callout so users self-correct during intake, not after the mode's gate fires.
- **Specificity gate suggests, doesn't reject.** 3–5 candidate narrowings with rationale — the user has something concrete to react to, not just "be more specific."
- **Facet list arrives with rationale.** Not a raw bulleted list the user must evaluate cold.
- **Annotation defaults.** Length, beats, and voice all have sensible defaults; user only touches them if they want to diverge.
- **Single rendered file.** `[formatting mode for <style>-annotated-bib]` emits the deliverable ready to submit; no manual assembly or paste-target assembly.

## 5. Scope boundary (ROADMAP cross-references)

Explicitly out of scope, routed to other ROADMAP items:

- **PRISMA flow, screening stages, inclusion/exclusion scoring.** Belongs to *Research modes → Literature review / systematic review (with PRISMA)*. A systematic review is a different deliverable with different integrity requirements; the annotated bib is the lower-ceremony cousin.
- **Quality-scoring rubrics beyond the 4-beat evaluation.** Not required for the standard annotated-bib deliverable; avoid inventing a rubric the feature doesn't need.
- **Cross-project citation dedup.** Belongs to *Framework extensions → Cross-project citation reuse*.
- **Alternative output media** (slide decks, interactive web). Not a document-type extension.

ROADMAP `### Annotated bibliography` entry to be updated from `S` to `M` on ship; design spec linked from the entry.

## 6. Implementation plan (pending)

Next step per the brainstorming skill: invoke `writing-plans` to produce a phase-by-phase implementation plan covering:

- Schema extension (add `annotation` to `citations/schema.md §Additions`)
- Brief template file + `install.sh --type` handling + `.sourced-project-type` marker
- New `[annotated-bib mode]` definition in `templates/CLAUDE.md §7`, with the project-type preamble naming reachable modes
- Editing mode subset rules in `templates/CLAUDE.md §7`
- Per-style render variant rules in each `templates/styles/<name>/style.md`
- Per-style LaTeX `template.tex` adjustments for the annotation-block layout
- Test fixtures: one complete annotated-bib sample project end-to-end per style (5 fixtures)
- Documentation: `docs/MODES.md` updates, `docs/STYLES.md` paste-target table updates, ROADMAP entry resize and cross-reference to this spec
