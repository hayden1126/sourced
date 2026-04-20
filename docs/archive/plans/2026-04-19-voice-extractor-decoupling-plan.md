# Voice-Extractor Decoupling Implementation Plan

> **Status: Shipped 2026-04-19 via PR #7.** This document is historical — all tasks completed. See `docs/archive/specs/2026-04-19-voice-extractor-decoupling-design.md` for the design.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decouple `voice-extractor`'s skeleton from the academic register; ship 6 register-specific skeletons reorganized into 4 orthogonal axes (Iron / Tone / Structure / Dimension); auto-route skeleton selection by classifier confidence.

**Architecture:** Replace the single `templates/voices/academic.md` (which doubles as shipped voice AND default skeleton, leaking academic framing into every derived voice) with a family of 6 skeletons: `academic.md`, `casual.md`, `technical.md`, `journalistic.md`, `narrative.md`, `hybrid.md`. Each uses identical section structure under 4 top-level headers. `voice-extractor.md` updates to route by classifier output (≥85% single register → that skeleton; <85% → `hybrid.md`). No new halt categories; `mixed-register` replaces halt-behavior with auto-route-to-hybrid.

**Tech Stack:** Markdown (voice skeletons, subagent definition, docs), bash (install.sh reserved-name list).

**Spec:** `docs/archive/specs/2026-04-19-voice-extractor-decoupling-design.md` (commit `2e72b4e`). When this plan references "spec §N", it means that file's section N.

---

## File Structure

### New files

- `templates/voices/casual.md` — casual register skeleton
- `templates/voices/technical.md` — technical register skeleton
- `templates/voices/journalistic.md` — journalistic register skeleton
- `templates/voices/narrative.md` — narrative register skeleton
- `templates/voices/hybrid.md` — register-neutral fallback skeleton (lean, anti-bias prose)

### Modified files

- `templates/voices/academic.md` — reorganize into 4-axis structure; prose stays academic-register-specific but re-parented under `## Iron rules / ## Tone / ## Structure / ## Dimension` headers
- `agents/voice-extractor.md` — expand `register` enum, remove `skeleton_path` hardcoded default, change `mixed` behavior from halt to auto-route-to-hybrid, expand shipped-name reserved list, add `### Register drift` report section, expand classifier signal set
- `install.sh` — no logic changes; the existing voice-library copy loop already globs `templates/voices/*.md`. BUT if the subagent reserved-name check lives in shell, update that list.
- `docs/VOICES.md` — document the 6 skeletons, 4-axis section structure, routing behavior, hybrid.md's lean contract
- `ARCHITECTURE.md` — voice-system section gains a paragraph on skeleton-per-register + 4 axes
- `README.md` — update voice-preservation bullet if needed to mention 6-skeleton calibration

### Unchanged

- CLAUDE.md §9 (voice) and §10 (generation signatures) — the voice system's consumer side is unchanged; modes still read one `voice.md` per project. The rules in §10 already transclude into every skeleton via the iron-rules section.
- `install.sh` iron-rule and §10-exemption validation logic — still runs on every voice file regardless of skeleton origin.

---

## Task breakdown

7 tasks. Tasks 1-6 build the new skeletons; Task 7 updates voice-extractor; Task 8 does install.sh + docs; Task 9 runs smoke verification.

---

### Task 1: Reorganize academic.md into 4-axis structure

No content rewrite — this task ONLY re-parents existing sections under the new top-level headers. It's a pure reorganization commit; voice-extractor's output against this refactored file should be byte-identical to its output against the pre-refactor file (modulo section ordering).

**Files:**
- Modify: `templates/voices/academic.md`

- [ ] **Step 1: Read current academic.md**

```bash
cat /home/hayden/sourced/templates/voices/academic.md
```

Note the current section order: `# Voice rules` → intro paragraph → `## Iron rules` → `## The Core Rule` → `## Stance: Direct but Humble` → `## Sentence Structure` → `## Sentence Connectedness` → `## Paragraph Flow` → `## Information Pacing` → `## Concept Setup` → `## Exploratory vs Verdict Tone` → `## Thinking Out Loud` → `## Building Arguments` → `## Analogies and Anecdotes` → `## Including the Reader` → `## Brevity Rules` → `## Punctuation` → `## §10 exemptions` → `## No Preamble` → `## Formatting`.

- [ ] **Step 2: Rewrite academic.md with new 4-axis structure**

Use the Write tool to replace the file. The new structure:

```markdown
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

**Anchors I often use:**
- Measurement distortion: Clever Hans, the horse reading subtle cues
- Implicit learning: chicken sexing, experts can't explain how
- Coordination without control: split-brain experiments

Not every vivid analogy earns its place. Drop it if the connection to your specific claim is loose ("this reminds me of..."). Cut back an analogy you find yourself extending across multiple paragraphs to keep it working: it should illuminate one point, not run the argument.

### Punctuation

Punctuation patterns that function as AI generation signatures (em dashes, "not X but Y" pivots, ornamental triads) are governed by CLAUDE.md §10 *Generation signatures to rewrite*, which applies across every voice. Use this section only for author-specific punctuation habits the corpus clearly shows (semicolon style, ellipsis use, colon introducing evidence, etc.). Leave TBD rather than inventing a rule the corpus does not settle. An author-specific rule that contradicts §10 must be stated explicitly ("this author uses em-dashes for appositives"); silence defers to §10.

Direct quotations follow CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* (source punctuation preserved verbatim). This section governs the writer's own prose.

**Ellipses** for trailing thoughts: "And if you just... change it slightly, the whole thing breaks."

### Formatting

**Bold** for emphasis (not caps). *Italics* for technical terms. Bullet points sparingly.
```

Note the section splits:
- `## Brevity Rules` splits into `### Weak Adverbs` (under Tone) + `### Paragraph Length` (under Structure)
- `## §10 exemptions` nests as `### §10 exemptions` under `## Iron rules`

- [ ] **Step 3: Verify section structure**

Run:
```bash
cd /home/hayden/sourced && grep -n '^## ' templates/voices/academic.md
```

Expected output exactly:
```
## Iron rules
## Tone
## Structure
## Dimension
```

And:
```bash
grep -n '^### ' templates/voices/academic.md
```

Expected (order-dependent):
```
### §10 exemptions
### Stance
### Sentence Structure
### Exploratory vs Verdict Tone
### Thinking Out Loud
### Including the Reader
### Weak Adverbs
### No Preamble
### The Core Rule
### Sentence Connectedness
### Paragraph Flow
### Information Pacing
### Concept Setup
### Building Arguments
### Paragraph Length
### Analogies and Anecdotes
### Punctuation
### Formatting
```

If the section counts or nesting don't match, fix before committing.

- [ ] **Step 4: Verify content preservation**

Run:
```bash
grep -c 'Clever Hans\|chicken sexing\|split-brain\|Spotted Elk\|ExAhestOtse\|Sacred Hat' templates/voices/academic.md
```

