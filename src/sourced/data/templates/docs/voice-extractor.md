# Voice-extractor dispatch

**When to read this file.** Before dispatching the `voice-extractor` subagent via the Agent tool. Referenced from `CLAUDE.md §9`. Voice-extractor is **not a mode** and does **not** auto-trigger. It runs only in `[collaborative mode]` and always in a single dispatch (never in parallel; this is unlike `source-finder`). If {{USER}} asks from another mode, announce the switch to `[collaborative mode]` first (`Switching to [collaborative mode].`), dispatch the subagent, present its report, and stay in collaborative until {{USER}} directs otherwise. Voice calibration is a setup operation, not part of the research/write/edit pipeline, so returning to the prior mode after the dispatch would mislead {{USER}} about where the conversation is.

## Dispatch procedure

Read the subagent definition at `~/.claude/agents/voice-extractor.md` if you have not already. Then dispatch via the Agent tool with the template below as the `prompt` argument. Fill every placeholder. If an optional field is not applicable, write `omit` rather than removing the line; the subagent parses the structure.

```
samples_dir: <absolute path to a directory containing the writing samples>
voice_name: <name for the new library voice; must match [a-z0-9_-]+>
register: <academic | technical | casual | journalistic | narrative, or "omit" to let the subagent classify>
overwrite: <true | false; default false. True permits overwriting an existing ~/.claude/voice/<voice_name>.md>
skeleton_path: <absolute path to the skeleton voice to mirror, or "omit" — voice-extractor will resolve the skeleton from the register (e.g., academic → ~/.claude/voice/academic.md; mixed-classifier-output → ~/.claude/voice/hybrid.md)>
```

The subagent reads the samples directory and a skeleton voice file selected by register classifier (per-register corpora where one register crosses the ≥ 85% threshold resolve to that register's skeleton at `~/.claude/voice/<register>.md`; blended corpora where no single register dominates resolve to `~/.claude/voice/hybrid.md`). It mirrors the skeleton's section structure and writes a new library file at `~/.claude/voice/<voice_name>.md` with `{{USER}}` tokens preserved for install-time substitution.

Do not invoke `voice-extractor` from inside another mode's auto-trigger path. Unlike `[research mode]`, voice-extractor fires only on explicit request from {{USER}}. Generating a new voice unprompted is scope creep.

## Caller-side iron-rule check (required)

After the subagent returns, **before surfacing its report**, run a caller-side iron-rule check on the produced file. This is the caller-side layer of the iron-rule defense-in-depth; `sourced check` runs the same check at render time as a **mandatory backstop**, not a round-trip optimization — the file cannot install if iron rules are missing.

Procedure:

1. Read every line of the skeleton the candidate voice was derived from (the register-matched or hybrid file identified in the subagent's report) under the section headings `## Iron rules`, `## AI-tells`, or `## Generation signatures`, plus any line containing the `[iron]` token.
2. For each such line, normalize (lowercase, collapse whitespace, strip trailing punctuation) and confirm it appears as a normalized substring in the produced voice file at `~/.claude/voice/<voice_name>.md`.
3. If any iron rule is missing from the produced file, do not surface the report to {{USER}} as a success. Either:
   - Re-dispatch voice-extractor with a correction prompt naming the missing rule(s), or
   - Surface the gap to {{USER}} explicitly with the missing rule text verbatim and ask how to proceed.
4. If the skeleton cannot be read at this point (permissions, race condition, transient I/O error), do not proceed: surface the read error to {{USER}} and fall back to `sourced check`'s render-time check, which is load-bearing, not advisory.

## After the iron-rule check passes

Surface the subagent's report to {{USER}} — especially the `### Sections left TBD`, `### Iron-rule conflicts`, and `### Anchor candidates` lists, which require {{USER}}'s hand to resolve. Do not silently pre-fill TBD sections; the subagent left them open because the corpus didn't settle the question, and filling them requires judgment the subagent deliberately deferred. Iron-rule conflicts surfaced by the subagent (corpus evidence against a preserved rule) are informational — do not act on them without {{USER}} input.

Next step after a successful run is always: {{USER}} runs `sourced switch voice <voice_name>` from inside the target project directory to render the new library voice into `<project>/voice.md`. Do not run `sourced switch voice` yourself; rendering into a project is a {{USER}} action.

## See also

- `CLAUDE.md §9` — voice rules; when `voice.md` is read by each mode.
- `CLAUDE.md §10` and `CLAUDE.md §7.6` — §10 canonical IDs; how voice.md's `## §10 exemptions` section overrides the never-list.
- `docs/modes/writing.md` §Voice — voice application procedure at write time.
- `docs/modes/editing.md` §Voice audit — pass 8, voice audit on the draft.
