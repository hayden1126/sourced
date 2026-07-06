# Staged reader review and voice extraction v2

- **Date:** 2026-07-06
- **Status:** Proposed. Design spike deliverable for issues [#51](https://github.com/hayden1126/sourced/issues/51) and [#29](https://github.com/hayden1126/sourced/issues/29) (reader-simulation half); Next queue row 1.
- **Scope:** The staged-reader-review primitive (protocol, artifact schema, gate placement); the voice fidelity measure (#51 Q1); voice representation (#51 Q2); the code fork (#51 Q3); multi-register coverage (#51 Q4); corpus intake (#51 Q5); consumer map; decomposed issue list.
- **Out of scope:** All implementation (tracked in §10). The citation-payload critic (#29 evidence 1) runs as its own thread, Next queue row 2; this spec does not design it. Peer review mode and revision mode implementation (consumers, §9).

## 1. Problem

Two problems from the 2026-07-04 paper session turn out to share one primitive.

**Voice measurement is blind.** The #51 diagnosis: the voice file represents voice as parts (per-section rules, 2-3 quote exemplars each), and the drafter reconstructs from parts. Rules state constraints well; they under-specify generation. Nothing measures how close a draft is to the corpus, so improvement is blind and stopping is a judgment call. The session sharpened this: no in-flow voice failure was caught all session, and a session cannot distinguish "the voice file held" from "in-flow drafting cannot notice its own flatness" (#51 comment, 2026-07-04). That indistinguishability is the measurement problem.

**Reader-level defects are invisible to every existing pass.** The session shipped a four-study section too dense to hold, statistical vocabulary undefined at first use, and two mechanism strands unjoined for three sections. The prose obeys the voice file's pacing rules sentence by sentence; the failures exist only at whole-essay scale (#51 comment; observations.md, #29 bullet). All nine editing passes audit sentences and citations. None reads cumulative load or term-introduction order.

One instrument caught the second class of defect: a staged reader review (three blind personas, lockstep section-by-section reading, per-section ratings with quoted trip points). It is the only mechanism that has ever detected a joint-level failure in this framework, and it is simultaneously the candidate answer to the first problem's Q1. Designing it once, persona-neutral, is the point of this spec.

## 2. Evidence base

Observed, not predicted. Sources: issue #51 comment (2026-07-04), issue #29 comment (2026-07-04), `~/papers/cross-sex-empathy/notes/observations.md`.

1. Three blind readers converged on the same three defects; whole-document review smooths over exactly these (the prototype skill's design rationale, confirmed in the field).
2. The defects were invisible to the 9-pass editing audit: they are properties of the joint distribution across sections, not of any sentence.
3. The prose-drafter's structural self-audit passed a content contradiction (Wong 2018 called longitudinal; the cited entry is the quote calling for longitudinal work because none exists). Upstream self-audit "no flags" is not evidence. This drives the payload critic (queue row 2) and one design invariant here: reviewers never see, and never trust, upstream audit output.
4. At-the-moment observation logging failed across the session; every real observation landed at a gate (merge, format, post-review). Instrumentation designed here is gate-native.
5. A working prototype exists at `~/.claude/skills/staged-reader-review/SKILL.md`, exercised once on a real paper (3 readers, 6 sections). Most of the protocol is codification, not invention (§3.1).

## 3. The staged-reader-review primitive

### 3.1 What exists and what is new

Honest split, because "design" here is mostly transcription:

| Piece | Status |
|---|---|
| Personas, briefing rules, one-outsider requirement | Exists in prototype |
| Lockstep sectioning, no peek ahead, reaction-before-rating | Exists in prototype |
| Anchored 1-5 clarity and coherence scales | Exists in prototype |
| Stateful sequential reading (no independent re-scoring) | Exists in prototype, with rationale |
| Consolidation rules (convergence, spread, out-of-scope) | Exists in prototype |
| Per-section artifact schema with stable IDs | **New** (§3.3) |
| Verdict vocabulary aligned to mode gates | **New** (§3.3) |
| Gate placement and formatting-mode wiring | **New** (§3.4) |
| #33 pre-flight attachment | **New** (§3.4) |
| Persona parameterization contract for consumers | **New** (§3.5, §9) |

### 3.2 Protocol (persona-neutral)

The bundle version keeps the prototype's protocol intact. Summary, normative:

- N blind reader personas, default 3, maximum 5. Each persona declares a background and a watch-list. At least one persona is an outsider to the draft's field. Personas must differ in what they attend to, not just their label.
- Input is the **rendered output** of `[formatting mode]` (the `.gdocs.md`, `.plain.md`, or equivalent sibling), split at its natural section boundaries. Never split mid-argument. Readers judge what a real reader receives, not the source prose.
- Sections go to all readers in lockstep, one at a time, no peek ahead. Each reader writes a reaction first (80-120 words), then rates clarity 1-5 and coherence 1-5 on the anchored scales. Comprehension is rated, not prose quality.
- Reading is sequential and stateful. A reader lost in section 2 struggles in section 5; surfacing that cascade is the instrument. Do not isolate per-section scoring.
- Readers never see: the citation log, the brief, the voice file, other readers' output, or any upstream audit report (evidence item 3).
- After the final section, each reader returns a synthesis: clarity arc, coherence arc, strongest and weakest section, highest-leverage change, verdict.
- The parent consolidates per §3.3. Convergence (2 or more readers) is the primary signal; single-reader concerns are listed separately; high-spread sections are flagged ambiguous rather than weak.

### 3.3 The artifact: `<draft>.reader-review.md`

The review is a forced artifact (VISION enforcement principle): a review that produced no file has not run. Sibling to the rendered output, structured for two consumers: the writer now, `[revision mode]` later.

```markdown
# Reader review: <draft> (<date>)

## Protocol
- Reviewed file: <rendered sibling, e.g. draft.gdocs.md>
- Sections: S1 "<heading>" (<words>w) ... Sn
- Readers: R1 <persona name>: <background, watch-list>. R2 ... R3 ...
- Upstream gate artifacts checked: <see §3.4>

## Ratings
| Section | R1 cl | R1 co | R2 cl | R2 co | R3 cl | R3 co |
|---|---|---|---|---|---|---|

## Findings
### RR-1: <one-line defect> [severity: high|medium|low] [sections: S3-S5] [readers: 2/3]
<verbatim trip-point quotes, compiled reader reasoning, 2-5 sentences>

## Single-reader notes
### RN-1: <note> [reader: R2] [section: S4]

## Verdict
- Per reader: R1 <accept|minor|major>, R2 ..., R3 ...
- Consolidated: <accept | minor revision | major revision>
- Top actions: <at most 3, keyed to RR ids>

## Out of scope
- <deferred concern, why: needs new evidence / contradicts venue / already addressed>
```

Design points:

- **Stable IDs.** `S<n>` for sections, `RR-<n>` for convergent findings, `RN-<n>` for single-reader notes. Revision mode's comment-to-change tracking keys off these; nothing needs a retrofit later.
- **Verdict vocabulary** is fixed to three values so a future gate can read it mechanically.
- **Quotes are verbatim trip points**, not reader transcripts. Compile patterns; the prototype's "quote sparingly" rule holds.
- Markdown, writer-facing. No JSON sibling until a mechanical consumer exists; the schema above is regular enough to parse when revision mode needs it.

### 3.4 Gate placement and the #33 attachment

The review runs **after formatting completes**, on the rendered sibling, invoked from collaborative mode. It does not block formatting (formatting stays the terminal pipeline stage) and it does not self-trigger; the writer asks for it. Recommended for any draft leaving the writer's hands.

Wiring is two pointers, not a new mode:

1. `docs/modes/formatting.md` Exit Gates gains one allowed transition: after the step 8 report, "run a staged reader review on the rendered output" is a named next step, with the artifact schema referenced.
2. The review's pre-flight records upstream gate artifacts in `## Protocol`: the editing handoff's §4 audit list and voice surface-scan report, and the pass-5 lists (proper-noun, paste-artifact, punctuation mechanics). Each is marked `present` or `absent`. This is issue #33's option 2 implemented one gate downstream, at zero enforcement cost: an absent list is now visible in a durable artifact instead of silently unchecked. It records; it does not halt.

Why not a new mode: mode discipline is for prose-touching stages with transitions to police. The review is read-only over a rendered sibling and produces one artifact. A bundle skill (the codified prototype) plus the two pointers above covers it. `[peer review mode]` stays a ROADMAP entry for the rubric-parameterized consumer and can wrap this skill in mode ceremony when its trigger fires.

### 3.5 Execution substrate

The prototype orchestrates with one-shot subagents: spawn per persona, `SendMessage` per section, `END` for synthesis, parent consolidates. The 2026-07-04 run worked with exactly this shape. Agent Teams (ROADMAP entry, angles 2 and 3) would add a coordinator and shared state; nothing in the evidence requires either, and the consolidation rules are deliberately parent-owned so convergence judgment stays in one place. Decision: one-shot subagents with lockstep messaging. Re-evaluate only if consolidation proves error-prone across consumers.

One caveat carried from the prototype: all readers run on the same base model, so added readers can amplify a shared blind spot. Persona diversity must be in the watch-lists. The Track B control-pair mechanism (§4.2) is the quantitative version of the same discipline.

## 4. The fidelity measure (#51 Q1): two tracks

Q1 asked for one measure. The session evidence says there are two different quantities, and conflating them is how the blindness persisted.

### 4.1 Track A: reader experience

The primitive above. It measures whether the draft lands: pacing, term order, cumulative load, joint-level coherence. It detected the only joint-distribution failure ever caught. It runs at the post-format gate, per draft, and its per-section ratings give the extract-draft-edit loop its first numeric signal.

Honest caveat (from the #51 comment): Track A measures reader experience, not authorial voice. A draft can rate 5/5 across sections and still not sound like the writer. Track A alone cannot answer "is this my voice."

### 4.2 Track B: authorial voice, blinded author-verification A/B

The measure for "does this sound like the writer," runnable without the writer's ear:

- **Sampling.** K passages from the corpus, K from the draft, matched for register and length (target K around 8-12; below 5 the discrimination estimate is noise).
- **Control pairs.** Corpus-vs-corpus pairs calibrate the judge's baseline: if judges "detect" differences between two passages by the same author, that rate is the floor any draft comparison is read against. Without controls the score is uninterpretable.
- **Judging.** Blind LLM judges see pairs and answer: same author, yes or no, confidence 1-5, with the deciding cue named. Judges are lens-split (lexical choice, rhythm and sentence shape, structural habits) rather than replicated, per the shared-blind-spot caveat.
- **Score.** Discrimination rate above the control floor. At-floor means judges cannot tell draft from corpus: high fidelity. Well above floor means the draft has a detectable signature, and the named cues say what to fix.
- **Loop use.** The score is cheap and repeatable, so it can drive extract-draft-edit iterations and give the stopping rule #51 asked for: stop when discrimination sits at the control floor across two consecutive drafts.

Track B needs real code (sampling, blinding, bookkeeping, scoring): §6.

### 4.3 What the two tracks close

Track A catches joint-level reader failures at the gate where evidence actually lands. Track B catches voice drift without the writer reading every draft. The known gap that remains: neither measures section-scale pacing against the *corpus* (Track A measures it against reader comprehension, which is the consumer that matters). Stylometric corpus-distance measures (function words, char n-grams; decoupling spec §8 residual risk 1) stay follow-up work, adopted only if Track B's named cues prove too coarse to act on.

## 5. Representation (#51 Q2): constraints in rules, generation from passages

### 5.1 Split the jobs

The decomposition diagnosis says the voice file fails as a generation source because rules and atomized exemplars are marginals. But the rules file is good at what it actually holds: iron rules, cut patterns, the never-list, §10 exemptions. Constraints. Keep them there.

Generation grounding moves to continuous prose: at drafting time, the prose-drafter dispatch carries 2-4 whole passages from the writer's corpus, matched to the current section's register, alongside the rules. The drafter imitates joint structure directly instead of reconstructing it from named parts. Context cost is not a constraint; the dispatch is already inlined (#51 body, Q2).

### 5.2 Passage retrieval at draft time

- Corpus lives adjacent to the project (the per-project layout already has `samples/`; the voice library keeps a per-voice corpus pointer for cross-project reuse).
- Passages are indexed once per corpus: register tag, topic keywords, length, source file. The index is a small JSON sidecar; no embeddings (retrieval is a filter plus a diversity pick, not similarity search).
- `[writing mode]` requests passages per section: register from the section's plan entry, 2-4 passages, at least two source files when the corpus allows (single-file dominance is the #51 starved-corpus failure).
- Retrieved passages enter the dispatch as exhibits with provenance comments, same convention as today's worked paragraphs.

Worked paragraphs stay as the fallback when no corpus is adjacent (shipped voices, corpus-less projects).

### 5.3 Why not just more worked paragraphs

Scaling exhibits inside the voice file was Q2's other candidate. Rejected as the primary path: the exhibit unit is still the paragraph, hand-picked once at extraction time, frozen thereafter. Retrieval picks per section, per draft, register-matched, and the corpus stays the single source of truth instead of a second copy inside the voice file. The 2026-07-04 session also showed the failure that worked paragraphs cannot cover lives across sections; that is Track A's job (§4.3), not the exhibits'.

## 6. The code fork (#51 Q3): in-repo

### 6.1 What needs real code

Prompt-defined subagents cannot do: Track B's sampling, blinding, control bookkeeping, and scoring; the corpus index and retrieval filter; per-register floor accounting at intake (§8). All are mechanical, deterministic, and testable. STATUS already recorded Q3 "leans yes"; this spec confirms it.

### 6.2 Recommendation: in-repo, as a `sourced voice` subcommand family

**Recommendation: improve in place. No standalone tool.** Reasoning:

1. Every consumer is a sourced mode or agent: the writing-mode dispatch consumes retrieval, the extract-draft-edit loop consumes Track B, the extractor consumes intake floors. A standalone tool would ship an interop layer for exactly one consumer and exactly one user.
2. The project layout the code needs (`samples/`, `config/voice.md`, the voice library) is sourced's own. A separate tool would import sourced's conventions or duplicate them.
3. The CLI already has the infrastructure code needs: install plumbing, validators, golden tests, CI. A spin-out re-buys all of it.
4. VISION: private tool, not a product. A standalone voice tool is a product with zero external demand evidence. The same logic that declined single-binary distribution applies.

Shape: `sourced voice index <corpus-dir>`, `sourced voice retrieve --register X --n 3`, `sourced voice ab <corpus-dir> <draft>`. LLM steps inside `ab` (the judges) call the API directly from the CLI with pinned prompts, which is Direct-API offload candidate 1 resolved as a byproduct.

### 6.3 Consequences for the gated entries

- **Direct-API offload, candidate 1:** subsumed. `sourced voice ab` is the direct-API path; the entry's candidates 2-3 are untouched.
- **Scoped subagents:** the long-run home of extraction is `sourced voice extract` (option 1 shape); until then the aggressive-description stopgap is not worth a PR. The entry's trigger has fired (this recommendation exists); its answer is "resolve by migration, no interim work."
- **Per-agent model selection, voice half:** judge and extraction model choice becomes CLI config (the config-overlay shape it already favored).
- **Voice-merging:** declined 2026-07-06; if ever reopened, it designs against the retrieval representation, not the rules file.

## 7. Coverage (#51 Q4): multi-register without dropped registers

The ~/writing failure: `multi_register=primary` dropped the personal-essay register and delegated it to a sibling voice file that no longer existed. Registers the corpus covers must not silently vanish.

Changes:

1. **`segmented` becomes the recommended route for blended corpora in real use** (one file, rules tagged by register inline). The ~/writing phase-3 voice file already has this shape (sub-register taxonomy, register-tagged rules, per-register worked paragraphs) and it held for the register it was used in on 2026-07-04. `split` remains the default dispatch value for safety; the report's routing section now names segmented as the single-writer recommendation.
2. **Per-register floors** (§8): a register below floor is not extracted, and is not delegated anywhere. It lands in a new `## Uncovered registers` section of the voice file: register name, evidence mass found, floor it missed. Absence becomes inspectable.
3. **No sibling delegation.** A voice file never points at another voice file as the home of a register. The 2026-07-04 evidence is that such pointers rot.
4. Persuasion stays unmodeled (decoupling spec §8, residual risk 5). Out of scope here; noted for the record.

## 8. Intake (#51 Q5): corpus floors and the dimension support map

Existing floors (3 files, 5,000 words, intake honesty from #50) stay. Added:

- **Per-register floor:** a register is extractable at 2+ files and 1,500+ words within that register. Below floor: `## Uncovered registers`, per §7.
- **Dimension support map:** the extractor's report gains `### Dimension support map`, one row per voice-file section: supported / thin / unsupported, with the corpus evidence count. The ~/writing failure this fixes: `Anchors: TBD` appeared with no intake-time warning that the corpus was topically too narrow to fill it (#51 body). Anchors and Analogies require 2+ topics; the map says so at intake instead of leaving a hole discovered at draft time.
- **Demand versus repair:** the extractor demands (rejects, warns, leaves TBD with a named reason). It never repairs silently: no synthetic exemplars, no padding a register with near-register files. Matches the existing "never fabricates rules or exemplars" contract.
- Guidance lands in `docs/VOICES.md`: minimum corpus (3 files, 5,000 words, 2+ topics), per-register minimums, and what each dimension needs from the corpus.

## 9. Consumer map

| Consumer | Relationship to the primitive | When |
|---|---|---|
| Writer at the post-format gate | Invokes the skill directly; reads the artifact | On ship-worthy drafts, now |
| #29 reader-simulation critics | The primitive **is** this consumer; no separate design | Closed into this spec |
| Peer review mode (ROADMAP) | Rubric-persona parameterization: one persona per rubric axis, same protocol, same artifact | Act when its ROADMAP trigger fires |
| Revision mode (ROADMAP) | Consumes the artifact's RR/RN ids as its comment input | Act when a real revision round arrives |
| #51 extract-draft-edit loop | Track A per-section numbers plus Track B score drive iteration and stopping | With `sourced voice ab` |
| Agent Teams (ROADMAP) | Evaluated as substrate, not adopted (§3.5) | Only on consolidation failure |

## 10. Decomposed issues

For filing after this spec merges. Ordered; 1 and 2 are independent of each other after this spec, 3 depends on 2's plumbing decisions only loosely, 4 is extractor-side and independent.

1. **Ship `staged-reader-review` as a bundle skill with the review artifact schema.** Codify the prototype into `src/sourced/data/skills/staged-reader-review/`; add the artifact schema (§3.3), the upstream-gate-artifact pre-flight (§3.4, the #33 attachment), and the formatting-mode exit-gate pointer. Effort M. Closes the reader-simulation half of #29; #33 gets its option-2 record.
2. **`sourced voice` subcommand skeleton plus corpus index.** CLI plumbing, `voice index`, the JSON sidecar schema, per-register accounting shared with intake floors. Effort M.
3. **Blinded author-verification A/B: `sourced voice ab`.** Sampling with register/length matching, control pairs, lens-split judges via direct API, discrimination score against the control floor, report format. Effort M. Direct-API offload candidate 1 resolves here.
4. **Passage retrieval at draft time.** `voice retrieve` plus the writing-mode dispatch wiring (2-4 register-matched passages as exhibits with provenance). Effort L: touches the drafting protocol, needs a real paper to validate against.
5. **Voice extraction v2 intake and coverage.** Per-register floors, `## Uncovered registers`, `### Dimension support map`, no-sibling-delegation rule, segmented-recommendation note in VOICES.md. Effort M.
6. **Revision-mode input schema note.** One-page addition when revision mode's trigger fires: map RR/RN ids to the revision-cycle log. Effort S. Deferred until the trigger.

Issue #51 closes when this spec merges and issues 1-5 are filed (its deliverable: design doc, fork recommendation, decomposed list). Issue #29 stays open as the payload critic's home (queue row 2) and closes when that PR lands; its reader-simulation half is issue 1.

## 11. Accepted residual risks

1. **Same-base-model readers and judges.** Persona watch-lists and judge lenses are the mitigation, control pairs the calibration; a shared blind spot can still pass both tracks. Named, not solved.
2. **Track B judge prompts are load-bearing.** A leading judge prompt manufactures discrimination. Control pairs catch drift over time but not a systematically biased prompt; prompt review at PR time is the only gate.
3. **Retrieval quality is a filter, not semantics.** Register-tag plus keyword filtering can retrieve topically wrong passages for an unusual section. Acceptable: the drafter imitates structure, not content, and provenance comments keep the writer able to spot a bad pick.
4. **One-session evidence.** Every quantitative claim here traces to a single register, style, and paper. The design assumes the mechanisms generalize; the numbers (floors, K, thresholds) are starting points, revisable on the second real paper.
5. **Section boundaries are judgment.** Lockstep review inherits whatever sectioning the splitter chooses; a bad split hides a boundary defect. The natural-units rule from the prototype is guidance, not enforcement.

## 12. Sequencing

Issue 1 first (it is transcription plus schema; it immediately upgrades every future paper session). Issues 2-3 next as one code arc (index, then ab). Issue 4 after a real paper is available to validate retrieval against. Issue 5 rides with the first extractor touch after 2. No phase gates between them beyond ordinary PR review; none of this touches the citation pipeline.
