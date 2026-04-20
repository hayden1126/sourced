# Roadmap

Forward-looking ideas for extending sourced's coverage. Organized by theme and rough priority.

**Scope discipline.** The project's core value prop is citation integrity + voice preservation + mode discipline + paraphrase-default authoring with decoupled style rendering. Items on this list extend those values; items ruled out as scope creep are flagged at the bottom so the boundary stays visible. New items should clear that bar.

This file is different from the local `issues.md` (gitignored, tracks active bugs/decisions) and from `ARCHITECTURE.md` (describes what exists today). `ROADMAP.md` is aspirational; no guarantee of delivery order.

## Reading the entries

Each entry carries three tags:

- **Priority**: `next` (well-understood, ready to pick up) · `later` (depends on signal from real use) · `maybe` (surface area worth evaluating).
- **Effort**: `S` (< 1 day, mechanical) · `M` (1–3 days, new document type or mode) · `L` (1–2 weeks, structural change) · `XL` (multi-week, cross-cutting).
- **Status**: `open` · `in progress` · `shipped` · `declined`. Shipped items stay for historical context.

Items that require a schema change, new mode, or new gate are called out in the entry.

---

## Citation styles

Current shipped: `apa7`, `chicago17-ad`, `chicago17-nb`, `ieee`, `mla9` — all on the slim schema with vendored CSL files under `templates/styles/<name>/`. Each new style is a slim `templates/styles/<name>.md` file plus a `templates/styles/<name>/<csl>.csl` (optionally) a `reference-styled.docx` for the `word` target.

### MLA 9
**Priority:** next · **Effort:** M · **Status:** shipped (commit 3c870c6).

Modern Language Association 9th edition. Rounds out humanities coverage (literature, languages, cultural studies). Uses in-text `(Author Page)` with no year, full publication details in a Works Cited list. Author-page proof-of-concept for the `shape: author-page` branch added in commit 2ff3ab5. CSL shipped: `modern-language-association.csl`.

### Chicago 17 notes-bibliography
**Priority:** next · **Effort:** M · **Status:** shipped (commit dbfa41f).

