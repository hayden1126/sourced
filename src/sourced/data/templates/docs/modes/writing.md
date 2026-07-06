# [writing mode]

## Overview

Writing converts a refined outline into prose in two phases — **Phase 1: Plan** (you write a per-section prose-plan in your own context, naming sentence roles and closure types) and **Phase 2: Draft** (you dispatch a `prose-drafter` subagent per section, passing the plan plus inlined voice rules, worked paragraphs, cut patterns, §10 never-list, and relevant citation log entries; the drafter returns prose and a self-audit; you then run per-sentence checks on the returned prose).

The failure mode this two-phase shape exists to prevent is **paragraph-scale rhythm breakdown** — the AI-flavored prose that results when sentences are emitted one at a time against a modular claim + quote outline with no paragraph-shape plan in between. Earlier versions of this mode composed sentence-by-sentence in parent context, which mixed planning state with generation state and reproduced the patterns §10 names (aphoristic closures, compression-stranded verbs, first-person commitment in third-person registers). Separating plan from draft, and moving the draft into an isolated subagent, breaks that mixing.

Writing is not a rigid mode per spec §13.1; sub-mode transitions within writing (Phase 1 → Phase 2 → per-sentence audit) do not require {{USER}} checkpoints unless the brief's autonomy level is `Low`. The `writing → editing` gate is still {{USER}}-initiated (manifest §7.4).

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "write this" / "put this into prose" / "write out X" or equivalent (see manifest §7.2).
- Project type must be `essay`. [writing mode] is not valid for `annotated-bib` projects (manifest §7.1).

**Do not enter when:**
- The refined outline has not been approved. The gate `refining → writing` requires the §4 audit list with zero unresolved `flagged` rows plus explicit outline approval from {{USER}} (manifest §7.4). Silence is not approval.
- `config/voice.md` is missing. Stop and ask {{USER}} to run `sourced switch voice <name>`. Do not guess voice rules.
- `[UNSOURCED]` tokens or unresolved `[VERIFY: …]` tokens appear in the outline where they carry load-bearing claims. Resolve via [research mode] first.
- The voice file lacks a `## Worked paragraphs` section or a `## Cut patterns` section — these are load-bearing inputs to `prose-drafter` dispatches. Stop and ask {{USER}} to re-run `voice-extractor` with the current skeleton (which ships these sections) or to hand-add the sections to an older derived voice.

## Steps

Writing runs in two phases: Phase 1 produces a prose-plan in parent context; Phase 2 dispatches `prose-drafter` per section and audits returned prose. Both phases execute within a single entry to `[writing mode]`; the Phase 1 → Phase 2 transition is internal, not a manifest-level gate.

### Phase 1 — Plan

In Phase 1 you produce a structured prose-plan for the section being drafted. The plan is a **thinking artifact**, not a deliverable — its job is to force decisions about paragraph shape before any prose commits. The plan's fields use structured one-clause values and tag vocabulary; if you find yourself writing a sentence of prose under a plan field, that is an Iron Law violation (see below).

#### Phase 1 Iron Law

```
┌────────────────────────────────────────────────────────────┐
│  PLAN FIELDS ARE TAGS AND ONE-CLAUSE VALUES — NOT PROSE.   │
│  IF YOU CATCH YOURSELF WRITING A SENTENCE, STOP AND TAG.   │
│  SENTENCE-ROLE VOCABULARY IS SHARED WITH config/voice.md AND│
│  prose-drafter: USE THE SAME TAG NAMES ACROSS ALL THREE.   │
└────────────────────────────────────────────────────────────┘
```

#### Phase 1 steps

1. **Announce entry.** First output of the turn: `Switching to [writing mode].` Name the section in one clause after the announcement: "writing section 2" / "drafting the phonological-refutation section."

2. **Read `config/voice.md` in full.** All voice rules apply strictly at write time — not only Paragraph Flow. Do not work from memory of prior sessions. If `config/voice.md` is missing, halt and ask {{USER}} to run `sourced switch voice <name>`.

3. **Read `docs/modes/writing.md §Never-list` (this section, below) in full.** On first entry per session, re-read it even if you believe you know it. The restructure-don't-retokenize rule and cross-sentence retokenization check are load-bearing and easy to misapply from memory. On every entry, close the step with a load line: `never-list: <N> entries, first <id>, last <id>`, copied from the file just read. A count or ID that disagrees with the file is a failed load; re-read before drafting.

4. **Load the citation log** (`sources/<draft>.citations.json`). Every claim you draft will need an ID. If the log is absent for a section with citations in the outline, stop and ask {{USER}}.

5. **Declare the section's register mode.** Read `config/voice.md ## Sub-register taxonomy` (or equivalent). Pick one of the labels (`academic-report`, `prospectus`, `personal-essay`, etc.) based on the brief and the section's role. If the brief does not specify, default to `academic-report` for essay projects and flag the default in the plan's `Register Mode` field. The register mode filters which `config/voice.md` rules apply in Phase 2.

