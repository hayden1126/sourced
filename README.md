# Sourced

A Claude Code setup for writing academic papers with the model in the loop. Built around three non-negotiables: every citation is verified and full-text accessible, every paraphrase matches source scope, and the writer's voice stays theirs instead of getting flattened into AI-flavored academic prose.

For students and researchers who want Claude-generated scholarship they can defend without rewriting it line by line.

The primary agent (academic-researcher) lives in each project's `CLAUDE.md`. Two subagents live globally in `~/.claude/agents/`: source-finder (parallel source research, dispatched during `[research mode]`) and voice-extractor (one-shot voice calibration from a corpus of writing samples).

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
- `~/.claude/agents/voice-extractor.md`
- `~/.claude/citations/schema.md`
- `~/.claude/templates/brief.template.md`
- `~/.claude/voice/<name>.md` (voice library; shipped voices land here, custom voices can be added alongside)

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

## Voices

Voice rules live in a per-project `voice.md` rendered from a named voice in the voice library. Voice is per-project, so concurrent Claude Code sessions on different projects can carry different voices without conflict.

The shipped `academic` voice is the author's own: personal register plus specific analogy anchors (Clever Hans, chicken sexing, split-brain) calibrated to one writer. Treat it as an example, not a neutral academic default. For a different author or a different register, copy it to a new name and edit.

Pick a voice at install:

```bash
/path/to/sourced/install.sh --voice academic   # default
/path/to/sourced/install.sh --voice mycustom   # requires ~/.claude/voice/mycustom.md
```

`--voice` is validated before any project file is written. An invalid name errors out cleanly with the list of available voices; no half-installed project.

Author a custom voice by copying the shipped one and editing:

```bash
cp ~/.claude/voice/academic.md ~/.claude/voice/mycustom.md
# edit ~/.claude/voice/mycustom.md
/path/to/sourced/install.sh --voice mycustom   # inside the target project directory
```

Library voice files are templates: any `{{USER}}` token is substituted with your configured name when `install.sh --voice` renders the voice into a project. That's why the shipped `academic.md` shows `{{USER}}` on line 3 — the token is replaced per-project, so each project's `voice.md` carries the right name without the library file having to store it.

### Generating a voice from writing samples

Hand-authoring a voice file is slow. If you have a corpus of the writer's prose (past papers, essays, reports, blog posts — whatever is representative), the `voice-extractor` subagent produces a calibrated first draft of the library file.

**Requirements.** At least 5 files and 5,000 words combined, in `.md` or `.txt`. Other file types (PDF, `.docx`, `.rtf`) are silently skipped and listed in the report. More samples produce more stable patterns; the 5-file / 5,000-word floor is a hard minimum, not a target. 15,000–30,000 words across 10+ files is where the output gets genuinely useful.

**Usage.** Open Claude Code in any project that already has a rendered `CLAUDE.md`. The agent reads `CLAUDE.md` §9 at startup and knows how to dispatch the subagent. Ask in natural language:

> *"Generate a new library voice called `mycustom` from the samples at `~/writing/papers/`. The register is academic."*

The agent will announce a switch to `[collaborative mode]` if needed, dispatch `voice-extractor` in a single Agent call, and present the report when the subagent returns. Name hygiene: pick a name matching `[a-z0-9_-]+` (lowercase letters, digits, underscore, hyphen — uppercase is rejected). The name `academic` is reserved because the shipped voice lives there; the subagent refuses with `shipped-name-collision` if you try it, regardless of the `overwrite` flag.

**What the subagent does:**

- Mirrors the section structure of a skeleton voice (default: the shipped `academic.md`).
- Fills each section from patterns found in the samples, with verbatim exemplars attributed to their source file in HTML comments.
- Leaves sections `TBD —` where the samples don't settle the question. Never fabricates rules or exemplars.
- Surfaces recurring named references as "anchor candidates" in the report. The Anchors block in the output file is always TBD by design; anchors are a judgment call only you can make.
- Classifies the corpus register if you don't pass one. Refuses with `register-mismatch` if the label you passed contradicts what the samples show, or `mixed-register` if no single register accounts for at least 70% of the corpus.

