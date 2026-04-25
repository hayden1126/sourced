# [annotated-bib mode]

## Overview

Annotated-bib mode turns a merged citation log into a formatted annotated bibliography — per-entry annotations first, then a compiled draft. The failure mode this mode exists to prevent is **field-overreach**: annotation prose that extends past what the log entry's fields support, invents evaluation, or softens the partial-entry constraint into a paraphrase that carries unverified inference. Every beat is grounded in existing fields; a gap is surfaced to {{USER}}, not filled.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "annotate this" / "write the annotations" / "compile the bib" (manifest §7.2).
- **{{USER}}-gated handoff from `[research mode]`.** {{USER}} confirms the merged log is ready to annotate. Do not enter on your own judgment that research is complete.

**Do not enter when:**
- The project type is not `annotated-bib`. Attempting entry from an essay-type project is a gate violation (manifest §7.4 forbidden transitions); use `[writing mode]` there.
- The merged log is not ready — outstanding source-finder shards, pending validation failures, or {{USER}} has not confirmed the log is complete. Return to `[research mode]`.
- `config/voice.md`, `config/style.md`, or the brief at `config/<name>.brief.md` is missing. Stop and ask {{USER}} to run `sourced update` or `sourced switch voice/style <name>` as appropriate; do not annotate with guessed rules.

## Iron Law

```
┌─────────────────────────────────────────────────────────────┐
│  NO ANNOTATION WITHOUT LOG-FIELD GROUNDING                  │
│  NO PHASE 2 WITHOUT PHASE 1 COMPLETE (ALL IN-SCOPE ENTRIES) │
└─────────────────────────────────────────────────────────────┘
```

An annotation beat that cannot be grounded in the log entry's fields is either flagged to {{USER}} (naming the insufficient field) or dropped. Inference, extrapolation, and impression-based evaluation are fabrication regardless of how confident they read. Phase 2 (draft compile) does not begin until every in-scope entry has a completed annotation; partial-compile is not a valid state.

## Steps

### Entry

1. **Announce entry.** First output of the turn: `Switching to [annotated-bib mode].`

2. **Read `config/voice.md` in full.** The iron rules govern annotation prose. Do not operate from memory. If `config/voice.md` is missing, stop and ask {{USER}} to run `sourced switch voice <name>`.

3. **Read `config/style.md` in full.** Required for Phase 2 ordering and file-naming conventions. If missing, stop and ask {{USER}} to run `sourced switch style <name>`.

4. **Read the brief at `config/<name>.brief.md`.** The brief's *Topic* statement and *Scope statement* sub-sections (in-scope / out-of-scope / boundary cases) are the only context used to assess relevance in the annotation's relevance beat. If the brief is missing, stop and ask {{USER}} — do not proceed without it.

5. **Load the citation log** (`sources/<draft>.citations.json`). Identify every entry with `verification_status: "verified"` or `"partial"`. These are the in-scope entries for Phase 1.

### Phase 1: per-entry annotation

For each in-scope log entry, in turn:

6. **Generate the annotation.** Write 150–250 words, four beats in order. Percentages below are approximate word-budget allocations; ±5% drift per beat is acceptable when a source demands more summary or thinner evaluation:

   a. **Paraphrased summary (~50%).** What the source argues, shows, or demonstrates. Draw from `context_description` and `surrounding_context`. Preserve every qualifier in `exact_quote` — hedges, conditions, populations, periods. Preserve second-order attribution ("Smith, reviewing Jones, argues…"). Do not extend past what the fields contain; flag gaps with the field name rather than filling.

   b. **Relevance (~25%).** Which in-scope bullet or boundary case the source speaks to, in specific terms. Generic relevance ("this source addresses the topic") is a failure mode. State thin relevance as thin.

   c. **Location (~15%).** `location` verbatim as it appears in the log entry ("p. 42", "§3.2", "chapter 4, pp. 118–124"). At most one short phrase from `exact_quote` if the specific formulation is the reason to cite this source; otherwise paraphrase. Do not quote `surrounding_context` — that field is verification-only and not part of the annotation record.

   d. **Evaluation (~10%).** One strength and one limit, relative to the bibliography's topic. Draw only from fields the entry carries. Do not invent evaluative claims the fields don't support; pick a different dimension or omit and flag to {{USER}}.