Expected: 6 (one match per anchor name / illustration; each should still be present in the reorganized file).

Also:
```bash
wc -l templates/voices/academic.md
```

Expected: 100-160 lines (was ~149). Significant deviation either direction (above 200 or below 80) indicates accidental loss or bloat.

- [ ] **Step 5: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/academic.md
git commit -m "Reorganize academic.md into 4-axis structure (Iron/Tone/Structure/Dimension)"
```

---

### Task 2: Author casual.md skeleton

**Files:**
- Create: `templates/voices/casual.md`

- [ ] **Step 1: Read academic.md as the structural template**

```bash
cat /home/hayden/sourced/templates/voices/academic.md
```

Note the section order post-reorg: Iron rules (with §10 exemptions nested) / Tone / Structure / Dimension.

- [ ] **Step 2: Write casual.md**

Use the Write tool. Preserve the exact 4-axis + section structure from academic.md. Preserve `## Iron rules` and `### §10 exemptions` VERBATIM (transclusion identity matters — install.sh validates iron rules across skeletons). Rewrite every non-iron section's prose for the casual register. Example passages to adapt (conversational, contraction-heavy, short-sentence baseline):

```markdown
# Voice rules

Voice calibration tuned to {{USER}}'s casual writing — blog posts, personal essays, conversational pieces. The shipped `casual` voice is a register-specific skeleton: it encodes conversational-register defaults for tone (first-person ease, contractions, short sentences), structure (explicit connectives, short argument arcs), and dimension (analogies close to experience, inline punctuation, light formatting). Copy to a new name and edit for a different author within the casual register; for a different register (academic, technical, journalistic, narrative) start from the matching shipped skeleton instead. Applies in `[outlining mode]` (Paragraph Flow at outline time), `[writing mode]` (all rules, strictly), and `[editing mode]` (voice audit).

Read this file in full on entry to any of those modes; do not work from memory of prior sessions. The rules are load-bearing for the project's voice-preservation promise.

## Iron rules

[VERBATIM from academic.md — including the CLAUDE.md §10 paragraph + "restructure don't retokenize" paragraph + ### §10 exemptions nested subsection. Copy-paste; do not edit.]

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

- "Wait, does this actually matter? I think it does — but only if you're optimizing for X."
- "So what does this tell us? Maybe nothing. Or maybe it's the whole point."

### Including the Reader

"You" and "we" both work. Pick based on feel. "You" is direct; "we" is collaborative. Don't lecture.

- "You end up choosing between two bad options."
- "We've all been here before."

Not: "The reader must understand..."

### Weak Adverbs

Cut weak adverbs: "really", "very", "quite", "somewhat", "fairly", "rather", "basically", "actually", "honestly". "This is really quite important" becomes "This is important." Casual prose allows "kind of" / "sort of" as authentic hedges when they carry actual meaning — "I sort of agree" can be genuine ambivalence. Cut them when they stack or dilute. "This is sort of basically actually a problem" is not casual, it's bad.

### No Preamble

Same as academic — skip "That's a great point!" openings. Start with the substance.

## Structure

### The Core Rule

Casual prose doesn't mean sloppy. Every sentence earns its place; if it doesn't add something the reader couldn't guess, cut it. The iteration loop applies here too: draft, reread, cut, rewrite.

Casual writing usually has a lower ceiling for length than academic — aim to be shorter than you think. Blog posts and personal essays that run long lose their conversational energy.

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

Heavy points get their own paragraphs. Light points cluster. Don't load every sentence — let some just breathe.

- Paced: "The demo crashed on stage. Everyone laughed politely. Then we spent three weeks rebuilding."
- Packed: claim + evidence + caveat + pivot all in one sentence, every sentence.

### Concept Setup

Define terms inline but lightly — a parenthetical or a "basically, it's X" aside. Don't formally introduce every specialized word; casual readers can handle inference better than textbook readers.

- Set up: "Chicken sexing — the practice of telling male and female chicks apart, which expert sexers can do reliably but can't explain how — is the classic example."
- Dropped: "The phenomenon exhibits characteristics consistent with implicit learning." (no setup; assumes the reader already knows the term)

### Building Arguments

Walk through the reasoning but feel free to skip steps the reader will fill in. Counterpoints appear as "yeah, but" moments, not formal objections.

- "I know, I know — you could just use X. But X has its own problems."

### Paragraph Length

2 to 4 sentences per paragraph is the casual baseline. One-sentence paragraphs are allowed for emphasis. Avoid paragraphs longer than 5 sentences — the conversational energy dies.

## Dimension

### Analogies and Anecdotes

Anecdotes from personal experience anchor casual writing. Specific, small-scale, concrete. The reader should be able to picture the scene.

**Anchors I often use:**
- TBD — derived from corpus

Analogies closer to everyday objects than to technical concepts. Cut any that require domain knowledge to land.

### Punctuation

Ellipses for trailing thoughts and drift. Em dashes — oh wait, forbidden — use commas or period-then-fragment instead. Parentheticals (like this) are welcome but don't stack.

Casual prose uses more semicolons than formal prose suggests, but still sparingly. Colons introduce lists or announce a payoff.

### Formatting

Minimal. **Bold** for genuine emphasis, not caps. *Italics* for a word you're using self-consciously. Bullet lists only when the content really is a list; flowing prose otherwise.
```

Continue with the `## Structure` and `## Dimension` sections following this register-shift pattern. The key is: every non-iron section's prose is rewritten to describe the rule in casual register terms, with casual-register exemplars. Preserve subsection headings from academic.md (so the section-count grep in Step 4 matches).

- [ ] **Step 3: Verify iron rules section is byte-identical to academic.md**

```bash
cd /home/hayden/sourced
diff <(awk '/^## Iron rules/{flag=1;next} /^## Tone/{flag=0} flag' templates/voices/academic.md) \
     <(awk '/^## Iron rules/{flag=1;next} /^## Tone/{flag=0} flag' templates/voices/casual.md)
```

Expected: no output (iron rules section is identical across both files).

If diff shows content: fix casual.md to match academic.md's iron rules section exactly. `install.sh` validates this at install time and will refuse to install a voice file where iron rules differ.

- [ ] **Step 4: Verify section count matches academic.md**

```bash
cd /home/hayden/sourced
diff <(grep '^## ' templates/voices/academic.md) <(grep '^## ' templates/voices/casual.md)
diff <(grep '^### ' templates/voices/academic.md) <(grep '^### ' templates/voices/casual.md)
```

Expected: no output. Section structure is identical; only prose differs.

Note: subsection NAMES may differ intentionally when register semantics differ (academic's "Weak Adverbs" vs. casual's "Weak Qualifiers"). If the diff flags these differences, review: it's OK as long as each skeleton uses meaningful register-calibrated names for the same rule-axis slot.

Actually — **revision**: keep subsection names identical across skeletons so voice-extractor's section-matching logic is trivial. Rename casual.md's `### Weak Qualifiers` to `### Weak Adverbs`. The content can still be casual-specific; the header stays.

