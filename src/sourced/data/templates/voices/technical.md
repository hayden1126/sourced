# Voice rules

Voice calibration tuned to {{USER}}'s technical writing — documentation, API references, procedural guides, RFCs, postmortems. Encodes technical-register defaults under the phase-3 sub-register contract: tone (imperative, precise, minimal ornament), structure (one-step-per-sentence, parallel form, bulleted sequences), dimension (diagrams-not-analogies, precise punctuation, code-block-friendly formatting). Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (Phase 1 plan + Phase 2 `prose-drafter` dispatch), and `[editing mode]` (Pass 0 Revision + Pass 8 voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Sub-register taxonomy

Technical writing is not a single register. This voice covers three sub-registers; rules below are tagged with the sub-register where they apply strongly. Untagged rules apply across all three.

- **`reference`** — API docs, function signatures, configuration references. Imperative voice; no first-person; no exploratory hedging. Each entry describes one observable behavior. Examples: language reference, library API docs, CLI flag descriptions.
- **`tutorial`** — step-by-step walkthroughs aimed at a specific learning outcome. Second-person ("you call connect, then..."); contextual asides allowed; concrete examples per step. Examples: getting-started guides, "your first X" posts, codelabs.
- **`design-rationale`** — RFCs, design docs, postmortems, ADRs. Discursive prose with named tradeoffs; first-person plural ("we chose B because...") allowed for team-authored docs; counterargument-naming required. Examples: architecture decision records, postmortems, RFC documents.

When the corpus spans multiple sub-registers, `voice-extractor` produces one voice file per sub-register rather than unioning them; see `data/agents/voice-extractor.md § Multi-register corpora`. Unioning is the documented failure mode (a `tutorial` second-person rule imported into `reference` produces inconsistent prose where some entries address the reader and others state behavior).

**Determining sub-register at write time.** `[writing mode]` Phase 1 declares the sub-register for the section in the prose-plan's Register Mode field. The declaration filters which rules below apply. If the brief does not specify, assume `reference` (the technical default — strictest baseline) and flag the assumption in the prose-plan.

## Worked paragraphs

Paragraph-scale exhibits with per-sentence annotation. Each exhibit's annotation shape (`S1=…; S2=…; closure-type=…`) matches the prose-plan's sentence-role sequence — the plan uses the same vocabulary, so an exhibit IS a model for a plan block.

### Exhibit 1 — reference (illustrative)

> The `connect()` method establishes a connection to the configured endpoint. It returns a `Connection` object on success and raises `ConnectionError` on failure. The method is idempotent: calling it on an already-connected instance returns the existing `Connection` without performing additional handshake work. Authentication is not performed here; call `authenticate()` after `connect()` returns.

<!-- annotation:
S1=opener-signature (names the method, states its purpose in one clause); opener-shape=imperative-declaration
S2=development-return-shape (return value on success, exception on failure; parallel structure)
S3=development-property (idempotence; specific behavior the caller may rely on)
S4=closure-cross-reference (points the reader to the next required call); closure-type=transitional
paragraph-pattern: signature → return-shape → property → cross-reference
handoff-to-next: the next paragraph documents `authenticate()`
source: illustrative; voice-extractor replaces with corpus paragraph at extraction time
-->

### Exhibit 2 — tutorial (illustrative)

TBD — voice-extractor populates from corpus when tutorial samples are present. If the corpus is purely reference or design-rationale, this exhibit stays TBD.

### Exhibit 3 — design-rationale (illustrative)

TBD — voice-extractor populates from corpus when design-rationale samples are present. If the corpus is purely reference or tutorial, this exhibit stays TBD.

Voice-extractor replaces these shipped exhibits with corpus-derived paragraphs when run against an author's samples. The shipped exhibits are illustrative of the shape, not defaults to retain; the extractor's output file carries the author's actual patterns.

## Tone

### Stance

**Rule.** Be exact. Acknowledge limits explicitly (preconditions, edge cases, unsupported inputs). Don't hedge for politeness — either a claim is true or it isn't.

**Exemplars `[reference]`:**
- "Returns null when the input is empty; raises TypeError on non-string input."
- "Caching is disabled by default; set cache=True to enable."

**Exemplars `[design-rationale]`:**
- "We chose B because restart survival is a hard requirement; A's lower latency does not offset the operational cost."
- "Considered a retry-with-backoff loop; rejected because the upstream service returns non-idempotent responses on retry."

**Not:** "One would hope the function behaves reasonably under most conditions." / "It is generally the case that null may perhaps be returned."

