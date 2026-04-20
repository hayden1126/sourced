# Sourced

A Claude Code setup for writing academic papers with the model in the loop. Built around three non-negotiables: every citation is verified and full-text accessible, every paraphrase matches source scope, and the writer's voice stays theirs instead of getting flattened into AI-flavored academic prose.

For students and researchers who want Claude-generated scholarship they can defend without rewriting it line by line.

The primary agent (academic-researcher) lives in each project's `CLAUDE.md`. Two subagents live globally in `~/.claude/agents/`: source-finder (parallel source research, dispatched during `[research mode]`) and voice-extractor (one-shot voice calibration from a corpus of writing samples).

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation, with generator-level guardrails.** Per-author voice files specify sentence structure, stance, pacing, concept setup, and punctuation habits. A global inventory of AI-writing signatures (em dashes, "not X but Y" pivots, ornamental triads, throat-clearing adverbs, demonstrative-noun openers) applies regardless of voice and is enforced at both writing and editing time.
- **Paraphrase as default.** Direct quotes are reserved for wording that's itself the evidence. Quote-density flags fire on over-quoted paragraphs in both writing and editing modes.
- **Citation rendering is decoupled from authoring.** Prose carries Pandoc-style IDs (`[@id]`, `@id`, `[@id, p. N]`); a separate formatting mode resolves them per style (five shipped: APA 7, Chicago 17 author-date, Chicago 17 notes-bibliography, IEEE, MLA 9) into a sibling output file for a chosen paste target. All paste targets render through `pandoc --citeproc` reading the style's vendored CSL file.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Ten cognitive modes, one announced per transition. Gates between stages require explicit approval; silence is not an override.
- **Defense-in-depth for iron rules.** Category-level voice prohibitions ("no em dashes") are checked in three places: inside `voice-extractor` at generation time, inside `academic-researcher` at caller-return time, and inside `install.sh` at render time. Any one layer missing doesn't ship a broken voice.
- **Per-voice exemption syntax with install-time validation.** §10's Never list carries stable IDs; a voice library file can exempt specific rules via `## §10 exemptions` bullets. `install.sh` validates the IDs against the canonical set extracted from CLAUDE.md and aborts on typos. Silence is not permission.
- **Bundled skills for extraction tasks.** `browser-reader-extract` connects to a user-launched Chrome and extracts text with `[p. N]` page markers from DRM'd browser readers (OverDrive Read proven; Kindle Cloud Reader, Scribd extendable via a documented pattern). Installed into `~/.claude/skills/` by default; writers who never need it pay zero setup cost.

## Prerequisites

- [Claude Code](https://claude.com/product/claude-code) installed. This project configures it; it does not replace it.
- `bash` available for running `install.sh`.
- `~/.claude/` writable (the installer creates it on first run).
- A directory for your paper. Any directory works: a fresh folder, a git repo you already have, or an existing project.
- **poppler-utils** (`pdftotext`, `pdfinfo`, `pdftoppm`). Claude Code's Read tool renders PDFs through `pdftoppm`; `[research mode]` extracts text from PDF sources via `pdftotext`.
- **pandoc** 3.1+. Required by every `[formatting mode]` paste target (`word`, `google-docs`, `plain-markdown`); all three render through the pandoc + citeproc + CSL pipeline.
- **python3**. Used at per-project install time to cross-check a vendored CSL file's `<title>` against the style's declaration (`validate_csl_title` in `install.sh`). Ships by default with current Debian, Ubuntu, WSL, and macOS; install via your package manager if missing.

`install.sh` checks that `pdftotext`, `pandoc`, and `python3` are all on PATH and aborts with a clear install command if any is missing. It does not install them for you; use your package manager.

Install on Debian, Ubuntu, or WSL (python3 is typically already present):

```bash
sudo apt-get install -y poppler-utils pandoc python3
```

On macOS (python3 ships with recent macOS; `brew install python3` if missing):

```bash
brew install poppler pandoc
```

**Optional:** the `browser-reader-extract` skill (for extracting text from DRM'd browser readers like OverDrive, Kindle Cloud Reader, Scribd) needs Node 18+ and `puppeteer-core`. Install Node via your package manager; on first use of the skill, run `npm install` inside `~/.claude/skills/browser-reader-extract/` to fetch `puppeteer-core`. Writers who never use the skill pay zero setup cost.

## Quickstart

```bash
# first time: clone and install globally
git clone https://github.com/hayden1126/sourced.git
cd sourced
./install.sh --global-only

# per-project: render CLAUDE.md, voice.md, style.md, and an empty brief
cd ~/writing/my-paper
/path/to/sourced/install.sh --brief my_paper
```

On first run you'll be prompted for your name. It gets saved to `~/.claude/sourced.config`.

After `--brief my_paper`, the project carries:
- `CLAUDE.md` — the agent operating rules.
- `voice.md` — the active voice (default: `academic`).
- `style.md` — the active citation style (default: `apa7`).
- `my_paper.brief.md` — empty intake brief for this paper.

Open Claude Code from inside the project directory and start a session. The agent opens in `[collaborative mode]` and will propose filling out the brief first.

## Documentation

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — surface-area map: files, modes, subagents, invariants, extension points.
- [`ROADMAP.md`](./ROADMAP.md) — forward-looking feature ideas organized by theme and priority, plus declared scope boundaries.
- [`docs/INSTALL.md`](./docs/INSTALL.md) — full install, updating, flags reference, renaming yourself.
- [`docs/MODES.md`](./docs/MODES.md) — modes reference + end-to-end workflow walkthrough + gate discipline.
- [`docs/VOICES.md`](./docs/VOICES.md) — voice system, `voice-extractor` usage, iron rules, defense-in-depth, §10 exemption syntax, direct-quote carve-out.
- [`docs/STYLES.md`](./docs/STYLES.md) — citation styles, paste targets (including the `word` pandoc+CSL pipeline), on-demand style references, `[formatting mode]`, authoring a custom style.
- [`docs/SKILLS.md`](./docs/SKILLS.md) — shipped skills (`browser-reader-extract`), when to reach for them, how to author new ones.

## License

None specified. Private repo for now.

## Migration from earlier versions

If you installed an earlier version of sourced that placed `academic-researcher.md` as a subagent at `~/.claude/agents/academic-researcher.md`, running the new `install.sh` will remove that file automatically. The agent content now lives in each project's `CLAUDE.md`.

Projects installed before CLAUDE.md §10 (*Generation signatures to rewrite*) existed can pull the new rules via `install.sh --update` from within the project directory; the managed block refreshes while preserving any non-managed content you've added outside the sentinels.
