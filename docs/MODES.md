# Modes

[← Back to README](../README.md)

Ten cognitive modes, one announced per transition. Full definitions live in [`templates/CLAUDE.md`](../templates/CLAUDE.md) §7; this page is the reference card plus a walkthrough of the typical workflow.

## Modes at a glance

| Mode | Purpose |
|------|---------|
| `[collaborative]` | Default. Think aloud with forward momentum. |
| `[red team]` | Systematically attack your own argument. |
| `[babble]` | Stream-of-consciousness, no structure. |
| `[research]` | Find and vet sources. Auto-triggers when any other mode hits an unsourced claim. Dispatches `source-finder` subagents in parallel for 3+ sub-topics. |
| `[plan]` | Map sources to arguments before writing. Requires an intake brief (or explicit skip). |
| `[outlining]` | Paragraph-level structure, citations attached by id, no prose. Purely generative. |
| `[refining]` | Stress-test the outline against the citation log. Runs the §4 audit (scope, attribution, inference, cherry-pick, synthesis) and integrity checks before prose exists. |
| `[writing]` | Outline to prose. Applies voice rules (§9), generation signatures (§10), paraphrase default, Pandoc citation IDs. |
| `[editing]` | Seven-pass audit on prose: ID validation → §4 citation → partial-entry recheck → grammar → AI-tell (§10) → quote-density → voice (§9). |
| `[formatting]` | Render prose into style-specific output for a named paste target. Terminal stage; source prose never modified. |

## Typical workflow

The agent is announcement-driven: every mode transition outputs `Switching to [X].` before anything else (that line is your sanity check on what it thinks it's doing), and four stage gates (before refining, before writing, before formatting, plus research round-trips) stop and wait for your approval. Prefix a turn with `[non-academic]` to skip the framework for one turn; add "stay non-academic" to extend.

One end-to-end session, showing where modes announce and where the gates fire:

1. `install.sh --brief cheyenne_essay` renders `CLAUDE.md`, `voice.md`, `style.md`, and an empty `cheyenne_essay.brief.md`.
2. Open Claude Code. First turn is `[collaborative]` (no announcement on the first message). The agent proposes filling out the brief; you fill it.
3. You say "start planning." Agent announces `Switching to [plan mode].`, reads the brief, re-states the autonomy level, proposes a research strategy, and waits.
4. You approve. Agent auto-triggers `[research mode]`, dispatches `source-finder` subagents in parallel if three-plus sub-topics warrant it, runs the merge protocol, and returns with `Switching back to [plan mode].` plus a merged report of logged citations, gaps, and rejected sources.
5. Back in `[plan mode]`, the agent maps sources to arguments and presents the plan. **Gate:** you approve before advancing.
6. Agent switches to `[outlining mode]`, builds paragraph-level structure with citations attached by id. **Gate:** you approve ("ready to refine, or more outlining?").
7. `[refining mode]` runs the §4 audit (scope, attribution, inference, cherry-pick, synthesis) against the log. **Gate:** you approve the refined outline.
8. `[writing mode]` turns outline into prose, applying voice rules, §10 generation signatures, and the paraphrase default. The draft lands at `<draft>.md` with Pandoc citation IDs (`[@id]`, `@id`).
9. `[editing mode]` runs the seven-pass audit. The handoff gate blocks on any unresolved §10 voice-audit hits; you must "address or mark intentional" before format. Silence ≠ override.
10. `[formatting mode for <target>]` (e.g., `google-docs`, `plain-markdown`, `word`) renders `<draft>.md` into `<draft>.<target>.md`. Source prose is unchanged; the formatted sibling carries resolved `(Author Year, page)` citations and a References list per `style.md`. The `word` target (supported by all 5 shipped styles via pandoc+CSL) additionally runs pandoc + CSL and emits a `<draft>.docx` submission binary.

At any point, `[red team]` and `[babble]` are available for stress-testing or unstructured thinking. `[non-academic]` escapes the framework for one turn.

## Gate discipline

- **Plan → Outlining.** Agent presents the research plan; you approve or redirect.
- **Outlining → Refining.** Agent asks "ready to refine, or more outlining?"; silence ≠ approval.
- **Refining → Writing.** Agent presents the refined outline with citations attached; you approve.
- **Editing → Formatting.** Agent runs a final §10 surface scan; any hits surface as blockers ("address before format, or mark as intentional?"). Silence ≠ override.
- **Research round-trip.** When a mode auto-triggers research, the agent announces entry to `[research mode]`, runs, and announces return to the prior mode.

## The editing mode seven passes

`[editing mode]` runs these in fixed order. Sequence is load-bearing: citation resolution precedes the audit that depends on IDs; mechanics precede cadence.

1. **ID validation.** Every `[@id]` resolves against the citation log; rendered author-year strings flagged as legacy regressions.
2. **§4 citation audit.** Scope, attribution, byline, inference, cherry-pick per claim; synthesis per multi-citation claim.
3. **Partial-entry recheck.** Citations with `verification_status: "partial"` re-checked against the pasted passage.
4. **Grammar pass.** Tense/mood consistency, attributing verbs before quotes, pronoun antecedents, restrictive/non-restrictive, dangling participles, parallel structure. Target is unambiguity, not rule compliance.
5. **AI-tell pass (§10).** Never-list patterns flagged on sight; density-list patterns checked against per-essay budgets. Restructure sentence shape, don't retokenize.
6. **Quote-density pass.** Direct-quote words over ~15% of a paragraph or two adjacent sentences both quoting → flag for paraphrase.
7. **Voice audit (§9).** Connectedness, paragraph flow, pacing, concept setup, exploratory vs verdict tone. Voice does not override grammar-pass unambiguity flags.

See [VOICES.md](./VOICES.md) for what `[writing]` and `[editing]` mean by "voice rules," and [STYLES.md](./STYLES.md) for what `[formatting]` does with `style.md` and paste targets.
