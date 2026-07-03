# Voice rules

Voice calibration tuned to {{USER}}'s casual writing — blog posts, personal essays, conversational pieces. Encodes conversational-register defaults under the phase-3 sub-register contract: tone (first-person ease, contractions, short sentences), structure (explicit connectives, short argument arcs), dimension (analogies close to experience, inline punctuation, light formatting). Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 8 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Sub-register taxonomy

Casual writing is not a single register. This voice covers three sub-registers; rules below are tagged with the sub-register where they apply strongly. Untagged rules apply across all three.

- **`personal-essay`** — first-person reflective prose, narrative-driven, thesis-light or thesis-late. Examples: blog posts about an experience, mini-memoir pieces, "what I learned from X" reflections.
- **`commentary`** — opinion take on something current or specific, named stance, argument-forward. Examples: Substack-style posts taking a position, opinion blog posts, conversational responses to ongoing discourse.
- **`process-post`** — "how I built X / what I learned from Y" walkthrough, first-person setup + concrete steps + reflection. Examples: technical-adjacent how-to posts, recipe-style narratives, project retrospectives.

When the corpus spans multiple sub-registers, `voice-extractor` produces one voice file per sub-register rather than unioning them; see `data/agents/voice-extractor.md § Multi-register routing`. Unioning is the documented failure mode (a `commentary` sharper-stance rule imported into `personal-essay` reflective prose produces over-emphatic essays).

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field. The declaration filters which rules below apply. If the brief does not specify, assume `personal-essay` (the casual default) and flag the assumption in the prose-plan.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

### Exhibit 1 — personal-essay (illustrative)

> The first time I tried to bake bread without a recipe, the loaf came out dense and grey. I'd watched my grandmother do it a hundred times, flour and water and a pinch of salt and the dough's surface tightening into a smooth dome, but watching wasn't the same as knowing. What I'd missed was waiting. She'd let the dough sit far longer than I had, and the difference between her loaf and mine came down to time I hadn't given it.

<!-- annotation:
S1=opener-scene (first-person, concrete sensory detail; sets up the failure); opener-shape=narrative-anecdote
S2=expansion-context (recalls the watched ritual in a list; serial commas, no em-dashes)
S3=pivot-realization (short sentence names what the writer missed; sets up the reflection)
S4=closure-synthesis (returns to the difference and names time as the variable); closure-type=synthesis
paragraph-pattern: scene → context-recall → pivot → synthesis
handoff-to-next: the next paragraph picks up "time I hadn't given it" and generalizes
source: illustrative; voice-extractor replaces with corpus paragraph at extraction time
-->

### Exhibit 2 — commentary (illustrative)

TBD — voice-extractor populates from corpus when commentary samples are present. If the corpus is purely personal-essay or process-post, this exhibit stays TBD.

### Exhibit 3 — process-post (illustrative)

TBD — voice-extractor populates from corpus when process-post samples are present. If the corpus is purely personal-essay or commentary, this exhibit stays TBD.

Voice-extractor replaces these shipped exhibits with corpus-derived paragraphs when run against an author's samples. The shipped exhibits are illustrative of the shape, not defaults to retain; the extractor's output file carries the author's actual patterns.

## Tone

### Stance

**Rule.** State views like you're talking to one person. Contractions are fine. First-person is welcome. Acknowledge when you're not sure but don't hedge for its own sake.

**Exemplars `[personal-essay, commentary]`:**
- "I think this is worth doing, even if it's inconvenient."
- "Honestly, I'm not sure what the right move is here."

**Not:** "It is my considered opinion that this course of action merits pursuit." / "One might argue that..."

### Sentence Structure

**Rule.** Short sentences. Fragments are fine when they land. Contractions throughout. Casual prose's baseline is shorter than academic — but stacked one-clause declaratives with no hand-off still read as choppy. Vary the length; a short sentence earns its punch by sitting between longer ones.

**Exemplars:**
- "This works. Sort of."
- "You wouldn't believe how often this breaks."
- "It's not the most elegant fix, but it's a fix."

**Not:** "One might observe that the implementation, while functional, does not demonstrate optimal elegance."

### Exploratory vs Verdict Tone

