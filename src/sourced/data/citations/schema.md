# Citation log schema

Single source of truth for the structure of entries in any citation log (`sources/<draft>.citations.json` or `sources/working.citations.json`). Semantic rules for when to use each value live in the project's `CLAUDE.md` and in `source-finder.md`; this file defines structure, allowed values, and ID format only.

## Entry structure

Each in-text citation is one entry. Same source cited three times = three entries, one per instance.

```json
{
  "id": "smith-2010-001",
  "source": {
    "authors": ["Smith, Jane A."],
    "year": 2010,
    "title": "Title of Work",
    "publication": "Journal Name, 'Book: Publisher', or venue per §Source type",
    "volume_issue_pages": "42(3), 12-34",
    "doi_or_url": "https://doi.org/...",
    "reliability_basis": {
      "venue_type": "one of the nine §Reliability basis venue classes",
      "venue_basis": "one named checkable fact about the venue: publisher, index membership, sponsoring society",
      "author_credentials": "credential evidence copied verbatim plus where it was observed, or 'group author: <standing>' / 'none stated'"
    }
  },
  "location": "specific location inside the source: page (canonical 'p. N' / 'pp. N-M' form), section, chapter, paragraph, timestamp",
  "exact_quote": "a single contiguous verbatim span copied from the rendered source at the location this entry records (see §Verification fields); never a paraphrase, synthesis across passages, or reconstruction from memory",
  "surrounding_context": "a single contiguous verbatim span from the same rendered view as exact_quote: the quote plus 1-2 sentences immediately before and after it; never a summary, an availability note, or any other text not printed in the source (see §Verification fields, context_trace)",
  "context_description": "what the author is arguing in this passage and why it supports the claim",
  "claim_supported": "the specific claim in the draft this citation is cited for",
  "citation_string": "(Smith, 2010, p. 42)",
  "provisional_reference": "subtopic:animacy-grammar",
  "draft_reference": null,
  "verification_status": "verified | partial",
  "retrieval": {
    "source_path": "URL, PDF path, library access, or 'pasted by {{USER}}'",
    "access_mode": "rendered-html | pdf-render | ocr-fulltext | snippet (see §Verification fields; snippet never reaches verified)",
    "printed_page_observed": "p. 42",
    "tool_page_index": 56,
    "pdf_page_offset": 14,
    "verification_trace": {
      "first_20": "first 20 chars of exact_quote",
      "last_20": "last 20 chars of exact_quote"
    },
    "context_trace": {
      "first_20": "first 20 chars of surrounding_context",
      "last_20": "last 20 chars of surrounding_context"
    }
  },
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

`source.authors` is also the source of truth for author names rendered into prose. `[formatting mode]` (CLAUDE.md §7) reads `source.authors` to render every inline citation; if the byline is wrong here, every rendered citation that resolves through this entry is wrong. Logging-time verification is recorded by the byline rules above (`author_evidence` when a name is not printed verbatim); re-verification in a later session is recorded by updating `retrieved_at` (see below for the trigger) and, when `[editing mode]` Pass 2 fires, overwriting `retrieval.verification_trace` and `retrieval.context_trace` from the re-opened source. An entry touched in a later session without a fresh `retrieved_at` is unverified regardless of what was checked silently.

## Reliability basis

`source.reliability_basis` externalizes the §3(a) reliability judgment the way the `retrieval.*` fields externalize §3(b): a discipline-level rule ("confirm reliability") is rationalized past by logging agents; a field conspicuously missing or boilerplate is not. Required on every entry with `verification_status: "verified"`, including reference-work list-shape entries (reliability is a property of the source, not of the quote shape, so the list-shape exemption below does not extend here). Not required on `"partial"` entries: {{USER}} supplied the passage, and the reliability call on a pasted source is his.

- `reliability_basis.venue_type`: string, exactly one of `"peer-reviewed-journal"` (refereed journal or refereed conference proceedings), `"academic-press-book"` (university or academic-press monograph, or a chapter in an edited academic volume), `"trade-press-book"` (commercial-publisher nonfiction), `"preprint"` (arXiv, SSRN, bioRxiv, or similar unrefereed server), `"government-or-standards"` (agency report, statistical office, standards body), `"reference-work"` (dictionary, encyclopedia, gazetteer, handbook), `"journalism"` (edited newsroom outlet), `"primary-source"` (historical document, archival material, original dataset), `"grey-literature"` (working paper, thesis, NGO or white paper, attributed expert blog). Never any other value; there is no `"other"` and no `"unknown"`. Peer-review status is a property of the venue class, not a separate field: classifying a source as `"peer-reviewed-journal"` asserts refereeing exists, and classes where review is not the norm carry that fact in the class itself. A venue that fits no class has failed the reliability check; reject rather than log a guessed classification.
- `reliability_basis.venue_basis`: string. At least one named, externally checkable fact about the venue: publisher, index or database membership, sponsoring society, or institutional standing (e.g., `"published by Cambridge University Press"`, `"indexed in DOAJ"`, `"flagship journal of the Linguistic Society of America"`). Generic vouching with no named fact (`"reputable journal"`, `"well-known publisher"`) fails merge validation. For `"grey-literature"`, this field must additionally state why this instance clears the §3(a) bar despite the venue class.
- `reliability_basis.author_credentials`: string. Credential evidence copied verbatim, plus where it was observed (e.g., `"'Department of Linguistics, University of Colorado' printed under the byline, p. 1"` or `"'Professor of Economics, MIT' per https://economics.mit.edu/people/smith"`). A credential you cannot quote from a location you can name is a judgment from memory. Two escape literals are legal: `"group author: <organization's standing>"` (only when `source.authors` carries a group author per §Author-field provenance) and `"none stated"` (venue-only reliability; surfaced in the merge report). Generic vouching (`"credible expert"`, `"respected scholar"`) fails merge validation.

Field-appropriate recency is deliberately not a sub-field. Its inputs are already logged artifacts (`source.year` on every entry; the dispatch template's date-range constraint, filled or `none`), and a forced "recency ok" value would be a ritual counter, satisfiable by the same silent assent this object exists to remove.

`reliability_basis` describes the source, not the retrieval event. Derive it once per source and reuse it verbatim across that source's entries (the `pdf_page_offset` pattern). It is set when the source is first verified and is not re-derived on staleness re-fetch or `[editing mode]` Pass 2: a re-fetch updates `retrieved_at` and overwrites `verification_trace` and `context_trace`, and leaves `reliability_basis` unchanged. Re-derive it only when re-verification changes `source.publication` or `source.authors` (the old basis then describes a source the entry no longer cites); a venue that has visibly changed (domain moved, journal delisted) is surfaced to {{USER}}, not silently rewritten. Entries logged before this field existed carry no `reliability_basis` and are grandfathered until the source is next re-opened for any re-verification; that first re-open populates the field, once. Never populate it from memory, and never on an "accept as-is" staleness resolution: if the source was not re-opened, the field stays absent.

`venue_type` is a reliability classification, not a bibliographic type. The bibliographic type lives in the optional `source.type` field (§Source type below); when it is absent, the CSL-JSON emitter infers `type` from `source.publication`. The emitter never reads `reliability_basis` in either case: any fact the renderer needs (publisher, proceedings name, repository) belongs in `source.publication`, not only in `venue_basis`.

## Source type (optional)

Optional string field `source.type`: the bibliographic class of the source. When present, the CSL-JSON emitter uses it as the CSL `type` directly and skips publication-string inference (see `csl-json-emitter.md` §Source-type inference, rule 0). Exactly one of eight values: `"article-journal"`, `"book"`, `"chapter"`, `"webpage"`, `"paper-conference"`, `"report"`, `"thesis"`, `"dataset"`. Never any other value and never free text; a source that fits none of the eight stays untyped and takes the inference path. Absent is legal on every entry: absence means the emitter infers `type` from `source.publication` exactly as it did before this field existed.

Set it at logging time when the class is evident from the rendered artifact (a proceedings header, a report series page, a thesis title page, a dataset landing page). The four values `"paper-conference"`, `"report"`, `"thesis"`, and `"dataset"` are the reason the field exists: they have no inference route, and without an explicit type they render as `article-journal` through the emitter's fallback, or worse, silently through rule 1 when `volume_issue_pages` is set. Leave the field absent when unsure; a wrong type renders worse than no type.

`source.type` is per-source, like `reliability_basis`: derive it once and reuse it verbatim across that source's entries. Present on some siblings and absent on others is legal (the emitter reads the value from any sibling that carries it); two different non-absent values on siblings hard-fail the merge (step 2 below).

What `source.publication` holds, per class: the journal name (`"article-journal"`), `"Book: <publisher>"` (`"book"`; never the bare string `"Book"`, which renders with no publisher), `"In <book title>, edited by <editors>, <publisher>"` (`"chapter"`), the site name (`"webpage"`), the proceedings or conference name (`"paper-conference"`), the issuing institution or agency (`"report"`), the degree-granting institution (`"thesis"`), the repository or distributor (`"dataset"`). The emitter parses `source.publication` under the resolved class's rules whether the class was explicit or inferred, so a typed entry with a malformed publication string still renders badly; the publication parseability check (merge step 2 below) surfaces the malformed shapes observed in the field.

## Verification fields

Six sub-fields inside `retrieval` (all but the derived `pdf_page_offset`) force externalized, validator-checkable evidence that `exact_quote`, `surrounding_context`, and `location` are grounded in the rendered source. These exist because discipline-level rules ("verify," "cross-check") are rationalized past by logging agents; a field conspicuously missing or malformed is not.

- `retrieval.printed_page_observed` — string. The printed page number visible on the rendered page header/footer, OR the literal string `"not visible"` if the header/footer does not show one (scanned image, missing header, digital-only). Verbatim applies to the number, not the typography around it: read the page number off the rendered view (Arabic or Roman), then record it in canonical page form, `"p. N"` for a single page, `"pp. N-M"` for a range (the form every exemplar in this file shows). A page number you did not see on the rendered view is not observed: never adopt one from a search index, catalog record, or citing work. Required on every entry whose source is paginated.
- `retrieval.tool_page_index` — integer. The tool-reported page index (PDF page number, sequential page in a reader). Recorded alongside `printed_page_observed` so the offset between them is explicit.
- `retrieval.pdf_page_offset` — integer. The difference between `tool_page_index` and `printed_page_observed`, recorded once per source. Subsequent entries from the same source reuse the recorded offset rather than recomputing it.
- `retrieval.verification_trace` — object. `{"first_20": "...", "last_20": "..."}` — the first 20 and last 20 characters of `exact_quote` as they appeared in the rendered view, verbatim. Lets the parent's merge-protocol validator spot-check that the span is a real copy, not a reconstruction. Required on every entry with `verification_status: "verified"` whose `exact_quote` is not in list-shape (reference works, see below).
- `retrieval.context_trace`: object. `{"first_20": "...", "last_20": "..."}`: the first 20 and last 20 characters of `surrounding_context` as they appeared in the rendered view, verbatim. Mirrors `verification_trace` so the parent's spot-check can confirm the context against the re-opened source, not just the quote; the merge-layer check on `surrounding_context` itself is the containment hard-fail (merge step 2: string-shape `exact_quote` must appear verbatim inside `surrounding_context`). Required on every entry with `verification_status: "verified"` whose `exact_quote` is not in list-shape (same condition as `verification_trace`; the list-shape exemption in §Reference-work shape extends here). Not required on `"partial"` entries at the schema level; the main-thread logging discipline (`docs/modes/research.md`) still populates it from the paste. Entries logged before this field existed carry no `context_trace` and are grandfathered until the source is next re-opened for any re-verification; that first re-open populates the field, once.
- `retrieval.access_mode`: string, exactly one of `"rendered-html"` (the full work as rendered HTML in the fetch or browser view), `"pdf-render"` (the full work as a readable PDF or page-image reader, text layer or rendered page images, opened page by page), `"ocr-fulltext"` (the complete OCR text of a scanned work, for example an archive.org full-text view: the whole body is readable but page furniture may not survive), or `"snippet"` (search-inside or keyword-in-context windows returned by a search index; not full text). Never any other value. Required on every entry with `verification_status: "verified"`; not required on `"partial"` entries ({{USER}} supplied the passage, and the access path on a pasted source is his). `"snippet"` is structurally incompatible with `"verified"`: a snippet shows a match, not the work, and §3(b) full-text access has not happened; the merge protocol hard-fails the combination. `"ocr-fulltext"` reaches `"verified"` (the full text was read) but is surfaced in the merge report, because printed page numbers often do not survive OCR: on `"ocr-fulltext"` entries, `printed_page_observed` must come from a page marker visible in the OCR text itself or be `"not visible"`, never from a search index, catalog record, or citing work. Entries logged before this field existed carry no `access_mode` and are grandfathered until the source is next re-opened for any re-verification; that first re-open populates the field, once.
- `retrieval.per_entity_locators` — array of `{entity: string, locator: string}`. Required when `exact_quote` enumerates multiple named entities, terms, or claims. Each object records the rendered locator (URL anchor, page, section) where that specific entity is attested. Forces the multi-entity scope check.

`location` must equal `retrieval.printed_page_observed` for paginated sources (or the corresponding value for section-/chapter-/timestamp-keyed sources). Both fields carry the canonical `"p. N"` / `"pp. N-M"` form. The merge-protocol validator compares the page token, normalizes cosmetic form differences to canonical on merge, and rejects entries where the tokens disagree.

## `citation_string` is informational

`citation_string` is a portability hint and a grep target; it is not load-bearing. The authoritative rendering of an inline citation comes from `source.authors` + `source.year` resolved per the project's `config/style.md` in `[formatting mode]` (CLAUDE.md §7). Setting `citation_string` to an APA-7 string at logging time is fine and recommended for portability across projects with different styles, but downstream rendering does not depend on it. `[formatting mode]` does not read this field during normal operation.

## Reference-work shape for `exact_quote`

For sources where no prose can be quoted verbatim (dictionaries, wordlists, gazetteers, structured glossaries), `exact_quote` may be a JSON array of objects instead of a string:

```json
"exact_quote": [
  {"headword": "Ma'heo'o", "definition": "sacred mystery; sacred power", "locator": "entry M, p. 312"},
  {"headword": "Voestaa'e", "definition": "white woman (proper name)", "locator": "entry V, p. 489"}
]
```

Each item's fields are verbatim from the source. When `exact_quote` is in list-shape, `retrieval.verification_trace` and `retrieval.context_trace` are not required (the locators inside each item serve the same forcing function), but `retrieval.per_entity_locators` is also not required (the list itself carries locators). Whitespace, a paraphrase, a descriptive summary, or a placeholder is never an acceptable substitute for the list-shape; if you cannot populate the list, reject per section 3.

## Correct-entry exemplar

A valid entry under the new schema looks like this. Every externalized verification field is populated; `location` equals `retrieval.printed_page_observed`; `access_mode` records the rendered view the copies came from; multi-entity entries carry per-entity locators.

```json
{
  "id": "smith-2010-001",
  "source": {
    "authors": ["Smith, Jane A."],
    "year": 2010,
    "title": "Title of Work",
    "publication": "Journal Name",
    "volume_issue_pages": "42(3), 12–34",
    "doi_or_url": "https://doi.org/10.xxxx/yyyy",
    "reliability_basis": {
      "venue_type": "peer-reviewed-journal",
      "venue_basis": "published by the American Psychological Association; indexed in Scopus",
      "author_credentials": "'Department of Psychology, University of Toronto' printed under the byline, p. 12"
    }
  },
  "location": "p. 24",
  "exact_quote": "inhibitory control, the cognitive capacity to suppress a dominant response in favor of a context-appropriate alternative",
  "surrounding_context": "Subjects high on measures of executive function consistently outperform controls on tasks requiring inhibitory control, the cognitive capacity to suppress a dominant response in favor of a context-appropriate alternative. This effect replicates across age groups.",
  "context_description": "Smith is defining inhibitory control as part of her executive-function framework",
  "claim_supported": "inhibitory control is the capacity to suppress a dominant response",
  "citation_string": "(Smith, 2010, p. 24)",
  "provisional_reference": "subtopic:executive-function",
  "draft_reference": null,
  "verification_status": "verified",
  "retrieval": {
    "source_path": "https://doi.org/10.xxxx/yyyy",
    "access_mode": "pdf-render",
    "printed_page_observed": "p. 24",
    "tool_page_index": 38,
    "pdf_page_offset": 14,
    "verification_trace": {
      "first_20": "inhibitory control, ",
      "last_20": "ropriate alternative"
    },
    "context_trace": {
      "first_20": "Subjects high on mea",
      "last_20": "s across age groups."
    }
  },
  "retrieved_at": "2026-04-20T09:00:00Z",
  "added_at": "2026-04-20T09:03:00Z"
}
```

A multi-entity entry additionally carries `retrieval.per_entity_locators` — one object per named entity with its own `locator` field.

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

**Precedence.** Two thresholds fire, inner before outer. The inner bound is per-session: any entry touched for the first time in a new conversation is stale on that touch (CLAUDE.md §4 item 3) regardless of `retrieved_at` age — this catches drift across session boundaries. The outer bound is the 90-day rule above, blocking for mutable sources (web pages, preprints) and advisory for stable ones (DOIs, published articles, books); it catches drift within a single long-running conversation that the session-boundary check alone would miss. Both can fire on the same entry; when they do, surface the entry in a single grouped staleness prompt rather than two separate ones, matching `[formatting mode]`'s pre-flight pattern (CLAUDE.md §7).

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
- After all finders in a batch return, academic-researcher merges shards into the main log (`sources/<draft>.citations.json` or `sources/working.citations.json`) in one pass.

Merge protocol for academic-researcher. Do not start the merge until every finder in the batch has returned.

1. Read each shard file in ascending `<finder-id>` order (lexicographic sort of the filenames). If a shard is not valid JSON on read, treat it as a failed shard per the failure handling below; do not attempt to repair a partial or malformed shard.
2. For each entry, validate against the schema. Required fields present; enum values legal. Hard-fail each of the following:
   - `exact_quote` and `surrounding_context` empty, whitespace-only, or punctuation-only. "Non-empty" means at least one non-whitespace, non-punctuation character.
   - Paginated source (entry's `source.volume_issue_pages` is set) without `retrieval.printed_page_observed`.
   - `verification_status: "verified"` with string-shape `exact_quote` lacking `retrieval.verification_trace`.
   - String-shape `exact_quote` not contained verbatim inside `surrounding_context`. The context is a single contiguous span from the rendered view containing the quote plus its neighbors; a `surrounding_context` that does not contain the quote is a summary or a placeholder, not context.
   - `verification_status: "verified"` with string-shape `exact_quote` lacking `retrieval.context_trace`.
   - `verification_status: "verified"` without `retrieval.access_mode`, or with a value outside the four §Verification fields access modes.
   - `retrieval.access_mode: "snippet"` on a `verified` entry. A snippet window is not full-text access under §3(b); the source should have been rejected (usually `abstract-only`), never logged.
   - `verification_status: "verified"` without a complete `source.reliability_basis`: all three sub-fields present and non-empty per §Reliability basis. List-shape entries are not exempt; `"partial"` entries are.
   - `reliability_basis.venue_type` not one of the nine §Reliability basis values, or facially inconsistent with `source.publication` (e.g., `"peer-reviewed-journal"` on an entry whose `source.publication` is `"Book"` or contains `"edited by"`).
   - `reliability_basis.venue_basis` or `reliability_basis.author_credentials` naming no specific checkable fact: no named publisher, index, society, institution, position, or prior work; generic adjectives only. The two `author_credentials` escape literals (§Reliability basis) are legal values, not violations.
   - Entries for the same source (same collapsed `lastname-year` id) carrying non-identical `reliability_basis` objects. The field is per-source; disagreement between sibling entries signals per-entry improvisation.
   - `source.type` present but not one of the eight §Source type values, or entries for the same source (same collapsed `lastname-year` id) carrying two different non-absent `source.type` values. The field is closed-enum and per-source; absent on any subset of siblings is legal.
   - `exact_quote` enumerating more than one named entity (names, terms, distinct claims) without `retrieval.per_entity_locators` covering each.
   - `location` disagreeing with `retrieval.printed_page_observed` on paginated sources. Compare the page token, not the string: strip any `"p."` or `"pp."` prefix and surrounding whitespace from both fields, then compare what remains, Arabic or Roman (`"443"`, `"p.443"`, and `"p. 443"` all carry page 443; `"p. xii"` carries page xii; `"pp. 12-34"` and `"12-34"` the same range). Tokens agree but a field is off-form: not a hard-fail; write the canonical `"p. N"` / `"pp. N-M"` form into the entry as merged (the shard file itself is never edited, so this is the validator's write-back, not a hand-fix). Tokens disagree: hard-fail. When `retrieval.printed_page_observed` is the literal `"not visible"`, this bullet does not compare; `location` carries the best stable locator available (tool page via the recorded offset, section, or chapter) and the entry is checked for that correspondence instead.
   - `verification_status: "partial"` on an entry written to a source-finder shard (`.claude/citations/working.<finder-id>.json`). `partial` is reserved for main-thread provenance (`{{USER}}`-pasted passages); source-finders have no `"partial"` path and must reject uncertain sources per `agents/source-finder.md`. A finder-written `"partial"` passes the enum check but violates the semantic contract; hard-fail closes the loophole at the structural layer.
   A hard-fail entry is surfaced to {{USER}} with the specific rule that fired; do not merge it. The three resolution paths below (fix in place, drop and merge rest, abandon) apply, with one carve-out: when the hard-fail is `verification_trace missing`, `context_trace missing`, `access_mode missing or "snippet"`, `per_entity_locators missing`, `exact_quote enumerating multiple entities`, or `exact_quote not contained in surrounding_context`, the "fix in place" path is NOT available. The source must be re-opened and the entry re-logged; reconstructing verification_trace from memory is exactly the failure these fields exist to block. Fix-in-place is reserved for formatting-only issues (whitespace trim, location-offset recorded incorrectly against an already-correct printed_page_observed) and for `reliability_basis` failures, where the fix is re-opening the source or the venue page and recording what the lookup returned, never typing a plausible basis from memory.

**Publication parseability check (surfaced, not blocking).** After the hard-fail pass, check each entry's `source.publication` and `source.doi_or_url` against the emitter's parseable shapes (`~/.claude/citations/csl-json-emitter.md` §Source-type inference). Four shapes fire, each named by a token:
   - `chapter-markers`: the string looks like a chapter but will not parse as one. It contains `"Ed.)"` or `"Eds.)"` or starts with `"Book chapter in"`, and it neither contains `"edited by"` nor begins with `"In "`. The emitter will type it `book` (the starts-with-`"Book"` rule) or misparse it, dropping container-title, editors, and pages.
   - `bare-book`: `source.publication` is exactly `"Book"`, with no `": <publisher>"` tail. The entry renders with no publisher. The fix is `"Book: <publisher>"`, with the publisher in `source.publication` itself, not only in `reliability_basis.venue_basis` (the emitter never reads `reliability_basis`).
   - `url-not-doi`: `source.doi_or_url` holds a URL that does not start with `https://doi.org/` or `http://dx.doi.org/`, on an entry whose type resolves to `article-journal` (explicit `source.type`, or the inference cascade lands there). Styles render that URL where a published article wants a DOI or nothing. The canonical DOI belongs in `source.doi_or_url`; the URL the work was retrieved from belongs in `retrieval.source_path`.
   - `untyped-proceedings`: `source.publication` contains `"Proceedings"`, `"Symposium"`, or `"Conference on"` while `source.type` is absent and the resolved type is `article-journal`. Rule 1 types these silently; only an explicit `source.type: "paper-conference"` renders them right.

   A hit does not block the merge and does not license editing the shard: publication strings are free prose by design, the emitter has a fallback, and false positives are possible. It must surface. The merge report includes the line `publication-parse-risk: <id(token), ... or none>` (example: `publication-parse-risk: leaper-2022-001(chapter-markers), allport-1954-001(bare-book)`); a merge report without this line has not run the check. Surface each hit with the suggested corrected string; {{USER}} decides whether to correct the merged log entry or accept the render risk. Correcting the log entry now is cheaper than hand-correcting `<draft>.bib.json` at format time.

