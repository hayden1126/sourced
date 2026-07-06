# Voice rules

Voice calibration tuned to {{USER}}'s narrative writing — personal essays, reflection pieces, college application essays, memoir-adjacent work. Encodes narrative-register defaults under the phase-3 sub-register contract: tone (first-person, scene-aware, reflective), structure (chronological or thematic arcs, scene → reflection alternation), dimension (specific sensory detail, deliberate punctuation for rhythm, minimal formatting). Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 9 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Sub-register taxonomy

Narrative writing is not a single register. This voice covers three sub-registers; rules below are tagged with the sub-register where they apply strongly. Untagged rules apply across all three.

- **`scene-driven`** — present-tense or past-tense scene with sensory detail, dialogue, embodied action; reflection minimized or deferred. Examples: opening scenes of memoir chapters, vignettes, action-forward pieces.
- **`reflective`** — past-tense looking back; abstract movement; meaning-making in the foreground; scene used as illustration. Examples: meditation essays, retrospective reflections, mid-life reckonings.
- **`argumentative-personal`** — first-person essay with thesis; scene + reflection alternation in service of an argument; closer to academic personal-essay than memoir. Examples: New York Times Modern Love columns, polished college-application essays, thesis-driven personal essays.

When the corpus spans multiple sub-registers, `voice-extractor` produces one voice file per sub-register rather than unioning them; see `data/agents/voice-extractor.md § Multi-register routing`. Unioning is the documented failure mode (a `scene-driven` sensory-density rule imported into `argumentative-personal` produces over-described prose where every paragraph stops to describe a room before resuming the argument).

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field. The declaration filters which rules below apply. If the brief does not specify, assume `reflective` (the narrative middle-baseline) and flag the assumption in the prose-plan.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

### Exhibit 1 — reflective (illustrative)

> The afternoon I left, my grandmother was already in the garden. She didn't look up when the cab honked. I had said goodbye the night before, in the kitchen, and we both seemed to have agreed that the morning version would be smaller. Years later, I would wonder whether she was sparing me or sparing herself. By then there was no one to ask.

<!-- annotation:
S1=opener-scene-anchor (specific time, named figure, embodied action); opener-shape=scene-anchor-past-tense
S2=development-detail (concrete sensory detail; the cab honk, the not-looking-up)
S3=development-context (explanation of the prior night; introduces the agreement that frames the question)
S4=pivot-reflection (years-later move; introduces the unanswered question)
S5=closure-loss (short sentence; the loss is named without being explained); closure-type=synthesis
paragraph-pattern: scene-anchor → detail → context → reflection-pivot → loss
handoff-to-next: the next paragraph either steps further back into reflection or returns to a different scene from the same period
source: illustrative; voice-extractor replaces with corpus paragraph at extraction time
-->

### Exhibit 2 — scene-driven (illustrative)

TBD — voice-extractor populates from corpus when scene-driven samples are present. If the corpus is purely reflective or argumentative-personal, this exhibit stays TBD.

### Exhibit 3 — argumentative-personal (illustrative)

TBD — voice-extractor populates from corpus when argumentative-personal samples are present. If the corpus is purely scene-driven or reflective, this exhibit stays TBD.

Voice-extractor replaces these shipped exhibits with corpus-derived paragraphs when run against an author's samples. The shipped exhibits are illustrative of the shape, not defaults to retain; the extractor's output file carries the author's actual patterns.

## Tone

### Stance

**Rule.** Claims are often provisional, grounded in experience. "I thought" / "I realized" / "it turned out" rather than "research shows" or "I argue." First-person is the baseline, not a stylistic choice. In `argumentative-personal`, first-person commitment to a position is allowed and expected; in `scene-driven` and `reflective`, the stance accumulates from accumulated specifics rather than declarative claim.

**Exemplars:**
- "I didn't understand, at first, why it mattered."
- "Looking back, I was asking the wrong question."

**Not:** "It is evident that the experience was formative." / "One comes to recognize that..."

### Sentence Structure

**Rule.** Varies with scene vs. reflection. Scene sentences are tight, concrete, often sensory. Reflection sentences are longer, more abstract, often questioning. Uniform medium-length sentences across both modes flatten the rhythm.

**Exemplars:**
- Scene: "The room smelled like burnt coffee. She didn't look up when I walked in."
- Reflection: "Something about that afternoon stayed with me, not the conversation itself, but the way the light fell across the desk while she talked."

**Not:** uniform medium-length sentences across both modes — rhythm comes from the contrast.

### Exploratory vs Verdict Tone

**Rule.** Narrative prose lives in exploration. Verdicts are rare and reserved for rhetorical impact. Most of the writing earns its authority through specificity, not conclusion. In `argumentative-personal`, verdicts can land at section ends or in the closing paragraph; even there, the verdict should follow accumulated scene rather than open the section.

**Exemplars:**
- Exploratory: "I keep coming back to that afternoon, and I still don't know what to make of it."
- Verdict (earned, rare): "That was the moment I stopped believing him."

