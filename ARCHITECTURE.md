# Architecture at a glance

Orientation for someone reading the repo. Read `README.md` for installation; read `src/sourced/data/templates/CLAUDE.md` for the agent's full operating rules. The Python CLI that orchestrates installation lives at `src/sourced/`. This file sketches the surface area and how the pieces connect.

Design history lives in `docs/archive/{specs,plans}/`, each file carrying a `Status: Shipped <date> (PR #N)` banner. In-flight specs and plans, when they exist, live at `docs/specs/` and `docs/plans/` (created on demand) and move to the archive with a banner when the work lands.

## File layout

```
sourced/
├── pyproject.toml              # Python package metadata; entry point sourced=sourced.cli:main.
├── README.md                   # User-facing install + quickstart.
├── ARCHITECTURE.md             # This file.
├── ROADMAP.md                  # Forward-looking ideas + scope boundaries.
├── docs/                       # Topic guides (INSTALL, MODES, VOICES, STYLES, SKILLS).
├── src/
│   └── sourced/
│       ├── cli.py              # argparse root + dispatch + error→exit-code mapping.
│       ├── __main__.py         # python -m sourced entry point.
│       ├── commands/           # One file per subcommand: install, global_install, new, update, switch, check + _pipeline.
│       ├── validators/         # Stateless: csl (pre-render), iron_rules + exemptions (post-render). Return list[Finding], never raise.
│       ├── render.py           # Pure {{USER}} substitution + bundled-data Path resolution via importlib.resources.
│       ├── project.py          # Per-project sentinels, markers, .sourced.bak rollback.
│       ├── mirror.py           # shutil.copytree wrapper for ~/.claude/ population.
│       ├── config.py           # ~/.claude/sourced.config (SOURCED_USER) read/write, shell-env-format-compatible.
│       ├── context.py          # Runtime state (dry_run, verbose, quiet, color, strict).
│       ├── errors.py           # SourcedError hierarchy + exit-code mapping.
│       ├── ui.py               # Color/print helpers; should_color tty-gates auto.
│       └── data/               # Bundled, read-only at runtime; mirrored to ~/.claude/ by global-install.
│           ├── agents/         # Subagent definitions: source-finder, voice-extractor, sourced-helper, prose-drafter.
│           ├── citations/      # Citation log schema + CSL-JSON emitter spec.
│           ├── skills/         # Skill library (e.g. browser-reader-extract).
│           ├── filters/        # Pandoc Lua filters (promoted from templates/filters in PR 3).
│           └── templates/
│               ├── CLAUDE.md   # Primary agent operating instructions.
│               ├── brief.template.md, brief.template.annotated-bib.md
│               ├── styles/     # 5 shipped slim styles + per-style asset dirs (CSL, template.tex, …).
│               └── voices/     # 6 shipped voice skeletons (academic, casual, hybrid, journalistic, narrative, technical).
└── tests/
    ├── cli/                    # Python CLI tests:
    │   ├── unit/               # Per-module unit tests (167 tests).
    │   ├── integration/        # Subprocess-driven end-to-end tests (58 tests).
    │   └── golden/             # syrupy snapshots for 14 shipped templates.
    ├── emitter/                # CSL-JSON emitter reference fixtures + well-formedness tests.
    └── parity/                 # 5 styles × 4 paste targets = 20 goldens (the long-lived render parity suite).
```

