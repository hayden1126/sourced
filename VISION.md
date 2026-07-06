# Vision

Sourced exists so one writer can put Claude in the loop of real academic writing and still defend every line. The bar is scholarship the writer can stand behind without rewriting it sentence by sentence: every citation verified, every paraphrase honest, every word in the writer's own voice. It is a private, professional-grade tool for real papers, not a product.

## Who it serves

Students and researchers producing defensible scholarship. Single-writer by design: one author, one voice, one accountable person per paper. Collaboration happens through artifacts (drafts, reviews, shared citation logs), never through real-time co-editing.

## Non-negotiables

Six values define the project. Everything sourced ships must extend at least one of them.

**Citation integrity.** A source is citable only if it is reliable for the field and its full text is accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated. No fabricated citations, quotes, page numbers, or DOIs, ever.

**Synthesis integrity.** A paraphrase must match the scope of what the source says: hedges, conditions, and populations survive the rewrite. Attribution chains are preserved, and inference steps are marked rather than hidden. The §4 audit enforces this at outline time and again at prose time.

**Voice preservation.** The prose stays the writer's. Per-author voice files calibrate tone, structure, and dimension; iron rules pass through every layer verbatim; a global inventory of AI-writing signatures (§10) is enforced at writing and editing time.

**Paraphrase default.** Direct quotes are reserved for wording that is itself the evidence. Quote-density checks flag over-quoted passages before they ship.

**Decoupled rendering.** Prose carries style-agnostic Pandoc citation IDs. A separate formatting stage renders them per style through pandoc and vendored CSL into a sibling file. Rendering never modifies source prose, and switching styles never means rewriting.

**Mode discipline.** The agent works in one announced mode at a time. Stage gates require explicit approval; silence is never an override.

## Enforcement principle

Rules are forced artifacts, not mental verbs. A rule that asks the model to "verify," "confirm," or "re-check" can be satisfied by silent assent, and silent assent is how fabrications ship. Every check must produce something inspectable: a log field, a list, a validator result, a report row. If a rule cannot name its artifact, it is not yet a rule. The 2026-07-03 audit ([docs/archive/audits/2026-07-03-mental-verb-audit.md](docs/archive/audits/2026-07-03-mental-verb-audit.md)) converted the bundle; issue [#45](https://github.com/hayden1126/sourced/issues/45) closed the last gap by forcing the §3(a) reliability judgment into `source.reliability_basis`.

## What sourced is not

- Not a reference manager. Zotero owns that model; a one-way export is the most sourced would add.
- Not a slide generator. Different medium, different rules.
- Not an argument mapper. The §4 audit catches inference drift, and the staged reader review catches whole-essay coherence, without graph tooling.
- Not a general grammar checker. The editing passes target ambiguity and AI-specific failure modes; a dedicated tool can do the rest.
- Not a plagiarism detector. The discipline here is preventive; post-hoc corpus comparison is Turnitin's job.
- Not a real-time collaboration tool. Single-writer by design, as above.
- Not a co-authoring tool. One author, one voice, one accountable person per paper; a blended voice makes voice preservation unfalsifiable.
- Not a writing tutor. Mode discipline already announces every mode entry and gate; a pedagogy layer serves a user class this private tool does not have.
- Not a distributed product. One writer runs it from a checkout; release engineering extends none of the six values.
- Not a legal-citation system. Bluebook is a structurally different citation model; if it ever matters, it is a standalone subproject.

Full rationale for each: [ROADMAP §Scope boundaries](./ROADMAP.md#scope-boundaries-declined-with-rationale).

## The bar for new work

Every open ROADMAP entry names what it serves: one of the six non-negotiables, or `ergonomics` for workflow comfort that extends none of them. Ergonomics work is allowed and useful, but it never outranks integrity work. An idea that serves neither gets declined with its rationale recorded in ROADMAP §Scope boundaries, so the line stays visible.
