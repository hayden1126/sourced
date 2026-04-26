# Style: IEEE

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline bracket numbers and References list entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

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
  - CSL title: "IEEE Reference Guide version 11.29.2023"
- On-demand references: (none)
- Last reviewed: 2026-04-19.

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

- pandoc flags: `--citeproc --wrap=none -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — preserves ASCII apostrophes inside italic spans for linguistic glottal-stop notation while letting pandoc's `-smart` writer curl English apostrophes and quotes outside italics. `[formatting mode]` resolves the name to `~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Apply hanging indent to References after pasting (Format > Align > Indentation options > Special > Hanging)."
- Post-pandoc transforms: strip pandoc fenced-div markers from the References block (`sed -e '/^::: /d' -e '/^:::$/d'`); Google Docs' "Paste as markdown" renders the `:::` wrappers as literal text. The `-header_attributes` pandoc extension handles the heading-attribute counterpart (`# References {#bibliography .unnumbered}` — pandoc emits `{#bibliography}` for any reference section title via `--metadata reference-section-title=`, regardless of the heading text).

### plain-markdown

- pandoc flags: `--citeproc --wrap=preserve -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — same rationale as the google-docs target.
- Paste-time instructions: (none)
- Post-pandoc transforms: strip pandoc fenced-div markers from the References block (`sed -e '/^::: /d' -e '/^:::$/d'`); most destinations (Obsidian, Notion, GitHub render, Reddit) paste the `:::` wrappers as literal text.

### word

- pandoc flags: `--citeproc`
- reference.docx: `ieee/reference-styled.docx` — Times New Roman 10pt / two-column body, single-spaced References with hanging indent, per IEEE manuscript template. Optional; on absence, pandoc default layout; surface tolerable warning.
- Post-pandoc transforms: (none)

### latex

- pandoc flags: `--citeproc --standalone -t latex`
- template.tex: `ieee/template.tex` — `IEEEtran` class (conference option), single-column body, IEEE-matching typography. `CSLReferences` environment redefined to use a flat list (no hanging indent) so bracketed-number citations compile under IEEEtran's narrow columns. Required; `[formatting mode]` resolves the relative path to `~/.claude/style/ieee/template.tex` and adds `--template=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Compile with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)."
  - "IEEEtran ships with TeX Live in the `collection-publishers` bundle (Debian: `texlive-publishers`). A minimal TeX Live install may need this package before compilation succeeds."
- Post-pandoc transforms: (none)

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