`sourced global-install` mirrors bundled data from `src/sourced/data/` into `~/.claude/`. `sourced install` from inside a project renders `<project>/CLAUDE.md`, `<project>/config/voice.md`, `<project>/config/style.md` (and optionally `<project>/config/<name>.brief.md`). `sourced check` verifies prereqs (`pdftotext`, `pdfinfo`, `pdftoppm`, `pandoc` ≥ 3.1, `python3`) plus `~/.claude/` health plus per-voice iron-rule integrity; missing tools surface with install hints rather than auto-installing (see [docs/INSTALL.md](./docs/INSTALL.md#prerequisite-check)).

Shipped skills under `src/sourced/data/skills/<name>/` mirror into `~/.claude/skills/<name>/` on every install; Claude Code auto-discovers them across all projects. Style asset directories under `src/sourced/data/templates/styles/<name>/` mirror into `~/.claude/style/<name>/` so `[formatting mode]` can pick up CSL files, reference.docx, on-demand reference tables (e.g., `classical-abbreviations.md`), and other per-style binaries without a separate fetch. The on-demand reference pattern lets a style offload rarely-used lookups (per-author classical abbreviations) without paying per-format-pass load cost; `config/style.md` stays lean and the reference file is Read only when a citation triggers it.

## Python package

Phase 1 ports the framework's installer from the legacy bash script to a Python CLI under `src/sourced/`. The package follows a strict module-boundary discipline (per design spec §3):

- `cli.py` is the only module that touches argparse. Subcommand modules accept plain Python args.
- `commands/` modules orchestrate; they delegate I/O to the shared pipeline (`commands/_pipeline.py`).
- `validators/` modules are pure: each takes input, returns `list[Finding]`, and never raises. The pipeline gathers findings and decides whether to halt (errors always halt; warnings halt only under `--strict`).
- `ui.py` owns all user-facing presentation (color, print formatting, error display). Other modules return data; `ui.py` renders it.
- `data/` is read-only at runtime; `bundled_path()` and `read_template()` in `render.py` resolve it via `importlib.resources` so editable installs hot-reload edits.

Three error layers (`errors.py`):
- `UsageError` (exit 2) — argparse-style misuse; never reaches the user from inside a command.
- `ValidationError` (exit 4) — a validator surfaced an error, or `--strict` promoted a warning.
- `ProjectError` (exit 5) — project-state preconditions broken (missing dir, malformed sentinels, corrupted marker).

Pipeline shape (per spec §5.3):
1. `config.load_user_name()` — read or prompt.
2. `read_template(subpath)` — read bundled.
3. PRE-render validators (style CSL title, …).
4. `render(template, ctx)` — `{{USER}}` substitution.
5. POST-render validators (iron rules, exemptions).
6. `_maybe_raise(findings, ctx)` — halt on errors / strict warnings.
7. Dry-run guard, then `write_atomic` (tempfile + rename) or `mirror_tree`.

Reference design: [`docs/archive/specs/2026-04-21-sourced-cli-decomposition-design.md`](./docs/archive/specs/2026-04-21-sourced-cli-decomposition-design.md).

## The primary agent

`academic-researcher`, defined in `src/sourced/data/templates/CLAUDE.md`. One agent per project. Operates in exactly one mode at a time. Mode switches are announced. Gates between stages require explicit user approval.

## Modes

| Mode | Purpose | Gates into |
|------|---------|------------|
| `[collaborative mode]` | Default. Exploratory riffing, sparring, thinking aloud. | Any mode. |
| `[plan mode]` | Formulate research question, argument, source needs. Requires intake brief or explicit skip. | `[outlining mode]` |
| `[outlining mode]` | Paragraph-level structure with claims + citation IDs. Purely generative, no audits. | `[refining mode]` (handoff gate) |
| `[refining mode]` | Stress-test the outline. Citation / structure / synthesis-integrity (§4) audit before prose exists. | `[writing mode]` (sign-off gate) |
| `[writing mode]` | Convert refined outline into prose. Apply `config/voice.md`, §10 generation signatures, paraphrase default, Pandoc citation IDs. | `[editing mode]` |
| `[annotated-bib mode]` | Per-entry annotation (4-beat: summary / relevance / location / evaluation) and draft compile. Grounded only in log fields; §3 verification inherited. Annotated-bib projects only; replaces `[outlining]` / `[refining]` / `[writing]`. | `[editing mode]` |
| `[editing mode]` | Eight-pass audit: ID validation → §4 citation → partial-entry recheck → grammar → proofreading → AI-tell (§10) → quote-density → voice (§9). Handoff gate blocks on unresolved voice-audit hits. In annotated-bib projects, pass 7 (quote-density) and the §9 flow-rules part of pass 8 are skipped. | `[formatting mode]` (handoff gate) |
| `[finetuning mode]` | Bounded local substitution (word to paragraph): produce 3–5 alternatives with declared tradeoff axes; never applies a single-option change without explicit {{USER}} selection. {{USER}}-only entry via explicit or implicit trigger. | Returns to prior mode on completion. |
| `[formatting mode]` | Render source prose into style-specific output for a named paste target (`word`, `google-docs`, `plain-markdown`, `latex` — all rendered via pandoc+CSL). Terminal stage; source prose never modified. | Done. |
| `[research mode]` | Source vetting and logging. Auto-triggers from other modes when a claim needs a source. Dispatches `source-finder` subagents in parallel for 3+ sub-topics. | Returns to prior mode on completion. |
| `[red team mode]` | Systematically challenge every claim. Counterpoints, blind spots. | Any mode. |
| `[babble mode]` | Stream-of-consciousness. No structure. Raw material for collaboration. | Any mode. |

## Subagents

| Subagent | Dispatched by | Purpose | Parallel? |
|----------|---------------|---------|-----------|
| `source-finder` | academic-researcher during `[research mode]` | Vet and log sources for one sub-topic; return a structured report (`### Logged / ### Rejected / ### Gaps / ### Alternative framings`). | Yes — 3+ per dispatch batch. Each writes to its own shard; parent merges with ID-collision resolution. |
| `voice-extractor` | academic-researcher (from `[collaborative mode]` only, on explicit user request) | Read a writing-samples corpus, mirror the skeleton voice file's section structure, emit a per-author voice library file at `~/.claude/voice/<name>.md`. Iron rules preserved verbatim. | No. One-shot utility. |

## Per-project files

- `<project>/CLAUDE.md` — agent operating rules (rendered from `src/sourced/data/templates/CLAUDE.md`).
- `<project>/config/voice.md` — voice rules (rendered from `~/.claude/voice/<name>.md`).
- `<project>/config/style.md` — citation + document-layout rules (rendered from `~/.claude/style/<name>.md`).
- `<project>/config/<name>.brief.md` — intake brief for a specific paper (optional; `sourced install --brief <name>` or `sourced new <name>`).
- `<project>/<draft>.md` — source prose with Pandoc citation IDs.
- `<project>/sources/<draft>.citations.json` — citation log for the draft (schema: `citations/schema.md`).
- `<project>/<draft>.<target>.md` — formatted output written by `[formatting mode]` (e.g., `<draft>.gdocs.md`).
- `<project>/.sourced-project-type` — project-type marker written by `sourced install` when `--type` is non-default (currently only `annotated-bib`); contains the type name on a single line. Absence means essay (legacy-safe default).

## Citation handling: three moments

Each moment is owned by exactly one mode family.

1. **Logging** (`[research mode]`) — verify source, append JSON entry to the citation log. Every entry carries:
   - Core source fields: `source.authors`, `source.year`, `exact_quote`, `surrounding_context`, `retrieved_at`, `verification_status`.
   - Externalized verification sub-fields under `retrieval`: `retrieval.printed_page_observed`, `retrieval.tool_page_index`, `retrieval.pdf_page_offset`, `retrieval.verification_trace`, and `retrieval.per_entity_locators` (required when `exact_quote` enumerates multiple named entities). See [`citations/schema.md`](./citations/schema.md) §Verification fields for when each is required.
2. **In-prose IDs** (`[outlining mode]`, `[writing mode]`, `[editing mode]`) — prose carries `[@id]` / `@id` / `[@id, p. N]` Pandoc syntax. Never rendered author-year strings.
3. **Rendering** (`[formatting mode]`) — resolve IDs against the log, emit style-specific inline citations and a References list into a sibling file.

The log is the single source of truth for author names and years; rendering is decoupled from authoring.

## Citation rendering pipeline

Step 3 above (rendering) delegates to `pandoc --citeproc` reading the style's vendored CSL file under `src/sourced/data/templates/styles/<name>/`. `[formatting mode]` emits the citation log as CSL-JSON per the mapping in [`citations/csl-json-emitter.md`](./citations/csl-json-emitter.md), hands pandoc the source prose plus CSL-JSON plus CSL, and receives rendered inline citations and a References list. The same pipeline serves all four paste targets (`word`, `google-docs`, `plain-markdown`, `latex`); paste-target differences are output format (`.docx` / markdown / `.tex`) plus per-target post-pandoc transforms and per-target asset binding (reference.docx for word, template.tex for latex). See [`docs/STYLES.md`](./docs/STYLES.md) for the end-to-end description.

## Voice system: three layers

1. **Skeletons** (`src/sourced/data/templates/voices/{academic,casual,technical,journalistic,narrative,hybrid}.md`) — section structure + `## Iron rules` section. Each is a register-specific (or, for `hybrid.md`, register-neutral) calibration template. Copied verbatim into the voice library on global install.
2. **Voice library** (`~/.claude/voice/<name>.md`) — per-author calibrated voice files. The 6 shipped voices (`academic`, `casual`, `technical`, `journalistic`, `narrative`, `hybrid`) ARE the skeletons; derived voices are generated by `voice-extractor` from a writing-samples corpus and mirror the matching skeleton's section structure (selected by register classification — see `docs/VOICES.md`).
3. **Project voice** (`<project>/config/voice.md`) — rendered from the chosen library voice on `sourced install --voice <name>` or `sourced switch voice <name>`, with `{{USER}}` substituted.

**Skeleton-per-register (6 skeletons).** As of 2026-04-19, the voice library ships 6 register-specific skeletons (`academic`, `casual`, `technical`, `journalistic`, `narrative`, `hybrid`) instead of a single `academic.md`. Voice-extractor selects the skeleton based on corpus classification: a dominant-register corpus (≥ 85%) uses that register's skeleton; a blended corpus (< 85%) uses `hybrid.md`, which is authored with register-neutral non-iron prose and explicit anti-bias instructions. Each skeleton organizes rules under 4 orthogonal axes — `## Iron rules`, `## Tone`, `## Structure`, `## Dimension` — so a voice can be calibrated along each axis independently. See `docs/VOICES.md` for the full register map and routing logic.

**Iron rules** (content under `## Iron rules` / `## AI-tells` / `## Generation signatures` section headings in a voice skeleton, plus any line containing the `[iron]` token) pass through verbatim at every layer. `voice-extractor` refuses to downgrade iron rules to TBD; the sourced CLI refuses to install a voice file where any iron rule is missing.

Generation signatures (AI-writing tells that apply regardless of voice) live in CLAUDE.md §10, not in individual voice files. Each bullet on §10's Never list carries a stable `[id: <name>]` marker. A voice library file may exempt a specific rule by listing the matching ID under its `## §10 exemptions` section; the sourced CLI validates the section against the ID set extracted live from `src/sourced/data/templates/CLAUDE.md` and aborts on any unknown ID. Silence is not permission: a voice file that omits the section or leaves the bullet list empty inherits §10 in full.

## Style system

`src/sourced/data/templates/styles/<name>.md` ships citation + layout rules per academic style. Currently shipped: APA 7, Chicago 17 author-date, Chicago 17 notes-bibliography, IEEE, MLA 9 — all on the slim schema (framework-specific metadata + document layout only; CSL owns rendering). `[formatting mode]` is the only mode that reads `config/style.md`; all other modes emit style-agnostic Pandoc IDs.

## Invariants

- **Source prose is never modified by `[formatting mode]`.** Formatted output is always a sibling file.
- **No fabricated citations.** If full text isn't accessible, the source is rejected, not approximated.
- **Every paraphrase matches source scope.** §4 audit runs at refining (outline-level) and editing (prose-level).
- **No em dashes in generated prose.** Iron, per CLAUDE.md §10.
- **Mode switches are announced.** Every mode transition emits a one-line marker before any other output.
- **Gates are not bypassable by silence.** Advancing `[outlining] → [refining] → [writing] → [editing] → [formatting]` requires explicit user approval; silence is not an override.

## Extension points

- **New voice from scratch.** Copy any of the 6 shipped skeletons (e.g., `src/sourced/data/templates/voices/academic.md` for an academic-register voice; `src/sourced/data/templates/voices/casual.md` for casual; `src/sourced/data/templates/voices/hybrid.md` for register-neutral) → `~/.claude/voice/<name>.md`, edit per-section rules, preserve the `## Iron rules` section verbatim, then `sourced install --voice <name>` or `sourced switch voice <name>` from a project.
- **New voice from corpus.** Ask the agent to generate a voice from a writing-samples directory; it dispatches `voice-extractor` in `[collaborative mode]` and surfaces the report. Fill in `TBD` sections by hand, then `sourced install --voice <name>` or `sourced switch voice <name>`.
- **New style.** Copy any of the five shipped slim styles (`apa7.md`, `chicago17-ad.md`, `chicago17-nb.md`, `ieee.md`, `mla9.md`) as a starting template, vendor the matching CSL file under `src/sourced/data/templates/styles/<name>/`, edit per-style metadata + document layout, then `sourced install --style <name>` or `sourced switch style <name>`.
- **New mode.** Add a `### [mode name]` subsection to `src/sourced/data/templates/CLAUDE.md` §7 (entry rules, workflow, handoff). Register it in the mode-switching table. Any auto-trigger rules need explicit announce-on-entry and announce-on-return semantics.
- **New subagent.** Add `src/sourced/data/agents/<name>.md` with frontmatter (`name`, `description`, `tools`, `model`) plus a dispatch template. Reference it from the relevant mode section in CLAUDE.md.

## Defense-in-depth for iron rules

Iron rules (voice-skeleton rules that must pass through derived voices unchanged) are checked in three places:

1. **Inside `voice-extractor`** — step 3 identifies iron rules from the skeleton; step 5 branch preserves them verbatim; step 8 self-check before writing.
2. **Caller-side in `academic-researcher`** — after `voice-extractor` returns, CLAUDE.md §9 instructs the caller to substring-check each iron rule against the produced file before surfacing the report.
3. **Install-time in the sourced CLI** — `iron_rules` validator in `commands/_pipeline.render_voice` + `commands/check.check_voice_iron_rules` normalizes both skeleton and candidate, substring-matches, and aborts install on any missing rule.

One layer failing doesn't ship a broken voice. All three would have to miss.
