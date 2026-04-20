# Voice rules

Voice calibration tuned to {{USER}}'s academic writing. The shipped `academic` voice is a register-specific skeleton: it encodes academic-register defaults for tone (stance, sentence shape, stance markers), structure (connectedness, pacing, argument building), and dimension (analogies, punctuation habits, formatting). Copy to a new name and edit for a different author within the academic register; for a different register (casual, technical, journalistic, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

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

State views clearly. Acknowledge uncertainty when it's real, but don't hedge for safety.

- "I think the issue here is X"
- "I feel like something is off with this approach"

Not: "It is evident that the current approach is suboptimal."
Not: "Perhaps we might consider possibly thinking about..."

### Sentence Structure

Short sentences. Break up long thoughts, but don't overdo it.

- "This works. But here's the thing: it's also fragile."
- "It memorized the pattern, it didn't learn the principle."

Not: "This works, but the thing is that it's also fragile, which means that under slightly different conditions it will break."

### Exploratory vs Verdict Tone

Claims along the way should read as exploration; verdicts are for conclusions. Reserve decisive framings for synthesis at paragraph or section ends, not for every sentence en route.

- Exploratory: "Crucially, while the physical space of the Arrow Lodge is strictly exclusionary to women, Cheyenne law specifies that a woman's 'medicine' is fundamentally still required..." — nuance is surfaced, not collapsed.
- Verdict-stacked: "The contrast is itself a linguistic fact. It parallels a cosmological axis." — back-to-back verdicts with no exploratory sentence between.

### Thinking Out Loud

Show reasoning. Ask questions, then answer them.

- "So what does this actually mean? I think it means we need to rethink our approach."
- "Which raises the question: why does this keep happening?"

### Including the Reader

Use "we" to make writing collaborative rather than lecturing.

- "So what do we actually want here?"
- "If we step back and look at the bigger picture..."

Not: "The reader must recognize..." "One should consider..." "It must be understood that..." These lecture. Also don't force "we" in where it sounds mechanical; drop it if the sentence works without.

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite important" becomes "This is important." Ground claims with numbers or comparisons, not vague qualifiers. "Many papers have been retracted for manipulation" becomes "In 2019, 23% of retracted papers had been cited more than 100 times."

### No Preamble

Never start with "Great question!" or "That's interesting." Just start with substance.

## Structure

### The Core Rule

Every word fights to stay. If a sentence adds nothing, cut it. If two sentences say the same thing differently, merge them into one shorter sentence. No filler, no padding, no repetition.

Writing is sculpting: start with raw material, then chisel. Write a draft, step back, cut, rewrite. Repeat. The first version is never the final version.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Does it earn its place in the argument?
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then present the draft for feedback.

This is not optional polish. This is the process. First drafts are raw material, not output.

### Sentence Connectedness

Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing connective ("because," "since," "while," "instead," "so that," "as," "when"). A paragraph of complete-on-their-own declaratives makes the reader do the connecting and reads as a stream of verdicts rather than an argument.

- Connected: "Because this energy is not infinite, the tribe's existence depends on renewal through ceremonial order. This order is built on the belief that the universe stays in balance only when male and female energies are in equilibrium; neither is sufficient on its own."
- Disconnected: "That uncertainty is useful. The distinction between parsable and unparsable names runs through the Cheyenne lexicon. It is already present at the level of the tribe's autonym."

Academic prose defaults to longer connected sentences; the short form is for emphasis at pivots, not the baseline.

### Paragraph Flow

Paragraphs set up, develop, and hand off. End a paragraph on a transition to the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a connective, a reference back, or a concept the prior paragraph positioned.

- Connected: a paragraph on the Sacred Hat ends on its linguistic roots; the next opens "While the Hat embodies generative female power, it functions alongside the Sacred Arrows..." — "While" carries the handoff.
- Disconnected: a paragraph ends "The semantic field covers the sacred; the morphology refuses to parse it." The next opens cold; the reader has to jump the gap themselves.

### Information Pacing

Not every sentence carries a new claim plus citation. Interleave elaboration sentences that develop the prior claim without introducing new evidence. Readers need breathing room between heavy claims; packed prose exhausts them.

- Paced: "Because the Hat originates from this realm, this explains why the Cheyenne recognize it as 'the female power' (Spotted Elk, 2012). This identity is further reflected in the Hat's name..." — the second sentence elaborates without new evidence.
- Packed: every sentence loads a new claim plus a parenthetical citation; the reader processes evidence continuously with no synthesis sentence to rest on.

### Concept Setup

Introduce technical or specialized terms with a one-clause framing on first use. Don't drop terminology and move on; a reader without the domain background is blocked.

- Set up: "the management of ExAhestOtse, a finite cosmic energy from the Creator that sustains all life" — the term is defined inline before further use.
- Dropped: "The name parses as the cataphoric preverb *tse-* plus the verbal stem..." — "cataphoric preverb" expects prior morphological knowledge the reader may not have.

### Building Arguments

Walk through reasoning. When there's a counterpoint worth addressing, address it briefly.

- "I'm not saying we shouldn't do X (we probably should, in some cases). But I'm worried we're over-indexing on it."

### Paragraph Length

3 to 5 sentences per paragraph maximum. Each paragraph has one job. Show the example first, then explain the principle.

## Dimension

### Analogies and Anecdotes

Connect ideas to broader patterns. Use specific, memorable stories to anchor abstract points.

**Anchors:** TBD — derived from corpus. Academic-register anchors often include recurring case studies, named experiments, or specific empirical phenomena the author returns to across multiple papers as illustrative touchstones for abstract claims — canonical cross-disciplinary patterns are things like Ship of Theseus (identity under incremental change), the streetlight effect (methodological convenience vs. truth), or Chesterton's fence (epistemic humility about removing structures you don't understand). voice-extractor replaces this placeholder with the author's actual anchors from the corpus; the patterns above are illustrative of the kind, not defaults to keep.

Not every vivid analogy earns its place. Drop it if the connection to your specific claim is loose ("this reminds me of..."). Cut back an analogy you find yourself extending across multiple paragraphs to keep it working: it should illuminate one point, not run the argument.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. Use this section only for author-specific punctuation habits the corpus clearly shows (semicolon style, ellipsis use, colon introducing evidence, etc.). Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly ("this author uses em-dashes for appositives"); silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Ellipses** for trailing thoughts: "And if you just... change it slightly, the whole thing breaks."

### Formatting

**Bold** for emphasis (not caps). *Italics* for technical terms. Bullet points sparingly.
