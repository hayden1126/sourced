# Voice rules

Voice calibration for blended-register corpora. The shipped `hybrid` voice is a register-neutral skeleton: it encodes the UNDERLYING rules (connectedness, pacing, concept setup, iron prohibitions) without committing to a register's specific framing. Use as the base skeleton when the writing-samples corpus spans registers (e.g., school essays that are structurally academic but tonally casual; blog posts that mix reflective and journalistic patterns). voice-extractor selects hybrid.md automatically when the classifier finds no single register above 85% of the corpus.

For a register-specific calibration (academic papers, casual blog posts, technical documentation, journalistic pieces, narrative reflection), start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

**Note for downstream readers.** This skeleton is filled in by `voice-extractor` from a blended-register corpus. Any `TBD — derived from corpus` marker that remains in the rendered file signals the corpus did not settle that rule; treat such markers as "fall back to general register judgment" rather than a hard rule, and apply the surrounding prose guidance as context.

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `install.sh` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

### §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.

## Tone

### Stance

State views clearly. How hedged vs. how direct varies by register — academic prose hedges more, technical prose is direct, narrative prose reflective. voice-extractor: set the stance calibration from corpus evidence. Do NOT default to a specific register's hedging level.

TBD — derived from corpus.

### Sentence Structure

Sentences vary in length and shape across registers. Academic prose defaults long; casual short; technical imperative; narrative scene-aware; journalistic inverted. voice-extractor: set the baseline sentence-length rhythm from corpus evidence. Reserve short/punchy forms for emphasis at pivots regardless of baseline.

TBD — derived from corpus.

### Exploratory vs Verdict Tone

Exploration dominates in narrative and academic reflection; verdict dominates in reporting and technical reference. voice-extractor: identify where the corpus falls on this axis and calibrate. Do not default to any register's balance.

TBD — derived from corpus.

### Thinking Out Loud

Present in narrative and casual prose; rare in reporting and reference documentation. voice-extractor: if the corpus shows this pattern, calibrate exemplars; if absent, emit TBD rather than adding it.

TBD — derived from corpus.

### Including the Reader

First-person, second-person, third-person each dominate in different registers. voice-extractor: identify which pronoun-perspective the corpus uses and set as the baseline.

TBD — derived from corpus.

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

Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing relationship (explicit connectives, parallel structure, or implicit logical flow). How the connection is MARKED varies — explicit connectives, semicolons, short-sentence juxtaposition, restatement. The baseline rhythm varies too — some writers chain short, some build long.

voice-extractor: set the marker style AND baseline rhythm from corpus evidence. Do NOT default to "longer connected sentences" or any register-specific shape; extract what the corpus shows. If the corpus is thin on this section, TBD rather than impose a register-specific pattern.

### Paragraph Flow

Paragraphs set up, develop, and hand off. End a paragraph on a transition to the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a connective, a reference back, or a concept the prior paragraph positioned.

How the handoff is MARKED varies by register: academic uses explicit connectives ('While,' 'Moreover'); casual uses shorter bridges; narrative uses sensory callbacks; journalistic uses inverted-pyramid ordering.

voice-extractor: set the handoff style from corpus evidence. TBD if unclear.

### Information Pacing

Claim density varies by register. Academic prose can pack multiple claims per paragraph; technical prose emits one claim per sentence; narrative prose alternates heavy and light. voice-extractor: identify the pacing pattern the corpus shows and calibrate. Interleave elaboration sentences appropriately for the identified register.

### Concept Setup

Introduce specialized terms or domain references with appropriate framing on first use. The DEGREE of setup varies — academic prose can run longer definitions; casual prose uses parentheticals; technical prose uses formal definition blocks; narrative prose uses scene. voice-extractor: set the setup convention from corpus evidence.

### Building Arguments

Develop reasoning. Address counterpoints. How formally — full objection-response vs. casual "yeah, but" — varies by register. voice-extractor: set the argumentation style from corpus evidence.

### Paragraph Length

Paragraph length varies dramatically by register. Journalistic: 1-3 sentences. Casual: 2-4. Academic: 3-5. Narrative: highly variable. voice-extractor: measure the corpus's paragraph-length distribution and set the baseline accordingly.

## Dimension

### Analogies and Anecdotes

Connect abstract points to specific patterns. The TYPE of analogy varies — academic uses technical illustrations; casual uses everyday objects; technical uses system analogies; journalistic uses anecdotes about named people; narrative is itself anecdote. voice-extractor: identify the analogy type the corpus uses and calibrate.

**Anchors:** TBD — derived from corpus.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*, not a comma, colon, or period-fragment swap that preserves the mid-clause-interruption rhythm. Use this section only for author-specific punctuation habits the corpus clearly shows (ellipses, semicolons, colons, and so on). voice-extractor: identify what the corpus uses characteristically and describe the pattern. An author-specific rule that contradicts §10 must be stated explicitly; silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

TBD — derived from corpus.

### Formatting

Markdown formatting density varies by destination. voice-extractor: identify the corpus's formatting conventions (bold frequency, italics use, bullet-point density, code-block presence) and set the baseline.

TBD — derived from corpus.
