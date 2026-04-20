# Architecture at a glance

Orientation for someone reading the repo. Read `README.md` for installation; read `templates/CLAUDE.md` for the agent's full operating rules. This file sketches the surface area and how the pieces connect.

## File layout

```
sourced/
├── install.sh                  # Renders templates into ~/.claude and the active project.
├── README.md                   # User-facing install and usage.
├── ARCHITECTURE.md             # This file.
├── agents/
│   ├── source-finder.md        # Subagent: vet sources in parallel for §3-integrity citations.
│   └── voice-extractor.md      # Subagent: derive a voice file from a writing-samples corpus.
├── citations/
│   ├── schema.md               # Citation log entry structure, staleness rules, ID format.
│   └── csl-json-emitter.md     # Log → CSL-JSON mapping consumed by pandoc --citeproc.
├── skills/
│   └── browser-reader-extract/ # Skill: extract text + [p. N] markers from DRM'd browser readers.
├── tests/
│   ├── emitter/                # CSL-JSON emitter fixtures + unit tests.
│   └── parity/                 # Golden outputs: 5 styles × 3 paste targets = 15 goldens.
└── templates/
    ├── CLAUDE.md               # Primary agent (academic-researcher) operating instructions.
    ├── brief.template.md       # Per-paper intake brief skeleton.
    ├── styles/
    │   ├── apa7.md             # APA 7 (author-date) — slim style.
    │   ├── apa7/               # Vendored apa.csl + per-style assets.
    │   ├── chicago17-ad.md     # Chicago 17 author-date — slim style.
    │   ├── chicago17-ad/       # Vendored CSL + per-style assets.
    │   ├── chicago17-nb.md     # Chicago 17 notes-bibliography — slim style.
    │   ├── chicago17-nb/       # Vendored CSL + per-style assets.
    │   ├── ieee.md             # IEEE (numeric) — slim style.
    │   ├── ieee/                # Vendored CSL + per-style assets.
    │   ├── mla9.md             # MLA 9 (author-page) — slim style.
    │   └── mla9/               # Vendored CSL + per-style assets.
    └── voices/
        └── academic.md         # Voice skeleton; derived voices mirror this structure.
```