7. **Apply constraints:**
   - **§10 applies absolutely.** The never-list is absolute on annotation prose. The density budget is per-annotation, not cumulative across the bib.
   - **Voice iron rules apply.** `config/voice.md ## Iron rules` govern every annotation. §9 sentence connectedness, paragraph flow, information pacing, and building-arguments rules do NOT apply — annotations are per-entry blocks, not multi-paragraph prose. The boundary mirrors `[editing mode]`'s pass 8 reduction in annotated-bib projects.
   - **Style-agnostic.** Do not render author-year strings (`(Smith, 2010)`) or bracket numbers inside annotation prose. Cross-references to other entries use `[@id]`; `[formatting mode]` resolves them per the active style at rendering time.
   - **Partial-entry constraint.** For `verification_status: "partial"` entries, the relevance and evaluation beats must stay inside the `exact_quote` span. Any beat that cannot stay within the span is dropped with a flag to {{USER}} naming the constraint.
   - **No fabrication.** Never invent page numbers, section references, or quoted phrases. When a required beat cannot be grounded in the log entry's fields, stop and surface the gap to {{USER}} with the insufficient field named.

8. **Write the annotation to the entry's `annotation` field** in the citation log. Do not hold it in memory; write it to the log before moving to the next entry. §3 verification is inherited from logging time; annotation does not re-open sources or dispatch new research.

9. **Repeat steps 6–8 for every in-scope entry.** If {{USER}} flags an annotation during Phase 1, complete that flag before continuing to the next entry.

### Phase 2: draft compile

Phase 2 begins only when every in-scope log entry has a completed annotation in the log.

10. **Determine ordering.** Check the brief for a specified ordering preference. If not specified, ask {{USER}} before proceeding: alphabetical by first-author surname (default) or thematic-by-facet. Wait for explicit direction.

11. **Emit `<draft>.md`** as one block per entry. File structure:

    ```
    # <title from the brief, or "Annotated Bibliography">

    ### [@<id>]

    <annotation prose from the log's annotation field>

    ### [@<next-id>]

    <annotation prose>
    ```

    For thematic-by-facet ordering, add facet headers (`##`) above each block group before the first `### [@<id>]` entry in that group.

12. **`### [@<id>]` heading format.** Carry the bare Pandoc citation token only. Do not render the references-list form inline — `[formatting mode]` resolves that at Moment 3. Writing a rendered reference string here defeats the style-agnostic discipline the Pandoc-ID system provides.

### Handoff to `[editing mode]`

13. **Present completion.** When every in-scope entry is annotated and the draft compiles cleanly, present to {{USER}}: "Compilation complete, {N} entries annotated. Ready to edit, or more compilation work?" Silence is not approval.

14. **On flagged entry:** if {{USER}} flags an annotation for rework, re-enter Phase 1 for the flagged entries only. Re-announce: `Switching to [annotated-bib mode]. Reworking {N} flagged entries.`

15. **Announce handoff.** On explicit {{USER}} readiness: `Switching to [editing mode].`

## Red Flags

If you catch yourself thinking any of the following, stop:

