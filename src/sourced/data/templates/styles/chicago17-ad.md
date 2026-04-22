# Style: Chicago 17 (Author-Date)

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline parenthetical author-date citations and References list entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

## Style identity

- Name: Chicago Manual of Style, 17th edition, author-date system.
- Shape: author-date
- In-text marker: parenthetical
- List heading: References
- Authority: The Chicago Manual of Style, 17th ed. (University of Chicago Press, 2017), chapters 14-15 (citations), chapters 1-2 (manuscript layout).
- Default for: humanities and social-science work where the syllabus specifies "Chicago author-date" (or where the professor's own publications use parenthetical author-year style). Not for notes-bibliography (NB) contexts; use chicago17-nb.md for those.
- Source consulted:
  - CMOS 17 (print and paywalled online), chapters 14-15 for citations, chapters 1-2 for manuscript layout.
  - https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-2.html (CMOS Online author-date quick guide, free); accessed 2026-04-19.
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

### Fonts and spacing

- Font: Times New Roman 12 or similar serif default. CMOS 17 §2.8 prefers
  serif for body text.
- Line spacing: double in print/Word destinations; single in markdown unless
  destination overrides.
- Paragraph indent: 0.5 in first-line indent. Markdown: no indent (rendered
  flat); paragraph break is a blank line.

### Margins

- 1 in all sides.

### Heading hierarchy

- CMOS 17 §1.55-1.56 defines five heading levels. The system is more
  flexible than APA's; common practice for short papers uses 2-3 levels.
- Level 1: centered, bold, headline case. Markdown: `## Heading`.
- Level 2: centered, regular weight, headline case. Markdown: `### Heading`.
- Level 3: flush left, bold, headline case. Markdown: `#### Heading`.
- Levels 4 and 5 exist; rarely needed in {{USER}}'s work. Add when first used.

### Title block

- Student papers: separate title page, title centered roughly one-third down
  the page, byline / course / instructor / date stacked centered below.
- Markdown destinations: `# Title` at top, then a blank line, then a
  metadata block (author / date / course) as plain lines.

### Page numbering

- CMOS 17 §1.7 specifies page numbers top-right or top-center.

### Footnotes

The author-date system uses parenthetical citation, not footnotes, for
source attribution. Footnotes are reserved for substantive content notes
(commentary, asides, tangential references). Numbered superscript in body,
full note at page bottom (Word) or as a numbered list at section/document
end (markdown).

### Block quotes

Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10. `[formatting mode]` pre-flight enforces this threshold (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present.

## Paste target expression rules

### google-docs

- pandoc flags: `--citeproc --wrap=none -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — preserves ASCII apostrophes inside italic spans for linguistic glottal-stop notation while letting pandoc's `-smart` writer curl English apostrophes and quotes outside italics. `[formatting mode]` resolves the name to `~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "Apply double-spacing in Google Docs if the destination expects it (Format > Line & paragraph spacing > Double)."
- Post-pandoc transforms:
  1. Strip pandoc fenced-div markers (`sed -e '/^::: /d' -e '/^:::$/d'`); Google Docs' "Paste as markdown" renders the `:::` wrappers as literal text. The `-header_attributes` pandoc extension handles the heading-attribute counterpart (`# References {#references .unnumbered}`).
  2. Classical-abbreviations rewrite (see §Style identity.On-demand references).

### plain-markdown

- pandoc flags: `--citeproc --wrap=preserve -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — same rationale as the google-docs target.
- Paste-time instructions: (none)
- Post-pandoc transforms:
  1. Strip pandoc fenced-div markers (`sed -e '/^::: /d' -e '/^:::$/d'`); most destinations (Obsidian, Notion, GitHub render, Reddit) paste the `:::` wrappers as literal text.
  2. Classical-abbreviations rewrite.

### word

- pandoc flags: `--citeproc`
- reference.docx: `chicago17-ad/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging References. Optional; file not shipped yet; on absence, pandoc uses default layout and surfaces a tolerable warning.
- Post-pandoc transforms: classical-abbreviations rewrite.

### latex

- pandoc flags: `--citeproc --standalone -t latex`
- template.tex: `chicago17-ad/template.tex` — article class, 12pt Times-family, 1in margins, single-spaced body, hanging-indent References. `iftex` guard supports `pdflatex`, `xelatex`, and `lualatex`. Required; `[formatting mode]` resolves the relative path to `~/.claude/style/chicago17-ad/template.tex` and adds `--template=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Compile with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)."
- Post-pandoc transforms: classical-abbreviations rewrite.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
