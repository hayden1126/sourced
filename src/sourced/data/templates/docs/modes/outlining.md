# [outlining mode]

## Overview

Outlining produces a paragraph-level structural plan — claim, citation ids, role, and paragraph-to-paragraph handoff — before any prose exists. The failure mode this mode exists to prevent is **premature prose**: moving from plan to writing without settling the argument's structure, so every structural error becomes a sentence-level editing cost instead of a one-line outline fix.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "draft this" / "outline this" / "structure this" or equivalent (see manifest §7.2).
- The brief is complete enough for outlining: every load-bearing field in `<draft>.brief.md` is filled or explicitly TBD'd (manifest §7.4, `plan → outlining` gate).

**Do not enter when:**
- The brief is not yet ready (key fields blank, scope still open). Return to `[plan mode]` or ask {{USER}} to fill the brief first.
- The project type is `annotated-bib`. Annotated-bib projects skip outlining and go from plan/research directly to `[annotated-bib mode]`. Entering outlining from an annotated-bib project is a registry violation (manifest §7.1).
- No citation log exists. Outlining attaches ids to claims; without a log to draw from, the paragraph-level plan is structurally empty. Redirect to `[research mode]` first.

## Iron Law

```
┌──────────────────────────────────────────────────────┐
│  NO PROSE IN OUTLINING — IDs ATTACH; THEY DON'T AUDIT │
└──────────────────────────────────────────────────────┘
```

Outlining is generative, not evaluative. Attach citation ids to claims as you draft. Do not stop to verify scope, check inference chains, or audit flow — that is `[refining mode]`'s job. The cost of an audit at outline time is wasted work on structure that may change; the cost of prose at outline time is that every structural revision becomes a sentence-level rewrite.

## Steps

1. **Announce entry.** First output of the turn: `Switching to [outlining mode].`

2. **Read `voice.md` in full.** Paragraph Flow rules apply at outline time — you need them to construct the handoff line for each paragraph. If `voice.md` is missing, stop and ask {{USER}} to run `sourced switch voice <name>` before continuing. Do not guess at voice rules.

3. **Load the citation log.** Open `<draft>.citations.json` adjacent to the draft (or `.claude/citations/working.citations.json` before a draft file exists). The outline attaches bare ids from this log to each paragraph's claim. If the log is missing, stop — directing {{USER}} to `[research mode]` is the correct move, not inventing placeholder ids.

4. **Read the brief.** Confirm the thesis, scope, audience, and section structure (if the brief names one). These govern what sections exist and what the argument needs to accomplish.

5. **Build the outline — sections first, then paragraphs.** For each section, name its role in the argument (setup, argument, counterargument, synthesis, conclusion). Then, within each section, build paragraphs:

   - **Claim.** One sentence. What this paragraph asserts.
   - **Citation ids.** Bare ids from the log that support the claim (e.g., `smith-2010-001`, `chen-2021-003`). NOT Pandoc `[@id]` syntax — that belongs in `[writing mode]`.
   - **Role.** One clause: what the paragraph does in the argument (introduces the problem, presents the main evidence, addresses the counterpoint, synthesizes two threads).
   - **Handoff.** The transition, reference-back, or concept that bridges this paragraph to the next, per `voice.md §Paragraph Flow`. If you cannot name the handoff, the paragraphs are not connected yet — resolve the connection before moving on.

   If a claim has no supporting id from the log, mark it explicitly: `[UNSOURCED: <claim>]`. Do not invent ids or skip the slot silently.

6. **Name explicit counterpoints.** For each counterpoint the paper will address, list it with the ids that will answer it. Counterpoints should appear in their structural location (the paragraph or section where the paper meets them), not as a separate appendix.

7. **Present the outline and ask.** When the outline is at a place you would call complete, present it in full and ask: "Outline is at a place I'd call complete. Ready to refine, or more outlining?" Completion is {{USER}}'s judgment, not yours. Do not interpret silence or topic-shift as acceptance.

## What This Mode Does NOT Do

- **Produce prose.** Sentences belong in `[writing mode]`. The outline carries claims and handoffs, not drafted paragraphs.
- **Render citation strings.** Citations stay as bare ids (`smith-2010-001`). Pandoc syntax (`[@id]`, `@id`) is `[writing mode]`'s notation; rendered strings (`(Smith, 2010)`) are `[formatting mode]`'s output.
- **Audit claims.** Scope drift, inference chains, load-bearing checks, and byline rechecks all happen in `[refining mode]`. Outlining attaches ids; refining stress-tests the attachment. This is the cheap-cuts-before-expensive-cuts principle: catch structural problems before prose exists, and catch citation-integrity problems before prose is invested in a particular structure.
- **Auto-advance to refining.** The handoff gate is {{USER}}-initiated. Outlining cannot self-certify as complete (manifest §7.4, `outlining → refining` gate).

## Red Flags

