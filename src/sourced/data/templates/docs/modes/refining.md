# [refining mode]

## Overview

Refining stress-tests the outline against the citation log before prose exists. Every claim gets a row in the §4 audit list; the gate to `[writing mode]` does not open until that list is clean and {{USER}} approves the refined outline explicitly. The failure mode this mode exists to prevent is **outline drift** — claims that made it past outlining but will not survive a sentence-level audit once prose is written, caught here at the lowest possible cost.

This is a **rigid** mode. The §4 audit list is the primary forcing artifact of the essay pipeline; its emission is what gates the `refining → writing` transition. §4 in root CLAUDE.md is the iron rule; this body is the operational protocol.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "refine this" / "tighten the outline" / "stress-test this" or equivalent (see manifest §7.2).
- **Gated handoff from `[outlining mode]`.** {{USER}} has explicitly signed off on the outline and directed the move to refining (manifest §7.4 `outlining → refining` gate).

**Do not enter when:**
- The `outlining → refining` gate has not been satisfied — no explicit sign-off from {{USER}} on the outline. Do not enter on your own judgment that outlining looks done. "Looks good" from you is not the gate; "looks good" from {{USER}} is.
- No outline exists yet. If {{USER}} says "refine this" but the session has no outline, surface the gap and enter `[outlining mode]` first.
- The project type is not `essay`. Refining is `essay`-only (manifest §7.1). Annotated-bib projects skip this mode; the citation audit runs inside `[annotated-bib mode]` instead.
- {{USER}}'s request is a single-span substitution on existing prose. That is `[finetuning mode]`.

## Iron Law

```
┌─────────────────────────────────────────────────────────────────────┐
│  NO ADVANCE TO WRITING WITHOUT §4 AUDIT LIST + REFINED OUTLINE      │
│  APPROVAL FROM {{USER}}                                             │
│  VOICE RULES DO NOT APPLY HERE — CITATION AND STRUCTURE AUDIT ONLY  │
│  STRUCTURAL CUTS AT REFINING ARE CHEAP; CUTS AFTER PROSE EXISTS     │
│  ARE NOT — DO NOT PUNT THEM TO EDITING                              │
└─────────────────────────────────────────────────────────────────────┘
```

Skipping the §4 audit list at refining means it will be run at editing on prose that already exists — at orders of magnitude higher rework cost per flagged row. Punting a structural cut to editing means rewriting sentences that should never have been written. The whole point of this mode is to pay the cheap cost now.

## Steps

### Entry

1. **Announce entry.** First output of the turn: `Switching to [refining mode].` Name the outline in one clause after the announcement: "refining the Cheyenne essay outline" / "refining the working outline".

2. **Load the outline and citation log.** Read the outline file (or the outline section of the working document). Load the citation log (`<draft>.citations.json` or `.claude/citations/working.citations.json`). Both are required before the iterative loop begins; do not run the audit from memory.

3. **Re-read the brief.** In particular, re-read the autonomy level (manifest §6) and the research question from `[plan mode]`. The final check in the iterative loop (step 4, item 7) tests whether the outline is answering that question.

### Iterative audit loop

4. **Run all seven checks as an iterative loop.** Reread the outline, apply each check, revise, reread. Iterate until a full reread surfaces no issues. The loop runs until it converges; a first pass that finds issues is not a complete run.

   **Check 1 — Paragraph necessity.** Does each paragraph earn its place in the argument? If removing it leaves the argument intact, it is filler dressed as argument. Mark for cut or merge.

   **Check 2 — Claim load-bearing.** Is each claim load-bearing, or is it padding? A claim is load-bearing if downstream claims depend on it or if the thesis rests on it. Claims that are true but inert can be cut without loss.

   **Check 3 — Citation-to-claim match (§4 audit).** Does each citation actually support the claim it is attached to? Cross-check each `@id` against its log entry — `exact_quote`, `surrounding_context`, `context_description`, `claim_supported` — and confirm the outline's paraphrase of the claim has not drifted past what the source says. This is the audit `[outlining mode]` intentionally deferred; it runs here and nowhere before.

   **Check 4 — Partial-entry recheck.** For every `verification_status: "partial"` entry whose citation appears in the outline, recheck against the partial-entry constraint in `~/.claude/citations/schema.md §Partial entries`. The "not load-bearing" clause in that constraint is re-evaluated against the **current outline**, not the outline at logging time. If a partial entry now supports a load-bearing claim, the options are: (a) find a verified source by escalating to `[research mode]`, or (b) treat the claim as a gap and surface it to {{USER}}.

   **Check 5 — Paragraph sequencing.** Does each paragraph follow from the one before it and set up the one after? Test this as a forward read and a backward read: forward checks whether each paragraph's opening follows from the previous closing; backward checks whether each paragraph's closing sets up the next opening. A paragraph that requires reordering to make either check pass should be moved now.

   **Check 6 — Counterpoint placement.** Are counterpoints addressed at the right point in the argument, or do they appear early enough to undermine claims that haven't been established yet? A counterpoint placed before its answering claim weakens rather than strengthens.

   **Check 7 — Research question alignment.** Is the outline answering the question set in `[plan mode]`? Read the research question from the brief and read the outline's implied thesis. Misalignment here is a scope problem — surface it to {{USER}} before emitting the sign-off package.

