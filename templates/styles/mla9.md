# Style: MLA 9

This file specifies every style decision for the project, organized so a model
in [formatting mode] can look up a single rule without rereading the file.
Sections are addressable: "see §Inline citations / Two authors", "see
§References list / Sort order". Rules are normative; do not improvise.

## Style identity

- Name: MLA 9th edition.
- Shape: author-page
- In-text marker: parenthetical
- List heading: Works Cited
- Authority: MLA Handbook, 9th edition (Modern Language Association of
  America, 2021), chapters 5-6 for citations, chapter 1 for manuscript
  layout.
- Default for: literary studies, languages, humanities essays where the
  syllabus or publication specifies MLA.
- Source consulted:
  - https://style.mla.org/ (official MLA Style Center; publisher-run; free
    Q&A and sample citations); accessed 2026-04-19.
  - MLA Handbook, 9th ed. (print), for rules not covered in the online
    Style Center.
  - https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/
    (Purdue OWL MLA 9; non-authoritative; used for disambiguation only);
    accessed 2026-04-19.
- CSL provenance:
  - file: mla9/modern-language-association.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "MLA Handbook 9th edition (in-text citations)" (matches
    authority).
- On-demand references:
  - (none yet; classical texts in MLA context may need the per-author
    abbreviation table at chicago17-ad/classical-abbreviations.md if the
    writer is citing Greek or Latin primary sources alongside literary
    scholarship)
- Last reviewed: 2026-04-19.

## Inline citations

Resolution rules for Pandoc-style IDs in source prose. Each row is
exhaustive for that case; if a case isn't listed, ask {{USER}} rather than
guessing.

The defining marks of MLA 9 vs. author-date styles: no year in in-text
citation; a page locator (or alternative locator like a paragraph, line, or
timestamp) appears inside the parenthetical; no comma between author and
locator.

### One author

- Parenthetical (`[@id, p. 42]`): `(Smith 42)`. No comma, no "p." before the
  number.
- Narrative (`@id`): "Smith argues...". When the author's name appears in
  prose, the parenthetical carries only the locator: `Smith argues X (42)`.
- Without locator (`[@id]`): `(Smith)`. Used when citing a work as a whole
  rather than a specific passage. Page locator is preferred whenever the
  source is paginated.
- Page range (`[@id, pp. 42-44]`): `(Smith 42-44)`. Hyphen.

### Two authors

- Parenthetical: `(Smith and Jones 42)`. Word "and", no ampersand.
- Narrative: "Smith and Jones argue..."; parenthetical carries locator only:
  `(42)`.

### Three or more authors

- Parenthetical: `(Smith et al. 42)`. "et al." in roman, no italics (MLA 9
  §6.11).
- Narrative: "Smith et al. argue...".

### Group / corporate author

- First mention parenthetical: `(Modern Language Association 42)`.
- Subsequent: same form, or shortened if a short name is registered for the
  project (`(MLA 42)`).
- Narrative first mention: "the Modern Language Association argues...".
- For government agencies, MLA 9 permits "United States, Department of X"
  to disambiguate by agency hierarchy in Works Cited; in-text uses a
  shortened form.

### No author

Use the title (or a shortened title, up to four significant words) in
place of author.

- Article, chapter, or web page (title in quotes): `("Short Title" 42)`.
- Book, journal, or standalone work (title italicized): `(*Short Title* 42)`.
- Narrative: "The article 'Short Title' argues..." with no parenthetical
  name.

### Sources without page numbers

MLA 9 recognizes that many digital sources lack pagination. Use alternative
locators in order of preference (MLA 9 §6.33):

1. Paragraph number (if explicitly numbered by the source): `(Smith, par. 12)`.
2. Section name or heading: `(Smith, "Methods")`.
3. Line number for poetry or classical texts: `(Dante, Inf. 5.73)` or
   `(Shakespeare, Hamlet 1.2.129)` (act.scene.line).
4. Timestamp for audio or video: `(Smith 00:12:45)`.
5. If none of the above applies, cite with author name only: `(Smith)`.

Do not invent a page number. If the source is paginated but the specific
locator is unknown, halt and surface to {{USER}}.

### Multi-citation

