# Voice rules

Voice calibration for blended-register corpora. Encodes the UNDERLYING rules (connectedness, pacing, concept setup, iron prohibitions) without committing to a register's specific framing. Use as the base skeleton when the writing-samples corpus spans registers (e.g., school essays that are structurally academic but tonally casual; blog posts that mix reflective and journalistic patterns).

`voice-extractor` selects `hybrid.md` automatically when the classifier finds no single register above 85% of the corpus AND `multi_register=segmented`. Other `multi_register` settings (`split`, `primary`) route differently — see `data/agents/voice-extractor.md § Multi-register routing`.

For a register-specific calibration (academic papers, casual blog posts, technical documentation, journalistic pieces, narrative reflection), start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 9 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

**Note for downstream readers.** This skeleton is filled in by `voice-extractor` from a blended-register corpus. Any `TBD — derived from corpus` marker that remains in the rendered file signals the corpus did not settle that rule; treat such markers as "fall back to general register judgment" rather than a hard rule, and apply the surrounding prose guidance as context.

Two TBD forms can appear in a voice file, distinguished by suffix: `TBD — derived from corpus` (this skeleton's placeholder — voice-extractor may fill it in, or the rendered file keeps it as a general-register-fallback signal) and `TBD — samples did not surface this pattern. Fill in or delete.` (voice-extractor's emit for a section the corpus could not settle — requires {{USER}} action before the voice is considered complete). Both prefix with `TBD —` so downstream readers can grep a single pattern for all unfilled sections; the suffix disambiguates the reason and the required response. Do not collapse the two suffixes into one form.

## Sub-register taxonomy

Hybrid voice files are produced from cross-register corpora; the sub-register taxonomy is therefore corpus-specific rather than fixed. `voice-extractor` populates this section with the register clusters identified in the corpus, naming each cluster's dominant register tag and its share of the word count. A typical hybrid voice covers 2–3 sub-registers; rules below are tagged with the sub-register where they apply strongly, using the register tags `[register: <tag>]` form (e.g., `[register: academic-report]`, `[register: casual-personal-essay]`). Untagged rules apply across the hybrid corpus.

When the corpus is genuinely cross-register and {{USER}} accepts a single hybrid file, the segmented extraction produces this voice file. When {{USER}} prefers separate voice files per cluster, voice-extractor returns `multi-register-corpus` with a cluster manifest and {{USER}} re-dispatches once per cluster — see the `split` mode in `data/agents/voice-extractor.md`.

**Sub-registers identified in corpus:** TBD — derived from corpus. voice-extractor lists detected register clusters with word-count shares.

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field, choosing from the sub-register tags identified above. The declaration filters which rules below apply. If the brief does not specify, surface the ambiguity to {{USER}} rather than guessing.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

In a hybrid voice file, exhibits are populated per detected sub-register. If the corpus has 2 register clusters, 2 exhibits; 3 clusters, 3 exhibits.

### Exhibit 1 — primary cluster

TBD — derived from corpus. voice-extractor populates with a paragraph-scale exhibit from the corpus's largest register cluster, with provenance header and per-sentence annotation.

### Exhibit 2 — secondary cluster

TBD — derived from corpus. voice-extractor populates if a second register cluster exists in the corpus; otherwise this section is omitted.

### Exhibit 3 — tertiary cluster

TBD — derived from corpus. voice-extractor populates if a third register cluster exists in the corpus; otherwise this section is omitted.

Voice-extractor replaces these placeholders with corpus-derived paragraphs at extraction time. The annotation block on each exhibit names the sub-register tag the exhibit belongs to.

## Tone

### Stance

**Rule.** State views clearly. How hedged vs. how direct varies by register — academic prose hedges more, technical prose is direct, narrative prose reflective. voice-extractor: set the stance calibration from corpus evidence per sub-register cluster. Do NOT default to a specific register's hedging level; emit register-tagged rule blocks where the corpus shows different stance discipline by cluster.

**Exemplars:** TBD — derived from corpus, populated per sub-register cluster.

### Sentence Structure

**Rule.** Sentences vary in length and shape across registers. Academic prose defaults long; casual short; technical imperative; narrative scene-aware; journalistic inverted. voice-extractor: set the baseline sentence-length rhythm from corpus evidence per sub-register cluster. Reserve short/punchy forms for emphasis at pivots regardless of baseline.