`install.sh --global-only` renders into `~/.claude/`. `install.sh` from inside a project renders `<project>/CLAUDE.md`, `<project>/voice.md`, `<project>/style.md`. A prerequisite check (`pdftotext`, `pandoc` ≥ 3.1, `python3`) runs at the top of every invocation; missing tools abort the install with apt/brew hints rather than auto-installing (see [docs/INSTALL.md](./docs/INSTALL.md#prerequisite-check)).

Shipped skills under `skills/<name>/` mirror into `~/.claude/skills/<name>/` on every install; Claude Code auto-discovers them across all projects. Style asset directories under `templates/styles/<name>/` mirror into `~/.claude/style/<name>/` so `[formatting mode]` can pick up CSL files, reference.docx, on-demand reference tables (e.g., `classical-abbreviations.md`), and other per-style binaries without a separate fetch. The on-demand reference pattern lets a style offload rarely-used lookups (per-author classical abbreviations) without paying per-format-pass load cost; `style.md` stays lean and the reference file is Read only when a citation triggers it.

## The primary agent

`academic-researcher`, defined in `templates/CLAUDE.md`. One agent per project. Operates in exactly one mode at a time. Mode switches are announced. Gates between stages require explicit user approval.

## Modes

| Mode | Purpose | Gates into |
|------|---------|------------|
| `[collaborative mode]` | Default. Exploratory riffing, sparring, thinking aloud. | Any mode. |
| `[plan mode]` | Formulate research question, argument, source needs. Requires intake brief or explicit skip. | `[outlining mode]` |
| `[outlining mode]` | Paragraph-level structure with claims + citation IDs. Purely generative, no audits. | `[refining mode]` (handoff gate) |
| `[refining mode]` | Stress-test the outline. Citation / structure / synthesis-integrity (§4) audit before prose exists. | `[writing mode]` (sign-off gate) |
| `[writing mode]` | Convert refined outline into prose. Apply `voice.md`, §10 generation signatures, paraphrase default, Pandoc citation IDs. | `[editing mode]` |
| `[editing mode]` | Seven-pass audit: ID validation → §4 citation → partial-entry recheck → grammar → AI-tell (§10) → quote-density → voice (§9). Handoff gate blocks on unresolved voice-audit hits. | `[formatting mode]` (handoff gate) |
| `[formatting mode]` | Render source prose into style-specific output for a named paste target (`word`, `google-docs`, `plain-markdown` — all rendered via pandoc+CSL). Terminal stage; source prose never modified. | Done. |
| `[research mode]` | Source vetting and logging. Auto-triggers from other modes when a claim needs a source. Dispatches `source-finder` subagents in parallel for 3+ sub-topics. | Returns to prior mode on completion. |
| `[red team mode]` | Systematically challenge every claim. Counterpoints, blind spots. | Any mode. |
| `[babble mode]` | Stream-of-consciousness. No structure. Raw material for collaboration. | Any mode. |

## Subagents

| Subagent | Dispatched by | Purpose | Parallel? |
|----------|---------------|---------|-----------|
| `source-finder` | academic-researcher during `[research mode]` | Vet and log sources for one sub-topic; return a structured report (`### Logged / ### Rejected / ### Gaps / ### Alternative framings`). | Yes — 3+ per dispatch batch. Each writes to its own shard; parent merges with ID-collision resolution. |
| `voice-extractor` | academic-researcher (from `[collaborative mode]` only, on explicit user request) | Read a writing-samples corpus, mirror the skeleton voice file's section structure, emit a per-author voice library file at `~/.claude/voice/<name>.md`. Iron rules preserved verbatim. | No. One-shot utility. |

## Per-project files

- `<project>/CLAUDE.md` — agent operating rules (rendered from `templates/CLAUDE.md`).
- `<project>/voice.md` — voice rules (rendered from `~/.claude/voice/<name>.md`).
- `<project>/style.md` — citation + document-layout rules (rendered from `~/.claude/style/<name>.md`).
- `<project>/<name>.brief.md` — intake brief for a specific paper (optional; `install.sh --brief <name>`).
- `<project>/<draft>.md` — source prose with Pandoc citation IDs.
- `<project>/<draft>.citations.json` — citation log for the draft (schema: `citations/schema.md`).
- `<project>/<draft>.<target>.md` — formatted output written by `[formatting mode]` (e.g., `<draft>.gdocs.md`).

## Citation handling: three moments

Each moment is owned by exactly one mode family.

1. **Logging** (`[research mode]`) — verify source, append JSON entry to the citation log. Every entry carries `source.authors`, `source.year`, `exact_quote`, `surrounding_context`, `retrieved_at`, `verification_status`.
2. **In-prose IDs** (`[outlining mode]`, `[writing mode]`, `[editing mode]`) — prose carries `[@id]` / `@id` / `[@id, p. N]` Pandoc syntax. Never rendered author-year strings.
3. **Rendering** (`[formatting mode]`) — resolve IDs against the log, emit style-specific inline citations and a References list into a sibling file.

The log is the single source of truth for author names and years; rendering is decoupled from authoring.

## Citation rendering pipeline

Step 3 above (rendering) delegates to `pandoc --citeproc` reading the style's vendored CSL file under `templates/styles/<name>/`. `[formatting mode]` emits the citation log as CSL-JSON per the mapping in [`citations/csl-json-emitter.md`](./citations/csl-json-emitter.md), hands pandoc the source prose plus CSL-JSON plus CSL, and receives rendered inline citations and a References list. The same pipeline serves all three paste targets (`word`, `google-docs`, `plain-markdown`); paste-target differences are post-pandoc transforms. See [`docs/STYLES.md`](./docs/STYLES.md) for the end-to-end description.

## Voice system: three layers

1. **Skeleton** (`templates/voices/academic.md`) — section structure + `## Iron rules` section. Copied verbatim into the voice library on global install.
2. **Voice library** (`~/.claude/voice/<name>.md`) — per-author calibrated voice files. The shipped `academic` voice is the skeleton itself; derived voices are generated by `voice-extractor` from a writing-samples corpus and mirror the skeleton's section structure.
3. **Project voice** (`<project>/voice.md`) — rendered from the chosen library voice on `install.sh --voice <name>`, with `{{USER}}` substituted.

**Iron rules** (content under `## Iron rules` / `## AI-tells` / `## Generation signatures` section headings in a voice skeleton, plus any line containing the `[iron]` token) pass through verbatim at every layer. `voice-extractor` refuses to downgrade iron rules to TBD; `install.sh` refuses to install a voice file where any iron rule is missing.

Generation signatures (AI-writing tells that apply regardless of voice) live in CLAUDE.md §10, not in individual voice files. Each bullet on §10's Never list carries a stable `[id: <name>]` marker. A voice library file may exempt a specific rule by listing the matching ID under its `## §10 exemptions` section; `install.sh` validates the section against the ID set extracted live from `templates/CLAUDE.md` and aborts on any unknown ID. Silence is not permission: a voice file that omits the section or leaves the bullet list empty inherits §10 in full.

## Style system

`templates/styles/<name>.md` ships citation + layout rules per academic style. Currently shipped: APA 7, Chicago 17 author-date, Chicago 17 notes-bibliography, IEEE, MLA 9 — all on the slim schema (framework-specific metadata + document layout only; CSL owns rendering). `[formatting mode]` is the only mode that reads `style.md`; all other modes emit style-agnostic Pandoc IDs.

## Invariants

- **Source prose is never modified by `[formatting mode]`.** Formatted output is always a sibling file.
- **No fabricated citations.** If full text isn't accessible, the source is rejected, not approximated.
- **Every paraphrase matches source scope.** §4 audit runs at refining (outline-level) and editing (prose-level).
- **No em dashes in generated prose.** Iron, per CLAUDE.md §10.
- **Mode switches are announced.** Every mode transition emits a one-line marker before any other output.
- **Gates are not bypassable by silence.** Advancing `[outlining] → [refining] → [writing] → [editing] → [formatting]` requires explicit user approval; silence is not an override.

## Extension points

- **New voice from scratch.** Copy `templates/voices/academic.md` → `~/.claude/voice/<name>.md`, edit per-section rules, preserve the `## Iron rules` section verbatim, then `install.sh --voice <name>` from a project.
- **New voice from corpus.** Ask the agent to generate a voice from a writing-samples directory; it dispatches `voice-extractor` in `[collaborative mode]` and surfaces the report. Fill in `TBD` sections by hand, then `install.sh --voice <name>`.
- **New style.** Copy any of the five shipped slim styles (`apa7.md`, `chicago17-ad.md`, `chicago17-nb.md`, `ieee.md`, `mla9.md`) as a starting template, vendor the matching CSL file under `templates/styles/<name>/`, edit per-style metadata + document layout, then `install.sh --style <name>`.
- **New mode.** Add a `### [mode name]` subsection to `templates/CLAUDE.md` §7 (entry rules, workflow, handoff). Register it in the mode-switching table. Any auto-trigger rules need explicit announce-on-entry and announce-on-return semantics.
- **New subagent.** Add `agents/<name>.md` with frontmatter (`name`, `description`, `tools`, `model`) plus a dispatch template. Reference it from the relevant mode section in CLAUDE.md.

## Defense-in-depth for iron rules

Iron rules (voice-skeleton rules that must pass through derived voices unchanged) are checked in three places:

1. **Inside `voice-extractor`** — step 3 identifies iron rules from the skeleton; step 5 branch preserves them verbatim; step 8 self-check before writing.
2. **Caller-side in `academic-researcher`** — after `voice-extractor` returns, CLAUDE.md §9 instructs the caller to substring-check each iron rule against the produced file before surfacing the report.
3. **Install-time in `install.sh`** — `validate_iron_rules` in `render_voice` normalizes both skeleton and candidate, substring-matches, and aborts install on any missing rule.

One layer failing doesn't ship a broken voice. All three would have to miss.
