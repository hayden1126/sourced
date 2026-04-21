# Style: MLA 9

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline parenthetical author-page citations and Works Cited entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

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
  - CSL title: "MLA Handbook 9th edition (in-text citations)"
- On-demand references:
  - `mla9/classical-abbreviations.md` — cross-reference only; MLA does not prescribe classical abbreviation, so no post-pandoc hook fires. Content mirrors `chicago17-ad/classical-abbreviations.md`.
- Last reviewed: 2026-04-19.

## Document layout

### Fonts and spacing

- Font: serif (Times New Roman 12 preferred), double-spaced throughout.
- Paragraph indent: 0.5 in first-line indent.

### Margins

- 1 in all sides.

### Heading hierarchy

MLA 9 does not prescribe a strict heading hierarchy; most papers use flat
or lightly-nested headings.

- Level 1: `## Heading` (markdown) / centered bold (print).
- Level 2: `### Heading` (markdown) / flush left bold (print).

### Title block

- MLA papers do not use a separate title page (unless the instructor
  requires one). Four-line header at top-left of first page: author name,
  instructor, course, date (day-month-year format: `5 Apr. 2022`). Title
  centered on the next line.
- Markdown destinations: the header fits naturally as a metadata block
  below the title.

### Page numbering

- Page numbers in upper-right corner with the author's surname preceding:
  `Smith 3`.

### Footnotes

MLA 9 permits substantive content notes via footnote or endnote (writer's
choice), numbered superscript in body. Footnotes are for commentary, not
for citation; citations stay in parenthetical form.

### Block quotes

Threshold: 4 lines of prose, 3 lines of verse (MLA 9 §6.36). Verse quotations use a slash `/` with spaces to mark line breaks when inline; block form for 4+ lines of prose / 3+ lines of verse with no quotation marks. `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2).

## Paste target expression rules

### google-docs

- pandoc flags: `--citeproc --wrap=none -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — preserves ASCII apostrophes inside italic spans for linguistic glottal-stop notation while letting pandoc's `-smart` writer curl English apostrophes and quotes outside italics. `[formatting mode]` resolves the name to `~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Apply hanging indent to Works Cited after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "MLA page-number header ('Smith 3') requires a custom Google Docs header; add via Insert > Headers > Header, then type surname + page number."
- Post-pandoc transforms: strip pandoc fenced-div markers from the Works Cited block (`sed -e '/^::: /d' -e '/^:::$/d'`); Google Docs' "Paste as markdown" renders the `:::` wrappers as literal text. The `-header_attributes` pandoc extension handles the heading-attribute counterpart (`# Works Cited {#works-cited .unnumbered}`).

### plain-markdown

- pandoc flags: `--citeproc --wrap=preserve -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — same rationale as the google-docs target.
- Paste-time instructions: (none)
- Post-pandoc transforms: strip pandoc fenced-div markers from the Works Cited block (`sed -e '/^::: /d' -e '/^:::$/d'`); most destinations (Obsidian, Notion, GitHub render, Reddit) paste the `:::` wrappers as literal text.

### word

- pandoc flags: `--citeproc`
- reference.docx: `mla9/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging Works Cited, "Lastname N" page-number header. Optional; on absence, pandoc default layout; surface tolerable warning.
- Post-pandoc transforms: (none)

### latex

- pandoc flags: `--citeproc --standalone -t latex`
- template.tex: `mla9/template.tex` — article class, 12pt Times-family, 1in margins, double-spaced body, hanging-indent Works Cited. `iftex` guard supports `pdflatex`, `xelatex`, and `lualatex`. Required; `[formatting mode]` resolves the relative path to `~/.claude/style/mla9/template.tex` and adds `--template=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Compile with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)."
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
