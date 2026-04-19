# Style: Chicago 17 (Author-Date)

This file specifies every style decision for the project, organized so a model
in [formatting mode] can look up a single rule without rereading the file.
Sections are addressable: "see §Inline / Two authors", "see §References /
Sort order". Rules are normative; do not improvise.

## Style identity

- Name: Chicago Manual of Style, 17th edition, author-date system.
- Authority: The Chicago Manual of Style, 17th edition (University of Chicago
  Press, 2017), chapters 14-15 for citations, chapters 1-2 for manuscript
  layout.
- Default for: humanities and social-science work where the syllabus
  specifies "Chicago author-date" (or where the professor's own publications
  use parenthetical author-year style). Not for notes-bibliography (NB)
  contexts; for those, use a chicago17-nb.md style file instead (not yet
  shipped).
- Last reviewed: 2026-04-18.

## Inline citations

Resolution rules for Pandoc-style IDs in source prose. Each row is exhaustive
for that case; if a case isn't listed, ask {{USER}} rather than guessing.

The defining marks of Chicago author-date vs. APA: no comma between author
and year, and no "p." before page numbers. Otherwise the systems look
similar.

### One author
- Parenthetical (`[@id]`): `(Smith 2010)`. No comma between author and year.
- Narrative (`@id`): `Smith (2010)`.
- With page locator (`[@id, p. 42]`): `(Smith 2010, 42)`. No "p.", just the
  number after a comma.
- With page range (`[@id, pp. 42-44]`): `(Smith 2010, 42-44)`. En-dash, not
  hyphen.

### Two authors
- Parenthetical: `(Smith and Jones 2010)`. Word "and" inside parens (not the
  ampersand APA uses).
- Narrative: `Smith and Jones (2010)`.

### Three authors
- Parenthetical, first citation: `(Smith, Jones, and Brown 2010)`. List all
  three.
- Parenthetical, subsequent citations: `(Smith et al. 2010)`. Shorten after
  first mention.
- Narrative, first citation: `Smith, Jones, and Brown (2010)`.
- Narrative, subsequent: `Smith et al. (2010)`.
- "First mention" is per-document, not per-paragraph. The formatting pass
  tracks first vs. subsequent across the whole draft.

### Four or more authors
- Parenthetical: `(Smith et al. 2010)`. Always shortened to first author plus
  "et al.", from the first citation onward.
- Narrative: `Smith et al. (2010)`.
- The full author list still appears in the References entry; only the
  in-text citation is shortened.

### Group / corporate author
- First mention parenthetical: `(American Philosophical Association [APA]
  2020)`. Full name, then bracketed abbreviation if one is registered for the
  project.
- Subsequent: `(APA 2020)`.
- Narrative first mention: `the American Philosophical Association (APA
  2020)`.
- Subsequent narrative: `APA (2020)`.
- If `source.authors` in the log is a group author with no abbreviation
  registered for the project, use the full name on every mention.

### No author
- Parenthetical: `("Title of Work" 2010)` for articles, chapters, web pages;
  `(Title of Work 2010)` italic for books, reports, journals.
- Use the title (or shortened title — first few significant words) in place
  of author. Headline-style capitalization in the citation.

### No date
- `n.d.` in place of year: `(Smith n.d.)`. No comma before `n.d.`.
- Multiple `n.d.` works by the same author: append lowercase letters,
  `(Smith n.d.-a)`, `(Smith n.d.-b)`. Letter assignment matches the
  References list ordering (alphabetical by title, ignoring leading
  articles). The formatting pass assigns letters; do not guess them in
  source prose.

### Multi-citation
- Pandoc `[@a; @b]` resolves to `(AuthorA YearA; AuthorB YearB)`. Semicolon
  separator.
- Order: alphabetical by first author's surname (CMOS 17 §15.30).
- Same author, multiple years: `(Smith 2008, 2010)`. Comma-separated years
  after the single author name.

### Direct quotes
- Block quote threshold: 100 words or 5+ lines (CMOS 17 §13.10). Looser than
  APA's 40-word rule.
- Under the threshold: inline with double quotation marks. Citation
  immediately follows closing quote, before terminal punctuation if
  mid-sentence: `... "X" (Smith 2010, 42).`
- Over the threshold: indent 0.5 in (or one tab in markdown), no quotation
  marks, citation after the closing punctuation: `... text. (Smith 2010, 42)`.
- Single-spaced inside the block quote in print formats; the surrounding
  body remains double-spaced.

## References list

### Heading
- Title "References", centered, top of new page in print formats. Bold per
  CMOS 17 §1.55-1.56 if treated as a level-1 heading.
- Markdown / web destinations: `## References` heading, no centering.

