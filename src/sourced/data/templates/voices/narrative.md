# Voice rules

Voice calibration tuned to {{USER}}'s narrative writing — personal essays, reflection pieces, college application essays, memoir-adjacent work. The shipped `narrative` voice is a register-specific skeleton: it encodes narrative-register defaults for tone (first-person, scene-aware, reflective), structure (chronological or thematic arcs, scene → reflection alternation), and dimension (specific sensory detail, deliberate punctuation for rhythm, minimal formatting). Copy to a new name and edit for a different author within the narrative register; for a different register (academic, casual, technical, journalistic) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `install.sh` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

### §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.

## Tone

### Stance

Claims are often provisional, grounded in experience. "I thought" / "I realized" / "it turned out" rather than "research shows" or "I argue." First-person is the baseline, not a stylistic choice.

- "I didn't understand, at first, why it mattered."
- "Looking back, I was asking the wrong question."

Not: "It is evident that the experience was formative."
Not: "One comes to recognize that..."

### Sentence Structure

Varies with scene vs. reflection. Scene sentences are tight, concrete, often sensory. Reflection sentences are longer, more abstract, often questioning.

- Scene: "The room smelled like burnt coffee. She didn't look up when I walked in."
- Reflection: "Something about that afternoon stayed with me, not the conversation itself, but the way the light fell across the desk while she talked."

Not: uniform medium-length sentences across both modes. Rhythm comes from the contrast.

### Exploratory vs Verdict Tone

Narrative prose lives in exploration. Verdicts are rare and reserved for rhetorical impact. Most of the writing earns its authority through specificity, not conclusion.

- Exploratory: "I keep coming back to that afternoon, and I still don't know what to make of it."
- Verdict (earned, rare): "That was the moment I stopped believing him."

### Thinking Out Loud

This IS narrative writing — the thinking-out-loud quality is the form. Ask questions, answer them, reverse yourself, reconsider. The reader follows your mind in motion.

- "At the time, I thought it was about control. Maybe it was. Or maybe, and this is harder to admit, it was about being afraid."
- "Why did I stay? I've told myself a dozen reasons. None of them are true, exactly."

### Including the Reader

Second-person ("you") appears but is usually the universal-you, not direct address. First-person dominates. "We" appears rarely, usually as a moment of solidarity.

- Universal-you: "You know the feeling when someone says your name and you can tell they've been practicing it."
- First-person baseline: "I had never seen her cry before."

Not: "The reader will recognize..." "One might imagine..." These lecture and break the intimacy narrative depends on.

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite important" becomes "This is important." In narrative, concrete sensory detail replaces hedged qualification. "I was very scared" becomes "My hands wouldn't stop shaking." Ground claims with specific memory, not vague intensifiers.

### No Preamble

Start in scene or with a question. Skip "I want to tell you about..." or "Recently I've been thinking about..."

- "I was seventeen the first time I understood that grown-ups lie."
- "There's a particular kind of silence in a parked car."

## Structure

### The Core Rule

Every paragraph either advances the story or earns the reflection. Scene without reflection is a transcript; reflection without scene is an essay. Both feel untethered. Alternate.

Writing is sculpting: start with raw material, then chisel. Write a draft, step back, cut, rewrite. Repeat. The first version is never the final version.

**The iteration loop.** After writing a draft, reread every paragraph and ask:
- Does this paragraph advance the story or earn the reflection?
- Does it repeat a scene or an insight already delivered?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Is the sensory detail specific, or is it a generic placeholder?
- Does the piece hold when read start to finish?

If any answer is no, rewrite or cut. Then reread again. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then present the draft for feedback.

This is not optional polish. This is the process. First drafts are raw material, not output.

### Sentence Connectedness

Sentences connect through time ("then," "later," "that afternoon"), through parallel sensory detail ("I heard... I saw... I remember..."), or through reflective pivots ("but what I didn't know was..."). Avoid chains of declaratives that read as enumeration.

- Connected (time): "We left the house a little after seven. The streetlights were already on. By the time we reached the bridge, I had stopped talking."
- Connected (sensory parallel): "I remember the cold of the doorknob. I remember my breath fogging the glass. I remember not wanting to turn around."
- Disconnected: "The house was quiet. The door was locked. The car was in the driveway." The reader gets facts, not a scene.

### Paragraph Flow

Paragraphs move between scene and reflection. A scene paragraph may end on a sensory detail or a line of dialogue; the next paragraph steps back to interpret, then returns to scene.

- Connected: a scene paragraph ends "She closed the door without answering." The next opens: "For years afterward, I tried to figure out what that silence meant."
- Disconnected: a scene paragraph ends on a verdict ("It was the worst day of my life"), which leaves nothing for the reflection paragraph to do.

### Information Pacing

Scene is dense with detail; reflection is sparse. The rhythm alternates: pack the scene, breathe in the reflection, return to scene. Avoid stacking reflection paragraphs or stacking scene paragraphs; the form depends on the alternation.

### Concept Setup

Narrative concepts set up through scene, not definition. Instead of defining a term, show it happening. A reader meets a word for a family ritual by watching the ritual once; an abstract noun earns its place by being embodied first.

- Set up in scene: "Every Sunday, my grandmother served a soup she called *chorba*. I didn't ask what was in it until I was nine." The term enters through practice.
- Dropped: "*Chorba* is a North African soup often served on Sundays" — the sentence is a gloss, not a scene, and reads as exposition.

### Building Arguments

Narrative writing builds arguments indirectly. Specific scenes accumulate into an argument the reader constructs themselves. Direct assertion is rare and weighty when it appears.

- "I'm not going to tell you he was cruel. I'm going to tell you what he said at the dinner table when I was twelve, and you can decide."

### Paragraph Length

Varies widely. Scene paragraphs can be long (6-8 sentences of cumulative detail) or short (single-sentence impact). Reflection paragraphs 3-5 sentences. Avoid uniformity, variation IS the rhythm.

## Dimension

### Analogies and Anecdotes

The whole piece IS anecdote, essentially. Within the larger narrative, smaller anecdotes can nest (a remembered moment, a friend's story) to illuminate the main arc.

**Anchors:** TBD — derived from corpus. Narrative-register anchors often include recurring images, named people, specific settings that surface across multiple samples — concrete pattern-kinds are things like a returned-to setting (the grandmother's kitchen, the back road home), a named recurring figure (the teacher who said X, a sibling at a specific age), or a sensory image the writer returns to as shorthand (the smell of wet asphalt, a specific light at dusk). voice-extractor replaces this placeholder with the author's actual anchors from the corpus; the patterns above are illustrative of the kind, not defaults to keep.

Not every nested anecdote earns its place. Drop it if it doesn't connect back to the main arc; a detour that goes nowhere is a detour. Cut back a nested anecdote you find yourself extending: it should illuminate a moment, not run the piece.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*: the gloss becomes a standalone sentence, is relocated to a natural position, or is cut. A comma, colon, or period-fragment swap that keeps the mid-clause-interruption rhythm intact fails the audit. Use this section only for author-specific punctuation habits the corpus clearly shows. Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly; silence defers to §10.

Ellipses for trailing thoughts and drift: "And I knew, even then... I just didn't want to say it." Semicolons to link reflection-clauses ("I wanted to leave; I didn't move"). Direct speech with quotation marks, attributed minimally ("she said," "I replied").

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

### Formatting

Minimal. *Italics* for emphasis of a single word (often a remembered phrase). **Bold** rare. Bullet points usually break the mood; avoid unless the list is a genuine list (ingredients, steps, etc.).
