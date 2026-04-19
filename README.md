# Sourced

A Claude Code setup for writing academic papers with the model in the loop. Built around three non-negotiables: every citation is verified and full-text accessible, every paraphrase matches source scope, and the writer's voice stays theirs instead of getting flattened into AI-flavored academic prose.

For students and researchers who want Claude-generated scholarship they can defend without rewriting it line by line.

The primary agent (academic-researcher) lives in each project's `CLAUDE.md`. Two subagents live globally in `~/.claude/agents/`: source-finder (parallel source research, dispatched during `[research mode]`) and voice-extractor (one-shot voice calibration from a corpus of writing samples).

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation, with generator-level guardrails.** Per-author voice files specify sentence structure, stance, pacing, concept setup, and punctuation habits. A global inventory of AI-writing signatures (em dashes, "not X but Y" pivots, ornamental triads, throat-clearing adverbs, demonstrative-noun openers) applies regardless of voice and is enforced at both writing and editing time.
- **Paraphrase as default.** Direct quotes are reserved for wording that's itself the evidence. Quote-density flags fire on over-quoted paragraphs in both writing and editing modes.
- **Citation rendering is decoupled from authoring.** Prose carries Pandoc-style IDs (`[@id]`, `@id`, `[@id, p. N]`); a separate formatting mode resolves them per style (APA 7 or Chicago 17 author-date) into a sibling output file for a chosen paste target.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Ten cognitive modes, one announced per transition. Gates between stages require explicit approval; silence is not an override.
- **Defense-in-depth for iron rules.** Category-level voice prohibitions ("no em dashes") are checked in three places: inside `voice-extractor` at generation time, inside `academic-researcher` at caller-return time, and inside `install.sh` at render time. Any one layer missing doesn't ship a broken voice.

## Prerequisites

- [Claude Code](https://claude.com/product/claude-code) installed. This project configures it; it does not replace it.
- `bash` available for running `install.sh`.
- `~/.claude/` writable (the installer creates it on first run).
- A directory for your paper. Any directory works: a fresh folder, a git repo you already have, or an existing project.

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
- [`docs/INSTALL.md`](./docs/INSTALL.md) — full install, updating, flags reference, renaming yourself.
- [`docs/MODES.md`](./docs/MODES.md) — modes reference + end-to-end workflow walkthrough + gate discipline.
- [`docs/VOICES.md`](./docs/VOICES.md) — voice system, `voice-extractor` usage, iron rules, defense-in-depth.
- [`docs/STYLES.md`](./docs/STYLES.md) — citation styles, paste targets, `[formatting mode]`, authoring a custom style.

## License

None specified. Private repo for now.

## Migration from earlier versions

If you installed an earlier version of sourced that placed `academic-researcher.md` as a subagent at `~/.claude/agents/academic-researcher.md`, running the new `install.sh` will remove that file automatically. The agent content now lives in each project's `CLAUDE.md`.

Projects installed before CLAUDE.md §10 (*Generation signatures to rewrite*) existed can pull the new rules via `install.sh --update` from within the project directory; the managed block refreshes while preserving any non-managed content you've added outside the sentinels.
