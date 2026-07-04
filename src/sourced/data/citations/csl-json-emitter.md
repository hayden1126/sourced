# CSL-JSON emitter specification

Maps citation log entries (structure defined in `citations/schema.md`) to CSL-JSON objects that `pandoc --citeproc` consumes as its `--bibliography`. Read by `[formatting mode]` (CLAUDE.md §7 step 4) to produce `<draft>.bib.json`.

## Scope

One unique source → one CSL-JSON object. Deduplicate across multiple log entries that point at the same source: a source cited three times has three log entries with ids `smith-2010-001`, `smith-2010-002`, `smith-2010-003` but produces **one** CSL-JSON object with `id: "smith-2010"` (the collapsed form). The pre-pandoc pass (§7 step 3) rewrites `<author>-<year>-NNN` → `<author>-<year>` in the derived markdown; this emitter keys the bibliography to that collapsed form.

## Field mapping

| Log field | CSL-JSON field | Rule |
|-----------|----------------|------|
| `id` (collapsed to `<author>-<year>`) | `id` | Strip trailing `-NNN` from every log id; dedupe by the result. |
| `source.authors` | `author` (array) | Parse each `"Lastname, First Middle"` string by splitting on the first comma: `{family: "Lastname", given: "First Middle"}`. Strings without a comma are corporate authors → `{literal: "Name"}`. |
| `source.year` | `issued.date-parts: [[YEAR]]` | Integer. If `source.year` is `null` or the string `"n.d."`, omit the `issued` key entirely; CSL renders the style's no-date form. |
| `source.title` | `title` | Pass-through string. |
| `source.publication` | `container-title`, `publisher`, `publisher-place` (see §Source-type inference) | Free-form in the log; splitting depends on the resolved type (explicit `source.type` or inferred; see §Source-type inference). |
| `source.volume_issue_pages` | `volume`, `issue`, `page` | Parsing depends on the resolved type (see §Source-type inference). If the field is empty, omit all three. For `article-journal`: parse `"42(3), 12-34"` → `volume: "42"`, `issue: "3"`, `page: "12-34"`. If no parens, treat the whole first token as `volume`; if no comma, there is no page. For `chapter` and `book`: treat the whole value as `page` (these forms are page ranges, not journal volume/issue). For `paper-conference`: if the value contains a comma or parentheses, apply the article-journal parsing (serial-style proceedings); else treat the whole value as `page` (a bare page range). For `report`, `thesis`, and `dataset`: treat the whole value as `page`, same as `chapter` and `book`. For `webpage` and the fallback: apply the article-journal parsing. |
| `source.doi_or_url` | `DOI` or `URL` | If the value starts with `https://doi.org/` or `http://dx.doi.org/`, strip the prefix and store as `DOI`. Else if the value is a non-empty URL, store as `URL`. If the field is empty, omit both. |
| `source.type` (optional) | `type` | Passed through when present and one of the eight schema enum values; otherwise inferred per §Source-type inference below. |

Fields not listed above (`exact_quote`, `surrounding_context`, `context_description`, `claim_supported`, `citation_string`, `provisional_reference`, `draft_reference`, `verification_status`, `retrieval`, `retrieved_at`, `added_at`) and the `source.reliability_basis` sub-object are **not** emitted — they are logging metadata, not bibliographic data.

## Source-type inference

The optional `source.type` log field (schema.md §Source type) resolves `type` when present; inference is the absent-type path.

0. If `source.type` is present and is one of the eight schema values (`article-journal`, `book`, `chapter`, `webpage`, `paper-conference`, `report`, `thesis`, `dataset`), use it as the CSL `type` directly. Skip the inference cascade below and do not emit the rule-5 fallback warning. Map fields per the matching rule below for the first four values, and per §Explicit-only types for the last four. If `source.type` is present but not one of the eight values, surface a tolerable warning naming the entry id and the illegal value, ignore the field, and continue with inference. When dedupe collapses sibling entries and only some carry `source.type`, use the value from any sibling that carries it; if siblings disagree (a state the merge protocol hard-fails), use the lowest-`NNN` sibling's value and surface a tolerable warning naming the ids and both values.