- [ ] **Step 5: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/casual.md
git commit -m "Add casual register skeleton"
```

---

### Task 3: Author technical.md skeleton

Same procedure as Task 2, register-shifted for technical writing (documentation, procedural, API references). Key register markers:

- Imperative voice ("Call this function with..." not "One calls this function with...")
- Minimal ornament; precise domain terminology
- One instruction per sentence
- Parallel structure
- Bulleted sequences common
- Definitions up front for terms; no inline "basically it's X"

**Files:**
- Create: `templates/voices/technical.md`

- [ ] **Step 1: Copy academic.md as starting point**

```bash
cd /home/hayden/sourced
cp templates/voices/academic.md templates/voices/technical.md
```

- [ ] **Step 2: Rewrite non-iron sections for technical register**

Use Edit tool on `templates/voices/technical.md`. Preserve `## Iron rules` section verbatim. For each non-iron section, replace academic prose with technical-register prose. Key rewrites:

- **Intro paragraph** (replaces "Voice calibration tuned to {{USER}}'s academic writing..."):
  `Voice calibration tuned to {{USER}}'s technical writing — documentation, API references, procedural guides, technical blog posts. The shipped `technical` voice is a register-specific skeleton: it encodes technical-register defaults for tone (imperative, precise, minimal ornament), structure (one-step-per-sentence, parallel form, bulleted sequences), and dimension (diagrams-not-analogies, precise punctuation, code-block-friendly formatting). Copy to a new name and edit for a different author within the technical register; for a different register (academic, casual, journalistic, narrative) start from the matching shipped skeleton instead.`

- **### Stance**: Content: "Be exact. Acknowledge limits explicitly (preconditions, edge cases, unsupported inputs). Don't hedge for politeness — either a claim is true or it isn't."
  Exemplars: `"Returns null when the input is empty; raises TypeError on non-string input." / "Caching is disabled by default; set cache=True to enable."`
  Not: `"One would hope the function behaves reasonably..."`

- **### Sentence Structure**: "One instruction per sentence. Parallel structure for sequences (all imperatives, all declaratives — don't mix). Avoid subordinate clauses that bury the main action."
  Exemplars: `"Call connect() first. Then call authenticate(). The sequence matters because connection state is established lazily." / "Invoke the hook on mount; unregister it on unmount."`
  Not: `"When you need to connect, which you do before authenticating, and only after having set up the socket state..."`

- **### Exploratory vs Verdict Tone** → technical prose is verdict-heavy by nature. Keep the section but rewrite: "Technical documentation reports observed behavior. Frame claims as exact: what the code does, what it returns, what it raises. Exploratory prose is rare — reserve it for design rationale or tradeoff discussion, not for reference documentation."

- **### Thinking Out Loud** — mostly absent from technical writing. Rewrite: "In reference documentation, omit this entirely. In design docs or tradeoff discussions, you may reason through options, but mark it visibly ('Considered approach A; rejected because...')."

- **### Including the Reader**: "Use 'you' for instructions directed at the reader. Avoid 'we' in pure reference documentation; it confuses whose code does what."
  Exemplars: `"You receive a Context object when the handler fires." / "The caller supplies the hash; the function does not compute it."`
  Not: `"We typically recommend that one first consider..."`

- **### Weak Adverbs**: Keep (same rule applies across registers). Rewrite exemplars to technical domain.

- **### No Preamble**: Same rule; technical writing version is especially strict. "Start with the function signature, not an essay about why the function exists."

- **### The Core Rule** (under Structure): The iteration loop stays. Rewrite exemplars to technical context: "Does this sentence describe observable behavior, or speculate? / Does this instruction chain parallel prior instructions in the same section?"

- **### Sentence Connectedness**: Technical sentences connect less through explicit connectives and more through parallel structure. "Instructions chain through parallel verbs and shared subjects. Subordinators appear sparingly; when they do, they mark causation or precondition precisely."
  Exemplars: `"Open the file. Read the header. Validate the version field. If validation fails, close the file and raise InvalidFormatError."`

- **### Paragraph Flow**: Technical paragraphs are often single-purpose: one behavior described, then the next. Flow through proximity, not connectives.
  Exemplars: `"A paragraph describes the happy path. The next paragraph describes error conditions. The connection is structural, not linguistic."`

- **### Information Pacing**: Technical pacing differs — claim density is higher (every sentence says a specific fact), but complexity per sentence is lower. Readers digest facts as a stream.
  Exemplars: `"Instead of one heavy claim with nested caveats, emit four simple claims in sequence."`

- **### Concept Setup**: Define every specialized term on first use. No assumptions about domain background.
  Exemplars: `"A promise is an object that represents the future result of an asynchronous operation. Its state is one of: pending, fulfilled, rejected."`

- **### Building Arguments**: Technical arguments are usually tradeoff analyses. Frame as: option A (pros, cons), option B (pros, cons), chosen. Address counterpoints by naming them, not by explicitly rebutting.

- **### Paragraph Length**: "2-4 sentences typical. Reference documentation can run shorter (single-sentence paragraphs for function descriptions). Design docs can run longer (5-7 sentences when walking through a tradeoff). Exceed 7 only if every sentence is load-bearing."

- **### Analogies and Anecdotes**: Technical writing uses analogies sparingly. Prefer diagrams, code examples, or precise descriptions. When analogy helps, make it computationally grounded. Replace academic's "Clever Hans / chicken sexing / split-brain" anchor block with: `TBD — derived from corpus. Technical-register analogies often lean on familiar systems (locks, queues, caches, protocols) rather than everyday objects.`

- **### Punctuation**: Technical prose uses more colons (introducing code, examples, definitions). Semicolons rare. Ellipses avoided (implies incomplete thought, not welcome in reference docs).

- **### Formatting**: Technical writing has more markdown surface: `code` for identifiers, ```code blocks``` for examples, `**bold**` for warnings/important, `*italics*` for filenames or technical terms on first use.

- [ ] **Step 3: Verify iron rules + section structure identical to academic.md**

Same grep / diff commands as Task 2 Step 3-4.

- [ ] **Step 4: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/technical.md
git commit -m "Add technical register skeleton"
```

---

### Task 4: Author journalistic.md skeleton

**Files:**
- Create: `templates/voices/journalistic.md`

- [ ] **Step 1: Copy academic.md as starting point**

```bash
cd /home/hayden/sourced
cp templates/voices/academic.md templates/voices/journalistic.md
```

- [ ] **Step 2: Rewrite non-iron sections for journalistic register**

Journalistic register markers:
- Mid-register formal (between casual and academic)
- Active voice; concrete subjects
- Inverted pyramid: lede first, detail after, nuance last
- News-peg argumentation: every claim earns its place by connecting to the story
- Attribution explicit: "according to X" / "X said" rather than "it is believed that"

Key rewrites (use Edit tool):

- **Intro**: `Voice calibration tuned to {{USER}}'s journalistic writing — news stories, feature pieces, commentary, reported essays. The shipped `journalistic` voice is a register-specific skeleton: it encodes journalistic-register defaults for tone (lede-first, active voice, attributed), structure (inverted pyramid, news-peg argumentation), and dimension (illustrative anecdotes, plain punctuation, formatting light). Copy to a new name and edit for a different author within the journalistic register...`