**Rule.** Think out loud more than pronounce. Conversational writing earns its authority by showing the reasoning; verdict-stacking reads as lecturing. In `commentary`, the verdict is allowed at the end of the argument, not at the start.

**Exemplars:**
- Exploratory: "Which makes me wonder whether the whole framing is off."
- Verdict-stacked (avoid): "This is clearly the wrong approach. The right approach is obvious." — back-to-back verdicts kill the conversation.

### Thinking Out Loud

**Rule.** Questions and answers, asides, second thoughts. Let the reader follow the thinking; don't hand them conclusions.

**Exemplars:**
- "Wait, does this actually matter? I think it does, but only if you're optimizing for X."
- "So what does this tell us? Maybe nothing. Or maybe it's the whole point."

### Including the Reader

**Rule.** "You" and "we" both work. Pick based on feel. "You" is direct; "we" is collaborative. Don't lecture.

**Exemplars:**
- "You end up choosing between two bad options."
- "We've all been here before."

**Not:** "The reader must understand..."

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." "This is really quite important" becomes "This is important." Casual prose allows "kind of" / "sort of" as authentic hedges when they carry meaning ("I sort of agree" can be genuine ambivalence). Cut them when they stack or dilute. "This is sort of basically actually a problem" is not casual, it's bad.

### No Preamble

**Rule.** Never start a paragraph or turn with "Great question!" / "That's interesting." Open on substance.

## Structure

### The Core Rule

**Rule.** Casual prose doesn't mean sloppy. Every sentence earns its place; if it doesn't add something the reader couldn't guess, cut it.

**Concision is a means, not an end.** Casual prose has a lower length ceiling than academic, but chiseling below the conversational rhythm is a failure mode, not a success. If cutting a word makes the sentence read like a stub, put the word back. Stranded verbs ("none of the three resolves") read as AI even in casual register; see `## Cut patterns > compression-stranded-verb`.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list.)
- Does it earn its place?
- Does the piece flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. First drafts are raw material, not output.

### Sentence Connectedness

**Rule.** Sentences hand off, but the connectives are lighter than academic. "And," "but," "so," "then" carry more weight than full subordinators ("because," "whereas"). Casual prose can chain shorter sentences than academic prose, but full disconnection still reads as choppy.

**Exemplars:**
- Connected: "I tried the first approach and it broke immediately. So I backed off and tried something simpler."
- Disconnected (avoid): "I tried the first approach. It broke. I tried something simpler."

### Paragraph Flow

**Rule.** Paragraphs are conversational beats. They can be shorter than academic — a single idea, one or two sentences, then a paragraph break. But they still connect: end on a question, a setup, or a callback the next paragraph picks up.

**Exemplars:**
- Connected: A paragraph ends "I couldn't get it out of my head." The next opens "That nagging sense is usually worth listening to."
- Disconnected (avoid): Every paragraph ends on a full stop and opens cold.

### Information Pacing

**Rule.** Heavy points get their own paragraphs. Light points cluster. Don't load every sentence; let some just breathe.

**Exemplar:**
- Paced: "The demo crashed on stage. Everyone laughed politely. Then we spent three weeks rebuilding."

### Concept Setup

**Rule.** Define terms inline but lightly — a parenthetical or a "basically, it's X" aside. Don't formally introduce every specialized word; casual readers can handle inference better than textbook readers.

**Exemplars:**
- Set up: "Chicken sexing (telling male and female chicks apart, which expert sexers can do reliably but can't explain how) is the classic example."
- Dropped (avoid): "The phenomenon exhibits characteristics consistent with implicit learning."

### Building Arguments

**Rule.** Walk through reasoning but feel free to skip steps the reader will fill in. Counterpoints appear as "yeah, but" moments, not formal objections. In `commentary`, sharper objection-naming is allowed; in `personal-essay`, keep counterpoints conversational.

**Exemplar:**
- "I know, I know, you could just use X. But X has its own problems."

### Paragraph Length

**Rule.** 2 to 4 sentences per paragraph is the casual baseline. One-sentence paragraphs are allowed for emphasis. Avoid paragraphs longer than 5 sentences — the conversational energy dies.

### Reduced Structures and Parse Load

**Rule.** Drop "that" freely in casual prose ("the thing she said," not "the thing that she said") — but don't stack two or three reduced relatives in one sentence. The reader has to backtrack to identify the subject. See `## Cut patterns > reduced-relative-stacking`.