**Parent-thread spot-check.** The `verification_trace` field can be fabricated by an agent from memory, which defeats its purpose. The academic-researcher (parent thread), on every merge pass, picks up to 3 entries randomly (or by highest-stakes: verified entries cited in a load-bearing paragraph; `"ocr-fulltext"` entries are preferred picks, their page fidelity is the weakest). For each picked entry, open the source at `retrieval.source_path` (or `source.doi_or_url`), locate `exact_quote`, and confirm that the actual first-20 and last-20 characters match `verification_trace`; then locate the neighbor text around it, confirm the first-20 and last-20 characters of `surrounding_context` match `context_trace`, and confirm `retrieval.access_mode` names the access the open view actually affords (a snippet window behind a claimed `rendered-html` or `ocr-fulltext` is a `spot-check-failed` incident). Mismatches are surfaced as `spot-check-failed` incidents and the entry is unmerged. While the source is open, also check its `source.reliability_basis`: confirm `venue_type` matches what the rendered artifact shows, and confirm the named facts in `venue_basis` and `author_credentials` exist (a credential stated as printed on the source is confirmed from the already-open view; an off-source fact takes one lookup). The spot-check verifies the copy, not the judgment: whether the recorded evidence exists is checkable; whether it is sufficient remains {{USER}}'s question, flagged in the merge report when it looks weak. A named fact that cannot be found is a `spot-check-failed` incident, same handling as a trace mismatch. Spot-checks scale with batch size: 1 entry per 4 merged, capped at 3. Record spot-check outcomes in the merge report to {{USER}}. The merge report must also include three `reliability_basis` surfacing lines: `credentials-none-stated: <ids or none>`, `preprints-merged: <ids or none>`, `grey-literature-merged: <ids or none>`, plus one access-mode surfacing line: `ocr-fulltext-merged: <ids or none>`; a merge report without these lines has not inspected `reliability_basis` or `access_mode`. **On any spot-check failure, escalate: spot-check every remaining entry from the same finder before merging any of them.** Fabrication tends to cluster within one finder's output (a single bad session drifts multiple entries); clearing the batch without escalation misses that signal and ships the siblings of the caught fabrication.
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

