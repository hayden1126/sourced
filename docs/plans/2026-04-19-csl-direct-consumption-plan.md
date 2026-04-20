# CSL Direct Consumption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shift citation and bibliography rendering from hand-maintained per-style rules (duplicated in 5 style.md files) to `pandoc --citeproc` driven by vendored CSL files, for all paste targets.

**Architecture:** All three paste targets (`word`, `google-docs`, `plain-markdown`) invoke `pandoc --citeproc --bibliography=<draft>.bib.json --csl=<csl>` for rendering. `style.md` slims to ~60-80 lines containing only identity/provenance, document layout, paste-target flags, and special tokens — removing all per-source-type entry formats, per-author-count inline rules, numbering, and footnote-body rules (CSL's territory). CLAUDE.md §7 [formatting mode] gets a structural rewrite: Shape-branch dispatch goes away; a uniform pre-pandoc → pandoc → post-pandoc pipeline replaces it. Migration is staged across 5 PRs.

**Tech Stack:** bash (install.sh), pandoc 3.1+ with citeproc, CSL 1.0.2 (XML), CSL-JSON (bibliography), Python 3 (XML parsing in install.sh), markdown (all doc/spec files).

**Spec:** `docs/specs/2026-04-19-csl-direct-consumption-design.md` (commit `4a8774e`). When this plan says "per spec §N", that refers to sections in that file.

---

## File Structure

### New files

- `citations/csl-json-emitter.md` — log-entry → CSL-JSON mapping + source-type inference heuristic. Read by `[formatting mode]` at emit time (§7 step 4).
- `tests/emitter/` — emitter parity fixtures.
  - `tests/emitter/article-journal/input.citations.json`
  - `tests/emitter/article-journal/expected.bib.json`
  - `tests/emitter/book/input.citations.json`
  - `tests/emitter/book/expected.bib.json`
  - `tests/emitter/chapter/input.citations.json`
  - `tests/emitter/chapter/expected.bib.json`
  - `tests/emitter/webpage/input.citations.json`
  - `tests/emitter/webpage/expected.bib.json`
  - `tests/emitter/fallback/input.citations.json` — exercises the default-to-article-journal fallback warning.
  - `tests/emitter/fallback/expected.bib.json`
  - `tests/emitter/README.md` — manual-run instructions.
- `tests/parity/<style>/` — one dir per shipped style (`apa7`, `chicago17-ad`, `chicago17-nb`, `ieee`, `mla9`).
  - `fixture.pandoc.md` — collapsed markdown ready for pandoc.
  - `fixture.bib.json` — hand-authored CSL-JSON bibliography.
  - `golden/<target>.<ext>` — hand-authored expected output per target (`plain-markdown.md`, `google-docs.md`, `word.docx`).
  - `run.sh` — runner that invokes pandoc for each target, diffs against `golden/`.
- `tests/parity/README.md` — manual-run instructions.

### Files to modify

- `install.sh` — upgrade pandoc presence-check to a 3.1+ version-parsed check; add CSL-title cross-check at per-project style install.
- `templates/CLAUDE.md` — rewrite §7 [formatting mode] procedure (lines ~359-404); minor updates to §8 staleness language if the rewrite changes which step triggers the staleness prompt (it doesn't — step 2 still owns it).
- `docs/STYLES.md` — update the "Style file structure" table (slim-schema required sections), "Paste targets" section (all targets go through pandoc now), and "How `[formatting mode]` uses style.md" summary. Add a note about the dead-weight-window during PR2.
- `templates/styles/apa7.md` — slim (PR2a touches, PR3 finalizes).
- `templates/styles/chicago17-ad.md` — slim (PR2a touches, PR3 finalizes).
- `templates/styles/chicago17-nb.md` — slim (PR2a touches, PR2 finalizes).
- `templates/styles/ieee.md` — slim (PR2a touches, PR2 finalizes).
- `templates/styles/mla9.md` — slim (PR2a touches, PR2 finalizes).

### Files unchanged

- CSL files in `templates/styles/<name>/*.csl` — already vendored; no change.
- `templates/styles/chicago17-ad/classical-abbreviations.md` — sidecar stays; only the hook specification moves into the slim style.md.
- `citations/schema.md` — no schema change in this plan.

---

## Phase 1 — PR0.5: CSL-JSON emitter specification + fixtures

**Goal of this PR:** Publish the log → CSL-JSON mapping as an addressable specification the formatter reads; ship fixtures covering each inferred source type and the fallback path. No schema changes, no §7 changes.

### Task 1.1: Author `citations/csl-json-emitter.md`

**Files:**
- Create: `citations/csl-json-emitter.md`

- [ ] **Step 1: Write the emitter specification file.**

Content to create:

````markdown
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
| `source.publication` | `container-title`, `publisher`, `publisher-place` (see §Source-type inference) | Free-form in the log; splitting depends on inferred type. |
| `source.volume_issue_pages` | `volume`, `issue`, `page` | Parse `"42(3), 12-34"` → `volume: "42"`, `issue: "3"`, `page: "12-34"`. If no parens, treat the whole first token as `volume`. If no comma, there is no page. If the field is empty, omit all three. |
| `source.doi_or_url` | `DOI` or `URL` | If the value starts with `https://doi.org/` or `http://dx.doi.org/`, strip the prefix and store as `DOI`. Else store as `URL`. |
| *(derived)* | `type` | Inferred per §Source-type inference below. |

Fields not listed above (`exact_quote`, `surrounding_context`, `context_description`, `claim_supported`, `citation_string`, `provisional_reference`, `draft_reference`, `verification_status`, `retrieval`, `retrieved_at`, `added_at`) are **not** emitted — they are logging metadata, not bibliographic data.

## Source-type inference

The log has no `type` field today. Infer deterministically, in order:

1. If `source.volume_issue_pages` is non-empty AND `source.publication` does not start with `"Book"` AND `source.publication` does not contain `"edited by"` → `article-journal`.
   - `container-title`: the full `source.publication` string.
   - `publisher`, `publisher-place`: omit.
2. If `source.publication` starts with `"Book"` (either the literal string `"Book"` or `"Book: <publisher details>"`) → `book`.
   - `publisher`: whatever follows `"Book: "`, or omit if `"Book"` is the whole value.
   - `publisher-place`: omit unless the publisher string contains a `, <City>` suffix (heuristic — see §Known gaps).
   - `container-title`: omit.
3. If `source.publication` contains `"edited by"` OR begins with `"In "` → `chapter`.
   - `container-title`: the book title (parsed from the text following `"In "` up to `"edited by"`, or the whole string if no `"edited by"`).
   - `editor`: parsed from text following `"edited by"` as `{family, given}` objects, comma-split.
   - `publisher`: if present after the editor list (comma-separated suffix).
4. Else if `source.doi_or_url` is a URL not beginning with `doi.org` → `webpage`.
   - `container-title`: the full `source.publication` string (often the site name).
   - `URL` is already set from the field mapping.
5. **Fallback:** default to `article-journal`. Surface a tolerable warning naming the log entry id and the reason (e.g., "no volume/issue/pages present; no clear book/chapter markers; DOI present; defaulting type to `article-journal`"). The user can correct the log entry and re-run.

CSL `type` is load-bearing: `article-journal` vs. `book` vs. `chapter` vs. `webpage` drives entirely different entry formats in every style. Fallback warnings should trigger human review before trusting the formatted output.

## Known gaps (accepted residual)

- `publisher-place` for `book` entries is heuristic. The log's `source.publication` is free prose; cities aren't structurally marked. Emit `publisher-place` only when a `, <CityName>` suffix is clearly present (capitalized word after a comma, not numeric, not containing digits). Else omit; citeproc renders the book without a place.
- `chapter` editor parsing assumes the "edited by Firstname Lastname, Publisher" shape. Non-standard orderings produce best-effort output; the user can correct the log entry.
- Untyped sources (conference papers, technical reports, theses, datasets) all map to the fallback. Future log schema additions (e.g., optional `source.type` field) would let the user bypass inference.

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
````

- [ ] **Step 2: Walk through the spec against the four fixtures in §Task 1.2 mentally.**

For each of the 4 type cases and the fallback, confirm the spec section covers the mapping used in the fixture's `expected.bib.json`. If a fixture reveals a gap, fix the spec first, then the fixture.

- [ ] **Step 3: Commit.**

```bash
git add citations/csl-json-emitter.md
git commit -m "Add CSL-JSON emitter specification"
```

---

### Task 1.2: Write emitter fixtures

**Files:**
- Create: `tests/emitter/article-journal/input.citations.json`
- Create: `tests/emitter/article-journal/expected.bib.json`
- Create: `tests/emitter/book/input.citations.json`
- Create: `tests/emitter/book/expected.bib.json`
- Create: `tests/emitter/chapter/input.citations.json`
- Create: `tests/emitter/chapter/expected.bib.json`
- Create: `tests/emitter/webpage/input.citations.json`
- Create: `tests/emitter/webpage/expected.bib.json`
- Create: `tests/emitter/fallback/input.citations.json`
- Create: `tests/emitter/fallback/expected.bib.json`
- Create: `tests/emitter/README.md`

- [ ] **Step 1: Write each fixture pair using the worked examples from Task 1.1.**

Each `input.citations.json` is a JSON array with one or more log entries (use the worked-example log entry from the spec; add a second entry for the same source with a different NNN suffix to exercise dedup in at least one fixture — put it in `article-journal/`).

Each `expected.bib.json` is a JSON array with the CSL-JSON object(s) the emitter must produce.

For `article-journal/input.citations.json`, include two entries to exercise dedup:
```json
[
  { "id": "smith-2010-001", "source": { "authors": ["Smith, Jane A."], "year": 2010, "title": "Pragmatic Markers in Contact Situations", "publication": "Journal of Pragmatics", "volume_issue_pages": "42(3), 12-34", "doi_or_url": "https://doi.org/10.1016/j.pragma.2010.01.005" } },
  { "id": "smith-2010-002", "source": { "authors": ["Smith, Jane A."], "year": 2010, "title": "Pragmatic Markers in Contact Situations", "publication": "Journal of Pragmatics", "volume_issue_pages": "42(3), 12-34", "doi_or_url": "https://doi.org/10.1016/j.pragma.2010.01.005" } }
]
```

`article-journal/expected.bib.json` is a one-element array (dedupe collapses both inputs):
```json
[
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
]
```

For the other four fixture dirs (`book/`, `chapter/`, `webpage/`, `fallback/`), use the corresponding worked example from the spec as the single-entry input, and the example's CSL-JSON as `expected.bib.json` (wrapped in a one-element array). Omit the fields that the spec's field-mapping rules say to omit.

- [ ] **Step 2: Write the README.**

Content:

```markdown
# Emitter parity fixtures

Each subdirectory is one source-type case. To verify the emitter specification against a fixture:

1. Read `citations/csl-json-emitter.md` (the specification).
2. Open `input.citations.json` (log entries).
3. Apply the spec's field-mapping and type-inference rules mentally.
4. Compare your result to `expected.bib.json`.

The fallback fixture should also produce a warning message (format specified in the emitter spec). The warning is not in `expected.bib.json` — verify the message shape by reading the spec.

These fixtures are reference material for `[formatting mode]` when it emits `<draft>.bib.json` from a project's citation log (CLAUDE.md §7 step 4). They are not executable tests; the tool's procedures are LLM-followed.
```

- [ ] **Step 3: Commit.**

```bash
git add tests/emitter/
git commit -m "Add CSL-JSON emitter parity fixtures"
```

---

## Phase 2 — PR1: Parity harness scaffolding + goldens

**Goal of this PR:** Create per-style parity test scaffolding and hand-author golden files per style × target. Ship 15 goldens (5 styles × 3 targets). No style.md or §7 changes yet.

### Task 2.1: Parity harness scaffolding

**Files:**
- Create: `tests/parity/README.md`
- Create: `tests/parity/run-all.sh`

- [ ] **Step 1: Write the harness README.**

Content:

```markdown
# Parity harness

Verifies that `pandoc --citeproc` + the vendored CSL file produces the expected output for each shipped style × paste-target combination.

## Scope

Tests the pandoc+CSL middle of CLAUDE.md §7 (steps 4-5) with deterministic inputs. Does not test the LLM-driven pre-flight, threshold check, or post-pandoc classical-abbreviations rewrite. Those are validated by the LLM reading the spec and applying it.

## Per-style structure

Each `tests/parity/<style>/` contains:

- `fixture.pandoc.md` — hand-authored collapsed markdown (shape: what §7 step 3 would emit from a representative source draft). Uses Pandoc citation syntax `[@id]`, `@id`, `[@id, p. N]`, etc.
- `fixture.bib.json` — hand-authored CSL-JSON bibliography matching the ids in `fixture.pandoc.md`.
- `golden/<target>.<ext>` — hand-authored expected output per paste target:
  - `golden/plain-markdown.md`
  - `golden/google-docs.md`
  - `golden/word.docx.md` — the intermediate markdown pandoc emits for the word target, before docx binarization. Storing `.docx` binaries in git is hostile to review; compare the markdown intermediate instead.
- `run.sh` — invokes pandoc per target, writes output under `actual/`, diffs against `golden/`.

## Running

To run one style:
```bash
cd tests/parity/<style>/
./run.sh
```

To run all styles:
```bash
cd tests/parity/
./run-all.sh
```

Requires pandoc 3.1+ on PATH.

## Acceptance

`diff` returns empty, or the only differences are in the tolerated-diff allowlist (trailing newlines, hard-wrap line breaks where `--wrap=preserve` is set). Any difference in ordering, punctuation, bibliography content, or rendered citation text is a failure.

## Authoring goldens

Build each golden file by hand from the style's authoritative reference (e.g., MLA Style Center examples, IEEE sample paper, Chicago NB sample paper), applied to the fixture's sources. If you cannot find a reference example for a case, mark the case in the golden with a comment and exclude it from the fixture; a harness that always passes because it ignores hard cases is worse than no harness.
```

- [ ] **Step 2: Write `run-all.sh`.**

Content:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=0
for style_dir in "${SCRIPT_DIR}"/*/; do
  style=$(basename "${style_dir}")
  [[ -f "${style_dir}/run.sh" ]] || continue
  echo "=== ${style} ==="
  if ! (cd "${style_dir}" && ./run.sh); then
    failures=$((failures + 1))
  fi
done

if [[ ${failures} -gt 0 ]]; then
  echo ""
  echo "${failures} style(s) failed parity."
  exit 1
fi

echo ""
echo "All styles passed parity."
```

Make executable:

```bash
chmod +x tests/parity/run-all.sh
```

- [ ] **Step 3: Commit.**

```bash
git add tests/parity/README.md tests/parity/run-all.sh
git commit -m "Add parity harness scaffolding"
```

---

### Task 2.2: Per-style fixtures and goldens

Repeat this task for each of the 5 shipped styles: `apa7`, `chicago17-ad`, `chicago17-nb`, `ieee`, `mla9`.

**Per-style files:**
- Create: `tests/parity/<style>/fixture.pandoc.md`
- Create: `tests/parity/<style>/fixture.bib.json`
- Create: `tests/parity/<style>/golden/plain-markdown.md`
- Create: `tests/parity/<style>/golden/google-docs.md`
- Create: `tests/parity/<style>/golden/word.docx.md`
- Create: `tests/parity/<style>/run.sh`

- [ ] **Step 1 (per style): Author the fixture input.**

`fixture.pandoc.md` template (adapt per style, especially for footnote shapes — NB uses narrative `@id` for first-cite/short-form cases):

```markdown
# Fixture: <style> parity

Single-author pragmatic point [@smith-2010]. Narrative form: @smith-2010 argued the case.

Two-author case [@jones-cruz-2015]. Narrative: @jones-cruz-2015 found that.

Three-plus author case [@able-baker-chen-2019]. Narrative: @able-baker-chen-2019 demonstrated.

Corporate author [@mla-2021].

No-date source [@perennial-nd].

Multi-citation [@smith-2010; @jones-cruz-2015].

Page locator [@smith-2010, p. 42].

Page range [@smith-2010, pp. 42-44].

# References
```

For footnote styles (chicago17-nb), use narrative `@id` patterns that exercise first-cite-full / short-subsequent / `ibid.` rules. Example:

```markdown
The argument developed by @smith-2010 ran counter to earlier claims. Smith's later
work [@smith-2010] extended the point. The parallel case in @jones-cruz-2015
reinforced it; [@jones-cruz-2015, p. 88] supplied the numerical support.

# Bibliography
```

For numeric-sequence styles (ieee), use patterns that exercise range-collapsing:

```markdown
Prior results [@smith-2010] set the baseline. Subsequent work expanded the
finding [@jones-cruz-2015]. Consecutive improvements [@able-baker-chen-2019;
@smith-2010; @jones-cruz-2015] (should render as bracketed numbers; consecutive
ones collapse per IEEE §Numbering rules).

# References
```

- [ ] **Step 2 (per style): Author `fixture.bib.json`.**

Populate with one CSL-JSON entry per unique id in the fixture. Use the emitter spec (from Phase 1) as the mapping source. Minimum entries:

```json
[
  {"id": "smith-2010", "type": "article-journal", "author": [{"family": "Smith", "given": "Jane A."}], "issued": {"date-parts": [[2010]]}, "title": "Pragmatic Markers in Contact Situations", "container-title": "Journal of Pragmatics", "volume": "42", "issue": "3", "page": "12-34", "DOI": "10.1016/j.pragma.2010.01.005"},
  {"id": "jones-cruz-2015", "type": "article-journal", "author": [{"family": "Jones", "given": "Robert"}, {"family": "Cruz", "given": "Elena"}], "issued": {"date-parts": [[2015]]}, "title": "Code-switching in Classroom Discourse", "container-title": "Applied Linguistics", "volume": "36", "issue": "2", "page": "84-102"},
  {"id": "able-baker-chen-2019", "type": "article-journal", "author": [{"family": "Able", "given": "Amir"}, {"family": "Baker", "given": "Bea"}, {"family": "Chen", "given": "Chao"}], "issued": {"date-parts": [[2019]]}, "title": "Multilingual Practices in Urban Contexts", "container-title": "Language in Society", "volume": "48", "issue": "1", "page": "55-80"},
  {"id": "mla-2021", "type": "webpage", "author": [{"literal": "Modern Language Association"}], "issued": {"date-parts": [[2021]]}, "title": "How do I cite a source with multiple authors?", "container-title": "MLA Style Center", "URL": "https://style.mla.org/citing-multiple-authors/"},
  {"id": "perennial-nd", "type": "webpage", "author": [{"family": "Perennial", "given": "Paul"}], "title": "Undated Commentary", "container-title": "Perennial Blog", "URL": "https://example.com/undated"}
]
```

- [ ] **Step 3 (per style): Author each golden.**

Build each `golden/<target>.<ext>` by hand. Procedure:

1. Read the style's authoritative reference (linked in the current style.md's `§Style identity.Source consulted`).
2. For each cited id in `fixture.pandoc.md`, work out what the style's inline rendering should be.
3. For each unique source in `fixture.bib.json`, work out the bibliography entry per the style's entry-format rule.
4. Write the golden file: the post-pandoc markdown output, including rendered inline citations + a References/Bibliography/Works Cited section (heading text per the style's `List heading:` field in style.md).
5. For `golden/google-docs.md`, the output should match `golden/plain-markdown.md` for most styles (same markdown body) plus any paste-time instruction prepended as a single line at top (e.g., MLA: "Apply hanging indent in Google Docs after pasting (Format > Align > Indentation options > Special > Hanging).").
6. For `golden/word.docx.md`, the output is pandoc's markdown intermediate before it produces the `.docx` binary — typically identical to `plain-markdown.md` except that references come from citeproc output structured for docx rendering (footnotes as pandoc-native footnote refs for NB).

**Reference sources to consult** (already listed in each current style.md):
- `apa7` → apastyle.apa.org
- `chicago17-ad` → chicagomanualofstyle.org + Purdue OWL
- `chicago17-nb` → chicagomanualofstyle.org (sample paper, notes-bibliography system)
- `ieee` → IEEE Reference Guide PDF
- `mla9` → style.mla.org

- [ ] **Step 4 (per style): Write `run.sh`.**

Content (adjust `<style>` and `<csl-filename>` per style; the CSL filename is in the current style.md's `§Style identity.CSL provenance.file`):

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CSL_FILE="${REPO_DIR}/templates/styles/<style>/<csl-filename>.csl"
STYLE_NAME="<style>"

mkdir -p "${SCRIPT_DIR}/actual"
failures=0

# -t markdown-citations (not -t markdown): pandoc's markdown writer round-trips citation syntax and drops the bibliography unless this writer extension is disabled.

# plain-markdown
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  --wrap=preserve \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/plain-markdown.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/plain-markdown.md" "${SCRIPT_DIR}/actual/plain-markdown.md"; then
  echo "[${STYLE_NAME}] plain-markdown FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] plain-markdown OK"
fi

# google-docs
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  --wrap=none \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/google-docs.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/google-docs.md" "${SCRIPT_DIR}/actual/google-docs.md"; then
  echo "[${STYLE_NAME}] google-docs FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] google-docs OK"
fi

# word (intermediate markdown)
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/word.docx.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/word.docx.md" "${SCRIPT_DIR}/actual/word.docx.md"; then
  echo "[${STYLE_NAME}] word.docx.md FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] word.docx.md OK"
fi

exit ${failures}
```

Make executable:

```bash
chmod +x tests/parity/<style>/run.sh
```

- [ ] **Step 5 (per style): Run the harness.**

```bash
cd tests/parity/<style>/
./run.sh
```

Expected: three `OK` lines. If any `FAIL`, the discrepancy is in the hand-authored golden vs. pandoc+CSL output. Triage:
- If the golden has a typo or rule mistake (e.g., wrong punctuation, wrong author-et-al threshold), fix the golden.
- If pandoc+CSL produces something demonstrably wrong per the style authority (e.g., misrendered multi-author), the CSL file itself may be wrong. Read the CSL, confirm against the authority. If the CSL is the problem, **stop** — this is a show-stopper for the migration; surface to the spec owner rather than patching the CSL in-tree.
- If the two disagree on a cosmetic choice (comma-space after author name, e.g.), accept pandoc's output as the authoritative rendering; update the golden. The whole point of the shift is that CSL, not our .md files, is source of truth.

- [ ] **Step 6 (per style): Commit.**

```bash
git add tests/parity/<style>/
git commit -m "Add parity fixtures and goldens for <style>"
```

- [ ] **Step 7 (after all 5 styles complete): Run the aggregate harness.**

```bash
cd tests/parity/
./run-all.sh
```

Expected: `All styles passed parity.` Commit only the fixtures; do not commit `actual/` output.

Add `actual/` to `.gitignore` at the end of PR1:

```bash
echo "tests/parity/*/actual/" >> .gitignore
git add .gitignore
git commit -m "Gitignore parity harness actual/ output"
```

---

## Phase 3 — PR2a: Pre-slim §Document layout + §On-demand references on all 5 styles

**Goal of this PR:** Normalize the §Document layout and §Style identity.On-demand references subsections across all 5 style.md files to the slim-schema shape. Leaves §Inline citations / §References list / §Footnote citations / §Numbering rules untouched (those are removed in PR2 and PR3). Enables the §7 rewrite in PR2 to read a consistent shape from every style.md file during the dead-weight window.

### Task 3.1: Update each style.md's §Document layout to the slim shape

Repeat for each of the 5 styles: `apa7`, `chicago17-ad`, `chicago17-nb`, `ieee`, `mla9`.

**Per-style files:**
- Modify: `templates/styles/<style>.md`

- [ ] **Step 1 (per style): Read the current §Document layout section.**

The current section exists in every shipped style.md (find the `## Document layout` header). Contains: title block, heading hierarchy, body text, spacing, margins, fonts, page numbering. Some styles have mini-subsections named differently (`### Title block`, `### Title page`, `### Footnotes`). The slim-schema shape is:

```markdown
## Document layout

### Fonts and spacing
[font family, size, line spacing, paragraph spacing — per current content]

### Margins
[margin values — per current content]

### Heading hierarchy
[markdown → destination interpretation — per current content]

### Title block
[per current content]

### Page numbering
[running header / footer — per current content]

### Block quotes
[threshold if any — see Step 2 below]
```

Reshape the existing content into these subsections. Preserve every fact; only reorganize. If the current section has content that doesn't fit a subsection above (e.g., "Footnotes" for styles that use endnotes/footnotes substantively), add a subsection for it at the end.

- [ ] **Step 2 (per style): Add the Block quotes subsection.**

Each style.md gets a `### Block quotes` subsection at the end of `## Document layout`. Content per style:

- `apa7`: "Threshold: 40 words. Direct quotes of 40 words or more are rendered as block quotes in source prose (indented, no surrounding quotation marks, citation after the closing punctuation). `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present."
- `chicago17-ad`: "Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10."
- `chicago17-nb`: "Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10."
- `ieee`: "Threshold: none. IEEE has no prescribed block-quote threshold; writers use editorial judgment."
- `mla9`: "Threshold: 4 lines of prose, 3 lines of verse (MLA 9 §6.36). Verse quotations use a slash `/` with spaces to mark line breaks when inline; block form for 4+ lines of prose / 3+ lines of verse with no quotation marks. `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight."

- [ ] **Step 3 (per style): Commit.**

```bash
git add templates/styles/<style>.md
git commit -m "Reshape <style> §Document layout; add Block quotes subsection"
```

---

### Task 3.2: Add §Style identity.On-demand references to each style.md (or verify it's already correct)

Repeat for each of the 5 styles.

**Per-style files:**
- Modify: `templates/styles/<style>.md`

- [ ] **Step 1 (per style): Check current §Style identity for the On-demand references bullet.**

Every current style.md has `- On-demand references:` under `## Style identity`. Content per style:

- `apa7`: `(none)`
- `chicago17-ad`: A pointer to `chicago17-ad/classical-abbreviations.md`. Update to the slim-schema form with a hook specification:
    ```markdown
    - On-demand references:
      - `chicago17-ad/classical-abbreviations.md` — classical-author abbreviation table.
      - Hook: after pandoc renders output, walk each bibliography entry and each footnote (for NB; n/a here); for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
    ```
- `chicago17-nb`: Same content as chicago17-ad; NB shares the sidecar. Update the current `On-demand references:` bullet to:
    ```markdown
    - On-demand references:
      - `chicago17-ad/classical-abbreviations.md` — shared with chicago17-ad.
      - Hook: after pandoc renders output, walk each footnote body and each bibliography entry; for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
    ```
- `ieee`: `(none)`
- `mla9`: `(none; classical texts in MLA context may need the chicago17-ad/classical-abbreviations.md sidecar if the writer is citing Greek or Latin primary sources — cross-reference only, not a hook).` The current mla9.md has a similar note; keep it as a pointer without a hook — MLA does not use classical abbreviations by default.

- [ ] **Step 2 (per style): Commit.**

```bash
git add templates/styles/<style>.md
git commit -m "Normalize <style> §Style identity.On-demand references to slim-schema form"
```

---

### Task 3.3: Update `docs/STYLES.md` to document the dead-weight window

**Files:**
- Modify: `docs/STYLES.md`

- [ ] **Step 1: Read `docs/STYLES.md` fully.**

```bash
# (Human-run; not a scripted step.)
cat docs/STYLES.md
```

Identify the "Style file structure" section and the "How `[formatting mode]` uses style.md" section — both will need updates in PR2. For PR2a, only add a one-paragraph note explaining the in-flight transition.

- [ ] **Step 2: Add the transition note.**

Insert immediately after the "Shipped styles" table and before "Pick a style at install":

```markdown
## Schema transition in progress

The 5 shipped style files are being migrated from a rendering-rules-in-markdown schema to a slim schema where `pandoc --citeproc` + vendored CSL files own all rendering. During the migration, some style.md files carry dead-weight old rendering-rule sections (§Inline citations, §References list, §Footnote citations, §Numbering rules) that `[formatting mode]` no longer reads. The dead-weight will be removed in the final migration PR. See `docs/specs/2026-04-19-csl-direct-consumption-design.md` for the full shift description.
```

- [ ] **Step 3: Commit.**

```bash
git add docs/STYLES.md
git commit -m "Document schema transition in docs/STYLES.md"
```

---

## Phase 4 — PR2: §7 rewrite + install.sh upgrade + slim NB, IEEE, MLA

**Goal of this PR:** Rewrite CLAUDE.md §7 [formatting mode] to the new pandoc-centric procedure. Upgrade install.sh to check pandoc ≥ 3.1 and cross-check CSL `<title>` against style.md provenance. Fully slim three shipped styles: chicago17-nb, ieee, mla9.

### Task 4.1: Rewrite CLAUDE.md §7 [formatting mode]

**Files:**
- Modify: `templates/CLAUDE.md` (replace the `### [formatting mode]` subsection, lines ~359-404 in the current file).

- [ ] **Step 1: Locate the current §7 [formatting mode] block.**

Current start marker: `### [formatting mode]` (approximately line 359). Current end marker: the blank line before `### Mode switching table` (approximately line 405, right before `## 8. Citations`). Replace everything between these markers.

- [ ] **Step 2: Write the new [formatting mode] block.**

Replacement content (paste verbatim; content matches spec §4):

```markdown
### [formatting mode]

*On entry, read `./style.md` in full. If style.md is missing, stop and ask {{USER}} to run `install.sh --style <name>`. Re-read on every entry; do not work from memory of prior sessions.*

*Enter only after the gated handoff from `[editing mode]` ({{USER}} confirmed the prose is ready to format); do not enter on your own judgment that editing is "done".*

Convert source prose with Pandoc-style citation IDs into a fully-rendered document for a specific paste target. This is the terminal stage. Source prose is not modified; output goes to a sibling file. Rendering is delegated to `pandoc --citeproc` reading the style's vendored CSL file; the procedure below is uniform across all paste targets and all style Shapes.

**Mode invocation carries the paste target.** Examples: `[formatting mode for google-docs]`, `[formatting mode for plain-markdown]`, `[formatting mode for word]`. The target is required; if {{USER}} says "format this" without a target, ask which one. Supported targets are listed under `§Paste target expression rules` in style.md; if the named target isn't present, refuse and surface to {{USER}} rather than guessing.

**Procedure (run in this order; halt on the first failure).**

1. **Read style.md and the citation log.** Verify style.md's `§Style identity.CSL provenance.file` resolves to an existing CSL file on disk (path: `~/.claude/style/<style>/<csl-filename>` per install.sh's layout). Halt if missing.
2. **Pre-flight.** Halt on any of:
   - `[VERIFY: ...]` tokens in source prose — unresolved verification debt.
   - `[UNSOURCED]` tokens in source prose — claims with no source.
   - Rendered citation strings (e.g., `(Smith, 2010)`, `Smith (2010)`, `[1]`) anywhere in source prose, including inside block quotes. These should have been converted to Pandoc IDs in `[editing mode]`. Surface and ask {{USER}} whether to convert in place or return to `[editing mode]`.
   - Citation IDs that don't resolve to a log entry. Surface unresolved IDs by line.
   - **Stale `retrieved_at`** on any id referenced in source prose (per schema.md §Staleness). Collect every stale entry first; do not prompt one-by-one. Grouped report (id, `retrieved_at` or "missing", source URL, reference count). Per-entry choices: re-fetch and re-verify (preferred for web sources), accept as-is (acceptable for stable DOIs), treat as gap and return to `[editing mode]`. Offer "re-fetch all" / "accept all" / mixed shortcuts. "Accept as-is" holds for this format pass only.
   - **Inline direct quotes in source prose exceeding the block-quote threshold declared in `§Document layout.Block quotes`** of style.md. This is an LLM-judgment check over quotation-marked spans in prose; it reads the threshold value (e.g., "40 words", "4 lines") and flags plausible exceedances. Surface and refuse; user returns to `[editing mode]` to convert the inline quote to a block quote. `[formatting mode]` does not rewrite prose.
3. **Pre-pandoc pass.** Copy source prose to `<draft>.pandoc.md`; collapse per-instance citation IDs (regex `<author>-<year>-\d{3}` → `<author>-<year>`) in the copy. Source `<draft>.md` is NEVER modified.
4. **Emit CSL-JSON bibliography** from the citation log to `<draft>.bib.json`, following `~/.claude/citations/csl-json-emitter.md` (the emitter specification). One entry per unique source, keyed to the collapsed id. Filter the log to ids actually referenced in source prose; dead log entries are not emitted. Tolerable emitter warnings (per the specification's §Source-type inference fallback rule) are collected for the step 8 report but do not halt.
5. **Invoke pandoc.** Read flags from style.md `§Paste target expression rules.<target>.pandoc flags`. Per-target output routing:
   - `word` → `<draft>.docx`
   - `google-docs` → `<draft>.gdocs.md`
   - `plain-markdown` → `<draft>.plain.md`

   The invocation shape is: `pandoc <flags> --bibliography=<draft>.bib.json --csl=<csl-path> -o <output> <draft>.pandoc.md`. The `--reference-doc=<path>` flag applies only when style.md `§Paste target expression rules.word` declares a reference.docx path.
6. **Handle pandoc exit and stderr.**
   - Non-zero exit: halt; surface stderr in full.
   - Exit 0 with stderr non-empty: classify warnings per the table in `§Citeproc warning classification` below. Blocking warnings halt before writing output; tolerable warnings pass through to the step 8 report.
7. **Post-pandoc pass.**
   - Apply `§Style identity.On-demand references` transforms if declared. For chicago17-ad and chicago17-nb, this is the classical-abbreviations rewrite: walk the rendered output; for each bibliography entry and (for NB) each footnote body, read back to the CSL-JSON entry that produced it; if the entry's `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Other styles: skip.
   - Prepend paste-time instruction strings from `§Paste target expression rules.<target>.Paste-time instructions` to the output file (single line(s) at the top, each prefixed with a conventional marker like `<!-- paste-time: -->`).
8. **Report to {{USER}}.** One paragraph: source file, target, output sibling file, citations resolved, unique References entries, stale `retrieved_at` handled (re-fetched / accepted / gap), tolerable pandoc or emitter warnings surfaced, any paste-time instructions {{USER}} must apply (e.g., "apply hanging indent in Google Docs after pasting"). Do not summarize the prose itself.

**Citeproc warning classification.**

| Warning pattern | Classification | Action |
|-----------------|----------------|--------|
| "reference not found" / "citation [@id] not resolved" | Blocking | Halt before writing output. |
| "missing field: type" on an entry in the emitted CSL-JSON | Blocking | Halt — CSL `type` drives rendering; fix the emitter inference path, don't let the default fire silently. |
| "missing field: DOI" / "missing field: URL" on applicable types | Tolerable | Surface in report. |
| "missing field: publisher-place" / other optional fields | Tolerable | Surface in report. |
| "unrecognized element" or similar CSL-parse warning | Blocking | Halt — CSL file is suspect. |

**What [formatting mode] does NOT do:**
- Edit prose. Voice rules, claim revisions, citation re-attribution, block-quote conversion all belong upstream (in `[editing mode]` or earlier).
- Add or modify citation log entries. The log is read-only here, with one carve-out: when {{USER}} chooses "re-fetch and re-verify" on a stale entry in step 2, you update that entry's `retrieved_at` (and `source.authors` if the byline has changed) before rendering. Note the update in the step 8 report.
- Choose a style. Style is fixed by `style.md`. Switching styles means re-running with a different `style.md` (via `install.sh --style <name>` and re-formatting), not improvising in this mode.
- Branch on Shape. Shape is audit metadata in the slim schema; pandoc+CSL owns Shape-specific rendering. The procedure above is uniform for author-date, author-page, footnote, numeric-sequence, and numeric-alpha styles.

**Re-running formatting** is cheap and idempotent. If {{USER}} changes style.md, re-run formatting on the same source. If {{USER}} wants a different paste target (e.g., google-docs and plain-markdown both), run formatting twice with different invocations; each writes its own sibling file. The source `.md` and the citation log are unchanged (modulo the staleness carve-out above).
```

- [ ] **Step 3: Verify §8 and §10 references still resolve.**

Grep for remaining references to the old §7 structure:

```bash
grep -n "§7 step" templates/CLAUDE.md
grep -n "formatting mode.*step" templates/CLAUDE.md
```

Expected matches: §8 may reference §7 step numbers. Cross-check that the step numbers in §8 still point at the right steps under the new procedure:
- §8 Moment 3 should reference "the procedure in §7 [formatting mode]" without step numbers; if step numbers appear, re-point them.
- §8's "`[formatting mode]`'s pre-flight (§7)" references should remain valid (step 2 is still pre-flight).

Update any step-number references that have shifted. The new procedure has 8 steps; the old had 8 steps too, with broadly the same responsibilities (pre-flight is step 2 in both), so most references should pass through unchanged.

- [ ] **Step 4: Commit.**

```bash
git add templates/CLAUDE.md
git commit -m "Rewrite CLAUDE.md §7 [formatting mode] for pandoc+CSL pipeline"
```

---

### Task 4.2: Upgrade `install.sh` pandoc version check

**Files:**
- Modify: `install.sh` (`check_prerequisites` function, lines ~68-91)

- [ ] **Step 1: Read the current `check_prerequisites` function.**

Currently checks for `pandoc` presence only. Replace with a presence + version check.

- [ ] **Step 2: Replace `check_prerequisites`.**

Replace the existing function definition with:

```bash
check_prerequisites() {
  # Tools required by the framework at runtime. pdftotext/pdftoppm come from
  # poppler-utils; Claude Code's built-in Read uses pdftoppm for PDF rendering,
  # and [research mode] uses pdftotext.
  # pandoc 3.1+ with citeproc is required by every [formatting mode] paste
  # target (word, google-docs, plain-markdown). python3 is used at style-install
  # to cross-check the CSL <title> against style.md provenance.
  local missing=()
  command -v pdftotext >/dev/null 2>&1 || missing+=("poppler-utils (pdftotext, pdfinfo, pdftoppm)")
  command -v python3   >/dev/null 2>&1 || missing+=("python3")

  if ! command -v pandoc >/dev/null 2>&1; then
    missing+=("pandoc 3.1 or newer")
  else
    # pandoc --version first line looks like "pandoc 3.1.9" or "pandoc.exe 3.1.9".
    local pandoc_version
    pandoc_version=$(pandoc --version | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n1)
    local major minor
    major=${pandoc_version%%.*}
    minor=${pandoc_version#*.}
    minor=${minor%%.*}
    if [[ -z "${major}" || -z "${minor}" ]]; then
      missing+=("pandoc 3.1 or newer (detected unparseable version: $(pandoc --version | head -n1))")
    elif (( major < 3 || (major == 3 && minor < 1) )); then
      missing+=("pandoc 3.1 or newer (detected ${pandoc_version}; Ubuntu 22.04 and older apt ships 2.9 and is below minimum)")
    fi
  fi

  [[ ${#missing[@]} -eq 0 ]] && return 0

  echo "Missing prerequisites:" >&2
  for tool in "${missing[@]}"; do
    echo "  - ${tool}" >&2
  done
  echo "" >&2
  echo "Install on Debian/Ubuntu 24.04+/WSL Ubuntu 24.04+:" >&2
  echo "  sudo apt-get install -y poppler-utils pandoc python3" >&2
  echo "" >&2
  echo "Install on Debian/Ubuntu 22.04 or older (apt pandoc is 2.9, too old):" >&2
  echo "  sudo apt-get install -y poppler-utils python3" >&2
  echo "  # then install pandoc 3.1+ from https://github.com/jgm/pandoc/releases" >&2
  echo "" >&2
  echo "Install on macOS:" >&2
  echo "  brew install poppler pandoc python3" >&2
  echo "" >&2
  echo "Install on Windows (PowerShell as admin):" >&2
  echo "  winget install --id JohnMacFarlane.Pandoc" >&2
  echo "  winget install --id Python.Python.3" >&2
  exit 1
}
```

- [ ] **Step 3: Manually test the version check.**

Run:

```bash
bash -c 'pandoc --version | head -n1'
```

Expected: a version string. If your installed pandoc is 2.x (possible on older Ubuntu), run `./install.sh --global-only` from a scratch dir; expect the install to halt with the "pandoc 3.1 or newer" error and the matrix hints. If your pandoc is 3.1+, the install proceeds.

- [ ] **Step 4: Commit.**

```bash
git add install.sh
git commit -m "Require pandoc 3.1+ and python3 in install.sh prerequisites"
```

---

### Task 4.3: Add CSL-title cross-check to `install.sh`

**Files:**
- Modify: `install.sh` (add a new validation function; call it from the per-project style rendering flow, after `STYLE_SOURCE` is resolved at ~line 293).

- [ ] **Step 1: Add the `validate_csl_title` function.**

Insert this function definition BEFORE the `# ---- style preflight:` block (around line 280, immediately before `DEST_STYLE="${TARGET_DIR}/style.md"`). Rationale: bash functions must be defined before they are called, and the call site (Step 2) is inside the style preflight block. Placing the definition after the call site (e.g., before `# ---- step 2: per-project CLAUDE.md`) would fail at runtime with "command not found".

```bash
# Cross-check the vendored CSL file's <title> against the style.md's declared
# CSL provenance title. Catches "shipped the wrong CSL file" before the user
# sees a mis-rendered document in [formatting mode]. Runs python3 to parse the
# CSL XML properly; grep would false-positive on <title> elements nested
# elsewhere in the CSL structure.
#
# Arguments: style_source (path to style.md), style_name.
# Returns 0 on match (or if style.md declares no CSL provenance, which is
# allowed for legacy styles during the migration). Returns 1 on mismatch.
validate_csl_title() {
  local style_source="$1" style_name="$2"
  local declared_title csl_rel_path csl_abs_path actual_title

  declared_title=$(awk '
    /^  - CSL title:/ {
      # Extract content between the first pair of double quotes on this line.
      # Handles trailing prose after the closing quote (e.g., "...title..." (note)).
      # If no quotes are present, fall back to the post-colon content trimmed.
      line = $0
      sub(/^  - CSL title:[[:space:]]*/, "", line)
      if (match(line, /"[^"]*"/)) {
        print substr(line, RSTART + 1, RLENGTH - 2)
      } else {
        # No quotes — use the whole trimmed remainder.
        sub(/^[[:space:]]+/, "", line)
        sub(/[[:space:]]+$/, "", line)
        print line
      }
      exit
    }
  ' "${style_source}")
  csl_rel_path=$(awk '/^  - file:/{sub(/^  - file:[[:space:]]*/, ""); print; exit}' "${style_source}")

  # If neither is declared, skip (legacy style.md pre-schema; migration window).
  if [[ -z "${declared_title}" && -z "${csl_rel_path}" ]]; then
    return 0
  fi

  if [[ -z "${csl_rel_path}" ]]; then
    echo "Warning: ${style_source} declares a CSL title but no CSL provenance file path; skipping cross-check." >&2
    return 0
  fi

  csl_abs_path="${REPO_DIR}/templates/styles/${csl_rel_path}"
  if [[ ! -f "${csl_abs_path}" ]]; then
    echo "Error: ${style_source} declares CSL provenance file '${csl_rel_path}' but ${csl_abs_path} does not exist." >&2
    return 1
  fi

  actual_title=$(python3 - "${csl_abs_path}" <<'PYEOF'
import sys, xml.etree.ElementTree as ET
path = sys.argv[1]
tree = ET.parse(path)
root = tree.getroot()
# CSL namespace: http://purl.org/net/xbiblio/csl
ns = {'csl': 'http://purl.org/net/xbiblio/csl'}
info = root.find('csl:info', ns)
if info is None:
    print("")
    sys.exit(0)
title = info.find('csl:title', ns)
print(title.text.strip() if title is not None and title.text else "")
PYEOF
)

  if [[ -z "${declared_title}" ]]; then
    echo "Warning: ${style_source} declares CSL file '${csl_rel_path}' but no CSL title; skipping cross-check." >&2
    return 0
  fi

  if [[ "${actual_title}" != "${declared_title}" ]]; then
    echo "Error: CSL title mismatch for style '${style_name}'." >&2
    echo "  declared in ${style_source}: '${declared_title}'" >&2
    echo "  actual in  ${csl_abs_path}: '${actual_title}'" >&2
    echo "" >&2
    echo "Either the shipped CSL file is wrong, or the style.md provenance declaration drifted." >&2
    echo "Re-vendor the correct CSL file from github.com/citation-style-language/styles or update style.md." >&2
    return 1
  fi

  return 0
}
```

- [ ] **Step 2: Call `validate_csl_title` from the per-project style flow.**

Locate the per-project style flow (the block starting with `# ---- step 4: per-project style` around line 558). Add the call immediately after the `STYLE_SOURCE` existence check passes, before the `render_style` invocations. Specifically, insert after line ~301:

```bash
if ! validate_csl_title "${STYLE_SOURCE}" "${STYLE}"; then
  exit 1
fi
```

The exact insertion site is after the existing `STYLE_SOURCE` not-found check in the "style preflight" block (right before `# Extracts iron rules from a voice library file.`).

- [ ] **Step 3: Test the check.**

Pick a shipped style with CSL provenance declared (ieee or mla9 both have it). Run:

```bash
./install.sh --global-only
```

Expected: exit 0. The validation passes because the declared title matches the CSL's actual `<title>` element (assuming no drift).

To exercise the failure path, temporarily edit a style.md (e.g., `templates/styles/ieee.md`) to change the declared `CSL title:` to something wrong. Run install; expect a mismatch error. Revert the edit.

- [ ] **Step 4: Commit.**

```bash
git add install.sh
git commit -m "Add CSL <title> cross-check to install.sh per-project style flow"
```

---

### Task 4.4: Slim `templates/styles/chicago17-nb.md`

**Files:**
- Modify: `templates/styles/chicago17-nb.md` (full rewrite to slim schema).

- [ ] **Step 1: Read the current chicago17-nb.md and PR2a-updated sections.**

After PR2a, §Document layout and §Style identity.On-demand references are already in slim-schema shape. The rest of the file (350 lines total) contains old sections to remove: §Footnote citations, §Bibliography, §Direct quotes, plus any style-specific appendices.

- [ ] **Step 2: Write the slim chicago17-nb.md.**

Target file (paste-target subsection pandoc flags per current `§Paste target expression rules` subsections in the old file; fill each one per the old content, reformatting to the new pinned-flags shape):

```markdown
# Style: Chicago 17 (Notes-Bibliography)

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline footnotes, short-form references, ibid. behavior, and bibliography entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

## Style identity

- Name: Chicago Manual of Style, 17th edition — Notes and Bibliography system.
- Shape: footnote
- In-text marker: footnote
- List heading: Bibliography
- Authority: The Chicago Manual of Style, 17th ed. (University of Chicago Press, 2017), chapters 14 (notes and bibliography) and 13 (quotations).
- Default for: history, theology, art history, classics, and other humanities using footnote citation.
- Source consulted:
  - https://www.chicagomanualofstyle.org/ (publisher-run; subscription; edition confirmation and sample paper); accessed 2026-04-19.
  - Sample paper: https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html (free portion, notes-bibliography examples); accessed 2026-04-19.
- CSL provenance:
  - file: chicago17-nb/chicago-notes-bibliography-17th-edition.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "Chicago Manual of Style 17th edition (note)"
- On-demand references:
  - `chicago17-ad/classical-abbreviations.md` — shared with chicago17-ad.
  - Hook: after pandoc renders output, walk each footnote body and each bibliography entry; for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
- Last reviewed: 2026-04-19.

## Document layout

### Fonts and spacing
[copy the current content from chicago17-nb.md §Document layout → Fonts or equivalent]

### Margins
[copy current content]

### Heading hierarchy
[copy current content]

### Title block
[copy current content]

### Page numbering
[copy current content]

### Footnotes
[copy current content — NB uses footnotes substantively, so this subsection is load-bearing for the destination's footnote rendering, not for citation content]

### Block quotes
Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10. `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present.

## Paste target expression rules

### google-docs
- pandoc flags: `--citeproc --wrap=none -t markdown-smart`
- Paste-time instructions:
  - "Apply hanging indent to Bibliography after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "Footnotes paste as inline markers in Google Docs; convert to Google Docs footnotes using Insert > Footnote if needed. Google Docs does not round-trip pandoc `[^N]: body` blocks into native footnotes automatically."
- Post-pandoc transforms: classical-abbreviations rewrite (see §Style identity.On-demand references).

### plain-markdown
- pandoc flags: `--citeproc --wrap=preserve -t markdown`
- Paste-time instructions: (none)
- Post-pandoc transforms: classical-abbreviations rewrite.

### word
- pandoc flags: `--citeproc --reference-doc=~/.claude/style/chicago17-nb/reference-styled.docx`
- reference.docx: `chicago17-nb/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging Bibliography paragraph style, footnote paragraph style. Optional; on absence, pandoc default layout; surface as a tolerable warning in the step 8 report.
- Post-pandoc transforms: classical-abbreviations rewrite.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
```

When filling in `[copy current content]` sections: read the current chicago17-nb.md's §Document layout subsections and paste the existing content verbatim into the new subsection structure. Preserve every fact; only reorganize.

- [ ] **Step 3: Overwrite chicago17-nb.md with the slim content.**

Use the Write tool. Do not leave any section from the old file behind except what's in the slim schema.

- [ ] **Step 4: Run the parity harness for chicago17-nb.**

```bash
cd tests/parity/chicago17-nb/
./run.sh
```

Expected: three `OK` lines (plain-markdown, google-docs, word.docx.md). If any FAIL, the slimming may have removed a §Document layout rule the hand-authored golden depended on; re-read the golden, identify the rule, and either (a) restore it in the slim file under §Document layout if it's genuinely a layout rule, or (b) fix the golden if it leaked a rendering-rule choice (those are now CSL's, not ours).

- [ ] **Step 5: Commit.**

```bash
git add templates/styles/chicago17-nb.md
git commit -m "Slim chicago17-nb.md to pandoc+CSL schema"
```

---

### Task 4.5: Slim `templates/styles/ieee.md`

**Files:**
- Modify: `templates/styles/ieee.md`.

- [ ] **Step 1: Apply the same slim-schema shape as Task 4.4 to ieee.md.**

The slim template for IEEE:

```markdown
# Style: IEEE

## Style identity

- Name: IEEE (Institute of Electrical and Electronics Engineers).
- Shape: numeric-sequence
- In-text marker: bracket-number
- List heading: References
- Authority: IEEE Reference Guide, version 11.29.2023, maintained by the IEEE Author Center.
- Default for: electrical engineering, computer engineering, computer science, IEEE venues.
- Source consulted:
  - https://ieeeauthorcenter.ieee.org/ ; accessed 2026-04-19.
  - https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/ ; accessed 2026-04-19.
- CSL provenance:
  - file: ieee/ieee.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "IEEE"
- On-demand references: (none)
- Last reviewed: 2026-04-19.

## Document layout

[five subsections — Fonts and spacing, Margins, Heading hierarchy, Title block, Page numbering — copied from the current ieee.md §Document layout; plus §Block quotes:]

### Block quotes
Threshold: none. IEEE has no prescribed block-quote threshold; writers use editorial judgment.

## Paste target expression rules

### google-docs
- pandoc flags: `--citeproc --wrap=none -t markdown-smart`
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
- Post-pandoc transforms: (none)

### plain-markdown
- pandoc flags: `--citeproc --wrap=preserve -t markdown`
- Paste-time instructions: (none)
- Post-pandoc transforms: (none)

### word
- pandoc flags: `--citeproc --reference-doc=~/.claude/style/ieee/reference-styled.docx`
- reference.docx: `ieee/reference-styled.docx` — Times New Roman 10pt / two-column body, single-spaced References with hanging indent, per IEEE manuscript template. Optional; on absence, pandoc default layout; surface tolerable warning.
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time.
```

**Verify the CSL title.** Before writing, confirm the CSL title declared above matches the actual CSL file at `templates/styles/ieee/ieee.csl`. Run:

```bash
python3 -c "
import xml.etree.ElementTree as ET
ns = {'csl': 'http://purl.org/net/xbiblio/csl'}
root = ET.parse('templates/styles/ieee/ieee.csl').getroot()
print(root.find('csl:info/csl:title', ns).text)
"
```

If the printed title differs from `"IEEE"`, use the printed title in the slim file's `CSL title:` field. (The current ieee.md declares `"IEEE Reference Guide version 11.29.2023"`, but what matters is that the slim file declares what the CSL file actually says.)

- [ ] **Step 2: Overwrite ieee.md with the slim content.**

- [ ] **Step 3: Run the parity harness for ieee.**

```bash
cd tests/parity/ieee/
./run.sh
```

Expected: three OK lines. Triage per Task 4.4 step 4 if any fail.

- [ ] **Step 4: Commit.**

```bash
git add templates/styles/ieee.md
git commit -m "Slim ieee.md to pandoc+CSL schema"
```

---

### Task 4.6: Slim `templates/styles/mla9.md`

**Files:**
- Modify: `templates/styles/mla9.md`.

- [ ] **Step 1: Apply the slim-schema shape to mla9.md.**

Slim template:

```markdown
# Style: MLA 9

## Style identity

- Name: MLA 9th edition.
- Shape: author-page
- In-text marker: parenthetical
- List heading: Works Cited
- Authority: MLA Handbook, 9th edition (Modern Language Association of America, 2021), chapters 5-6 (citations), chapter 1 (manuscript layout).
- Default for: literary studies, languages, humanities essays.
- Source consulted:
  - https://style.mla.org/ ; accessed 2026-04-19.
  - MLA Handbook, 9th ed. (print).
- CSL provenance:
  - file: mla9/modern-language-association.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: [fill from the CSL file; run the python3 check as in Task 4.5 step 1]
- On-demand references:
  - (none; classical texts in MLA context may cross-reference chicago17-ad/classical-abbreviations.md but no hook fires — MLA does not prescribe classical abbreviation)
- Last reviewed: 2026-04-19.

## Document layout

[five subsections copied from current mla9.md, plus §Block quotes:]

### Block quotes
Threshold: 4 lines of prose, 3 lines of verse (MLA 9 §6.36). Verse quotations use a slash `/` with spaces to mark line breaks when inline; block form for 4+ lines of prose / 3+ lines of verse with no quotation marks. `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2).

## Paste target expression rules

### google-docs
- pandoc flags: `--citeproc --wrap=none -t markdown-smart`
- Paste-time instructions:
  - "Apply hanging indent to Works Cited after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "MLA page-number header ('Smith 3') requires a custom Google Docs header; add via Insert > Headers > Header, then type surname + page number."
- Post-pandoc transforms: (none)

### plain-markdown
- pandoc flags: `--citeproc --wrap=preserve -t markdown`
- Paste-time instructions: (none)
- Post-pandoc transforms: (none)

### word
- pandoc flags: `--citeproc --reference-doc=~/.claude/style/mla9/reference-styled.docx`
- reference.docx: `mla9/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging Works Cited, "Lastname N" page-number header. Optional; on absence, pandoc default layout; surface tolerable warning.
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time.
```

- [ ] **Step 2: Overwrite mla9.md with the slim content.**

- [ ] **Step 3: Run the parity harness for mla9.**

```bash
cd tests/parity/mla9/
./run.sh
```

Expected: three OK lines.

- [ ] **Step 4: Commit.**

```bash
git add templates/styles/mla9.md
git commit -m "Slim mla9.md to pandoc+CSL schema"
```

---

### Task 4.7: Update `docs/STYLES.md` to the new schema

**Files:**
- Modify: `docs/STYLES.md` (replace "Style file structure", "How `[formatting mode]` uses style.md", and relevant sections).

- [ ] **Step 1: Replace the "Style file structure" section.**

Locate `## Style file structure`. Replace the existing table and section-role prose with:

```markdown
## Style file structure

Each style file has a fixed section structure so `[formatting mode]` can look up rules by section name. Sections are addressable (e.g., "see §Style identity.CSL provenance", "see §Paste target expression rules.google-docs"). The required sections are the same for every style; rendering of inline citations, references, and footnotes is delegated to `pandoc --citeproc` reading the vendored CSL file.

Required sections (every style):

| Section | Role |
|---------|------|
| §Style identity | Name, Shape (audit-only), In-text marker (audit-only), List heading (runtime-read), Authority, Default for, Source consulted, CSL provenance (file / source / fetched / CSL title), On-demand references (post-pandoc hook per style), Last reviewed. |
| §Document layout | Fonts and spacing, Margins, Heading hierarchy, Title block, Page numbering, (optional) Footnotes, Block quotes (threshold if any — enforced in `[editing mode]`, verified in `[formatting mode]` pre-flight). |
| §Paste target expression rules | Per-target subsections (google-docs, plain-markdown, word): pandoc flags, paste-time instructions, post-pandoc transforms, reference.docx path (word only). |
| §Special tokens | `[VERIFY: ...]` and `[UNSOURCED]` policy. Most styles carry the standard block. |
```

Remove the old Shape-keyed required-sections table (`author-date`, `author-page`, `footnote`, `numeric-sequence`, `numeric-alpha` columns) — no longer needed; the schema is uniform across shapes.

- [ ] **Step 2: Replace the "Paste targets" section.**

Locate `## Paste targets`. Replace with:

```markdown
## Paste targets

`[formatting mode]` renders into one of the target formats defined under the style's `§Paste target expression rules` section. The target is required at mode invocation: `[formatting mode for google-docs]`, `[formatting mode for plain-markdown]`, `[formatting mode for word]`. An unspecified target is a refusal, not a default.

All three targets are rendered by `pandoc --citeproc` reading the style's vendored CSL file. Flags per target (including output markdown dialect, wrap behavior, and reference.docx) live in the style's `§Paste target expression rules` subsections.

- **`google-docs`** — markdown output tuned for Google Docs paste (smart quotes, en-dashes preserved). Features not expressible at paste time (hanging indents, custom headers) surface as a one-line instruction at the top of the output.
- **`plain-markdown`** — faithful markdown pass-through.
- **`word`** — pandoc emits `.docx` directly, optionally styled by a reference.docx bundled per style.
- **`latex`** — reserved; not implemented.
```

- [ ] **Step 3: Replace the "How `[formatting mode]` uses style.md" section.**

Replace the abbreviated procedure with the new one (matching CLAUDE.md §7):

```markdown
## How `[formatting mode]` uses `style.md`

`[formatting mode]` is the only mode that reads `style.md`. All other modes emit style-agnostic Pandoc IDs, so source prose is decoupled from style choice. Switching styles is cheap: `install.sh --style <new>` then re-run formatting.

The formatting procedure (abbreviated; see CLAUDE.md §7 for the full version):

1. Read `style.md` + the citation log. Verify CSL file exists on disk.
2. Pre-flight. Halt on `[VERIFY: ...]`, `[UNSOURCED]`, rendered citation strings, unresolved IDs, stale `retrieved_at`, or inline direct quotes exceeding the style's block-quote threshold.
3. Pre-pandoc pass: collapse per-instance citation IDs into a derived `<draft>.pandoc.md`. Source prose unchanged.
4. Emit CSL-JSON bibliography from the log to `<draft>.bib.json` per `citations/csl-json-emitter.md`.
5. Invoke pandoc with flags from `§Paste target expression rules.<target>`; output per target (`.docx`, `.gdocs.md`, `.plain.md`).
6. Handle pandoc stderr: halt on blocking warnings (unresolved citation, missing type, CSL-parse error); surface tolerable warnings in the report.
7. Post-pandoc pass: apply On-demand references transforms (e.g., classical-abbreviations rewrite); prepend paste-time instructions.
8. Report.

Re-running with a different style or target is idempotent: each run writes its own sibling file.
```

- [ ] **Step 4: Remove the "Schema transition in progress" section added in PR2a.**

Locate and delete the transition note (it described the dead-weight window; PR3 will finish the migration, at which point the window is only one PR wide).

Actually — keep it in place with an updated message. Replace the PR2a transition note with:

```markdown
## Schema transition in progress

The 5 shipped style files are mid-migration from a rendering-rules-in-markdown schema to the slim schema above. After this PR, chicago17-nb, ieee, and mla9 are fully slim; apa7 and chicago17-ad still carry dead-weight old rendering-rule sections (§Inline citations, §References list, §Footnote citations, §Numbering rules) that `[formatting mode]` no longer reads. The dead-weight will be removed in the next (final) migration PR. See `docs/specs/2026-04-19-csl-direct-consumption-design.md` for the full shift description.
```

- [ ] **Step 5: Commit.**

```bash
git add docs/STYLES.md
git commit -m "Update docs/STYLES.md for slim-schema + pandoc+CSL pipeline"
```

---

## Phase 5 — PR3: Slim remaining styles (apa7, chicago17-ad)

**Goal of this PR:** Remove dead-weight rendering-rule sections from apa7.md and chicago17-ad.md, bringing all 5 shipped styles onto the slim schema. Final cleanup PR; no §7 changes.

### Task 5.1: Slim `templates/styles/apa7.md`

**Files:**
- Modify: `templates/styles/apa7.md`.

- [ ] **Step 1: Apply the slim-schema shape.**

Slim template:

```markdown
# Style: APA 7

## Style identity

- Name: APA 7th edition.
- Shape: author-date
- In-text marker: parenthetical
- List heading: References
- Authority: Publication Manual of the American Psychological Association, 7th edition (American Psychological Association, 2020).
- Default for: psychology, education, behavioral and social sciences.
- Source consulted:
  - https://apastyle.apa.org/ ; accessed 2026-04-19.
- CSL provenance:
  - file: apa7/apa.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: [fill from the CSL file; run the python3 check as in Task 4.5 step 1]
- On-demand references: (none)
- Last reviewed: 2026-04-19.

## Document layout

[five subsections — Fonts and spacing, Margins, Heading hierarchy, Title block, Page numbering — copied from current apa7.md; plus §Block quotes:]

### Block quotes
Threshold: 40 words. Direct quotes of 40 words or more are rendered as block quotes in source prose (indented, no surrounding quotation marks, citation after the closing punctuation). `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present.

## Paste target expression rules

### google-docs
- pandoc flags: `--citeproc --wrap=none -t markdown-smart`
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
- Post-pandoc transforms: (none)

### plain-markdown
- pandoc flags: `--citeproc --wrap=preserve -t markdown`
- Paste-time instructions: (none)
- Post-pandoc transforms: (none)

### word
- pandoc flags: `--citeproc --reference-doc=~/.claude/style/apa7/reference-styled.docx`
- reference.docx: `apa7/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging References, APA title page layout. Optional; on absence, pandoc default layout; surface tolerable warning. (Not yet shipped; ship separately.)
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time.
```

**Note: apa.csl was vendored during PR1** (commit `6f8fed3`). `templates/styles/apa7/apa.csl` already exists; the CSL provenance block in `apa7.md` already points at it. No vendoring step needed in PR3 — just slim the style.md file.

Verify the vendored file is still present before proceeding:

```bash
ls -la templates/styles/apa7/apa.csl
# Should exist; ~2000 lines
```

- [ ] **Step 2: Overwrite apa7.md.**

- [ ] **Step 3: Run the parity harness for apa7.**

```bash
cd tests/parity/apa7/
./run.sh
```

Expected: three OK lines.

- [ ] **Step 4: Commit.**

```bash
git add templates/styles/apa7.md
git commit -m "Slim apa7.md to pandoc+CSL schema"
```

---

### Task 5.2: Slim `templates/styles/chicago17-ad.md`

**Files:**
- Modify: `templates/styles/chicago17-ad.md`.

- [ ] **Step 1: Apply the slim-schema shape.**

Slim template:

```markdown
# Style: Chicago 17 (Author-Date)

## Style identity

- Name: Chicago Manual of Style, 17th edition — Author-Date system.
- Shape: author-date
- In-text marker: parenthetical
- List heading: References
- Authority: The Chicago Manual of Style, 17th ed. (University of Chicago Press, 2017), chapter 15 (author-date system).
- Default for: social sciences using Chicago with parenthetical citation.
- Source consulted:
  - https://www.chicagomanualofstyle.org/ ; accessed 2026-04-19.
- CSL provenance:
  - file: chicago17-ad/chicago-author-date-17th-edition.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "Chicago Manual of Style 17th edition (author-date)"
- On-demand references:
  - `chicago17-ad/classical-abbreviations.md` — classical-author abbreviation table.
  - Hook: after pandoc renders output, walk each bibliography entry; for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
- Last reviewed: 2026-04-19.

## Document layout

[five subsections copied from current chicago17-ad.md, plus §Block quotes:]

### Block quotes
Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10.

## Paste target expression rules

### google-docs
- pandoc flags: `--citeproc --wrap=none -t markdown-smart`
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
- Post-pandoc transforms: classical-abbreviations rewrite.

### plain-markdown
- pandoc flags: `--citeproc --wrap=preserve -t markdown`
- Paste-time instructions: (none)
- Post-pandoc transforms: classical-abbreviations rewrite.

### word
- pandoc flags: `--citeproc --reference-doc=~/.claude/style/chicago17-ad/reference-styled.docx`
- reference.docx: `chicago17-ad/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging References. Optional; on absence, pandoc default layout; surface tolerable warning.
- Post-pandoc transforms: classical-abbreviations rewrite.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time.
```

- [ ] **Step 2: Overwrite chicago17-ad.md.**

- [ ] **Step 3: Run the parity harness for chicago17-ad.**

```bash
cd tests/parity/chicago17-ad/
./run.sh
```

Expected: three OK lines.

- [ ] **Step 4: Commit.**

```bash
git add templates/styles/chicago17-ad.md
git commit -m "Slim chicago17-ad.md to pandoc+CSL schema"
```

---

### Task 5.3: Remove "Schema transition in progress" from `docs/STYLES.md`

**Files:**
- Modify: `docs/STYLES.md`.

- [ ] **Step 1: Delete the `## Schema transition in progress` section entirely.**

The migration is complete after PR3; the note is no longer applicable.

- [ ] **Step 2: Run the full parity harness one last time.**

```bash
cd tests/parity/
./run-all.sh
```

Expected: `All styles passed parity.`

- [ ] **Step 3: Commit.**

```bash
git add docs/STYLES.md
git commit -m "Remove migration transition note; shift complete"
```

---

## Post-implementation

After PR3 merges:

1. Update the auto-memory entry at `~/.claude/projects/-home-hayden-sourced/memory/project_csl_architecture_shift.md` — mark the shift as **shipped** rather than approved, note final commit SHAs.
2. Update ROADMAP.md — the 8 tier-2 styles (Vancouver, AMA, Harvard, ACM, ACS, Turabian 9, CSE, MHRA) now become mechanical ~15-min-per-style work under the slim schema; adjust timing estimates accordingly.
3. Consider whether the parity harness should become a CI gate. Out of scope for this shift; a separate decision once pandoc-on-CI is on someone's plate.
