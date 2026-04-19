# Citation log schema

Single source of truth for the structure of entries in any citation log (`<draft>.citations.json` or `.claude/citations/working.citations.json`). Semantic rules for when to use each value live in the project's `CLAUDE.md` and in `source-finder.md`; this file defines structure, allowed values, and ID format only.

## Entry structure

Each in-text citation is one entry. Same source cited three times = three entries, one per instance.

```json
{
  "id": "smith-2010-001",
  "source": {
    "authors": ["Smith, Jane A."],
    "year": 2010,
    "title": "Title of Work",
    "publication": "Journal Name, Publisher, or 'Book'",
    "volume_issue_pages": "42(3), 12-34",
    "doi_or_url": "https://doi.org/..."
  },
  "location": "specific location inside the source: page, section, chapter, paragraph, timestamp",
  "exact_quote": "verbatim text from the source that supports the claim",
  "surrounding_context": "1-2 verbatim sentences immediately before and after the exact quote",
  "context_description": "what the author is arguing in this passage and why it supports the claim",
  "claim_supported": "the specific claim in the draft this citation is cited for",
  "citation_string": "(Smith, 2010, p. 42)",
  "provisional_reference": "subtopic:animacy-grammar",
  "draft_reference": null,
  "verification_status": "verified | partial",
  "retrieval": "URL, PDF path, library access, or 'pasted by {{USER}}'",
  "retrieved_at": "2026-04-17T14:18:00Z",
  "added_at": "2026-04-17T14:23:00Z"
}
```

## Author-field provenance

`source.authors` must reflect what the source itself states, not what the cataloging context implies. Three cases:

- **Byline present.** Use the byline as printed (author name, editor, "by X"). Normalize to APA surname-first format.
- **No byline, institutional source.** Use the group author per APA 7.21 (the organization, project, or site name as it appears on the page). Do not infer an individual author from site ownership, maintainer history, or publication patterns.
- **No byline, non-institutional source.** Treat as anonymous per APA 9.12 (title moves to the author position in References). Do not assign a person.

If you assign an individual author whose name is not printed in or signed on the source itself (initials, editorial signature, "compiled by"), record the evidence in a new `author_evidence` field with the verbatim text and its location on the page (e.g., `"author_evidence": "signed 'WL' at end of page"`). Absence of this field on an entry with a named individual author asserts that the byline is printed verbatim somewhere on the source.

`source.authors` is also the source of truth for author names rendered into prose. `[formatting mode]` (CLAUDE.md §7) reads `source.authors` to render every inline citation; if the byline is wrong here, every rendered citation that resolves through this entry is wrong. Verify it once at logging time and re-verify it any time the entry is touched in a later session (see `retrieved_at` below for the re-verification trigger).

## `citation_string` is informational

`citation_string` is a portability hint and a grep target; it is not load-bearing. The authoritative rendering of an inline citation comes from `source.authors` + `source.year` resolved per the project's `style.md` in `[formatting mode]` (CLAUDE.md §7). Setting `citation_string` to an APA-7 string at logging time is fine and recommended for portability across projects with different styles, but downstream rendering does not depend on it. `[formatting mode]` does not read this field during normal operation.

## Allowed enum values

- `verification_status`: `"verified"` | `"partial"`. Never any other value. If verification fails, reject the source rather than logging.
  - `"verified"`: you have read the full work yourself.
  - `"partial"`: {{USER}} pasted the target passage plus enough surrounding text to populate `surrounding_context`, but the rest of the work is not accessible. Permitted only when `claim_supported` is strictly contained within `exact_quote` (a direct restatement of the pasted passage, not an inference from it or a generalization of it). Partial entries may not anchor load-bearing claims; if the paper's argument depends on the claim, treat it as a gap rather than logging partial.

## Timestamp format

- `added_at`: ISO 8601 in UTC, seconds precision, with trailing `Z`. Example: `2026-04-17T14:23:00Z`. No fractional seconds, no local-time offsets. Set when the entry is first written to the log; never updated.
- `retrieved_at`: ISO 8601 in UTC, same format as `added_at`. Marks when the source was actually fetched and read for this entry, distinct from when the entry was logged. For sources read in the same session as logging, the two timestamps are typically minutes apart. For entries created from text {{USER}} pasted, `retrieved_at` is the time of the paste. Update `retrieved_at` whenever the source is re-fetched and re-verified in a later session (e.g., during an `[editing mode]` byline recheck or a `[formatting mode]` staleness prompt).

Every entry must carry both timestamps. Legacy entries logged before this field was introduced have no `retrieved_at` and are treated as stale on first encounter; see "Staleness" below.

## Staleness

Web pages mutate. The byline, year, title, and even the verbatim text can change between sessions without notice. `retrieved_at` exists to make staleness visible.

- An entry is **fresh** if `retrieved_at` is within 90 days of the current date.
- An entry is **stale** if `retrieved_at` is older than 90 days, or if `retrieved_at` is missing entirely (legacy entries).
- The 90-day threshold applies to web pages, preprints, and other mutable sources. For published journal articles, books, and stable PDFs accessed by DOI, staleness is informational only: the underlying work doesn't change, but verifying that you still have access (and that `source.authors` still matches what you'd extract today) is cheap insurance.