## Annotation (annotated-bibliography projects only)

Optional string field `annotation`. Populated by `[annotated-bib mode]` (templates/CLAUDE.md §7) in projects whose `.sourced-project-type` marker is `annotated-bib`; absent on essay-project entries.

Shape: 150–250 words of style-agnostic prose, four beats in order. Percentages are approximate allocations summing to 100%; ±5% drift per beat is fine when a specific source demands more summary or thinner evaluation.

1. Paraphrased summary of what the source argues or shows (~50% of word budget), drawn from `context_description` + `surrounding_context`. Preserves every qualifier in `exact_quote` (hedges, conditions, populations). Preserves second-order attribution ("Smith, reviewing Jones, argues …").
2. Relevance to the bibliography's topic (~25%), naming which in-scope bullet the source speaks to.
3. Location of key quotable material (~15%), reading `location` verbatim; at most one short phrase from `exact_quote` quoted inline.
4. Brief evaluation (~10%), one strength + one limit drawn only from fields the entry carries.

Generated from log fields only; no source re-read at annotation time (§3 verification is inherited from logging, not re-opened). Style-agnostic: do not render `(Smith, 2010)` inside the annotation; cross-references to other entries use `[@id]` form.

`verification_status: "partial"` entries: relevance and evaluation beats must stay inside the `exact_quote` span or be dropped. Drops emit a `### Partial-entry beats dropped` forcing list in `[annotated-bib mode]`'s compile report — entries of the form `{id, beat_dropped, reason}`. Empty list required when no drops occurred; no silent drops. A flag as prose to {{USER}} is not sufficient; the list is the artifact downstream gates inspect.