### Emit the §4 audit list

5. **After the iterative loop converges, emit the §4 audit list.** One row per citation audited, recording pass/`flagged: <reason>` for items 1, 2, 4, 5, 6 of §4. Item 3 (byline) is recorded via `retrieved_at` updates on the log entry and does not appear in this list (see manifest §7.5 and §4 item 3 in root CLAUDE.md).

   **Row grammar (canonical shape; `sourced check` I5 parses against this).** Each row is:

   ```
   <@id>: <item_1> ; <item_2> ; <item_4> ; <item_5> ; <item_6>
   ```

   Each item cell is exactly one of:
   - `pass` — audit item ran and found no issue.
   - `flagged: <one-line reason>` — audit item found an issue; resolution still pending.
   - `flagged → resolved: <action>` — audit item found an issue, resolved in this same turn (`action` is one of `prose revised`, `log updated`, `citation dropped`, `citation replaced with @<id>`, or a short equivalent).
   - `N/A` — permitted only for item 6 (synthesis) on single-source citations.

   No other cell values are valid. A row containing any `flagged: <reason>` (pending) closes the `refining → writing` gate. Only rows whose every cell is `pass`, `flagged → resolved: <action>`, or `N/A` pass the gate. Example rows:

   ```
   smith-2010-001: pass ; pass ; flagged: outline says "always" where exact_quote says "sometimes under Z" ; pass ; N/A
   chen-2021-003: pass ; pass ; flagged → resolved: outline claim scoped down to match hedge ; pass ; pass
   rodriguez-2019-001: pass ; pass ; pass ; flagged → resolved: cherry-pick risk resolved, surrounding_context noted ; pass
   ```

   **Scope of audit at refining is the outline (claim-level), not prose (sentence-level).** The check is: does the outline's claim, as written, accurately represent what the source says? `[editing mode]` runs the same §4 audit later against finished sentences; that audit operates at sentence-level drift. The two catch different failure modes and neither replaces the other.

   This list must appear in the same output turn as the sign-off package (step 7). A narrative summary of what the audit covered does not satisfy the forcing artifact; the list is the audit, per spec §3.5. Absence of the list in the sign-off turn means the audit did not run.

6. **Resolve all flagged rows before proceeding.** A row with `flagged: <reason>` (pending) means either: (a) revise the outline claim to match the source, (b) update the log entry if the audit revealed a logging error, (c) escalate to `[research mode]` to find a verified replacement, or (d) surface to {{USER}} as an unresolvable gap and cut the claim from the outline. Do not advance to the sign-off package (step 7) with any unresolved `flagged` rows. Any row with a pending `flagged: <reason>` cell closes `refining → writing` regardless of whether the sign-off package has been presented.

### Sign-off gate

7. **Present the refined outline to {{USER}}.** The sign-off package includes:
   - Section-by-section structure with one-line purpose per section.
   - Citations attached per paragraph (the `@id` list for each paragraph, as a quick scan map).
   - The §4 audit list (required; the gate does not pass without it).
   - Any uncertainties that remain after the loop converged.
   - Any places where the outline shifted during refining (cuts, reorders, claim revisions) — {{USER}} needs to know what changed since outlining.

8. **Wait for explicit approval.** "Looks good, start writing" is approval. Silence is not. An unenthusiastic or hedged read ("sure, I guess") is not; surface the hedge and ask whether to proceed. Do not advance to `[writing mode]` without a clear signal. "Good, ship it" / "good" / "fine" / "looks fine" are not sign-off. The required phrasing names advance ("start writing" or equivalent). Casual affirmatives that do not name advance are hedged; re-surface the refined outline and ask again.

9. **Announce advance.** On approval: `Switching to [writing mode].`

## Red Flags

If you catch yourself thinking any of the following, stop and check:

