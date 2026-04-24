# Voice rules

Voice calibration tuned to {{USER}}'s journalistic writing — news stories, feature pieces, commentary, reported essays. The shipped `journalistic` voice is a register-specific skeleton: it encodes journalistic-register defaults for tone (lede-first, active voice, attributed), structure (inverted pyramid, news-peg argumentation), and dimension (illustrative anecdotes, plain punctuation, formatting light). Copy to a new name and edit for a different author within the journalistic register; for a different register (academic, casual, technical, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

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

Claims carry attribution. "According to X, Y" rather than "Y is true." In commentary, state the view once, plainly; don't hedge repeatedly.

- "Federal officials said the program would launch in June."
- "Critics argued the timeline was unrealistic."

Not: "It is believed that the program will launch in June."
Not: "The timeline is, arguably, possibly, perhaps unrealistic."

### Sentence Structure

Subject-verb-object, active voice. Keep subjects concrete: people, organizations, actions, not abstractions. Subordinate clauses allowed when they add context, not when they defer the main point.

- "The mayor announced the plan Monday."
- "Officials declined to name the source, citing ongoing negotiations."

Not: "It was announced by the office of the mayor that the plan would proceed."

### Exploratory vs Verdict Tone

Journalistic prose is fact-forward; verdicts appear only in commentary and opinion. Reporting states what is known and attributes it. Opinion pieces can take a stance but must make it visible as a stance, not smuggle it in as fact.

- Reporting: "The agency rejected the application on April 3, citing incomplete documentation."
- Commentary (stance visible): "The agency's rejection reads as procedural cover for a decision made weeks earlier."
- Smuggled verdict (fails audit): "The agency, predictably, rejected the application." Reporting prose cannot carry "predictably" without attribution.

### Thinking Out Loud

Rare in reporting. Common in columns and commentary. In commentary, walk the reader through your reasoning but keep it tight; journalistic prose doesn't indulge the mental wandering that academic or casual prose permits.

- Column: "The obvious objection is that voters don't care about procedural norms. Maybe. But the polling from March suggests otherwise."
- Reporting (no thinking-out-loud): state the facts and attributions; speculation belongs to sourced analysts, not the reporter.

### Including the Reader

Third person dominates in reporting. First-person is reserved for reported essays and columns, where the writer's presence in the story is the point.

- Reporting: "Readers may wonder whether the agency had authority to act unilaterally."
- Reported essay: "The central question, as I followed the case through three hearings, is whether the statute means what it says."

Not: "We all know the agency overstepped." Reporting cannot assume reader agreement; commentary must earn it.

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite important" becomes "This is important." Ground claims with numbers, attributed quotes, or specific comparisons, not vague qualifiers. "Many papers have been retracted for manipulation" becomes "In 2019, 23% of retracted papers had been cited more than 100 times." Journalistic prose prizes concrete detail; weak adverbs feel especially out of place next to a hard number or a named source.

### No Preamble

Start with the lede. Skip throat-clearing entirely, no "Recent events have prompted..." or "This week saw..." The first sentence carries the who, what, when, or why; warm-up sentences don't exist in journalistic prose.

## Structure

### The Core Rule

Every paragraph earns its place in the story. If a paragraph doesn't advance the reader's understanding of the news peg, cut it. Reporting has a tight word budget; feature pieces run slightly looser; columns tightest of all.

Drafting is sculpting: start with the reporting, then chisel to the story. Write a draft, step back, cut everything that doesn't advance the lede, rewrite. Repeat. The first version is never the filed version.

**The iteration loop.** After writing a draft, reread every paragraph and ask:
- Does this paragraph advance the reader's understanding of the news peg?
- Does it repeat information already delivered?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Is every factual claim attributed?
- Does the piece hold when read from top to bottom at pace?

If any answer is no, rewrite or cut. Then reread again. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then file the draft.

This is not optional polish. This is the process. First drafts are reporting notes in paragraph shape, not copy.

### Sentence Connectedness

Sentences connect through shared subjects and chronological progression. Formal connectives ("because," "however," "instead") appear at key pivots, not between every sentence. Journalistic prose favors implicit connection: the next sentence continues the same actor or picks up the next moment in the sequence.

- Connected (shared subject): "The governor vetoed the bill Thursday. She said the measure would have exposed the state to federal litigation. Her office released the veto message within the hour."
- Connected (pivot with "however"): "The committee voted 9 to 4 to advance the nomination. However, two members who voted yes said they would oppose the nominee on the floor."
- Disconnected: "The veto came Thursday. The federal government had threatened litigation. Her office stayed quiet." The reader has to supply the causal link.

### Paragraph Flow

Inverted pyramid. The most important fact goes in the first paragraph. The second-most-important in the second. And so on. Feature pieces relax this but still lead with the hook.