- *"The fields don't quite support this evaluation, but it's clearly true about the source."* — No. Evaluation is grounded in fields only. "Clearly true" is an inference; inferences are fabrication here.
- *"The partial-entry constraint is too strict for this beat — I'll extend slightly past `exact_quote`."* — No. The constraint is absolute. Drop the beat and flag it.
- *"I'll draft the compile before all annotations are done — I can fill in the remaining few after."* — No. Phase 2 requires Phase 1 complete. The Iron Law is not a suggested sequence.
- *"The relevance beat is obvious — one sentence like 'this source is relevant to the topic' is fine."* — No. Generic relevance is a failure mode. Name the specific in-scope bullet or boundary case.
- *"I don't need to re-read `config/voice.md` — I've applied the iron rules before."* — Re-read on every entry. Memory of prior sessions drifts; the file is the authority.
- *"The `surrounding_context` field has useful material I can quote in the location beat."* — No. `surrounding_context` is verification-only. Quote only from `exact_quote`, and at most one short phrase.
- *"I'm doing this in an essay project but the user asked for it."* — That's a gate violation. Surface it and redirect to `[writing mode]`.
- *"Evaluation dimension X isn't supported by fields — I'll silently swap to dimension Y."* — No. Step 6d (pick different dimension or omit with flag) requires the substitution be surfaced to {{USER}}. Silent swap changes what the annotation claims about the source; it must be flagged.
- *"Research mode just returned a complete merged log — the next logical step is annotating."* — No. Annotated-bib entry requires EXPLICIT "merged log is ready to annotate" from {{USER}}; logical-next-step inference is a gate violation. Ask: "Research complete. Ready to annotate, or more research?"

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "The brief's scope statement doesn't explicitly name this source's topic — I'll infer it's in scope." | Inference is out of scope. Ask {{USER}} whether the source is in scope before annotating it. An out-of-scope entry annotated is wasted work if it doesn't compile. |
| "The evaluation beat needs one more line — I'll pull from the abstract I remember reading." | You are annotating from fields, not from memory of the source. If the fields don't support a second evaluation line, the beat is done. "I remember reading" is a fabrication path. |
| "150 words is too short for a complex source — I'll go to 280." | 150–250 is the shape from `~/.claude/citations/schema.md §Annotation`. Exceeding it is a constraint violation. Compress the beats within budget; care beyond budget is indiscipline. |
| "Summary is 70% but annotation is under 250 words, so it's fine." | ±5% drift is per-beat, not a pool to reallocate. Any beat outside its corridor is a beat violation regardless of total word count. Compress within-beat; do not cross-fund from other beats. |
| "I'll render the reference inline under the `### [@<id>]` heading — easier for {{USER}} to read during review." | Inline rendering defeats the style-agnostic discipline. The `### [@<id>]` heading IS the reference token; `[formatting mode]` renders the final form. Don't pre-render. |
| "The location field says 'p. 42' — I'll add surrounding context so {{USER}} knows where to look." | Reproduce `location` verbatim. Any wording change is a transcription error. If `location` is too sparse, that's a log entry gap — surface it to {{USER}}, don't paper over it. |
| "The summary beat is pulling from `surrounding_context` — that's what the field is there for." | `surrounding_context` is a verification-only field; it provides evidence that `exact_quote` was not cherry-picked. Draw the summary from `context_description` and `surrounding_context` for phrasing cues, but quote only from `exact_quote`. When in doubt, paraphrase rather than quote, and never reproduce `surrounding_context` as annotation prose. |
| "Ordering doesn't matter much — I'll go alphabetical without asking." | If the brief specifies ordering, follow it. If it doesn't, ask before compiling. The ordering choice affects how the bibliography reads thematically; it's {{USER}}'s call. |
| "I'll skip the handoff question and switch directly to `[editing mode]` once the draft is done." | The handoff question is the gate. Silence is not approval; the question forces engagement and gives {{USER}} the option to request more compilation work before editing begins. |
| "{{USER}} said 'good' after the compile — I'll advance to editing." | Affirmative-but-non-explicit is silence. The handoff gate phrase is "ready to edit" or equivalent explicit readiness ("ready to edit", "start editing", "yes, edit"). A casual "good" or "ok" or "thanks" after the compile does not close the gate — re-surface the compile count and ask again. |

## Quick Reference

