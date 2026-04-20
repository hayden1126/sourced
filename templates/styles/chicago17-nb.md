# Style: Chicago 17 (Notes-Bibliography)

This file specifies every style decision for the project, organized so a model
in [formatting mode] can look up a single rule without rereading the file.
Sections are addressable: "see §Footnote citations / Short form", "see
§Bibliography / Sort order". Rules are normative; do not improvise.

## Style identity

- Name: Chicago Manual of Style, 17th edition, notes-bibliography system.
- Shape: footnote
- In-text marker: footnote (numbered superscript in body; full note at page
  bottom in Word, numbered list at end-of-document for markdown via Pandoc
  `[^N]` syntax)
- List heading: Bibliography
- Authority: The Chicago Manual of Style, 17th edition (University of Chicago
  Press, 2017), chapter 14 for citations, chapter 1 for manuscript layout.
- Default for: humanities and social-science work where the syllabus
  specifies "Chicago notes-bibliography" or "Chicago footnote" or "Chicago
  humanities"; history, theology, art history, literature. For author-date
  Chicago contexts, use chicago17-ad.md instead.
- Source consulted:
  - CMOS 17 (print and paywalled online), chapter 14 for notes and
    bibliography, chapter 1 for manuscript layout.
  - https://owl.purdue.edu/owl/research_and_citation/chicago_manual_17th_edition/cmos_formatting_and_style_guide/chicago_manual_of_style_17th_edition.html
    (Purdue OWL Chicago 17 NB, free, non-authoritative; used for
    disambiguation); accessed 2026-04-19.
  - CMOS Online quick guide at chicagomanualofstyle.org has migrated to
    CMOS 18 as of September 2024; the 17th-edition authoritative rules live
    only in the print manual. Rules below are pinned to 17.
- CSL provenance:
  - file: chicago17-nb/chicago-notes-bibliography-17th-edition.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - filename-pinned to 17th-edition variant so the master-branch's
    chicago-notes-bibliography.csl (now tracking CMOS 18) does not silently
    override.
- On-demand references:
  - `chicago17-ad/classical-abbreviations.md` — shared with chicago17-ad.
  - Hook: after pandoc renders output, walk each footnote body and each bibliography entry; for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
- Last reviewed: 2026-04-19.

## Footnote citations

Resolution rules for Pandoc-style IDs in source prose. Each `[@id]` or
`[@id, p. N]` in the source becomes a footnote marker in the derived markdown
and a full note body in the footnote array (see CLAUDE.md §7 [formatting
mode] step 3c). Full form fires on first cite of a source; short form fires
on every subsequent cite of the same source within the draft.

The defining marks of Chicago NB vs. Chicago author-date: citations are
footnotes not parenthetical, every note is numbered sequentially across the
document, and a separate Bibliography lists sources alphabetically.

### Full first-cite form (per source type)

- **Book, one author**:
  `1. Firstname Lastname, *Title of Book* (City: Publisher, Year), page.`
- **Book, two authors**:
  `2. Firstname Lastname and Firstname Lastname, *Title of Book* (City: Publisher, Year), page.`
- **Book, three authors**:
  `3. Firstname Lastname, Firstname Lastname, and Firstname Lastname, *Title of Book* (City: Publisher, Year), page.`
- **Book, four or more authors** (CMOS 17 §14.76): list first author in the
  note plus "et al."; the bibliography entry lists all authors up to ten
  (eleven-plus: first seven + "et al.").
  `4. Firstname Lastname et al., *Title of Book* (City: Publisher, Year), page.`
- **Chapter in edited book**:
  `5. Firstname Lastname, "Chapter Title in Headline Case," in *Title of Book*, ed. Firstname Lastname (City: Publisher, Year), page.`
- **Journal article**:
  `6. Firstname Lastname, "Article Title in Headline Case," *Journal Name* 42, no. 3 (Year): page, DOI or URL.`
- **Web page, dated**:
  `7. Firstname Lastname, "Title of Page," Site Name, Month Day, Year, https://example.com/path.`