- First paragraph names the who, what, when. "A federal judge on Tuesday blocked the new visa rule, siding with a coalition of universities that sued last month."
- Second paragraph adds context, why it matters. "The ruling reopens the pipeline for an estimated 40,000 graduate students whose applications had been frozen since January."
- Third paragraph introduces the tension or conflict. "Administration lawyers said they would appeal; the plaintiffs called the ruling a vindication of established law."

Disconnected flow: leading with setup ("For decades, visa policy has been contested...") defers the news and loses the reader by paragraph three.

### Information Pacing

Facts and attribution alternate. Claim, attribution, claim, attribution. Heavy packing of facts without attribution reads as editorial; dense strings of attributions without content read as hedged.

- Paced: "The district spent $2.3 million on the program last year, according to the superintendent's office. The money covered training, materials, and a new assessment system. Teachers said the assessment was the most visible change in the classroom."
- Packed (fact-heavy, no attribution): "The district spent $2.3 million on training, materials, and an assessment system that teachers found visible in the classroom, a change driven by last year's board decision that also restructured the central office." The reader cannot tell which clause is reported and which is analysis.

### Concept Setup

Define unfamiliar terms parenthetically and quickly. Readers won't tolerate a pause for a three-sentence definition; give them enough to keep reading and move on.

- Set up: "The agency uses reverse-repurchase agreements (overnight loans collateralized by Treasury securities) to manage short-term rates."
- Set up, one clause: "The union filed a ULP, an unfair labor practice charge, alleging the district bargained in bad faith."
- Dropped: "The agency's repo operations set the floor on the policy rate." Readers without a finance desk background cannot follow.

### Building Arguments

In commentary: name your claim, support it with reporting, anticipate the obvious counterargument briefly, move on. Don't stage-manage a debate the reader didn't come for.

- "The bill is worse than its sponsors claim. Three provisions, on funding, enforcement, and reporting, do less than the sponsors' own summary suggests. The obvious defense, that the bill is a first step, doesn't hold: the first-step framing was also offered in 2019, and the 2019 bill was never followed up."

### Paragraph Length

1 to 3 sentences is the baseline for reporting. 2 to 4 for features. 3 to 5 for columns. Single-sentence paragraphs are common at pivot points and shouldn't be avoided; they mark the shift from one phase of the story to the next.

## Dimension

### Analogies and Anecdotes

Anecdotes anchor human stories. One-paragraph vignettes: a named person, a specific moment, a quoted line. Analogies draw from everyday experience, not domain-technical machinery.

**Anchors:** TBD, derived from corpus. Journalistic-register anecdotes often feature named subjects, specific scenes, and direct quotes.

Not every vivid anecdote earns its place. Drop it if it doesn't connect to the news peg; the story isn't about the anecdote, the anecdote serves the story. Cut an anecdote you find yourself extending across multiple paragraphs: a vignette is a moment, not a scene.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*, not a comma or parenthesis substitution that preserves the mid-clause-interruption rhythm. Use this section only for author-specific punctuation habits the corpus clearly shows. Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly; silence defers to §10.

Semicolons are rare in journalistic prose. Colons introduce attribution or lists. Quotation marks carry direct speech, always attributed to a named source or, when the source can't be named, a clearly labeled role ("a senior official said").

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

### Formatting

Sparingly. **Bold** for pull quotes in some publications; check house style. *Italics* for publication titles, ship names, and legal case names. Bullets only when content is genuinely list-shaped (vote tallies, enumerated findings, day-by-day timelines); flowing prose otherwise.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. The annotation vocabulary (`S1=<role>; ... closure-type=...`) matches the prose-plan's sentence-role sequence used by `[writing mode]` Phase 1 and `prose-drafter`.

TBD — derived from corpus. voice-extractor populates this section with 1–3 corpus-derived paragraphs when run against an author's samples.

## Cut patterns

Named failure modes observed in AI-drafted prose. `voice-extractor` and `[editing mode]` Pass 7 flag these explicitly. Shipped patterns below are register-default; the extractor adds author-specific patterns when a `failures_dir` is provided.

### aphoristic-closure

**Pattern.** Paragraph ends on a rhetorically-balanced pronouncement that substitutes rhetoric for reasoning.
**Fix.** Restructure to `closure-type: transitional`, `synthesis`, or `question-out`. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for concision, producing a fragment-like sentence.
**Fix.** Restore the stranded complement.

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs stacked across clauses without a concrete agent.
**Fix.** Rewrite around a concrete subject + active verb.

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in one sentence.
**Fix.** Restore "that" or split the sentence.

Additional canonical patterns apply in register-specific contexts: `first-person-commitment-in-academic-report` (academic registers only), `citation-atomization` (citation-dense registers only).
