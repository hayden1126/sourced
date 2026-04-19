# Style: APA 7

This file specifies every style decision for the project, organized so a model
in [formatting mode] can look up a single rule without rereading the file.
Sections are addressable: "see §Inline / Two authors", "see §References /
Sort order". Rules are normative; do not improvise.

## Style identity

- Name: APA 7th edition.
- Authority: Publication Manual of the American Psychological Association,
  7th edition (2020).
- Default for: behavioral and social sciences; {{USER}}'s primary work.
- Last reviewed: 2026-04-18.

## Inline citations

Resolution rules for Pandoc-style IDs in source prose. Each row is exhaustive
for that case; if a case isn't listed, ask {{USER}} rather than guessing.

### One author
- Parenthetical (`[id]`): `(Smith, 2010)`.
- Narrative (`@id`): `Smith (2010)`.
- With page locator (`[@id, p. 42]`): `(Smith, 2010, p. 42)`.
- With page range (`[@id, pp. 42-44]`): `(Smith, 2010, pp. 42-44)`. En-dash, not hyphen.

### Two authors
- Parenthetical: `(Smith & Jones, 2010)`. Ampersand inside parens.
- Narrative: `Smith and Jones (2010)`. Word "and" outside parens.

### Three or more authors
- Parenthetical: `(Smith et al., 2010)`. Italicize nothing; "et al." is roman.
- Narrative: `Smith et al. (2010)`.
- Exception: if shortening produces an ambiguous citation (two different
  works both shorten to "Smith et al., 2010"), list as many surnames as needed
  to disambiguate, then "et al." Resolve from `source.authors` in the log.

### Group / corporate author
- First mention parenthetical: `(American Psychological Association [APA], 2020)`.
- Subsequent: `(APA, 2020)`.
- Narrative first mention: `the American Psychological Association (APA, 2020)`.
- Subsequent narrative: `APA (2020)`.
- If `source.authors` in the log is a group author with no abbreviation
  registered for the project, use the full name on every mention.

### No author
- Parenthetical: `("Title of Work," 2010)` for articles/chapters,
  `(Title of Work, 2010)` italic for books/reports.
- Use the title (or shortened title) in place of author. Title-case in the
  citation; per APA, sentence-case in the References entry.

### No date
- `n.d.` in place of year: `(Smith, n.d.)`.
- Multiple `n.d.` works by the same author: append lowercase letters,
  `(Smith, n.d.-a)`, `(Smith, n.d.-b)`. Letter assignment matches the
  References list ordering (alphabetical by title, ignoring leading articles).
  The formatting pass assigns letters; do not guess them in source prose.

### Multi-citation
- Pandoc `[@a; @b]` resolves to `(AuthorA, YearA; AuthorB, YearB)`.
- Order: alphabetical by first author's surname (APA 8.12).
- Same author, multiple years: `(Smith, 2008, 2010)`.

### Direct quotes
- Block quote threshold: 40 words.
- Under 40: inline with double quotation marks. Citation immediately follows
  closing quote, before terminal punctuation if mid-sentence: `... "X" (Smith, 2010, p. 42).`
- Over 40: indent 0.5 in (or one tab in markdown), no quotation marks,
  citation after the closing punctuation: `... text. (Smith, 2010, p. 42)`.

## References list

### Heading
- Title "References", centered, bold, top of new page in print formats.
- Markdown / web destinations: `## References` heading, no centering.

### Sort order
- Alphabetical by first author's surname.
- Same first author, single vs. multi-author works: single-author entries
  before multi-author entries.
- Same first author, multiple works: chronological, oldest first. Same year:
  alphabetical by title, append `a`/`b`/`c` to the year (matches inline `n.d.-a`).
- Group authors alphabetized by the first significant word of the name.

### Entry format (journal article)
`Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article in sentence case. Journal Name in Title Case and Italics, Volume(Issue), pages. https://doi.org/...`

### Entry format (book)
`Author, A. A. (Year). Title of book in sentence case and italics. Publisher.`

### Entry format (chapter in edited book)
`Author, A. A. (Year). Title of chapter in sentence case. In E. E. Editor (Ed.), Title of book in italics (pp. xx-xx). Publisher.`

### Entry format (web page, dated)
`Author, A. A. (Year, Month Day). Title of page in sentence case and italics. Site Name. https://...`

### Entry format (web page, no date)
`Author, A. A. (n.d.). Title of page in sentence case and italics. Site Name. Retrieved Month Day, Year, from https://...`
- Include the "Retrieved [date], from" only when the page is expected to change.
- For stable pages, omit the retrieval date.

### Indentation and spacing
- Hanging indent: 0.5 in (first line flush, subsequent lines indented).
- Double-spaced in print formats; single-spaced acceptable in web/markdown
  destinations unless the destination's expression rules say otherwise.

### URLs and DOIs
- DOI preferred over URL when both exist.
- Format DOIs as `https://doi.org/10.xxxx/...`. No "doi:" prefix, no
  "Retrieved from" preamble.
- No period after a URL or DOI.

## Document layout

### Title block
- Title centered, bold, upper half of first page.
- Below the title: author name (no title or degree), affiliation,
  course/instructor (student paper variant), date.
- Markdown destinations: `# Title` at top, then a blank line, then a
  metadata block (author / date / course) as plain lines.

### Heading hierarchy
- Level 1: centered, bold, title case. Markdown: `## Heading`.
- Level 2: flush left, bold, title case. Markdown: `### Heading`.
- Level 3: flush left, bold italic, title case. Markdown: `#### Heading`.
- Levels 4 and 5 exist; rarely needed in {{USER}}'s work. Add when first used.

### Body text
- Font: Times New Roman 12, Calibri 11, or similar serif/sans default.
  In markdown destinations, font is the destination's choice.
- Line spacing: double in print/Word destinations; single in markdown unless
  destination overrides.
- Paragraph indent: 0.5 in first-line indent. Markdown: no indent (rendered
  flat); paragraph break is a blank line.
- Margins: 1 in all sides. Markdown: not applicable.

### Footnotes
- APA 7 prefers parenthetical author-date over footnotes; use footnotes only
  for substantive content notes, not citation.
- Numbered superscript in body, full note at page bottom (Word) or as a
  numbered list at section/document end (markdown).

## Paste target expression rules

A paste target says HOW the conventions above are expressed in the destination
format. The style file says WHAT the conventions are; the target says how to
emit them.

### google-docs
- Output a single markdown block that pastes cleanly into a Google Doc.
- Preserve heading levels (`#`, `##`, etc.); Google Docs renders them.
- Use "smart quotes" and en-dashes literally (Google Docs preserves them).
- Italics: use `*italic*` (Google Docs converts on paste).
- Hanging indents in References: NOT achievable via paste. Emit references as
  a flat numbered or bulleted list and instruct {{USER}} once at the top of the
  output: "Apply hanging indent to References after pasting (Format > Align >
  Indentation options > Special > Hanging)."
- Double-spacing: not applied at paste time; instruct once in the same header
  if the destination expects it.

### plain-markdown
- Faithful pass-through. Resolve all citation IDs, generate References, but
  apply no destination-specific transforms. This is the default for archival
  copies and for further conversion downstream (Pandoc, etc.).

### word
- Reserved. Not implemented yet. Formatting mode should refuse and ask
  {{USER}} for the desired expression.

### latex
- Reserved. Not implemented yet.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format
  time. Formatting mode must halt and surface every occurrence rather than
  emitting them into the formatted output. See CLAUDE.md §10.
