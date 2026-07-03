# Sourced

A Claude Code setup for writing academic papers with the model in the loop. Built around three non-negotiables: every citation is verified and full-text accessible, every paraphrase matches source scope, and the writer's voice stays theirs instead of getting flattened into AI-flavored academic prose.

For students and researchers who want Claude-generated scholarship they can defend without rewriting it line by line.

The primary agent (academic-researcher) lives in each project's `CLAUDE.md`. Four subagents live globally in `~/.claude/agents/`: source-finder (parallel source research, dispatched during `[research mode]`), voice-extractor (one-shot voice calibration from a corpus of writing samples), prose-drafter (isolated section drafting during `[writing mode]`), and sourced-helper (read-only Q&A about the framework itself).

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation, with generator-level guardrails.** Per-author voice files specify tone, structure, and dimension rules across 4 axes. Voice-extractor selects one of 6 shipped register skeletons (academic, casual, technical, journalistic, narrative, hybrid) based on corpus classification. A global inventory of AI-writing signatures (em dashes, "not X but Y" pivots, ornamental triads, throat-clearing adverbs, demonstrative-noun openers) applies regardless of register and is enforced at both writing and editing time.
- **Paraphrase as default.** Direct quotes are reserved for wording that's itself the evidence. Quote-density flags fire on over-quoted paragraphs in both writing and editing modes.
- **Citation rendering is decoupled from authoring.** Prose carries Pandoc-style IDs (`[@id]`, `@id`, `[@id, p. N]`); a separate formatting mode resolves them per style into a sibling output file for a chosen paste target. Five styles ship (APA 7, Chicago 17 author-date, Chicago 17 notes-bibliography, IEEE, MLA 9) across four paste targets (`word`, `google-docs`, `plain-markdown`, `latex`). All paste targets render through `pandoc --citeproc` reading the style's vendored CSL file.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Twelve cognitive modes, one announced per transition. Gates between stages require explicit approval; silence is not an override.
- **Defense-in-depth for iron rules.** Category-level voice prohibitions ("no em dashes") are checked in three places: inside `voice-extractor` at generation time, inside `academic-researcher` at caller-return time, and inside the `sourced` CLI at render time. Any one layer missing doesn't ship a broken voice.
- **Per-voice exemption syntax with install-time validation.** §10's Never list carries stable IDs; a voice library file can exempt specific rules via `## §10 exemptions` bullets. The `sourced` CLI validates the IDs against the canonical set extracted from CLAUDE.md and aborts on typos. Silence is not permission.
- **Bundled skills for extraction tasks.** `browser-reader-extract` connects to a user-launched Chrome and extracts text with `[p. N]` page markers from DRM'd browser readers (OverDrive Read proven; Kindle Cloud Reader, Scribd extendable via a documented pattern). Installed into `~/.claude/skills/` by default; writers who never need it pay zero setup cost.

## Prerequisites

