# Roadmap

Forward-looking ideas for extending sourced's coverage: a ranked next queue, then a catalog organized by theme.

**Scope discipline.** [`VISION.md`](./VISION.md) defines the six non-negotiables and the bar new work must clear. Every open entry names what it serves; items ruled out as scope creep are flagged at the bottom so the boundary stays visible.

This file is different from [GitHub Issues](https://github.com/hayden1126/sourced/issues) (active bugs, parked decisions, observation items) and from `ARCHITECTURE.md` (describes what exists today). The Next queue below is the one ranked list across both trackers: queue rows may point at issues. The catalog is aspirational; no guarantee of delivery order.

## Next queue

What gets picked up next, ranked. A thread absent from this table is by definition not next. Reranking evidence: the 2026-07-04 paper session (the first full end-to-end real use) and the 2026-07-06 spike spec ([`docs/archive/specs/2026-07-06-staged-reader-review-and-voice-v2-design.md`](docs/archive/specs/2026-07-06-staged-reader-review-and-voice-v2-design.md), PR #68).

| # | Thread | Why now | Serves | Effort | Where |
|---|--------|---------|--------|--------|-------|
| 1 | Staged-reader-review bundle skill plus the review artifact schema | Spec merged; mostly codification of a field-proven prototype; immediately upgrades every future paper session and carries the #33 option-2 record | synthesis integrity | M | [#70](https://github.com/hayden1126/sourced/issues/70) |
| 2 | The `sourced voice` code arc: corpus index, then the blinded author-verification A/B | The fork decision landed in-repo; the A/B delivers the Track B fidelity score and stopping rule, and resolves Direct-API offload candidate 1 | voice preservation | M each | [#71](https://github.com/hayden1126/sourced/issues/71), [#72](https://github.com/hayden1126/sourced/issues/72) |
| 3 | `sourced doctor` deeper diagnostics | Field-evidenced: the 2026-07-03 `~/.claude` wipe and the #61 stale-version incident are exactly its use cases | ergonomics | S | Python CLI phase 5 tail, below |
| 4 | Slack between blocks: `extract-pdf-highlights`, after its containment-aware rewording | S-effort citation-integrity skill that collides with nothing above | citation integrity | S | Skills, below |

Sequenced behind the queue, not in it: [#73](https://github.com/hayden1126/sourced/issues/73) (passage retrieval) activates when a real paper session exists to validate against; [#74](https://github.com/hayden1126/sourced/issues/74) (extraction v2 intake) rides with the first extractor touch after #71.

2026-07-06 round shipped: the #51+#29 design spike (PR #68, #51 closed, follow-ups #70-#74), the citation-payload critic (PR #75, #29 closed), and the #34 consistency suite plus pass-count drift fix (PRs #69 and #75, #34 closed).

## Reading the entries

Each open entry carries four tags:

- **Effort**: `S` (< 1 day, mechanical) · `M` (1–3 days, new document type or mode) · `L` (1–2 weeks, structural change) · `XL` (multi-week, cross-cutting).
- **Status**: `open` · `in progress` · `scoping` · `declined`. Shipped work is compressed to a short note citing its PRs; the archived spec or plan carries the detail.
- **Serves**: which VISION.md non-negotiable the entry extends, or `ergonomics` for workflow comfort that extends none. Exactly one plain value, no hedging parentheticals.
- **Trigger**: when the entry becomes active work. `queued` (it holds a Next-queue row) · `act when <gate-time artifact>` (a named, inspectable event at a gate: a merge report line, a formatting-mode input, a review artifact) · `none yet` (a recorded idea with no known activation).

Triggers name gate-time artifacts because in-flow observation does not happen: the 2026-07-04 session's at-the-moment logging sections came back empty, while every real observation landed at a gate (merge, format, post-review). A trigger that cannot name its artifact will never fire. This is VISION.md's enforcement principle applied to the roadmap itself.

Maintenance rule: the Next queue changes in the same commit as the Status change or issue event that justifies it.

Items that require a schema change, new mode, or new gate are called out in the entry.

---

## Citation styles

Current shipped: `apa7`, `chicago17-ad`, `chicago17-nb`, `ieee`, `mla9` — all on the slim schema with vendored CSL files under `src/sourced/data/templates/styles/<name>/`. Each new style is a slim `src/sourced/data/templates/styles/<name>.md` file plus a `src/sourced/data/templates/styles/<name>/<csl>.csl` (optionally) a `reference-styled.docx` for the `word` target.

**Shipped styles (history).** MLA 9 (commit 3c870c6, author-page shape), Chicago 17 notes-bibliography (commit dbfa41f, footnote shape, CSL filename-pinned to the 17th-edition variant), IEEE (commit fba4a05, numeric-sequence shape). Each was the proof-of-concept for its `shape:` branch; the shape plumbing landed in commit 2ff3ab5.

### Tier-2 rollout (pinning table)
**Effort:** S each · **Status:** open · **Serves:** decoupled rendering · **Trigger:** act when a real paper needs a style outside the shipped five at the formatting gate.

Eight styles queued behind the shipped five. Per [`docs/archive/specs/2026-04-19-csl-direct-consumption-design.md`](docs/archive/specs/2026-04-19-csl-direct-consumption-design.md) §11, each targets ~15 minutes of per-style work now that the slim schema has shipped — a slim `style.md`, a vendored CSL, and parity fixtures. This table pre-resolves the CSL filename + authority-URL lookups so rollout PRs stay mechanical; edition-pinning caveats flag where upstream drift (e.g., CMOS 17 → 18) requires a suffixed-filename pin rather than the plain variant.

| Style | CSL filename | Authority URL | Edition pinning caveats |
|---|---|---|---|
| Vancouver | `dependent/vancouver-nlm.csl` | https://www.icmje.org/recommendations/ | Ships only as a dependent style; resolves to parent `nlm-citation-sequence.csl`. Safer pin: vendor the independent parent directly. ICMJE Recommendations are a living spec (no edition number). |
| AMA | `american-medical-association.csl` | https://academic.oup.com/amamanualofstyle | Pinned to 11th edition in `<title>`; upstream ships `american-medical-association-10th-edition.csl`, so precedent exists for suffixed variants. Plain file will likely drift on AMA 12 — hedge by forking to `american-medical-association-11th-edition.csl` on vendor. |
| Harvard | `harvard-cite-them-right.csl` | https://www.citethemrightonline.com/ | **High drift** — upstream title already rolled to "Cite Them Right 12th edition" while summary says 11th. Safer pin: `harvard-cite-them-right-11th-edition.csl`. `harvard1.csl` removed from upstream — do not use. |
| ACM | `association-for-computing-machinery.csl` | https://www.acm.org/publications/authors/reference-formatting | ACM Reference Format (numeric). Alternate: `acm-sig-proceedings.csl` (legacy). Living spec (Version 3 current); no version marker in filename so drift risk is implicit. Author-year submissions typically reuse Chicago. |
| ACS | `american-chemical-society.csl` | https://pubs.acs.org/doi/book/10.1021/acsguide | Pinned to "ACS Guide 2022 revision." ACS Guide is digital-first and continuously updated, so upstream may refresh in place. No edition-suffixed variants upstream — fork locally with year suffix if strict pinning needed. |
| Turabian 9 | `dependent/turabian-notes-bibliography.csl` | https://press.uchicago.edu/ucp/books/book/chicago/M/bo27847540.html | **High drift, two-layer.** Dependent on `chicago-notes-bibliography-subsequent-author-title-17th-edition.csl` — CMOS 17→18 drift propagates through. Turabian 10 already published, so upstream may re-point soon. **Pin both** dependent + parent. Alternate: `dependent/turabian-author-date.csl`. |
| CSE | `cse-citation-sequence.csl` | https://www.councilscienceeditors.org/scientific-style-and-format | Pinned to SSF 9th edition (citation-sequence). 8th-edition suffixed variants exist upstream, establishing drift precedent. Variants: `cse-name-year.csl`, `cse-citation-name.csl`. |
| MHRA | `mhra-notes.csl` | https://www.mhra.org.uk/style | Pinned to "MHRA Style Guide 4th edition (notes)." No edition-suffixed variants upstream, so future 5th ed would drift in place. Alternates: `mhra-author-date.csl`, `mhra-notes-subsequent-ibid.csl`, `mhra-shortened-notes.csl`. |

---

## Document types

Beyond "argumentative essay with sources." Each new type probably extends the mode system or adds a new target output.

### Annotated bibliography — phase 3
**Effort:** M · **Status:** phases 1+2 shipped 2026-04-20; phase 3 open · **Serves:** decoupled rendering · **Trigger:** act when a real annotated-bib project reaches [formatting mode].

Phases 1+2 shipped the `annotated-bib` project type end to end: schema extension (`citations/schema.md §Annotation`), brief template, `--type annotated-bib` install flag + `.sourced-project-type` marker, `[annotated-bib mode]` + mode adaptations. Design spec: [`docs/archive/specs/2026-04-20-annotated-bibliography-design.md`](docs/archive/specs/2026-04-20-annotated-bibliography-design.md).

**Phase 3 open.** Per-style paste-target variants (`apa7-annotated-bib`, `chicago17-ad-annotated-bib`, etc.) that render per-entry bibliography entries followed by annotation blocks via `pandoc --citeproc` + CSL. Open design question: inject annotations via CSL `note` field mapping plus custom CSL-JSON emitter path, or post-pandoc merge of rendered bibliography + log's `annotation` field by id match. Upstream citation-style-language/styles has `apa-annotated-bibliography.csl` for APA; other styles may need vendored variants. LaTeX `template.tex` adjustments per style for annotation-block layout. Test fixtures per style. Originally sized S; resized M after design work surfaced the project-type fork cost.

### Grant proposal
**Effort:** M · **Status:** open · **Serves:** ergonomics · **Trigger:** act when a real grant proposal project materializes.

Different section structure (Specific Aims, Background / Significance, Approach, Budget Justification). `[plan mode]` needs grant-aware templates; mode gates map per-section rather than global. Funder-specific formatting (NIH vs. NSF vs. private foundations) probably ships as templates-on-templates.

### Thesis / dissertation
**Effort:** L · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a real dissertation project materializes.

Multi-chapter, shared bibliography, cross-chapter citation management. Structural changes needed:

- Citation log scope: single shared log at project root rather than per-draft adjacent.
- `[refining mode]` cross-chapter audit: synthesis audit across chapters, not only within one draft.
- `[formatting mode]`: per-chapter rendering into a shared References list.
- Brief schema extension: chapter-level structure + dissertation-level framing.

Natural extension for long-form academic work. Worth writing once a real dissertation project materializes.

### Literature review / systematic review (with PRISMA)
**Effort:** L · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a real systematic-review project materializes.

Targets medical / social-science students who run systematic searches. Needs:

- PICO framing in the intake brief (Population, Intervention, Comparison, Outcomes).
- Inclusion/exclusion criteria tracking in `[research mode]`.
- PRISMA flowchart emission (records identified → screened → included, with counts and exclusion reasons).
- Source-finder extension: respect structured inclusion criteria rather than just the topic description.

Schema extension: citation log entries carry `screening_decision` and `exclusion_reason` fields when part of a systematic review.

### Book review / review essay
**Effort:** S · **Status:** open · **Serves:** ergonomics · **Trigger:** none yet.

Text-engagement heavy, often long-form quotation with extended analysis. Differs from an argumentative paper: primary source is a single book, not a literature spread. Probably a brief-template variant more than a new mode.

### Conference paper / short-form academic
**Effort:** S · **Status:** open · **Serves:** ergonomics · **Trigger:** none yet.

Tight word limits, specific formatting per conference. Ships as a brief-template variant + per-conference style files.

---

## Research modes

New modes that extend integrity discipline into adjacent workflows.

### Peer review mode
**Effort:** M · **Status:** open · **Serves:** synthesis integrity · **Trigger:** act when a real draft needs a rubric review once the primitive skill ([#70](https://github.com/hayden1126/sourced/issues/70)) ships.

Rubric-driven review of a complete draft. Reshaped 2026-07-06: the 2026-07-04 session discredited the original whole-draft single-reviewer shape. All three blind readers converged on defects (cumulative reader load, term-introduction order, argument strands left unjoined across sections) that whole-document review smooths over; only staged section-by-section reading caught them. Evidence on [#29](https://github.com/hayden1126/sourced/issues/29) and [#51](https://github.com/hayden1126/sourced/issues/51).

This entry is the rubric-persona consumer of the staged-reader-review primitive designed in the 2026-07-06 spec (§3, §9): personas parameterized by rubric axis (argument clarity, evidence adequacy, counterargument handling, methods rigor, writing quality), each running the staged sectional protocol, producing a durable numbered review. Differs from red-team as before: durable output artifact, runs against a complete draft, rubric rather than ad-hoc counterpoints.

### Revision mode
**Effort:** M · **Status:** open · **Serves:** synthesis integrity · **Trigger:** act when a real paper enters a revision round with reviewer comments in hand.

Respond to editor / reviewer comments with citation-linked revisions. Given a reviewer comments file plus the draft, produce a response letter + revised draft with change tracking. Integrity concern shifts from "paraphrase matches source" to "revision addresses the comment without introducing new scope creep."

Schema extension: revision-cycle log tracking which comment maps to which change.

Design note (2026-07-06): the natural input is the staged-reader-review primitive's per-section artifact, not freeform comment text; this entry is the primitive's third consumer, and the artifact schema it will consume now exists (spec §3.3, stable RR/RN ids, shipping with [#70](https://github.com/hayden1126/sourced/issues/70)). The 2026-07-04 session produced the first real review artifact (unanimous minor revision, deliberately unapplied).

### Primary-source research
**Effort:** M · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a real project cites an archival, interview, or field source.

Archives, interviews, fieldwork, oral histories. Different verification rules than peer-reviewed literature: full-text access is often physical (archive visit), not digital. Schema extension: `source_type: "archival" | "interview" | "field" | "literature"` with type-specific verification protocols. `[research mode]` delegates to different verification flows per type.

---

## Paste targets

Current shipped: `google-docs`, `plain-markdown`, `word`, `latex`. All 5 styles render uniformly via `pandoc --citeproc` + vendored CSL after the 2026-04-19 CSL direct-consumption migration; `latex` shipped 2026-04-20 (PR #11: per-style pandoc `template.tex`, engine-agnostic via `iftex`, user owns compilation).

### Figure and table handling
**Effort:** M · **Status:** open · **Serves:** decoupled rendering · **Trigger:** act when a real draft carries a figure into [formatting mode].

Currently all 4 paste targets pass markdown `![caption](path)` through pandoc's defaults: `\includegraphics{path}` for `latex`, embedded binary for `word`, the image path verbatim for `plain-markdown` and `google-docs`. No style file prescribes figure-specific rules; no parity fixture exercises a figure. First-class support would cover:

- **Resource path resolution.** A convention for a `figures/` directory at the project root plus a pandoc `--resource-path` hook so authors can use relative paths without hand-managing CWD. `[formatting mode]` composes the flag.
- **Cross-reference passthrough.** `{#fig:foo}` anchors rendering as `\label{fig:foo}` in LaTeX and durable anchors in markdown targets; `@fig:foo` references resolving uniformly across targets (pandoc's `pandoc-crossref` filter or its built-in equivalent is the likely mechanism).
- **Per-style figure conventions.** APA 7's "Figure N" numbering with italic captions; Chicago 17 (both variants) "Figure N." with sentence-case captions; IEEE "Fig. N." with specific placement rules. Codified in `style.md` `§Document layout`.
- **Parity coverage.** Each style's fixture gains a figure exercise; goldens verify caption placement, numbering, and cross-reference text.
- **Table handling.** Markdown table → LaTeX `tabular` / `longtable` (pandoc handles natively); Word / Google Docs through the same mechanism. Caption and label rules extend.

Schema likely unchanged (figures live in the prose, not the citation log). Main work is per-style layout authoring plus fixture extension.

Related: `arXiv-ready submission` (below) depends on this; figure-aware LaTeX output is the non-trivial piece of that follow-up.

### arXiv-ready submission
**Effort:** M · **Status:** open · **Serves:** decoupled rendering · **Trigger:** act when a real preprint targets arXiv; depends on figure and table handling landing first.

Full arXiv submission format (LaTeX + figures + bibliography). Builds on the LaTeX target but adds arXiv-specific quirks (figure handling, bibliography inclusion, preprint metadata).

### Obsidian / Roam / Logseq
**Effort:** M · **Status:** open · **Serves:** ergonomics · **Trigger:** none yet.

Knowledge-base integration. Citation IDs resolve to wiki-links in the destination tool rather than rendered author-year strings. Targets writers who use a PKM system alongside their academic writing.

---

## Skills

The `browser-reader-extract` pattern extends to several other extraction tasks. Each is a new directory under `src/sourced/data/skills/` with its own `SKILL.md`.

### `extract-pdf-highlights`
**Effort:** S · **Status:** open · **Serves:** citation integrity · **Trigger:** queued (Next queue row 4).

Pull the user's highlights and annotations from an annotated PDF into the citation log as paste-entry candidates. Solves the "I already read and annotated this" gap: the writer has done the reading and wants the quotes plus page numbers extracted without retyping. Prerequisite: `pdftotext` plus annotation parsing.

Reworded 2026-07-06 for the PR #63/#64 schema: a bare highlight yields an `exact_quote` with no context, which now trips the merge-time containment hard-fail or tempts placeholder context (the #58 failure). The skill must extract `surrounding_context` around each highlight, set `retrieval.access_mode`, and emit canonical page forms, not just quotes and page numbers.

### `extract-jstor`
**Effort:** S · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a merge report rejects a source the writer holds authorized JSTOR access to (post-#64, access failures surface as merge rejections).

JSTOR-specific version of `browser-reader-extract` for paywalled-but-authorized academic articles. Similar Chrome remote-debug + puppeteer-core pattern, different iframe/selector specifics. Given JSTOR's market share in humanities/social-science scholarship, high leverage per line.

### `extract-arxiv-latex`
**Effort:** S · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a math-heavy source loses formulas or code in PDF extraction.

Fetch arXiv LaTeX source rather than the rendered PDF. More reliable for math-heavy papers where PDF extraction loses formulas and code blocks. arXiv provides a public API; no browser automation needed.

### Additional browser readers
**Effort:** S each · **Status:** open · **Serves:** citation integrity · **Trigger:** act when an extraction session hits that reader.

Kindle Cloud Reader, Scribd, Archive.org's in-browser reader, HathiTrust. Each follows the pattern documented in `browser-reader-extract/SKILL.md`'s *Adding a new reader* section. Prioritize based on what real writers hit.

### `extract-transcript`
**Effort:** M · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a real interview or transcript source enters a project.

Clean interview transcripts (Zoom output, Otter.ai export, YouTube auto-caption) into quote-ready form with timestamps. Ties into the primary-source research mode above. Handles speaker diarization, timestamp normalization, and quote-extraction formatting.

### `extract-scholar-citations`
**Effort:** M · **Status:** open · **Serves:** ergonomics · **Trigger:** none yet.

Harvest citations from a Google Scholar author page or search results with automatic verification pass against the §3 rules. Different failure mode than current: Scholar produces citation metadata that may not match the accessible full text. Verification still required; Scholar is a discovery tool, not a verification shortcut. Retagged ergonomics 2026-07-06: discovery speed extends no integrity value, and the metadata-mismatch failure mode means any implementation must route through the PR #64 access-mode and containment gates.

---

## Framework extensions

Cross-cutting features that touch multiple modes.

**Shipped (history).** Per-project directory restructure, 2026-04-24 via PR #26: projects group into `config/`, `sources/`, `samples/`, `failures/`, with auto-migration on `sourced update` and invariant I11 guarding against flat-path regressions. Design spec: [`docs/archive/specs/2026-04-24-per-project-directory-restructure-design.md`](docs/archive/specs/2026-04-24-per-project-directory-restructure-design.md).

### Python CLI (`sourced`) — phase 5 tail
**Effort:** S–M each · **Status:** phases 1–4 shipped (PRs #19–#26); phase 5 open · **Serves:** ergonomics · **Trigger:** `sourced doctor` diagnostics queued (Next queue row 3); the remaining items act when the matching friction artifact lands.

The CLI decomposition shipped in four phases between 2026-04-22 and 2026-04-25: phase 1 ported `install.sh` to the Python CLI (PRs #19–#23), phase 2 extracted the CLAUDE.md dispatch manifest + externalized mode bodies (PR #24), phase 3 shipped the voice pipeline (PR #25), phase 4 the per-project directory restructure (PR #26). Design specs: [`docs/archive/specs/2026-04-21-sourced-cli-decomposition-design.md`](./docs/archive/specs/2026-04-21-sourced-cli-decomposition-design.md), [`docs/archive/specs/2026-04-23-claude-md-manifest-extraction-design.md`](./docs/archive/specs/2026-04-23-claude-md-manifest-extraction-design.md).

**Phase 5 items still open** (GitHub Actions CI shipped 2026-07-03 in the cleanup pass):

- `sourced doctor` deeper diagnostics: conda poisoning, PATH duplicates, orphan-file detection in `~/.claude/`. Queued: the 2026-07-03 `~/.claude` wipe and the #61 stale-version incident are its use cases, and a stale mirrored bundle silently runs old protocol text.
- `--format=json` structured output. Act when a consumer for machine-readable output exists.
- Shell completion (bash/zsh/fish). Act when tab-completion friction shows up in real use.
- User-defaults config migration from `~/.claude/sourced.config` to `~/.config/sourced/config.toml`. Act when the config surface grows past the current single file.

Phase 3 spike (mode bodies as skills, spec OQ6) is tracked in [issue #36](https://github.com/hayden1126/sourced/issues/36).

### Per-agent model selection via `sourced model`
**Effort:** S · **Status:** scoping · **Serves:** ergonomics · **Trigger:** none yet; the voice half lands as CLI config in the `sourced voice` arc (spec §6.3, the config-overlay shape this entry already favored), leaving only the non-voice agents for this entry.

Each shipped agent (`source-finder`, `voice-extractor`, `sourced-helper`, `prose-drafter`) currently has a hardcoded `model:` in its frontmatter. A `sourced model <agent> <model>` subcommand would let the user override the model per agent — e.g., switch `source-finder` from `sonnet` to `opus` for a more expensive but more thorough research run, or downgrade `sourced-helper` to `haiku` for cost.

**Architecture decision TBD.** Two candidate shapes:
1. **Mutate the mirrored copy** at `~/.claude/agents/<name>.md`. Simple to ship; user choices get clobbered by `sourced global-install` unless the CLI learns to detect-and-preserve the mutation.
2. **Config overlay** in `~/.claude/sourced.config` under an `[agents.<name>] model = "..."` section. Apply at mirror time so user choices survive bundle updates. Cleaner but adds a config surface.

Option 2 is the favored read; needs spec work before commit.

### Scoped subagents (private to `sourced` commands)
**Effort:** M · **Status:** scoping · **Serves:** mode discipline · **Trigger:** resolved by migration; the entry retires when `sourced voice extract` ships (spec §6.3: extraction's long-run home is the CLI, which removes the agent from the dispatcher's tree; no interim scoping work).

Some shipped agents (notably `voice-extractor`) shouldn't auto-trigger when Claude Code's agent dispatcher decides a "voice corpus extraction" sounds relevant to general academic-researcher work. They're meant to run only when explicitly invoked by a sourced subcommand (`sourced voice extract`, not yet shipped). Today every agent in `~/.claude/agents/` is fair game for the dispatcher.

**Architecture decision TBD.** Three candidate shapes:
1. **Relocate to `~/.claude/sourced/internal-prompts/`** outside the `agents/` discovery tree. `sourced voice extract` invokes Anthropic API directly with the prompt as system message. Bypasses the Claude Code dispatcher entirely; aligns with the "direct-API offload" entry below.
2. **Aggressive description-scoping** — rewrite the agent's `description:` to actively discourage auto-trigger ("ONLY when explicitly dispatched by a sourced voice subcommand — never proactively"). Easiest; least reliable.
3. **Wait for a Claude Code "private agent" mechanism** if one becomes available upstream.

Decision depends on whether the direct-API path lands first (option 1 falls out for free) or whether the aggressive-scoping route is good enough as a stopgap. Gate recorded 2026-07-06: the motivating agent is voice-extractor, and if the #51 spike forks voice extraction into a standalone tool, the agent leaves `~/.claude/agents/` and the auto-trigger problem dissolves by removal.

### `sourced-helper` agent — extensions
**Effort:** S–M · **Status:** scoping · **Serves:** ergonomics · **Trigger:** act when observed friction names one of the three extensions.

Phase 1 shipped `sourced-helper.md` — a `haiku` agent that knows the CLI surface, file layout, voices, styles, modes, and common gotchas, and answers questions read-only. Extensions worth scoping:

1. **`/sourced-help` slash-command skill** alongside the agent so users can summon it explicitly without relying on dispatcher heuristics.
2. **Doc reflection.** The agent's system prompt is self-contained today; phase 2 could have it `Read` shipped docs (`docs/MODES.md`, `docs/VOICES.md`, etc.) on demand for deeper questions, similar to how `claude-code-guide` reads its own knowledge base.
3. **Live introspection.** Wire the agent to surface `sourced check` output, current project state, etc. for diagnostic questions. Would need read-only project-state helpers in the CLI.

Decision TBD per item; ship in order of observed friction.

### Direct-API offload for deterministic workflows
**Effort:** L · **Status:** scoping · **Serves:** ergonomics · **Trigger:** candidate 1 resolved: `sourced voice ab` ([#72](https://github.com/hayden1126/sourced/issues/72)) is the direct-API path (spec §6.3); candidates 2 and 3 none yet.

Today `sourced` is a Python CLI for file mirroring + validation; the cognitive work happens inside Claude Code where `academic-researcher` dispatches subagents. Some workflows are well-defined enough to offload to direct Anthropic API calls inside the CLI — deterministic Python flow control, tuned prompts, cheaper models per step (`haiku` for boring extraction, `sonnet` for judgment, `opus` only when warranted). Candidates:

1. **Voice extraction from a corpus** — currently a `voice-extractor` subagent dispatched from inside Claude Code; could become `sourced voice extract <samples-dir> [--register academic]` that scripts the same prompt sequence with hardcoded conditionals.
2. **Citation parsing/validation** — verify a `<draft>.citations.json` log against source PDFs without spinning up an interactive agent session.
3. **Style validation** — the existing `validators/csl.py` already runs without the LLM; the `style.md` schema check could grow LLM-assisted suggestions for malformed entries.

**Architecture decision TBD.** The hybrid is the leading read: keep Claude Code as the substrate for interactive writing/research, use direct API for narrow workflows where flow control matters more than dispatcher creativity. Tradeoff: each migrated workflow needs careful prompt engineering plus golden tests, and the codebase grows a runtime dependency on the `anthropic` SDK. Don't rebuild Claude Code wholesale — a separate platform is months of effort that competes with `sourced` rather than complementing it.

Candidate 1 note (updated 2026-07-06 post-spike): resolved. The spike went in-repo, and [#72](https://github.com/hayden1126/sourced/issues/72) implements the A/B judges as direct API calls from the CLI with pinned prompts, which is this candidate in its corrected v2 shape (the original idea, scripting the v1 extractor, would have fossilized the decomposition failure #51 diagnosed).

### Cross-project citation reuse
**Effort:** L · **Status:** open · **Serves:** citation integrity · **Trigger:** act when a merge-time overlap check reports a DOI or `source_hash` shared with a prior project's citation log.

One writer, many papers, overlapping sources. A cross-project citation library (verify once, use many) reduces re-verification cost. `[research mode]` would check the shared library first before dispatching source-finders.

Schema extension: add `source_hash` (content-addressed or DOI-based) that dedupes across project log files. Staleness thresholds still apply per use; re-verification may still be needed for web sources.

Gate note (2026-07-06): the old mutual gate with the Verified-claims database was circular (the database promoted when this landed, then superseded it on landing, which plans a throwaway). Both entries now share one trigger: a second real project overlapping sources with an existing log. Reuse demand was structurally unobservable until now because cross-sex-empathy was the first project ever run; a one-line merge-time DOI/`source_hash` overlap report makes the trigger fire automatically. At trigger time, choose once between this dedup-lite version and the full database below.

### Verified-claims database (PageIndex-style retrieval)
**Effort:** XL · **Status:** scoping · **Serves:** citation integrity · **Trigger:** act when the cross-project overlap trigger fires and the brainstorming plus design-spec session this entry requires has run.

Persistent, tree-indexed database of verified claims and citations across all of one writer's projects. Each entry is a node carrying provenance (which session verified, when), the §4 audit results, and a position in the source's tree-of-contents index. `[research mode]` consults the local database first; only dispatches `source-finder` subagents for online search when (a) entries are stale per `~/.claude/citations/schema.md §Staleness` or (b) topical coverage is insufficient. Amortizes §3/§4 verification cost across writing sessions — the most expensive operation today is full-text verification, not citation rendering, so a write-once-read-many substrate compounds quickly across a writer's body of work.

Field note (2026-07-04 session): the cost premise held in practice; full-text verification was the expensive step, and #58 showed exactly what ships when it is shortcut (a snippet reached "verified"). The amortization premise has zero data points until a second overlapping project exists.

[**PageIndex**](https://github.com/VectifyAI/PageIndex) (vectorless, reasoning-based RAG; one tree index per document; LLM walks the tree at retrieval time; no embeddings, no chunking parameters) is the leading candidate for the per-source index layer. Three reasons it fits sourced's discipline where vector RAG and entity-graph approaches don't:

1. **Vectorless = auditable reasoning.** Retrieval is just an LLM tree-walk, the same shape `source-finder` already uses for relevance assessment. Vector similarity bypasses §4 with opaque scores; PageIndex's reasoning steps are inspectable.
2. **Tree structure preserves §4 context.** Cherry-pick (item 5) requires `surrounding_context` adjacent to `exact_quote`. A tree position keeps surroundings structurally close — no re-fetch needed to evaluate context.
3. **Reasoning-native = auditable retrieval contract.** Each tree-walk step can be logged in a per-claim `retrieval_trace` field, parallel to the existing `verification_trace`. The model's "why this node" reasoning becomes inspectable at audit time.

GraphRAG ruled out: multi-step entity-extraction pipelines, brittle on long-tail terminology, no fetch-coverage guarantee — too many places where the pipeline can silently miss a relevant claim. The tradeoff is wrong direction for a verification-led system.

**Open architecture questions** (need a brainstorming + design-spec session before any code):

- **Storage location.** `~/.claude/library/` per-user vs. shared-team substrate vs. project-local extension of `sources/`?
- **Schema.** Extend `sources/<draft>.citations.json` to carry tree-node refs (and sync log entries on first-use)? Or new format under `~/.claude/library/<source-hash>/{tree.json, claims.json}`? The two need to interoperate cleanly.
- **Trust boundary.** Verified-once-trust-forever, or re-verify on every reuse against `§Staleness` rules? Different answers for stable DOIs vs. web sources. Likely tiered.
- **Retrieval contract.** Silent (database substitutes for `source-finder` when coverage is sufficient) vs. surfaced ("Found N local entries covering claims X, Y, Z; want me to use them or re-verify online?"). Surfacing is the safer default; silent is the higher-leverage version once trust is calibrated.
- **Migration path.** How do existing per-project `citations.json` logs flow into the database? Bulk import + tree-build at the end of each project, or live writes during `[research mode]`?
- **Re-verification UX.** When does the writer get prompted vs. when is re-fetch automatic? Tied to autonomy level (§6) or always-confirm?

**Strong scope-discipline note.** The database must extend §3/§4 verification, not bypass it. "Claim X has 5 supporting citations in the database" is different from "those citations are still valid for the current draft." Staleness gates remain. The tree index is a retrieval substrate, not a trust substrate — every reuse runs against the same audit checks. If implemented carelessly, this entry becomes the failure mode §3 was built to prevent.

Touch points (provisional): `~/.claude/citations/schema.md` (claim-node and source-tree schema additions); `src/sourced/data/agents/source-finder.md` (database-first dispatch); the shipped `docs/modes/research.md` mode body (database lookup ahead of online search); new `sourced library` subcommand (build/list/prune/inspect); CLI integration with PageIndex (or a vendored subset thereof).

Related: `### Cross-project citation reuse` (above, smaller cousin — supersedes on landing); `### Direct-API offload for deterministic workflows` (database build/index workflows are candidates for direct-API automation).

### Babble-as-ideation across plan / research / refining
**Effort:** M · **Status:** open · **Serves:** ergonomics · **Trigger:** act when gate-time evidence from a real paper records premature convergence on one angle.

Today `[babble mode]` is collaborative-only — useful for warm-up but disconnected from the research lifecycle. Real planning involves divergent-then-convergent cycles; sourced currently skips divergence everywhere except the §6 brief's open-ended fields. Three insertion points worth supporting:

- **Pre-research (`babble → plan`).** "What angles, what hypotheses, what would falsify this?" Generates candidate framings before the brief converges on one.
- **Mid-research (`babble → research`).** "What counter-positions exist? What's missing in the source set?" Probes for gaps while finders are still mappable to new sub-topics.
- **Post-research (`babble → refining`).** "What synthesis comes out of this set of verified sources? What unexpected combinations?" Finds non-obvious linkages before the outline locks.

Schema. Each babble exit produces a structured artifact rather than dissolving into the next mode's context — either `<draft>.ideation.md` (sibling file) or a `## Ideation log` section in the brief. Outputs carry hypotheses, counter-positions, synthesis sketches with brief reasoning, plus a session timestamp. Outputs are not §10-gated (per current babble carve-out for ideation-flagged prose) but become inputs to subsequent modes' planning. Accumulates across the project lifecycle so post-research babble can see what pre-research babble surfaced and which strands survived contact with the source set.

Touch points. §7.4 transition table (new allowed transitions: `babble → plan`, `babble → research`, `babble → refining`); `docs/modes/babble.md` (currently inline in CLAUDE.md §7.7 — would externalize on this entry's first concrete body); plan/research/refining mode bodies' "See also" sections; brief template's optional `## Ideation log` section.

No schema change to the citation log; no new gate. The artifact format is the only new schema, and it's writer-facing markdown rather than runtime-parsed JSON.

### Claude Code Agent Teams integration
**Effort:** M–L · **Status:** open · **Serves:** ergonomics · **Trigger:** none yet. The 2026-07-06 spec evaluated the substrate for the primitive and did not adopt it (one-shot subagents with lockstep messaging and parent-owned consolidation; spec §3.5); angle 1 is the only open angle.

Claude Code's Agent Teams feature (`TeamCreate` / `TeamDelete` / `SendMessage` tool family) lets subagents coordinate as a structured team — shared context or explicit handoffs rather than one-shot dispatch-and-consolidate. Current `sourced` subagents (`source-finder`, `voice-extractor`) are one-shot utilities; the main agent dispatches, receives a report, and does the merging itself.

Three plausible integration angles worth scoping before committing to a design:

1. **Parallel source-finders with a coordinator.** `[research mode]` already dispatches multiple finders in parallel, but each returns an independent report and the main thread consolidates. A team-based version adds a coordinator that dedupes candidate sources across finders and surfaces disagreements (two finders flag the same source with different reliability assessments). Moves merge-logic out of the main agent.
2. **Editing-critic team for `[editing mode]`.** [Issue #29](https://github.com/hayden1126/sourced/issues/29) has been parked on whether refining/editing should use specialist subagents. Agent Teams would naturally implement the critic pattern there: grammar critic, voice-tells critic, citation-integrity critic, paraphrase critic, each reading the same draft, with reports flowing to the main agent for the actual prose revision.
3. **Peer-review mode as a team.** The `### Peer review mode` ROADMAP item envisions a rubric-driven reviewer. A team could split by rubric axis (argument clarity, evidence adequacy, counterargument handling, methods rigor, writing quality), each axis owned by a specialist team member with a structured report.

**Investigation-first.** The `Team*` tool schemas have not been loaded or tested yet (they are gated behind `ToolSearch` as deferred tools). Scope the API surface before any design — specifically: what state is shared across team members, what handoff semantics exist, whether teams persist across turns, and whether the per-session token economics work given that `source-finder` already burns tokens fast. If the integration story is weak, stay with one-shot subagents.

Re-scoped 2026-07-06: the 2026-07-04 staged review worked without team coordination, so the session evidence supports the consumers (the critics), not the mechanism. Angle 1 is the only standalone piece, and no merge-logic failure has been observed yet.

Related: [issue #29](https://github.com/hayden1126/sourced/issues/29) (editing-critic subagents); `### Peer review mode` above (team candidate); `### Revision mode` (team candidate).

### Translation workflow
**Effort:** L · **Status:** open · **Serves:** synthesis integrity · **Trigger:** act when a real project cites a non-English source.

Quoting from non-English sources with verbatim original + translation + translator attribution. Current §4 verbatim-quotation rule doesn't distinguish between "verbatim in the source language" and "verbatim in the paraphrased translation." Schema extension: add `original_language`, `translation`, `translator` fields. `[formatting mode]` handles display conventions per style (APA vs. Chicago differ on bracket notation for translations).

---

## Scope boundaries (declined, with rationale)

Flagged so the line stays visible; [`VISION.md §What sourced is not`](./VISION.md#what-sourced-is-not) carries the one-line versions. If any of these become urgent for a real writer, reopen for discussion.

### Zotero / Mendeley sync
**Rationale:** Users with reference managers already have one. sourced's citation log is first-class; sync would be bidirectional complexity that duplicates Zotero's own model. A one-way export (sourced → .bib or .ris) is reasonable; full sync is scope creep.

### Slide-deck generation
**Rationale:** Different medium, different rules. A paper's argument structure rarely maps one-to-one to a presentation. Better as an external tool that consumes sourced's markdown output.

### Formal argument mapping (Toulmin, argument graphs)
**Rationale:** Interesting but diverges from the citation-integrity focus; closer to philosophical-logic tooling than source verification. The whole-essay coherence concerns argument maps target (inference drift, stacked weak supports, unjoined strands) are owned by the staged reader review (issues [#29](https://github.com/hayden1126/sourced/issues/29), [#51](https://github.com/hayden1126/sourced/issues/51)): in the 2026-07-04 session, two argument strands stayed unjoined for three sections past every single-pass audit including §4, and the staged sectional reading caught them. The working remedy is reader simulation, not graph tooling. (Rationale updated 2026-07-06; the earlier version credited the §4 audit alone.)

### Real-time multi-user collaboration
**Rationale:** sourced is single-writer by design. Real-time editing is a fundamentally different model. Collaboration patterns sourced CAN support: send drafts to advisor with comment-round-trip (revision mode, above); shared citation log across a research group (cross-project citation reuse, above); peer review mode (above). These cover the collaboration cases without the real-time engineering.

### Grammar / style checker beyond §10 AI-tells and §9 voice
**Rationale:** Grammarly, LanguageTool, etc. do this well. sourced's grammar pass targets ambiguity and AI-specific failure modes, not general writing polish. Reader-level comprehension defects (cumulative load, term-introduction order) are not grammar polish: they stay inside sourced's line, owned by the staged-reader-review critics (issues #29, #51). Users wanting deeper grammar help should run a dedicated tool alongside.

### Plagiarism detection
**Rationale:** The §4 verbatim-quotation + paraphrase-default rules are designed to prevent the drift patterns that produce plagiarism in the first place. Post-hoc detection (comparing draft against a corpus) is a different problem solved by Turnitin and similar. sourced's discipline is preventive.

### Bluebook
**Rationale:** Declined 2026-07-06 (was an open XL entry under Citation styles). Legal citation is a structurally different model (case law, statutes, signals, short-form, supra, id.), and the entry itself judged it a standalone subproject rather than a shipped style. Zero demand from any real project. Reopen if a real legal-writing project materializes; the question to revisit is subproject-vs-style, not whether to vendor a CSL.

### Teaching mode
**Rationale:** Declined 2026-07-06 (was an open M entry under Framework extensions). sourced is a private, professional-grade tool, not a product; a pedagogy narration layer serves a student user class that does not exist here. Mode discipline already announces every mode entry and gate, which covers part of what the entry wanted. Reopen if a real student user materializes.

### Single-binary distribution (Go or Rust)
**Rationale:** Declined 2026-07-06 (was an open L entry under Framework extensions). Release channels, Homebrew formulae, and curl-pipe installers are distribution work for non-dev users who do not exist: the tool has one user, a developer running from a checkout. A behavior-identical rewrite extends none of the six values. Reopen if a non-dev writer is blocked by Python tooling.

### Voice-merging for co-authored papers
**Rationale:** Declined 2026-07-06 (was an open L entry under Framework extensions). VISION is explicit: one author, one voice, one accountable person per paper. A blended voice makes voice preservation unfalsifiable (whose voice survives?) and splits accountability, and the entry itself conceded real co-authors may not want it. Section-level collaboration already works through artifacts: separate projects, per-author voice files. Reopen only if real co-authors materialize with a concrete need, and design against whatever representation the #51 spike lands.

---

## Contributing an idea

Add an entry under the appropriate theme. Use this template:

```markdown
### <Feature name>
**Effort:** <S | M | L | XL> · **Status:** open · **Serves:** <citation integrity | synthesis integrity | voice preservation | paraphrase default | decoupled rendering | mode discipline | ergonomics> · **Trigger:** <queued | act when <gate-time artifact> | none yet>.

<2–4 sentences: what problem it solves, what use case it opens, how it extends the value it names.>

<If a schema change, new mode, or new gate is needed, call it out explicitly. Point at the closest existing mechanism.>
```

Two rules the template enforces. Serves names exactly one plain value: either the entry extends a non-negotiable or it is honest ergonomics, with no hedging parentheticals. A trigger must name a gate-time artifact (a merge report line, a formatting-mode input, a review artifact); entries proposing instrumentation must also name the gate where their evidence is collected, because in-flow observation does not happen.

Scope discipline matters more than queue position: an item that extends none of the six values and isn't honest ergonomics belongs in a scope-boundary note rather than the open list. The bar is defined in [`VISION.md §The bar for new work`](./VISION.md#the-bar-for-new-work).
