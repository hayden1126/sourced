# Voices

[← Back to README](../README.md)

Voice rules live in a per-project `voice.md` rendered from a named voice in the voice library. Voice is per-project, so concurrent Claude Code sessions on different projects can carry different voices without conflict.

The shipped `academic` voice is the author's own: personal register plus specific analogy anchors (Clever Hans, chicken sexing, split-brain) calibrated to one writer. Treat it as an example, not a neutral academic default. For a different author or a different register, copy it to a new name and edit, or generate one from a corpus (see below).

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

## Pick a voice at install

```bash
/path/to/sourced/install.sh --voice academic   # default
/path/to/sourced/install.sh --voice mycustom   # requires ~/.claude/voice/mycustom.md
```

`--voice` is validated before any project file is written. An invalid name errors out cleanly with the list of available voices; no half-installed project.

Library voice files are templates: any `{{USER}}` token is substituted with your configured name when `install.sh --voice` renders the voice into a project. That's why the shipped `academic.md` shows `{{USER}}` on line 3 — the token is replaced per-project, so each project's `voice.md` carries the right name without the library file having to store it.

## Authoring a custom voice by hand

Copy the shipped skeleton and edit:

```bash
cp ~/.claude/voice/academic.md ~/.claude/voice/mycustom.md
# edit ~/.claude/voice/mycustom.md
/path/to/sourced/install.sh --voice mycustom   # inside the target project directory
```

The skeleton's section structure is canonical: every section appears in every derived voice. Don't delete sections — leave `TBD` rather than inventing a rule your taste doesn't settle. Iron rules (under `## Iron rules` in the skeleton, or anywhere else carrying the `[iron]` token) must pass through verbatim.

## Generating a voice from a writing-samples corpus

Hand-authoring a voice file is slow. If you have a corpus of the writer's prose (past papers, essays, reports, blog posts — whatever is representative), the `voice-extractor` subagent produces a calibrated first draft of the library file.

**Requirements.** At least 3 files and 5,000 words combined, in `.md` or `.txt`. Other file types (PDF, `.docx`, `.rtf`) are silently skipped and listed in the report. More samples produce more stable patterns; the 3-file / 5,000-word floor is a hard minimum, not a target. 15,000–30,000 words across 10+ files is where the output gets genuinely useful.

**Usage.** Open Claude Code in any project that already has a rendered `CLAUDE.md`. The agent reads `CLAUDE.md` §9 at startup and knows how to dispatch the subagent. Ask in natural language:

> *"Generate a new library voice called `mycustom` from the samples at `~/writing/papers/`. The register is academic."*

The agent will announce a switch to `[collaborative mode]` if needed, dispatch `voice-extractor` in a single Agent call, and present the report when the subagent returns. Name hygiene: pick a name matching `[a-z0-9_-]+` (lowercase letters, digits, underscore, hyphen — uppercase is rejected). The name `academic` is reserved because the shipped voice lives there; the subagent refuses with `shipped-name-collision` if you try it, regardless of the `overwrite` flag.

**What the subagent does:**

- Mirrors the section structure of a skeleton voice selected by the register classifier: a dominant-register corpus (≥ 85%) routes to its matching shipped skeleton (`academic`, `casual`, `technical`, `journalistic`, `narrative`); a blended corpus routes to `hybrid.md` (register-neutral). No single default.
- Fills each section from patterns found in the samples, with verbatim exemplars attributed to their source file in HTML comments.
- Leaves sections `TBD —` where the samples don't settle the question. Never fabricates rules or exemplars.
- Preserves iron rules verbatim (see below).
- Surfaces recurring named references as "anchor candidates" in the report. The Anchors block in the output file is always TBD by design; anchors are a judgment call only you can make.
- Classifies the corpus register if you don't pass one. Routes to the matching skeleton when a single register reaches ≥ 85% of the corpus; routes to `hybrid.md` (register-neutral) when no single register dominates. Refuses with `register-mismatch` only when the label you passed flatly contradicts what the samples show.

**After the subagent returns:**