6. **Write the section plan** — one `### Section plan` block per section being drafted. The plan has these fields:

   - **Section label** — short name for the section.
   - **Rhetorical arc** — 1 sentence: what this section does in the paper (sets up the problem, develops the central contrast, delivers the synthesis, etc.).
   - **Register mode** — the sub-register label you declared in step 5.
   - **Voice-alignment notes** — 1–2 lines naming which rules are load-bearing for this section specifically (e.g., "parenthetical gloss on Cheyenne terms — high density here"; "cut patterns to watch: aphoristic-closure at paragraph ends, first-person-commitment-in-academic-report at S1 of ¶2").
   - **Per-paragraph plan** — one block per paragraph in the section:

     ```
     #### Paragraph <N>
     - Claim: <verbatim from refined outline>
     - Role: <verbatim from refined outline: setup | argument | counterargument | synthesis | ...>
     - Opener shape: <state-claim-flat | bridge-from-prior | name-counterpoint | introduce-example | reference-back>
     - Development pattern: <claim → evidence → interpretation | three-example walk | scholar-then-synthesis | set-up-then-refute | ...>
     - Sentence-role sequence: S1=<role>; S2=<role>[, @<id>]; S3=<role>[, @<id>]; S4=<role>
       (Sentence count: 3-5; role vocabulary from config/voice.md ## Worked paragraphs annotations.)
     - Citation placement: <id list from outline, mapped to sentence positions per the sentence-role sequence>
     - Handoff: <verbatim from refined outline — how this paragraph bridges to the next>
     - Closure-type: transitional | synthesis | question-out
       (NEVER aphoristic. Aphoristic closures are a §10 canonical ID and a ## Cut patterns entry.)
     ```

   - **Cross-paragraph connective tissue** — one line per adjacent pair:

     ```
     - P1→P2: "<connective word or phrase>" (<contrast | amplification | sequence | pivot | exemplification>)
     - P2→P3: ...
     ```

7. **Optional {{USER}} checkpoint.** By default, Phase 1 does not pause for {{USER}} approval — forward momentum is the baseline. Exceptions:

   - Brief autonomy level is `Low`: present the plan and ask `"Plan looks right? Dispatch the drafter, or revise?"` before Phase 2.
   - {{USER}} opens the turn with `[plan-first]`: pause after Phase 1 regardless of autonomy.
   - Section has >6 paragraphs: pause to confirm the slicing strategy (see `## Granularity` below).

   Absent an explicit trigger, proceed directly to Phase 2.

### Phase 2 — Draft

In Phase 2 you dispatch one `prose-drafter` subagent per section, inlining everything the drafter needs. The drafter has `omitClaudeMd: true` and sees no prior conversation context; your dispatch prompt is its entire input. Miss an input, the drafter can't compensate.

#### Phase 2 Iron Law

```
┌────────────────────────────────────────────────────────────────┐
│  DISPATCH INLINES: plan, voice_rules (register-filtered),      │
│    worked_paragraphs, cut_patterns, never_list,                │
│    citation_entries, prose_context.                            │
│  DRAFTER RETURNS: prose + self-audit + flags. YOU RUN CHECKS.  │
│  SELF-AUDIT MISMATCH OR NON-EMPTY FLAGS BLOCK → INTERVENE.     │
└────────────────────────────────────────────────────────────────┘
```

#### Phase 2 steps

8. **Filter voice rules by register.** From `config/voice.md`, extract the rule sections whose register tag matches the section's declared `Register Mode` or is unmarked (register-independent). Drop rules tagged for other registers. This is the single most important filtering step — a personal-essay Stance rule applied to an academic-report dispatch is the `first-person-commitment-in-academic-report` cut pattern.

9. **Select worked-paragraph exhibits.** From `config/voice.md ## Worked paragraphs`, pick 1–2 exhibits whose register-tag matches `Register Mode`. If no exhibit exists for the register, pass the closest match and flag it in the dispatch (the drafter will cope but note the gap).

10. **Bundle cut patterns.** From `config/voice.md ## Cut patterns`, inline every pattern block. Cut patterns are register-independent in most cases; if a pattern carries a `[register: ...]` tag, include only when the tag matches `Register Mode`.

11. **Load the never-list.** Extract the full `## Never-list` section from this file (writing.md) plus any `## §10 exemptions` bullets from `config/voice.md`. Inline both in the dispatch.

12. **Gather citation entries.** From the citation log (`sources/<draft>.citations.json`), pull the entry for every `@id` referenced in the section plan's Citation placement fields. Inline the full entry (`id`, `source.authors`, `source.title`, `source.year`, `source.url`, `exact_quote`, `surrounding_context`, `retrieved_at`, `draft_reference`).

13. **Stage the prose context.** Provide:
    - `prev_section_last_sentence` — the last sentence of the section before this one (from the draft file, if already written) or `omit` if first section.
    - `next_section_planned_opener` — one-line description of how the next section opens (from the refined outline) or `omit` if last section.

