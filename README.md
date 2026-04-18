# Sourced

A Claude Code setup for writing academic papers with the model in the loop. Built around three non-negotiables: every citation is verified and full-text accessible, every paraphrase matches source scope, and the writer's voice stays theirs instead of getting flattened into AI-flavored academic prose.

For students and researchers who want Claude-generated scholarship they can defend without rewriting it line by line.

The primary agent (academic-researcher) lives in each project's `CLAUDE.md`; a parallel-research subagent (source-finder) lives globally in `~/.claude/agents/`.

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation.** Explicit rules for sentence structure, stance, analogies, punctuation, brevity. No em dashes. No AI-flavored academic phrasing.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Announcement required on every mode switch. Outlining is purely generative; refining owns integrity checking; sign-off gates prevent premature advancement.

## Prerequisites

- [Claude Code](https://claude.com/product/claude-code) installed. This project configures it; it does not replace it.
- `bash` available for running `install.sh`.
- `~/.claude/` writable (the installer creates it on first run).
- A directory for your paper. Any directory works: a fresh folder, a git repo you already have, or an existing project.

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

These paths are fixed; the install targets always go to `~/.claude/`, regardless of where the repo itself lives.

## Per-project setup

Each writing project gets its own `CLAUDE.md` (the academic-researcher definition, rendered with your name). Run `install.sh` from inside the project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh
```

This re-renders global files (cheap, idempotent) and drops `CLAUDE.md` into the project directory. With `--brief <name>` it also drops an empty `<name>.brief.md` rendered from the brief template:

```bash
/path/to/sourced/install.sh --brief my_paper
# → creates CLAUDE.md and my_paper.brief.md in the current directory
```

## Modes at a glance

Nine cognitive modes, one announced per transition. Full definitions live in `CLAUDE.md` section 7; this is the reference card.

| Mode | Purpose |
|------|---------|
| `[collaborative]` | Default. Think aloud with forward momentum. |
| `[red team]` | Systematically attack your own argument. |
| `[babble]` | Stream-of-consciousness, no structure. |
| `[research]` | Find and vet sources. Auto-triggered when any other mode hits an unsourced claim. |
| `[plan]` | Map sources to arguments before writing. Requires a brief. |
| `[outlining]` | Paragraph-level structure, citations attached by id, no prose. |
| `[refining]` | Stress-test the outline against the citation log. Runs the five-check audit. |
| `[writing]` | Outline to prose, applying voice rules and inline APA citations. |
| `[editing]` | Polish prose; re-audit citations against the log. |

## Typical workflow

The agent is announcement-driven: every mode transition outputs `Switching to [X].` before anything else (that line is your sanity check on what it thinks it's doing), and three stage gates (before refining, before writing, before research ends) stop and wait for your approval. Prefix a turn with `[non-academic]` to skip the framework for one turn; add "stay non-academic" to extend.

One end-to-end session, showing where modes announce and where the gates fire:

1. `install.sh --brief cheyenne_essay` renders `CLAUDE.md` and an empty `cheyenne_essay.brief.md`.
2. Open Claude Code. First turn is `[collaborative]` (no announcement on the first message). The agent proposes filling out the brief; you fill it.
3. You say "start planning." Agent announces `Switching to [plan mode].`, reads the brief, re-states the autonomy level, proposes a research strategy, and waits.
4. You approve. Agent auto-triggers `[research mode]`, dispatches `source-finder` subagents in parallel if three-plus sub-topics warrant it, runs the merge protocol, and returns with `Switching back to [plan mode].` plus a merged report of logged citations, gaps, and rejected sources.
5. Back in `[plan mode]`, the agent maps sources to arguments and presents the plan. **Gate:** you approve before advancing.
6. Agent switches to `[outlining mode]`, builds paragraph-level structure with citations attached by id. **Gate:** you approve ("ready to refine, or more outlining?").
7. `[refining mode]` runs the five-check audit (scope, attribution, inference, cherry-pick, synthesis) against the log. **Gate:** you approve the refined outline.
8. `[writing mode]` turns outline into prose, applying voice rules. Then `[editing mode]` polishes and re-audits.

At any point, `[red team]` and `[babble]` are available for stress-testing or unstructured thinking. `[non-academic]` escapes the framework for one turn.

## Updating

### Updating the sourced install

When you pull new changes to the `sourced` repo, re-render the global files:

```bash
cd /path/to/sourced
git pull
./install.sh --global-only
```

Then refresh each project (see below).

### Updating a project's CLAUDE.md

To refresh a project's CLAUDE.md in place without losing content you've added outside the managed block (project-specific notes, active briefs, TODO lists):

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --update
```

This replaces only the content between the `<!-- sourced:begin managed -->` and `<!-- sourced:end managed -->` sentinels. Everything outside the sentinels is preserved.

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

## File layout

Global files (installed once, shared across projects) and per-project files (rendered per-paper):

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

## License

None specified. Private repo for now.

## Migration from earlier versions

If you installed an earlier version of sourced that placed `academic-researcher.md` as a subagent at `~/.claude/agents/academic-researcher.md`, running the new `install.sh` will remove that file automatically. The agent content now lives in each project's `CLAUDE.md`.