- [Claude Code](https://claude.com/product/claude-code) installed. This project configures it; it does not replace it.
- Python 3.10+ (`python3 --version`).
- `pipx` for installing the `sourced` CLI. (`brew install pipx` on macOS; `sudo apt install pipx python3-venv` on Ubuntu/WSL; `winget install pipx` on Windows native.) After installing pipx: `pipx ensurepath`, then **open a new terminal**.
- `~/.claude/` writable (the CLI creates it on first run).
- A directory for your paper. Any directory works: a fresh folder, a git repo you already have, or an existing project.
- **poppler-utils** (`pdftotext`, `pdfinfo`, `pdftoppm`). Claude Code's Read tool renders PDFs through `pdftoppm`; `[research mode]` extracts text from PDF sources via `pdftotext`.
- **pandoc** 3.1+. Required by every `[formatting mode]` paste target (`word`, `google-docs`, `plain-markdown`, `latex`); all four render through the pandoc + citeproc + CSL pipeline.
- **TeX Live** (optional). Only needed if you'll compile the `[formatting mode for latex]` output to PDF. `sourced` emits a `.tex` file; compilation is your job. Not checked by `sourced check`. See [`docs/INSTALL.md`](./docs/INSTALL.md#optional-tex-live-for-the-latex-paste-target) for package guidance per platform.

Run `sourced check` to verify all prereqs are present + `~/.claude/` is healthy + installed voices are intact. It does not install missing tools for you; use your package manager.

Install on Debian, Ubuntu, or WSL (python3 is typically already present):

```bash
sudo apt-get install -y poppler-utils pandoc python3
```

On macOS (python3 ships with recent macOS; `brew install python3` if missing):

```bash
brew install poppler pandoc
```

**Optional:** the `browser-reader-extract` skill (for extracting text from DRM'd browser readers like OverDrive, Kindle Cloud Reader, Scribd) needs Node 18+ and `puppeteer-core`. Install Node via your package manager; on first use of the skill, run `npm install` inside `~/.claude/skills/browser-reader-extract/` to fetch `puppeteer-core`. Writers who never use the skill pay zero setup cost.

## Install

```bash
# HTTPS (default for non-dev users; works through corporate firewalls):
pipx install 'git+https://<TOKEN>@github.com/hayden1126/sourced.git'

# SSH (power-user path; pre-seed known_hosts on a fresh machine):
ssh-keyscan github.com >> ~/.ssh/known_hosts
pipx install git+ssh://git@github.com/hayden1126/sourced.git
```

Verify and set up:

```bash
sourced --version
sourced check                # verifies prereqs + ~/.claude/ readiness
sourced global-install       # populates ~/.claude/ (prompts for your name on first run)
```

Per-project:

```bash
cd ~/writing/new-paper
sourced install --brief my_paper --voice academic --style apa7

# or sugar:
cd ~/writing
sourced new my-paper --voice academic --style apa7
```

After install, the project carries:
- `CLAUDE.md` — the agent operating rules.
- `config/voice.md` — the active voice (default: `academic`).
- `config/style.md` — the active citation style (default: `apa7`).
- `config/my_paper.brief.md` — empty intake brief for this paper (with `--brief`).

Open Claude Code from inside the project directory and start a session. The agent opens in `[collaborative mode]` and will propose filling out the brief first.

Updates:

```bash
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@main'
sourced global-install       # idempotent
cd ~/writing/my-paper
sourced update               # refresh managed block of CLAUDE.md
```

For deeper troubleshooting (pipx gotchas, conda interference, port-22-blocked networks), see [`docs/INSTALL.md`](./docs/INSTALL.md). For a one-shot answer to "how do I X" questions, ask Claude Code — the bundled `sourced-helper` agent activates on framework questions and points at the right command or file.

## Documentation

- [`VISION.md`](./VISION.md) — why the project exists: the six non-negotiables, what sourced is not, and the bar new work must clear.
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — surface-area map: files, modes, subagents, invariants, extension points.
- [`ROADMAP.md`](./ROADMAP.md) — forward-looking feature ideas organized by theme and priority, plus declared scope boundaries.
- [`docs/INSTALL.md`](./docs/INSTALL.md) — full install, updating, flags reference, renaming yourself.
- [`docs/MODES.md`](./docs/MODES.md) — modes reference + end-to-end workflow walkthrough + gate discipline.
- [`docs/VOICES.md`](./docs/VOICES.md) — voice system, `voice-extractor` usage, iron rules, defense-in-depth, §10 exemption syntax, direct-quote carve-out.
- [`docs/STYLES.md`](./docs/STYLES.md) — citation styles, paste targets (including the `word` pandoc+CSL pipeline), on-demand style references, `[formatting mode]`, authoring a custom style.
- [`docs/SKILLS.md`](./docs/SKILLS.md) — shipped skills (`browser-reader-extract`), when to reach for them, how to author new ones.

## License

Private repo; no license granted. Direction and scope live in [`VISION.md`](./VISION.md).

## Migration from earlier versions

**From `install.sh`-based installs:** the bash installer is retired. `pipx install` the new CLI per the install section above, then `sourced global-install` (idempotent — overwrites the bash-era files in `~/.claude/`). Projects installed via `install.sh` keep working; run `sourced update` from inside each one to refresh its managed block.

**From even earlier:** if you installed a version that placed `academic-researcher.md` at `~/.claude/agents/academic-researcher.md`, `sourced global-install` will not remove it — but the agent content now lives in each project's `CLAUDE.md`, so the standalone agent file is dead weight. Delete it manually if you want a clean tree.

Projects installed before CLAUDE.md §10 (*Generation signatures to rewrite*) existed can pull the new rules via `sourced update` from within the project directory; the managed block refreshes while preserving any non-managed content you've added outside the sentinels.