14. **Dispatch the `prose-drafter` subagent.** Tool: `Agent` (subagent). Dispatch prompt structure:

    ```
    You are prose-drafter. Draft prose for the following section.

    section_label: <label>
    register_mode: <label>
    granularity: section

    section_plan:
    <full Phase 1 plan block, verbatim>

    voice_rules:
    <register-filtered rule sections from config/voice.md, with **Rule.** and **Exemplars:** preserved>

    worked_paragraphs:
    <matching exhibits from config/voice.md ## Worked paragraphs, verbatim with annotation blocks>

    cut_patterns:
    <matching patterns from config/voice.md ## Cut patterns, verbatim>

    never_list:
    <full ## Never-list prose from docs/modes/writing.md, plus config/voice.md ## §10 exemptions bullets>

    citation_entries:
    <JSON array of full log entries for every @id in the plan>

    prose_context:
      prev_section_last_sentence: <verbatim or "omit">
      next_section_planned_opener: <one-line or "omit">

    Return: section prose + ### Self-audit + ### Flags per your contract.
    ```

15. **Audit the returned prose.** The drafter's self-audit tells you what the drafter thinks it did. Your job is to confirm and correct.

    a. **Self-audit consistency.** Confirm every paragraph's self-audit has one bullet per emitted sentence, every role matches the plan's sentence-role sequence, and every `Closure-type:` line matches the plan's closure-type field. Mismatch → re-dispatch (budget: 2 re-dispatches per section) or fall back to hand-drafting.

    b. **Per-sentence checks on returned prose.** Run the check list in `## Per-sentence audit checklist` (below) against every sentence. Treat the drafter's self-audit as a hint, not a substitute — the drafter may have flagged nothing while still emitting a §10 hit. Parent's audit is independent.

    c. **Flag resolution.** The drafter's `### Flags` block names the things it caught that it couldn't resolve. For each flag:
       - `paragraph-N-plan-mismatch` → re-plan that paragraph in Phase 1 and re-dispatch with the revised plan.
       - `paragraph-N-cut-pattern-near-miss` → inspect the prose around the flag; if the drafter restructured and the pattern is gone, the flag is informational. If still present, fix in-parent or re-dispatch.
       - `§10-<id>-conflicts-with-rule` → the drafter hit a voice/§10 conflict. §10 wins unless a `## §10 exemptions` bullet exists (manifest §7.6). Restructure around §10.
       - `stale-byline-<id>` → fire the §3 self-correction trigger and switch to `[research mode]` for byline re-verification.
       - `unsourced-claim-paragraph-N` → switch to `[research mode]` to find a source, or remove the claim.
       - `oversized-section-N-paragraphs` → re-slice the section into mini-sections (≤6 paragraphs) and re-dispatch.
       - `scope-drift-near-miss-<id>` → re-audit the paraphrase against `exact_quote`; fix in-parent.
       - `cross-section-handoff-weak` → revise S1 or S-last to strengthen the bridge; in-parent fix is usually sufficient.

16. **Stitch.** Once the section's drafter returned and audits pass, append the prose to the draft file. Do not insert a section break or separator the draft doesn't require; the prose is drop-in.

17. **On completion of a section,** present the prose to {{USER}} and ask whether to continue to the next section or stop. Do not advance to `[editing mode]` on your own; the gate is {{USER}}-initiated only (manifest §7.4).

### Granularity

Default is **section per dispatch**. Sections over 6 paragraphs are sliced into 3–4 paragraph mini-sections (each a separate dispatch, stitched in order). The 6-paragraph cap guards against rhythm breakdown at longer scales.

**Paragraph-per-dispatch** is an alternative mode for heterogeneous sections (different registers, wildly varied evidence density). Set `granularity=paragraph` in the dispatch when:
- The section's paragraphs span two or more registers and you want separate drafter context per register.
- One paragraph has failed re-dispatch at section-scale twice and you want to isolate it.
- {{USER}} explicitly requests paragraph granularity.

Otherwise, section. Paragraph dispatches lose some paragraph-to-paragraph rhythm because the drafter doesn't see the full arc; the plan's cross-paragraph connective tissue compensates but imperfectly.

### Per-sentence audit checklist

Applied to drafter's returned prose, post-dispatch. Each check fires independently. After running the checklist on a section, emit `parent-audit: <k> hits (<check names>)` or `parent-audit: no hits`; each fix or re-dispatch below traces to a named hit. A section accepted without a parent-audit line has not been audited.