When `source.type` is absent, infer deterministically, in order:

1. If `source.volume_issue_pages` is non-empty AND `source.publication` does not start with `"Book"` AND `source.publication` does not contain `"edited by"` → `article-journal`.
   - `container-title`: the full `source.publication` string.
   - `publisher`, `publisher-place`: omit.
2. If `source.publication` starts with `"Book"` (either the literal string `"Book"` or `"Book: <publisher details>"`) → `book`.
   - `publisher`: whatever follows `"Book: "`, or omit if `"Book"` is the whole value.
   - `publisher-place`: omit unless the publisher string contains a `, <City>` suffix (heuristic — see §Known gaps).
   - `container-title`: omit.
3. If `source.publication` contains `"edited by"` OR begins with `"In "` → `chapter`.
   - `container-title`: the book title (parsed from the text following `"In "` up to `"edited by"`, or the whole string if no `"edited by"`).
   - `editor`: parsed from text following `"edited by"`. Split that text by comma. The **last** comma-segment is treated as the publisher (see below); all preceding segments are editor segments. Each editor segment may itself contain multiple editors joined with `" and "` or `", and "` (Oxford-comma form): split each segment on `", and "` first, then on `" and "`, to produce individual editor names. Each individual editor name is a person name in given-then-family order (Western prose form, unlike `source.authors` which is surname-first); split on whitespace and treat the last whitespace-token as `family`, the rest as `given`. Example: `"Alan Roth, Cambridge University Press"` → editors = `[{family: "Roth", given: "Alan"}]`, publisher = `"Cambridge University Press"`. Multi-editor example: `"Alan Roth and Bob Smith, Cambridge University Press"` → editors = `[{family: "Roth", given: "Alan"}, {family: "Smith", given: "Bob"}]`, publisher = `"Cambridge University Press"`. If only one comma-segment is present, treat it as the sole editor segment (still subject to `" and "` splitting) and omit `publisher`.
   - `publisher`: the last comma-segment after `"edited by"` (per above), if present.
4. Else if `source.doi_or_url` is non-empty and does NOT start with `https://doi.org/` or `http://dx.doi.org/` → `webpage`.
   - `container-title`: the full `source.publication` string (often the site name).
   - `URL` is already set from the field mapping.
5. **Fallback:** default to `article-journal`, and apply the article-journal field-mapping rules above (`container-title`: full `source.publication`; omit `publisher`/`publisher-place`). Surface a tolerable warning naming the log entry id and the reason (e.g., "no volume/issue/pages present; no clear book/chapter markers; DOI present; defaulting type to `article-journal`"). The user can correct the log entry and re-run.

### Explicit-only types

Four enum values have no inference route and are reachable only through `source.type`:

- `paper-conference`: `container-title`: the full `source.publication` string (the proceedings or conference name). `publisher`, `publisher-place`: omit. `source.volume_issue_pages` parses per the field-mapping table (serial form or bare page range).
- `report`: `publisher`: the full `source.publication` string (the issuing institution or agency). `container-title`: omit. `publisher-place`: apply the book heuristic (§Known gaps).
- `thesis`: `publisher`: the full `source.publication` string (the degree-granting institution). `container-title`: omit. `publisher-place`: apply the book heuristic.
- `dataset`: `publisher`: the full `source.publication` string (the repository or distributor). `container-title`, `publisher-place`: omit. Styles that label datasets (APA renders "[Data set]") derive the label from `type`; nothing extra is emitted.

The shipped styles render all eight types through their vendored CSL files. A style without an explicit branch for a type (ieee has none for `dataset`, mla9 none for `report`) falls through to its generic monographic form, which is still closer than a mistyped `article-journal`.

