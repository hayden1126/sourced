# Style: IEEE

This file specifies every style decision for the project, organized so a model
in [formatting mode] can look up a single rule without rereading the file.
Sections are addressable: "see §Inline citations / Multi-citation", "see
§Reference list / Sort order". Rules are normative; do not improvise.

## Style identity

- Name: IEEE (Institute of Electrical and Electronics Engineers).
- Shape: numeric-sequence
- In-text marker: bracket-number
- List heading: References
- Authority: IEEE Reference Guide, version 11.29.2023 (tracking 2023
  editorial guidelines), maintained by the IEEE author center.
- Default for: electrical engineering, computer engineering, computer
  science, and most IEEE-affiliated conferences and journals.
- Source consulted:
  - https://ieeeauthorcenter.ieee.org/ (IEEE Author Center, publisher-run,
    free); accessed 2026-04-19.
  - https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/
    (IEEE Editorial Style Manual for authors, free); accessed 2026-04-19.
  - https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf
    (direct PDF of the Reference Guide; may redirect to a Google Docs preview
    in some browsers); accessed 2026-04-19.
- CSL provenance:
  - file: ieee/ieee.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "IEEE Reference Guide version 11.29.2023" (matches the
    authority above).
- On-demand references: (none)
- Last reviewed: 2026-04-19.

## Inline citations

Resolution rules for Pandoc-style IDs in source prose. IEEE assigns a number
to each source on first appearance and reuses that number on every
subsequent citation of the same source. Numbers are square-bracketed and
appear inline, treated as a noun or as a trailing reference marker per
context.

See §Numbering rules below for number assignment procedure.

### Single source

- Parenthetical or trailing (`[@id]`): `[1]`.
- Narrative (`@id`): "as shown in [1]", or "per [1]", or "the method in [1]".
  The number is treated as a noun phrase; integrate grammatically.
- With page locator (`[@id, p. 42]`): `[1, p. 42]`. Use "p." for a single
  page, "pp." for a range.
- With page range (`[@id, pp. 42-44]`): `[1, pp. 42-44]`. Hyphen inside the
  brackets, not en-dash.
- With section or chapter (`[@id, ch. 3]`, `[@id, sec. 2.1]`): `[1, ch. 3]`,
  `[1, sec. 2.1]`.

### Multi-citation

- Multiple distinct sources (Pandoc `[@a; @b]`): `[1], [3]`. Each number in
  its own brackets, separated by commas.
- Consecutive number range: `[1]-[3]`. Hyphen between brackets; use the
  range form only when the set is strictly consecutive. Non-consecutive sets
  render as `[1], [3], [5]`.
- Numeric order within a multi-citation is the order the numbers were
  assigned, not the order the ids appear in the Pandoc source.

### No author

Treat the title as the author for numbering purposes. The rendered number is
unchanged; the distinction matters only in the Reference list entry.

### No date

IEEE references always carry a year when the source has one; when genuinely
missing, use `n.d.` in the Reference list entry only. The in-text number is
unchanged.

### Group / corporate author

Treated as a single source for numbering. The organization name appears in
the Reference list entry (see §Reference list / Entry format).

### Direct quotes

- **Inline quote**: standard double quotation marks; number follows the
  closing punctuation: `... "quoted text" [1, p. 42].`
- **Block quote**: IEEE does not codify a strict length threshold; follow
  the target venue's instructions. For general use: 4+ lines of prose block
  quote, indented 0.25 in from left margin, single-spaced, no quotation
  marks, number and page at the end: `... text [1, p. 42].`

## Numbering rules

The number assigned to each source is load-bearing; the References list
order depends on it.

- **Assignment**: numbers are assigned during [formatting mode] step 3c in
  first-appearance order through the source prose (reading top to bottom,
  left to right). First mention of a new source gets the next available
  number; subsequent mentions reuse the assigned number. See CLAUDE.md §7
  step 3 for the procedure.
- **Reset**: within a single document, numbering is continuous; do not reset
  at section boundaries. Multi-chapter documents (theses, long technical
  reports) typically keep a single consolidated References section.
