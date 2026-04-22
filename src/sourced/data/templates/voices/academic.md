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

- Exploratory: "Crucially, while the replication produced results consistent with the original finding, the experimenters noted that the apparatus differed in ways the published protocol had not disclosed..." — nuance is surfaced, not collapsed.
- Verdict-stacked: "The distinction is structural. It tracks the disciplinary boundary." — back-to-back verdicts with no exploratory sentence between.

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

**Concision is a means, not an end.** The baseline register for this voice is medium-to-long connected prose (see §Sentence Connectedness); chiseling below that baseline is a failure mode, not a success. If cutting a word makes the sentence awkward to read aloud, put the word back. If compressing two sentences into one merges two different thoughts, do not merge them. "Every word fights to stay" means filler doesn't survive; it does not mean every removal is a win. A grammatically tight sentence that trips the reader on first read has been over-chiseled. The fix is to restore connective tissue, not to defend the compression.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Does it earn its place in the argument?
- **Does it read fluidly aloud, or does the reader trip on it?** A clipped fragment ("none of the three resolves"), a stranded preposition that lands awkwardly ("where is the 'there' the stem points at?"), or a register-high verb where a plain one would carry the meaning ("legible" where "visible" works) all signal over-compression. Restore the word or restructure around a different shape.
- **Does a negation sentence sit immediately before an affirmation that asserts the alternative?** That is §10's "not X but Y" pattern retokenized with a period; break the adjacency or drop the negation.
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then present the draft for feedback.

This is not optional polish. This is the process. First drafts are raw material, not output.

### Sentence Connectedness

Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing connective ("because," "since," "while," "instead," "so that," "as," "when"). A paragraph of complete-on-their-own declaratives makes the reader do the connecting and reads as a stream of verdicts rather than an argument.

- Connected: "Because the archive was destroyed during the 1944 bombing, later historians worked from secondary summaries rather than primary documents. Those summaries compressed what the originals made explicit; each subsequent citation loses a layer of specificity."
- Disconnected: "The tension is productive. The gap between theory and practice appears throughout the economics literature. It recurs at the level of individual policy debates."

Academic prose defaults to longer connected sentences; the short form is for emphasis at pivots, not the baseline.

### Paragraph Flow

Paragraphs set up, develop, and hand off. End a paragraph on a transition to the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a connective, a reference back, or a concept the prior paragraph positioned.

- Connected: a paragraph on Brown's 1954 cross-sectional data ends on the methodological gap it exposed; the next opens "While Brown worked with cross-sectional samples, the longitudinal follow-up found substantially different patterns..." — "While" carries the handoff.
- Disconnected: a paragraph ends "The statistical model captures the correlation; the mechanism remains unspecified." The next opens cold; the reader has to jump the gap themselves.

### Information Pacing

Not every sentence carries a new claim plus citation. Interleave elaboration sentences that develop the prior claim without introducing new evidence. Readers need breathing room between heavy claims; packed prose exhausts them.

- Paced: "Because the replication used a larger and more diverse sample, the effect size contracted (Patel and Kim, 2019). This reduction reflects not a failure of the original finding but a correction to its population validity..." — the second sentence elaborates without new evidence.
- Packed: every sentence loads a new claim plus a parenthetical citation; the reader processes evidence continuously with no synthesis sentence to rest on.

### Concept Setup

Introduce technical or specialized terms with a one-clause framing on first use. Don't drop terminology and move on; a reader without the domain background is blocked.

- Set up: "the role of inhibitory control, the cognitive capacity to suppress a dominant response in favor of a context-appropriate alternative" — the term is defined inline before further use.
- Dropped: "The analysis assumes *Gauss-Markov conditions* hold across the panel..." — "Gauss-Markov conditions" expects prior econometric knowledge the reader may not have.

### Building Arguments

Walk through reasoning. When there's a counterpoint worth addressing, address it briefly.

- "I'm not saying we shouldn't do X (we probably should, in some cases). But I'm worried we're over-indexing on it."

### Paragraph Length

3 to 5 sentences per paragraph maximum. Each paragraph has one job. Show the example first, then explain the principle.

### Reduced Structures and Parse Load

A reduced relative clause (dropped "that"), a cataphoric pronoun ("one," "this," "that," pointing forward to content the sentence hasn't yet delivered), or a long noun-phrase subject is each acceptable on its own. Two or three stacked in one sentence force the reader to backtrack to identify the subject. Limit yourself to one parse-load element per sentence; if the argument needs more, split the sentence.

Prefer the explicit "that" when the sentence already has a long subject, a cataphoric reference, or multiple clauses. The word savings are not worth the parse cost. This is a principled exception to the Core Rule's cut bias: "that" is optional grammatically but load-bearing for readability once a sentence carries other parse-load elements.

- Stacked: "The axis Moore's data reveals is one the names themselves display across the census record, and the morphological contrast this prospectus has traced reads onto it directly." Three reduced relatives plus a cataphoric "one"; the reader backtracks to find each subject.
- Split: "Moore's data reveals a vertical axis, and the names themselves display the same axis across the census record. The morphological contrast between transparent names and Ma'heo'o reads onto that axis directly." One idea per sentence, with explicit noun phrases in place of the cataphora.

Signal: if the reader has to re-read a clause to identify its subject, a reduced relative is probably doing the damage. Restore the "that," or split the sentence at the clause boundary.

### Weak Nominalizations

Prefer verbs over nouns made from verbs. Prefer concrete subjects over abstract ones. A chain of abstract nouns ("the scope of X… the widening into Y… the strategies Z uses to place W in relation to…") reads as institutional padding even when every word passes the Core Rule's cut test. This is the opposite failure mode of over-compression: when the cut-bias stops firing, the prose expands into abstract-noun cascades that disconnect the agent from the action.

- Nominalized: "widening the scope to the morphological strategies the Cheyenne lexicon uses to place bearers in relation to what the culture considers sacred"
- Verbed: "widening the scope to the Cheyenne morphology that marks which bearers the culture treats as sacred"

Watch especially for sentences whose subject is an abstract noun made from a verb ("the argument," "the question," "the distinction," "the tension," "the refusal") when every clause extends the cascade. Rewrite around a concrete agent and an active verb when the subject doesn't need to stay abstract. Small-word redundancy is a related tell; a repeated "as" ("read as X rather than as Y" should be "read as X rather than Y") survives the Core Rule because individual words pass but the pattern is compression-artifact slack.

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
