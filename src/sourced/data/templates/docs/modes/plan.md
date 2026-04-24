# [plan mode]

## Overview

Plan mode frames the research question, defines the argument's shape, and maps the sources needed — before any source is fetched or any prose is drafted. The failure mode this mode exists to prevent is **premature commitment**: entering `[research mode]` without a scoped question, or entering `[outlining mode]` without a defensible argument map, and then discovering mid-draft that the foundation doesn't hold.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "plan this" / "what should I research" / "map sources" or equivalent (see manifest §7.2).
- Brief is present OR skip-brief escape is active (manifest §7.4 gate; see §6 of root CLAUDE.md).

**Do not enter when:**
- No brief exists and {{USER}} has not explicitly invoked the skip-brief escape. Propose filling out a brief first; do not begin planning on a blank intake.
- The task is a targeted revision, citation lookup, or single-section edit. Those belong in the relevant downstream mode, not plan.
- Project type is `annotated-bib` but the brief's Topic and Scope statement have not been written yet. Topic-specificity gate (Phase 1, see below) fires on entry; if there is nothing to test, route back to intake.

## Steps

1. **Announce entry.** First output of the turn: `Switching to [plan mode].`

2. **Read the brief.** Load `<draft-name>.brief.md` or `.claude/briefs/working.brief.md` per §6. Restate the autonomy level in one sentence: `Brief sets autonomy to [level]; I will [behavior description].` If the brief omits the autonomy level, assume medium and say so. The restate is not optional — {{USER}} uses it to confirm the brief was read and the level is current.

