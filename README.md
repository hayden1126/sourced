# Sourced

Claude Code agents for rigorous academic research, drafting, and editing. A two-agent system that enforces source verification, prevents paraphrase drift, and preserves the writer's voice.

## What's in here

- **`academic-researcher`** — the primary orchestrator. Runs across nine modes (collaborative, red team, babble, research, plan, drafting, refining, writing, editing) with an explicit intake-brief step and autonomy-level controls before planning.
- **`source-finder`** — dispatched in parallel by academic-researcher for multi-topic research. Each finder verifies its own sources, writes to a shard file, and returns a structured report. Parent merges shards with ID collision resolution.
- **Citation log schema** — machine-readable record of every citation with `exact_quote`, `surrounding_context`, and `claim_supported` fields. Source of truth for the References section.

## What it does differently

- **No fabricated citations.** Sources must be peer-reviewed (or field-appropriate) AND full-text accessible. Abstract-only, paywalled, or content-mill sources are rejected, not approximated.
- **Synthesis integrity.** Paraphrases must match source scope. Attribution chains are preserved. Inference steps are marked, not hidden. Audit runs at refining stage (outline) and editing stage (prose).
- **Voice preservation.** Explicit rules for sentence structure, stance, analogies, punctuation, brevity. No em dashes. No AI-flavored academic phrasing.
- **Parallel research with integrity.** When three or more independent sub-topics need sources, source-finders dispatch in parallel. Each writes to its own shard; the parent merges with validation and collision resolution.
- **Mode discipline.** Announcement required on every mode switch. Drafting is purely generative; refining owns integrity checking; sign-off gates prevent premature advancement.

## Install

Clone wherever you keep repos. `install.sh` finds itself via `$BASH_SOURCE`, so the clone path doesn't matter.

```bash
git clone https://github.com/hayden1126/sourced.git
cd sourced
./install.sh
```

If you prefer a specific location, pass it to `git clone`:

```bash
git clone https://github.com/hayden1126/sourced.git ~/code/sourced
cd ~/code/sourced
./install.sh
```

On first run you'll be prompted for your name. It gets saved to `~/.claude/sourced.config` and substituted into the templates on every install.

After install, the agents are available to Claude Code from any working directory:

- `~/.claude/agents/academic-researcher.md`
- `~/.claude/agents/source-finder.md`
- `~/.claude/citations/schema.md`

These paths are fixed — the install targets always go to `~/.claude/`, regardless of where the repo itself lives.

## Update

From inside your cloned repo directory (wherever you put it):

```bash
git pull
./install.sh
```

The install script re-renders with your saved name. No re-prompt.

## Per-project files

The agents use two kinds of paths:

| Path | Scope | Lives at |
|------|-------|----------|
| `~/.claude/citations/schema.md` | global (same for every paper) | user-level |
| `~/.claude/agents/*.md` | global | user-level |
| `.claude/citations/working.citations.json` | project-local pre-draft | per-paper |
| `.claude/citations/working.<finder-id>.json` | project-local shards | per-paper |
| `<draft>.brief.md` | next to the draft | per-paper |
| `<draft>.citations.json` | next to the draft | per-paper |

Schema and agents install once per user. Citation logs, briefs, and shards live inside each paper's working directory.

## Change your name

Edit or delete `~/.claude/sourced.config` and re-run `./install.sh`.

## Structure

```
sourced/
├── agents/
│   ├── academic-researcher.md    # template with {{USER}}
│   └── source-finder.md          # template with {{USER}}
├── citations/
│   └── schema.md                 # template with {{USER}}
├── install.sh                    # render + install
└── README.md
```

## License

None specified. Private repo for now.
