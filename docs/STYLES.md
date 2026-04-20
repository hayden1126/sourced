# Styles

[← Back to README](../README.md)

Citation and document-layout rules live in a per-project `style.md` rendered from a named style in the style library. Style is per-project; different projects can carry different styles, and the style on any project can be switched later.

## Shipped styles

| Name | Shape | Typical domain |
|------|-------|----------------|
| `apa7` | author-date | Behavioral and social sciences. Default for new projects. |
| `chicago17-ad` | author-date | Humanities / social science with parenthetical Chicago. |
| `chicago17-nb` | footnote + bibliography | History, theology, art history; footnote-centric humanities work. |
| `ieee` | numeric-sequence | Electrical / computer engineering, computer science, IEEE venues. |
| `mla9` | author-page | Literary studies, languages, humanities essays. |

Each renders citations from Pandoc-style IDs (`[@id]`, `@id`, `[@id, p. N]`) in source prose into style-compliant inline citations (or footnotes, for `chicago17-nb`) and References entries (or Bibliography / Works Cited per the style's terminology) at `[formatting mode]` time. Additional styles in the ROADMAP (Vancouver, AMA, Harvard, ACM, ACS, Turabian 9, CSE, MHRA) follow the same structural patterns.

## Schema transition in progress

The 5 shipped style files are mid-migration from a rendering-rules-in-markdown schema to the slim schema above. After this PR, chicago17-nb, ieee, and mla9 are fully slim; apa7 and chicago17-ad still carry dead-weight old rendering-rule sections (§Inline citations, §References list, §Footnote citations, §Numbering rules) that `[formatting mode]` no longer reads. The dead-weight will be removed in the next (final) migration PR. See `docs/specs/2026-04-19-csl-direct-consumption-design.md` for the full shift description.

## Pick a style at install

```bash
/path/to/sourced/install.sh --style apa7           # default
/path/to/sourced/install.sh --style chicago17-ad
```

`--style` is validated before any project file is written. An invalid name errors out cleanly; no half-installed project.

## Style file structure

Each style file has a fixed section structure so `[formatting mode]` can look up rules by section name. Sections are addressable (e.g., "see §Style identity.CSL provenance", "see §Paste target expression rules.google-docs"). The required sections are the same for every style; rendering of inline citations, references, and footnotes is delegated to `pandoc --citeproc` reading the vendored CSL file.

Required sections (every style):

| Section | Role |
|---------|------|
| §Style identity | Name, Shape (audit-only), In-text marker (audit-only), List heading (runtime-read), Authority, Default for, Source consulted, CSL provenance (file / source / fetched / CSL title), On-demand references (post-pandoc hook per style), Last reviewed. |
| §Document layout | Fonts and spacing, Margins, Heading hierarchy, Title block, Page numbering, (optional) Footnotes, Block quotes (threshold if any — enforced in `[editing mode]`, verified in `[formatting mode]` pre-flight). |
| §Paste target expression rules | Per-target subsections (google-docs, plain-markdown, word): pandoc flags, paste-time instructions, post-pandoc transforms, reference.docx path (word only). |
| §Special tokens | `[VERIFY: ...]` and `[UNSOURCED]` policy. Most styles carry the standard block. |

## Paste targets

`[formatting mode]` renders into one of the target formats defined under the style's `§Paste target expression rules` section. The target is required at mode invocation: `[formatting mode for google-docs]`, `[formatting mode for plain-markdown]`, `[formatting mode for word]`. An unspecified target is a refusal, not a default.

All three targets are rendered by `pandoc --citeproc` reading the style's vendored CSL file. Flags per target (including output markdown dialect, wrap behavior, and reference.docx) live in the style's `§Paste target expression rules` subsections.

- **`google-docs`** — markdown output tuned for Google Docs paste (smart quotes, en-dashes preserved). Features not expressible at paste time (hanging indents, custom headers) surface as a one-line instruction at the top of the output.
- **`plain-markdown`** — faithful markdown pass-through.
- **`word`** — pandoc emits `.docx` directly, optionally styled by a reference.docx bundled per style.
- **`latex`** — reserved; not implemented.

## How `[formatting mode]` uses `style.md`

`[formatting mode]` is the only mode that reads `style.md`. All other modes emit style-agnostic Pandoc IDs, so source prose is decoupled from style choice. Switching styles is cheap: `install.sh --style <new>` then re-run formatting.

The formatting procedure (abbreviated; see CLAUDE.md §7 for the full version):

1. Read `style.md` + the citation log. Verify CSL file exists on disk.
2. Pre-flight. Halt on `[VERIFY: ...]`, `[UNSOURCED]`, rendered citation strings, unresolved IDs, stale `retrieved_at`, or inline direct quotes exceeding the style's block-quote threshold.
3. Pre-pandoc pass: collapse per-instance citation IDs into a derived `<draft>.pandoc.md`. Source prose unchanged.
4. Emit CSL-JSON bibliography from the log to `<draft>.bib.json` per `citations/csl-json-emitter.md`.
5. Invoke pandoc with flags from `§Paste target expression rules.<target>`; output per target (`.docx`, `.gdocs.md`, `.plain.md`).
6. Handle pandoc stderr: halt on blocking warnings (unresolved citation, missing type, CSL-parse error); surface tolerable warnings in the report.
7. Post-pandoc pass: apply On-demand references transforms (e.g., classical-abbreviations rewrite); prepend paste-time instructions.
8. Report.

Re-running with a different style or target is idempotent: each run writes its own sibling file.

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
