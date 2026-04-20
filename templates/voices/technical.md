# Voice rules

Voice calibration tuned to {{USER}}'s technical writing — documentation, API references, procedural guides, technical blog posts. The shipped `technical` voice is a register-specific skeleton: it encodes technical-register defaults for tone (imperative, precise, minimal ornament), structure (one-step-per-sentence, parallel form, bulleted sequences), and dimension (diagrams-not-analogies, precise punctuation, code-block-friendly formatting). Copy to a new name and edit for a different author within the technical register; for a different register (academic, casual, journalistic, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

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

Be exact. Acknowledge limits explicitly (preconditions, edge cases, unsupported inputs). Don't hedge for politeness — either a claim is true or it isn't.

- "Returns null when the input is empty; raises TypeError on non-string input."
- "Caching is disabled by default; set cache=True to enable."

Not: "One would hope the function behaves reasonably under most conditions."
Not: "It is generally the case that null may perhaps be returned."

### Sentence Structure

One instruction per sentence. Parallel structure for sequences (all imperatives, all declaratives — don't mix). Avoid subordinate clauses that bury the main action.

- "Call connect() first. Then call authenticate(). The sequence matters because connection state is established lazily."
- "Invoke the hook on mount; unregister it on unmount."

Not: "When you need to connect, which you do before authenticating, and only after having set up the socket state, the handshake proceeds."

### Exploratory vs Verdict Tone

Technical documentation reports observed behavior. Frame claims as exact: what the code does, what it returns, what it raises. Exploratory prose is rare — reserve it for design rationale or tradeoff discussion, not for reference documentation.

- Reference: "The function returns the first matching element, or null if no match exists."
- Design rationale (exploratory is permitted): "A linear scan works because the collection is small in practice; a hash index would add setup cost that rarely pays back."

### Thinking Out Loud

In reference documentation, omit this entirely. In design docs or tradeoff discussions, you may reason through options, but mark it visibly ("Considered approach A; rejected because...").

- "Considered a retry-with-backoff loop; rejected because the upstream service returns non-idempotent responses on retry."
- "Two designs were evaluated: a pull-based poller and a push-based webhook receiver. The push-based design was chosen because latency requirements ruled out polling intervals above one second."

### Including the Reader

Use "you" for instructions directed at the reader. Avoid "we" in pure reference documentation; it confuses whose code does what.

- "You receive a Context object when the handler fires."
- "The caller supplies the hash; the function does not compute it."

Not: "We typically recommend that one first consider the socket state before invoking the handshake."

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite fast" becomes "This completes in under 5 ms." Ground claims with numbers, units, or comparisons, not vague qualifiers. "The cache is fairly effective" becomes "The cache hits 92% of requests in the benchmark."

### No Preamble

Start with the function signature, not an essay about why the function exists. Skip "This document describes..." openings entirely.

## Structure

### The Core Rule

Every word fights to stay. If a sentence adds nothing, cut it. If two sentences say the same thing differently, merge them into one shorter sentence. No filler, no padding, no repetition.

Writing is sculpting: start with raw material, then chisel. Write a draft, step back, cut, rewrite. Repeat. The first version is never the final version.

**The iteration loop.** After writing a draft, reread every sentence and ask:
- Does this sentence describe observable behavior, or speculate?
- Does this instruction chain parallel prior instructions in the same section?
- Does it sound formulaic or AI-generated? (Cross-check against CLAUDE.md §10's Never list specifically; retokenizing the pattern is not a fix.)
- Does it earn its place in the reference or procedure?
- Does the section flow when read start to finish?

If any answer is no, rewrite or cut. Then reread again. Do not stop after one pass. Keep iterating until a full reread surfaces no issues. Only then present the draft for feedback.

This is not optional polish. This is the process. First drafts are raw material, not output.

### Sentence Connectedness

Instructions chain through parallel verbs and shared subjects. Subordinators appear sparingly; when they do, they mark causation or precondition precisely.

- Connected: "Open the file. Read the header. Validate the version field. If validation fails, close the file and raise InvalidFormatError."
- Disconnected: "The file should be opened. Version validation is important. Errors may be raised."

Technical prose favors parallel structure over explicit connectives; repeated sentence shape carries the handoff that connectives carry in academic prose.

### Paragraph Flow

Technical paragraphs are often single-purpose: one behavior described, then the next. Flow through proximity, not connectives.

- Connected: "A paragraph describes the happy path. The next paragraph describes error conditions. The connection is structural, not linguistic."
- Disconnected: a paragraph on request parsing ends on an unrelated aside; the next paragraph opens on response formatting with no structural signal that a new topic has begun.

### Information Pacing

Technical pacing: claim density higher, complexity per sentence lower. Readers digest facts as a stream.

- Paced: "Instead of one heavy claim with nested caveats, emit four simple claims in sequence."
- Packed: "The function, which under certain conditions related to buffer state and provided that the caller has not already acquired the lock, may return a partial result that the caller must reassemble."

### Concept Setup

Define every specialized term on first use. No assumptions about domain background.

- Set up: "A promise is an object that represents the future result of an asynchronous operation. Its state is one of: pending, fulfilled, rejected."
- Dropped: "The promise resolves before the microtask queue drains." ("promise" and "microtask queue" both assume prior knowledge.)

### Building Arguments

Technical arguments are usually tradeoff analyses. Frame as: option A (pros, cons), option B (pros, cons), chosen. Address counterpoints by naming them, not by explicitly rebutting.

- "Option A: in-memory cache. Lower latency (sub-millisecond reads), but state is lost on restart. Option B: Redis. Adds one network hop per read, but state survives restart. We chose B because restart survival is a hard requirement."

### Paragraph Length

2-4 sentences typical. Reference documentation can run shorter (single-sentence paragraphs for function descriptions). Design docs can run longer (5-7 sentences when walking through a tradeoff). Exceed 7 only if every sentence is load-bearing.

## Dimension

### Analogies and Anecdotes

Technical writing uses analogies sparingly. Prefer diagrams, code examples, or precise descriptions. When analogy helps, make it computationally grounded (locks, queues, caches, protocols).

**Anchors:** TBD — derived from corpus. Technical-register analogies often lean on familiar systems (locks, queues, caches, protocols) rather than everyday objects.

Not every vivid analogy earns its place. Drop it if the connection to your specific claim is loose. A precise description or a code example almost always beats a metaphor.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. Use this section only for author-specific punctuation habits the corpus clearly shows (semicolon style, ellipsis use, colon introducing evidence, etc.). Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly ("this author uses em-dashes for appositives"); silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

Technical prose uses more colons (introducing code, examples, definitions). Semicolons rare. Ellipses avoided (implies incomplete thought, not welcome in reference docs).

### Formatting

Technical writing has more markdown surface than other registers. Use `code` for identifiers (function names, variables, flags, paths). Use ```code blocks``` for runnable examples and multi-line snippets. Use **bold** for warnings and load-bearing notes. Use *italics* for filenames or technical terms on first use. Bullet lists are common for parameter sets, return values, and step sequences.
