# Style: Chicago 17 (Notes-Bibliography)

This file is the per-project style reference read by `[formatting mode]` (CLAUDE.md §7). Rendering of inline footnotes, short-form references, ibid. behavior, and bibliography entries is delegated to `pandoc --citeproc` reading the vendored CSL file declared below. This file specifies only what pandoc+CSL does not encode: document layout, paste-target flags, post-pandoc hooks, and special-token policy.

## Style identity

- Name: Chicago Manual of Style, 17th edition — Notes and Bibliography system.
- Shape: footnote
- In-text marker: footnote
- List heading: Bibliography
- Authority: The Chicago Manual of Style, 17th ed. (University of Chicago Press, 2017), chapters 14 (notes and bibliography) and 13 (quotations).
- Default for: history, theology, art history, classics, and other humanities using footnote citation.
- Source consulted:
  - https://www.chicagomanualofstyle.org/ (publisher-run; subscription; edition confirmation and sample paper); accessed 2026-04-19.
  - Sample paper: https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html (free portion, notes-bibliography examples); accessed 2026-04-19.
- CSL provenance:
  - file: chicago17-nb/chicago-notes-bibliography-17th-edition.csl
  - source: github.com/citation-style-language/styles
  - fetched: 2026-04-19
  - CSL title: "Chicago Manual of Style 17th edition (notes and bibliography)"
- On-demand references:
  - `chicago17-nb/classical-abbreviations.md` — bundled with this style; content mirrors `chicago17-ad/classical-abbreviations.md`.
  - Hook: after pandoc renders output, walk each footnote body and each bibliography entry; for every entry whose CSL-JSON `author[].family` matches an author in the sidecar's allowlist, rewrite the rendered title per the sidecar's abbreviation column. Applies to all paste targets.
- Last reviewed: 2026-04-19.

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

- CMOS 17 §1.7 specifies page numbers top-right or top-center; numbered footnotes restart at 1 on each new page in Word output.

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

Threshold: 100 words (roughly five typed lines). Rendered as block quotes per Chicago 17 §13.10. `[editing mode]` enforces; `[formatting mode]` verifies in pre-flight (CLAUDE.md §7 step 2) and halts if an over-threshold inline direct quote is still present.

## Paste target expression rules

### google-docs

- pandoc flags: `--citeproc --wrap=none -t markdown-citations-header_attributes-smart`
- lua-filter: `smart-quotes.lua` — preserves ASCII apostrophes inside italic spans for linguistic glottal-stop notation while letting pandoc's `-smart` writer curl English apostrophes and quotes outside italics. `[formatting mode]` resolves the name to `~/.claude/filters/<name>` and adds `--lua-filter=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Apply hanging indent to Bibliography after pasting (Format > Align > Indentation options > Special > Hanging)."
  - "Footnotes paste as inline markers in Google Docs; convert to Google Docs footnotes using Insert > Footnote if needed. Google Docs does not round-trip pandoc `[^N]: body` blocks into native footnotes automatically."
- Post-pandoc transforms:
  1. Strip pandoc fenced-div markers (`sed -e '/^::: /d' -e '/^:::$/d'`); Google Docs' "Paste as markdown" renders the `:::` wrappers as literal text. The `-header_attributes` pandoc extension handles the heading-attribute counterpart (`# Bibliography {#bibliography .unnumbered}`).
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
- reference.docx: `chicago17-nb/reference-styled.docx` — Times New Roman 12pt, double-spaced body, 0.5in hanging Bibliography paragraph style, footnote paragraph style. Optional; on absence, pandoc default layout; surface as a tolerable warning in the step 8 report.
- Post-pandoc transforms: classical-abbreviations rewrite.

### latex

- pandoc flags: `--citeproc --standalone -t latex`
- template.tex: `chicago17-nb/template.tex` — article class, 12pt Times-family, 1in margins, single-spaced body. Footnotes render natively via pandoc's `\footnote{...}` commands emitted by citeproc; no custom footnote machinery needed. Required; `[formatting mode]` resolves the relative path to `~/.claude/style/chicago17-nb/template.tex` and adds `--template=<absolute-path>` to the pandoc invocation.
- Paste-time instructions:
  - "Compile with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)."
- Post-pandoc transforms: classical-abbreviations rewrite.

## Special tokens

- `[VERIFY: ...]` and `[UNSOURCED]` in source prose are ERRORS at format time. Formatting mode halts and surfaces every occurrence. See CLAUDE.md §7 [formatting mode] step 2.