- **Web page, no date**:
  `8. Firstname Lastname, "Title of Page," Site Name, accessed Month Day, Year, https://example.com/path.`
- **Translation of classical or primary text** (for classical works, see
  §On-demand references: classical texts):
  `9. PrimaryAuthor, *Title of Work*, trans. Translator Name (City: Publisher, Year), pagination.`

### Short subsequent-cite form (CMOS 17 §14.29-14.35)

After a source has been fully cited once, later notes use a shortened form:

- Single author, single work:
  `12. Smith, *Title*, 42.`
- Two authors:
  `13. Smith and Jones, *Title*, 42.`
- Three-plus authors (always shortened to "et al." in notes regardless of
  number, per §14.29):
  `14. Smith et al., *Title*, 42.`
- Article (short title in quotes, not italics; shortened if the full title is
  long):
  `15. Smith, "Short Title," 42.`

`ibid.` (repeating the immediately preceding note) is permitted in CMOS 17
but deprecated in CMOS 18; use short form preferentially. When the preceding
citation is unambiguous and the writer prefers concision, `ibid.` with a new
page number is allowed: `ibid., 43.`

### Group / corporate author

- First note: `(American Philosophical Association [APA], 2020)` (full name,
  then bracketed abbreviation if registered for the project).
- Subsequent short form: `APA, *Title*, 42.`

### No author

Use the title in the author position. Full first-cite:
`16. "Title of Article in Quotes," *Journal Name* 42 (Year): 12-34.`
Short form: `17. "Short Title," 12.`

### No date

Use `n.d.` in place of the year: `(City: Publisher, n.d.)`.

### Multi-citation in one note

Combine sources with semicolons inside the same footnote:
`18. Smith, *Book A*, 12; Jones, *Book B*, 34.`

### Direct quotes

- **Block quote threshold**: 100 words or 5+ lines (CMOS 17 §13.10).
- **Under threshold**: inline with double quotation marks. Footnote marker
  follows closing punctuation: `... "quoted text."^{N}`
- **Over threshold**: block-indented 0.5 in (or one tab in markdown), no
  quotation marks, footnote marker follows the final punctuation of the
  block quote.
- **Single-spaced** inside block quotes in print formats; surrounding body
  remains double-spaced.

### Classical Greek and Latin works

Same rules as chicago17-ad.md §Classical Greek and Latin works: classical
works are cited by standard pagination (Stephanus, Bekker, etc.), not modern
page numbers. First mention in a note should integrate the translation,
subsequent short-form citations use standard pagination with no year.

- First note: `19. Plato, *Republic*, trans. G. M. A. Grube, revised by C. D. C. Reeve (Indianapolis: Hackett, 1992), 514a.`
- Subsequent: `20. Plato, *Rep.*, 515b.`

When a citation resolves to a classical work (ancient author in
`source.authors`, standard pagination in the locator), read
`~/.claude/style/chicago17-ad/classical-abbreviations.md` for the per-author
abbreviation table before emitting the note. Pagination-system rules
(Stephanus, Bekker, Ennead-tractate-chapter, etc.) are in chicago17-ad.md
§Classical Greek and Latin works; those rules apply here unchanged.

### Personal communication / interview

- In-note only: `21. Jane Smith, personal communication to the author, March 15, 2023.`
- NOT included in Bibliography (CMOS 17 §14.214) unless the interview is
  recorded and archived in a publicly accessible location.

### Reprint of older work

- First note: `22. David Hume, *A Treatise of Human Nature* (1739; repr., Oxford: Clarendon Press, 1978), 412.`
- Short form preserves the reprint year: `23. Hume, *Treatise*, 415.`

### Multi-volume work

- Whole work: `24. Firstname Lastname, *Title of Work*, 3 vols. (City: Publisher, Year-Year), 2:123.`
  (Volume number before colon, page after.)
- Single volume: `25. Firstname Lastname, *Title of Work*, vol. 2, *Subtitle of Volume* (City: Publisher, Year), 123.`

## Bibliography

### Heading

- Title "Bibliography", centered, bold, top of new page in print formats
  (CMOS 17 §1.55-1.56, treated as a level-1 heading).