1. Read the report — especially `### Sections filled` (low-confidence sections deserve a look), `### Sections left TBD`, `### Iron-rule conflicts`, `### Anchor candidates`, and `### Exemplar audit` (spot-check a few quotes against their source files).
2. Open `~/.claude/voice/<voice_name>.md` in an editor. Search for `TBD —` markers. Each one needs either a hand-written rule (drawing on the report's guidance) or deletion. At minimum, fill in the Anchors block from the `### Anchor candidates` list, or delete it if none fit.
3. Once no TBDs remain, render the voice into a project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --voice mycustom
```

**Re-running:**

- **Corpus was too thin.** Add samples, re-run with `overwrite: true`. Without `overwrite`, the subagent refuses to clobber an existing library file.
- **Register was inferred and came out wrong.** Re-run with the correct `register:` label (`academic | technical | casual | journalistic | narrative`).
- **Want a different skeleton.** Pass `skeleton_path: <absolute path>` pointing at another voice in `~/.claude/voice/`.

**Scope.** Voice-extractor is a one-shot setup utility. It runs only when you ask, never auto-triggers during writing or research, and never runs in parallel with itself. It does not modify your project's `CLAUDE.md`, `voice.md`, or anything under the project directory — it writes exactly one file, `~/.claude/voice/<voice_name>.md`. Rendering into a project is always a deliberate `install.sh --voice <voice_name>` step you run yourself.

## Iron rules and defense-in-depth

Some voice rules are **iron**: they pass through every derived voice verbatim regardless of what the writing-samples corpus shows. A rule is iron if either:

- It sits under a skeleton section whose heading is `## Iron rules`, `## AI-tells`, or `## Generation signatures`; or
- Its line carries the literal token `[iron]` anywhere.

Iron rules are enforced in three places:

1. **Inside `voice-extractor`.** Step 3 identifies iron rules from the skeleton; step 5 preserves them verbatim; step 8 self-checks the draft before writing.
2. **Caller-side in `academic-researcher`.** After `voice-extractor` returns, the agent substring-checks each iron rule against the produced file before surfacing the report. A missing iron rule blocks the report from being treated as success.
3. **Install-time in `install.sh`.** `validate_iron_rules` normalizes both skeleton and candidate (lowercase, collapse whitespace, strip trailing punctuation), substring-matches each iron rule, and aborts install with non-zero exit on any miss.

Any one layer failing doesn't ship a broken voice. All three would have to miss.

Generation signatures, the AI-writing tells that apply regardless of voice, live in CLAUDE.md §10, not in individual voice files. Voice files cover per-author calibration (sentence structure, stance, pacing, punctuation habits); §10 covers category-level prohibitions the system enforces uniformly.

## Direct quotations are carved out of §10 and voice

Text inside a direct quotation is evidence, not generated prose. Verbatim quotation wins over both §10 Never-list prohibitions and voice-level punctuation rules: preserve the source's em dashes, ornamental triads, commas, colons, and semicolons as printed. The carve-out applies to the quoted span only; the writer's framing sentence around the quote still obeys §10 (`"Hegel — writing in 1807 — argues..."` is flagged as an em-dash violation in the framing, independent of the quote that follows).

If a substitution is genuinely unavoidable (downstream renderer cannot emit the character, for example), mark it with a bracketed editorial note rather than replacing silently: `adequate to them [,] i.e., the state` makes the change visible. Silent replacement fails §4's no-ellipsis-trickery discipline. See CLAUDE.md §10 *Direct quotations* and §4 *Quote verbatim* for the full rule.

## Exempting a §10 pattern for one voice

If a writer legitimately uses a pattern on CLAUDE.md §10's Never list (em-dashes for appositives, ornamental triads for rhetorical emphasis, etc.), the voice library file can exempt that specific rule. Silence in the voice file is not permission; the exemption has to be declared explicitly, and `install.sh` validates it at render time.

**Canonical IDs.** Each bullet on §10's Never list carries a stable ID:

| ID | What it covers |
|----|----------------|
| `em-dashes` | Em dashes for appositives, interruptions, or ranges. |
| `not-x-but-y` | "Not X but Y" and its comparative-pivot variants. |
| `ornamental-triads` | Triadic or tetradic ornamental lists. |
| `throat-clearing-openers` | Sentence-initial "Crucially," "Ultimately," etc. |
| `demonstrative-openers` | Demonstrative-noun paragraph openers with a weak antecedent. |
| `ornamental-compounds` | Hyphenated conceptual compounds that appear once and disappear. |

The IDs are extracted from `templates/CLAUDE.md` §10 at install time, so adding or renaming an ID in that file flows through to validation with no extra registration step.

**How to declare an exemption.** Open the library voice file at `~/.claude/voice/<name>.md`. Find the `## §10 exemptions` section. Add one bullet per exempted rule; each bullet starts with a canonical ID, followed by a separator (colon, en-dash, or hyphen) and a one-line rationale grounded in corpus evidence:

```
## §10 exemptions

- em-dashes: author uses them for appositives; 43 instances across 8 samples.
- ornamental-triads: deliberate balanced lists for rhetorical cadence; 12 instances.
```

Only the leading ID is machine-read; the rationale is for the reader. Unknown IDs (typos, outdated names) fail install-time validation and abort the render. `install.sh` prints the known-ID list when it rejects an exemption so the fix is immediate.

**Why the workflow has a manual step.** `voice-extractor` will not auto-populate `## §10 exemptions`. Corpus evidence of a §10 pattern surfaces in the subagent's `### Iron-rule conflicts` report; promoting a conflict to an exemption bullet is a deliberate decision made after reviewing the flagged instances. Auto-exemption would defeat the voice-preservation-with-guardrails promise the framework is built around — the guardrails should only drop when the writer confirms the pattern is intentional.

**Scope and runtime.** An exemption suspends the named §10 rule for the writer's own prose and no other surface. Quoted text, other Never-list items, density thresholds, and iron rules are all unaffected. At runtime, `[writing mode]` and `[editing mode]` scan `voice.md`'s `## §10 exemptions` on entry; each listed ID suspends its §10 rule, others continue to fire.

## Project-level voice handling

Each project's `voice.md` records which library voice it was installed from (as an HTML comment on the first line). A later bare `install.sh --update` reuses that choice and refreshes `voice.md` from the current library version, so upstream voice-rule changes propagate. Switching to a different voice on an existing project requires `--force` (replace) or `--update --voice <new>` (explicit switch).

Shipped voices at `~/.claude/voice/<shipped-name>.md` are refreshed on every install from the repo. User-authored voices (names that don't collide with shipped ones) are left untouched. To customize a shipped voice without losing edits, copy to a new name first.