### Thinking Out Loud

**Rule.** This IS narrative writing — the thinking-out-loud quality is the form. Ask questions, answer them, reverse yourself, reconsider. The reader follows your mind in motion.

**Exemplars:**
- "At the time, I thought it was about control. Maybe it was. Or maybe, and this is harder to admit, it was about being afraid."
- "Why did I stay? I've told myself a dozen reasons. None of them are true, exactly."

### Including the Reader

**Rule.** Second-person ("you") appears but is usually the universal-you, not direct address. First-person dominates. "We" appears rarely, usually as a moment of solidarity.

**Exemplars:**
- Universal-you: "You know the feeling when someone says your name and you can tell they've been practicing it."
- First-person baseline: "I had never seen her cry before."

**Not:** "The reader will recognize..." / "One might imagine..." (lectures and breaks the intimacy narrative depends on)

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." In narrative, concrete sensory detail replaces hedged qualification. "I was very scared" becomes "My hands wouldn't stop shaking." Ground claims with specific memory, not vague intensifiers.

### No Preamble

**Rule.** Start in scene or with a question. Skip "I want to tell you about..." or "Recently I've been thinking about..."

**Exemplars:**
- "I was seventeen the first time I understood that grown-ups lie."
- "There's a particular kind of silence in a parked car."

## Structure

### The Core Rule

**Rule.** Every paragraph either advances the story or earns the reflection. Scene without reflection is a transcript; reflection without scene is an essay. Both feel untethered. Alternate.

**Concision is a means, not an end.** Narrative prose tolerates more sensory detail than other registers, but stranded verbs and aphoristic closures still trip the reader. See `## Cut patterns > compression-stranded-verb` and `## Cut patterns > aphoristic-closure`.

**The iteration loop.** After writing a draft, reread every paragraph and ask:
- Does this paragraph advance the story or earn the reflection?
- Does it repeat a scene or an insight already delivered?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list.)
- Is the sensory detail specific, or is it a generic placeholder?
- Does the piece hold when read start to finish?

If any answer is no, rewrite or cut. Then reread again. First drafts are raw material, not output.

### Sentence Connectedness

**Rule.** Sentences connect through time ("then," "later," "that afternoon"), through parallel sensory detail ("I heard... I saw... I remember..."), or through reflective pivots ("but what I didn't know was..."). Avoid chains of declaratives that read as enumeration.

**Exemplars:**
- Connected (time): "We left the house a little after seven. The streetlights were already on. By the time we reached the bridge, I had stopped talking."
- Connected (sensory parallel): "I remember the cold of the doorknob. I remember my breath fogging the glass. I remember not wanting to turn around."

**Not:** "The house was quiet. The door was locked. The car was in the driveway." (reader gets facts, not a scene)

### Paragraph Flow

**Rule.** Paragraphs move between scene and reflection. A scene paragraph may end on a sensory detail or a line of dialogue; the next paragraph steps back to interpret, then returns to scene.

**Exemplar:**
- Connected: a scene paragraph ends "She closed the door without answering." The next opens: "For years afterward, I tried to figure out what that silence meant."

**Not:** a scene paragraph ending on a verdict ("It was the worst day of my life"), which leaves nothing for the reflection paragraph to do.

### Information Pacing

**Rule.** Scene is dense with detail; reflection is sparse. The rhythm alternates: pack the scene, breathe in the reflection, return to scene. Avoid stacking reflection paragraphs or stacking scene paragraphs; the form depends on the alternation.

### Concept Setup

**Rule.** Narrative concepts set up through scene, not definition. Instead of defining a term, show it happening. A reader meets a word for a family ritual by watching the ritual once; an abstract noun earns its place by being embodied first.

**Exemplars:**
- Set up in scene: "Every Sunday, my grandmother served a soup she called *chorba*. I didn't ask what was in it until I was nine." (the term enters through practice)
- Dropped (avoid): "*Chorba* is a North African soup often served on Sundays" (the sentence is a gloss, not a scene, and reads as exposition)

### Building Arguments `[register: argumentative-personal]`

**Rule.** Narrative writing builds arguments indirectly. Specific scenes accumulate into an argument the reader constructs themselves. Direct assertion is rare and weighty when it appears. In `argumentative-personal`, named thesis is allowed, but it should land after the scene work has earned it.

**Exemplar:**
- "I'm not going to tell you he was cruel. I'm going to tell you what he said at the dinner table when I was twelve, and you can decide."

### Paragraph Length

**Rule.** Varies widely. Scene paragraphs can be long (6–8 sentences of cumulative detail) or short (single-sentence impact). Reflection paragraphs 3–5 sentences. Avoid uniformity — variation IS the rhythm.

### Reduced Structures and Parse Load

**Rule.** Drop "that" freely in narrative prose ("the thing she said," not "the thing that she said") — but don't stack two or three reduced relatives in one sentence. The reader has to backtrack to identify the subject. See `## Cut patterns > reduced-relative-stacking`.

## Dimension