- Pandoc `[@a; @b]` resolves to `(Smith 42; Jones 15)`. Semicolon separator.
- Same author, multiple works: include a shortened title to disambiguate:
  `(Smith, "Article One" 12; Smith, "Article Two" 34)`.

### Direct quotes

- **Block quote threshold**: 4+ lines of prose or 3+ lines of verse (MLA 9
  §6.40).
- **Under threshold (prose)**: inline with double quotation marks.
  Parenthetical follows closing quotation mark, before terminal
  punctuation: `Smith argues that "the tradition continues" (42).`
- **Over threshold (prose)**: indent 0.5 in (or one tab in markdown), no
  quotation marks, parenthetical follows terminal punctuation: `... text.
  (Smith 42)`.
- **Verse, up to 3 lines**: inline with double quotation marks, slashes
  (` / `) marking line breaks: `"One line / Two line" (Smith 1-2)`.
- **Verse, 4+ lines**: block-indented as prose, line breaks preserved.

### Classical and scriptural sources

For classical Greek and Latin works, MLA 9 accepts standard pagination
(Stephanus, Bekker) in place of modern page numbers:

- `(Plato, Rep. 514a)`, `(Aristotle, NE 1094a1-3)`.
- Abbreviations follow CMOS 17 §10.45 conventions; when writing literary
  scholarship that draws on classical sources, read
  `~/.claude/style/chicago17-ad/classical-abbreviations.md` for the
  per-author abbreviation table before emitting such a citation.

For biblical citations: `(Matt. 5.3-12)`, book abbreviated, chapter and
verse separated by period. Bible is not listed in Works Cited when cited
parenthetically by book.chapter.verse only.

## Works Cited

### Heading

- Title "Works Cited", centered, top of new page.
- Markdown destinations: `## Works Cited` heading, no centering.

### Sort order

- Alphabetical by first author's surname.
- Multiple works by the same author: alphabetical by title (ignoring
  leading articles). Replace the author name with three hyphens (`---`)
  in the second and subsequent entries.
- No-author works: alphabetical by title.

### Entry format: MLA 9 container model

MLA 9 uses a "container" model where each entry lists the source's
immediate context (a journal, a book, a website) and, if applicable, a
larger context that contains the first (a database, an archive). The
container order is:

1. Author.
2. Title of source.
3. Title of container,
4. Other contributors,
5. Version,
6. Number,
7. Publisher,
8. Publication date,
9. Location.

Elements not applicable to a given source are omitted. Punctuation: period
after author, title of source, and location; commas between the other
elements within a container.

### Entry format (journal article)

`Lastname, Firstname. "Article Title in Headline Case." *Journal Name*, vol. 42, no. 3, Year, pp. 12-34, https://doi.org/10.xxxx/yyyy.`

- Article title in double quotes, headline case.
- Journal name italicized.
- "vol." and "no." markers before volume and issue.
- DOI preferred over URL when both exist; format as full https resolver.

### Entry format (book)

`Lastname, Firstname. *Title of Book*. Publisher, Year.`

- Book title italicized, headline case.
- MLA 9 drops publisher-city (MLA 8 change retained in MLA 9); differs from
  Chicago which keeps the city.

### Entry format (chapter in edited book)

`Lastname, Firstname. "Chapter Title." *Title of Book*, edited by Firstname Lastname, Publisher, Year, pp. 12-34.`

### Entry format (web page, dated)

`Lastname, Firstname. "Title of Page." *Site Name*, Publisher (if different from Site Name), Day Month Year, https://example.com/path.`

- Date format: day-month-year with month abbreviated (e.g., "5 Apr. 2022").
- Accessed date optional; include when the source is likely to change or
  when publication date is absent.

### Entry format (web page, no date)

`Lastname, Firstname. "Title of Page." *Site Name*, Publisher, https://example.com/path. Accessed Day Month Year.`

- "Accessed" date added when publication date is genuinely unavailable.

### Entry format (work in a larger database)

Nested containers. Outer container is the database; inner container is the
journal or book:

`Lastname, Firstname. "Article Title." *Journal Name*, vol. 42, no. 3, Year, pp. 12-34. *JSTOR*, https://doi.org/10.xxxx/yyyy.`

- Inner container (journal) closes with period before outer container
  (database) begins.

### Entry format (translation of classical or primary text)

