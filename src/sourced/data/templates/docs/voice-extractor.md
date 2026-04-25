# Voice-extractor dispatch

**When to read this file.** Before dispatching the `voice-extractor` subagent via the Agent tool. Referenced from `CLAUDE.md §9`. Voice-extractor is **not a mode** and does **not** auto-trigger. It runs only in `[collaborative mode]` and always in a single dispatch (never in parallel; this is unlike `source-finder`). If {{USER}} asks from another mode, announce the switch to `[collaborative mode]` first (`Switching to [collaborative mode].`), dispatch the subagent, present its report, and stay in collaborative until {{USER}} directs otherwise. Voice calibration is a setup operation, not part of the research/write/edit pipeline, so returning to the prior mode after the dispatch would mislead {{USER}} about where the conversation is.

## Dispatch procedure

Read the subagent definition at `~/.claude/agents/voice-extractor.md` if you have not already. Then dispatch via the Agent tool with the template below as the `prompt` argument. Fill every placeholder. If an optional field is not applicable, write `omit` rather than removing the line; the subagent parses the structure.

```
samples_dir: <absolute path to a directory containing the writing samples, or "omit" to default to <project>/samples/>
voice_name: <name for the new library voice; must match [a-z0-9_-]+>
register: <academic | technical | casual | journalistic | narrative, or "omit" to let the subagent classify>
multi_register: <split | primary | segmented; default "split">
failures_dir: <absolute path to a directory of AI-vs-edit pairs, or "omit" to default to <project>/failures/ if non-empty>
overwrite: <true | false; default false. True permits overwriting an existing ~/.claude/voice/<voice_name>.md>
skeleton_path: <absolute path to the skeleton voice to mirror, or "omit" — voice-extractor will resolve the skeleton from the register (e.g., academic → ~/.claude/voice/academic.md; mixed-classifier-output → ~/.claude/voice/hybrid.md)>
```

When `samples_dir: omit` appears in a dispatch, the dispatcher resolves it to `<project>/samples/` (the phase-4 default) and passes the absolute path to the subagent. Same for `failures_dir: omit` → `<project>/failures/` if non-empty (otherwise treated as not provided, no failure mining). The subagent itself only ever sees absolute paths; this defaulting is dispatcher-side per spec §7.