## Dimension

### Analogies and Anecdotes

**Rule.** Anecdotes from personal experience anchor casual writing. Specific, small-scale, concrete. The reader should be able to picture the scene. Cut any anchor that requires domain knowledge to land — casual register's reach is wider than academic's.

**Anchors:** TBD — derived from corpus. Casual-register anchors lean on everyday objects or situations (cooking, commuting, tools-at-hand) rather than technical or academic examples.

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*. Use this section only for author-specific punctuation habits the corpus shows beyond the §10-governed patterns.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns (casual-register baseline):**
- Ellipses for trailing thoughts and drift: "And if you just... change it slightly, the whole thing breaks." Use sparingly.
- Parentheticals (like this) are welcome but don't stack them.

### Formatting

**Rule.** Minimal. **Bold** for genuine emphasis (not caps). *Italics* for a word being used self-consciously. Bullet lists only when the content really is a list; flowing prose otherwise.

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 7 explicitly flag. Each pattern carries a canonical ID; `failures_dir` before/after pairs populate author-specific instances at extraction time. Shipped patterns are register-default.

### aphoristic-closure

**Pattern.** Paragraph ends on a crisp, rhetorically-balanced pronouncement that substitutes rhetoric for reasoning. Casual signatures: "And maybe that's the whole point." / "Sometimes that's all you can do." / "Some things really are that simple."

**Why it reads as AI.** Casual prose's strength is forward momentum and specific observation. A profundity-closure trades both for a vague gesture toward universality.

**Fix.** Restructure to a `transitional` or `synthesis` closure: end on what the next paragraph picks up, or end on a concrete observation. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision, producing a fragment-like sentence. "It just doesn't" (doesn't what?), "She got it" (got what?).

**Why it reads as AI.** Conversational prose tolerates fragments, but only when context makes the missing complement obvious. A stranded verb without context-recovery trips the reader on first read.

**Fix.** Restore the stranded complement, or restructure so the fragment IS the joke / IS the point.

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs ("the realization that," "the awareness of," "the experience of") stacked across clauses without a concrete agent. Casual prose drifts here when imitating thoughtful-essay register.

**Why it reads as AI.** Casual register's hallmark is concrete subjects + active verbs ("I noticed," "she said," "the room got quiet"). When the cut-bias stops firing, prose expands into abstract-noun cascades that read as performed-thoughtful rather than thinking.

**Fix.** Rewrite around a concrete agent and an active verb.

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in one sentence, often combined with a cataphoric pronoun.

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack. Casual prose drops "that" naturally — but stacking is a sentence-engineering tell.

**Fix.** Restore "that" and/or split the sentence.

### explainer-padding `[register: personal-essay, commentary]`

**Pattern.** Phrases that perform helpfulness or framing without adding information. Signatures: "As you might know," "It's worth pointing out," "What's interesting is," "One thing to note here is," "The thing is..."

**Why it reads as AI.** Casual prose's hallmark is forward momentum — a personal voice pulling the reader through. Performative-helpful framings stop the momentum to signal "now I will explain something" instead of just doing it. A reader who came for the writer's voice doesn't need the meta-narration.

**Fix.** Cut the framing entirely. The sentence underneath usually stands on its own; if it doesn't, the framing wasn't the problem.

### second-person-drift `[register: personal-essay]`

**Pattern.** Slip from first-person ("I noticed," "I tried") to generic second-person ("you notice," "you try") mid-paragraph, where the second-person is doing assertion-by-implication rather than direct address.

**Why it reads as AI.** The shift hides the writer's stance behind a generalized "you." First-person owns the claim ("I find this annoying"); second-person flattens it into received wisdom ("you'll find this annoying"). In a personal essay, the personal frame IS the voice — drifting to "you" surrenders it.

**Fix.** Pick one. If the claim is personal observation, keep "I." If the writer is genuinely addressing the reader directly (process-post advice, commentary call-to-action), keep "you" but make it explicit. Don't drift.

Additional canonical patterns apply in register-specific contexts: `first-person-commitment-in-academic-report` (academic registers only — N/A here), `citation-atomization` (citation-dense registers only — N/A here).

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

## §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
