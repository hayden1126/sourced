# Voice rules

Voice calibration tuned to {{USER}}'s academic writing. The shipped `academic` voice encodes academic-register defaults for tone (stance, sentence shape, stance markers), structure (connectedness, pacing, argument building), and dimension (analogies, punctuation habits, formatting). Copy to a new name and edit for a different author within the academic register; for a different register (casual, technical, journalistic, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 8 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Sub-register taxonomy

Academic writing is not a single register. This voice covers three sub-registers; rules below are tagged with the sub-register where they apply strongly. Untagged rules apply across all three.

- **`academic-report`** — formal third-person prose with declarative thesis, citation-dense development, and section-end synthesis. Default when the brief does not specify sub-register. Examples: research papers, literature reviews, course reports.
- **`prospectus`** — compressed academic-report, usually 3–4 pages. Claim-forward opening (no narrative lure), argument-first development, forward-looking closing ("In the poster I will..."). No first-person stance; first-person appears only in process statements about the paper itself.
- **`personal-essay`** — first-person argumentative with question-driven structure. May delay thesis across multiple paragraphs for a narrative lure. Examples: admissions essays, reflection pieces.

When the corpus spans multiple sub-registers, `voice-extractor` produces one voice file per sub-register rather than unioning them; see `data/agents/voice-extractor.md § Multi-register corpora`. Unioning is the documented failure mode (a `personal-essay` first-person commitment rule imported into an `academic-report` produces awkward prose).

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field. The declaration filters which rules below apply. If the brief does not specify, assume `academic-report` and flag the assumption in the prose-plan.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

### Exhibit 1 — academic-report

> The material manifestation of this religious ideology is concentrated in two primary sacred objects: the Sacred Buffalo Hat (*Ésevone*) and the Sacred Arrows (*Maahōtse*). The Sacred Buffalo Hat was brought to the Cheyenne by the cultural hero Erect Horns, who received the gift from the Creator after entering a sacred mountain alongside a woman. This journey represents a passage into the Deep Earth (*Nsthoaman*), a subterranean realm that corresponds to the absolute downward direction of the universe, or the nadir. Because the Hat originates from this realm, this explains why the Cheyenne recognize it as "the female power." This identity is further reflected in the Hat's name; while *Ésevone* colloquially translates to "female bison," its linguistic roots mean "Something Coming Out of the Ground."

<!-- annotation:
S1=opener-claim (names the two objects, sets up the pair structure); opener-shape=state-claim-flat
S2=development-narrative (origin story of object A); parenthetical-gloss on Ésevone
S3=development-connect (connects origin to cosmological location); parenthetical-gloss on Nsthoaman
S4=development-interpret (because-clause ties location to gender coding)
S5=closure-etymological-confirmation (translation pairing confirms the gender reading); closure-type=synthesis
paragraph-pattern: state-pair → develop-A → connect-to-cosmology → interpret → confirm-via-etymology
handoff-to-next: transitions from "the Hat" to the Arrows, which structures the next paragraph
source: my_writing/report_2.txt (adapted for brevity)
-->

### Exhibit 2 — prospectus

> Cheyenne personal names function as morphologically transparent predicates: small claims about their bearers, assembled from parts with identifiable meanings. And these place their bearers along a vertical cosmological axis. Standing at the top of the cosmological axis is the Creator, *Ma'heo'o*. Contrarily, *Ma'heo'o* is not morphologically transparent. Its translation, "All-Father," does not hold up under Cheyenne phonology, and no alternatives accurately translate.