Sibling to the already-shipped `chicago17-ad` (author-date). Notes-bibliography is the footnote-centric form preferred in history, theology, art history. Footnote proof-of-concept for the `shape: footnote` branch added in commit 2ff3ab5; exercises the §Footnote citations / §Bibliography section pair and the footnote-body array handling in CLAUDE.md §7 step 6. CSL shipped: `chicago-notes-bibliography-17th-edition.csl` (filename-pinned to the 17th-edition variant because the repo's unsuffixed file has migrated to CMOS 18).

### IEEE
**Priority:** next · **Effort:** M · **Status:** shipped (commit fba4a05).

Electrical / computer engineering. Numeric-sequence proof-of-concept for the `shape: numeric-sequence` branch added in commit 2ff3ab5. Numbers assigned by first appearance through source prose; References sorted by assigned number. CSL shipped: `ieee.csl` (version 11.29.2023, tracks IEEE 2023 editorial guidelines).

### Tier-2 rollout (pinning table)
**Priority:** later · **Effort:** S each · **Status:** open.

Eight styles queued behind the core three (MLA 9, Chicago 17 NB, IEEE). Per [`docs/archive/specs/2026-04-19-csl-direct-consumption-design.md`](docs/archive/specs/2026-04-19-csl-direct-consumption-design.md) §11, each targets ~15 minutes of per-style work now that the slim schema has shipped — a slim `style.md`, a vendored CSL, and parity fixtures. This table pre-resolves the CSL filename + authority-URL lookups so rollout PRs stay mechanical; edition-pinning caveats flag where upstream drift (e.g., CMOS 17 → 18) requires a suffixed-filename pin rather than the plain variant.

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

### Bluebook
**Priority:** maybe · **Effort:** XL · **Status:** open.

Legal writing. Massive spec (case law, statutes, regulations), different citation structure entirely (`v.`, signals, short-form, supra, id.). Probably a standalone subproject rather than a shipped style; worth scoping before committing.

---

## Document types

Beyond "argumentative essay with sources." Each new type probably extends the mode system or adds a new target output.

### Annotated bibliography
**Priority:** next · **Effort:** S · **Status:** open.

Output IS the citation log, formatted as per-entry blocks with paraphrase + analysis rather than an argumentative essay. Cheap to ship: new `[formatting mode]` target or a new mode that emits `<draft>.annotated.md` from the log directly. Schema needs a per-entry `annotation` field (new optional field, backward-compatible).

### Thesis / dissertation
**Priority:** later · **Effort:** L · **Status:** open.

Multi-chapter, shared bibliography, cross-chapter citation management. Structural changes needed:

- Citation log scope: single shared log at project root rather than per-draft adjacent.
- `[refining mode]` cross-chapter audit: synthesis audit across chapters, not only within one draft.
- `[formatting mode]`: per-chapter rendering into a shared References list.
- Brief schema extension: chapter-level structure + dissertation-level framing.

Natural extension for long-form academic work. Worth writing once a real dissertation project materializes.

### Literature review / systematic review (with PRISMA)
**Priority:** later · **Effort:** L · **Status:** open.

Targets medical / social-science students who run systematic searches. Needs:

- PICO framing in the intake brief (Population, Intervention, Comparison, Outcomes).
- Inclusion/exclusion criteria tracking in `[research mode]`.
- PRISMA flowchart emission (records identified → screened → included, with counts and exclusion reasons).
- Source-finder extension: respect structured inclusion criteria rather than just the topic description.

Schema extension: citation log entries carry `screening_decision` and `exclusion_reason` fields when part of a systematic review.

### Grant proposal
**Priority:** later · **Effort:** M · **Status:** open.

Different section structure (Specific Aims, Background / Significance, Approach, Budget Justification). `[plan mode]` needs grant-aware templates; mode gates map per-section rather than global. Funder-specific formatting (NIH vs. NSF vs. private foundations) probably ships as templates-on-templates.

### Book review / review essay
**Priority:** maybe · **Effort:** S · **Status:** open.

Text-engagement heavy, often long-form quotation with extended analysis. Differs from an argumentative paper: primary source is a single book, not a literature spread. Probably a brief-template variant more than a new mode.

### Conference paper / short-form academic
**Priority:** maybe · **Effort:** S · **Status:** open.

Tight word limits, specific formatting per conference. Ships as a brief-template variant + per-conference style files.

---

## Research modes

New modes that extend integrity discipline into adjacent workflows.

### Peer review mode
**Priority:** next · **Effort:** M · **Status:** open.

Agent simulates a structured peer reviewer (not ad-hoc red-team). Produces a numbered review with categories: argument clarity, evidence adequacy, counterargument handling, methods rigor, writing quality. Could be a new mode (`[peer review mode]`) or a structured extension of `[red team mode]`.

Differs from red-team: produces a durable output artifact (the review itself), runs against a complete draft rather than during the writing loop, uses a rubric rather than ad-hoc counterpoints. Good for self-review before submitting, or for reviewing someone else's paper.

### Revision mode
**Priority:** later · **Effort:** M · **Status:** open.

Respond to editor / reviewer comments with citation-linked revisions. Given a reviewer comments file plus the draft, produce a response letter + revised draft with change tracking. Integrity concern shifts from "paraphrase matches source" to "revision addresses the comment without introducing new scope creep."

Schema extension: revision-cycle log tracking which comment maps to which change.

### Primary-source research
**Priority:** later · **Effort:** M · **Status:** open.

Archives, interviews, fieldwork, oral histories. Different verification rules than peer-reviewed literature: full-text access is often physical (archive visit), not digital. Schema extension: `source_type: "archival" | "interview" | "field" | "literature"` with type-specific verification protocols. `[research mode]` delegates to different verification flows per type.

---

## Paste targets

Current shipped: `google-docs`, `plain-markdown`, `word`, `latex` (all 5 styles — APA 7, Chicago 17 author-date, Chicago 17 notes-bibliography, IEEE, MLA 9 — render uniformly via `pandoc --citeproc` + vendored CSL after the 2026-04-19 CSL direct-consumption migration; `latex` added 2026-04-20).

### LaTeX
**Priority:** next · **Effort:** M · **Status:** shipped 2026-04-20.

STEM / math / physics. Uses the existing pandoc + citeproc + CSL pipeline (no biblatex, no natbib) plus a per-style pandoc `template.tex` that sets document class, geometry, and the `CSLReferences` environment. `IEEEtran` for the IEEE style; `article` for APA, Chicago (both variants), and MLA. Engine-agnostic via `iftex` guard — compiles under `pdflatex`, `xelatex`, and `lualatex`. Shipped artifact is a standalone `.tex` file; user owns compilation. Figure/table handling stays at pandoc defaults; arXiv-ready packaging is a follow-up item.

### Figure and table handling
**Priority:** later · **Effort:** M · **Status:** open.

Currently all 4 paste targets pass markdown `![caption](path)` through pandoc's defaults: `\includegraphics{path}` for `latex`, embedded binary for `word`, the image path verbatim for `plain-markdown` and `google-docs`. No style file prescribes figure-specific rules; no parity fixture exercises a figure. First-class support would cover:

- **Resource path resolution.** A convention for a `figures/` directory at the project root plus a pandoc `--resource-path` hook so authors can use relative paths without hand-managing CWD. `[formatting mode]` composes the flag.
- **Cross-reference passthrough.** `{#fig:foo}` anchors rendering as `\label{fig:foo}` in LaTeX and durable anchors in markdown targets; `@fig:foo` references resolving uniformly across targets (pandoc's `pandoc-crossref` filter or its built-in equivalent is the likely mechanism).
- **Per-style figure conventions.** APA 7's "Figure N" numbering with italic captions; Chicago 17 (both variants) "Figure N." with sentence-case captions; IEEE "Fig. N." with specific placement rules. Codified in `style.md` `§Document layout`.
- **Parity coverage.** Each style's fixture gains a figure exercise; goldens verify caption placement, numbering, and cross-reference text.
- **Table handling.** Markdown table → LaTeX `tabular` / `longtable` (pandoc handles natively); Word / Google Docs through the same mechanism. Caption and label rules extend.

Schema likely unchanged (figures live in the prose, not the citation log). Main work is per-style layout authoring plus fixture extension.

Related: `arXiv-ready submission` (below) depends on this; figure-aware LaTeX output is the non-trivial piece of that follow-up.

### arXiv-ready submission
**Priority:** later · **Effort:** M · **Status:** open.

Full arXiv submission format (LaTeX + figures + bibliography). Builds on the LaTeX target but adds arXiv-specific quirks (figure handling, bibliography inclusion, preprint metadata).

### Obsidian / Roam / Logseq
**Priority:** maybe · **Effort:** M · **Status:** open.

Knowledge-base integration. Citation IDs resolve to wiki-links in the destination tool rather than rendered author-year strings. Targets writers who use a PKM system alongside their academic writing.

---

## Skills

The `browser-reader-extract` pattern extends to several other extraction tasks. Each is a new directory under `skills/` with its own `SKILL.md`.

### `extract-pdf-highlights`
**Priority:** next · **Effort:** S · **Status:** open.

Pull the user's highlights and annotations from an annotated PDF into the citation log as paste-entry candidates. Solves the "I already read and annotated this" gap: writer has done the reading, wants the quotes + page numbers extracted into citation log entries without retyping. Prerequisite: `pdftotext` + annotation parsing.

### `extract-jstor`
**Priority:** next · **Effort:** S · **Status:** open.

JSTOR-specific version of `browser-reader-extract` for paywalled-but-authorized academic articles. Similar Chrome remote-debug + puppeteer-core pattern, different iframe/selector specifics. Given JSTOR's market share in humanities/social-science scholarship, high leverage per line.

### `extract-arxiv-latex`
**Priority:** later · **Effort:** S · **Status:** open.

Fetch arXiv LaTeX source rather than the rendered PDF. More reliable for math-heavy papers where PDF extraction loses formulas and code blocks. arXiv provides a public API; no browser automation needed.

### `extract-transcript`
**Priority:** later · **Effort:** M · **Status:** open.

Clean interview transcripts (Zoom output, Otter.ai export, YouTube auto-caption) into quote-ready form with timestamps. Ties into the primary-source research mode above. Handles speaker diarization, timestamp normalization, and quote-extraction formatting.

### Additional browser readers
**Priority:** later · **Effort:** S each · **Status:** open.

Kindle Cloud Reader, Scribd, Archive.org's in-browser reader, HathiTrust. Each follows the pattern documented in `browser-reader-extract/SKILL.md`'s *Adding a new reader* section. Prioritize based on what real writers hit.

### `extract-scholar-citations`
**Priority:** maybe · **Effort:** M · **Status:** open.

Harvest citations from a Google Scholar author page or search results with automatic verification pass against the §3 rules. Different failure mode than current: Scholar produces citation metadata that may not match the accessible full text. Verification still required; Scholar is a discovery tool, not a verification shortcut.

---

## Framework extensions

Cross-cutting features that touch multiple modes.

### Cross-project citation reuse
**Priority:** later · **Effort:** L · **Status:** open.

One writer, many papers, overlapping sources. A cross-project citation library (verify once, use many) reduces re-verification cost. `[research mode]` would check the shared library first before dispatching source-finders.

Schema extension: add `source_hash` (content-addressed or DOI-based) that dedupes across project log files. Staleness thresholds still apply per use; re-verification may still be needed for web sources.

### Voice-merging for co-authored papers
**Priority:** maybe · **Effort:** L · **Status:** open.

Papers with multiple authors sometimes need blended voices: author A writes section 1, author B writes section 2, both voices coexist. Current voice system is per-project-single-voice. Options: section-level voice assignment in the brief, or a "blended" voice type that doesn't strictly enforce either author's rules. Unclear whether real co-authors actually want this vs. simply alternating paragraph-by-paragraph.

### Translation workflow
**Priority:** maybe · **Effort:** L · **Status:** open.

Quoting from non-English sources with verbatim original + translation + translator attribution. Current §4 verbatim-quotation rule doesn't distinguish between "verbatim in the source language" and "verbatim in the paraphrased translation." Schema extension: add `original_language`, `translation`, `translator` fields. `[formatting mode]` handles display conventions per style (APA vs. Chicago differ on bracket notation for translations).

### Teaching mode
**Priority:** maybe · **Effort:** M · **Status:** open.

Agent explains why it's making each decision for a student learning the academic-writing process. Current agent executes mode-gate discipline silently; a teaching variant would surface "I'm auto-triggering research mode because claim X needs a source" explanations at every mode entry. Opt-in verbosity.

### Claude Code Agent Teams integration
**Priority:** maybe · **Effort:** M–L · **Status:** open.

Claude Code's Agent Teams feature (`TeamCreate` / `TeamDelete` / `SendMessage` tool family) lets subagents coordinate as a structured team — shared context or explicit handoffs rather than one-shot dispatch-and-consolidate. Current `sourced` subagents (`source-finder`, `voice-extractor`) are one-shot utilities; the main agent dispatches, receives a report, and does the merging itself.

Three plausible integration angles worth scoping before committing to a design:

1. **Parallel source-finders with a coordinator.** `[research mode]` already dispatches multiple finders in parallel, but each returns an independent report and the main thread consolidates. A team-based version adds a coordinator that dedupes candidate sources across finders and surfaces disagreements (two finders flag the same source with different reliability assessments). Moves merge-logic out of the main agent.
2. **Editing-critic team for `[editing mode]`.** `issues.md #5` has been parked on whether refining/editing should use specialist subagents. Agent Teams would naturally implement the critic pattern there: grammar critic, voice-tells critic, citation-integrity critic, paraphrase critic, each reading the same draft, with reports flowing to the main agent for the actual prose revision.
3. **Peer-review mode as a team.** The `### Peer review mode` ROADMAP item envisions a rubric-driven reviewer. A team could split by rubric axis (argument clarity, evidence adequacy, counterargument handling, methods rigor, writing quality), each axis owned by a specialist team member with a structured report.

**Investigation-first.** The `Team*` tool schemas have not been loaded or tested yet (they are gated behind `ToolSearch` as deferred tools). Scope the API surface before any design — specifically: what state is shared across team members, what handoff semantics exist, whether teams persist across turns, and whether the per-session token economics work given that `source-finder` already burns tokens fast. If the integration story is weak, stay with one-shot subagents.

Related: `issues.md #5` (editing-critic subagents, parked); `### Peer review mode` above (team candidate); `### Revision mode` (team candidate).

---

## Scope boundaries (declined, with rationale)

Flagged so the line stays visible. If any of these become urgent for a real writer, reopen for discussion.

### Zotero / Mendeley sync
**Rationale:** Users with reference managers already have one. sourced's citation log is first-class; sync would be bidirectional complexity that duplicates Zotero's own model. A one-way export (sourced → .bib or .ris) is reasonable; full sync is scope creep.

### Slide-deck generation
**Rationale:** Different medium, different rules. A paper's argument structure rarely maps one-to-one to a presentation. Better as an external tool that consumes sourced's markdown output.

### Formal argument mapping (Toulmin, argument graphs)
**Rationale:** Interesting but diverges from citation integrity focus. Closer to philosophical-logic tooling than source-verification. The `[refining mode]` §4 audit already catches many of the concerns formal argument maps address (inference drift, stacked weak supports), without the graph-building overhead.

### Real-time multi-user collaboration
**Rationale:** sourced is single-writer by design. Real-time editing is a fundamentally different model. Collaboration patterns sourced CAN support: send drafts to advisor with comment-round-trip (revision mode, above); shared citation log across a research group (cross-project citation reuse, above); peer review mode (above). These cover the collaboration cases without the real-time engineering.

### Grammar / style checker beyond §10 AI-tells and §9 voice
**Rationale:** Grammarly, LanguageTool, etc. do this well. sourced's grammar pass (editing mode pass 4) targets ambiguity and AI-specific failure modes, not general writing polish. Users wanting deeper grammar help should run a dedicated tool alongside.

### Plagiarism detection
**Rationale:** The §4 verbatim-quotation + paraphrase-default rules are designed to prevent the drift patterns that produce plagiarism in the first place. Post-hoc detection (comparing draft against a corpus) is a different problem solved by Turnitin and similar. sourced's discipline is preventive.

---

## Contributing an idea

Add an entry under the appropriate theme. Use this template:

```markdown
### <Feature name>
**Priority:** <next | later | maybe> · **Effort:** <S | M | L | XL> · **Status:** open.

<2–4 sentences: what problem it solves, what use case it opens, how it extends the core value prop.>

<If a schema change, new mode, or new gate is needed, call it out explicitly. Point at the closest existing mechanism.>
```

Scope discipline matters more than priority: an item that doesn't extend citation integrity / voice preservation / mode discipline / decoupled rendering probably belongs in a scope-boundary note rather than the open list.