CSL `type` is load-bearing: `article-journal` vs. `book` vs. `chapter` vs. `webpage` vs. the explicit-only four drives entirely different entry formats in every style. Fallback warnings should trigger human review before trusting the formatted output; an explicit `source.type` removes both the warning and the review.

## Known gaps (accepted residual)

- `publisher-place` for `book` entries is heuristic. The log's `source.publication` is free prose; cities aren't structurally marked. Emit `publisher-place` only when a `, <CityName>` suffix is clearly present (capitalized word after a comma, not numeric, not containing digits). Else omit; citeproc renders the book without a place.
- `chapter` editor parsing assumes the "edited by Firstname Lastname[ and Firstname Lastname...], Publisher" shape (multiple editors joined with `" and "` or `", and "` are supported). Other orderings (e.g., surname-first prose, role-suffixed names) produce best-effort output; the user can correct the log entry.
- Untyped conference papers, technical reports, theses, and datasets still map to the fallback: those classes have no inference route, and only an explicit `source.type` reaches them. The residual is now producer discipline (set the field at logging time), not a missing schema field.
- `thesis` entries carry no genre (doctoral vs. master's) and `dataset` entries no version: the log has no fields for either, and citeproc renders the entry without those slots.

## Worked examples

### article-journal

Log entry:
```json
{
  "id": "smith-2010-001",
  "source": {
    "authors": ["Smith, Jane A."],
    "year": 2010,
    "title": "Pragmatic Markers in Contact Situations",
    "publication": "Journal of Pragmatics",
    "volume_issue_pages": "42(3), 12-34",
    "doi_or_url": "https://doi.org/10.1016/j.pragma.2010.01.005"
  }
}
```

CSL-JSON output (after dedupe of any sibling entries):
```json
{
  "id": "smith-2010",
  "type": "article-journal",
  "author": [{"family": "Smith", "given": "Jane A."}],
  "issued": {"date-parts": [[2010]]},
  "title": "Pragmatic Markers in Contact Situations",
  "container-title": "Journal of Pragmatics",
  "volume": "42",
  "issue": "3",
  "page": "12-34",
  "DOI": "10.1016/j.pragma.2010.01.005"
}
```

### book

Log entry:
```json
{
  "id": "jones-1998-001",
  "source": {
    "authors": ["Jones, Robert"],
    "year": 1998,
    "title": "Linguistic Landscapes",
    "publication": "Book: Oxford University Press",
    "volume_issue_pages": "",
    "doi_or_url": ""
  }
}
```

CSL-JSON output:
```json
{
  "id": "jones-1998",
  "type": "book",
  "author": [{"family": "Jones", "given": "Robert"}],
  "issued": {"date-parts": [[1998]]},
  "title": "Linguistic Landscapes",
  "publisher": "Oxford University Press"
}
```

### chapter

Log entry:
```json
{
  "id": "lee-2015-001",
  "source": {
    "authors": ["Lee, Mei"],
    "year": 2015,
    "title": "Code-switching in Bilingual Classrooms",
    "publication": "In Classroom Discourse, edited by Alan Roth, Cambridge University Press",
    "volume_issue_pages": "87-110",
    "doi_or_url": ""
  }
}
```

CSL-JSON output:
```json
{
  "id": "lee-2015",
  "type": "chapter",
  "author": [{"family": "Lee", "given": "Mei"}],
  "issued": {"date-parts": [[2015]]},
  "title": "Code-switching in Bilingual Classrooms",
  "container-title": "Classroom Discourse",
  "editor": [{"family": "Roth", "given": "Alan"}],
  "publisher": "Cambridge University Press",
  "page": "87-110"
}
```

### webpage

Log entry:
```json
{
  "id": "mla-2021-001",
  "source": {
    "authors": ["Modern Language Association"],
    "year": 2021,
    "title": "How do I cite a source with multiple authors?",
    "publication": "MLA Style Center",
    "volume_issue_pages": "",
    "doi_or_url": "https://style.mla.org/citing-multiple-authors/"
  }
}
```

CSL-JSON output:
```json
{
  "id": "mla-2021",
  "type": "webpage",
  "author": [{"literal": "Modern Language Association"}],
  "issued": {"date-parts": [[2021]]},
  "title": "How do I cite a source with multiple authors?",
  "container-title": "MLA Style Center",
  "URL": "https://style.mla.org/citing-multiple-authors/"
}
```

### paper-conference (explicit `source.type`)

Log entry:
```json
{
  "id": "okafor-2019-001",
  "source": {
    "type": "paper-conference",
    "authors": ["Okafor, Adaeze"],
    "year": 2019,
    "title": "Streaming Consensus under Partial Synchrony",
    "publication": "Proceedings of the 38th ACM Symposium on Principles of Distributed Computing",
    "volume_issue_pages": "211-220",
    "doi_or_url": "https://doi.org/10.1145/xxxx.yyyy"
  }
}
```

CSL-JSON output:
```json
{
  "id": "okafor-2019",
  "type": "paper-conference",
  "author": [{"family": "Okafor", "given": "Adaeze"}],
  "issued": {"date-parts": [[2019]]},
  "title": "Streaming Consensus under Partial Synchrony",
  "container-title": "Proceedings of the 38th ACM Symposium on Principles of Distributed Computing",
  "page": "211-220",
  "DOI": "10.1145/xxxx.yyyy"
}
```

No warning. Without `source.type`, rule 1 would fire (`volume_issue_pages` non-empty, no book or chapter markers) and silently type this `article-journal`; no fallback warning would surface the mistype.

### report (explicit `source.type`)

Log entry:
```json
{
  "id": "sandoval-2021-001",
  "source": {
    "type": "report",
    "authors": ["Sandoval, Maria"],
    "year": 2021,
    "title": "Rural Broadband Access After the 2020 Subsidy Round",
    "publication": "Government Accountability Office",
    "volume_issue_pages": "",
    "doi_or_url": "https://www.gao.gov/products/gao-21-xxxx"
  }
}
```

CSL-JSON output:
```json
{
  "id": "sandoval-2021",
  "type": "report",
  "author": [{"family": "Sandoval", "given": "Maria"}],
  "issued": {"date-parts": [[2021]]},
  "title": "Rural Broadband Access After the 2020 Subsidy Round",
  "publisher": "Government Accountability Office",
  "URL": "https://www.gao.gov/products/gao-21-xxxx"
}
```

No warning. Without `source.type`, rule 4 would fire (non-DOI URL, empty `volume_issue_pages`) and type this `webpage`.

### fallback

Log entry (no volume/issue/pages, no book/chapter markers, DOI present):
```json
{
  "id": "opaque-2022-001",
  "source": {
    "authors": ["Opaque Collective"],
    "year": 2022,
    "title": "Untitled Working Paper",
    "publication": "SomeVenue",
    "volume_issue_pages": "",
    "doi_or_url": "https://doi.org/10.5555/xxxx"
  }
}
```

CSL-JSON output (with warning):
```json
{
  "id": "opaque-2022",
  "type": "article-journal",
  "author": [{"literal": "Opaque Collective"}],
  "issued": {"date-parts": [[2022]]},
  "title": "Untitled Working Paper",
  "container-title": "SomeVenue",
  "DOI": "10.5555/xxxx"
}
```

Warning surfaced by the formatter: `emitter fallback: entry opaque-2022-001 has no volume/issue/pages and no book/chapter markers; type defaulted to article-journal. Verify the entry's source.publication field or expect a misrendered bibliography entry.`

## Use in `[formatting mode]`

§7 step 4 invokes this emitter against the log filtered to ids actually referenced in source prose (dead log entries — ones present in the log but not cited — are not emitted). The output is written to `<draft>.bib.json` and passed to pandoc as `--bibliography=<draft>.bib.json`.
