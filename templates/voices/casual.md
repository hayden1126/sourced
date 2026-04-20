# Voice rules

Voice calibration tuned to {{USER}}'s casual writing — blog posts, personal essays, conversational pieces. The shipped `casual` voice is a register-specific skeleton: it encodes conversational-register defaults for tone (first-person ease, contractions, short sentences), structure (explicit connectives, short argument arcs), and dimension (analogies close to experience, inline punctuation, light formatting). Copy to a new name and edit for a different author within the casual register; for a different register (academic, technical, journalistic, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

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

State views like you're talking to one person. Contractions are fine. First-person is welcome. Acknowledge when you're not sure — but don't hedge for its own sake.

- "I think this is worth doing, even if it's inconvenient."
- "Honestly, I'm not sure what the right move is here."

Not: "It is my considered opinion that this course of action merits pursuit."
Not: "One might argue that..."

### Sentence Structure

Short sentences. Fragments are fine when they land. Contractions throughout.

- "This works. Sort of."
- "You wouldn't believe how often this breaks."
- "It's not the most elegant fix, but it's a fix."

Not: "One might observe that the implementation, while functional, does not demonstrate optimal elegance."

### Exploratory vs Verdict Tone

Think out loud more than pronounce. Conversational writing earns its authority by showing the reasoning; verdict-stacking reads as lecturing.

- Exploratory: "Which makes me wonder whether the whole framing is off."
- Verdict-stacked: "This is clearly the wrong approach. The right approach is obvious." — back-to-back verdicts kill the conversation.

### Thinking Out Loud

Questions and answers, asides, second thoughts. Let the reader follow the thinking, don't hand them conclusions.

- "Wait, does this actually matter? I think it does, but only if you're optimizing for X."
- "So what does this tell us? Maybe nothing. Or maybe it's the whole point."

### Including the Reader

"You" and "we" both work. Pick based on feel. "You" is direct; "we" is collaborative. Don't lecture.

- "You end up choosing between two bad options."
- "We've all been here before."

Not: "The reader must understand..."

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite important" becomes "This is important." Casual prose allows "kind of" / "sort of" as authentic hedges when they carry actual meaning — "I sort of agree" can be genuine ambivalence. Cut them when they stack or dilute. "This is sort of basically actually a problem" is not casual, it's bad.

### No Preamble

Never start with "Great question!" or "That's interesting." Just start with substance.

## Structure

### The Core Rule

Casual prose doesn't mean sloppy. Every sentence earns its place; if it doesn't add something the reader couldn't guess, cut it. The iteration loop applies here too: draft, reread, cut, rewrite.

Casual writing usually has a lower ceiling for length than academic — aim to be shorter than you think. Blog posts and personal essays that run long lose their conversational energy.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Does it earn its place?
- Does the piece flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. First drafts are raw material, not output.

### Sentence Connectedness

Sentences hand off, but the connectives are lighter. "And," "but," "so," "then" carry more weight than in academic prose; full subordinators ("because," "whereas") appear but not every sentence.

- Connected: "I tried the first approach and it broke immediately. So I backed off and tried something simpler."
- Disconnected: "I tried the first approach. It broke. I tried something simpler."

Casual prose can chain shorter sentences more than academic prose, but full disconnection still reads as choppy.

### Paragraph Flow

Paragraphs are conversational beats. They can be shorter than academic paragraphs — a single idea, one or two sentences, then a paragraph break. But they still connect: end on a question, a setup, or a callback the next paragraph picks up.

- Connected: A paragraph ends "I couldn't get it out of my head." The next opens "That nagging sense is usually worth listening to."
- Disconnected: Every paragraph ends on a full stop and opens cold.

### Information Pacing

Heavy points get their own paragraphs. Light points cluster. Don't load every sentence, let some just breathe.

- Paced: "The demo crashed on stage. Everyone laughed politely. Then we spent three weeks rebuilding."
- Packed: claim + evidence + caveat + pivot all in one sentence, every sentence.

### Concept Setup

Define terms inline but lightly — a parenthetical or a "basically, it's X" aside. Don't formally introduce every specialized word; casual readers can handle inference better than textbook readers.

- Set up: "Chicken sexing (telling male and female chicks apart, which expert sexers can do reliably but can't explain how) is the classic example."
- Dropped: "The phenomenon exhibits characteristics consistent with implicit learning." (no setup; assumes the reader already knows the term)

### Building Arguments

Walk through the reasoning but feel free to skip steps the reader will fill in. Counterpoints appear as "yeah, but" moments, not formal objections.

- "I know, I know, you could just use X. But X has its own problems."

### Paragraph Length

2 to 4 sentences per paragraph is the casual baseline. One-sentence paragraphs are allowed for emphasis. Avoid paragraphs longer than 5 sentences — the conversational energy dies.

## Dimension

### Analogies and Anecdotes

Anecdotes from personal experience anchor casual writing. Specific, small-scale, concrete. The reader should be able to picture the scene.

**Anchors:** TBD — derived from corpus. Casual-register anchors lean on everyday objects or situations — cooking, commuting, tools-at-hand — rather than technical or academic examples. Cut any anchor that requires domain knowledge to land.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. Use this section only for author-specific punctuation habits the corpus clearly shows (semicolon style, ellipsis use, parenthetical style, etc.). Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly; silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Ellipses** for trailing thoughts and drift: "And if you just... change it slightly, the whole thing breaks." Parentheticals (like this) are welcome but don't stack them.

### Formatting

Minimal. **Bold** for genuine emphasis, not caps. *Italics* for a word you're using self-consciously. Bullet lists only when the content really is a list; flowing prose otherwise.
