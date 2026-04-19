# Installation

[← Back to README](../README.md)

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
- `~/.claude/agents/voice-extractor.md`
- `~/.claude/citations/schema.md`
- `~/.claude/templates/brief.template.md`
- `~/.claude/voice/<name>.md` (voice library; shipped voices land here, custom voices can be added alongside)
- `~/.claude/style/<name>.md` (style library; same pattern)

These paths are fixed; the install targets always go to `~/.claude/`, regardless of where the repo itself lives.

## Per-project setup

Each writing project gets its own `CLAUDE.md` (the academic-researcher definition, rendered with your name), `voice.md`, and `style.md`. Run `install.sh` from inside the project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh
```

This re-renders global files (cheap, idempotent) and drops `CLAUDE.md`, `voice.md`, and `style.md` into the project directory. With `--brief <name>` it also drops an empty `<name>.brief.md`:

```bash
/path/to/sourced/install.sh --brief my_paper
# → creates CLAUDE.md, voice.md, style.md, and my_paper.brief.md in the current directory
```

## Updating

### Updating the sourced install

When you pull new changes to the `sourced` repo, re-render the global files:

```bash
cd /path/to/sourced
git pull
./install.sh --global-only
```

Then refresh each project (see below).

### Updating a project

To refresh a project's CLAUDE.md in place without losing content you've added outside the managed block (project-specific notes, active briefs, TODO lists):

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --update
```

`--update` does three things. First, it replaces only the content between the `<!-- sourced:begin managed -->` and `<!-- sourced:end managed -->` sentinels in CLAUDE.md; everything outside those sentinels is preserved. Second, it refreshes `voice.md` from the library voice the project was installed with (read from the marker on voice.md line 1). Third, it refreshes `style.md` from the library style the project was installed with. Upstream rule changes propagate via `--update`.

To switch to a different voice or style on an existing project, pass `--update --voice <new>` (explicit voice switch), `--update --style <new>` (explicit style switch), or `--force` (replace everything).

### Overwriting outright

If a CLAUDE.md exists but you want a fresh render regardless:

```bash
/path/to/sourced/install.sh --force
```

## Flags reference

| Flag | Effect |
|------|--------|
| `--global-only` | Install or refresh global files only (source-finder, voice-extractor, schema, brief template, voice library, style library). Skip per-project files. |
| `--project <path>` | Drop per-project files into `<path>` instead of `$PWD`. |
| `--force` | Overwrite existing CLAUDE.md, voice.md, style.md, and brief (if `--brief`) without asking. |
| `--update` | Refresh the managed block of CLAUDE.md (preserving content outside sentinels) and refresh `voice.md` and `style.md` from the project's installed voice and style. |
| `--voice <name>` | Pick the voice rendered into this project's `voice.md` (default: `academic`). Shipped voices live in `templates/voices/`; custom voices can be placed at `~/.claude/voice/<name>.md`. |
| `--style <name>` | Pick the citation/document style rendered into this project's `style.md` (default: `apa7`). Shipped styles live in `templates/styles/`; custom styles can be placed at `~/.claude/style/<name>.md`. |
| `--brief <name>` | Also drop `<name>.brief.md` into the project from `templates/brief.template.md`. |

## File layout

Global files (installed once, shared across projects) and per-project files (rendered per-paper):

| Path | Scope |
|------|-------|
| `~/.claude/agents/source-finder.md` | global subagent (parallel source research) |
| `~/.claude/agents/voice-extractor.md` | global subagent (one-shot voice calibration from samples) |
| `~/.claude/citations/schema.md` | global citation log schema |
| `~/.claude/templates/brief.template.md` | global brief template |
| `~/.claude/voice/<name>.md` | voice library (shipped + custom voices available for project selection) |
| `~/.claude/style/<name>.md` | style library (shipped + custom styles) |
| `<project>/CLAUDE.md` | per-project; contains the inlined academic-researcher rules |
| `<project>/voice.md` | per-project; the active voice for this project |
| `<project>/style.md` | per-project; the active citation style for this project |
| `<project>/<draft>.brief.md` | per-project, next to the draft |
| `<project>/<draft>.citations.json` | per-project, next to the draft |
| `<project>/<draft>.<target>.md` | formatted output written by `[formatting mode]` (e.g., `<draft>.gdocs.md`) |
| `<project>/.claude/citations/working.citations.json` | per-project, pre-draft |
| `<project>/.claude/citations/working.<finder-id>.json` | per-project, source-finder shards |

## Change your name

Edit or delete `~/.claude/sourced.config` and re-run `./install.sh --global-only`.

## Repo structure

```
sourced/
├── ARCHITECTURE.md              # surface-area map (read first)
├── README.md                    # landing page, quickstart
├── docs/
│   ├── INSTALL.md               # this file
│   ├── MODES.md
│   ├── VOICES.md
│   └── STYLES.md
├── install.sh                   # global + per-project install
├── agents/
│   ├── source-finder.md
│   └── voice-extractor.md
├── citations/
│   └── schema.md
└── templates/
    ├── CLAUDE.md
    ├── brief.template.md
    ├── styles/
    │   ├── chicago17-ad.md
    │   └── apa7.md
    └── voices/
        └── academic.md
```
