# Modes

[← Back to README](../README.md)

Twelve cognitive modes, one announced per transition. The dispatch manifest (registry, triggers, gates, forcing artifacts, precedence) lives in the shipped [`CLAUDE.md`](../src/sourced/data/templates/CLAUDE.md) §7; full mode protocols are the shipped [`docs/modes/<name>.md`](../src/sourced/data/templates/docs/modes/) bodies, deployed into each project and read on mode entry. This page is the reference card plus a walkthrough of the typical workflow.

## Project types

Two project types select different mode graphs:

- **Essay** (default). All eleven essay modes are reachable. Created with `sourced new <name>` or `sourced new <name> --type essay`.
- **Annotated bibliography**. `[outlining]`, `[refining]`, `[writing]` are unreachable; `[annotated-bib]` replaces them. `[plan]`, `[research]`, and `[editing]` behave differently (facet decomposition, per-facet dispatch, reduced editing audit). Created with `sourced new <name> --type annotated-bib`. A marker file `.sourced-project-type` at project root records the type; absence = essay.

## Modes at a glance

| Mode | Purpose | Available in |
|------|---------|--------------|
| `[collaborative]` | Default. Think aloud with forward momentum. | all |
| `[red team]` | Systematically attack your own argument. | all |
| `[babble]` | Stream-of-consciousness, no structure. | all |
| `[research]` | Find and vet sources. Auto-triggers when any other mode hits an unsourced claim. Dispatches `source-finder` subagents in parallel for 3+ sub-topics. Dispatch template carries scope statement verbatim in annotated-bib projects. | all |
| `[plan]` | Map sources to arguments before writing (essay). Run topic specificity gate and facet decomposition (annotated-bib). Requires a brief (or explicit skip). | all |
| `[outlining]` | Paragraph-level structure, citations attached by id, no prose. Purely generative. | essay |
| `[refining]` | Stress-test the outline against the citation log. Runs the §4 audit (scope, attribution, inference, cherry-pick, synthesis) and integrity checks before prose exists. | essay |
| `[writing]` | Outline to prose. Applies voice rules (§9), generation signatures (§10), paraphrase default, Pandoc citation IDs. | essay |
| `[annotated-bib]` | Per-entry annotation (4-beat: summary / relevance / location / evaluation) and draft compile. Grounded only in log fields; §3 verification inherited. | annotated-bib |
| `[editing]` | Ten-pass audit on prose: revision → ID validation → §4 citation → partial-entry recheck → grammar → proofreading → AI-tell (§10) → cut-pattern → quote-density → voice (§9). In annotated-bib projects, pass 8 (quote-density) and the §9 flow-rules part of pass 9 are skipped. | all |
| `[finetuning]` | Bounded local substitution: produce 3–5 alternatives with declared tradeoff axes for a word-to-paragraph span; never ships a single-option change without explicit selection. {{USER}}-only, via explicit or implicit trigger. | all |
| `[formatting]` | Render prose into style-specific output for a named paste target. Terminal stage; source prose never modified. | all |

## Typical workflow

The agent is announcement-driven: every mode transition outputs `Switching to [X].` before anything else (that line is your sanity check on what it thinks it's doing), and four stage gates (before refining, before writing, before formatting, plus research round-trips) stop and wait for your approval. Prefix a turn with `[non-academic]` to skip the framework for one turn; add "stay non-academic" to extend.

One end-to-end session, showing where modes announce and where the gates fire:

1. `sourced new cheyenne_essay` renders `CLAUDE.md`, `config/voice.md`, `config/style.md`, and an empty `config/cheyenne_essay.brief.md`.
2. Open Claude Code. First turn is `[collaborative]` (no announcement on the first message). The agent proposes filling out the brief; you fill it.
3. You say "start planning." Agent announces `Switching to [plan mode].`, reads the brief, re-states the autonomy level, proposes a research strategy, and waits.
4. You approve. Agent auto-triggers `[research mode]`, dispatches `source-finder` subagents in parallel if three-plus sub-topics warrant it, runs the merge protocol, and returns with `Switching back to [plan mode].` plus a merged report of logged citations, gaps, and rejected sources.
5. Back in `[plan mode]`, the agent maps sources to arguments and presents the plan. **Gate:** you approve before advancing.
6. Agent switches to `[outlining mode]`, builds paragraph-level structure with citations attached by id. **Gate:** you approve ("ready to refine, or more outlining?").
7. `[refining mode]` runs the §4 audit (scope, attribution, inference, cherry-pick, synthesis) against the log. **Gate:** you approve the refined outline.
8. `[writing mode]` turns outline into prose, applying voice rules, §10 generation signatures, and the paraphrase default. The draft lands at `<draft>.md` with Pandoc citation IDs (`[@id]`, `@id`).
9. `[editing mode]` runs the ten-pass audit. The handoff gate blocks on any unresolved §10 voice-audit hits; you must "address or mark intentional" before format. Silence ≠ override.
10. `[formatting mode for <target>]` (e.g., `google-docs`, `plain-markdown`, `word`) renders `<draft>.md` into `<draft>.<target>.md`. Source prose is unchanged; the formatted sibling carries resolved `(Author Year, page)` citations and a References list per `config/style.md`. The `word` target (supported by all 5 shipped styles via pandoc+CSL) additionally runs pandoc + CSL and emits a `<draft>.docx` submission binary.
11. Optionally, before the draft goes out, you ask for a staged reader review: the `staged-reader-review` skill (see [SKILLS.md](./SKILLS.md)) runs blind persona readers over the rendered sibling section by section and writes `<draft>.reader-review.md`.

At any point, `[red team]` and `[babble]` are available for stress-testing or unstructured thinking. `[non-academic]` escapes the framework for one turn.

## Gate discipline

- **Plan → Outlining.** Agent presents the research plan; you approve or redirect.
- **Outlining → Refining.** Agent asks "ready to refine, or more outlining?"; silence ≠ approval.
- **Refining → Writing.** Agent presents the refined outline with citations attached; you approve.
- **Editing → Formatting.** Agent runs a final §10 surface scan; any hits surface as blockers ("address before format, or mark as intentional?"). Silence ≠ override.
- **Research round-trip.** When a mode auto-triggers research, the agent announces entry to `[research mode]`, runs, and announces return to the prior mode.

## The editing mode passes

`[editing mode]` runs a fixed-order pass sequence: citation mechanics first (ID validation, the §4 audit, partial-entry recheck), then language mechanics (grammar, proofreading), then cadence (AI-tells, quote density, voice). The order is load-bearing, and several passes emit forced lists the formatting handoff gate checks. The canonical pass definitions live in the shipped [`docs/modes/editing.md`](../src/sourced/data/templates/docs/modes/editing.md) body; do not rely on summaries of it, including this one.

See [VOICES.md](./VOICES.md) for what `[writing]` and `[editing]` mean by "voice rules," and [STYLES.md](./STYLES.md) for what `[formatting]` does with `config/style.md` and paste targets.
