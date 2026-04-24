# [research mode]

## Overview

Find and vet sources. Apply §3 source verification at every candidate. Collect APA-ready metadata as you go. Log verified sources to the citation log per §8 Moment 1. Never hallucinate citations, bylines, page numbers, or DOIs. The central failure mode this mode exists to prevent is **logging or citing an unverified source** — a source whose full text you have not read, whose byline you have not confirmed from the source itself, or whose metadata you are reconstructing from memory.

This is a **rigid** mode. The iron law is non-negotiable. §3 and §4 are in root CLAUDE.md as iron rules; this mode body is the operational protocol.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "research this" / "find sources" / "look this up" or equivalent (see manifest §7.2).
- **§3 self-correction — unverified citation (auto-fire).** You catch yourself about to cite a source without verified full-text access. Procedure: emit the self-correction sentence `"wait... I haven't actually verified the full text is accessible, let me do that first."` then announce `Switching to [research mode] (invoked from [<prior mode>]).` and execute verification.
- **§3 self-correction — stale byline at write time (auto-fire).** Rendering a citation as `@id` for narrative use where the log entry's `retrieved_at` predates the current conversation's start **OR is missing/null entirely** (treat missing as stale). Emit `"wait... I'm about to render an author I haven't verified from the source, let me check the page."` then switch, re-verify, update `retrieved_at` to now.
- **§3 self-correction — stale byline at format time (auto-fire).** `[formatting mode]` pre-flight finds a log entry with missing or stale `retrieved_at`. Surface all stale entries as a grouped report and ask {{USER}} whether to re-fetch before rendering.
- **Unsourced-claim auto-fire.** A claim without a source surfaces in any prose mode (`[outlining]`, `[writing]`, `[editing]`). Switch here rather than improvising a source inline.

**Do not enter when:**
- {{USER}} pasted source text directly ("here's the passage, use it") — that's main-thread direct logging (see §Main-thread logging discipline below), not research mode entry.
- The citation is already in the log AND `retrieved_at` is fresh (post session start) AND byline was confirmed in this session AND `verification_status` is `"verified"` (not `"partial"`). Re-verification is required whenever ANY of those conditions fails, including the case where a `partial` entry is being promoted to load-bearing use.
- The claim can be honestly reframed without a source ("some scholars argue" → "I'll hedge this"). Research mode is for claims that need evidence; claims that can be restated without evidence may not need it.

## Iron Law

```
┌─────────────────────────────────────────────────────────────┐
│  NO LOG ENTRY WITHOUT §3(a) RELIABILITY + §3(b) FULL-TEXT   │
│  NO RENDERED CITATION WITHOUT FRESH retrieved_at            │
│  NO SUBSTITUTION: source you read IS source you log         │
└─────────────────────────────────────────────────────────────┘
```

**Verified means you read it.** Abstracts, summaries, citations inside review articles, publisher landing pages, and cataloging metadata do not count. A log entry whose full text you have not read is a fabrication regardless of how confident the metadata looks. Reading a later paper that discusses, cites, or summarizes the target work is not reading the target work. Each log entry corresponds to a source whose full text **you** opened — no substitution by a same-author paper, a successor paper, or a paper with a similar title. Default action on uncertainty is **reject**, not revise — revising is allowed only when you can re-open the source and produce the corrected span in one pass; otherwise reject and surface the gap.

## Steps

### Entry

1. **Announce entry.** First output of the turn:
   - **From explicit trigger**: `Switching to [research mode].`
   - **From auto-trigger (§3 self-correction)**: the self-correction sentence first (verbatim), then on the next line `Switching to [research mode] (invoked from [<prior mode>]).` The invoking-mode name is captured in the announcement itself so the round-trip state lives in the transcript, not in working memory.