**Exemplars:** TBD — derived from corpus.

### Exploratory vs Verdict Tone

**Rule.** Exploration dominates in narrative and academic reflection; verdict dominates in reporting and technical reference. voice-extractor: identify where the corpus falls on this axis per cluster and calibrate. Do not default to any register's balance.

**Exemplars:** TBD — derived from corpus.

### Thinking Out Loud

**Rule.** Present in narrative and casual prose; rare in reporting and reference documentation. voice-extractor: if the corpus shows this pattern in any cluster, calibrate exemplars; if absent, emit TBD rather than adding it.

### Including the Reader

**Rule.** First-person, second-person, third-person each dominate in different registers. voice-extractor: identify which pronoun-perspective each corpus cluster uses and set per-cluster baselines.

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." Ground claims with numbers or comparisons, not vague qualifiers. "Many papers have been retracted for manipulation" becomes "In 2019, 23% of retracted papers had been cited more than 100 times." This rule applies across registers; the THRESHOLD for grounding may vary (technical prose grounds with units; narrative prose grounds with sensory detail), but the cut-the-vague-qualifier discipline holds.

### No Preamble

**Rule.** Never start a paragraph or turn with "Great question!" / "That's interesting." / "Let me..." Open on substance. Applies across all registers in the hybrid corpus.

## Structure

### The Core Rule

**Rule.** Every word fights to stay. If a sentence adds nothing, cut it. If two sentences say the same thing differently, merge them into one shorter sentence. No filler, no padding, no repetition.

**Concision is a means, not an end.** The baseline rhythm varies by register — academic prefers medium-to-long connected prose; casual prefers shorter; technical prefers parallel imperatives. Chiseling below the cluster-specific baseline is a failure mode. Stranded verbs and reduced-relative stacking trip the reader regardless of register; see `## Cut patterns`.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list.)
- Does it earn its place in the argument?
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. First drafts are raw material, not output.

### Sentence Connectedness

**Rule.** Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing relationship (explicit connectives, parallel structure, or implicit logical flow). How the connection is MARKED varies — explicit connectives, semicolons, short-sentence juxtaposition, restatement.

voice-extractor: set the marker style AND baseline rhythm from corpus evidence per sub-register cluster. Do NOT default to "longer connected sentences" or any register-specific shape; extract what the corpus shows. If the corpus is thin on this section, TBD rather than impose a register-specific pattern.

**Exemplars:** TBD — derived from corpus per cluster.

### Paragraph Flow

**Rule.** Paragraphs set up, develop, and hand off. End a paragraph on a transition to the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a connective, a reference back, or a concept the prior paragraph positioned.

How the handoff is MARKED varies by register: academic uses explicit connectives ("While," "Moreover"); casual uses shorter bridges; narrative uses sensory callbacks; journalistic uses inverted-pyramid ordering.

voice-extractor: set the handoff style from corpus evidence per cluster. TBD if unclear.

### Information Pacing

**Rule.** Claim density varies by register. Academic prose can pack multiple claims per paragraph; technical prose emits one claim per sentence; narrative prose alternates heavy and light. voice-extractor: identify the pacing pattern the corpus shows per cluster and calibrate.

### Concept Setup

**Rule.** Introduce specialized terms or domain references with appropriate framing on first use. The DEGREE of setup varies — academic prose can run longer definitions; casual prose uses parentheticals; technical prose uses formal definition blocks; narrative prose uses scene. voice-extractor: set the setup convention from corpus evidence per cluster.

### Building Arguments

**Rule.** Develop reasoning. Address counterpoints. How formally — full objection-response vs. casual "yeah, but" — varies by register. voice-extractor: set the argumentation style from corpus evidence per cluster.

### Paragraph Length

**Rule.** Paragraph length varies dramatically by register. Journalistic: 1–3 sentences. Casual: 2–4. Academic: 3–5. Narrative: highly variable. voice-extractor: measure the corpus's paragraph-length distribution per cluster and set the baseline accordingly.

### Reduced Structures and Parse Load

**Rule.** A reduced relative clause (dropped "that"), a cataphoric pronoun, or a long noun-phrase subject is each acceptable on its own. Two or three stacked in one sentence force the reader to backtrack. Limit yourself to one parse-load element per sentence; if the argument needs more, split the sentence. This rule applies across registers in the hybrid corpus. See `## Cut patterns > reduced-relative-stacking`.