- Markdown destinations: `## Bibliography` heading, no centering.

### Sort order

- Alphabetical by first author's surname.
- Multiple works by the same first author: chronological, earliest first.
- Same author, same year: append `a`/`b`/`c` to the year, alphabetical by
  title (ignoring leading articles). Letter assignment fires during
  formatting, not in source prose.
- Group authors alphabetized by first significant word of the name.

### Entry format (book)

`Lastname, Firstname. *Title of Book*. City: Publisher, Year.`

- Book title in italics, headline capitalization.
- Publisher city is included for Chicago (unlike APA 7).

### Entry format (chapter in edited book)

`Lastname, Firstname. "Chapter Title in Headline Case." In *Title of Book*, edited by Firstname Lastname, 12-34. City: Publisher, Year.`

### Entry format (journal article)

`Lastname, Firstname. "Article Title in Headline Case." *Journal Name* 42, no. 3 (Year): 12-34. https://doi.org/10.xxxx/yyyy.`

- Article title in double quotes, headline capitalization.
- Journal in italics, title case.
- Volume unitalicized; issue in `no. N` format; page range after colon.

### Entry format (web page, dated)

`Lastname, Firstname. "Title of Page in Headline Case." Site Name. Month Day, Year. https://example.com/path.`

### Entry format (web page, no date)

`Lastname, Firstname. "Title of Page in Headline Case." Site Name. Accessed Month Day, Year. https://example.com/path.`

- Access date included only when the page lacks a publication or revision
  date (CMOS 17 §14.207).

### Entry format (translation of classical or primary text)

`PrimaryAuthor. *Title of Work*. Translated by Translator Name. City: Publisher, Year.`

- Author is the conventional name (Plato, Aristotle, Augustine).
- Year is the modern edition year, not the original composition date.
- Example: `Plato. *Republic*. Translated by G. M. A. Grube. Revised by C. D. C. Reeve. Indianapolis: Hackett, 1992.`

### Entry format (reprint of older work)

`Lastname, Firstname. *Title of Work*. Year of original publication. Reprint, City: Publisher, ReprintYear.`

- Example: `Hume, David. *A Treatise of Human Nature*. 1739. Reprint, Oxford: Clarendon Press, 1978.`

### Entry format (multi-volume work)

- Whole work: `Lastname, Firstname. *Title*. N vols. City: Publisher, Year-Year.`
- Single volume: `Lastname, Firstname. *Title*. Vol. 2, *Subtitle*. City: Publisher, Year.`

### Indentation and spacing

- Hanging indent: 0.5 in (first line flush, subsequent lines indented).
- Single-spaced within entries, blank line between entries (CMOS 17 §14.61).
  This matches chicago17-ad and differs from APA 7 (double-spaced throughout).

### URLs and DOIs

- DOI preferred over URL when both exist.
- Format DOIs as `https://doi.org/10.xxxx/...`. No "doi:" prefix.
- Terminal period after a URL or DOI at the end of an entry (CMOS 17 §14.8).

## Document layout

### Fonts and spacing

- Font: Times New Roman 12 or similar serif default (CMOS 17 §2.8).
- Line spacing: double in print/Word destinations; single in markdown unless
  destination overrides.
- Paragraph indent: 0.5 in first-line indent. Markdown: no indent (flat
  rendering); paragraph break is a blank line.

### Margins

- 1 in all sides.

### Heading hierarchy

- CMOS 17 §1.55-1.56 defines five heading levels; short papers commonly use
  2-3.
- Level 1: centered, bold, headline case. Markdown: `## Heading`.
- Level 2: centered, regular weight, headline case. Markdown: `### Heading`.
- Level 3: flush left, bold, headline case. Markdown: `#### Heading`.

### Title block

- Student papers: separate title page, title centered roughly one-third down,
  byline / course / instructor / date stacked centered below.
- Markdown destinations: `# Title` at top, blank line, metadata block
  (author / date / course) as plain lines.

### Page numbering

- Not specified in the current style file; add when first needed.

### Footnotes