```
ENTRY:     Switching to [annotated-bib mode].
           Read config/voice.md (iron rules only). Read config/style.md. Read config/<name>.brief.md.
           Load citation log. Identify in-scope entries (verified + partial).

PHASE 1 (per entry, in turn):
  Generate annotation (150–250 words):
    a. Paraphrased summary (~50%)  — from context_description + surrounding_context
                                     Preserve qualifiers in exact_quote. No extension past fields.
    b. Relevance (~25%)            — name specific in-scope bullet or boundary case
    c. Location (~15%)             — location field verbatim + at most one phrase from exact_quote
    d. Evaluation (~10%)           — one strength + one limit, from fields only
  Constraints:
    §10 absolute (per-annotation budget)
    config/voice.md iron rules apply; §9 (connectedness, flow, pacing) does NOT apply
    style-agnostic: [@id] not (Author, Year)
    partial entries: relevance + evaluation within exact_quote span only
    no fabrication: gap → flag to {{USER}} with field name
  Write annotation to log entry's annotation field before next entry.

PHASE 2 (after all entries annotated):
  Ask ordering if brief doesn't specify: alphabetical or thematic-by-facet.
  Emit <draft>.md:
    ### [@<id>] heading (bare Pandoc token — do not render reference inline)
    annotation prose from log
    (for thematic: ## facet header above each group)

HANDOFF:   "Compilation complete, {N} entries annotated. Ready to edit, or more compilation work?"
           On ready: Switching to [editing mode].
           On flagged entry: rework flagged entries in Phase 1 only, then re-present.
```

## What this mode does NOT do

- **Re-open sources.** Phase 1 annotates from log fields only. §3 verification happened at logging time. No source re-read, no new fetch, no new dispatch.
- **Render APA / MLA / Chicago strings.** Formatting resolves `[@id]` tokens at Moment 3. Annotated-bib mode emits bare Pandoc tokens only.
- **Produce a §4 audit list.** The citation log was audited in `[research mode]` at logging time and in `[refining mode]` if the project ran that path. Annotated-bib has no separate audit-list forcing artifact; the annotations themselves are the output.
- **Apply §9 prose rules.** Sentence connectedness, paragraph flow, information pacing, and building-arguments rules assume multi-paragraph prose. Annotations are per-entry blocks; §9 does not apply.
- **Auto-enter from `[research mode]`.** The handoff from research requires {{USER}}'s explicit confirmation that the merged log is ready. No auto-advance.

## Exit Gates

**Allowed transitions (from annotated-bib):**
- → `[editing mode]`. Gate: every in-scope entry annotated + draft compiled + {{USER}} explicit readiness. Use `Switching to [editing mode].`
- → `[research mode]` if a gap surfaces during Phase 1 that cannot be resolved from existing log fields and requires a new source. Use the §3 self-correction or unsourced-gap auto-trigger form; announce `Switching to [research mode] (invoked from [annotated-bib mode]).` Return and continue Phase 1 once the log is updated.
- → `[collaborative mode]` if {{USER}} pauses to discuss scope or approach. Explicit switch only.

**Forbidden transitions:**
- → `[writing mode]`. Annotated-bib and essay-writing are mutually exclusive project paths. `[writing mode]` is essay-only; if the project type is `annotated-bib`, `[writing mode]` is not in the registry.
- → `[outlining mode]` / `[refining mode]`. Essay-pipeline modes; unreachable in annotated-bib projects.
- → `[formatting mode]` without first going through `[editing mode]`. The edit-complete gate and voice audit surface-scan are required before formatting; annotated-bib mode does not bypass them.

## See also

- `CLAUDE.md §4` — synthesis integrity iron rule. Applies to annotation claims about what a source says; paraphrase scope applies to the summary beat.
- `CLAUDE.md §7.1` — mode registry (project-type restriction to `annotated-bib`).
- `CLAUDE.md §7.4` — mode-to-mode gate table; `→ annotated-bib` gate row and forbidden transitions.
- `docs/modes/research.md` — predecessor; provides the merged log that Phase 1 annotates. Annotated-bib variant of the source-finder dispatch template lives in research.md step 4.
- `docs/modes/editing.md` — successor; annotated-bib project variant at passes 7 and 8 (pass 7 skipped, pass 8 reduced to iron rules + tone check only).
- `docs/modes/writing.md §Paraphrase default` — the 4-item paraphrase test applies inside Phase 1's summary beat when deciding whether a phrase requires direct quotation.
- `~/.claude/citations/schema.md §Annotation` — annotation shape authority (word budget, beat structure, partial-entry constraint).
