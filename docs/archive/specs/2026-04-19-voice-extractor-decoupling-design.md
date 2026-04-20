# Voice-extractor skeleton decoupling

- **Date:** 2026-04-19
- **Status:** Shipped 2026-04-19 via PR #7.
- **Scope:** Decouple voice-extractor's skeleton from the academic register; ship 6 register-specific skeletons + reorganize each into 4-axis structure
- **Out of scope:** Classifier feature-set expansion (LIWC / function words / char n-grams), weighted-blend continuous-register composition, post-generation style-fidelity evaluation, new subagent capabilities

## 1. Problem

User report: `voice-extractor` produces voice files that read "too academic" when the source corpus is a school-essay style (tonally casual, structurally academic, dimensionally narrative).

Prompt-engineer audit confirmed the root cause: `agents/voice-extractor.md:22` hardcodes `skeleton_path: ~/.claude/voice/academic.md`. The register classifier at step 2 outputs a label (academic / technical / casual / journalistic / mixed) but nothing in the workflow uses the classification to route to a different skeleton. The `academic.md` file serves two jobs: the shipped academic voice AND the default derivation skeleton. Its non-iron sections carry academic-register prose (e.g., `academic.md:58`: "Academic prose defaults to longer connected sentences") that leaks into every derived voice through the workflow's "mirror the skeleton's density" directive.

Prior-art survey (Biber's Multi-Dimensional Analysis; Oxford 2018 student-writing MDA; Sudowrite's `My Voice`; Stylo/JGAAP/LIWC literature) confirmed:
- Register is legitimately multi-dimensional; a hard-skeleton approach discards the blend case
- A narrative/reflective cluster is distinct from casual or academic and maps directly to common student writing (college essays, reflection pieces)
- Iron-rule-as-global-prohibition pattern is principled and underexplored in commercial tools
- The skeleton-per-register pattern is novel; Sudowrite's closest analog (fine-tune-on-samples) hides the voice model and isn't auditable

## 2. Decisions

### 2.1 Six shipped skeletons

Replace the single `templates/voices/academic.md` with a family of 6 register-specific skeletons. Each owns one register's calibration prior; `hybrid.md` is an explicit register-neutral fallback for blended corpora.

- `academic.md` — research papers, essays, dissertations (existing; rewrite non-iron prose)
- `casual.md` — conversational, blog posts, informal (new)
- `technical.md` — procedural, documentation, domain-terminology (new)
- `journalistic.md` — inverted-pyramid, mid-register formal (new)
- `narrative.md` — first-person, reflection, scene/past-tense-heavy (new)
- `hybrid.md` — register-neutral fallback (new)

### 2.2 Four-axis section structure

Each skeleton reorganizes into 4 top-level headers. Captures Biber-style dimension orthogonality without introducing file-composition complexity.

- `## Iron rules` — global prohibitions (CLAUDE.md §10 transclusion + any `[iron]` line); never calibrated; `## §10 exemptions` nests here as a carve-out
- `## Tone` — what the voice sounds like (register, stance, rhythm, vocabulary, audience-orientation)
- `## Structure` — how the prose is organized (connectedness, pacing, argument-building)
- `## Dimension` — unique author habits (anchors, punctuation quirks, formatting)

The existing sections in `academic.md` re-parent under these headers without content rewrite (beyond the non-iron register-shift documented in §7 below):

| Current section | New parent |
|---|---|
| Iron rules | `## Iron rules` |
| §10 exemptions | `## Iron rules` |
| Core Rule (iteration loop) | `## Structure` |
| Stance | `## Tone` |
| Sentence Structure | `## Tone` |
| Sentence Connectedness | `## Structure` |
| Paragraph Flow | `## Structure` |
| Information Pacing | `## Structure` |
| Concept Setup | `## Structure` |
| Exploratory vs Verdict Tone | `## Tone` |
| Thinking Out Loud | `## Tone` |
| Building Arguments | `## Structure` |
| Analogies and Anecdotes | `## Dimension` |
| Including the Reader | `## Tone` |
| Brevity Rules — weak adverbs | `## Tone` |
| Brevity Rules — 3-5 sentences per paragraph | `## Structure` |
| Punctuation | `## Dimension` |
| No Preamble | `## Tone` |
| Formatting | `## Dimension` |

The `Brevity Rules` section splits; its weak-adverbs subrule lives under Tone, its paragraph-length subrule under Structure.

### 2.3 Confidence-band routing (auto-route, no new halts)

Classifier expands from 4 labels → 5 (adds `narrative`). Workflow step 2's existing `mixed` outcome stops halting; instead routes to `hybrid.md`.

Routing decision:
- `register` param provided → use `templates/voices/<register>.md`. `register-mismatch` halt still fires only when corpus flatly contradicts a provided label.
- `register` param omitted → classify:
  - **≥ 85% single register** (one of academic / casual / technical / journalistic / narrative) → route to that skeleton
  - **< 85% on any single register** → route to `hybrid.md`

No `register-borderline` halt. No `mixed-register` halt. Auto-route handles both.