`PrimaryAuthor. *Title of Work*. Translated by Firstname Lastname, Publisher, Year.`

- Example: `Plato. *Republic*. Translated by G. M. A. Grube, revised by C. D. C. Reeve, Hackett, 1992.`

### Indentation and spacing

- Hanging indent: 0.5 in (first line flush, subsequent lines indented).
- Double-spaced throughout Works Cited, matching body-text spacing.

### URLs and DOIs

- DOI preferred over URL when both exist.
- Format DOIs as `https://doi.org/10.xxxx/...`. No "doi:" prefix.
- MLA 9 recommends including the full URL (unlike APA which sometimes
  strips the access wrapper); include protocol.

## Document layout

### Title block

- MLA papers do not use a separate title page (unless the instructor
  requires one). Four-line header at top-left of first page: author name,
  instructor, course, date (day-month-year format: `5 Apr. 2022`). Title
  centered on the next line.
- Markdown destinations: the header fits naturally as a metadata block
  below the title.

### Heading hierarchy

MLA 9 does not prescribe a strict heading hierarchy; most papers use flat
or lightly-nested headings.

- Level 1: `## Heading` (markdown) / centered bold (print).
- Level 2: `### Heading` (markdown) / flush left bold (print).

### Body text

- Font: serif (Times New Roman 12 preferred), double-spaced throughout.
- Paragraph indent: 0.5 in first-line indent.
- Margins: 1 in all sides.
- Page numbers in upper-right corner with the author's surname preceding:
  `Smith 3`.

### Footnotes

MLA 9 permits substantive content notes via footnote or endnote (writer's
choice), numbered superscript in body. Footnotes are for commentary, not
for citation; citations stay in parenthetical form.

## Paste target expression rules

### google-docs

- Output a single markdown block that pastes cleanly into a Google Doc.
- Preserve heading levels; Google Docs renders them.
- Works Cited: hanging indent NOT achievable via paste. Emit entries as a
  flat list and instruct {{USER}} at the top of the output: "Apply hanging
  indent to Works Cited after pasting (Format > Align > Indentation options
  > Special > Hanging)."
- Italics: `*italic*` (Google Docs converts on paste).
- Smart quotes and en-dashes preserved literally.

### plain-markdown

- Faithful pass-through. Resolve citation IDs and generate Works Cited;
  apply no destination-specific transforms.

### word

- Output two files: `<draft>.docx.md` (rendered markdown intermediate) and
  `<draft>.docx` (submission binary). Source `<draft>.md` is never modified.
- Collapse per-instance citation IDs in the derived `<draft>.docx.md`
  before invoking pandoc. See CLAUDE.md §7 [formatting mode] step 4.
- Dependencies (resolved at install time):
  - pandoc 3.1 or newer (citeproc built in).
  - CSL file at `~/.claude/style/mla9/modern-language-association.csl`.
    Required.
  - Reference docx matching §Document layout (Times New Roman 12 pt,
    double-spaced body, 0.5 in hanging-indent Works Cited paragraph
    style, Smith 3 header format), expected at
    `~/.claude/style/mla9/reference-styled.docx`. Optional; pandoc
    default layout used as fallback. Fallback must be reported in the
    step-8 report.
- Pipeline:
  1. Write the collapsed, fully-resolved markdown to `<draft>.docx.md`.
  2. Generate a source-level bibliography file from the citation log at
     `<draft>.bib.json` (CSL JSON, one entry per unique source keyed to
     collapsed ids).
  3. Invoke `pandoc --citeproc --bibliography=<draft>.bib.json --csl=~/.claude/style/mla9/modern-language-association.csl [--reference-doc=~/.claude/style/mla9/reference-styled.docx] -o <draft>.docx <draft>.docx.md`.
  4. Confirm pandoc exit status is 0 and both output files exist.
- Paste-time instructions: when the reference docx falls back to pandoc
  default, instruct {{USER}} once to apply Times New Roman 12 double-
  spaced, hanging indent Works Cited, and "Lastname N" page-number
  header in Word.

### latex

- Reserved. Not implemented yet.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format
  time. Formatting mode halts and surfaces every occurrence rather than
  emitting them into the formatted output. See CLAUDE.md §7 ([formatting
  mode] procedure step 2) and §8 (Moment 2).