- **### Stance**: Content: "Claims carry attribution. 'According to X, Y' rather than 'Y is true.' In commentary, state the view once, plainly; don't hedge repeatedly."
  Exemplars: `"Federal officials said the program would launch in June. / Critics argued the timeline was unrealistic."`

- **### Sentence Structure**: "Subject-verb-object, active voice. Keep subjects concrete: people, organizations, actions — not abstractions. Subordinate clauses allowed when they add context, not when they defer the main point."
  Exemplars: `"The mayor announced the plan Monday. / Officials declined to name the source, citing ongoing negotiations."`
  Not: `"It was announced by the office of the mayor..."`

- **### Exploratory vs Verdict Tone**: Journalistic prose is fact-forward; verdicts appear only in commentary/opinion. "Reporting states what is known and attributes it. Opinion pieces can take a stance but must make it visible as a stance, not smuggle it in as fact."

- **### Thinking Out Loud**: Rare in reporting. Common in columns/commentary. "In commentary, walk the reader through your reasoning but keep it tight — journalistic prose doesn't indulge the mental wandering that academic or casual prose permits."

- **### Including the Reader**: Third person dominates in reporting. First-person reserved for reported essays and columns.
  Exemplars: `"Readers may wonder whether... / The central question is whether..."`

- **### Weak Adverbs**: Same rule. Journalistic prose prizes concrete detail; weak adverbs feel especially out of place.

- **### No Preamble**: "Start with the lede. Skip throat-clearing entirely — no 'Recent events have prompted...' or 'This week saw...'"

- **### The Core Rule** (Structure): "Every paragraph earns its place in the story. If a paragraph doesn't advance the reader's understanding of the news peg, cut it. Reporting has a tight word budget; feature pieces slightly looser; columns tightest of all."

- **### Sentence Connectedness**: "Sentences connect through shared subjects and chronological progression. Formal connectives ('because,' 'however') appear at key pivots, not between every sentence."

- **### Paragraph Flow**: "Inverted pyramid. Most important fact first paragraph. Second-most-important second. And so on. Feature pieces relax this but still lead with the hook."
  Exemplars: `"First paragraph names the who/what/when. Second paragraph adds context: why it matters. Third paragraph introduces the tension or conflict."`

- **### Information Pacing**: "Facts and attribution alternate. Claim → attribution → claim → attribution. Heavy packing of facts without attribution reads as editorial."

- **### Concept Setup**: "Define unfamiliar terms parenthetically, quickly. Readers won't tolerate a pause for a three-sentence definition."
  Exemplars: `"The agency uses reverse-repurchase agreements (overnight loans collateralized by Treasury securities) to manage short-term rates."`

- **### Building Arguments** (in commentary): "Name your claim, support it with reporting, anticipate the obvious counterargument briefly, move on."

- **### Paragraph Length**: "1-3 sentences is the baseline for reporting. 2-4 for features. 3-5 for columns. Single-sentence paragraphs are common at pivot points."

- **### Analogies and Anecdotes**: "Anecdotes anchor human stories. One-paragraph vignettes: a named person, a specific moment, a quoted line. Analogies from everyday experience; not domain-technical."
  Anchor block: `TBD — derived from corpus. Journalistic-register anecdotes often feature named subjects, specific scenes, and direct quotes.`

- **### Punctuation**: "Em dashes — oh wait, forbidden — use commas. Semicolons rare. Colons introduce attribution or lists. Quotation marks for direct speech, always attributed."

- **### Formatting**: "Sparingly. **Bold** for pull quotes in some publications. *Italics* for publication titles, ship names, legal case names. Bullets only when the content is genuinely list-shaped."

- [ ] **Step 3: Verify iron rules + structure identical**

Same grep / diff commands.

- [ ] **Step 4: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/journalistic.md
git commit -m "Add journalistic register skeleton"
```

---

### Task 5: Author narrative.md skeleton

**Files:**
- Create: `templates/voices/narrative.md`

- [ ] **Step 1: Copy academic.md as starting point**

```bash
cd /home/hayden/sourced
cp templates/voices/academic.md templates/voices/narrative.md
```

- [ ] **Step 2: Rewrite non-iron sections for narrative register**

Narrative register markers (per Biber student-writing MDA):
- First-person perspective; first-person pronouns frequent
- Past-tense heavy (recounting) with present-tense for reflection
- Scene-aware rhythm: sensory detail, dialogue, specific moments
- Reflection-forward: the "what did I learn" is the point
- Chronological OR thematic arc, not argumentative-linear

Key rewrites:

- **Intro**: `Voice calibration tuned to {{USER}}'s narrative writing — personal essays, reflection pieces, college application essays, memoir-adjacent work. The shipped `narrative` voice is a register-specific skeleton: it encodes narrative-register defaults for tone (first-person, scene-aware, reflective), structure (chronological or thematic arcs, scene → reflection alternation), and dimension (specific sensory detail, deliberate punctuation for rhythm, minimal formatting). Copy to a new name and edit for a different author within the narrative register...`

- **### Stance**: Content: "Claims are often provisional, grounded in experience. 'I thought' / 'I realized' / 'it turned out' rather than 'research shows' or 'I argue.' First-person is the baseline, not a stylistic choice."
  Exemplars: `"I didn't understand, at first, why it mattered. / Looking back, I was asking the wrong question."`

- **### Sentence Structure**: "Varies with scene vs. reflection. Scene sentences are tight, concrete, often sensory. Reflection sentences are longer, more abstract, often questioning."
  Exemplars (scene): `"The room smelled like burnt coffee. She didn't look up when I walked in."`
  Exemplars (reflection): `"Something about that afternoon stayed with me — not the conversation itself, but the way the light fell across the desk while she talked."`

- **### Exploratory vs Verdict Tone**: "Narrative prose lives in exploration. Verdicts are rare and reserved for rhetorical impact. Most of the writing earns its authority through specificity, not conclusion."

- **### Thinking Out Loud**: "This IS narrative writing — the thinking-out-loud quality is the form. Ask questions, answer them, reverse yourself, reconsider. The reader follows your mind in motion."
  Exemplars: `"At the time, I thought it was about control. Maybe it was. Or maybe — and this is harder to admit — it was about being afraid."`

- **### Including the Reader**: "Second-person ('you') appears but is usually the universal-you, not direct address. First-person dominates. 'We' appears rarely, usually as a moment of solidarity."

- **### Weak Adverbs**: Same rule. In narrative, concrete sensory detail replaces hedged qualification.