### Sentence Structure

**Rule.** One instruction per sentence. Parallel structure for sequences (all imperatives, all declaratives — don't mix). Avoid subordinate clauses that bury the main action. In `design-rationale`, longer sentences are allowed when walking through a tradeoff.

**Exemplars:**
- "Call connect() first. Then call authenticate(). The sequence matters because connection state is established lazily."
- "Invoke the hook on mount; unregister it on unmount."

**Not:** "When you need to connect, which you do before authenticating, and only after having set up the socket state, the handshake proceeds."

### Exploratory vs Verdict Tone

**Rule `[register: reference]`.** Reference documentation reports observed behavior. Frame claims as exact: what the code does, what it returns, what it raises. Exploratory prose is not allowed in reference register.

**Rule `[register: tutorial, design-rationale]`.** Exploratory prose is permitted when reasoning through a tradeoff or anticipating reader confusion. Mark it visibly ("Considered approach A; rejected because..." or "If you're wondering why X, the answer is..."). Don't smuggle exploration into reference-style declaratives.

**Exemplars:**
- Reference: "The function returns the first matching element, or null if no match exists."
- Design rationale: "A linear scan works because the collection is small in practice; a hash index would add setup cost that rarely pays back."

### Thinking Out Loud

**Rule `[register: reference]`.** Omit. Reference documentation does not narrate reasoning.

**Rule `[register: tutorial, design-rationale]`.** Reason through options, but mark it visibly. The reader should be able to tell exposition apart from decision.

**Exemplars:**
- "Considered a retry-with-backoff loop; rejected because the upstream service returns non-idempotent responses on retry."
- "Two designs were evaluated: a pull-based poller and a push-based webhook receiver. The push-based design was chosen because latency requirements ruled out polling intervals above one second."

### Including the Reader

**Rule `[register: tutorial]`.** Use "you" for instructions directed at the reader. The tutorial's frame is teach-the-reader-to-do-this.

**Rule `[register: reference]`.** Avoid "we." Avoid "you" except in error-message templates and parameter descriptions where the caller is the natural subject. Default to passive-of-record where the actor is the system itself: "the function returns," "the cache is invalidated," "the lock is acquired."

**Rule `[register: design-rationale]`.** "We" allowed for team-authored decisions. Avoid second-person; the reader is a peer reviewing the decision, not a learner being instructed.

**Exemplars:**
- Tutorial: "You receive a Context object when the handler fires."
- Reference: "The caller supplies the hash; the function does not compute it."
- Design-rationale: "We chose Postgres because the team already operates it; an SQLite-based design would have lower setup cost but require new operational expertise."

**Not:** "We typically recommend that one first consider the socket state before invoking the handshake." (mixes pronouns and registers)

### Weak Adverbs

**Rule.** Cut "really," "very," "quite," "somewhat," "fairly," "rather," "basically," "actually," "honestly." Ground claims with numbers, units, or comparisons, not vague qualifiers. "This is really quite fast" becomes "This completes in under 5 ms." "The cache is fairly effective" becomes "The cache hits 92% of requests in the benchmark."

### No Preamble

**Rule.** Start with the function signature, the configuration shape, or the decision being documented. Skip "This document describes..." openings entirely. The reader knows what kind of document they're reading.

## Structure

### The Core Rule

**Rule.** Every word fights to stay. If a sentence adds nothing, cut it. If two sentences say the same thing differently, merge them into one shorter sentence. No filler, no padding, no repetition.

**Concision is a means, not an end.** Technical prose tolerates compression better than narrative prose, but stranded verbs and reduced-relative stacking still trip the reader. See `## Cut patterns > compression-stranded-verb` and `## Cut patterns > reduced-relative-stacking`. The cut-bias should fire on filler words, not on the connective tissue that makes a sentence parseable.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence describe observable behavior, or speculate?
- Does this instruction chain parallel prior instructions in the same section?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list.)
- Does it earn its place in the reference or procedure?
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. First drafts are raw material, not output.

### Sentence Connectedness

**Rule.** Instructions chain through parallel verbs and shared subjects. Subordinators ("because," "while," "if") appear sparingly; when they do, they mark causation or precondition precisely. Technical prose favors parallel structure over explicit connectives; repeated sentence shape carries the handoff that connectives carry in academic prose.

**Exemplars:**
- Connected: "Open the file. Read the header. Validate the version field. If validation fails, close the file and raise InvalidFormatError."
- Disconnected (avoid): "The file should be opened. Version validation is important. Errors may be raised."