Chicago NB is a footnote-driven style: every source citation flows through
notes. Footnote bodies are authored by [formatting mode] step 3 (see
CLAUDE.md §7) and placed per paste target:

- **Word**: at page bottom, numbered superscript in body, full note text at
  bottom of same page (pandoc handles this natively via the CSL).
- **Markdown (google-docs, plain-markdown)**: Pandoc `[^N]: body` blocks at
  end of document. Google Docs converts `[^N]` to superscript on paste and
  places notes at document end; instruct {{USER}} once at the top of the
  output if page-bottom placement is required (Format > Page setup >
  Footnotes).

Substantive content notes (commentary, asides, tangents) use the same
numbering stream as source citations in Chicago NB; there is no separate
endnote/footnote split.

### Block quotes

Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10.

## Paste target expression rules

### google-docs

- Output a single markdown block that pastes cleanly into a Google Doc.
- Preserve heading levels (`#`, `##`, etc.); Google Docs renders them.
- Footnotes: emit Pandoc `[^N]` markers inline and `[^N]: body` blocks at
  end of document. On paste, Google Docs renders them as end-of-document
  notes; instruct {{USER}} once at the top of the output to convert to
  page-bottom notes if required (Insert > Footnote in Google Docs).
- Italics: use `*italic*` (Google Docs converts on paste).
- Hanging indents in Bibliography: NOT achievable via paste. Emit
  Bibliography entries as a flat list and instruct {{USER}} at the top of
  the output: "Apply hanging indent to Bibliography after pasting
  (Format > Align > Indentation options > Special > Hanging)."

### plain-markdown

- Faithful pass-through. Emit Pandoc `[^N]` footnote syntax in prose and
  `[^N]: body` blocks at end of document. Resolve citation IDs, generate
  Bibliography; apply no destination-specific transforms.

### word

- Output two files: `<draft>.docx.md` (rendered markdown intermediate,
  archive + re-runs) and `<draft>.docx` (submission binary). Source
  `<draft>.md` is never modified.
- Collapse per-instance citation IDs in the derived `<draft>.docx.md`
  before invoking pandoc. See CLAUDE.md §7 [formatting mode] step 4.
- Dependencies (resolved at install time):
  - pandoc 3.1 or newer (citeproc built in).
  - CSL file at `~/.claude/style/chicago17-nb/chicago-notes-bibliography-17th-edition.csl`.
    Required. Halt if missing.
  - Reference docx matching §Document layout (Times New Roman 12 pt,
    double-spaced body, 0.5 in hanging-indent Bibliography paragraph
    style), expected at `~/.claude/style/chicago17-nb/reference-styled.docx`.
    Optional; pandoc default layout used as fallback. Fallback must be
    reported loudly in the step-8 report (footnote font and Bibliography
    style will not match §Document layout; {{USER}} may need to patch
    styles in Word).
- Pipeline:
  1. Write the collapsed, fully-resolved markdown to `<draft>.docx.md`
     with Pandoc `[^N]` footnote syntax preserved. Pandoc emits page-
     bottom footnotes natively from this syntax.
  2. Generate a source-level bibliography file from the citation log at
     `<draft>.bib.json` (CSL JSON, one entry per unique source keyed to
     collapsed ids).
  3. Invoke `pandoc --citeproc --bibliography=<draft>.bib.json --csl=~/.claude/style/chicago17-nb/chicago-notes-bibliography-17th-edition.csl [--reference-doc=~/.claude/style/chicago17-nb/reference-styled.docx] -o <draft>.docx <draft>.docx.md`.
  4. Confirm pandoc exit status is 0 and both output files exist.
- Paste-time instructions: none when the reference docx is present. When
  the ref.docx fell back to pandoc default, instruct {{USER}} once to
  apply Times New Roman 12, double-spacing, hanging-indent Bibliography
  style, and confirm footnotes are at page bottom.

### latex

- Reserved. Not implemented yet.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format
  time. Formatting mode halts and surfaces every occurrence rather than
  emitting them into the formatted output. See CLAUDE.md §7 ([formatting
  mode] procedure step 2) and §8 (Moment 2).