### 2.4 Hybrid.md authored lean (no exhaustive menu)

`hybrid.md`'s non-iron prose states the underlying rule WITHOUT register framing and directs voice-extractor to the corpus. Does NOT enumerate per-register patterns as a menu (that would reproduce the skeleton-bias failure mode at the hybrid level).

Example Sentence Connectedness section in `hybrid.md`:

```markdown
### Sentence Connectedness

Sentences hand off. Each connects to the previous through a causal,
contrastive, or sequencing relationship. How the connection is marked
varies (explicit connectives, semicolons, short-sentence juxtaposition,
restatement). The baseline rhythm varies too (some writers chain short,
some build long).

Voice-extractor: set marker style AND baseline rhythm from corpus
evidence. Do NOT default to any register-specific shape; extract what
the corpus shows. If the corpus is thin on this section, emit TBD
rather than impose a pattern.
```

Register-specific skeletons (`academic.md`, `casual.md`, etc.) stay register-specific in their framing — each anchors voice-extractor's interpretation for that register. Only `hybrid.md` is lean.

### 2.5 Register-drift report section

Add a new `### Register drift` section to voice-extractor's report. Surfaces the classification breakdown when any non-dominant register had meaningful presence:

```markdown
### Register drift
Classified as academic (78%). Minority presence: narrative 18%, casual 4%.
If your intent is narrative or reflective voice, re-run with
`register: narrative` and `overwrite: true`.
```

Silent when the dominant register is ≥ 95% clean.

### 2.6 Single voice.md file per project (no file-level splitting)

Considered splitting the project's `voice.md` into `tone.md / structure.md / dimension.md` (three files per project composed at read time). Rejected: composition complexity outweighs the architectural clarity gain. Sections inside voice.md are already section-scoped; voice-extractor reads each section's corpus evidence independently, so a single file with 4-axis top-level headers captures the orthogonality without composition overhead. File-level splitting stays available as a future architectural move if the tool grows to cover more writing contexts.

## 3. Skeleton authoring approach

The 5 new skeletons are **hand-authored**, not generated. Each takes ~1 hour using `academic.md` (post-reorg) as the structural template:

1. Copy `academic.md` (now 4-axis structured)
2. Preserve `## Iron rules` section + `## §10 exemptions` verbatim
3. Rewrite every non-iron section's prose for the target register
4. Replace every academic-specific exemplar with a register-appropriate exemplar (not user-specific — these are shipped templates; user-specific content only appears in derived `~/.claude/voice/<name>.md` files)
5. Update the H1/intro paragraph to declare the register
6. `{{USER}}` tokens stay where `academic.md` carries them (install.sh renders per-project)

`hybrid.md` is the hardest to author — non-iron sections need register-neutral rule statements with explicit anti-bias instruction (§2.4 pattern).

Per-skeleton register anchoring:

| Skeleton | Non-iron tone-section prior | Non-iron structure-section prior |
|---|---|---|
| academic | Longer connected sentences; hedged stance; formal lexicon | Multi-clause connectives; formal argument structure |
| casual | Short direct sentences; contractions; first-person ease | Explicit connectives; paragraph-as-beat; short argument arcs |
| technical | Imperative voice; minimal ornament; domain terminology | One instruction per sentence; parallel structure; bulleted sequences |
| journalistic | Mid-register formal; active voice; lede-first | Inverted-pyramid graph structure; news-peg argumentation |
| narrative | First-person; scene-aware rhythm; past-tense-heavy | Scene/reflection paragraph structure; chronological or thematic arcs |
| hybrid | Corpus-derived; no register prior | Corpus-derived; no register prior |

## 4. voice-extractor.md changes

Concrete edits to `agents/voice-extractor.md`:

### 4.1 Inputs (line 20)
`register` enum expands to `academic | technical | casual | journalistic | narrative`. Default remains "classify if omitted."

### 4.2 Inputs (line 22)
`skeleton_path` default removed. Skeleton selection is now driven by register via lookup `~/.claude/voice/<register>.md`. Param remains for advanced override (user wants to derive against a custom skeleton they authored); no default hardcoded.

### 4.3 Workflow step 2 (line 40)
Classifier enum expands to 5 registers + `mixed`. New behavior: `mixed` no longer halts; sets skeleton to `hybrid.md` and proceeds. Classifier signal expansion: add narrative markers (first-person pronoun frequency, past-tense-narrative constructions, scene/dialogue indicators) to the existing signals. Threshold gate:
- Top register ≥ 85% → route to matching skeleton
- Top register < 85% → route to `hybrid.md`

### 4.4 Workflow step 5 (line 46)
"Read the section's purpose from the skeleton prose" remains. No bug now — the prose matches the register, and hybrid.md's prose is anti-bias.

"Mirror the skeleton's density" directive (line 51) stays. Each skeleton is already register-calibrated; matching density is register-appropriate.

### 4.5 Rejection categories
Remove `mixed-register` (no longer halts). Keep `register-mismatch` (user passed conflicting `register` param; corpus flatly contradicts). All others unchanged.

