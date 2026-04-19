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
- Parenthetical: `(Smith, Jones, and Brown 2010)`. List all three on every
  citation; CMOS 17 §15.29 does not shorten three-author works to "et al."
  in the in-text citation (this differs from APA, which shortens at three).
- Narrative: `Smith, Jones, and Brown (2010)`.

### Four or more authors
- Parenthetical: `(Smith et al. 2010)`. Always shortened to first author plus
  "et al.", from the first citation onward (CMOS 17 §15.29).
- Narrative: `Smith et al. (2010)`.
- The full author list (up to ten; for eleven or more list the first seven
  plus "et al.") appears in the References entry per CMOS 17 §15.9; only the
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

### Classical Greek and Latin works
Author-date handles ancient texts unevenly: classical works are cited by
standard pagination systems (Stephanus, Bekker, etc.), not modern page
numbers, so the year of any particular translation is usually irrelevant
for locating the passage.

- **First mention**: prefer narrative integration that introduces the
  translation: `In the Republic, Plato (trans. Grube and Reeve 1992)
  argues that...`
- **Subsequent references**: parenthetical with standard pagination, no
  year: `(Plato, Rep. 514a)`, `(Aristotle, NE 1094a1-3)`,
  `(Augustine, Conf. 8.12.29)`, `(Aquinas, ST I-II, q. 94, a. 2)`.
- **Standard pagination systems**:
  - Stephanus for Plato (e.g., `514a` — page 514, section a).
  - Bekker for Aristotle (e.g., `1094a1-3` — page 1094, column a, lines 1-3).
  - Ennead.tractate.chapter for Plotinus (e.g., `Enn. 1.6.9` — Ennead 1,
    tractate 6, chapter 9). Add Henry-Schwyzer line numbers when precision
    matters: `Enn. 1.6.9.34-37`. Bare chapter is the baseline form; line
    numbers are added for close textual analysis.
  - Volume.fragment for Stoic fragments via von Arnim's *Stoicorum
    Veterum Fragmenta* (e.g., `SVF 2.473` — vol. 2, fragment 473). The
    Long-Sedley collection (`LS`, Long and Sedley 1987, *The Hellenistic
    Philosophers*) is the dominant alternative in anglophone philosophy
    and is cited by passage code (number + letter): `LS 39A`, `LS 61H`.
    LS passage codes are not volume.fragment; the number identifies the
    thematic section and the letter the passage within it.
  - Book.section for Diogenes Laertius (e.g., `DL 7.87` — book 7,
    section 87).
  - Book.section for Sextus Empiricus (e.g., `PH 1.25` for Outlines of
    Pyrrhonism, `M 7.150` for Against the Mathematicians). Note that
    *M* 1-6 is sometimes titled *Against the Professors* and *M* 7-11
    *Adversus Dogmaticos*; the unified `M` numbering is standard.
  - Treatise + book.section for Cicero's multi-book philosophical works
    (e.g., `Off. 1.15`, `Fin. 3.20`, `ND 2.45`). Single-book works and
    speeches use treatise + section only (e.g., `Mil. 23`); works
    organized into multiple orations or books restore the book number
    (e.g., `Cat. 1.5`). When in doubt, follow the divisions of the
    standard edition (OCT or Teubner).
  - For Seneca: letter.section for the Letters (`Ep. 9.6`);
    book.chapter.section for the dialogues and treatises (`Ira 1.5.2`).
  - Book.section for Marcus Aurelius (e.g., `Med. 4.17`).
  - For Epicurus: cite the *Letters* by addressee (`Ep. Hdt.` to
    Herodotus, `Ep. Men.` to Menoeceus, `Ep. Pyth.` to Pythocles), the
    *Principal Doctrines* as `KD` (Kyriai Doxai) by numbered doctrine
    (`KD 1`, `KD 11`), and the *Vatican Sayings* as `SV` by saying
    number. Many Epicurean fragments survive only via Diogenes Laertius
    book 10 and are cited as `DL 10.NN` instead.
  - For Lucretius: `DRN` (De rerum natura), book.line (`DRN 2.216-93`).
  - For Epictetus: `Diss.` (Discourses), book.chapter.section
    (`Diss. 1.1.7`); `Ench.` (Enchiridion), section number (`Ench. 5`).
  - Patristic and medieval authors: book.chapter or book.chapter.section,
    depending on the work's standard division (Augustine's Confessions and
    City of God use book.chapter.section; some shorter works use just
    book.chapter).
  - Aquinas: part, question, article (e.g., `ST I-II, q. 94, a. 2`).
