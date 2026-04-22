# Style: APA 7

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline parenthetical author-date citations and References list entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

## Style identity

- Name: APA 7th edition.
- Shape: author-date
- In-text marker: parenthetical
- List heading: References
- Authority: Publication Manual of the American Psychological Association, 7th edition (2020), chapters 8-10 (citations), chapter 2 (manuscript layout).
- Default for: behavioral and social sciences; {{USER}}'s primary work.
- Source consulted:
  - Publication Manual, 7th ed. (2020), chapters 8-10 for citations, chapter 2 for manuscript layout.
  - https://apastyle.apa.org/ (official APA Style, publisher-run); accessed 2026-04-19.
- CSL provenance:
  - file: apa7/apa.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "APA Style 7th edition"
- On-demand references: (none)
- Last reviewed: 2026-04-19.

## Document layout

### Fonts and spacing

- Font: Times New Roman 12, Calibri 11, or similar serif/sans default.
  In markdown destinations, font is the destination's choice.
- Line spacing: double in print/Word destinations; single in markdown unless
  destination overrides.
- Paragraph indent: 0.5 in first-line indent. Markdown: no indent (rendered
  flat); paragraph break is a blank line.

### Margins

- 1 in all sides. Markdown: not applicable.

### Heading hierarchy

- Level 1: centered, bold, title case. Markdown: `## Heading`.
- Level 2: flush left, bold, title case. Markdown: `### Heading`.
- Level 3: flush left, bold italic, title case. Markdown: `#### Heading`.
- Levels 4 and 5 exist; rarely needed in {{USER}}'s work. Add when first used.

### Title block

- Title centered, bold, upper half of first page.
- Below the title: author name (no title or degree), affiliation,
  course/instructor (student paper variant), date.
- Markdown destinations: `# Title` at top, then a blank line, then a
  metadata block (author / date / course) as plain lines.

### Page numbering

- APA 7 §2.18 specifies a running head with page number in the top-right corner; student papers optional page-number-only per professor convention.

### Footnotes

APA 7 prefers parenthetical author-date over footnotes; use footnotes only
for substantive content notes, not citation. Numbered superscript in body,
full note at page bottom (Word) or as a numbered list at section/document
end (markdown).

### Block quotes

Threshold: 40 words. Direct quotes of 40 words or more are rendered as block quotes in source prose (indented, no surrounding quotation marks, citation after the closing punctuation). `[formatting mode]` pre-flight enforces this threshold (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present.

## Paste target expression rules

### google-docs

- pandoc flags: `--citeproc --wrap=none -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — preserves ASCII apostrophes inside italic spans for linguistic glottal-stop notation (e.g., `*Ma'heo'o*`) while letting pandoc's `-smart` writer curl English apostrophes and quotes outside italics. `[formatting mode]` resolves the name to `~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "Apply double-spacing in Google Docs if the destination expects it (Format > Line & paragraph spacing > Double)."
- Post-pandoc transforms: strip pandoc fenced-div markers from the References block (`sed -e '/^::: /d' -e '/^:::$/d'`); Google Docs' "Paste as markdown" renders the `:::` wrappers as literal text. The `-header_attributes` pandoc extension handles the heading-attribute counterpart (`# References {#references .unnumbered}`).

### plain-markdown

- pandoc flags: `--citeproc --wrap=preserve -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — same rationale as the google-docs target; most destinations (Obsidian, Notion, GitHub render) expect Unicode typography rather than ASCII.
- Paste-time instructions: (none)
- Post-pandoc transforms: strip pandoc fenced-div markers from the References block (`sed -e '/^::: /d' -e '/^:::$/d'`); most destinations (Obsidian, Notion, GitHub render, Reddit) paste the `:::` wrappers as literal text.

### word

- pandoc flags: `--citeproc`
- reference.docx: `apa7/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging References, APA title page layout. Optional; file not shipped yet; on absence, pandoc uses default layout and surfaces a tolerable warning.
- Post-pandoc transforms: (none)

### latex

- pandoc flags: `--citeproc --standalone -t latex`
- template.tex: `apa7/template.tex` — article class, 12pt Times-family, 1in margins, double-spaced body, hanging-indent References. `iftex` guard makes the template compile under `pdflatex`, `xelatex`, and `lualatex`. Required; `[formatting mode]` resolves the relative path to `~/.claude/style/apa7/template.tex` and adds `--template=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Compile with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)."
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