**After the subagent returns:**

1. Read the report — especially `### Sections filled` (low-confidence sections deserve a look), `### Sections left TBD`, `### Anchor candidates`, and `### Exemplar audit` (spot-check a few quotes against their source files).
2. Open `~/.claude/voice/<voice_name>.md` in an editor. Search for `TBD —` markers. Each one needs either a hand-written rule (drawing on the report's guidance) or deletion. At minimum, fill in the Anchors block from the `### Anchor candidates` list, or delete it if none fit.
3. Once no TBDs remain, render the voice into a project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --voice mycustom
```

**Re-running:**

- **Corpus was too thin.** Add samples, re-run with `overwrite: true`. Without `overwrite`, the subagent refuses to clobber an existing library file.
- **Register was inferred and came out wrong.** Re-run with the correct `register:` label (`academic | technical | casual | journalistic`).
- **Want a different skeleton.** Pass `skeleton_path: <absolute path>` pointing at another voice in `~/.claude/voice/`. Useful if a register-specific skeleton ships later.

**Scope.**

Voice-extractor is a one-shot setup utility. It runs only when you ask, never auto-triggers during writing or research, and never runs in parallel with itself. It does not modify your project's `CLAUDE.md`, `voice.md`, or anything under the project directory — it writes exactly one file, `~/.claude/voice/<voice_name>.md`. Rendering into a project is always a deliberate `install.sh --voice <voice_name>` step you run yourself.

Each project's `voice.md` records which library voice it was installed from (as an HTML comment on the first line). A later bare `install.sh --update` reuses that choice and refreshes `voice.md` from the current library version, so upstream voice-rule changes propagate. Switching to a different voice on an existing project requires `--force` (replace) or `--update --voice <new>` (explicit switch).

Shipped voices at `~/.claude/voice/<shipped-name>.md` are refreshed on every install from the repo. User-authored voices (names that don't collide with shipped ones) are left untouched. To customize a shipped voice without losing edits, copy to a new name first.

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

### Updating a project

To refresh a project's CLAUDE.md in place without losing content you've added outside the managed block (project-specific notes, active briefs, TODO lists):

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --update
```

`--update` does two things. First, it replaces only the content between the `<!-- sourced:begin managed -->` and `<!-- sourced:end managed -->` sentinels in CLAUDE.md; everything outside those sentinels is preserved. Second, it refreshes `voice.md` from the library voice the project was installed with (read from the marker on voice.md line 1), so upstream voice-rule changes propagate.

To switch to a different voice on an existing project, pass `--update --voice <new>` (explicit switch) or `--force --voice <new>` (replace).

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
| `<project>/CLAUDE.md` | per-project; contains the inlined academic-researcher rules |
| `<project>/voice.md` | per-project; the active voice for this project, rendered from the voice library |
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
│   ├── source-finder.md          # template with {{USER}}, installs to ~/.claude/agents/
│   └── voice-extractor.md        # template with {{USER}}, installs to ~/.claude/agents/
├── citations/
│   └── schema.md                 # template with {{USER}}, installs to ~/.claude/citations/
├── templates/
│   ├── CLAUDE.md                 # template with {{USER}}, rendered into each project
│   ├── brief.template.md         # template with {{USER}}, installs globally and rendered per-project on --brief
│   └── voices/
│       └── academic.md           # shipped voice; copies verbatim to ~/.claude/voice/academic.md, renders per-project via install.sh --voice
├── install.sh                    # global + per-project install
└── README.md
```

## License

None specified. Private repo for now.

## Migration from earlier versions

If you installed an earlier version of sourced that placed `academic-researcher.md` as a subagent at `~/.claude/agents/academic-researcher.md`, running the new `install.sh` will remove that file automatically. The agent content now lives in each project's `CLAUDE.md`.
