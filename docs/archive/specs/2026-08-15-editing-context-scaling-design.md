# Editing context-scaling: section-scoped editing plus a thin global pass

Date: 2026-08-15
Status: design approved; implementation in flight on branch `editing-section-scoped`
Serves: synthesis integrity (editing's Pass 2 is the §4 prose-time audit, which degrades at length; see §Diagnosis)
Related: ROADMAP Path 2 (audit ledger + retrieval) and Path 3 (stateless driver); issue #73
(passage retrieval); the Direct-API offload lane; the verified-claims DB.

## Problem

Running the full pipeline (plan, research, write, edit, format) on a real-length paper overflows the
context window. The failure is not spread evenly across the modes; it concentrates in editing.

## Diagnosis

Exploration of the codebase this session established where context actually accumulates.

- **Research and writing already externalize the heavy payloads.** `source-finder` reads full
  sources in an isolated `omitClaudeMd` subagent, writes verified entries to a shard file, and
  returns a report under 300 words. `prose-drafter` drafts each section in a fresh `omitClaudeMd`
  subagent fed only that section's `@id` citation entries, and the draft is appended to the file
  section by section. Neither mode co-locates the whole draft with the whole citation log.
- **Editing delegates nothing.** All ten passes run in one continuous context (`editing.md`), which
  holds `config/voice.md` in full, the entire draft, and the entire citation log. Pass 2 then emits
  the citation-payload re-read list, reproducing the verbatim `exact_quote` (and often
  `surrounding_context`) for every citation instance a second time. Seven of the ten passes
  re-traverse the whole draft; passes 6, 7, and 9 additionally re-read the never-list and voice file
  mid-stream.
- **Measured cost.** From the finished gender essay at `~/writing/cross-sex-empathy`: 1,821 words,
  27 citation instances, a 92 KB citation log (about 23K tokens). Per instance is roughly 850 tokens,
  dominated by `exact_quote` plus `surrounding_context` (the schema stores the quote plus one or two
  neighbor sentences on each side). That essay never overflowed because it is small; its value is a
  clean measurement of the per-instance cost.
- **Extrapolation.** A real seminar paper (about 7,000 words, about 30 sources, about 70 citation
  instances): the citation log alone is roughly 60K tokens, loaded whole and resident across all ten
  passes; Pass 2 re-emits most of it; the draft is resident and re-traversed; the pass artifacts
  accumulate. That lands near 150K to 250K tokens in one unbroken context, and it rises with length.
- **It is not only overflow.** "Context rot" (Chroma, 18 frontier models including Claude 4) shows
  accuracy degrading well before the window fills, and coherent, well-structured input degrading
  attention more than shuffled input. So whole-draft editing is very likely producing weaker audits
  on real papers even when it technically fits. This upgrades the problem from "sometimes crashes"
  to "systematically weaker editing at length."

The chat transcript of the gender-essay run is unrecoverable (no session history survives at the old
`papers/` slug, the new `writing/` slug, or in the `.claude-old` backup). The surviving artifacts in
that project are the evidence base and the end-to-end test target.

## Research synthesis

Four parallel research threads (long-form generation and revision; agent context management;
embedding-free retrieval and prompt caching; global coherence from local processing) converged on
one architecture. Load-bearing conclusions, with sources:

1. **The field moved from "summarize to fit" to "externalize and retrieve."** Durable state on disk,
   lightweight references resident, fresh isolated workers, summarization as a last resort.
   (Anthropic, *Effective context engineering for AI agents*, 2025-09-29; Manus, *Context
   Engineering for AI Agents*, 2025-07; MemGPT/Letta, arXiv:2310.08560.)
2. **Verbatim data must live on disk and be paged by reference, never summarized.** Compaction
   silently and unrecoverably destroys exactly quotes, paths, and citation provenance, which is the
   one class of data sourced cannot lose. (Anthropic context-engineering, as above; the Manus
   restorable-compaction ordering; Tao An, *Fidelity Before Structure*, arXiv:2601.00821, a recent
   preprint, not independently verified, but directionally convergent.)
3. **The swap mechanism is fresh file-keyed subagents, not forks.** A fork inherits the parent's
   context and stays bloated; a fresh subagent is itself the clean working-set boundary and returns
   a compact summary. (Anthropic, *How we built our multi-agent research system*, 2025-06-13.)
4. **Carry a compact structured global state; edit locally against it.** Re3's edit module maintains
   an attribute dictionary and edits surgically against it rather than re-reading the whole draft.
   For sourced this becomes an audit ledger (thesis, claims, term glossary, citation-id to location
   index). (Yang et al., *Re3*, EMNLP 2022, arXiv:2210.06774; DOC, arXiv:2212.10077.)
5. **Local and global passes split cleanly.** Grammar, per-sentence clarity, and citation fidelity
   are inherently local (a section plus its own citations). Terminology consistency,
   definition-before-use order, coreference, flow, and argument threading are inherently global but
   prose-only, so they run on a thin whole-draft view with the evidence payloads stripped. (Sci2Pol,
   arXiv:2509.21493; Grammarly/CoEdIT category split; Monocle, arXiv:2505.20195; Divide-Conquer-
   Reasoning, arXiv:2401.02132.)
6. **Isolation is not free.** Chunked editing has three documented failure modes: hallucination,
   seam artifacts, and lost global information. The fix is passing shared context (outline, neighbor
   boundary sentences, the ledger) through each unit. LongWriter measured roughly 6% coherence loss
   from naive segmentation. (Ou and Lapata, *Context-Aware Hierarchical Merging*, arXiv:2502.00977;
   LongWriter, arXiv:2408.07055.)
7. **Retrieval can stay embedding-free and verbatim.** Layered: metadata filter by section or claim,
   then BM25 plus MMR diversity when the filtered set is still large, then optional tree navigation.
   RARR supplies the per-claim "generate the lookup on demand" loop. All preserve verbatim spans
   because the retrieval target is a log entry, not an embedding. (PageIndex, VectifyAI; MMR,
   Carbonell and Goldstein, SIGIR 1998; RARR, arXiv:2210.08726.)
8. **Prompt caching helps the setup, not the payload.** Caching the frozen prefix (voice plus
   instructions, 1-hour TTL) discounts re-sending it per section, but only if the orchestrator emits
   a byte-identical prefix per call, which requires owning request construction (raw API or SDK),
   not relying on independent subagents to coincidentally align. Caching does not shrink the payload;
   it is complementary to scoped retrieval, not a substitute. (Anthropic prompt-caching docs.)
9. **A genuine gap.** No published system implements a cross-section defect-localizing editing pass;
   even CogWriter only validates each section against a plan, never sections against each other. The
   thin global pass below is the part with no prior art. sourced's existing `staged-reader-review` is
   the closest thing that exists.

## The three paths

The target architecture is: build a compact audit ledger once, run local passes per section in fresh
subagents (each fed only its section prose plus its citations by id plus the ledger plus boundary
context), then run one thin prose-only global pass for the cross-section checks. Payloads live in the
log and are fetched by id; compaction is the airbag. The paths differ in how much of that to build.

- **Path 1 (chosen).** Section-scoped editing plus one thin global pass. Local passes run per section
  in a fresh `section-editor` subagent fed only that section's prose plus its citations fetched by id;
  one thin global pass runs over concatenated prose with payloads stripped, carrying a lightweight
  running skeleton (one-line section summaries plus a term list). No new retrieval infrastructure
  beyond by-id or by-section fetch. Directly kills the confirmed bottleneck by copying the pattern
  writing already uses. Highest confidence, medium effort.
- **Path 2 (deferred to ROADMAP).** Path 1 plus a formal Re3-style audit ledger as durable state,
  plus layered embedding-free retrieval (metadata filter, then BM25 plus MMR). Robust to arbitrary
  length and citation density; more machinery to build and keep in sync (a stale ledger produces
  wrong audits; MMR trimming introduces a recall risk for a completeness-critical system). Trigger:
  a real paper whose per-section citation set is still too large after by-section fetch.
- **Path 3 (deferred to ROADMAP).** A stateless file-driven driver for the whole pipeline: every
  stage and section runs in a fresh context from durable files, orchestrated by a driver (CLI or a
  loop-engineering-style outer loop), with prompt-cached shared prefixes and compaction as airbag.
  Makes length unbounded at every stage and enables resumability and real prompt-cache economics,
  but is the largest change, touches all modes, likely moves parts out of Claude Code into
  direct-API calls, and raises a loop-engineering coupling question. Trigger: book or thesis-length
  work, or wanting the caching economics enough to go direct-API.

The retrieval literature itself argues for starting minimal: metadata filter first, BM25 plus MMR
only if the filtered set is still large. Path 1 is the metadata-filter increment.

## Path 1 design

### Design invariant: preserve the ten passes, change only their scope

The refactor keeps the ten-pass structure and the four forcing-artifact names exactly as they are. It
does not renumber or rename anything. What changes is the scope each pass runs at (per-section vs
global) and where it runs (the `section-editor` subagent vs the parent's global pass). This is a hard
constraint, not a stylistic choice, because several machine checks key on the current shape:

- Invariant I5 matches the four artifact name-strings (`revision report`, `§4 audit list`,
  `citation-payload re-read list`, `voice audit surface-scan report`) by exact bolded substring in
  §7.5, and requires each to appear in a mode body. The names stay verbatim in `editing.md`.
- The `editing-passes` DerivedCount in the consistency suite counts `**Pass N` tokens in `editing.md`
  against `docs/MODES.md`'s "N-pass audit" phrasing. Keeping ten `**Pass N` labels keeps that green
  with no `docs/MODES.md` change.
- The §7.4 editing to formatting gate and `formatting.md` entry both name the four artifacts. The
  handoff must still surface one consolidated set of the four named artifacts in the handoff turn.

So the artifacts are assembled from per-section local runs (their rows produced inside `section-editor`
and stitched by the parent) plus the global pass, and presented as the same four named artifacts at
handoff. The audit discipline is unchanged; only its context footprint shrinks.

### Pass classification (local vs global)

The current ten passes (`editing.md`) split by what they actually need in context. The pass labels
and numbers do not change; each is tagged local or global.

**Local** (needs the section plus its own citations only; runs in the `section-editor` subagent):

- Pass 1, ID validation, for ids appearing in the section.
- Pass 2, the §4 citation audit and its citation-payload re-read list. This is the heaviest pass and
  the most important to scope: it needs only the section's cited sentences and those citations'
  payloads, fetched by id. It never needed the whole log.
- Pass 3, partial-entry recheck, for partial entries cited in the section.
- Pass 4, grammar (per-sentence within the section).
- Pass 5, the paste-artifact and punctuation-mechanics lists (per-sentence within the section).
- Pass 8, quote-density (per-paragraph within the section).
- The per-paragraph sub-checks of Pass 0 (0b sub-claim support, 0c outline correspondence at
  paragraph level, 0d transitions within the section, 0e paragraph one-job) and the per-paragraph
  application of Pass 9 (voice) and Pass 6/7 (§10 and cut patterns) that are genuinely local to a
  sentence or paragraph.

**Global** (needs a thin whole-draft prose view, payloads stripped; runs in the parent or a
dedicated global pass):

- Pass 0's 0a purpose/thesis check and the structural-deviation check (step 4), which are
  whole-draft by definition.
- The cross-section half of Pass 5's proper-noun consistency (a name's spelling must agree across
  sections, not just within one).
- Terminology consistency and definition-before-use order (a term defined in section 5 but first
  used in section 2 is invisible to any single-section editor).
- Cross-section flow, transitions at section boundaries (seams), and argument threading across
  non-adjacent sections (the "two strands unjoined until the conclusion" defect the gender-essay
  reader-review caught).

Passes that are mixed (Pass 0, Pass 5, Pass 6/7, Pass 9) are split: the per-paragraph part runs
local, the cross-section part runs in the global pass. The ten-pass semantics are preserved; what
changes is the scope each part runs at.

### The `section-editor` subagent

A new agent `agents/section-editor.md`, sibling to `prose-drafter`, `omitClaudeMd: true`, tools
`Read, Glob, Grep` (Edit is not needed; it returns edited prose and artifacts, the parent stitches).
It mirrors the prose-drafter dispatch contract.

Input bundle (parent constructs and inlines, following the writing.md Phase 2 pattern):

- `section_label`, `register_mode`, the section prose to edit.
- `citation_entries`: full records for only the `@id`s in this section, fetched by id from the log
  (not the whole log). Same field set prose-drafter receives (`exact_quote`, `surrounding_context`,
  `reliability_basis`, `retrieval`, timestamps).
- `voice_rules` (register-filtered), `cut_patterns`, `never_list`, worked paragraphs.
- `boundary_context`: previous-section last sentence, next-section first sentence, and the section's
  outline slot, so local edits do not introduce seams.
- The audit-row grammar the local passes must emit (so the machine-checked format is preserved; see
  §Integration).

Return: the edited section prose plus the local forcing artifacts for that section (its slice of the
revision report, the citation-payload re-read list, the §4 audit list, and the per-section proofread
and voice lists), in the exact row grammar `sourced check` parses.

The parent runs its own independent per-sentence audit on the return (as writing.md already does for
prose-drafter), stitches the edited prose into the draft file, and accumulates the per-section
artifacts.

### The thin global pass

After all sections have run locally, one global pass over a thin whole-draft view:

- **Thin-view generator.** Concatenate the section prose, keep the `@id` markers, drop the quote
  payloads. This is prose only; the citation log is not loaded.
- **Running skeleton.** One-line summary per section plus a term list (term to defining section),
  built as sections complete. This is a lightweight, in-band precursor to Path 2's full ledger.
- **Global checks.** Pass 0a purpose/thesis, structural deviation, cross-section proper-noun
  consistency, terminology consistency, definition-before-use order, section-boundary seams, and
  argument threading. It re-descends into a section's full text only when it flags a specific seam
  (boundary-context injection, per Ou and Lapata).

### Forcing artifacts and the formatting gate

The four forcing artifacts (revision report, §4 audit list, citation-payload re-read list, voice
audit surface-scan report) still exist and still gate the handoff to formatting. What changes is that
the local artifacts are now emitted per section (and stitched into a per-draft record) and the
cross-section findings are added by the global pass. The editing to formatting gate passes only when
every section's local artifacts are clean (or acknowledged) and the global pass is clean. The exact
manifest wording (§7.4, §7.5) is updated to say the artifacts are assembled from per-section local
runs plus the global pass, without weakening the gate. See §Integration for the precise edits.

### Compaction placement

Compaction is the airbag, not the steering. It is safe only for ephemeral working state (audit
reasoning, prose-only pass output), never for the verbatim payloads, which are re-fetched from the
log by id. This inherits the property that makes Claude Code compaction safe (truth in files, summary
as pointer), available to sourced only because the payloads already live in the log. If any
compaction runs, restrict it to clearing already-consumed tool results; never route a quote-bearing
context through a summarizer, and never let it eat an un-consumed forcing artifact mid-edit.

## Integration points and risks

Precise touch points, from a read-only map of the current code.

**Manifest `src/sourced/data/templates/CLAUDE.md`.**
- §7.4 gate table, the `editing → formatting` row (line 273): keeps the four artifact names; the gate
  condition still reads "revision report + §4 audit clean + citation-payload re-read list clean +
  voice audit surface-scan report emitted + paste target named". No change needed beyond confirming
  the consolidated set is what the handoff emits. Note the `§4 audit list` name is shared with the
  `refining → writing` gate (line 271), so do not rename it.
- §7.5 forcing-artifact definitions (lines 286-295): update only the "Emitted by ... Pass N" phrasing
  to note per-section local emission plus global-pass consolidation. The four bolded name-strings
  stay verbatim (invariant I5). Keep §7 under the 200-line budget (invariant I9).
- §7.6 precedence, canonical §10 IDs, direct-quotations carve-out (lines 297-317): unchanged. The §10
  work still runs; it just runs per-paragraph (local) plus a cross-section scan (global).
- §4 items 1-6 (lines 92-124): unchanged. Pass 2 still audits prose against the log; it audits one
  section's cited sentences against that section's entries.

**Invariants (`src/sourced/validators/invariants.py`, I1-I11).**
- I5 (artifact reachability): keep the four names verbatim in `editing.md`. Satisfied by construction.
- I8 (mode-body compliance): `editing.md` must keep its six required sections in order (Overview,
  When to Use, Steps, Red Flags, Rationalizations, Exit Gates); it also carries an Iron Law box, kept.
  `section-editor` is an agent, not a mode, so I8 does not apply to it.
- I11 (no flat paths): `agents/section-editor.md` is scanned; use full paths (`config/voice.md`,
  `sources/<draft>.citations.json`), never bare filenames.
- No invariant parses the internal row grammar of the artifacts, so the per-section rows are enforced
  by mode-body prose only; the `section-editor` must emit the identical row grammar the parent expects.

**Dispatch (mirror `docs/modes/writing.md` Phase 2, steps 8-17).** The parent (`academic-researcher`,
defined inline in the project `CLAUDE.md`, not a separate file) dispatches `section-editor` via the
`Agent` tool from inside `[editing mode]`, exactly as it dispatches `prose-drafter` from `[writing
mode]`. Citation entries are selected per section by `@id` from `sources/<draft>.citations.json` and
inlined (step 12 is the pattern). On return, the parent runs its own independent audit (step 15) and
stitches the edited prose into the draft file (step 16). `section-editor` frontmatter mirrors
`prose-drafter`: `tools: "Read, Glob, Grep"`, `model: sonnet`, `omitClaudeMd: true`.

**Consistency suite (`tests/consistency/registry.py`).** The `editing-passes` DerivedCount stays green
because the ten `**Pass N` labels are preserved. There is no `shipped-agent-names` DerivedSet today, so
a new agent is not machine-checked; optionally add one to enforce the agent roster across README,
ARCHITECTURE, and INSTALL. Add a `test_skill_frontmatter`-style check only if we want agent frontmatter
validated (it currently is not).

**Agent registration (hand-maintained).** Agents auto-mirror from `src/sourced/data/agents/`, so
dropping `section-editor.md` there ships it. The human-maintained mentions to update for consistency:
the `editing.md` dispatch steps (new), `ARCHITECTURE.md` Subagents table (~lines 111-114), `README.md`
line 7 (count "Four" to "Five"), and `docs/INSTALL.md` (the install table ~lines 189-192 and the
file-tree ~lines 255-258).

**Golden snapshot.** If the shipped `CLAUDE.md` template changes (the §7.5 phrasing edits), regenerate
`tests/cli/golden/__snapshots__/test_render_golden.ambr` (`pytest tests/cli/golden/ --snapshot-update`)
and fold it into the same commit.

**`formatting.md`.** Validates presence of all four artifacts by exact name at entry (lines 11, 17,
180, 260). Unchanged, provided the handoff turn still surfaces the consolidated four.

Known risks:

- **Rigid, gate-governed mode.** editing.md is explicitly rigid with a load-bearing ten-pass order
  and manifest-referenced gates. The refactor must preserve pass semantics and gate strength; it
  changes scope, not the audit discipline.
- **Machine-checked formats.** `sourced check` parses the audit-row grammar. The per-section artifacts
  must emit the identical grammar so the invariant still passes.
- **Seams.** The documented failure mode of chunked editing. Mitigated by boundary context and the
  global pass; not eliminated. The global pass is the backstop.
- **The global cross-section pass has no prior art.** It is the novel component and the main quality
  risk; it is the same component in all three paths.
- **Cost.** Per-section dispatch multiplies LLM calls. Each is cheaper and bounded, but there are
  more of them.

## Testing and verification

- Consistency-suite coverage for the new `section-editor.md` (frontmatter present, parses, name
  matches dir), mirroring `test_skill_frontmatter`, plus any new verbatim-fragment or byte-identical
  clusters the editing rewrite introduces.
- Golden policy unchanged: agents and mode bodies are single-source (no golden); skeletons, voices,
  styles, and `CLAUDE.md` are snapshotted. Regenerate goldens only if `CLAUDE.md` is touched.
- Full gate: `pytest`, `ruff check src tests`, `python3 -m sourced check --invariants` (expect the
  full set green). Parity needs pandoc 3.1.3 on PATH.
- End-to-end: run the refactored editing mode against `~/writing/cross-sex-empathy` and confirm
  per-section contexts stay bounded (target about 25K to 30K per section, about 15K for the global
  pass) and the audit artifacts still emit per section. Real-artifact proof, not assertion.

## Future work

Paths 2 and 3 are logged in ROADMAP with triggers. Path 1 is the foundation; a real long paper tells
us whether the ledger and retrieval (Path 2) or the stateless driver (Path 3) earn their cost.