`[formatting mode]` reads this field when rendering an `annotated-bib` paste-target variant; essay paste targets ignore it. `[editing mode]` runs the §4 audit and §10 AI-tell pass on annotation prose; the `[editing mode]` quote-density pass and §9 paragraph-flow rules do not apply (both assume multi-paragraph prose).

## Typography

Fields that carry author-controlled typography (`source.title`, `source.authors`, `exact_quote`, `surrounding_context`, `annotation`) pass through the CSL-JSON emitter and pandoc+CSL rendering verbatim. Prefer Unicode characters over ASCII stand-ins when the source uses them: `'` (U+2019) for English apostrophes and right single quotes, `"` `"` (U+201C, U+201D) for curly double quotes, `—` (U+2014) for em-dashes, `–` (U+2013) for en-dashes in page ranges.

`[formatting mode]` runs pandoc with the `-smart` writer extension for the `google-docs` and `plain-markdown` paste targets, which curls ASCII `'` and `"` in the emitter output automatically. A companion lua-filter (`templates/filters/smart-quotes.lua`) reverses the conversion inside italic spans to preserve linguistic glottal-stop notation (`*Ma'heo'o*`, `*-'e*`). The filter cannot tell apart a glottal-stop `'` from an English contraction `'` when both appear in the same italic span; mixed-language titles (e.g., a source title like `A sacred error: Cheyenne Ma'heo'o doesn't mean "All-Father"`) should pre-bake the English apostrophe as Unicode U+2019 in the log so the filter leaves the linguistic `'` alone and the English `'` survives the round trip.

The `word` and `latex` paste targets handle typography natively via pandoc's docx and latex writers; pre-baked Unicode passes through unchanged.

## Additions

Two kinds of optional fields can appear beyond the required structure above.

- **Schema-defined optional fields.** Fields this schema defines but doesn't require on every entry (currently `author_evidence`, see "Author-field provenance"; `source.type`, see "Source type" above; and `annotation`, see "Annotation" above). When you use one, follow its definition exactly; do not redefine its semantics or shape per entry.
- **Ad-hoc additions.** Fields not defined by this schema, added when they help (scholarly counterarguments, topic tags, follow-up questions). Use a stable name and consistent shape across entries in the same log.

Never remove fields from this schema.
