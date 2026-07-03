# Voice rules

Voice calibration tuned to {{USER}}'s journalistic writing — news stories, feature pieces, commentary, reported essays. Encodes journalistic-register defaults under the phase-3 sub-register contract: tone (lede-first, active voice, attributed), structure (inverted pyramid, news-peg argumentation), dimension (illustrative anecdotes, plain punctuation, formatting light). Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 8 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Sub-register taxonomy

Journalistic writing is not a single register. This voice covers three sub-registers; rules below are tagged with the sub-register where they apply strongly. Untagged rules apply across all three.

- **`news-report`** — straight reporting; inverted pyramid; full attribution; no first-person; no editorial stance. Examples: news stories, agency briefs, court reports.
- **`feature`** — narrative reporting; scene-setting allowed; named subjects with quoted dialogue; first-person occasionally if the writer is in the story. Examples: longform features, profiles, reported essays.
- **`commentary`** — opinion column; named stance; first-person standard; argument-forward with anticipated counterarguments. Examples: op-eds, opinion columns, editorial-page pieces.

When the corpus spans multiple sub-registers, `voice-extractor` produces one voice file per sub-register rather than unioning them; see `data/agents/voice-extractor.md § Multi-register routing`. Unioning is the documented failure mode (a `commentary` first-person stance rule imported into `news-report` produces editorialized reporting that fails the basic attribution discipline of the genre).

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field. The declaration filters which rules below apply. If the brief does not specify, assume `news-report` (the journalistic default — strictest baseline) and flag the assumption in the prose-plan.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

### Exhibit 1 — news-report (illustrative)

> A federal judge on Tuesday blocked the new visa rule, siding with a coalition of universities that sued last month. The ruling reopens the pipeline for an estimated 40,000 graduate students whose applications had been frozen since January. Administration lawyers said they would appeal; the plaintiffs called the ruling a vindication of established law. The decision is the third in two months to halt agency rules issued under emergency authority.

<!-- annotation:
S1=lede (who, what, when in one clause); opener-shape=lede-active-voice
S2=development-stakes (why-it-matters: scope of impact with one specific number)
S3=development-conflict (both sides quoted; semicolon links the two attributions)
S4=closure-context (places the decision in a pattern; transitions to next paragraph on the broader trend); closure-type=transitional
paragraph-pattern: lede → stakes → conflict → context
handoff-to-next: the next paragraph picks up "third in two months" and details the prior two rulings
source: illustrative; voice-extractor replaces with corpus paragraph at extraction time
-->

### Exhibit 2 — feature (illustrative)

TBD — voice-extractor populates from corpus when feature samples are present. If the corpus is purely news-report or commentary, this exhibit stays TBD.

### Exhibit 3 — commentary (illustrative)

TBD — voice-extractor populates from corpus when commentary samples are present. If the corpus is purely news-report or feature, this exhibit stays TBD.

Voice-extractor replaces these shipped exhibits with corpus-derived paragraphs when run against an author's samples. The shipped exhibits are illustrative of the shape, not defaults to retain; the extractor's output file carries the author's actual patterns.

## Tone

### Stance

**Rule `[register: news-report, feature]`.** Claims carry attribution. "According to X, Y" rather than "Y is true." Anonymous attribution requires a labeled role ("a senior official said") and editorial justification.

**Rule `[register: commentary]`.** State the view once, plainly; don't hedge repeatedly. The commentary's stance is the writer's own; attribution is not required for the claim, but reporting that supports the claim still is.

**Exemplars `[news-report]`:**
- "Federal officials said the program would launch in June."
- "Critics argued the timeline was unrealistic."

**Exemplars `[commentary]`:**
- "The bill is worse than its sponsors claim."
- "The agency's rejection reads as procedural cover for a decision made weeks earlier."

**Not:** "It is believed that the program will launch in June." (no attributed actor) / "The timeline is, arguably, possibly, perhaps unrealistic." (stacked hedges)

### Sentence Structure

**Rule.** Subject-verb-object, active voice. Keep subjects concrete: people, organizations, actions, not abstractions. Subordinate clauses allowed when they add context, not when they defer the main point.