- *"The §4 audit list is long; I'll summarize instead of emitting rows."* — Summaries do not satisfy the forcing artifact. Emit the rows. The list is what the gate checks, not a description of the list.
- *"The outline looked fine on a first read, I'll skip the iterative loop."* — First-read confidence is how drift survives. Run the loop until convergence; a single pass is not convergence.
- *"{{USER}} signed off on the outline in `[outlining mode]`; that sign-off carries forward."* — The outlining sign-off gates entry to refining, not advance to writing. The refining sign-off is a separate gate on the refined outline.
- *"Partial entries are fine; the constraint only says they can't be load-bearing."* — Recheck each one against the current outline. The "not load-bearing" clause is evaluated against the outline as it stands now, not at logging time. An entry that was peripheral at log time may now be load-bearing.
- *"Voice feels off in this section — I'll flag it here."* — Voice rules do not apply at refining time. No `voice.md` read on entry to this mode. Voice is `[writing mode]` and `[editing mode]`'s domain; this mode is citation-and-structure only. Voice catches voice; this catches claim drift.
- *"This structural cut will require rewriting a whole section — I'll flag it instead of cutting."* — Cut it. Flagging a cut and deferring it to editing means rewriting prose that exists. The entire reason this mode precedes writing is that structural cuts here are cheap.
- *"The audit has no flagged rows, so I can advance without presenting the full sign-off package."* — No. The sign-off package includes the §4 audit list even when it is all-pass, plus the outline structure and citation map. {{USER}} needs to see the work, not just be told it passed.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "`[outlining mode]` already checked the citations." | Outlining defers the §4 audit by design — it builds the structure and attaches citations; it intentionally does not audit them. Refining is where the audit happens. They do different things; running both is correct. |
| "I can tell from reading the outline that the citations fit the claims." | Reading-level confidence is exactly what the iterative loop is designed to break. Cross-check `exact_quote` and `surrounding_context` for each `@id` against what the outline says the source shows. Drift is invisible at reading speed. |
| "The §4 audit is for editing, not for this stage." | The audit runs at both stages. Refining audits the outline (claim-level drift); editing audits the prose (sentence-level drift). Both are required. Skipping refining's run means sentence-level drift in editing will compound outline-level drift that should have been caught first. |
| "There is one unresolved `flagged` row but it's minor — I'll note it and advance." | The gate condition is zero unresolved `flagged` rows (manifest §7.4). One pending row closes the gate regardless of severity. Resolve it first. |
| "The partial entry's claim isn't load-bearing in the final paper — just in this section." | The partial-entry constraint evaluates load-bearing against the current outline. If the claim is structurally necessary to this section, it is load-bearing. Find a verified source or cut the claim. |
| "{{USER}} has seen the outline; the sign-off package is repetitive." | The sign-off package is not a repeat of the outline — it includes the §4 audit list, which did not exist when {{USER}} saw the outline, plus the record of changes made during refining. That combination is new information. |
| "The research question is roughly satisfied — close enough." | "Roughly" is a flag, not clearance. Surface the misalignment in check 7 and ask {{USER}} whether to adjust the outline or narrow the question. Close-enough misalignment is how papers drift from their stated question. |
| "Voice issues are blocking my read of the structure — I'll fix them while I'm here." | Record the voice observation (e.g., in a comment) and continue the structure audit. Do not apply voice rules. Voice is `[writing mode]`'s and `[editing mode]`'s domain; applying voice rules at refining mixes audit semantics and produces false confidence in sections that haven't been drafted yet. |
| "The sign-off package is long; I'll ask {{USER}} if they want the full thing." | Present the full package. The §4 audit list and the outline structure map are required, not optional based on {{USER}}'s preference for brevity. If {{USER}} wants to read it quickly, they will. |
| "{{USER}} said 'good, ship it' — that's approval enough." | Approval at the sign-off gate names the advance ("start writing" / "ready to write" / "advance to writing"). Casual "good" or "ship it" without naming writing is hedged; re-surface the outline and the audit list, and ask again. |

## Quick Reference

```
ENTRY:    Switching to [refining mode]. refining <outline name>.

LOAD:     outline file (or section) + citation log.
READ:     research question from brief (check 7 target).

ITERATIVE LOOP (until convergence):
  Check 1  — Paragraph necessity: does each paragraph earn its place?
  Check 2  — Claim load-bearing: is each claim structurally necessary?
  Check 3  — Citation-to-claim (§4 audit): does each @id support its claim?
             Cross-check exact_quote / surrounding_context / claim_supported.
  Check 4  — Partial-entry recheck: is each "partial" still non-load-bearing?
             Re-evaluate against current outline. Escalate or cut if now load-bearing.
  Check 5  — Paragraph sequencing: forward + backward read.
  Check 6  — Counterpoint placement: doesn't undermine unestablished claims.
  Check 7  — Research question alignment: does the outline answer plan's question?

EMIT §4 AUDIT LIST (required; sourced check I5 parses this):
  One row per citation:
    <@id>: <item_1> ; <item_2> ; <item_4> ; <item_5> ; <item_6>
  Cells: pass | flagged: <reason> | flagged → resolved: <action> | N/A (item 6 only)
  Scope: claim-level (outline claims vs log), not sentence-level (that's editing).

RESOLVE: all flagged rows before sign-off.

SIGN-OFF PACKAGE:
  - Section-by-section structure + one-line purpose per section.
  - Citations per paragraph (@id map).
  - §4 audit list (required).
  - Uncertainties remaining after loop.
  - Changes made during refining.

WAIT:     Explicit {{USER}} approval. Silence is not approval.

ADVANCE:  Switching to [writing mode].

FORCING ARTIFACT:  §4 audit list (required at sign-off; gates refining → writing).
```