1a. **False-positive check on entry.** On auto-trigger entry, re-check the trigger condition. If the check was wrong (e.g., `retrieved_at` is actually fresh — timezone mismatch, ISO parsing error, session-start race condition), do not silently abort. Announce `Switching back to [<prior mode>] — trigger was a false positive, retrieved_at is <timestamp>.` and return. The announcement is the audit trail; silent drop of an auto-trigger switch breaks round-trip state capture.

2. **Scope the work.** Name the claim(s) in one sentence each. For explicit triggers, ask {{USER}} if the scope isn't obvious. For auto-triggers, the scope is the specific claim that failed verification.

### Source-finder subagent dispatch (for 3+ independent sub-topics)

Dispatch `source-finder` subagents in parallel for three-plus independent sub-topics. For 1 or 2 sub-topics, do the research on the main thread — don't spawn a subagent for one or two topics. Never spawn source-finders outside `[research mode]`.

Source-finders read the existing log for context, verify each candidate against §3, write verified entries to their shard, and report back with logged ids, rejected sources, gaps, and alternative framings.

3. **Dispatch template (literal; do not improvise).** Use the template below as the `prompt` argument for each source-finder. Fill every placeholder. If a field is genuinely not applicable, write `none` rather than omitting it — an omitted field is silent and the finder will guess.

   ```
   Sub-topic: <one-sentence description of the sub-topic you are assigned>
   Supporting claim or question: <the specific claim or question this sub-topic serves in the paper>

   Paper context:
   - Working title: <title>
   - Overall argument: <one-sentence thesis>
   - Audience: <who this paper is for>

   Finder-id: <sfN, matching regex [a-z0-9-]+, typically sf1..sfN for a batch>
   Shard path (you write here): .claude/citations/working.<sfN>.json
   Main citation log path (read-only for context): <path to main log>

   Constraints:
   - Date range: <e.g., "post-2000" or "none">
   - Disciplines: <e.g., "linguistic anthropology, cultural anthropology" or "any">
   - Language: <e.g., "English-language scholarship only" or "none">
   - Sources to avoid: <specific authors, journals, or prior-logged sources, or "none">

   Schema (required reading before logging):
   <inline the full contents of ~/.claude/citations/schema.md here>
   ```

   Subagents run in isolated context and cannot read `~/.claude/citations/schema.md` themselves. Inlining the full schema is load-bearing — a summary will cause logging violations.

4. **Annotated-bib variant.** In `[annotated-bib]` projects, two fields differ; every other field (Finder-id, Shard path, Constraints, Schema) stays identical.
   - `Supporting claim or question:` → `Facet coverage: <what this facet of the topic encompasses>`
   - `Paper context:` block → carry the brief's *Scope statement* sub-sections verbatim (in-scope / out-of-scope / boundary cases) so the finder rejects out-of-scope candidates on the same criteria {{USER}} wrote. Include the topic's one-sentence statement as the first line of this block for orientation.
   - Per-facet entry target: `brief.target_entries / facet_count`, rounded up, bounded by the brief's per-facet cap. Dispatch one finder per approved facet; facets were locked in `[plan mode]`. Do not re-decompose mid-dispatch.

5. **Dispatch in parallel.** Always one message with N Agent tool calls. Never sequentially for a single batch. The parallel-dispatch property is load-bearing for throughput.

### Merge after dispatch

6. **Run the merge protocol from `~/.claude/citations/schema.md`.** Read each shard, validate entries, resolve any ID collisions against the main log and previously-merged shards (increment the `NNN` suffix), append validated entries to the main log, delete the shard file (unless held for failed-merge review per schema.md).

7. **On validation failure of any entry**, do not merge that shard. Follow the failed-shard protocol in schema.md and surface the problem to {{USER}}.

### Handling subagent-render-failed