**Exemplars:**
- "The mayor announced the plan Monday."
- "Officials declined to name the source, citing ongoing negotiations."

**Not:** "It was announced by the office of the mayor that the plan would proceed."

### Exploratory vs Verdict Tone

**Rule `[register: news-report, feature]`.** Fact-forward. State what is known and attribute it. Speculation belongs to sourced analysts, not the reporter. Verdict-language ("predictably," "as expected," "in a stunning move") is editorialization and fails the audit.

**Rule `[register: commentary]`.** Take a stance and make it visible. The reader should be able to tell the column's argument from its reporting. Smuggled verdicts ("the agency, predictably, rejected the application") are weaker than named verdicts ("the agency's rejection was predictable, and here's why").

**Exemplars:**
- Reporting: "The agency rejected the application on April 3, citing incomplete documentation."
- Commentary (stance visible): "The agency's rejection reads as procedural cover for a decision made weeks earlier."
- Smuggled verdict (avoid): "The agency, predictably, rejected the application."

### Thinking Out Loud

**Rule `[register: news-report]`.** Omit. Reporting does not narrate the reporter's reasoning.

**Rule `[register: feature, commentary]`.** Walk the reader through reasoning briefly, but keep it tight. Journalistic prose doesn't indulge the mental wandering that academic or casual prose permits. Mark exploratory passages so the reader can tell them apart from reporting.

**Exemplar `[commentary]`:**
- "The obvious objection is that voters don't care about procedural norms. Maybe. But the polling from March suggests otherwise."

### Including the Reader

**Rule `[register: news-report]`.** Third person dominates. First-person is excluded.

**Rule `[register: feature]`.** First-person is reserved for reported essays where the writer's presence in the story is the point. Use sparingly and intentionally.

**Rule `[register: commentary]`.** First-person is the column's voice. "We" risks claiming reader agreement that hasn't been earned; default to "I" for stance and "the reader" or named groups for shared reasoning.

**Exemplars:**
- News-report: "Readers may wonder whether the agency had authority to act unilaterally."
- Feature: "The central question, as I followed the case through three hearings, is whether the statute means what it says."

**Not:** "We all know the agency overstepped." (assumed reader agreement; commentary must earn it.)

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." Ground claims with numbers, attributed quotes, or specific comparisons, not vague qualifiers. "Many papers have been retracted for manipulation" becomes "In 2019, 23% of retracted papers had been cited more than 100 times." Journalistic prose prizes concrete detail; weak adverbs feel especially out of place next to a hard number or a named source.

### No Preamble

**Rule.** Start with the lede. Skip throat-clearing entirely; no "Recent events have prompted..." or "This week saw..." The first sentence carries the who, what, when, or why; warm-up sentences don't exist in journalistic prose.

## Structure

### The Core Rule

**Rule.** Every paragraph earns its place in the story. If a paragraph doesn't advance the reader's understanding of the news peg, cut it. Reporting has a tight word budget; feature pieces run slightly looser; columns tightest of all.

**Concision is a means, not an end.** Journalistic prose tolerates compression but stranded verbs and dropped attributions still trip the reader. See `## Cut patterns > compression-stranded-verb` and `## Cut patterns > unattributed-claim`.

**The iteration loop.** After writing a draft, reread every paragraph and ask:
- Does this paragraph advance the reader's understanding of the news peg?
- Does it repeat information already delivered?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list.)
- Is every factual claim attributed (in news-report and feature; in commentary, are claims supported)?
- Does the piece hold when read from top to bottom at pace?

If any answer is no, rewrite or cut. Then reread again. First drafts are reporting notes in paragraph shape, not copy.

### Sentence Connectedness

**Rule.** Sentences connect through shared subjects and chronological progression. Formal connectives ("because," "however," "instead") appear at key pivots, not between every sentence. Journalistic prose favors implicit connection: the next sentence continues the same actor or picks up the next moment in the sequence.

