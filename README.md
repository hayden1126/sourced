# Sourced

A Claude Code setup for rigorous academic research, drafting, and editing. The primary agent (academic-researcher) lives in each project's `CLAUDE.md`; a parallel-research subagent (source-finder) lives globally in `~/.claude/agents/`.

## What's in here

- **Academic-researcher rules** (inlined into per-project `CLAUDE.md`). Runs across nine modes (collaborative, red team, babble, research, plan, outlining, refining, writing, editing) with an explicit intake-brief step and autonomy-level controls before planning.
- **`source-finder`** — a globally-installed subagent, dispatched in parallel by the main thread for multi-topic research. Each finder verifies its own sources, writes to a shard file, and returns a structured report. The main thread merges shards with ID collision resolution.
- **Citation log schema** — machine-readable record of every citation with `exact_quote`, `surrounding_context`, and `claim_supported` fields. Source of truth for the References section.

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation.** Explicit rules for sentence structure, stance, analogies, punctuation, brevity. No em dashes. No AI-flavored academic phrasing.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Announcement required on every mode switch. Outlining is purely generative; refining owns integrity checking; sign-off gates prevent premature advancement.

## Install

Clone wherever you keep repos. `install.sh` finds itself via `$BASH_SOURCE`, so the clone path doesn't matter.

```bash
git clone https://github.com/hayden1126/sourced.git
cd sourced
./install.sh --global-only      # first time, from inside the repo
```

On first run you'll be prompted for your name. It gets saved to `~/.claude/sourced.config` and substituted into the templates on every render.

After `--global-only`, the global files are available to Claude Code from any working directory:

- `~/.claude/agents/source-finder.md`
- `~/.claude/citations/schema.md`
- `~/.claude/templates/brief.template.md`

These paths are fixed — the install targets always go to `~/.claude/`, regardless of where the repo itself lives.

## Per-project setup

Each writing project gets its own `CLAUDE.md` (the academic-researcher definition, rendered with your name). Run `install.sh` from inside the project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh
```

This re-renders global files (cheap, idempotent) and drops `CLAUDE.md` into the project directory. With `--brief <name>` it also drops an empty `<name>.brief.md` matching the section-6 schema:

```bash
/path/to/sourced/install.sh --brief my_paper
# → creates CLAUDE.md and my_paper.brief.md in the current directory
```

### Updating a project's CLAUDE.md

When you pull new changes to the sourced repo and want to refresh a project's CLAUDE.md without losing your "Active project state" section:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --update
```

This replaces only the content between the `<!-- sourced:begin managed -->` and `<!-- sourced:end managed -->` sentinels. Everything outside the sentinels (your project-specific notes, active briefs, etc.) is preserved.

### Overwriting outright

If a CLAUDE.md exists but you want a fresh render regardless:

```bash
/path/to/sourced/install.sh --force
```

## Flags reference

| Flag | Effect |
|------|--------|
| `--global-only` | Install or refresh global files (`~/.claude/agents/source-finder.md`, `~/.claude/citations/schema.md`, `~/.claude/templates/brief.template.md`) only. Skip CLAUDE.md. |
| `--project <path>` | Drop CLAUDE.md into `<path>` instead of `$PWD`. |
| `--force` | Overwrite existing CLAUDE.md (and brief, if `--brief`) without asking. |
| `--update` | Refresh the managed block of an existing CLAUDE.md, preserving content outside the sentinels. |
| `--brief <name>` | Also drop `<name>.brief.md` into the project from `templates/brief.template.md`. |

## Per-project files

| Path | Scope |
|------|-------|
| `~/.claude/agents/source-finder.md` | global subagent |
| `~/.claude/citations/schema.md` | global citation log schema |
| `~/.claude/templates/brief.template.md` | global brief template |
| `<project>/CLAUDE.md` | per-project; contains the inlined academic-researcher rules |
| `<project>/<draft>.brief.md` | per-project, next to the draft |
| `<project>/<draft>.citations.json` | per-project, next to the draft |
| `<project>/.claude/citations/working.citations.json` | per-project, pre-draft |
| `<project>/.claude/citations/working.<finder-id>.json` | per-project, source-finder shards |

## Change your name

Edit or delete `~/.claude/sourced.config` and re-run `./install.sh --global-only`.

## Structure

```
sourced/
├── agents/
│   └── source-finder.md          # template with {{USER}}, installs to ~/.claude/agents/
├── citations/
│   └── schema.md                 # template with {{USER}}, installs to ~/.claude/citations/
├── templates/
│   ├── CLAUDE.md                 # template with {{USER}}, rendered into each project
│   └── brief.template.md         # template with {{USER}}, installs globally and rendered per-project on --brief
├── install.sh                    # global + per-project install
└── README.md
```

## Migration from earlier versions

If you installed an earlier version of sourced that placed `academic-researcher.md` as a subagent at `~/.claude/agents/academic-researcher.md`, running the new `install.sh` will remove that file automatically. The agent content now lives in each project's `CLAUDE.md`.

## License

None specified. Private repo for now.