### Paragraph Flow

**Rule.** Technical paragraphs are often single-purpose: one behavior described, then the next. Flow through proximity, not connectives. Section structure (subheadings, bullets) carries the navigational signal; paragraph openings can be cold within a section.

**Exemplar:**
- Connected: a paragraph describes the happy path; the next paragraph describes error conditions. The connection is structural (parallel under the same subheading), not linguistic.

### Information Pacing

**Rule.** Claim density higher than narrative; complexity per sentence lower. Readers digest facts as a stream.

**Exemplars:**
- Paced: "Instead of one heavy claim with nested caveats, emit four simple claims in sequence."
- Packed (avoid): "The function, which under certain conditions related to buffer state and provided that the caller has not already acquired the lock, may return a partial result that the caller must reassemble."

### Concept Setup

**Rule.** Define every specialized term on first use. No assumptions about domain background. In `tutorial`, the definition can be informal ("a `Promise` is an object that..."); in `reference`, the definition should match the canonical specification.

**Exemplars:**
- Set up: "A promise is an object that represents the future result of an asynchronous operation. Its state is one of: pending, fulfilled, rejected."
- Dropped (avoid): "The promise resolves before the microtask queue drains." ("promise" and "microtask queue" both assume prior knowledge.)

### Building Arguments `[register: design-rationale]`

**Rule.** Technical arguments are usually tradeoff analyses. Frame as: option A (pros, cons), option B (pros, cons), chosen. Address counterpoints by naming them, not by explicitly rebutting. Counterargument-naming is required in design-rationale; absent it, the document reads as advocacy rather than decision.

**Exemplar:**
- "Option A: in-memory cache. Lower latency (sub-millisecond reads), but state is lost on restart. Option B: Redis. Adds one network hop per read, but state survives restart. We chose B because restart survival is a hard requirement."

### Paragraph Length

**Rule.** 2–4 sentences typical. Reference documentation can run shorter (single-sentence paragraphs for function descriptions). Design docs can run longer (5–7 sentences when walking through a tradeoff). Exceed 7 only if every sentence is load-bearing.

### Reduced Structures and Parse Load

**Rule.** Drop "that" sparingly in technical prose. Reference documentation often has long noun-phrase subjects (`the response object the handler returns`); stacking a reduced relative on top forces the reader to backtrack. Limit yourself to one parse-load element per sentence; if the doc-claim needs more, split the sentence. See `## Cut patterns > reduced-relative-stacking`.

## Dimension

### Analogies and Anecdotes

**Rule.** Technical writing uses analogies sparingly. Prefer diagrams, code examples, or precise descriptions. When analogy helps, make it computationally grounded (locks, queues, caches, protocols) — not everyday-object analogies that don't carry the precision the technical claim needs.

**Anchors:** TBD — derived from corpus. Technical-register anchors lean on familiar systems (locks, queues, caches, protocols, common data structures) rather than narrative anchors.

Not every vivid analogy earns its place. Drop it if the connection to your specific claim is loose. A precise description or a code example almost always beats a metaphor.

### Punctuation

**Rule.** Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads, aphoristic closures) are governed by CLAUDE.md §10 *Generation signatures to rewrite*. Use this section only for author-specific punctuation habits the corpus shows beyond the §10-governed patterns.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Author-specific patterns (technical-register baseline):**
- Colons introduce code, examples, or definitions: "The signature is: `connect(host: str, port: int) -> Connection`."
- Semicolons rare. Used to link two independent statements about the same behavior, not for ornamental balance.
- Ellipses avoided (implies incomplete thought, not welcome in reference docs).

### Formatting

**Rule.** Technical writing has more markdown surface than other registers.

- `code` for identifiers (function names, variables, flags, paths).
- ```code blocks``` for runnable examples and multi-line snippets.
- **bold** for warnings and load-bearing notes ("**Note:** this method blocks; do not call from the UI thread").
- *italics* for filenames or technical terms on first use.
- Bullet lists are common for parameter sets, return values, and step sequences.

## Cut patterns

Named failure modes observed in AI-drafted prose that `voice-extractor` and `[editing mode]` Pass 7 explicitly flag. Each pattern carries a canonical ID; `failures_dir` before/after pairs populate author-specific instances at extraction time. Shipped patterns are register-default.

### aphoristic-closure