### Analogies and Anecdotes

**Rule.** The whole piece IS anecdote, essentially. Within the larger narrative, smaller anecdotes can nest (a remembered moment, a friend's story) to illuminate the main arc. Cut a nested anecdote you find yourself extending across multiple paragraphs — a vignette is a moment, not another scene.

**Anchors:** TBD — derived from corpus. Narrative-register anchors often include recurring images, named people, specific settings that surface across multiple samples — a returned-to setting (the grandmother's kitchen, the back road home), a named recurring figure (the teacher who said X, a sibling at a specific age), or a sensory image the writer returns to as shorthand (the smell of wet asphalt, a specific light at dusk).

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*: the gloss becomes a standalone sentence, is relocated to a natural position, or is cut. A comma, colon, or period-fragment swap that keeps the mid-clause-interruption rhythm intact fails the audit.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns (narrative-register baseline):**
- Ellipses for trailing thoughts and drift: "And I knew, even then... I just didn't want to say it."
- Semicolons to link reflection-clauses: "I wanted to leave; I didn't move."
- Direct speech with quotation marks, attributed minimally ("she said," "I replied"). Attributed dialogue with sensory action beat is preferred over "she said" alone.

### Formatting

**Rule.** Minimal. *Italics* for emphasis of a single word (often a remembered phrase). **Bold** rare. Bullet points usually break the mood; avoid unless the list is a genuine list (ingredients, steps, etc.).

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 7 explicitly flag. Each pattern carries a canonical ID; `failures_dir` before/after pairs populate author-specific instances at extraction time. Shipped patterns are register-default.

### aphoristic-closure

**Pattern.** Paragraph ends on a crisp, rhetorically-balanced pronouncement that substitutes rhetoric for reasoning. Narrative signatures: "And maybe that was enough." / "The silence said everything." / "Some doors stay closed for a reason."

**Why it reads as AI.** Narrative prose's strength is specificity earning its meaning. A profundity-closure trades the specific scene the paragraph just delivered for a vague universal — undoing the work the scene did.

**Fix.** Restructure to a `transitional` or `synthesis` closure. End on a remembered sensory detail, a line of dialogue, or a question that the next paragraph picks up. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision, producing a fragment-like sentence. Narrative signatures: "I knew" (knew what?), "She had stopped" (stopped doing what?), "It was over" (over how?).

**Why it reads as AI.** Narrative prose tolerates fragments when context anchors them, but a stranded verb without scene-anchor reads as performed-significance rather than earned-significance.

**Fix.** Restore the stranded complement, OR restructure so the fragment IS the scene's beat (e.g., "I knew what she meant. I knew what she meant before she finished the sentence.").

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs ("the realization," "the recognition," "the awareness") stacked across clauses without a concrete agent or scene-anchor.

**Why it reads as AI.** Narrative register's hallmark is concrete subjects + specific scene ("I noticed," "she said," "the room got quiet"). When the cut-bias stops firing, prose expands into abstract-noun cascades that read as performed-thoughtful rather than thinking.

**Fix.** Rewrite around a concrete agent and an active verb. "The realization that she had been right came slowly" → "It took me weeks to see she'd been right."

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in one sentence, often combined with a cataphoric pronoun.

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack — fatal in narrative prose where the reader needs to stay anchored in scene.

**Fix.** Restore "that" and/or split the sentence. Narrative drops "that" naturally in close-third or dialogue voicing; stacking is sentence-engineering, not voice.

### telling-not-showing `[register: scene-driven, reflective]`

**Pattern.** Summary-statement of an emotional or experiential claim where a scene would do the work. Signatures: "The argument was painful." / "I felt very alone that year." / "Their relationship was complicated."

**Why it reads as AI.** AI-drafted narrative prose tends to summarize emotional content in abstract terms, because describing the specific scene that conveys the feeling requires sensory commitment the model defers. The reader gets a label instead of an experience.

**Fix.** Replace the summary with a scene that delivers the feeling. "The argument was painful" → "She put her cup down without drinking from it. She said my name twice before I looked up." The reader infers the feeling from the embodied detail.

### generic-sensory-placeholder `[register: scene-driven]`

**Pattern.** Sensory detail stated in generic terms that could describe many scenes. Signatures: "the cool morning air," "the warm afternoon sun," "the smell of fresh coffee," "the sound of laughter."

**Why it reads as AI.** AI-drafted scene prose tends to reach for the most-likely sensory cliché when the model lacks the specific scene-detail. The result reads as scene-shaped but doesn't anchor anywhere — the reader can't picture which morning, which kitchen, which laugh.

**Fix.** Replace the generic with the specific. "The cool morning air" → "the first cold morning that fall, when my breath caught at the door." If you can't recall the specific, the scene may not be earning its place — consider whether reflection or summary handles the moment better.

Additional canonical patterns apply in register-specific contexts: `first-person-commitment-in-academic-report` (academic registers only — N/A here), `citation-atomization` (citation-dense registers only — N/A here).

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

## §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