### Sort order
- Alphabetical by first author's surname.
- Same first author, single vs. multi-author works: single-author entries
  before multi-author entries.
- Same first author, multiple works: chronological, oldest first. Same year:
  alphabetical by title (ignoring leading articles), append `a`/`b`/`c` to
  the year (matches inline `n.d.-a`).
- Group authors alphabetized by the first significant word of the name.
- For authors with multiple works in the same year, the year-letter
  assignment is consistent across inline and References — the formatting
  pass owns letter assignment in one pass.

### Entry format (journal article)
`Smith, Jane A., John B. Jones, and Robert C. Brown. 2010. "Title of Article in Headline Case." Journal Name in Title Case and Italics 42 (3): 12-34. https://doi.org/...`
- Year follows author (no parentheses around it).
- Article title in double quotes, headline-style capitalization.
- Journal in italics, title case.
- Volume number unitalicized; issue in parens; page range after colon.

### Entry format (book)
`Smith, Jane A. 2010. Title of Book in Italics and Headline Case. Publisher City: Publisher.`
- Book title in italics, headline case.
- Publisher city is included for Chicago (unlike APA, which dropped it in
  the 7th edition).

### Entry format (chapter in edited book)
`Smith, Jane A. 2010. "Title of Chapter in Headline Case." In Title of Book in Italics, edited by First Last and First Last, 12-34. Publisher City: Publisher.`

### Entry format (web page, dated)
`Smith, Jane A. 2010. "Title of Page in Headline Case." Site Name. Month Day, Year. https://...`
- Site name unitalicized, in title case.
- Date is the publication or last-revision date if available.

### Entry format (web page, no date)
`Smith, Jane A. n.d. "Title of Page in Headline Case." Site Name. Accessed Month Day, Year. https://...`
- "Accessed [date]" only when no other date is available; CMOS 17 §14.207.
- For stable pages from authoritative sources, omit the access date.

### Indentation and spacing
- Hanging indent: 0.5 in (first line flush, subsequent lines indented).
- Single-spaced within entries, blank line between entries (CMOS 17 §15.10).
  This differs from APA, which double-spaces References throughout.

### URLs and DOIs
- DOI preferred over URL when both exist.
- Format DOIs as `https://doi.org/10.xxxx/...`. No "doi:" prefix.
- No period after a URL or DOI at the end of an entry.

## Document layout

### Title block
- Student papers: separate title page, title centered roughly one-third down
  the page, byline / course / instructor / date stacked centered below.
- Markdown destinations: `# Title` at top, then a blank line, then a
  metadata block (author / date / course) as plain lines.

### Heading hierarchy
- CMOS 17 §1.55-1.56 defines five heading levels. The system is more
  flexible than APA's; common practice for short papers uses 2-3 levels.
- Level 1: centered, bold, headline case. Markdown: `## Heading`.
- Level 2: centered, regular weight, headline case. Markdown: `### Heading`.
- Level 3: flush left, bold, headline case. Markdown: `#### Heading`.
- Levels 4 and 5 exist; rarely needed in {{USER}}'s work. Add when first used.

### Body text
- Font: Times New Roman 12 or similar serif default. CMOS 17 §2.8 prefers
  serif for body text.
- Line spacing: double in print/Word destinations; single in markdown unless
  destination overrides.
- Paragraph indent: 0.5 in first-line indent. Markdown: no indent (rendered
  flat); paragraph break is a blank line.
- Margins: 1 in all sides.

### Footnotes
- The author-date system uses parenthetical citation, not footnotes, for
  source attribution. Footnotes are reserved for substantive content notes
  (commentary, asides, tangential references).
- Numbered superscript in body, full note at page bottom (Word) or as a
  numbered list at section/document end (markdown).
- Substantive footnotes that themselves cite a source use the same
  author-date parenthetical inside the note: `For a contrasting view, see
  (Jones 2012, 88-90).`

## Paste target expression rules

A paste target says HOW the conventions above are expressed in the
destination format. The style file says WHAT the conventions are; the target
says how to emit them.

### google-docs
- Output a single markdown block that pastes cleanly into a Google Doc.
- Preserve heading levels (`#`, `##`, etc.); Google Docs renders them.
- Use "smart quotes" and en-dashes literally (Google Docs preserves them).
- Italics: use `*italic*` (Google Docs converts on paste).
- Hanging indents in References: NOT achievable via paste. Emit references
  as a flat numbered or bulleted list and instruct {{USER}} once at the top
  of the output: "Apply hanging indent to References after pasting (Format >
  Align > Indentation options > Special > Hanging)."
- Double-spacing: not applied at paste time; instruct once in the same
  header if the destination expects it.

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
  emitting them into the formatted output. See CLAUDE.md §7 ([formatting
  mode] procedure step 2) and §8 (Moment 2).