8. **Retry from main thread.** Before treating a `subagent-render-failed` rejection as a gap, retry the fetch from the main thread: main-thread `Read` has richer PDF handling than subagents.
9. **On render success**, apply the full §3 protocol (render success satisfies §3(b) but NOT §3(a) — you still have to confirm reliability). Log directly (as an academic-researcher entry, `provisional_reference: null`, `draft_reference` set immediately to the invoking mode's current location).
10. **Only after your own retry fails**, treat as a gap and surface to {{USER}}.

### Main-thread direct logging discipline

When you log on the main thread (paste-in from {{USER}}, retry after subagent-render-failed, any main-thread read), the **four retrieval forcing fields are mandatory**, same as for dispatched source-finders (`~/.claude/agents/source-finder.md` step 5):

- `printed_page_observed`
- `tool_page_index`
- `verification_trace`
- `per_entity_locators` (when `exact_quote` enumerates multiple entities)

`location` must equal `printed_page_observed` for paginated sources (or the corresponding value for section-/chapter-/timestamp-keyed sources, per `~/.claude/citations/schema.md` §Verification fields). `pdf_page_offset` records the offset once per source. Reference-work sources (dictionaries, wordlists) use the list-shape in `~/.claude/citations/schema.md` §Reference-work shape; per-item locators carry verification in place of `verification_trace`.

### Byline re-verification (stale retrieved_at)

11. **If the trigger was stale byline at write time**, re-fetch the source, confirm `source.authors` matches the printed byline, AND re-read the cited passage (the `exact_quote` context) before updating `retrieved_at` to the current timestamp. Do not update `retrieved_at` on the strength of a re-download or a visual scan of page 1 alone — the update claims you re-read the evidence, not just re-opened the file.
12. **If the trigger was stale byline at format time**, surface every stale entry in one grouped report to {{USER}}. Per-entry choices: re-fetch and re-verify (preferred for web sources), accept as-is (acceptable for stable DOIs), treat as gap and return to `[editing mode]`. Offer shortcut options: "re-fetch all" / "accept all" / mixed. "Accept as-is" holds for this format pass only.

### Present and decide

13. **Aggregate finder reports** into one merged report for {{USER}}:
    - New citations logged: ids with one-line descriptions of what each supports.
    - Gaps: sub-topics where no usable source surfaced, or claims still unsupported.
    - Rejected sources: include when a gap remains in the area they were meant to cover, OR when the rejection is itself worth knowing (predatory journal worth naming, strong candidate blocked by a paywall {{USER}} might bypass, source that contradicts the paper's direction).
    - Alternative framings surfaced by any finder, if any.

14. **Do not autonomously dispatch a second round.** {{USER}} decides whether to dispatch again, reframe, paste manually, or accept the gap.

### Exit

15. **Announce return.** The round trip completes when one of:
    - (a) the source is logged, OR
    - (b) {{USER}} decides to skip the claim, reframe it, or accept the gap, OR
    - (c) {{USER}} asks to stay in `[research mode]` for follow-up work.

    On (a) and (b), announce `Switching back to [<prior mode>].` Read the prior mode from the entry announcement line (the `(invoked from [X])` clause). If no prior mode-switch line exists in the session, return to `[collaborative mode]`. On (c), no return announcement — stay in `[research mode]` until {{USER}} switches explicitly.

## Red Flags

If you catch yourself thinking any of the following, stop and check:

- *"The abstract is clear enough, I don't need the full PDF."* — No. §3(b) requires the full text. Abstracts do not count.
- *"This is a top-tier journal, so the source is fine without me reading it."* — No. §3(a) reliability gates admission; §4 *Read before citing* gates use. Both are required; neither is optional because of journal prestige.
- *"I can reconstruct the byline from the catalog page."* — No. Verify from the source itself (printed byline, editorial signature, group author per APA 7.21). Cataloging context, site ownership, and maintainer history are not bylines.
- *"`retrieved_at` is from this year, probably still fresh."* — Check against session start. If it predates the current conversation, it's stale — re-verify before rendering a narrative citation.
- *"The subagent dispatch message would be cleaner if I rephrased it."* — No. The template is literal. Improvising produces silent field loss.
- *"Schema.md is long; I'll summarize for the subagent."* — No. Inline the full contents. Subagents run in isolated context.
- *"Only one of the sub-topics really needs parallel research — I'll spawn one source-finder."* — That's single-topic research; do it on the main thread. Source-finder dispatch is for 3+ independent sub-topics.
- *"The subagent returned subagent-render-failed, that's a gap."* — Not yet. Retry from the main thread first. Main-thread Read has richer PDF handling.
- *"Two finders logged the same source with different NNN suffixes — I'll pick one and drop the other."* — Run the schema.md merge protocol. ID collisions have a defined resolution (increment the suffix).
- *"This is a quick fact-check, I'll just cite from memory."* — Citing from memory IS fabrication if the retrieval wasn't this session. If the citation is already in the log with fresh `retrieved_at`, use it; otherwise, re-read the source.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "The publisher is reputable, so the source is §3(a)-reliable without checking author credentials." | Publisher reputation admits the venue, not the claim. §3(a) also requires the author has relevant credentials for the specific claim. Check both. |
| "I read this source two sessions ago; I remember the gist." | The gist is not a citation. If `retrieved_at` predates this session, re-verify the byline and re-read the relevant passage before citing. "Remembering the gist" is the most common fabrication path. |
| "The abstract says the paper establishes X — good enough for a background citation." | Background citations are citations. §3(b) full-text applies regardless of citation weight. Abstracts are not full text. |
| "The source is paywalled but I found a preprint on the author's site — that's the same source." | Maybe, maybe not. Preprint and published version can differ materially (revised conclusions, added/removed sections, different page numbering). Verify the version you read matches the version you're citing. Note both if you're citing the preprint. |
| "The subagent's shard has an entry that fails schema validation on one field — I'll hand-fix the field and merge." | Do not hand-edit a shard to make it pass. Follow the failed-shard protocol in schema.md. Hand-fixing hides what the subagent actually produced and defeats the validation discipline. |
| "The dispatch template's `Sources to avoid` field is overkill for this topic — I'll omit it." | Omitting a field is silent. Write `none`. An omitted field means the finder guesses; a `none` means the constraint is deliberately absent. |
| "{{USER}} pasted a passage — I can log it without the four retrieval fields because it's not a subagent entry." | The main-thread direct logging discipline requires the same four retrieval forcing fields as subagent dispatch. `printed_page_observed`, `tool_page_index`, `verification_trace`, `per_entity_locators` (when applicable). No carve-out for main-thread. |
| "Render succeeded on retry, that satisfies §3 so I'll log." | Render success satisfies §3(b) — you have the full text. It does not satisfy §3(a) — you still have to confirm reliability (venue, author credentials, field-appropriate recency). Log only after both pass. |
| "The announcement `Switching to [research mode] (invoked from [<prior mode>])` is verbose — I'll just say `Switching to [research mode].`" | The `(invoked from [X])` clause IS the round-trip state capture. Dropping it means when you return, you have to guess the prior mode from working memory. Include it every time on auto-trigger. |
| "The auto-trigger fired but the verification will be quick — I'll do it inline without the mode switch." | Inline verification without the switch defeats the point of the mode. {{USER}} needs to see the switch in both directions; the announcement is a control point. Switch. |
| "{{USER}} said 'just verify this quickly' — that's permission to skip the dispatch procedure." | Verify quickly means verify; it doesn't mean skip §3. If single-topic, do it on the main thread per steps 8–10 (main-thread Read + full §3 protocol). If multi-topic, dispatch. "Quickly" doesn't lower the verification bar. |
| "The stale byline report is long; I'll surface the first few and ask about the rest later." | No. Surface every stale entry in one grouped report. Partial surfacing invites {{USER}} to accept-as-is without seeing the full scope. |
| "The review article gives the full citation for the underlying paper — I have the byline, year, DOI, I can log the underlying paper." | You have the review's rendering of the underlying paper. You have not read the underlying paper. Log the review (if you've read it); do not log the underlying work until you open it yourself. Metadata adopted from a secondary source is fabrication — the secondary may have transcribed it wrong, summarized wrong, or attributed wrong. |
| "The PDF rendered but the OCR is garbled / it's image-only — I can see the byline on page 1 so I'll log it." | Seeing page 1 is not reading the full text. If the body is unreadable, §3(b) fails. Report as render-failed and retry from the main thread (step 8); do not log on a partial render. |
| "The Google Books / JSTOR preview shows the chapter title and author — that's the byline." | Previews crop, reorder, and sometimes misattribute. Byline verification requires the printed byline on the chapter's first page of full text. Preview surfaces do not count as the source. |
| "I verified this earlier in our work together — `retrieved_at` is old but I remember the check." | The check is the `retrieved_at` timestamp and the byline entry in the log. Your memory of having checked does not update the log, and "our work together" across sessions is not one session. If `retrieved_at` predates session start, re-verify and update the timestamp; no exceptions for "I remember." |
| "CrossRef / DOI.org returned author metadata — that's authoritative, I can populate `source.authors` from it." | DOI metadata is cataloging context (per §3's Byline rule and §8 Moment 1). The byline is what the source itself prints on page 1 (or equivalent: editorial signature, group author per APA 7.21). Use DOI metadata only as a cross-check, never as the primary source for `source.authors`. |
| "The successor paper (same author, later year) discusses this work extensively — I can log the earlier paper without re-opening it." | Reading the successor is not reading the earlier work. Open the earlier paper's full text. Each log entry corresponds to the source YOU opened. |
| "The schema.md is 400 lines — I'll inline the parts that matter for this dispatch and drop the examples." | The subagent cannot read schema.md on its own. "Parts that matter" is your guess; schema.md decides what's load-bearing. Inline it verbatim, byte-for-byte, including the examples. Summarization here is where the validation discipline breaks. |
| "Dispatching finder 1 first lets me dedupe before spawning 2 and 3 — more efficient." | Dedup is the merge protocol's job (ID collision resolution in schema.md). Sequential dispatch defeats throughput discipline; duplicates are cheap to resolve at merge. One message, N parallel Agent calls. |
| "One facet turned out broader than planned — I'll split it into two finder dispatches to cover it." | Facets were locked in `[plan mode]` with {{USER}}'s approval. Splitting mid-dispatch changes the brief's target-entries math and breaks the per-facet cap. Return to `[plan mode]` to re-decompose; do not split silently. |
| "The validator is rejecting a shard on a field that's obviously fine (e.g., a URL with a tracking parameter) — I'll strip the param and merge." | Any hand-edit to a shard before merge is hand-fixing. Follow the failed-shard protocol in schema.md; it's the only path. If the validator is genuinely wrong, fix the validator in a separate change. Do not hand-edit the shard to make it pass. |
| "This source isn't paginated (podcast, webpage, video), so `printed_page_observed` doesn't apply." | The field name is shorthand; the discipline is "record the stable locator you observed." For non-paginated sources, record the section / chapter / timestamp / paragraph-id per schema.md §Verification fields. The field is mandatory; "doesn't apply" is not an answer — if you can't produce a stable locator, you can't cite the source. |
| "`exact_quote` has one main entity and a passing mention of another — I'll treat as single-entity and skip `per_entity_locators`." | If the citation will be used to support claims about either entity, both need locators. When in doubt, populate `per_entity_locators`; over-population is cheap, under-population is a fabrication path. |
| "`(invoked from [writing mode])` is awkward — I'll write `from [writing mode]` or put it on its own line." | The exact parenthetical form is what the exit step parses on return (step 15). Any reformatting breaks the round-trip state capture. Use `(invoked from [X])` verbatim, same line as the switching sentence. |

## Quick Reference

```
ENTRY:
  Explicit:       Switching to [research mode].
  Auto-trigger:   <self-correction sentence verbatim>
                  Switching to [research mode] (invoked from [<prior mode>]).

VERIFY every candidate via §3:
  (a) Reliability — peer review / credentialed author / appropriate recency
  (b) Full-text   — readable PDF or rendered HTML, not abstract / paywall / citation-of

DISPATCH (3+ sub-topics):
  Parallel Agent tool calls in one message
  Literal template, every field filled (use "none" not omission)
  Inline full schema.md contents

LOG (main thread direct):
  Four retrieval forcing fields required:
    - printed_page_observed
    - tool_page_index
    - verification_trace
    - per_entity_locators (when exact_quote has multiple entities)
  location = printed_page_observed (paginated sources)

MERGE: per schema.md protocol. Hand-fix forbidden.

SUBAGENT-RENDER-FAILED: retry from main thread BEFORE calling it a gap.

EXIT (announce return):
  (a) source logged       → Switching back to [<prior mode>].
  (b) user skips/reframes → Switching back to [<prior mode>].
  (c) user asks to stay   → no return announcement; stay until explicit switch.
```

## What this mode does NOT do

- **Draft prose.** The mode produces log entries, not sentences. Drafting belongs in `[writing mode]`.
- **Restructure the argument.** If research reveals the argument needs reshaping, announce the return to the invoking mode and surface the structural question there (or prompt {{USER}} to switch to `[refining mode]`).
- **Auto-dispatch a second round.** {{USER}} decides whether to re-dispatch after seeing the merged report.
- **Generate APA strings.** Formatting is `[formatting mode]`'s job; research mode emits log entries with Pandoc IDs.
- **Fabricate under deadline pressure.** "I'll just cite from memory to keep moving" is the failure mode this mode exists to prevent, not an acceptable shortcut.

## Exit Gates

**Allowed transitions (from research):**
- → `[<prior mode>]` (read from `(invoked from [X])` clause in the entry announcement). This is the standard exit on condition (a) source logged or (b) {{USER}} skips/reframes/accepts gap. Use `Switching back to [<prior mode>].`
- → `[collaborative mode]` as default return when no prior mode-switch line exists in the session. Use `Switching back to [collaborative mode].`
- **Stay in research** on condition (c) — {{USER}} asks for follow-up work. No return announcement; stay until {{USER}} switches explicitly.

**Forbidden transitions:**
- → `[writing mode]` direct. Even if research surfaces prose-ready material, return to the invoking mode first and let {{USER}} direct the next step. Research does not promote itself to drafting.
- → `[formatting mode]` direct. Unreachable from research; formatting requires edit-complete gate.
- → `[plan mode]` direct. If research surfaces that planning was wrong, return to the invoking mode and surface the problem there.
- → Second `[research mode]` dispatch autonomously. {{USER}} authorizes second rounds, not the mode itself.

## See also

- `CLAUDE.md §3` — source verification iron rules (non-negotiable). The ground truth for this mode's reliability and full-text checks.
- `CLAUDE.md §4` — synthesis integrity; §4 *Read before citing*, *Paraphrase must match scope*, *Preserve attribution*, *Quote verbatim*. Applied at logging time (this mode) and at refining/editing time (downstream modes).
- `CLAUDE.md §7.3` — implicit/auto-fire trigger definitions (source of truth).
- `CLAUDE.md §7.4` — mode-to-mode gate table.
- `CLAUDE.md §8.1` — citation log schema (Moment 1).
- `~/.claude/citations/schema.md` — full entry structure, enum values, ID format, staleness rules, merge protocol, verification fields, reference-work shape.
- `~/.claude/agents/source-finder.md` — subagent definition; the four retrieval forcing fields originate at its step 5.