The subagent reads the samples directory and a skeleton voice file selected by register classifier (per-register corpora where one register crosses the ≥ 85% threshold resolve to that register's skeleton at `~/.claude/voice/<register>.md`; blended corpora where no single register dominates resolve per the `multi_register` setting). It mirrors the skeleton's section structure and writes a new library file at `~/.claude/voice/<voice_name>.md` with `{{USER}}` tokens preserved for install-time substitution.

### `multi_register` (phase-3 routing)

When the corpus crosses sub-register boundaries (academic-report + personal-essay; technical reference + casual blog), `multi_register` controls how the extractor handles the split. Mode meanings:

- **`split` (default).** Halt with the `multi-register-corpus` rejection and return a cluster manifest in the report. {{USER}} re-dispatches once per cluster (`samples_dir` filtered to a single cluster's files), producing one voice file per sub-register. This is the safest route — unioning multi-register evidence into one voice file is the documented failure mode (a personal-essay first-person stance rule imported into an academic-report produces awkward prose).
- **`primary`.** Skeleton resolves to the majority sub-register's file; the minority files are excluded from rule calibration but listed in the report's `### Excluded files` section. Use when {{USER}} explicitly wants one voice file from a known-mixed corpus and accepts that minority-register patterns are dropped.
- **`segmented`.** Skeleton resolves to `~/.claude/voice/hybrid.md`; rules are tagged by sub-register inline (`[register: academic-report]`, `[register: personal-essay]`). Use when the corpus is genuinely cross-register and {{USER}} wants a single hybrid voice file. Segmented coverage of each sub-register is reported in `### Segmented coverage`.

The phase-3 academic skeleton additionally carries a `## Sub-register taxonomy` section that names the in-register sub-registers (academic-report, prospectus, personal-essay). When the produced voice scopes-out a sub-register (e.g., `multi_register=primary` excluded personal-essay), the sub-register's `### Exhibit N` is left as `TBD — sub-register out of scope for this extraction` and rules tagged with that sub-register are dropped from exemplar attachment.

### `failures_dir` (phase-3 cut-pattern mining)

Optional. Absolute path to a directory of AI-draft-vs-user-edit pairs. The naming convention is `<stem>.ai.md` (the AI-generated draft) and `<stem>.edit.md` (the user's edited version); the subagent diffs each pair at paragraph level and mines voice-telling deltas (not mundane typos, factual swaps, or citation inserts) into `## Cut patterns` entries.

A `.ai.md` without its `.edit.md` sibling is malformed and halts with `malformed-failures-dir`. Minimum useful input is 1 pair; below that, omit the field.

The 6 canonical cut patterns ship from the skeleton (academic): `aphoristic-closure`, `compression-stranded-verb`, `abstract-nominalization-cascade`, `reduced-relative-stacking`, `first-person-commitment-in-academic-report`, `citation-atomization`. Failures-dir extension adds author-specific patterns alongside these; existing canonical patterns may also gain author-specific before/after exemplars from the corpus.

Do not invoke `voice-extractor` from inside another mode's auto-trigger path. Unlike `[research mode]`, voice-extractor fires only on explicit request from {{USER}}. Generating a new voice unprompted is scope creep.

### Phase-3 dispatch caveats

If {{USER}} discloses corpus contamination (e.g., AI-generated patches inside a sample file), surface the caveat in the dispatch prompt as **caller-provided corpus caveats**: name the §10 patterns to flag as contamination (so the subagent does NOT calibrate rules toward them) versus the §10 patterns {{USER}} has pre-authorized as exemption candidates (subject to corpus-supports-2+-instances threshold). Treat any pre-authorized exemption populated by the subagent as a candidate; {{USER}} promotes to `## §10 exemptions` after reviewing the report.

## Caller-side iron-rule check (required)

After the subagent returns, **before surfacing its report**, run a caller-side iron-rule check on the produced file. This is the caller-side layer of the iron-rule defense-in-depth; `sourced check` runs the same check at render time as a **mandatory backstop**, not a round-trip optimization — the file cannot install if iron rules are missing.

Procedure:

1. Read every line of the skeleton the candidate voice was derived from (the register-matched or hybrid file identified in the subagent's report) under the section headings `## Iron rules`, `## AI-tells`, or `## Generation signatures`, plus any line containing the `[iron]` token. The phase-3 skeleton structure places `## Iron rules` and `## §10 exemptions` as sibling H2 sections; only the iron-rule prose is captured by this check (the §10 exemptions H2 section holds bullet-list overrides validated separately by `sourced check` I3).
2. For each such line, normalize (lowercase, collapse whitespace, strip trailing punctuation) and confirm it appears as a normalized substring in the produced voice file at `~/.claude/voice/<voice_name>.md`.
3. If any iron rule is missing from the produced file, do not surface the report to {{USER}} as a success. Either:
   - Re-dispatch voice-extractor with a correction prompt naming the missing rule(s), or
   - Surface the gap to {{USER}} explicitly with the missing rule text verbatim and ask how to proceed.
4. If the skeleton cannot be read at this point (permissions, race condition, transient I/O error), do not proceed: surface the read error to {{USER}} and fall back to `sourced check`'s render-time check, which is load-bearing, not advisory.

## After the iron-rule check passes

Surface the subagent's report to {{USER}}. The phase-3 return report carries these sections requiring {{USER}}'s hand:

- **`### Sections left TBD`** — sections the corpus didn't settle (Anchors with topically-narrow corpus; sub-register exhibits scoped out by `multi_register`; thin-coverage exemplar blocks). {{USER}} fills or deletes; do not silently pre-fill.
- **`### Iron-rule conflicts`** — corpus evidence against a preserved §10 rule. Informational; {{USER}} promotes to `## §10 exemptions` by hand if appropriate. Do not act on these without {{USER}} input. The phase-3 subagent counts instances and surfaces 2+ -instance candidates with lifted exemplars.
- **`### Anchor candidates`** — recurring named touchstones surfaced from the corpus. {{USER}} selects the cross-paper anchors and edits the `### Analogies and Anecdotes` section to list them.
- **`### Corpus contamination notes`** (only when caller flagged contamination) — §10 patterns appearing in the corpus that {{USER}} pre-disclosed as AI-draft residue. The subagent did not calibrate rules toward these; the section is documentary. {{USER}} may decide whether to re-extract from a de-contaminated corpus.

Next step after a successful run is always: {{USER}} runs `sourced switch voice <voice_name>` from inside the target project directory to render the new library voice into `config/voice.md`. Do not run `sourced switch voice` yourself; rendering into a project is a {{USER}} action.

## Phase-3 downstream consumption

Once the voice file is rendered into a project, two phase-3 consumers read it at mode entry:

- **`[writing mode]` Phase 1.** Reads the voice's `## Sub-register taxonomy` to set the prose-plan's Register Mode field, and `## Worked paragraphs` exhibits to model paragraph-scale sentence-role sequences. Phase 2 dispatches the `prose-drafter` subagent (`~/.claude/agents/prose-drafter.md`) with the voice's `## Cut patterns`, `## §10 exemptions` bullets, and per-register rule prose inlined. Full procedure: `docs/modes/writing.md` §Voice.
- **`[editing mode]` Pass 0 + Pass 7.** Pass 0 Revision uses the voice's worked-paragraph annotations to score paragraph one-job and outline correspondence. Pass 7 Cut-pattern audit reads `## Cut patterns` directly to flag corpus-named failure modes in the draft. Full procedure: `docs/modes/editing.md`.

If voice-extractor is run again with `overwrite: true`, both consumers transparently pick up the regenerated rules on next mode entry — the voice file is the source of truth, not any cached rule excerpt.

## See also

- `CLAUDE.md §9` — voice rules; when `config/voice.md` is read by each mode.
- `CLAUDE.md §10` and `CLAUDE.md §7.6` — §10 canonical IDs; how `config/voice.md`'s `## §10 exemptions` section overrides the never-list.
- `docs/modes/writing.md` §Voice and §Phase 2 dispatch — voice application + `prose-drafter` invocation.
- `docs/modes/editing.md` §Voice audit (Pass 8) and §Cut-pattern audit (Pass 7) — voice-derived audits on the draft.
- `~/.claude/agents/prose-drafter.md` — the isolated drafter subagent dispatched from `[writing mode]` Phase 2.