- **Range collapsing**: in multi-citations, collapse consecutive numbers to
  a range (`[1]-[3]`) only when three or more are consecutive. Two
  consecutive numbers render as `[1], [2]` without collapsing.
- **Order within multi-citation**: numeric order, not Pandoc-source order.

## Reference list

### Heading

- Title "References", centered, bold, top of a new page in print formats.
- Markdown destinations: `## References` heading, no centering.

### Sort order

- By assigned number (first-appearance order through the document), not
  alphabetical. Entry N is the N-th source cited.
- Renumbering is expected on draft revisions; the formatter re-runs the
  assignment pass from scratch each format run.

### Entry format (journal article)

`[N] F. Lastname, F. Lastname, and F. Lastname, "Article title in headline case," Journal Name Abbreviation, vol. 42, no. 3, pp. 12-34, Mon. Year, doi: 10.xxxx/yyyy.`

- Entry starts with `[N]` matching the in-text number.
- Authors: initials-first-then-surname form; commas between; "and" before
  the last author. Up to six authors listed; seven or more lists the first
  author only with ", *et al.*" (italicized per some IEEE venues; verify
  with target journal).
- Article title: sentence or headline case per IEEE Reference Guide §B.
  Headline case is the common default; match the target journal.
- Journal title: abbreviated per IEEE journal-title abbreviations list (see
  IEEE author center). Italicized.
- Volume: "vol. 42" unitalicized.
- Issue: "no. 3" unitalicized; omit if the journal does not use issue
  numbers.
- Pages: "pp. 12-34" with hyphen.
- Month: three-letter abbreviation ("Jan.", "Feb.", "Mar.") plus year;
  omit month when not available.
- DOI: lowercase `doi: 10.xxxx/yyyy`. IEEE prefers the bare `doi:` prefix
  over the https://doi.org/ resolver form (differs from APA/Chicago).

### Entry format (conference paper)

`[N] F. Lastname and F. Lastname, "Paper title in headline case," in Proc. Conf. Name Abbrev., City, ST, USA, Year, pp. 12-34, doi: 10.xxxx/yyyy.`

- "in Proc." introduces conference proceedings.
- City + state (US) or city + country (non-US) after the conference name.
- Year placed after location.

### Entry format (book)

`[N] F. Lastname, Book Title in Italics and Headline Case, Nth ed. City, ST, USA: Publisher, Year.`

- Book title italicized, headline case.
- Edition: "2nd ed.", "3rd ed." after the title; omit for first edition.
- City + state (US) or city + country (non-US); colon before publisher.

### Entry format (chapter in edited book)

`[N] F. Lastname, "Chapter title in headline case," in Book Title in Italics, F. Editor and F. Editor, Eds., Nth ed. City, ST, USA: Publisher, Year, ch. 3, pp. 12-34.`

### Entry format (web page)

`[N] F. Lastname. "Page title in headline case." Site Name. Accessed: Mon. DD, Year. [Online]. Available: https://example.com/path`

- "Accessed:" label with month-day-year.
- `[Online]` marker in square brackets.
- "Available:" label before the URL.
- No terminal period after the URL.

### Entry format (standard)

`[N] Standard Number, Standard Title, Publisher, Year.`

- Example: `[1] IEEE 754-2019, IEEE Standard for Floating-Point Arithmetic, IEEE, 2019.`

### Indentation and spacing

- No hanging indent (unlike APA, Chicago). References are flush-left
  numbered entries, similar to a numbered list.
- Single-spaced within entries in print formats. Blank line between entries
  optional.
- The `[N]` marker may be offset (e.g., `[1] ` with a tab) for readability;
  pandoc's default IEEE CSL handles this automatically.

### URLs and DOIs

- DOI format: `doi: 10.xxxx/yyyy` (bare `doi:` prefix; IEEE convention).
- URL format: `Available: https://...` after `[Online].`
- DOI preferred over URL when both exist.

## Document layout

### Fonts and spacing

- Font: Times New Roman 10 pt two-column for IEEE conference and most
  journal formats (per IEEE Word and LaTeX templates). Single-spaced.
