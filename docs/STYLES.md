# Styles

[← Back to README](../README.md)

Citation and document-layout rules live in a per-project `style.md` rendered from a named style in the style library. Style is per-project; different projects can carry different styles, and the style on any project can be switched later.

## Shipped styles

- **`apa7`** — APA 7 author-date. Default for new projects.
- **`chicago17-ad`** — Chicago 17 author-date.

Both render citations from Pandoc-style IDs (`[@id]`, `@id`, `[@id, p. N]`) in source prose into style-compliant inline citations and References entries at `[formatting mode]` time.

## Pick a style at install

```bash
/path/to/sourced/install.sh --style apa7           # default
/path/to/sourced/install.sh --style chicago17-ad
```

`--style` is validated before any project file is written. An invalid name errors out cleanly; no half-installed project.

## Style file structure

Each style file ships a fixed section structure so `[formatting mode]` can look up a single rule without rereading the file. Sections are addressable (e.g., "see §Inline / Two authors").

- **§Style identity** — name, authority (manual + edition), default domain, last-reviewed date.
- **§Inline citations** — resolution rules for every Pandoc ID case (one author, two authors, three-plus, group author, no author, no date, multi-citation, direct quotes, classical texts).
- **§References list** — entry format per source type (journal article, book, chapter, web page, translation of primary text, reprint), sort order, indentation, URL/DOI handling.
- **§Document layout** — title block, heading hierarchy, body text spacing, footnotes.
- **§Paste target expression rules** — how the style's conventions are expressed in specific destination formats (see below).
- **§Special tokens** — how `[VERIFY: ...]` and `[UNSOURCED]` tokens in source prose are treated at format time.

## Paste targets

`[formatting mode]` renders into one of the target formats defined under the style's **Paste target expression rules** section. The target is required at mode invocation: `[formatting mode for google-docs]`, `[formatting mode for plain-markdown]`. An unspecified target is a refusal, not a default.

Currently shipped:

- **`google-docs`** — single markdown block with smart quotes, en-dashes, and italics preserved. Google Docs converts on paste. Features not expressible at paste time (hanging indents, double-spacing) emit a one-line instruction at the top of the output file.
- **`plain-markdown`** — faithful pass-through. Resolves citation IDs and generates References; applies no destination-specific transforms. Suitable for archival copies and further conversion downstream (Pandoc, etc.).
- **`word`** — implemented for `chicago17-ad`. Runs a pandoc + citeproc pipeline against the shipped CSL file and (optionally) a reference.docx that defines paragraph styles. Emits `<draft>.docx.md` (rendered-markdown intermediate) plus `<draft>.docx` (submission binary). If the reference.docx is not shipped for a style, pandoc default styles are used and the fallback is surfaced in the step-8 report. Not yet shipped for `apa7`.
- **`latex`** — reserved; not implemented.

## How `[formatting mode]` uses `style.md`

`[formatting mode]` is the only mode that reads `style.md`. All other modes emit style-agnostic Pandoc IDs, so source prose is decoupled from style choice. Switching styles is cheap: `install.sh --style <new>` then re-run formatting.

The formatting procedure (abbreviated; see CLAUDE.md §7 for the full version):

1. Read `style.md` + the citation log.
2. Pre-flight scan. Halt if the source prose carries `[VERIFY: ...]` tokens, `[UNSOURCED]` tokens, rendered author-year strings (legacy regressions), unresolved citation IDs, or stale `retrieved_at` timestamps on referenced entries.
3. Resolve every Pandoc ID against `source.authors` + `source.year` in the log, applying the matching rule from `style.md` §Inline citations.
4. **Collapse per-instance citation IDs (target-conditional).** For targets whose downstream renderer dedupes by id (currently `word` via pandoc+citeproc), rewrite `<author>-<year>-NNN` to `<author>-<year>` in the derived markdown so the same source does not emit duplicate References entries. Skip for `google-docs` and `plain-markdown` (our own renderer dedupes directly from the log).
5. Generate References list from the log per `style.md` §References. Deduped across multiple log entries pointing at the same source; sorted per style. For `word`, additionally emit a CSL-JSON bibliography at `<draft>.bib.json` keyed to the collapsed ids.
6. Apply document-layout rules (title block, headings, spacing, indentation) per the target's expression rules. Rules with no expression in the destination (e.g., hanging indents in google-docs) emit a one-line paste-time instruction at the top of the output.
7. Write output to `<draft>.<target>.md` (sibling file). For `word`, additionally invoke pandoc against the intermediate and emit `<draft>.docx`. Source prose is never modified.
8. Report the run: citations resolved, References entries, stale entries handled, paste-time instructions, any reference.docx fallback notice.

Re-running with a different style or target is idempotent: each run writes its own sibling file.

**On-demand style references.** Some styles ship lookup tables too large to carry inline in `style.md`. `[formatting mode]` reads them only when a citation triggers the lookup. Currently shipped for `chicago17-ad`: a per-author classical-works abbreviation table at `~/.claude/style/chicago17-ad/classical-abbreviations.md`, consulted when a citation resolves to an ancient author (Plato, Aristotle, Cicero, Seneca, Augustine, Aquinas, etc.). The pattern scales to any style that wants to offload a rarely-used reference without paying per-format-pass load cost.

## Authoring a custom style

Copy a shipped style as the template and edit:

```bash
cp ~/.claude/style/apa7.md ~/.claude/style/mystyle.md
# edit ~/.claude/style/mystyle.md
/path/to/sourced/install.sh --style mystyle
```

The section structure is fixed and load-bearing — `[formatting mode]` looks up rules by section name. Renaming or dropping sections breaks rendering. Adding a new paste target requires a new subsection under §Paste target expression rules naming the target and specifying expression rules for every layout category the style defines.

Shipped styles at `~/.claude/style/<shipped-name>.md` are refreshed on every install from the repo. User-authored styles (names that don't collide with shipped ones) are left untouched. To customize a shipped style without losing edits, copy to a new name first.

## Switching styles on an existing project

```bash
/path/to/sourced/install.sh --update --style chicago17-ad
```

This replaces `style.md` with the new style and records the choice in the style marker on line 1 of the file. Re-run formatting on any drafts to pick up the new rendering; source prose is unchanged.