- **### No Preamble**: "Start in scene or with a question. Skip 'I want to tell you about...' or 'Recently I've been thinking about...'"
  Exemplars: `"I was seventeen the first time I understood that grown-ups lie." / "There's a particular kind of silence in a parked car."`

- **### The Core Rule** (Structure): "Every paragraph either advances the story or earns the reflection. Scene without reflection is a transcript; reflection without scene is an essay. Both feel untethered. Alternate."

- **### Sentence Connectedness**: "Sentences connect through time ('then,' 'later,' 'that afternoon'), through parallel sensory detail ('I heard... I saw... I remember...'), or through reflective pivots ('but what I didn't know was...'). Avoid chains of declaratives that read as enumeration."

- **### Paragraph Flow**: "Paragraphs move between scene and reflection. A scene paragraph may end on a sensory detail or a line of dialogue; the next paragraph steps back to interpret, then returns to scene."
  Exemplars: `"A scene paragraph ends 'She closed the door without answering.' The next opens: 'For years afterward, I tried to figure out what that silence meant.'"`

- **### Information Pacing**: "Scene is dense with detail; reflection is sparse. The rhythm alternates — pack the scene, breathe in the reflection, return to scene."

- **### Concept Setup**: "Narrative concepts set up through scene, not definition. Instead of defining a term, show it happening."

- **### Building Arguments**: "Narrative writing builds arguments indirectly. Specific scenes accumulate into an argument the reader constructs themselves. Direct assertion is rare and weighty when it appears."

- **### Paragraph Length**: "Varies widely. Scene paragraphs can be long (6-8 sentences of cumulative detail) or short (single-sentence impact). Reflection paragraphs 3-5 sentences. Avoid uniformity — variation IS the rhythm."

- **### Analogies and Anecdotes**: "The whole piece IS anecdote, essentially. Within the larger narrative, smaller anecdotes can nest (a remembered moment, a friend's story) to illuminate the main arc."
  Anchor block: `TBD — derived from corpus. Narrative-register anchors often include recurring images, named people, specific settings that surface across multiple samples.`

- **### Punctuation**: "Ellipses for trailing thoughts and drift. Em dashes forbidden — use commas, colons, or period-fragment instead. Semicolons to link reflection-clauses. Direct speech with quotation marks, attributed minimally ('she said,' 'I replied')."

- **### Formatting**: "Minimal. Italics for emphasis of a single word (often a remembered phrase). Bold rare. Bullet points usually break the mood — avoid unless the list is a genuine list (ingredients, steps, etc.)."

- [ ] **Step 3: Verify iron rules + structure identical**

Same grep / diff commands.

- [ ] **Step 4: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/narrative.md
git commit -m "Add narrative register skeleton"
```

---

### Task 6: Author hybrid.md skeleton (lean, anti-bias)

**Files:**
- Create: `templates/voices/hybrid.md`

This is the load-bearing skeleton for blended / mixed corpora. Its non-iron prose deliberately does NOT anchor to any register; instead, it states the rule in register-neutral terms and directs voice-extractor to derive from corpus evidence.

- [ ] **Step 1: Copy academic.md as starting point**

```bash
cd /home/hayden/sourced
cp templates/voices/academic.md templates/voices/hybrid.md
```

- [ ] **Step 2: Rewrite every non-iron section with anti-bias prose**

Each non-iron section in hybrid.md follows this pattern:

1. State the underlying rule (what connects to what, what comes first, etc.)
2. Describe the degrees of freedom (what varies across registers)
3. Explicit anti-bias instruction for voice-extractor
4. TBD fallback for thin-coverage sections

Full rewrites (use Edit tool):

- **Intro paragraph**:
  `Voice calibration for blended-register corpora. The shipped `hybrid` voice is a register-neutral skeleton: it encodes the UNDERLYING rules (connectedness, pacing, concept setup, iron prohibitions) without committing to a register's specific framing. Use as the base skeleton when the writing-samples corpus spans registers (e.g., school essays that are structurally academic but tonally casual; blog posts that mix reflective and journalistic patterns). voice-extractor selects hybrid.md automatically when the classifier finds no single register above 85% of the corpus.`

  `For a register-specific calibration (academic papers, casual blog posts, technical documentation, journalistic pieces, narrative reflection), start from the matching shipped skeleton instead.`

- **### Stance**: "State views clearly. How hedged vs. how direct varies by register — academic prose hedges more, technical prose is direct, narrative prose reflective. voice-extractor: set the stance calibration from corpus evidence. Do NOT default to a specific register's hedging level."
  Exemplars: `TBD — derived from corpus.`

- **### Sentence Structure**: "Sentences vary in length and shape across registers. Academic prose defaults long; casual short; technical imperative; narrative scene-aware; journalistic inverted. voice-extractor: set the baseline sentence-length rhythm from corpus evidence. Reserve short/punchy forms for emphasis at pivots regardless of baseline."

- **### Exploratory vs Verdict Tone**: "Exploration dominates in narrative and academic reflection; verdict dominates in reporting and technical reference. voice-extractor: identify where the corpus falls on this axis and calibrate. Do not default to any register's balance."

- **### Thinking Out Loud**: "Present in narrative and casual prose; rare in reporting and reference documentation. voice-extractor: if the corpus shows this pattern, calibrate exemplars; if absent, emit TBD rather than adding it."

- **### Including the Reader**: "First-person, second-person, third-person each dominate in different registers. voice-extractor: identify which pronoun-perspective the corpus uses and set as the baseline."

- **### Weak Adverbs**: Keep same rule (register-invariant). Same exemplars.

- **### No Preamble**: Keep same rule.

- **### The Core Rule** (Structure): Keep the iteration loop verbatim — it's register-invariant ("every word fights to stay"). May adjust the register-specific examples in the iteration questions.

- **### Sentence Connectedness**:
  `Sentences hand off. Each connects to the previous through a causal, contrastive, or sequencing relationship (explicit connectives, parallel structure, or implicit logical flow). How the connection is MARKED varies — explicit connectives, semicolons, short-sentence juxtaposition, restatement. The baseline rhythm varies too — some writers chain short, some build long.`

  `voice-extractor: set the marker style AND baseline rhythm from corpus evidence. Do NOT default to "longer connected sentences" or any register-specific shape; extract what the corpus shows. If the corpus is thin on this section, TBD rather than impose a register-specific pattern.`

- **### Paragraph Flow**:
  `Paragraphs set up, develop, and hand off. End a paragraph on a transition to the next paragraph's topic, not on a verdict that closes the door. Open the next paragraph with a connective, a reference back, or a concept the prior paragraph positioned.`

  `How the handoff is MARKED varies by register: academic uses explicit connectives ('While,' 'Moreover'); casual uses shorter bridges; narrative uses sensory callbacks; journalistic uses inverted-pyramid ordering.`

  `voice-extractor: set the handoff style from corpus evidence. TBD if unclear.`