- **Voice.** Every `**Rule.**` in the filtered `voice_rules` applies to every sentence. Look for sentences that violate a rule despite the drafter's self-audit claiming compliance.
- **§10 never-list.** Scan every paragraph for entries in the never-list. Apply `Restructure, don't retokenize`. A period between X and Y (Cross-sentence retokenization) doesn't escape `not-x-but-y`. An aphoristic closure is a `aphoristic-closures` hit regardless of whether the drafter flagged it.
- **Paraphrase default.** Each direct quote in the prose must pass the 4-item test (wording-as-object-of-analysis, qualifier-would-be-lost, authority-rests-on-formulation, will-push-against-wording). Powerful-feel is not a carve-out.
- **§4 synthesis integrity.** Each paraphrase preserves `exact_quote` scope. Attribution preserved. Inference marked. Multi-source claims checked.
- **Pandoc IDs.** Every citation wrapped as `[@id]` / `@id` / `[@id, p. N]`. No rendered author-year strings.
- **Stale-byline.** Any `@id` in narrative position whose log entry's `retrieved_at` predates this conversation → fire §3 self-correction trigger.
- **Cut patterns.** Scan against every pattern in `config/voice.md ## Cut patterns`. Shipped patterns (aphoristic-closure, compression-stranded-verb, abstract-nominalization-cascade, reduced-relative-stacking, first-person-commitment-in-academic-report, citation-atomization) + any mined from `failures_dir` at extraction time.

Check failures → fix in-parent (for small, local issues) or re-dispatch with revised plan (for structural issues). Re-dispatch budget: 2 per section before escalating to {{USER}}.

## Red Flags

- *"I'll skip Phase 1 and just dispatch the drafter with the outline."* — No. The plan is what gives the drafter paragraph-shape discipline; without it, you get the same rhythm breakdown the two-phase split exists to prevent.
- *"Phase 1 is overhead for a short section."* — Phase 1 for even a 2-paragraph section costs less than one re-dispatch. The plan is a forcing artifact for shape decisions; skipping it defers the decisions to the drafter, which is exactly where they fail.
- *"I'll draft inline instead of dispatching."* — The isolation is the design point. Parent context carries planning state, cross-session memory, conversation rhythm; drafting inside that context reproduces the §10 patterns the never-list names. Dispatch.
- *"The drafter's self-audit says clean; I don't need to re-check."* — The drafter may be honest and still wrong. Self-audit is a hint; the parent's per-sentence audit is the authority.
- *"This cut-pattern hit is minor; I'll leave it."* — No. A cut pattern in the draft is evidence the dispatch bundle was under-specified or the plan was wrong. Fix in-parent or re-dispatch; don't ship.
- *"`config/voice.md` has no `## Worked paragraphs` section — I'll just skip that field in the dispatch."* — No. The skeleton ships with that section; if it's missing, the voice is an older derived file that needs re-extraction. Halt and ask {{USER}}.
- *"`config/voice.md`'s Phase 1 plan format feels redundant with the outline."* — The outline says what claims; the plan says what shapes. Different objects. The outline is the structural plan; the prose-plan is the rhetorical plan.
- *"The drafter returned prose with a hit on §10 `aphoristic-closures` and the closure-type was set to `synthesis` in the plan — the drafter ignored the plan."* — That's a flag for re-dispatch or in-parent fix, not a reason to change the plan. The plan is right; the drafter needs to conform.
- *"I want to make a structural change to the section — I'll just do it in Phase 2."* — No. Structural changes go back through `[refining mode]`. Writing does not restructure; it drafts what refining approved.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "Phase 1 + Phase 2 is slower than one-shot drafting." | Wall-clock yes, one pass. Quality-adjusted no — the re-dispatch budget catches errors that would otherwise need heavy editing. |
| "The drafter is just another LLM; dispatching doesn't help." | Dispatch isolation is the point, not the model. The parent's accumulated context reproduces the patterns §10 names; a fresh-context drafter with explicit rules avoids the pattern-imitation momentum. |
| "I'll draft in parent and dispatch only for long sections." | Inconsistent application; the parent can't develop the discipline needed for reliable per-sentence audit if sometimes it drafts, sometimes it audits. Dispatch consistently. |
| "The plan's sentence-role sequence feels over-specified." | The sequence is what makes the drafter's self-audit usable. Without a role per sentence, audit is subjective; with it, the parent can mechanically compare. |
| "closure-type: synthesis is the same thing as transitional." | It isn't. Synthesis closes the paragraph's argumentative arc (earned summary); transitional opens the next paragraph's topic (a bridge). The drafter treats them differently. |
| "My `config/voice.md` doesn't have register tags — I'll just ignore the register_mode field." | The register is still load-bearing for choosing exhibits and cut patterns. If `config/voice.md` is un-tagged, the voice file may be pre-phase-3 — consider re-extracting. In the meantime, declare a register anyway and apply the best-match rules manually. |
| "I hit a §10 conflict with a voice rule; I'll note it as a drafter flag and move on." | Resolve it. §10 > `config/voice.md` prose (manifest §7.6). If the voice rule needs to win, a `## §10 exemptions` bullet is required. Absence of a bullet is not permission. |

## Quick Reference

