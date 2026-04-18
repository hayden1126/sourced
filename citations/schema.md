# Citation log schema

Single source of truth for the structure of entries in any citation log (`<draft>.citations.json` or `.claude/citations/working.citations.json`). Semantic rules for when to use each value live in the agent files (`academic-researcher.md`, `source-finder.md`); this file defines structure, allowed values, and ID format only.

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
  "added_at": "2026-04-17T14:23:00Z"
}
```

## Allowed enum values

- `verification_status`: `"verified"` | `"partial"`. Never any other value. If verification fails, reject the source rather than logging.

## Timestamp format

- `added_at`: ISO 8601 in UTC, seconds precision, with trailing `Z`. Example: `2026-04-17T14:23:00Z`. No fractional seconds, no local-time offsets.

## Reference fields

Two fields track where a citation lives over its lifecycle:

- `provisional_reference`: set by source-finder at logging time, format `"subtopic:<name>"` where `<name>` is the sub-topic the source-finder was assigned. Provenance only. Never rewritten, never cleared. Always present on entries created during research.
- `draft_reference`: set lazily by academic-researcher the first time the citation is placed into an outline paragraph or draft prose. Format: section-level while the outline is still section-scoped (e.g., `"section:counterargument"`); paragraph-level once specific paragraph positions exist (e.g., `"paragraph:3.2"`, meaning section 3 paragraph 2). Start at section-level during `[drafting mode]`; narrow to paragraph-level during `[refining mode]` or `[writing mode]` once the outline resolves to specific paragraphs. `null` until first placed.

Entries written directly by academic-researcher during drafting (no source-finder involvement) may set `draft_reference` immediately and leave `provisional_reference` as `null`.

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

Merge protocol for academic-researcher:

1. Read each shard file in turn.
2. For each entry, validate against the schema (required fields present, enum values legal, `exact_quote` and `surrounding_context` non-empty).
3. Resolve ID collisions against both the main log and any shards already merged in this pass: if the id is already taken, increment the `NNN` suffix to the next free value.
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