**Pattern.** Paragraph ends on a rhetorically-balanced pronouncement that substitutes rhetoric for reasoning. Technical signatures: "After all, simplicity is the ultimate goal." / "The right answer is always: it depends." / "Engineering, in the end, is about tradeoffs."

**Why it reads as AI.** Reference documentation should end on a cross-reference or a fact. Design rationale should end on a decision. A profundity-closure trades concrete information for a vague gesture toward universal engineering wisdom.

**Fix.** Restructure to a `transitional` or `synthesis` closure: end on the next behavior, the next section, or the chosen option. Corresponds to canonical §10 ID `aphoristic-closures`.

### compression-stranded-verb

**Pattern.** Verb stripped of its object or qualifier for the sake of concision. Technical signatures: "the cache invalidates" (invalidates what?), "the handler returns" (returns what?), "the function may fail" (fails how?).

**Why it reads as AI.** Technical prose that omits the object or condition fails the precision iron rule. The reader should never have to guess which value, which condition, which mode of failure.

**Fix.** Restore the stranded complement. Be specific: what is invalidated, what is returned, what kind of failure.

### abstract-nominalization-cascade

**Pattern.** Sequence of abstract nouns made from verbs ("the invocation," "the completion," "the resolution") stacked across clauses without a concrete agent.

**Why it reads as AI.** Technical prose's hallmark is concrete subjects + active verbs ("the function returns," "the handler fires," "the cache invalidates"). When the cut-bias stops firing, prose expands into nominalization cascades that read as bureaucratic rather than precise.

**Fix.** Rewrite around a concrete agent and an active verb. "The completion of the invocation triggers..." → "When the call completes, ..."

### reduced-relative-stacking

**Pattern.** Two or three reduced relative clauses (dropped "that") stacked in one sentence, often combined with a long noun-phrase subject.

**Why it reads as AI.** Each reduced relative is individually grammatical; three in one sentence force the reader to backtrack to identify the subject — fatal in reference documentation where misidentification means misuse.

**Fix.** Restore "that" and/or split the sentence. Prefer the explicit "that" when the sentence already carries a long subject or multiple clauses.

### imperative-without-precondition `[register: reference, tutorial]`

**Pattern.** Imperative instruction stated without naming the precondition the reader must satisfy first. Signatures: "Call `flush()` to commit pending writes." (when `flush()` requires the connection to be in `WRITE` state).

**Why it reads as AI.** AI-drafted technical prose tends to state the action without the gating condition, because the gating condition is in another part of the documentation the model didn't traverse. The result reads as confident but is operationally wrong.

**Fix.** Name the precondition: "After `connect()` returns successfully and `authenticate()` has been called, `flush()` commits pending writes." Don't trust the reader to reconstruct the precondition from elsewhere; the rule is name-it-or-don't-write-it.

### speculative-future-behavior `[register: reference]`

**Pattern.** Reference documentation that speculates about future behavior or unsupported scenarios. Signatures: "The handler may return additional fields in future versions." / "Behavior on null input is currently unspecified."

**Why it reads as AI.** Reference documentation should describe what IS, not what MIGHT BE. Speculation invites callers to depend on unsupported guarantees; "currently unspecified" is a license for callers to assume any behavior is acceptable.

**Fix.** Either document the actual behavior on null input (authoritative claim) or omit the case entirely (let it be undefined behavior). For future-behavior speculation, move it to a separate "Stability" or "Roadmap" section where speculation is the genre.

Additional canonical patterns apply in register-specific contexts: `first-person-commitment-in-academic-report` (academic registers only — N/A here), `citation-atomization` (citation-dense registers only — N/A here).

## Iron rules

The rules in this section pass through to every derived voice file verbatim. `voice-extractor` preserves them without corpus calibration; `sourced check` refuses to install a voice file where any is missing.

CLAUDE.md §10 *Generation signatures to rewrite* applies to this voice in full. No item on §10's Never list is softened or downgraded to TBD, regardless of what the writing-samples corpus shows.

When removing a §10 pattern in existing prose, restructure the sentence shape rather than substituting punctuation or reordering tokens; retokenization preserves the rhythm that reads as AI.

## §10 exemptions

Per-voice overrides to CLAUDE.md §10's Never list. An exemption suspends a named rule for this voice's writer prose only; scope and format are defined in CLAUDE.md §10 *Exemptions*. Leave the bullet list empty to inherit §10 in full.

`voice-extractor` does not populate this section; corpus §10-pattern evidence goes into its `### Iron-rule conflicts` report and {{USER}} promotes bullets here by hand.