**Exemplars:**
- Connected (shared subject): "The governor vetoed the bill Thursday. She said the measure would have exposed the state to federal litigation. Her office released the veto message within the hour."
- Connected (pivot with "however"): "The committee voted 9 to 4 to advance the nomination. However, two members who voted yes said they would oppose the nominee on the floor."

**Not:** "The veto came Thursday. The federal government had threatened litigation. Her office stayed quiet." (reader has to supply the causal link)

### Paragraph Flow

**Rule `[register: news-report]`.** Inverted pyramid. The most important fact goes in the first paragraph; the second-most-important in the second; and so on.

**Rule `[register: feature, commentary]`.** Inverted pyramid relaxes; lead with the hook (a scene, a question, a specific image) but the news peg should land within the first 2–3 paragraphs.

**Exemplar `[news-report]`:**
- First paragraph names the who, what, when. Second paragraph adds context (why it matters). Third paragraph introduces the tension or conflict.

**Not:** Leading with setup ("For decades, visa policy has been contested...") in a news-report defers the news and loses the reader by paragraph three.

### Information Pacing

**Rule.** Facts and attribution alternate. Claim, attribution, claim, attribution. Heavy packing of facts without attribution reads as editorial; dense strings of attributions without content read as hedged.

**Exemplars:**
- Paced: "The district spent $2.3 million on the program last year, according to the superintendent's office. The money covered training, materials, and a new assessment system. Teachers said the assessment was the most visible change in the classroom."
- Packed (avoid): "The district spent $2.3 million on training, materials, and an assessment system that teachers found visible in the classroom, a change driven by last year's board decision that also restructured the central office." (reader can't tell which clause is reported and which is analysis)

### Concept Setup

**Rule.** Define unfamiliar terms parenthetically and quickly. Readers won't tolerate a pause for a three-sentence definition; give them enough to keep reading and move on.

**Exemplars:**
- "The agency uses reverse-repurchase agreements (overnight loans collateralized by Treasury securities) to manage short-term rates."
- "The union filed a ULP, an unfair labor practice charge, alleging the district bargained in bad faith."

**Not:** "The agency's repo operations set the floor on the policy rate." (readers without a finance desk background can't follow)

### Building Arguments `[register: commentary]`

**Rule.** Name your claim, support it with reporting, anticipate the obvious counterargument briefly, move on. Don't stage-manage a debate the reader didn't come for.

**Exemplar:**
- "The bill is worse than its sponsors claim. Three provisions, on funding, enforcement, and reporting, do less than the sponsors' own summary suggests. The obvious defense, that the bill is a first step, doesn't hold: the first-step framing was also offered in 2019, and the 2019 bill was never followed up."

### Paragraph Length

**Rule.** 1–3 sentences for news-report. 2–4 for features. 3–5 for commentary. Single-sentence paragraphs are common at pivot points and shouldn't be avoided; they mark the shift from one phase of the story to the next.

### Reduced Structures and Parse Load

**Rule.** Drop "that" sparingly in journalistic prose. Reporting has the tightest precision requirements of any register; a stacked reduced relative ("the document the agency the court named released") forces the reader to backtrack and may misidentify the actor. See `## Cut patterns > reduced-relative-stacking`.

## Dimension

### Analogies and Anecdotes

**Rule `[register: feature, commentary]`.** Anecdotes anchor human stories. One-paragraph vignettes: a named person, a specific moment, a quoted line. Analogies draw from everyday experience, not domain-technical machinery. Cut an anecdote you find yourself extending across multiple paragraphs — a vignette is a moment, not a scene.

**Rule `[register: news-report]`.** Anecdotes appear sparingly and only when they advance the news peg. A vignette that doesn't connect to the lede is decoration.

**Anchors:** TBD — derived from corpus. Journalistic-register anecdotes often feature named subjects, specific scenes, and direct quotes.

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*. The fix for a flagged em-dash is sentence-shape restructure per §10 *Restructure, don't retokenize*, not a comma or parenthesis substitution that preserves the mid-clause-interruption rhythm. Use this section only for author-specific punctuation habits the corpus shows beyond the §10-governed patterns.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns (journalistic-register baseline):**
- Semicolons rare. Used to link two attributions on the same fact ("officials said X; critics said Y").
- Colons introduce attribution or lists.
- Quotation marks carry direct speech, always attributed to a named source or, when the source can't be named, a clearly labeled role ("a senior official said").

### Formatting

**Rule.** Sparingly. **Bold** for pull quotes in some publications; check house style. *Italics* for publication titles, ship names, and legal case names. Bullets only when content is genuinely list-shaped (vote tallies, enumerated findings, day-by-day timelines); flowing prose otherwise.

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 7 explicitly flag. Each pattern carries a canonical ID; `failures_dir` before/after pairs populate author-specific instances at extraction time. Shipped patterns are register-default.

### aphoristic-closure

**Pattern.** Paragraph ends on a crisp, rhetorically-balanced pronouncement that substitutes rhetoric for reasoning. Journalistic signatures: "And the questions only multiply." / "In a town defined by such tensions, the latest chapter writes itself." / "Time will tell whether the gamble pays off."

**Why it reads as AI.** Reporting should end on a fact, an attribution, or a transition to the next paragraph. A profundity-closure trades concrete information for editorial gesture, blurring the line between reporting and commentary.

**Fix.** Restructure to a `transitional` or `synthesis` closure: end on the next development the story will pick up, or end on the most recent attributed fact. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision. Journalistic signatures: "officials denied" (denied what?), "the report concluded" (concluded what?), "the case proceeds" (proceeds where?).

**Why it reads as AI.** Journalism's precision demand is high — a stranded verb leaves the reader to guess the object, and guesses become misquotes.

**Fix.** Restore the stranded complement. Be specific: officials denied the allegation, the report concluded the program was effective, the case proceeds to oral argument next month.

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs ("the implementation," "the consideration," "the determination") stacked across clauses without a concrete agent.

**Why it reads as AI.** Journalistic prose's hallmark is concrete actors + active verbs ("the mayor announced," "officials said," "the judge ruled"). Nominalization cascades hide the actor behind bureaucratic vocabulary, undermining attribution.

**Fix.** Rewrite around a named agent and an active verb. "The implementation of the policy resulted in concerns" → "Officials raised concerns about how the policy was carried out."

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in one sentence, often combined with a long noun-phrase subject.

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack to identify the actor — fatal in a news report where mis-identification means a correction.

**Fix.** Restore "that" and/or split the sentence. Prefer the explicit "that" when the sentence already carries a long subject or multiple clauses.

### unattributed-claim `[register: news-report, feature]`

**Pattern.** Factual claim presented without attribution, as if the reporter independently knows the fact. Signatures: "The program has been popular." / "Officials are concerned." / "The plan would cost the city millions."

**Why it reads as AI.** AI-drafted journalistic prose tends to assert facts the model has internalized from training, without the chain of attribution that reporting requires. The result reads as authoritative but is operationally editorial.

**Fix.** Attribute every factual claim. Either name the source ("according to a 2024 review by the city auditor"), the document ("the program's annual report"), or the labeled role ("a department official familiar with the matter said"). If the claim can't be attributed, drop it.

### smuggled-verdict `[register: news-report]`

**Pattern.** Editorializing adverb or adjective inserted into reporting prose, where the modifier carries a stance the reporting itself does not establish. Signatures: "The agency, predictably, rejected the application." / "In a stunning move, the council voted to..." / "The administration's bizarre reasoning was that..."

**Why it reads as AI.** AI-drafted reporting tends to import opinion-piece adverbs into news prose. The reader sees an editorialized framing that the reporting doesn't support and the reporter wouldn't have signed off on.

**Fix.** Cut the editorializing modifier. If the stance is supported, move to commentary register and make the stance explicit. If the stance is not supported, removing the modifier strengthens the report.

Additional canonical patterns apply in register-specific contexts: `first-person-commitment-in-academic-report` (academic registers only — N/A here), `citation-atomization` (citation-dense registers only — N/A here).

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

## §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