```
ENTRY:   Switching to [writing mode]. drafting <section>.

PHASE 1: PLAN
  Step 0: Read config/voice.md (full). Read §Never-list (full). Load citation log.
  Step 1: Declare Register Mode.
  Step 2: Write ### Section plan:
            - Rhetorical arc (1 sentence)
            - Voice-alignment notes (1-2 lines)
            - Per-paragraph blocks (claim, role, opener-shape,
              development-pattern, sentence-role sequence,
              citation placement, handoff, closure-type)
            - Cross-paragraph connective tissue
  Step 3: Optional {{USER}} checkpoint (Low autonomy / [plan-first] / >6 ¶s).

PHASE 2: DRAFT
  Step 4: Filter voice rules by register mode.
  Step 5: Select worked_paragraphs exhibits by register mode.
  Step 6: Bundle cut_patterns.
  Step 7: Load never_list (+ §10 exemptions from config/voice.md).
  Step 8: Gather citation_entries (full log entries for every @id in plan).
  Step 9: Stage prose_context (prev sec last sentence, next sec opener).
  Step 10: Dispatch prose-drafter subagent. (Agent tool; granularity=section.)
  Step 11: Audit returned prose:
             - Self-audit consistency against plan
             - Per-sentence check list (voice, §10, paraphrase, §4, Pandoc, stale-byline, cut patterns)
             - Flag resolution (re-dispatch budget: 2 per section)
  Step 12: Stitch prose into draft file.
  Step 13: Present section to {{USER}}; ask continue-or-stop.

EXIT:    {{USER}}-initiated only → Switching to [editing mode].
```

## Exit Gates