- **Standard title abbreviations** per CMOS 17 §10.45 (use Latin or
  English forms; consistent within a paper). When a citation resolves
  to a classical work, read
  `~/.claude/style/chicago17-ad/classical-abbreviations.md` for the
  per-author abbreviation table (Plato, Aristotle, Cicero, Seneca,
  Augustine, Aquinas, etc.) before emitting the id. The file is
  shipped with this style; `install.sh --style chicago17-ad` installs
  it automatically.
- **Abbreviations are author-scoped.** The same abbreviation can refer
  to different works by different authors (`Rep.` is Plato's Republic
  AND Cicero's De re publica; `Ep.` is used for the letters of Seneca,
  Pliny, Horace, and others). Always include the author name in the
  citation to disambiguate: `(Plato, Rep. 514a)` vs. `(Cicero, Rep. 1.39)`,
  `(Seneca, Ep. 9.6)` vs. `(Pliny, Ep. 6.16)`.
- **Pandoc syntax.** `[@plato-republic-001, 514a]` resolves to
  `(Plato, Rep. 514a)`. The locator carries standard pagination; the
  year is suppressed for classical works. The formatter detects a
  classical work from the log entry's content (ancient author, standard
  pagination format in the locator); no schema change required.

### Personal communication / interview
- In-text only: `(J. Smith, pers. comm., March 15, 2023)`. Use the
  communicator's full name on first mention, surname on subsequent.
- NOT included in References — personal communications are not recoverable
  by readers (CMOS 17 §15.53).
- Exception: recorded and archived interviews that are publicly accessible
  get a normal entry under the interviewee's name.

### Reprint of older work
- In-text: `(Hume [1739] 1978)` — original publication year in brackets,
  reprint year following. Both years stay in subsequent citations.
- Pandoc syntax: `[@hume-treatise-001]` resolves to `(Hume [1739] 1978)`
  when the log entry carries an `original_year` field alongside the
  reprint `year`. Without an `original_year`, renders as the standard
  `(Hume 1978)`.

## References list

### Heading
- Title "References", centered, bold, top of new page in print formats
  (treated as a level-1 heading per CMOS 17 §1.55-1.56).
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
`Smith, Jane A., John B. Jones, and Robert C. Brown. 2010. "Title of Article in Headline Case." Journal Name in Title Case and Italics 42 (3): 12-34. https://doi.org/10.xxxx/yyyy.`
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
`Smith, Jane A. 2010. "Title of Page in Headline Case." Site Name. Month Day, Year. https://example.com/path.`
- Site name unitalicized, in title case.
- Date is the publication or last-revision date if available.

### Entry format (web page, no date)
`Smith, Jane A. n.d. "Title of Page in Headline Case." Site Name. Accessed Month Day, Year. https://example.com/path.`
- "Accessed [date]" included when no publication or revision date is
  available on the page (CMOS 17 §14.207).
- For stable, dated pages from authoritative sources, the access date may
  be omitted.

### Entry format (translation of classical or primary text)
`PrimaryAuthor. EditionYear. Title in Italics. Translated by Translator Name. City: Publisher.`
- Author is the original writer's conventional name (Plato, Aristotle,
  Augustine, Aquinas).
- Year is the translation/edition year — the year that locates the volume
  on a library shelf, not the original composition date.
- "Translated by" or "Edited and translated by" as appropriate; for
  revisions, append "Revised by [Reviser Name]."
- Example: `Plato. 1992. Republic. Translated by G. M. A. Grube. Revised
  by C. D. C. Reeve. Indianapolis: Hackett.`
- For a work cited only by standard pagination (Stephanus, Bekker), the
  References entry still uses the modern edition year — that's how the
  reader finds the volume; the standard pagination is how they find the
  passage within it.