- *"The claim is obvious — I'll draft a sentence or two to show the shape."* — No. Prose in the outline creates sunk cost on structure that may change in refining. The claim is the claim; the sentence is the sentence; they live in different modes.
- *"I don't have an id for this claim but I'll put a placeholder author-year for now."* — No. Use `[UNSOURCED: <claim>]`. Invented ids corrupt the log cross-check in `[refining mode]`.
- *"The handoff between paragraphs 3 and 4 is obvious — I'll leave it implicit."* — No. If you can't write the handoff in one clause, the connection isn't settled. Name it or rearrange.
- *"The outline looks good to me — I'll announce the switch to refining."* — No. Present the outline, ask, wait. The gate is {{USER}}'s sign-off, not your assessment.
- *"I'll use `[@smith-2010-001]` syntax — it looks cleaner."* — No. Pandoc syntax is `[writing mode]`'s notation. Use bare ids in the outline.
- *"voice.md is probably the same as last session — I'll work from memory."* — Re-read on every entry. The file is the authority.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "A few sentences of prose would make the outline clearer." | The outline is structure, not illustration. Prose in the outline turns a structural plan into a draft, which moves the sunk-cost problem into `[refining mode]`. |
| "Auditing claims as I go saves a round-trip through refining." | Refining stress-tests the whole outline at once against the full citation log. Partial auditing at outline time misses cross-claim inconsistencies and wastes effort on structure that may change. |
| "The `[@id]` syntax is more precise than a bare id." | Precision is not the issue. `[@id]` is write-time notation; bare ids are outline-time notation. Mixing them makes the outline look like a draft and blurs the mode boundary. |
| "I know the outline is ready — the handoff question is just formality." | Completion is {{USER}}'s judgment. Your read of readiness is a data point, not the gate. Present and ask. |
| "{{USER}} said 'looks good' or 'seems fine' — I'll advance." | Those are positive evaluations, not explicit sign-off. The required question is "Ready to refine, or more outlining?" and the accepted answer names advance ("ready to refine" or equivalent). A compliment is not a gate. |
| "voice.md's Paragraph Flow rules are simple enough to apply from memory." | Apply them from the file. Paragraph Flow is the specific section relevant at outline time; re-reading takes seconds and prevents stale-rule drift. |
| "The project type is annotated-bib but the outline would help." | Annotated-bib projects don't use outlining — the mode registry (manifest §7.1) is clear. An overlay may have already removed this mode from the allowed list; check `CLAUDE.d/` if present. |

## Quick Reference

```
ENTRY:   Switching to [outlining mode].

LOAD:    Read voice.md (Paragraph Flow only — applies now).
         Load citation log.
         Read brief (thesis, scope, audience).

BUILD:   Sections → Paragraphs. Per paragraph:
           Claim      — one sentence
           Citation ids — bare ids from log (e.g., smith-2010-001)
                          NOT [@id] syntax
                          Mark gaps as [UNSOURCED: <claim>]
           Role       — one clause
           Handoff    — one clause per voice.md §Paragraph Flow
                        If you can't name it, the connection isn't settled.
         Counterpoints — in their structural location, with supporting ids.

DOES NOT AUDIT — attach ids, don't verify them (that's refining).

HANDOFF: Present outline in full.
         Ask: "Outline is at a place I'd call complete.
               Ready to refine, or more outlining?"
         Wait. Do not auto-switch.
```

## Exit Gates

**Allowed transitions (from outlining):**
- → `[refining mode]`: when {{USER}} gives explicit sign-off ("ready to refine"). Announce `Switching to [refining mode].` (manifest §7.4, `outlining → refining` gate).
- → `[research mode]` via §3 self-correction auto-trigger or `[UNSOURCED]` gap that {{USER}} wants filled. Use `Switching to [research mode] (invoked from [outlining mode]).` Return to outlining after the source is logged: `Switching back to [outlining mode].` On return from `[research mode]`: fill the `[UNSOURCED]` slot with the logged `@id` in-place, then resume at step 5 and continue building the outline. Re-present the full outline to {{USER}} only at step 7 (sign-off), not on each individual slot fill.
- → `[collaborative mode]` if {{USER}} pauses to discuss scope or structure meta-questions. Explicit switch only.

**Forbidden transitions:**
- → `[writing mode]` direct. Writing requires a refined outline. The `outlining → writing` path does not exist; `[refining mode]` is required between them (manifest §7.4 forbidden transitions).
- → `[refining mode]` without {{USER}} sign-off. Auto-advancing on your own judgment is a gate violation regardless of how complete the outline appears.
- → `[formatting mode]` / `[editing mode]` direct. Both are downstream of writing; outlining is upstream of it.

## See also

- `CLAUDE.md §6` — brief schema and autonomy levels; prerequisite for outlining entry.
- `CLAUDE.md §7.1` — mode registry; `outlining` is `essay` project types only.
- `CLAUDE.md §7.4` — gate table: `plan → outlining` (brief complete), `outlining → refining` ({{USER}} sign-off), forbidden `outlining → writing` direct path.
- `CLAUDE.md §8` — citation log; Moment 2 (in-prose ids) begins in `[writing mode]`, not here.
- `docs/modes/refining.md` — the next mode; runs the §4 audit on the outline before prose exists.
- `docs/modes/writing.md` — where `[@id]` Pandoc syntax is introduced and Paragraph Flow is fully applied.
- `voice.md §Paragraph Flow` — the handoff-line rule applied at step 5.