### Weak Nominalizations

**Rule.** Prefer verbs over nouns made from verbs. Prefer concrete subjects over abstract ones. A chain of abstract nouns reads as institutional padding even when every word passes the Core Rule's cut test. This rule applies across registers in the hybrid corpus.

## Dimension

### Analogies and Anecdotes

**Rule.** Connect abstract points to specific patterns. The TYPE of analogy varies — academic uses technical illustrations; casual uses everyday objects; technical uses system analogies; journalistic uses anecdotes about named people; narrative is itself anecdote. voice-extractor: identify the analogy type the corpus uses per cluster and calibrate.

**Anchors:** TBD — derived from corpus. voice-extractor populates with cross-cluster recurring touchstones if the corpus has them; otherwise leaves TBD.

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*, not a comma, colon, or period-fragment swap that preserves the mid-clause-interruption rhythm. Use this section only for author-specific punctuation habits the corpus shows beyond the §10-governed patterns.

voice-extractor: identify what the corpus uses characteristically per cluster and describe the pattern. An author-specific rule that contradicts §10 must be stated explicitly; silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns:** TBD — derived from corpus.

### Formatting

**Rule.** Markdown formatting density varies by destination. voice-extractor: identify the corpus's formatting conventions per cluster (bold frequency, italics use, bullet-point density, code-block presence) and set the baseline.

TBD — derived from corpus.

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 7 explicitly flag. Each pattern carries a canonical ID; `failures_dir` before/after pairs populate author-specific instances at extraction time. Shipped patterns below are register-agnostic — they apply across the hybrid corpus regardless of cluster.

Hybrid voice files inherit all 6 canonical academic cut patterns because a hybrid corpus may contain academic-register samples; if the corpus has no academic cluster, the academic-specific patterns (`first-person-commitment-in-academic-report`, `citation-atomization`) are dropped at extraction time and noted in the report's `### Excluded patterns` section.

### aphoristic-closure

**Pattern.** Paragraph ends on a crisp, rhetorically-balanced pronouncement that substitutes rhetoric for reasoning.

**Why it reads as AI.** The shape sounds thesis-like without doing argument work. The reader has been given a feeling of resolution, not actual resolution.

**Fix.** Restructure to `closure-type: transitional`, `synthesis`, or `question-out`. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision, producing a sentence that reads as a fragment of a longer thought.

**Why it reads as AI.** The cut-bias of the Core Rule has fired past the readability threshold. The sentence is grammatically optimal and word-count minimal; it trips the reader on first read.

**Fix.** Restore the stranded complement.

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs stacked across clauses without a concrete agent or active verb.

**Why it reads as AI.** Inverse failure mode of `compression-stranded-verb`: when the cut-bias stops firing, prose expands into institutional-noun cascades that disconnect agent from action.

**Fix.** Rewrite around a concrete subject + active verb.

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in a single sentence, often combined with a cataphoric pronoun.

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack. Same root as `compression-stranded-verb` — optimization for word count at the cost of parseability.

**Fix.** Restore "that" and/or split the sentence.

### first-person-commitment-in-academic-report `[register-drift: personal-essay → academic-report]`

**Pattern.** First-person stance markers ("I think," "I believe," "my claim is") appearing in `academic-report` or `prospectus` prose. Applies only when the hybrid corpus contains an academic-register cluster.

**Why it reads as AI.** When a voice file is extracted from a multi-register corpus and unioned, personal-essay stance rules bleed into formal-register drafting. The resulting prose reads as undergraduate-essay register where the genre expects scholarly-voice.

**Fix.** Rewrite as third-person declarative. First-person only in process statements about the paper itself.

### citation-atomization `[register: academic-report, prospectus]`

**Pattern.** Fine-grained Pandoc IDs for the same domain treated as separate sources when a human writer would merge. Applies only when the hybrid corpus contains an academic-register cluster.

**Why it reads as AI.** Granular IDs betray the `source-finder` shard architecture. A human writer recognizes that multiple pages of one site or multiple entries of one dictionary are one citation.

**Fix.** At `[formatting mode]` time (or at drafting time for inline parentheticals), consolidate IDs that resolve to the same References entry.

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

## §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