### Entry format (multi-volume work)
- Whole multi-volume work: `Author. Year-Year. Title in Italics. N vols. City: Publisher.`
- Single volume of a multi-volume set: `Author. Year. Title in Italics. Vol. N of Series Title in Italics. City: Publisher.`
- A chapter or entry within a single volume of a multi-volume set:
  `Author. Year. "Chapter Title in Quotes." In Title of Volume in Italics, vol. N of Series Title, edited by Editor Name, NN-NN. City: Publisher.`

### Entry format (reprint of older work)
`Author. (OriginalYear) ReprintYear. Title in Italics. Editor / translator info if any. City: Reprint Publisher.`
- Original publication year in parentheses, reprint year follows without
  parentheses.
- Used when the original year is meaningful for understanding the work's
  place in intellectual history (especially common for classical
  philosophy reprints from the early modern period onward).
- Example: `Hume, David. (1739) 1978. A Treatise of Human Nature. Edited
  by L. A. Selby-Bigge. 2nd ed. Revised by P. H. Nidditch. Oxford:
  Clarendon Press.`

### Indentation and spacing
- Hanging indent: 0.5 in (first line flush, subsequent lines indented).
- Single-spaced within entries, blank line between entries (CMOS 17 §15.10).
  This differs from APA, which double-spaces References throughout.

### URLs and DOIs
- DOI preferred over URL when both exist.
- Format DOIs as `https://doi.org/10.xxxx/...`. No "doi:" prefix.
- Terminal period after a URL or DOI at the end of an entry (CMOS 17 §14.8;
  this differs from APA, which omits the terminal period).

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
- Output two files from one pass: `<draft>.docx.md` (the rendered-markdown
  intermediate, for archive and re-runs) and `<draft>.docx` (the
  submission binary). Source `<draft>.md` is never modified.
- Collapse per-instance citation IDs in the derived `<draft>.docx.md`
  before invoking pandoc. See CLAUDE.md §7 `[formatting mode]` step 4
  for the collapse procedure and its rationale; pandoc-citeproc dedupes
  by id, so three entries for one source render as three References
  entries unless collapsed.
- Dependencies (resolved at install time, not format time):
  - pandoc 3.1 or newer (citeproc is built in). Required. If missing,
    halt and surface `install.sh`'s prerequisite error.
  - CSL file for the style, shipped at
    `~/.claude/style/chicago17-ad/chicago-author-date-17th-edition.csl`.
    Required. If missing, halt and report; do not fall back to a
    different CSL edition silently (edition drift was the failure mode
    that motivated shipping this file).
  - Reference docx matching §Document layout (Times New Roman 12 pt,
    double-spaced body, 0.5 in hanging-indent Bibliography paragraph
    style), expected at
    `~/.claude/style/chicago17-ad/reference-styled.docx`. Optional. If
    missing, run pandoc without `--reference-doc` and report the
    fallback loudly in step 8 (paragraph style and hanging indents will
    not match §Document layout; {{USER}} may need to patch styles in
    Word).
- Pipeline:
  1. Write the collapsed, fully-resolved markdown to `<draft>.docx.md`.
  2. Generate a source-level bibliography file from the citation log
     (one entry per unique source, keyed to the collapsed ids) in CSL
     JSON format, at `<draft>.bib.json` next to the draft.
  3. Invoke `pandoc --citeproc
     --bibliography=<draft>.bib.json
     --csl=~/.claude/style/chicago17-ad/chicago-author-date-17th-edition.csl
     [--reference-doc=~/.claude/style/chicago17-ad/reference-styled.docx]
     -o <draft>.docx <draft>.docx.md`.
     The `--reference-doc` flag is omitted when the ref.docx is missing.
  4. Confirm pandoc exit status is 0 and both output files exist before
     reporting to {{USER}}.
- Paste-time instructions: none when the ref.docx is present. When the
  ref.docx fell back to pandoc's default, instruct {{USER}} once to
  apply Times New Roman 12, double-spacing, and hanging-indent
  References in Word after opening the file.

### latex
- Reserved. Not implemented yet.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format
  time. Formatting mode must halt and surface every occurrence rather than
  emitting them into the formatted output. See CLAUDE.md §7 ([formatting
  mode] procedure step 2) and §8 (Moment 2).