- Markdown destinations: font is the destination's choice; the formatter
  does not try to reproduce two-column layout in plain markdown.

### Margins

- IEEE templates specify tight margins; match the template.
- Markdown destinations: margin is the destination's choice.

### Heading hierarchy

IEEE uses all-caps roman numerals for sections in conference/journal
formats (e.g., `I. INTRODUCTION`); subsections use capital letters
(`A. Problem Statement`). Markdown destinations relax this to standard
heading levels.

- Level 1: `## I. Section Title` (or `## Section Title` in relaxed markdown).
- Level 2: `### A. Subsection Title`.
- Level 3: `#### 1) Sub-subsection`.

### Title block

- Conference papers and journal submissions: title centered at top, author
  names + affiliations + email below. IEEE conference templates (LaTeX or
  Word) handle this layout; the paste target should preserve it.
- Markdown destinations: `# Title` at top, blank line, metadata block
  (author / affiliation / date) as plain lines.

### Page numbering

- Not specified in the current style file; IEEE Word/LaTeX templates
  handle page numbering at the template level.

### Footnotes

Footnotes are for substantive content notes, not citation. Numbered
superscript in body, full note at page bottom (Word) or as a numbered list
at section/document end (markdown). The IEEE Reference Guide discourages
footnotes; use sparingly.

### Block quotes

Threshold: none. IEEE has no prescribed block-quote threshold; writers use editorial judgment.

## Paste target expression rules

### google-docs

- Output a single markdown block that pastes cleanly into a Google Doc.
- Preserve heading levels (`##`, `###`); Google Docs renders them.
- Reference list: emit `[1] Author, "Title," Journal, ...` as flat numbered
  entries. Hanging indent is not needed for IEEE (flush-left numbered list
  is standard); no paste-time instruction for indentation.
- Italics: use `*italic*` (Google Docs converts on paste).

### plain-markdown

- Faithful pass-through. Resolve citation IDs and generate References list;
  apply no destination-specific transforms.

### word

- Output two files: `<draft>.docx.md` (rendered markdown intermediate) and
  `<draft>.docx` (submission binary). Source `<draft>.md` is never modified.
- Collapse per-instance citation IDs in the derived `<draft>.docx.md`
  before invoking pandoc. See CLAUDE.md §7 [formatting mode] step 4.
- Dependencies (resolved at install time):
  - pandoc 3.1 or newer (citeproc built in).
  - CSL file at `~/.claude/style/ieee/ieee.csl`. Required.
  - Reference docx expected at `~/.claude/style/ieee/reference-styled.docx`.
    Optional; pandoc default layout used as fallback. IEEE conference
    submissions typically require IEEE's own Word template (downloaded
    from ieeeauthorcenter.ieee.org); for non-submission drafts the
    fallback is adequate.
- Pipeline:
  1. Write the collapsed, fully-resolved markdown to `<draft>.docx.md`.
  2. Generate a source-level bibliography file from the citation log at
     `<draft>.bib.json` (CSL JSON, one entry per unique source keyed to
     collapsed ids).
  3. Invoke `pandoc --citeproc --bibliography=<draft>.bib.json --csl=~/.claude/style/ieee/ieee.csl [--reference-doc=~/.claude/style/ieee/reference-styled.docx] -o <draft>.docx <draft>.docx.md`.
  4. Confirm pandoc exit status is 0 and both output files exist.
- Paste-time instructions: for IEEE submission venues, import the generated
  `.docx` into IEEE's official Word template rather than pasting to a blank
  document; IEEE templates carry two-column layout and font specifications
  the pandoc render does not reproduce.

### latex

- Reserved. Not implemented yet. IEEE provides official LaTeX templates
  (IEEEtran class) for submissions; the eventual LaTeX target will invoke
  pandoc with an IEEEtran-compatible template and the shipped CSL.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format
  time. Formatting mode halts and surfaces every occurrence rather than
  emitting them into the formatted output. See CLAUDE.md §7 ([formatting
  mode] procedure step 2) and §8 (Moment 2).