Stale entries are not errors at logging time; they only matter when the entry is touched again. `[editing mode]` (CLAUDE.md §7, byline recheck) and `[formatting mode]` (CLAUDE.md §7, pre-flight) both surface staleness and ask {{USER}} how to proceed (re-fetch and update, accept as-is, or treat the citation as a gap). Re-fetching and re-verifying updates `retrieved_at` to the new timestamp; `added_at` is never updated.

## Reference fields

Two fields track where a citation lives over its lifecycle:

- `provisional_reference`: set by source-finder at logging time, format `"subtopic:<name>"` where `<name>` is the sub-topic the source-finder was assigned. Provenance only. Never rewritten, never cleared. Always present on entries created during research.
- `draft_reference`: set lazily by academic-researcher the first time the citation is placed into an outline paragraph or draft prose. Format: section-level while the outline is still section-scoped (e.g., `"section:counterargument"`); paragraph-level once specific paragraph positions exist (e.g., `"paragraph:3.2"`, meaning section 3 paragraph 2). Start at section-level during `[outlining mode]`; narrow to paragraph-level during `[refining mode]` or `[writing mode]` once the outline resolves to specific paragraphs. `null` until first placed.

Entries written directly by academic-researcher (no source-finder involvement) may set `draft_reference` immediately and leave `provisional_reference` as `null`.

## ID format

`lastname-year-NNN` where:
- `lastname` is the first author's surname as it appears in the APA References entry, lowercased, no spaces.
- `year` is the four-digit publication year.
- `NNN` is a zero-padded incrementing suffix per source, starting at `001`.

Same source cited three times: `smith-2010-001`, `smith-2010-002`, `smith-2010-003`.

## Parallel dispatch shards

When academic-researcher dispatches multiple source-finders in parallel, each finder writes to its own shard file to avoid concurrent-write contention and ID collisions.

- Shard path format: `.claude/citations/working.<finder-id>.json`, where `<finder-id>` is a short unique token assigned by the parent at dispatch time (e.g., `sf1`, `sf2`, `sf-animacy`).
- Finders only write to their assigned shard path. They never append to the main log directly.
- After all finders in a batch return, academic-researcher merges shards into the main log (`<draft>.citations.json` or `.claude/citations/working.citations.json`) in one pass.

Merge protocol for academic-researcher. Do not start the merge until every finder in the batch has returned.

1. Read each shard file in ascending `<finder-id>` order (lexicographic sort of the filenames). If a shard is not valid JSON on read, treat it as a failed shard per the failure handling below; do not attempt to repair a partial or malformed shard.
2. For each entry, validate against the schema (required fields present, enum values legal, `exact_quote` and `surrounding_context` non-empty).
3. Resolve ID collisions against both the main log and any shards already merged in this pass: if the id is already taken, increment the `NNN` suffix to the next free value. Because shards are read in `<finder-id>` order, the lowest-id shard owns its original ids and higher-id shards renumber on collision. A rerun of the same batch must produce the same id assignments.
4. Append validated entries to the main log. If the main log file does not yet exist (first dispatch batch, no prior log), create it as an empty JSON array `[]` first, then append.
5. Delete the shard file after successful merge. If the shard is being held pending a failed-merge review, do not delete it; see failure handling below.

If validation fails on any entry, do not merge that shard. Surface the specific failing entry (or entries) to {{USER}} with the validation reason and ask how to proceed. Three resolution paths:

1. **Fix in place.** {{USER}} hand-edits the shard to correct the entry, then tells academic-researcher to retry the merge.
2. **Drop and merge rest.** {{USER}} says which entries to drop; academic-researcher removes them from the shard and retries the merge.
3. **Abandon.** {{USER}} says to drop the shard entirely. academic-researcher immediately renames the shard to `working.<finder-id>.failed.<ISO-8601-timestamp>.json` and records the reason {{USER}} gave alongside it (one-line comment in a sibling `<shard>.reason` file or inline at the top of the renamed shard). This is the clean abandon path.

Until the shard is either successfully merged (deleted) or explicitly abandoned (renamed to `.failed.<timestamp>`), the shard stays at its original path. Before dispatching a new batch, academic-researcher checks `.claude/citations/` for any pre-existing `working.<finder-id>.json` files:

- If a shard exists for a finder-id academic-researcher is about to reuse, rename the old shard to `working.<finder-id>.failed.<ISO-8601-timestamp>.json` and surface it to {{USER}} before dispatching. This is the catch-all rename for when a reuse collision happens before {{USER}} has explicitly abandoned the old shard.
- Abandoned failed shards stay under the `.failed.<timestamp>` name as a record. They are never auto-deleted.

## Additions

Additional fields are allowed when they help (scholarly counterarguments, topic tags, follow-up questions). Never remove fields from this schema.