### 4.6 Report format — new section
Add `### Register drift` between `### Register` and `### Sample stats`:

```markdown
### Register drift
<only emit when dominant register is < 95% clean>
Classified as <top> (<top-pct>%). Minority presence: <runner-up> <pct>%,
<third> <pct>%.
If your intent is <runner-up> voice, re-run with
`register: <runner-up>` and `overwrite: true`.
```

Silent when classification is dominant (≥ 95%).

## 5. Shipped-name reserved list

`voice-extractor.md` Preflight step 3 (shipped-name collision) expands:

```
Shipped names: academic, casual, technical, journalistic, narrative, hybrid
```

`install.sh` copies every `templates/voices/*.md` into `~/.claude/voice/` on every `--global-only` invocation (existing loop at line 205-210). Adding 5 new shipped voice files is automatic — no install.sh logic change required.

## 6. Migration

Existing user-generated voice files at `~/.claude/voice/<custom-name>.md` stay untouched. They were generated against the pre-decoupling `academic.md` skeleton; we do not regenerate without user opt-in.

Shipped `~/.claude/voice/academic.md` gets refreshed on next `install.sh --global-only` (normal behavior) — its content changes from "user-specific academic voice tuned to {{USER}}" to "register-neutral-per-register academic skeleton." Users who ran `install.sh --voice academic --force` to adopt the shipped academic voice as their project voice will see a content refresh on next install; this is the designed behavior (shipped voice is not guaranteed stable across versions).

voice-extractor's next-steps report (currently at line 118) gains a one-line addition:

```markdown
If you previously generated a voice against the pre-decoupling `academic.md`
skeleton, re-run voice-extractor with `overwrite: true` to pick up the new
routing and register-appropriate skeleton selection.
```

No automated migration; the tool doesn't rewrite user files.

## 7. Docs changes

- `docs/VOICES.md` — document the 6 skeletons, the 4-axis section structure, routing behavior, `register` param options, hybrid.md's lean contract
- `ARCHITECTURE.md` — voice-system section gains a paragraph on skeleton-per-register and the 4 axes
- `README.md` — `## What it does differently` bullet about voice preservation updates to mention 6-skeleton calibration; not a rewrite

## 8. Accepted residual risks

Named so future readers know these were seen and deprioritized.

1. **Classifier feature-set is thin.** Current signals (sentence length, contraction frequency, punctuation, vocabulary register) plus added narrative markers may still misclassify edge corpora. Follow-up: add LIWC-style word-category counts, function-word frequency, character n-grams (stylometric workhorses per Stylo / JGAAP literature). Not in this spec.
2. **Hybrid.md authorship is the load-bearing skeleton.** If hybrid.md's non-iron prose leaks register bias despite the anti-bias instruction, the failure mode from `academic.md` reappears at `hybrid.md`. Mitigation: careful authoring + review before merge; the spec's §2.4 example is the template.
3. **85% threshold is ad-hoc.** Biber's continuous-dimension framework would support a weighted-blend approach; we're using discrete bins for legibility. If the threshold proves wrong in practice (too many corpora falling into hybrid because 85% is too high), revise in a follow-up.
4. **No style-fidelity evaluation.** Prior art uses cosine similarity on style embeddings; we have no post-generation check. Out of scope; track for later.
5. **Persuasive / rhetorical dimension not covered as an axis.** Biber D4 (overt persuasion) is orthogonal to register. A personal-statement-with-persuasion corpus will route to `narrative.md` (captures structure) or `hybrid.md`; the persuasion lean is not separately calibrated. Future work: stance/persuasion axis modifier inside each skeleton, or a 7th `persuasive.md` skeleton.
6. **Literary fiction / poetry / screenwriting are out of scope.** Different failure modes (multi-voice narration, formal structure, meter) than voice-extractor is designed for; sourced is an academic-writing tool.

## 9. Follow-up work (out of this spec)

- Classifier feature-set expansion (residual risk 1)
- Stance / persuasion axis as a dimensional modifier (residual risk 5)
- Style-fidelity post-generation evaluation
- `business.md` / `scientific.md` skeletons if usage patterns show demand (currently both fold into existing skeletons adequately)
- Weighted-blend continuous-register composition if discrete bins prove too coarse

## 10. Implementation sequencing (one PR)

Unlike the CSL migration (5 PRs), this shift fits one PR:

1. Reorganize existing `academic.md` into 4-axis structure (content move; no prose rewrite)
2. Author the 4 new register-specific skeletons (casual, technical, journalistic, narrative) using `academic.md` as the structural template
3. Author `hybrid.md` (lean, anti-bias non-iron prose)
4. Update `agents/voice-extractor.md` per §4 (inputs, workflow, rejection categories, report)
5. Update `install.sh` shipped-name reserved list per §5 (one-line change)
6. Update docs per §7
7. Test: dispatch voice-extractor against 3 representative corpora (clean-academic, school-essay-blend, pure-casual) and verify skeleton selection + register-drift reporting

Single PR; no phase split. Total effort estimate: ~6-8 hours, front-loaded on skeleton authoring.