<!-- annotation:
S1=opener-thesis-flat (declarative thesis, no lure); opener-shape=state-claim-flat
S2=thesis-amplifier (adds the cosmological placement claim)
S3=thesis-specialize (introduces the Creator as the apex of the axis)
S4=pivot (names the contrast that drives the paper)
S5=closure-problem-statement (sets up the phonological argument for body paragraphs); closure-type=transitional
paragraph-pattern: thesis → amplifier → specialize → pivot → problem-statement
handoff-to-next: "All-Father" becomes the load-bearing term of the next paragraph, which explains transparent predicates
source: report_3.pdf (Hayden's edited prospectus opening)
-->

### Exhibit 3 — personal-essay

> I believe language itself can be heterotopiac — both a bridge and a boundary. Heritage language instruction creates spaces where bilingual students can think in their native tongue, preserving cultural identity while engaging with dominant academic discourse. Yet this same instruction risks reinforcing the separation it seeks to dismantle. If students develop fluency in their heritage language but never build comparable capacity in the surrounding society's language of power, the classroom becomes a refuge rather than a bridge. Would it create an environment so comfortable that there is no incentive to engage with the broader society?

<!-- annotation:
S1=opener-first-person-commitment (stance claim); opener-shape=state-commitment-I
S2=development-positive-case (builds the claim's affirmative support)
S3=pivot-contrast ("Yet" signals the counterpoint; handoff connective)
S4=development-counter-case (builds the risk)
S5=closure-question-out (question that opens the next paragraph); closure-type=question-out
paragraph-pattern: I-commit → amplify → pivot-Yet → counter-case → question-out
handoff-to-next: question asked in S5 is answered in the next paragraph, which picks up the "environment" frame
source: my_writing/UW Essay 2.pdf (condensed from multiple paragraphs)
-->

Voice-extractor replaces these shipped exhibits with corpus-derived paragraphs when run against an author's samples. The shipped exhibits are illustrative of the shape, not defaults to retain; the extractor's output file carries the author's actual patterns.

## Tone

### Stance

**Rule `[register: personal-essay]`.** State views in the first person and commit to positions: "I believe," "I think," "I notice," "I struggle to imagine." When uncertainty is genuine, name it directly ("The more I consider it, the less certain I become") rather than adding modal qualifiers for safety. First-person commitment is a genre marker of the personal essay; absence of it flattens the register.

**Rule `[register: academic-report, prospectus]`.** State views in third-person declarative. First-person stance markers ("I think," "I believe," "my claim is") are genre-wrong in formal academic writing; they mark undergraduate-essay register where the genre expects scholarly-voice. First-person is acceptable only in process statements about the paper itself ("In the poster I will extend...", "In the next section I address..."). Commit to positions through the structure of the sentence (what it asserts, how it handles counterpoints) rather than through pronoun markers.

**Exemplars `[personal-essay]`:**
- "I believe language itself can be heterotopiac — both a bridge and a boundary."
<!-- source: UW Essay 2.pdf -->
- "The more I consider it, the less certain I become on supporting either model."
<!-- source: UW Essay 2.pdf -->

**Exemplars `[academic-report, prospectus]`:**
- "Cheyenne personal names function as morphologically transparent predicates: small claims about their bearers, assembled from parts with identifiable meanings."
<!-- source: report_3.pdf -->
- "For the Cheyenne people, or *Tsétsėhéstȧhese*, the universe is an animate system that requires constant spiritual maintenance to survive."
<!-- source: my_writing/report_2.txt -->

**Not:** "It is evident that..." / "Perhaps one might consider possibly..." (register-neutral hedging). In academic-report: "I think the evidence suggests..." (first-person import from personal-essay).

### Sentence Structure

**Rule.** Sentences are medium to long by default, with connective tissue binding them. Short declaratives ("Likely not." "Change will not come easily.") mark pivots and emphatic endpoints — they are not the baseline. Do not default to fragments; the short form signals that the argument has reached a turning point.

**Exemplars:**
- "This deep spiritual connection is reflected in Cheyenne grammar, which spiritually imbues certain objects with peoplehood, the state of being a person."
<!-- source: my_writing/report_1.txt -->
- "Change will not come easily. But if we succeed, perhaps we will witness a world where minorities are no longer fighting to be heard."
<!-- source: UW Essay 2.pdf -->

**Not:** a paragraph composed entirely of short isolated declaratives, with no causal or contrastive links between them.

### Exploratory vs Verdict Tone

**Rule.** Claims along the way read as exploration; verdicts are reserved for conclusions. Hold questions open for multiple paragraphs before resolving them. Body paragraphs may end with a question (especially in `personal-essay`) rather than a closed statement. Reserve decisive framings for synthesis at section ends, not for every sentence en route.

**Exemplars `[personal-essay]`:**
- "Would it create an environment so comfortable that there is no incentive to engage with the broader society?"
<!-- source: UW Essay 2.pdf -->
- "Have our genes made us too 'selfish'? How can we claim greater value if we increasingly sabotage the survival of the very copies we are meant to protect?"
<!-- source: UW Essay 3.pdf -->

### Including the Reader

**Rule `[register: personal-essay]`.** Use "we" to make the argument collaborative. Move between "I" (personal stance) and "we" (shared reasoning) within the same essay. The shift is not mechanical — "I" grounds a personal observation, "we" invites the reader into the argument's implications.

**Rule `[register: academic-report, prospectus]`.** "We" is rare; "the reader," "one," "this paper" are also flattening if overused. Default to third-person declarative about the subject matter; the argument speaks through what it claims, not through a rhetorical reader-address.

**Exemplars `[personal-essay]`:**
- "If we neglect this, we risk reinforcing the very heterotopias that bilingual education seeks to dismantle. We risk creating a new era of separation, of prejudice."
<!-- source: UW Essay 2.pdf -->

**Not:** "The reader must recognize..." / "One should consider..." — these lecture rather than invite.

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." Ground claims with numbers, specific conditions, or concrete comparisons — not vague qualifiers. "Perhaps" appears in genuine uncertainty ("Perhaps the Walled City warns us...") but not as padding. When in doubt, cut it and check whether the claim is weaker or just more honest.

### No Preamble

**Rule.** Never start a paragraph or turn with "Great question!" / "That's interesting." / "Let me..." Open on substance: a term to define, a claim to interrogate, a named scholar's position, or a personal observation that frames the argument.

## Structure

### The Core Rule

**Rule.** Every word fights to stay. If a sentence adds nothing, cut it. If two sentences say the same thing differently, merge them into one shorter sentence. No filler, no padding, no repetition.

Writing is sculpting: start with raw material, then chisel. Write a draft, step back, cut, rewrite. Repeat. The first version is never the final version.

**Concision is a means, not an end.** The baseline register for this voice is medium-to-long connected prose (see `### Sentence Connectedness`); chiseling below that baseline is a failure mode, not a success. If cutting a word makes the sentence awkward to read aloud, put the word back. If compressing two sentences into one merges two different thoughts, do not merge them. "Every word fights to stay" means filler doesn't survive; it does not mean every removal is a win. A grammatically tight sentence that trips the reader on first read has been over-chiseled. The fix is to restore connective tissue, not to defend the compression.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence add something the reader doesn't already know?
- Does it repeat an idea from another part of the text?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Does it earn its place in the argument?
- Does it read fluidly aloud, or does the reader trip on it? A clipped fragment ("none of the three resolves"), a stranded preposition that lands awkwardly ("where is the 'there' the stem points at?"), or a register-high verb where a plain one would carry the meaning ("legible" where "visible" works) all signal over-compression. Restore the word or restructure around a different shape.
- Does this paragraph end on an aphoristic closure ("X is itself Y," "W handles what it handles," "That is the limit the paper holds")? That is a `## Cut patterns > aphoristic-closure` hit (also §10 canonical ID `aphoristic-closures`); restructure to `closure-type: transitional` or `synthesis` and drop the rhetorical shape.
- Does a negation sentence sit immediately before an affirmation that asserts the alternative? That is §10's "not X but Y" pattern retokenized with a period; break the adjacency or drop the negation.
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then present the draft for feedback. This is not optional polish; this is the process. First drafts are raw material, not output.

### Sentence Connectedness

**Rule.** Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing connective ("because," "since," "while," "instead," "so that," "as," "when"). Sentence-initial connectives ("Yet," "Still," "Whereas," "Nevertheless," "However," "While") appear throughout the corpus — this is the defining structural habit. A paragraph of complete-on-their-own declaratives makes the reader do the connecting and reads as a stream of verdicts rather than an argument.

**Exemplars:**
- "Whereas Benjamin laments that the original's aura 'withers' through reproduction, French sociologist Jean Baudrillard questions whether an 'original' still exists at all."
<!-- source: UW Essay 3.pdf -->
- "While the Hat embodies generative female power, it functions alongside the Sacred Arrows, which is operated under a male-governed framework."
<!-- source: my_writing/report_2.txt -->

Academic prose defaults to longer connected sentences; the short form is for emphasis at pivots, not the baseline.

### Paragraph Flow

**Rule.** Paragraphs set up, develop, and hand off. End a paragraph on a transition that opens the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a contrastive connector, a concept the prior paragraph positioned, or a direct reference back.

**Exemplar (paragraph-pair handoff):**
- A paragraph on the balanced bilingual model ends on Rodriguez's critique of it; the next opens "The transitional model uses the heritage language as a temporary bridge..." — the handoff is the contrast between the two models, not a summary verdict on the first.
<!-- source: UW Essay 2.pdf -->

**Not:** ending a paragraph on "And so copies of art, however cherished, cannot fully match the original in aura or value" and then opening the next paragraph cold on Baudrillard without a bridging connector.

### Information Pacing

**Rule.** Not every sentence carries a new claim plus citation. Interleave elaboration sentences that develop a prior claim without introducing new evidence. After citing a scholar, typically add a sentence of implication or synthesis before moving to the next source.

**Exemplar:**
- "Aura and authenticity may not belong solely then, to original 'originals.'" (elaboration after the description of the Tuscan painting) — the synthesis sentence precedes the next scholar.
<!-- source: UW Essay 3.pdf -->

### Concept Setup

**Rule.** Introduce technical or specialized terms with a one-clause framing on first use. Define inline: "heterotopia," "simulacra," "hyperreality," "ExAhestOtse," "obviative" all get framed before use. Do not drop terminology and move on.

**Exemplar:**
- "The term *heterotopia*, first introduced by philosopher Michel Foucault, describes spaces that exist as 'other': 'effectively enacted utopias' that 'represent' yet simultaneously 'challenge and invert' the societies that surround them."
<!-- source: UW Essay 2.pdf -->

### Building Arguments

**Rule.** Walk through reasoning. When there is a counterpoint worth addressing, address it. Present multiple competing scholars' positions within a single essay and adjudicate between them rather than ignoring the competition. Say when an argument is compelling and when it is incomplete.

**Exemplar `[personal-essay]`:**
- "I want to believe in Villanueva's vision: that bilingual education empowers marginalized students in America. Yet Rodriguez's concern lingers: does linguistic comfort foster 'public alienation'?"
<!-- source: UW Essay 2.pdf -->

### Paragraph Length

**Rule.** 3 to 5 sentences per paragraph. Each paragraph has one job. Show the example first, then explain the principle (for inductive paragraphs); state the claim first, then develop (for deductive paragraphs — academic-report default).

### Reduced Structures and Parse Load

**Rule.** A reduced relative clause (dropped "that"), a cataphoric pronoun ("one," "this," "that," pointing forward to content the sentence hasn't yet delivered), or a long noun-phrase subject is each acceptable on its own. Two or three stacked in one sentence force the reader to backtrack to identify the subject. Limit yourself to one parse-load element per sentence; if the argument needs more, split the sentence.

Prefer the explicit "that" when the sentence already has a long subject, a cataphoric reference, or multiple clauses. The word savings are not worth the parse cost. This is a principled exception to the Core Rule's cut bias: "that" is optional grammatically but load-bearing for readability once a sentence carries other parse-load elements.

**Exemplars:**
- Stacked (violates): "The axis Moore's data reveals is one the names themselves display across the census record, and the morphological contrast this prospectus has traced reads onto it directly." Three reduced relatives plus a cataphoric "one"; the reader backtracks.
- Split (fix): "Moore's data reveals a vertical axis, and the names themselves display the same axis across the census record. The morphological contrast between transparent names and *Ma'heo'o* reads onto that axis directly."
<!-- source: report_3 (before/after from tmp.md §2) -->

### Weak Nominalizations

**Rule.** Prefer verbs over nouns made from verbs. Prefer concrete subjects over abstract ones. A chain of abstract nouns ("the scope of X… the widening into Y… the strategies Z uses to place W in relation to…") reads as institutional padding even when every word passes the Core Rule's cut test. Opposite failure mode of over-compression: when the cut-bias stops firing, prose expands into abstract-noun cascades.

**Exemplars:**
- Nominalized: "widening the scope to the morphological strategies the Cheyenne lexicon uses to place bearers in relation to what the culture considers sacred"
- Verbed: "widening the scope to the Cheyenne morphology that marks which bearers the culture treats as sacred"
<!-- source: tmp.md §1 -->

Watch especially for sentences whose subject is an abstract noun made from a verb ("the argument," "the question," "the distinction," "the tension," "the refusal") when every clause extends the cascade. Rewrite around a concrete agent and an active verb when the subject doesn't need to stay abstract. Small-word redundancy is a related tell; repeated "as" ("read as X rather than as Y" should be "read as X rather than Y") survives the Core Rule because individual words pass but the pattern is compression-artifact slack.

### Parenthetical Gloss `[register: academic-report, prospectus]`

**Rule.** Introduce transliterated terms, proper nouns from a non-English language, or specialized vocabulary with a parenthetical gloss inline on first use. Use `(English gloss)` after a native term or `(native term)` after an English gloss, not footnotes. On second and later appearances, no gloss needed — the term is established. This is one of the most consistently visible structural habits in academic prose that touches non-English material.

**Exemplars:**
- "For the Cheyenne people, or *Tsétsėhéstȧhese*, the universe is an animate system..."
<!-- source: my_writing/report_2.txt -->
- "...a passage into the Deep Earth (*Nsthoaman*), a subterranean realm..."
<!-- source: my_writing/report_2.txt -->
- "at the axis's nadir (downward direction)"
<!-- source: report_3.pdf -->

## Dimension

### Analogies and Anecdotes

**Rule.** Connect ideas to broader patterns. Use specific, memorable anchors to make abstract claims concrete: a self-contained historical or cultural example is introduced, described briefly, and then explicitly connected to the essay's central argument. The connection is always stated, never implied and left for the reader to infer.

**Anchors:** TBD — derived from corpus. Academic-register anchors often include recurring case studies, named experiments, or specific empirical phenomena the author returns to across multiple papers as illustrative touchstones for abstract claims — canonical cross-disciplinary patterns are things like Ship of Theseus (identity under incremental change), the streetlight effect (methodological convenience vs. truth), or Chesterton's fence (epistemic humility about removing structures you don't understand). voice-extractor replaces this placeholder with the author's actual anchors from the corpus; the patterns above are illustrative of the kind, not defaults to keep.

Not every vivid analogy earns its place. Drop it if the connection to your specific claim is loose. Cut back an analogy you find yourself extending across multiple paragraphs to keep it working: it should illuminate one point, not run the argument.

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. Use this section only for author-specific punctuation habits the corpus clearly shows beyond the §10-governed patterns.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns (academic corpus typical):**
- Colons introduce evidence, elaboration, or a question the preceding clause poses.
- Semicolons: light use in reports, rare in personal essays.
- No trailing ellipses.

### Formatting

**Rule.** **Bold** for emphasis (not caps). *Italics* for technical terms, transliterated words, and cited titles. Bullet points sparingly, and not in the body of analytical prose.

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 8 explicitly flag. Each pattern carries a provisional-name tag; mining `failures_dir` pairs (`<stem>.ai.md` / `<stem>.edit.md`) populates author-specific instances into this section at extraction time. Shipped patterns are register-default; the extractor adds or removes based on corpus evidence.

Canonical patterns (shipped defaults):

### aphoristic-closure

**Pattern.** Paragraph ends on a crisp, rhetorically-balanced pronouncement that substitutes rhetoric for reasoning. Signatures: "X is itself Y," "W handles what it handles," "That is the limit the paper holds," "Y persists while X drifts," "No stronger claim is intended."

**Why it reads as AI.** The shape is a "profundity closure" — it sounds thesis-like without doing argument work. The reader has been given a feeling of resolution, not actual resolution.

**Fix.** Restructure to a `transitional` or `synthesis` closure: end on what the next paragraph picks up, or end on a factual consequence the argument has earned.

**Before / after:**
- AI: "The grammar of placement has a ceiling, and the Creator's name sits above it."
- Edit: (cut entirely; the claim is redundant given the preceding paragraph's setup)
<!-- source: report_3 v2 → pdf -->

- AI: "*Ma'heo'o*'s exemption is itself the interesting linguistic fact: it holds both phonetically and morphologically."
- Edit: (cut; the next paragraph's phonological argument makes the point directly)
<!-- source: report_3 v2 → pdf -->

This pattern corresponds to canonical §10 ID `aphoristic-closures`. A `## §10 exemptions` bullet naming `aphoristic-closures` is required to use this pattern in writer prose.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision, producing a sentence that reads as a fragment of a longer thought. Signatures: "none of the three resolves" (resolves what?), "any correction has to reach" (reach what?), "the argument becomes visible" (visible where/how?).

**Why it reads as AI.** The cut-bias of the Core Rule has fired past the readability threshold. The sentence is grammatically optimal and word-count minimal; it trips the reader on first read.

**Fix.** Restore the stranded complement. The word savings are not worth the parse cost (same principle as `### Reduced Structures and Parse Load`).

**Before / after:**
- AI: "none of the three resolves"
- Edit: "none of the three readings settles the meaning"
<!-- source: tmp.md §1 -->

- AI: "where is the 'there' the stem points at?"
- Edit: "what 'there' does the stem point to?"
<!-- source: tmp.md §1 -->

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs ("scope," "strategies," "lexicon," "relation," "placement") stacked across clauses without a concrete agent or active verb. Signature: sentences whose subject is "the argument," "the question," "the tension," "the refusal," extended across 2+ clauses.

**Why it reads as AI.** Inverse failure mode of `compression-stranded-verb`: when the cut-bias stops firing, prose expands into institutional-noun cascades that disconnect agent from action.

**Fix.** Rewrite around a concrete subject + active verb. Same guidance as `### Weak Nominalizations`.

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in a single sentence, often combined with a cataphoric pronoun. Signature: "the axis Moore's data reveals is one the names themselves display across the census record, and the morphological contrast this prospectus has traced reads onto it directly."

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack. Same root as `compression-stranded-verb` — optimization for word count at the cost of parseability.

**Fix.** Restore "that" and/or split the sentence. See `### Reduced Structures and Parse Load`.

### first-person-commitment-in-academic-report

**Pattern `[register-drift: personal-essay → academic-report]`.** First-person stance markers ("I think," "I believe," "my claim is," "I read these as...") appearing in `academic-report` or `prospectus` prose.

**Why it reads as AI.** When a voice file is extracted from a multi-register corpus and unioned, personal-essay stance rules bleed into formal-register drafting. The resulting prose reads as undergraduate-essay register where the genre expects scholarly-voice.

**Fix.** Rewrite as third-person declarative. First-person only in process statements about the paper itself ("In the poster I will extend...").

**Before / after:**
- AI: "I think that irresolution is worth the analysis. My claim in this paper is this: Cheyenne personal names are..."
- Edit: "Cheyenne personal names function as morphologically transparent predicates: small claims about their bearers, assembled from parts with identifiable meanings."
<!-- source: report_3 v2 → pdf -->

### citation-atomization

**Pattern `[register: academic-report, prospectus]`.** Fine-grained Pandoc IDs for the same domain treated as separate sources when a human writer would merge. Signature: `@leman-nda-001; @leman-ndb-001; @leman-ndc-001; @leman-ndd-001` all pointing at cheyennelanguage.org pages; each rendered as a separate parenthetical citation.

**Why it reads as AI.** Granular IDs betray the `source-finder` shard architecture. A human writer recognizes that multiple pages of one site or multiple entries of one dictionary are one citation.

**Fix.** At `[formatting mode]` time (or at drafting time for inline parentheticals), consolidate IDs that resolve to the same References entry.

**Before / after:**
- AI: "(Leman, n.d.-a), (Leman, n.d.-b), (Leman, n.d.-c)..."
- Edit: "(Cheyenne Language Web Site)" — single-citation consolidation
<!-- source: report_3 v2 → pdf -->

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

### §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