**Allowed transitions (from writing):**
- → `[editing mode]`. Gate: {{USER}}-initiated only. Use `Switching to [editing mode].`
- → `[research mode]` via §3 self-correction auto-trigger (stale byline or unverified citation surfaced during drafting or in drafter's flags). Use `Switching to [research mode] (invoked from [writing mode]).` Return to writing once the gap is resolved with `Switching back to [writing mode].`
- → `[finetuning mode]` on {{USER}}-initiated local-substitution ask mid-draft. Announce the switch; resume writing after selection.
- → `[refining mode]` if writing reveals a structural problem the outline does not resolve. Surface the structural question and let {{USER}} direct the switch; do not restructure at prose level.

**Forbidden transitions:**
- → `[editing mode]` on your own. The gate is {{USER}}-initiated only (manifest §7.4).
- → `[formatting mode]` direct. Formatting requires edit-complete gate; writing does not produce a paste-ready artifact.
- → `[outlining mode]` direct. Upstream; if the outline is wrong, the path is through [refining mode], not back to outlining from here.

---

## Never-list

**Canonical source of truth for §10 pattern prose.** [editing mode] pass 6 reads this section directly. `prose-drafter` dispatches include this section verbatim. Each entry carries `[id: <canonical-id>]` for `sourced check` I3 parsing and for `config/voice.md`'s `## §10 exemptions` mechanism. The canonical ID list in manifest §7.6 is the mechanical validation source of truth; the prose here is the operational source of truth.

These patterns are not claims about bad prose in general. A human author may use any of them with control. The concern is reproduction: when this agent pads, transitions, or performs analytical depth, these are the shapes it reaches for by default. A reader familiar with AI output clocks them as machine rhythm even when a human author would deploy the same pattern cleanly.

### Pattern entries

**Em dashes** [id: em-dashes]

Em dashes (—) used for appositives, interruptions, or ranges. The problem is the mid-clause interruption rhythm, not the character itself. Do not substitute commas or parentheses while keeping the interruption rhythm; that preserves the shape the reader notices. Restructure: make the gloss a standalone sentence, relocate it to a natural position, or cut it entirely if it is not load-bearing.

**"Not X but Y"** [id: not-x-but-y]

The contrastive pivot shape: "not X but Y," "X, not Y," "less X than Y," "not merely X but Y," "it is not that X, but that Y." When contrast is load-bearing, make Y the direct assertion and position X in a separate clause or drop it. Reordering to "Y, not X" preserves the comparative-pivot shape and fails the audit. See also the cross-sentence retokenization rule below — splitting X and Y across a sentence boundary does not escape the pattern.

**Ornamental triads** [id: ornamental-triads]

Triadic or tetradic lists ("X, Y, and Z"; "X, Y, Z, and W") where items are parallel for rhythm rather than argument. A genuine enumeration whose three or four items each carry independent argumentative weight is not flagged. An ornamental cadence that exists to sound thorough is. Reduce to the one item that carries the argument; cut the others, or name them only if each does distinct work.

**Throat-clearing openers** [id: throat-clearing-openers]

Sentence-initial: "Crucially," "Ultimately," "Fundamentally," "Importantly," "In essence," "It is worth noting that," "It bears mentioning that," "What is striking is." These perform emphasis without adding content. The emphasis claim should be carried by the sentence itself: by what it says and where it sits in the paragraph. An adverbial endorsement prepended to the sentence performs emphasis without adding content. Cut the opener and let the sentence stand.

**Demonstrative-noun paragraph openers** [id: demonstrative-openers]

Paragraph openers such as "This tension," "These dynamics," "This shift," "Such patterns" where the demonstrative is doing work the prior paragraph did not earn. The antecedent must be specific and recent — the immediately preceding paragraph's conclusion, stated precisely, not a gestural summary of a section's theme. If the demonstrative does not have a specific recent antecedent, name the antecedent directly or restructure the opening.

**Ornamental compounds** [id: ornamental-compounds]

Hyphenated conceptual compounds that disappear after one use: "state-as-universal-life," "recognition-work," "meaning-disclosure-practice." Coining a compound is acceptable when the term recurs and carries argumentative weight across the essay. Coining one for a single paragraph is AI ornamentation — the compound exists to sound conceptually dense rather than to do analytic work. Use standard phrasing for single-use concepts; reserve compounds for terms that earn their coinage through recurrence.

**Aphoristic closures** [id: aphoristic-closures]

Paragraph endings that land on a rhetorically-balanced pronouncement in place of earned conclusion. Signatures: "X is itself Y," "W handles what it handles," "That is the limit the paper holds," "Y persists while X drifts," "No stronger claim is intended." The shape simulates thesis-closure — the reader receives a feeling of resolution without actual resolution.

A closure is aphoristic when two or more of these signals hold:

- The sentence's structure is symmetrical ("X is Y"; "A and B" parallel) in a way the preceding paragraph did not set up.
- The sentence asserts a bounded framework-level claim ("the limit the paper holds," "the interesting linguistic fact") rather than an argument-level conclusion.
- The sentence's content is removable without losing the paragraph's argument — i.e., it is rhetorical sealant, not load-bearing inference.

**Restructure** to `closure-type: transitional` (end on what the next paragraph picks up), `closure-type: synthesis` (end on an earned consequence the argument has carried), or `closure-type: question-out` (end on a question the next section resolves). Never retain an aphoristic closure as cosmetic polish; the pattern reads as AI regardless of register.

### Density list

Acceptable once per essay; AI-ish when stacked. [editing mode] pass 6 flags any term appearing three or more times or any two sibling instances.

- **Abstract nominalizations**: "the convergence of," "the divergence over," "the question of where" — a verb clause reads more directly.
- **"For X… for Y…" parallel constructions** between clauses or sentences.
- **"As we shall see," "we come to see," "we can return to," "we must begin."**
- **Stacked sentence-initial participials**: "Drawing on X…", "Building on Y…", "Extending Z…" — two in a row is a signature.
- **"In this way" as a transition** — common in academic prose; becomes a tell at three or more occurrences per essay.

### Restructure, don't retokenize

Removing a never-list pattern requires changing the sentence **shape**, not swapping punctuation or reordering words.

When a pattern is flagged, identify the shape it produces — mid-clause interruption, balanced pivot, rhetorical escalation, ornamental triad — and rebuild around a different shape:

- An em-dashed appositive becomes a standalone sentence or is cut.
- A "not X but Y" becomes a direct assertion of Y, with X dropped or placed in a preceding sentence as independent background.
- An ornamental triad is reduced to the single item that carries the argument.
- An aphoristic closure becomes a transitional, synthesis, or question-out closure — the paragraph ends on work, not on rhetoric.

Substituting commas for em-dashes while keeping the interruption preserves the rhythm. Reordering "not X but Y" to "Y, not X" preserves the contrastive pivot. Neither counts as restructuring.

### Cross-sentence retokenization rule

Splitting X and Y across a sentence boundary does not escape the `not-x-but-y` pattern. "X. Y." where sentence 1 contains a clausal negation ("does not X," "is not X," "X never Y") and sentence 2 opens with a positive assertion that stands as the alternative — beginning with "It," "Instead," a pronoun co-referring to sentence 1's subject, or a noun phrase naming the alternative — is the same contrastive pivot as "not X but Y." A period is not structural change. The fix is to drop X, merge X into Y as a positive assertion, or place at least one sentence of unrelated content between them.

### Exemptions

A `## §10 exemptions` bullet in `config/voice.md` naming a canonical ID from the list above is the only override mechanism. Silence is not permission. Inline prose in `config/voice.md` arguing for a pattern without a matching exemption bullet has no runtime effect at write time or edit time (manifest §7.6). Unknown IDs fail `sourced check` install-time validation.

**Scope of an exemption.** An exemption suspends one never-list rule for this voice's writer prose. Each ID is independent. An exemption does not extend to prose generated on {{USER}}'s behalf that is not this voice's output ([red team mode] counter-phrasings, framework meta-commentary). The direct-quotations carve-out (root CLAUDE.md §10) is independent of exemptions.

**Runtime.** On entry to [writing mode] and [editing mode], scan `config/voice.md`'s `## §10 exemptions` section. If `config/voice.md` is missing, halt (see When to Use).

**Conflict surfacing.** If `config/voice.md` and §10 conflict without a matching exemption bullet, surface the conflict on first occurrence rather than resolving silently (manifest §7.6).

### Framework-meta carve-out

§10 governs generated academic prose: {{USER}}'s essay sentences, and agent-generated prose on {{USER}}'s behalf (drafts, paraphrases, counterphrasings, annotation blocks). §10 does not govern descriptive framework documentation written about the rules themselves — this file's own body prose, mode-body procedural prose in `docs/modes/`, and root `CLAUDE.md` manifest prose are framework meta, not academic prose. An em-dash appositive inside this file's description of the em-dash rule is not a rule violation; it is explanation. The carve-out is narrow: it covers framework files shipped by `sourced`, not any prose produced during a writing session. Read `editing mode`'s pass 6 accordingly — pass 6 audits the writer's draft against §10, not the framework's own documentation.

---

## Paraphrase default

Default to paraphrase. Direct quotation is the exception, not the standard option.

**Quote directly only when at least one of the following holds:**

- **(a) Wording as object of analysis.** The prose is analyzing the source's language itself — examining word choice, rhetorical structure, or specific phrasing as evidence.
- **(b) Qualifier or coined term lost in paraphrase.** Paraphrase would drop a hedge, condition, or coined term the argument depends on, and no paraphrase preserves it without adding your own words to carry what the original said in one.
- **(c) Authority rests on specific formulation.** The source's claim carries weight in this field because of how it is stated, and paraphrase would strip that force.
- **(d) You will push against the exact phrasing.** The prose will contest, qualify, or complicate the precise wording, making the original text itself the subject of the sentence.

In all other cases, paraphrase and run the §4 audit against the paraphrase using `exact_quote` and `surrounding_context` as ground truth.

**Flags that paraphrase is underused:**
- Direct-quote words exceed approximately 15% of a paragraph's word count.
- Two adjacent sentences both carry a direct quotation.

When a paragraph trips either flag, identify which quotes pass items (a)–(d) and convert the rest to paraphrase. Powerful-feel and vivid phrasing are not items (e) and (f); they are the rationalization for over-quoting.

**[editing mode] pass 8** re-applies this test to the finished prose and references this section by anchor. The 4-item test is the same at both write time and edit time; catching over-quoting at write time is cheaper.

---

## Voice

`config/voice.md` rules apply **strictly and in full** at write time — at Phase 1 (the plan's Voice-alignment notes reference specific rules by name) and at Phase 2 (the dispatch inlines register-filtered rule sections). [outlining mode] applies Paragraph Flow only; [writing mode] applies every section of `config/voice.md`. Do not elide sections.

**Read `config/voice.md` in full on every entry.** Memory from a prior session drifts. The file is the canonical source for this project's voice; different projects carry different voices.

**If `config/voice.md` is missing,** stop and ask {{USER}} to run `sourced switch voice <name>`. Do not guess rules and proceed.

**Phase-3 sections.** Modern `config/voice.md` files carry `## Sub-register taxonomy`, `## Worked paragraphs`, and `## Cut patterns` sections in addition to the traditional Tone/Structure/Dimension sections. If your project's `config/voice.md` lacks any of these, it was rendered from a pre-phase-3 skeleton or a derived voice that predates the contract change. Re-run `voice-extractor` against the original samples to produce a phase-3-shaped voice file, or hand-add the missing sections if re-extraction is not practical. `prose-drafter` dispatches require `worked_paragraphs` and `cut_patterns` inputs.

**Interaction with §10.** §10 > `config/voice.md` prose (manifest §7.6, precedence rule 2). A voice rule that conflicts with a §10 pattern has no runtime effect unless `config/voice.md` carries a `## §10 exemptions` bullet naming the canonical ID. Inline voice prose — even prose that says "em dashes are acceptable in this voice" — is not an exemption unless it appears as a bullet under `## §10 exemptions` with a canonical ID. Conflict surfacing: if `config/voice.md` and §10 conflict without an exemption, surface the conflict on first occurrence.

**At write time, voice rules are generative**, not just corrective: draft sentences toward the voice, not against §10. The edit-time voice audit (editing.md pass 9) is corrective; the write-time discipline is to build sentences that already fit both. `prose-drafter` inherits this discipline via the inlined rule sections + cut patterns; the parent's post-dispatch per-sentence audit is the safety net.

---

## In-prose IDs

Citations in source prose carry as Pandoc-style ID references. [formatting mode] resolves each ID against the citation log and emits a style-compliant string. Prose stays decoupled from style.

**This is Moment 2 of the three-citation-moment system** (manifest §8). [outlining mode] may carry bare IDs (`smith-2010-001`) attached to paragraph claims; wrapping into Pandoc syntax happens at Phase 2 (the plan's Citation placement fields carry bare IDs; the drafter wraps them in prose).

### Pandoc syntax table

| Pandoc syntax | Use | APA-7 example output |
|---------------|-----|----------------------|
| `[@id]` | Parenthetical, paraphrase | `(Smith, 2010)` |
| `@id` | Narrative, paraphrase | `Smith (2010)` |
| `[@id, p. N]` | Parenthetical, single page locator | `(Smith, 2010, p. 42)` |
| `[@id, pp. N–M]` | Parenthetical, page range (en-dash between numbers) | `(Smith, 2010, pp. 42–44)` |
| `[@a; @b]` | Multiple sources, parenthetical | `(AuthorA, YearA; AuthorB, YearB)` |

### Rules

**Never emit a rendered citation string in source prose.** A string like `(Smith, 2010)` or `Smith (2010)` in source prose is a regression. It short-circuits the renderer, defeats the byline-discipline guarantee (rendered author names bypass the log-verified `source.authors` field), and will be flagged in [editing mode] pass 1. [editing mode] pass 1 requires surfacing rendered-citation regressions to {{USER}} before converting — silent conversion is not allowed.

**Narrative IDs and stale-byline check.** `@id` (narrative) will produce a visible author name when [formatting mode] renders. Before wrapping a citation as `@id` for narrative use, check the log entry's `retrieved_at`. If it predates the current conversation's start or is missing, fire the §3 self-correction trigger and switch to [research mode] for byline re-verification. `prose-drafter` flags stale bylines in its `### Flags` block; parent acts on the flag.

### Special tokens

Two special tokens may appear in source prose during drafting:

- **`[VERIFY: ...]`** — a bibliographic detail you are not certain of (page number, year, DOI). Resolve before format time.
- **`[UNSOURCED]`** — a claim that has no source yet. Resolve before format time.

Both are format-time blockers per [formatting mode]'s pre-flight. Do not leave either token in prose you present as ready for editing without surfacing it to {{USER}}.

---

## Block quotes

Direct quotes longer than roughly 40 words go in a block quote. Format at source-prose level:

- Indent the quoted text.
- No quotation marks enclosing the block.
- Place the Pandoc citation at the closing position, after the closing punctuation of the quoted text: e.g., `[@smith-2010-001, p. 42]`.

The block-quote convention is style-agnostic at source-prose level. [formatting mode] delegates citation rendering for block-quoted passages to pandoc+CSL; the CSL encodes the style's direct-quote conventions.

**Direct-quotations carve-out (§4 governing rule).** §10 never-list patterns inside a direct quotation are not flagged. The quoted text is evidence, not generated prose. Preserve the source's punctuation verbatim inside the quoted span, including em dashes, ornamental triads, and any other pattern §10 would otherwise catch. §4 *Quote verbatim* is the governing rule; §10 is suspended inside the quoted span. See root CLAUDE.md §10 *Direct quotations carve-out* for the full carve-out definition and its limits (it is narrow: it covers the quoted span, not the writer's framing sentence next to it).

---

## What this mode does NOT do

- **Audit the full draft for §10 hits.** [editing mode] pass 6 does that. Write-time discipline is check-as-you-emit + per-sentence audit of drafter's return; pass 6 is the systematic audit over finished prose. The two are complementary, not redundant.
- **Render APA / MLA / Chicago strings.** [formatting mode] does that. Source prose carries Pandoc IDs only.
- **Make structural decisions unilaterally.** If writing reveals a structural problem, surface it and let {{USER}} direct the path back to [refining mode].
- **Advance to [editing mode] without {{USER}}'s initiation.** The writing → editing gate is {{USER}}-initiated only (manifest §7.4).
- **Run citation audits as a post-draft pass.** §4 synthesis integrity applies sentence by sentence during the Phase 2 audit of returned prose, not as a sweep after the section is done.

## See also

- `CLAUDE.md §3` — source verification; stale-byline self-correction trigger at write time (§7.3).
- `CLAUDE.md §4` — synthesis integrity; paraphrase scope, qualifier preservation, attribution.
- `CLAUDE.md §7.2` — explicit triggers (source of truth).
- `CLAUDE.md §7.4` — mode-to-mode gate table; `refining → writing` gate and `writing → editing` gate.
- `CLAUDE.md §7.5` — forcing artifacts: §4 audit list (emitted by [refining mode] before the gate here).
- `CLAUDE.md §7.6` — precedence rules, canonical §10 ID list, direct-quotations carve-out.
- `CLAUDE.md §8` — citation three-moment system; Moment 2 in-prose IDs (this file's §In-prose IDs).
- `docs/modes/refining.md` — predecessor; the §4 audit list this mode requires at entry.
- `docs/modes/editing.md` — successor; Pass 0 revision audits drafts against plans; pass 6 reads `docs/modes/writing.md#never-list`; pass 8 reads `docs/modes/writing.md §Paraphrase default`.
- `docs/modes/research.md` — target for stale-byline and unsourced-claim auto-triggers fired during writing.
- `config/voice.md` — voice rules loaded at step 2; `## §10 exemptions` bullets read at step 3; `## Worked paragraphs`, `## Cut patterns`, `## Sub-register taxonomy` consumed by Phase 2 dispatch.
- `~/.claude/agents/prose-drafter.md` — the subagent dispatched in Phase 2; its input contract is the dispatch shape in step 14.
- `~/.claude/citations/schema.md §Staleness` — `retrieved_at` staleness threshold used in the stale-byline check.