- **### Information Pacing**:
  `Claim density varies by register. Academic prose can pack multiple claims per paragraph; technical prose emits one claim per sentence; narrative prose alternates heavy and light. voice-extractor: identify the pacing pattern the corpus shows and calibrate. Interleave elaboration sentences appropriately for the identified register.`

- **### Concept Setup**:
  `Introduce specialized terms or domain references with appropriate framing on first use. The DEGREE of setup varies — academic prose can run longer definitions; casual prose uses parentheticals; technical prose uses formal definition blocks; narrative prose uses scene. voice-extractor: set the setup convention from corpus evidence.`

- **### Building Arguments**:
  `Develop reasoning. Address counterpoints. How formally — full objection-response vs. casual "yeah, but" — varies by register. voice-extractor: set the argumentation style from corpus evidence.`

- **### Paragraph Length**:
  `Paragraph length varies dramatically by register. Journalistic: 1-3 sentences. Casual: 2-4. Academic: 3-5. Narrative: highly variable. voice-extractor: measure the corpus's paragraph-length distribution and set the baseline accordingly.`

- **### Analogies and Anecdotes**:
  `Connect abstract points to specific patterns. The TYPE of analogy varies — academic uses technical illustrations; casual uses everyday objects; technical uses system analogies; journalistic uses anecdotes about named people; narrative is itself anecdote.`
  
  `**Anchors:**`
  `TBD — derived from corpus.`

- **### Punctuation**:
  `Author-specific punctuation habits. Ellipses, semicolons, colons, dashes all vary. voice-extractor: identify what the corpus uses characteristically and describe the pattern.`

- **### Formatting**:
  `Markdown formatting density varies by destination. voice-extractor: identify the corpus's formatting conventions (bold frequency, italics use, bullet-point density, code-block presence) and set the baseline.`

- [ ] **Step 3: Verify iron rules + structure identical to academic.md**

Same grep / diff commands.

Critically:
```bash
cd /home/hayden/sourced
grep -c "voice-extractor:" templates/voices/hybrid.md
```

Expected: at least 8 (each non-iron content-calibration section has an explicit voice-extractor instruction). This is the anti-bias signal density — if too low, voice-extractor may default to register-specific patterns.

- [ ] **Step 4: Commit**

```bash
cd /home/hayden/sourced
git add templates/voices/hybrid.md
git commit -m "Add hybrid register-neutral skeleton with anti-bias prose"
```

---

### Task 7: Update voice-extractor.md

Expand register enum, change skeleton selection, adjust workflow step 2, add `### Register drift` report section, expand shipped-name reserved list.

**Files:**
- Modify: `agents/voice-extractor.md`

- [ ] **Step 1: Update Inputs section — register enum expansion**

Locate the `register` param description (around line 20). Currently reads:
```
- `register` (optional) — one of `academic`, `technical`, `casual`, `journalistic`. If omitted, classify the corpus yourself and surface the classification at the top of your report.
```

Use the Edit tool to replace with:
```
- `register` (optional) — one of `academic`, `technical`, `casual`, `journalistic`, `narrative`. If omitted, classify the corpus yourself and surface the classification at the top of your report. The register value selects the skeleton file at `~/.claude/voice/<register>.md`.
```

- [ ] **Step 2: Update Inputs section — skeleton_path default change**

Locate the `skeleton_path` param description (around line 22). Currently reads:
```
- `skeleton_path` (optional) — path to the voice file whose section structure to mirror. Default: `~/.claude/voice/academic.md` (installed by `install.sh --global-only`). If the file at `skeleton_path` is missing, stop and report.
```

Replace with:
```
- `skeleton_path` (optional) — path to the voice file whose section structure to mirror. Default: resolved from the `register` value (or classifier output) as `~/.claude/voice/<register>.md`; `register=mixed` (classification result) resolves to `~/.claude/voice/hybrid.md`. If the file at `skeleton_path` is missing, stop and report.

  Explicit `skeleton_path` override is for advanced users authoring custom skeletons; normal use omits this param and lets skeleton selection flow from register.
```

- [ ] **Step 3: Update Preflight step 3 — shipped-name reserved list**

Locate step 3 (shipped-name collision check, around line 32). Currently reads:
```
3. **Shipped-name collision.** If `voice_name` is in the reserved list of shipped voices (currently: `academic`), stop with `shipped-name-collision` regardless of the `overwrite` value. Shipped voices are refreshed from the repo on every `install.sh --global-only`, so a generated file at a shipped name would be silently clobbered on next install. Reject rather than produce a file with a latent expiration. Maintainers: when a new shipped voice is added under `templates/voices/`, append its name to the reserved list in this check.
```

Replace the reserved-voices parenthetical:
```
3. **Shipped-name collision.** If `voice_name` is in the reserved list of shipped voices (currently: `academic`, `casual`, `technical`, `journalistic`, `narrative`, `hybrid`), stop with `shipped-name-collision` regardless of the `overwrite` value. Shipped voices are refreshed from the repo on every `install.sh --global-only`, so a generated file at a shipped name would be silently clobbered on next install. Reject rather than produce a file with a latent expiration. Maintainers: when a new shipped voice is added under `templates/voices/`, append its name to the reserved list in this check.
```

- [ ] **Step 4: Update Workflow step 2 — classifier behavior + narrative signals**

Locate workflow step 2 (around line 40). Currently reads:
```
2. **Register.** If provided, trust it. If omitted, classify the corpus as one of `academic`, `technical`, `casual`, `journalistic`, or `mixed` based on sentence length distribution, contraction frequency, punctuation habits, and vocabulary register. A corpus counts as `mixed` when no single register accounts for at least 70% of the sample word count. If classification lands on `mixed`, stop with `mixed-register` and ask the dispatcher to split the directory or pass a label. If a `register` label was provided but the corpus's patterns flatly contradict it (e.g., `academic` label on prose dominated by contractions and two-word sentences), stop with `register-mismatch` rather than silently recalibrating.
```

Replace with:
```
2. **Register.** If provided, trust it. If omitted, classify the corpus as one of `academic`, `technical`, `casual`, `journalistic`, `narrative`, or `mixed` based on:

   - sentence length distribution
   - contraction frequency
   - punctuation habits
   - vocabulary register
   - first-person-pronoun frequency (narrative marker)
   - past-tense-narrative constructions (narrative marker)
   - scene / dialogue indicators (narrative marker)

   Threshold: the corpus counts as a single register when that register accounts for at least 85% of the sample word count. Between 70% and 85%, or below 70% (no majority), the corpus counts as `mixed`.

   **Skeleton selection based on classifier output:**
   - Single register ≥ 85% → `skeleton_path = ~/.claude/voice/<register>.md`
   - `mixed` (< 85% single-register) → `skeleton_path = ~/.claude/voice/hybrid.md`; proceed with workflow

   `mixed` no longer halts. The hybrid skeleton is a first-class option for blended corpora.

   If a `register` label was provided but the corpus's patterns flatly contradict it (e.g., `academic` label on prose dominated by contractions and two-word sentences), stop with `register-mismatch` rather than silently recalibrating.
```