## What this mode does NOT do

- **Apply voice rules.** Voice is `[writing mode]` and `[editing mode]`'s domain. `voice.md` is not read on entry to this mode. Voice observations noted during refining are surfaced as comments, not applied.
- **Draft prose.** Refining operates on the outline only. Drafting belongs in `[writing mode]`.
- **Replace `[outlining mode]`.** Refining is not an outline-building step; it is an audit and stress-test of an outline that already exists and has been signed off by {{USER}}.
- **Auto-advance to `[writing mode]`.** The sign-off gate requires explicit {{USER}} approval on the refined outline with the §4 audit list present. The mode cannot clear its own gate.
- **Run sentence-level §4 audit.** That audit — prose against log at sentence granularity — belongs to `[editing mode]` pass 2. Refining's audit is claim-level: does the outline claim match the source?

## Exit Gates

**Allowed transitions (from refining):**
- → `[writing mode]`. Gate: §4 audit list emitted with zero unresolved `flagged` rows AND refined outline approved explicitly by {{USER}} (manifest §7.4). Use `Switching to [writing mode].`
- → `[research mode]`. Auto-fire via §3 self-correction (unverified citation discovered during check 3), or explicit escalation when check 4 finds a partial entry that is now load-bearing and no verified replacement is in the log. Use `Switching to [research mode] (invoked from [refining mode]).` Return to refining after source logged or gap accepted.
- → `[outlining mode]`. If check 7 reveals the outline has drifted from the research question far enough to require structural rebuilding, surface the finding and ask {{USER}} whether to return to outlining rather than trying to patch it at refining. {{USER}} decides; refining does not force a return to outlining unilaterally.
- → `[collaborative mode]`. If {{USER}} pauses to discuss scope, approach, or autonomy level during the loop. Explicit switch only; refining does not auto-downgrade.

**Forbidden transitions:**
- → `[writing mode]` with any unresolved `flagged` rows in the §4 audit list. Gate violation; halts with the specific pending rows named.
- → `[writing mode]` without explicit {{USER}} approval on the refined outline. Silence is not approval; do not read inaction as clearance.
- → `[outlining mode]` directly from `[writing mode]` — that route reverses the pipeline; it routes through `[refining mode]` in the normal flow. If a mid-writing structural issue surfaces, the correct path is `[writing mode]` → `[refining mode]` → `[writing mode]`, not a direct outlining re-entry.
- → `[editing mode]` direct. Editing audits prose; if no prose exists, editing has no input and the ask is an outlining or refining ask.
- → `[formatting mode]` direct. Unreachable from refining; formatting requires the full pipeline through writing and editing.

## See also

- `CLAUDE.md §4` — synthesis integrity iron rule; items 1, 2, 4, 5, 6 define the audit row content; item 3 (byline) defines the `retrieved_at` update path.
- `CLAUDE.md §7.4` — mode-to-mode gate table; `refining → writing` gate condition and its forcing artifact.
- `CLAUDE.md §7.5` — forcing artifact definitions; §4 audit list is defined there.
- `CLAUDE.md §7.6` — precedence rules; §4 verbatim > §10 inside quoted spans (applies when reading `exact_quote` from the log).
- `docs/modes/outlining.md` — predecessor mode; the outline produced and signed off there is the input to this mode.
- `docs/modes/writing.md` — successor mode; receives the refined outline and the §4 audit list at sign-off.
- `docs/modes/editing.md` — downstream mode that runs §4 audit again at sentence level; row grammar is identical so `sourced check` I5 parses both.
- `docs/modes/research.md` — escalation target for partial-entry-now-load-bearing findings (check 4) and for unverified citations discovered during the audit.
- `~/.claude/citations/schema.md §Partial entries` — defines the partial-entry constraint re-evaluated in check 4.
- `~/.claude/citations/schema.md §Staleness` — `retrieved_at` threshold; stale entries surfaced during check 3 trigger the byline re-verification path in `[research mode]`.