3. **For essay projects — question and argument frame.** State:
   - The working research question in one sentence.
   - The working claim/thesis at the current level of certainty (placeholder or "TBD" if the brief doesn't resolve it).
   - The argument structure: what the paper must establish in sequence (not section names — logical moves).
   - The kinds of sources needed and any known gaps or counterpoints that must be addressed.

   Flag uncertainties before advancing. Present the frame to {{USER}} and wait for input. Do not proceed to step 4 without at least one exchange confirming the frame, unless the brief and prior session make the frame clearly settled.

4. **After research — source mapping.** Once `[research mode]` returns, re-enter plan mode for source-mapping by default. {{USER}} may explicitly say "go straight to outlining" to skip; silence is not that permission. Map sources to argument moves: which source supports which claim, where concentration is too heavy, where gaps remain, which counterpoints are now covered and which are not. Present the map to {{USER}} and surface weak links. Plan and research may interleave across multiple turns; the mode switch announcement fires on each re-entry.

5. **Advance gate check.** Before handing off to `[outlining mode]`, confirm: every load-bearing field (argument/thesis, audience, scope, autonomy level, and any field marked `[required]` in `~/.claude/templates/brief.template.md`) is filled or explicitly TBD'd. Fields left entirely blank (no TBD, no value) fail the gate; an explicit "TBD" passes. Also confirm: the argument frame is agreed, and no unresolved source gaps sit under a central claim. State what is confirmed and what is still TBD. Do not advance without {{USER}} acknowledgment of the current state.

6. **Announce handoff.** `Ready to advance to [outlining mode]?` On yes: `Switching to [outlining mode].` On no: stay in plan or return to `[collaborative mode]` as {{USER}} directs.

---

## Annotated-bib project variant

In annotated-bib projects (project type `annotated-bib`), plan mode runs two sequential gated phases. `[outlining mode]`, `[refining mode]`, and `[writing mode]` are not in the mode registry for this project type; plan advances to `[research mode]` instead.

Steps 1 and 2 apply unchanged. Replace steps 3–6 with the following.

### Phase 1: Topic-specificity gate

Read the brief's *Topic* field and *Scope statement* (in-scope bullets, out-of-scope bullets, boundary cases). Apply the stranger test: could a stranger, given only those sections, predict with better than coin-flip accuracy whether a specific candidate source qualifies?

Failures that trigger the gate:

- One-word or single-phrase topic with no scope narrowing ("climate change", "academic burnout").
- Scope statement that restates the topic using synonyms without adding cuts.
- In-scope bullets that name whole fields rather than specific slices of the topic.
- Absent or vague out-of-scope bullets (absence is ambiguity, not permission).

**On failure:** do not auto-narrow. Surface 3–5 candidate narrowings drawn from the topic's actual sub-literature. Each narrowing gets a one-line rationale naming which facet of the user's topic it lives in. {{USER}} picks one, proposes an alternative, or rewrites scope. The gate re-fires if the next round remains too broad. An ungated advance is a protocol violation; "looks fine" is not gate passage; silence is not approval. An ungated advance to Phase 2 without explicit {{USER}} acknowledgment of Phase 1 passage is a protocol violation.

**On passage:** proceed to Phase 2.

### Phase 2: Facet decomposition

With topic narrow and scope clear, decompose into 3–6 facets. Facets are distinct angles of the one topic — not supporting arguments or sub-claims. Properties:

- **Mutually distinct.** A source should not plausibly qualify under two facets simultaneously.
- **Exhaustive within scope.** A source that clearly falls within the brief's scope should land in at least one facet. If you can identify a valid in-scope source that fits no facet, the decomposition has a gap.

Example: topic "workplace burnout in early-career trainee physicians (2015–2025)" → facets: (a) prevalence and measurement methods, (b) structural and systemic drivers, (c) interventions and outcome evaluation, (d) demographic variation within the trainee population, (e) comparison to analogous professions.

**Cap enforcement (before presentation).** Before surfacing the facet list to {{USER}}, count the proposed facets. If count > 6, collapse or consolidate to ≤6 before presenting. Presenting more than 6 to {{USER}} for approval does not legitimize an over-cap decomposition; the cap is enforced by the agent before presentation, not by {{USER}}'s approval.

Present the facet list with per-facet rationale. Wait for approval. Do not dispatch source-finders until facets are approved. On approval: `Switching to [research mode].`

## Red Flags

- *"The brief is partial but I have a sense of the scope — I'll proceed."* — Restate what is partial. Surface it. Don't proceed on a sense.
- *"The topic is narrow enough; the stranger test feels pedantic."* — Run the test anyway. Annotated-bib projects frequently fail Phase 1 the first time. The test is not a formality.
- *"I'll surface one candidate narrowing, not three to five."* — The range is load-bearing. One narrowing is a directive; three to five is a choice. {{USER}} picks.
- *"Research returned good sources — I'll skip the source-mapping step and jump to outlining."* — Source mapping is the default after a research round-trip. Only an explicit "go straight to outlining" from {{USER}} skips it; silence does not.
- *"{{USER}} seems ready to move on — I'll treat that as confirmation of the frame."* — Readiness to move on is not confirmation of the frame. Ask explicitly.
- *"Advance to outlining without confirmed argument frame."* — The essay-path gate requires at least one exchange confirming the frame before advancing. An ungated advance is a protocol violation; silence is not approval.
- *"I've produced 8 facets — I'll present them all and let {{USER}} pick."* — No. The cap is enforced by the agent before presentation, not by {{USER}}'s approval. Collapse or consolidate to ≤6 before surfacing.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "The brief is vague but we can sharpen it during outlining." | Outlining requires a brief complete enough to support it (manifest §7.4). Vagueness in the brief surfaces as structural instability in the outline — catch it in plan, not after an outline pass. |
| "Phase 1 passed easily — I'll combine it with Phase 2 to save a turn." | The phases are gated in sequence. Phase 1 passage and Phase 2 approval are two separate {{USER}} acknowledgments. Combining them removes one gate without telling {{USER}}, which is an ungated advance. |
| "I can see the obvious facets — no need to explain the per-facet rationale." | The rationale is what {{USER}} uses to approve or reshape the decomposition. Facets without rationale are names, not a structure {{USER}} can evaluate. |
| "The scope statement has out-of-scope bullets, so it passes the stranger test." | Out-of-scope bullets are necessary but not sufficient. The stranger test also requires the in-scope bullets to name specific cuts, not whole fields. Check both. |
| "The brief sets autonomy to High — I'll advance to outlining without waiting for confirmation." | High autonomy raises the small-call threshold (§6), it does not remove mode-to-mode gates. The plan → outlining gate requires the brief to be complete enough for outlining, regardless of autonomy level. |
| "Announcing the mode on re-entry to plan (after a research round-trip) is redundant." | The announcement fires on every mode switch. A re-entry from research to plan is a mode switch. The announcement is how {{USER}} tracks the current mode; omitting it breaks the transcript's mode-state record. |
| "Eight facets are all distinct and useful; cutting to six loses information." | Per-facet entry target is bounded by the brief's cap. Six facets is the ceiling; information that doesn't fit is surfaced as scope-growth, not as an over-cap dispatch. |

## Quick Reference

```
ENTRY:
  Switching to [plan mode].
  Read brief → restate autonomy level.

ESSAY PATH:
  State: working question / working thesis / argument moves / source kinds needed.
  Flag uncertainties. Wait for input.
  [After research] Re-enter plan for source-mapping by default.
    {{USER}} may say "go straight to outlining" to skip; silence is not that permission.
    Source map: claim → supporting sources, gaps, over-concentration.
  Advance check: brief load-bearing fields (argument/thesis, audience, scope, autonomy level,
    any [required] field in brief.template.md) filled or TBD'd; frame agreed; no central gaps.
  → "Ready to advance to [outlining mode]?"

ANNOTATED-BIB PATH:
  Phase 1 — Topic-specificity gate (stranger test):
    On failure → surface 3–5 candidate narrowings with rationale; wait for pick.
    Gate re-fires if still too broad.
    On passage → proceed to Phase 2.
  Phase 2 — Facet decomposition (3–6 facets):
    Distinct, exhaustive within scope. Per-facet rationale.
    Wait for approval.
    On approval → Switching to [research mode].

GATE: Explicit {{USER}} acknowledgment required at every advance. Silence is not approval.
```

## What this mode does NOT do

- **Fetch or vet sources.** That belongs in `[research mode]`. Plan identifies what kinds of sources are needed and where; research finds and verifies them.
- **Draft prose or produce an outline.** Outlining starts only after the plan-to-outlining gate passes.
- **Write annotations.** Annotation prose belongs in `[annotated-bib mode]`.
- **Auto-narrow the topic.** On Phase 1 failure, plan surfaces candidate narrowings and waits. It does not pick one and proceed.

## Exit Gates

**Allowed transitions (from plan):**

- → `[outlining mode]`: when brief is complete enough for outlining and {{USER}} confirms. Use `Switching to [outlining mode].` Gate: manifest §7.4 `plan → outlining` row.
- → `[research mode]`: after essay-path frame is agreed and {{USER}} initiates research, OR after annotated-bib Phase 2 facets are approved. Use `Switching to [research mode].`
- → `[collaborative mode]`: when {{USER}} pauses planning to discuss something meta (scope, autonomy, whether to proceed). Explicit switch only.

**Forbidden transitions:**

- → `[outlining mode]` without brief complete enough for outlining. Gate violation; halts with missing-field named.
- → `[writing mode]` direct. Plan does not produce prose-ready material.
- → `[formatting mode]` direct. Unreachable from plan.
- → `[annotated-bib mode]` direct from plan. Annotated-bib projects route through `[research mode]` after Phase 2; `[annotated-bib mode]` enters from an explicit trigger after research, not from plan.

## See also

- `CLAUDE.md §6` — intake brief schema, skip-brief escape, scope-growth soft-stop, autonomy levels. Source of truth for the brief-check step and the plan entry gate.
- `CLAUDE.md §7.2` — explicit triggers (source of truth for trigger phrases).
- `CLAUDE.md §7.4` — mode-to-mode gate table; the `→ plan` and `plan → outlining` rows govern this mode's entry and exit.
- `docs/modes/research.md` — target for the essay-path handoff and the annotated-bib Phase 2 handoff.
- `docs/modes/outlining.md` — target of the essay-path exit gate.
- `docs/modes/annotated-bib.md` — downstream mode for annotated-bib projects after research completes; entered via explicit trigger, not direct from plan.