- [ ] **Step 5: Update Report format — new `### Register drift` section**

Locate the report format block (around line 76-122). Insert a new `### Register drift` subsection between `### Register` and `### Sample stats`. Use the Edit tool.

Current fragment:
```
### Register
<provided | inferred> — <label>
<one-line reasoning if inferred>

### Sample stats
```

Replace with:
```
### Register
<provided | inferred> — <label>
<one-line reasoning if inferred>

### Register drift
<only emit when dominant register is < 95% clean; omit this section entirely when corpus is dominantly one register>
Classified as <top> (<top-pct>%). Minority presence: <runner-up> <runner-up-pct>%<, <third> <third-pct>%> when applicable.
If your intent is <runner-up> voice, re-run with `register: <runner-up>` and `overwrite: true`.

### Sample stats
```

- [ ] **Step 6: Update Rejection categories — remove mixed-register**

Locate Rejection categories section (around line 126-139). Find the `mixed-register` bullet:
```
- **`mixed-register`** — no `register` label provided and classification lands on `mixed`.
```

Delete this line (it's no longer a halt condition — mixed now auto-routes to hybrid). Keep `register-mismatch` and all others.

- [ ] **Step 7: Update Next steps section in report template**

Locate the `### Next steps` fragment at the end of the report template (around line 118). Add a new bullet about the decoupling:

Current (around line 121):
```
If the register was inferred and looks wrong, re-run with `register: <correct-label>` to force recalibration.
```

Append after that line:
```
If you previously generated a voice against the pre-decoupling `academic.md` skeleton (before the 6-skeleton decoupling shipped), re-run voice-extractor with `overwrite: true` to pick up the new routing and register-appropriate skeleton selection.
```

- [ ] **Step 8: Verify edits land without syntax damage**

```bash
cd /home/hayden/sourced
wc -l agents/voice-extractor.md
```

Expected: roughly 160-180 lines (was 160; added ~10 for register-drift section + narrative signals).

```bash
grep -c "narrative" agents/voice-extractor.md
```

Expected: at least 4 (register enum mention, classifier enum mention, skeleton-selection mention, narrative markers list).

```bash
grep -c "hybrid" agents/voice-extractor.md
```

Expected: at least 2 (shipped-name reserved list, mixed-auto-route skeleton path).

```bash
grep -c "mixed-register" agents/voice-extractor.md
```

Expected: 0 (the rejection category is gone).

- [ ] **Step 9: Commit**

```bash
cd /home/hayden/sourced
git add agents/voice-extractor.md
git commit -m "Update voice-extractor: expand registers, auto-route hybrid, add register-drift report"
```

---

### Task 8: Update docs (VOICES.md, ARCHITECTURE.md, README.md)

**Files:**
- Modify: `docs/VOICES.md`
- Modify: `ARCHITECTURE.md`
- Modify: `README.md` (minor)

- [ ] **Step 1: Read existing docs/VOICES.md**

```bash
cat /home/hayden/sourced/docs/VOICES.md
```

- [ ] **Step 2: Update docs/VOICES.md with 6-skeleton + 4-axis documentation**

Use Edit tool. Locate the section that currently describes the single shipped `academic` voice. Expand to cover:

1. **The 6 shipped skeletons** — name each; one-line purpose per; point at the file path
2. **The 4-axis section structure** — list Iron / Tone / Structure / Dimension with their scope
3. **Skeleton selection by register** — describe auto-routing (≥ 85% → matching skeleton; < 85% → hybrid.md)
4. **`register` param** — document the 5 allowed values + how classifier fills-in when omitted
5. **hybrid.md's lean contract** — one paragraph explaining why hybrid.md's non-iron prose is register-neutral and what that implies for voice-extractor's output

Concrete insertions:

After the intro paragraphs, insert:
```markdown
## Shipped skeletons

Sourced ships 6 register-specific voice skeletons under `~/.claude/voice/`. Each is a template for voice-extractor to mirror when generating a per-author voice file from a writing-samples corpus.

| Skeleton | Register | Typical documents |
|----------|----------|-------------------|
| `academic.md` | academic | research papers, essays, dissertations |
| `casual.md` | casual | blog posts, personal essays, conversational pieces |
| `technical.md` | technical | documentation, API references, procedural guides |
| `journalistic.md` | journalistic | news stories, features, reported commentary |
| `narrative.md` | narrative | personal essays, reflection pieces, college application essays, memoir |
| `hybrid.md` | register-neutral | blended corpora that don't cleanly fit one register |

Each skeleton has identical section structure (same 4 top-level headers; same subsection names). What varies is the non-iron prose within each section — each is calibrated to its register's defaults.

## Section structure: 4 orthogonal axes

Each skeleton organizes its rules under 4 top-level headers:

- **`## Iron rules`** — global prohibitions (CLAUDE.md §10 Never list + any line tagged `[iron]`). Never calibrated from corpus. `## §10 exemptions` nests as a subsection here for per-voice carve-outs.
- **`## Tone`** — what the voice sounds like: register, stance, sentence rhythm, vocabulary, audience orientation (we/you/third-person).
- **`## Structure`** — how the prose is organized: connectedness, pacing, concept setup, argument-building, paragraph length.
- **`## Dimension`** — unique author habits that vary independent of register: analogies / anchors, punctuation quirks, formatting conventions.

The 4 axes are orthogonal: a writer can be tonally casual + structurally academic + dimensionally narrative all at once. Voice-extractor calibrates each axis from corpus evidence per-section.

## Skeleton selection: auto-route by classifier

When you invoke `voice-extractor` with a writing-samples corpus, it classifies the corpus and picks a skeleton:

1. If you pass `register: <label>`, that skeleton is used directly. Halts only if the corpus flatly contradicts the label (`register-mismatch`).
2. If you omit `register`, the classifier runs:
   - **≥ 85% single register** → that register's skeleton is used.
   - **< 85% on any single register** (blended corpus) → `hybrid.md` is used.

No `mixed-register` halt. Blended corpora auto-route to hybrid without user intervention.

The classifier surfaces the full breakdown in the report's `### Register drift` section when the dominant register is < 95% clean, so you can re-run with a specific register if the auto-route looks wrong.

## Hybrid.md's contract

`hybrid.md` is the register-neutral fallback. Its non-iron prose deliberately does NOT describe rules in register-specific terms. Instead, each section states the underlying rule (what connects to what, what comes first, etc.) and directs voice-extractor to derive the specifics from corpus evidence.

**Why it matters:** a corpus that's structurally academic but tonally casual (school essays are the canonical example) would, under a single-skeleton system defaulting to academic, get flattened to academic register throughout. Hybrid.md preserves the blend: each section extracts its rule from THIS corpus, not from a pre-chosen register's template.

**When hybrid.md fires:** any corpus where no single register crosses 85%. Classifier surfaces the breakdown so you can see which registers contributed.
```

- [ ] **Step 3: Update ARCHITECTURE.md voice-system section**

Locate the "Voice system: three layers" section. After the three layers list, append a paragraph:

```markdown
**Skeleton-per-register (6 skeletons).** As of 2026-04-19, the voice library ships 6 register-specific skeletons (`academic`, `casual`, `technical`, `journalistic`, `narrative`, `hybrid`) instead of a single `academic.md`. Voice-extractor selects the skeleton based on corpus classification: a dominant-register corpus (≥ 85%) uses that register's skeleton; a blended corpus (< 85%) uses `hybrid.md`, which is authored with register-neutral non-iron prose and explicit anti-bias instructions. Each skeleton organizes rules under 4 orthogonal axes — `## Iron rules`, `## Tone`, `## Structure`, `## Dimension` — so a voice can be calibrated along each axis independently. See `docs/VOICES.md` for the full register map and routing logic.
```

- [ ] **Step 4: README.md minor update**

Locate the bullet that reads "Voice preservation, with generator-level guardrails." Update to mention the 6-skeleton system. Current:
```markdown
- **Voice preservation, with generator-level guardrails.** Per-author voice files specify sentence structure, stance, pacing, concept setup, and punctuation habits. A global inventory of AI-writing signatures (em dashes, "not X but Y" pivots, ornamental triads, throat-clearing adverbs, demonstrative-noun openers) applies regardless of voice and is enforced at both writing and editing time.
```

Replace with:
```markdown
- **Voice preservation, with generator-level guardrails.** Per-author voice files specify tone, structure, and dimension rules across 4 axes. Voice-extractor selects one of 6 shipped register skeletons (academic, casual, technical, journalistic, narrative, hybrid) based on corpus classification. A global inventory of AI-writing signatures (em dashes, "not X but Y" pivots, ornamental triads, throat-clearing adverbs, demonstrative-noun openers) applies regardless of register and is enforced at both writing and editing time.
```

- [ ] **Step 5: Commit the docs triple**

```bash
cd /home/hayden/sourced
git add docs/VOICES.md ARCHITECTURE.md README.md
git commit -m "Document 6-skeleton register decoupling across VOICES/ARCHITECTURE/README"
```

---

### Task 9: Smoke-verify the shift

No automated harness for voice-extractor (it's LLM-followed). Verification is a manual 3-corpus smoke test: dispatch voice-extractor against three representative corpora and check the skeleton it picks and the drift-report accuracy.

**Files:**
- Temporary (created in /tmp, not committed): 3 scratch corpora to dispatch against

- [ ] **Step 1: Create clean-academic scratch corpus**

Pick any writer's academic-style writing in your history (papers, essays, reports — anything clearly academic-register). Drop 5+ files with >5000 total words into `/tmp/scratch-academic/`. Each file should be `.md` or `.txt`.

If you don't have such a corpus readily available: skip the smoke test for this corpus; note in the report that clean-academic wasn't tested.

- [ ] **Step 2: Create school-essay scratch corpus (blended)**

Drop 5+ files in `/tmp/scratch-school-essay/` that are structurally academic but tonally casual. First-person narration in an essay shape. College application essays, reflection pieces, personal essays for class assignments. >5000 words total.

- [ ] **Step 3: Create pure-casual scratch corpus**

Drop 5+ files in `/tmp/scratch-casual/` that are conversational blog posts, diary entries, personal emails (scrubbed of recipient info if needed). >5000 words total.

- [ ] **Step 4: Manually dispatch voice-extractor against clean-academic**

Start a Claude Code session in a scratch project directory (not the sourced repo itself — the repo-self-guard refuses install into the repo). Dispatch:

```
Dispatch voice-extractor against samples in /tmp/scratch-academic. voice_name: smoke-academic. overwrite: true. samples_dir: /tmp/scratch-academic. register: omit. skeleton_path: omit.
```

Expected in the subagent's report:
- `### Register` — classified as `academic` with high confidence (≥ 85%)
- `### Register drift` — section absent (because academic was dominant ≥ 95%), OR minority-presence line if the corpus has some variation
- Resulting skeleton used: `~/.claude/voice/academic.md`
- Output file at `~/.claude/voice/smoke-academic.md`

Verify by inspecting the output file's sections and checking that section prose reflects academic-register calibration (long connected sentences in the Sentence Connectedness exemplar, etc.).

- [ ] **Step 5: Manually dispatch voice-extractor against school-essay**

Same dispatch pattern, against `/tmp/scratch-school-essay`.

Expected in the report:
- `### Register` — could be anything; likely `mixed` OR a register at 70-85%
- `### Register drift` — present, showing the breakdown (e.g., "Classified as academic (72%); casual was 21%, narrative was 7%")
- Resulting skeleton used: `~/.claude/voice/hybrid.md` (because < 85%)
- Output file preserves the blend: sections calibrated per corpus, not defaulted to academic

This is THE test. If the school-essay corpus routes to academic.md instead of hybrid.md, the 85% threshold is wrong. If it routes to hybrid.md but the output file reads academic anyway, hybrid.md's anti-bias prose isn't strong enough.

- [ ] **Step 6: Manually dispatch voice-extractor against pure-casual**

Same dispatch pattern, against `/tmp/scratch-casual`.

Expected:
- `### Register` — classified as `casual` with high confidence (≥ 85%)
- Resulting skeleton: `~/.claude/voice/casual.md`
- Output preserves casual register

- [ ] **Step 7: Clean up scratch corpora**

```bash
rm -rf /tmp/scratch-academic /tmp/scratch-school-essay /tmp/scratch-casual
rm -f ~/.claude/voice/smoke-academic.md ~/.claude/voice/smoke-school-essay.md ~/.claude/voice/smoke-casual.md
```

- [ ] **Step 8: Document smoke-test results in the PR body**

Not a commit step; document results in the PR description when opening it. For each of the 3 corpora, note:
- Which register the classifier chose
- Whether the drift section fired
- Which skeleton was used
- Whether the output file's sections visibly reflect the expected register calibration

If the school-essay corpus did NOT route to hybrid, investigate:
- Is the 85% threshold actually being read from the updated step 2?
- Are the narrative-marker signals working?
- Is the corpus genuinely ≥ 85% academic (in which case the test corpus is wrong, not the code)?

---

## Execution handoff

Plan complete and saved to `docs/plans/2026-04-19-voice-extractor-decoupling-plan.md`.

After all 9 tasks complete:
1. Run `wc -l templates/voices/*.md` and verify 6 files exist, each 100-160 lines
2. Run `diff <(grep '^## ' templates/voices/academic.md) <(grep '^## ' templates/voices/casual.md)` etc. across all pairs — all 6 skeletons should have identical `## `-level structure
3. `git log --oneline main..HEAD` should show 9 commits (Task 1-8; Task 9 is manual-verify only, no commit)
4. Push branch; open PR with smoke-test results from Task 9 in the body
