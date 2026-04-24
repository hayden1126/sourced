# [editing mode]

## Overview

Editing audits a drafted prose section against the citation log, the grammar, the mechanics, the §10 generation signatures, the quote-density budget, and the voice rules — in that order, as eight discrete passes. The failure mode this mode exists to prevent is **silent polish** — tightening prose in ways that paper over citation drift, mechanical errors, or voice violations, and handing off an AI-flavored draft to `[formatting mode]` without surfacing the hits. Each pass is a separate audit with its own forcing list; skipping or collapsing passes defeats the discipline the §4 audit and the voice audit were designed to carry.

This is a **rigid** mode. The eight-pass order is load-bearing; the handoff to `[formatting mode]` is artifact-gated. §4 in root CLAUDE.md is the iron rule; this body is the operational protocol.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "edit this" / "revise this" / "polish this" or equivalent (see manifest §7.2).
- **From `[writing mode]` on {{USER}}-initiated handoff.** Writing → editing is {{USER}}-initiated only (manifest §7.4); editing does not auto-enter from a completed writing pass.

**Do not enter when:**
- The draft has not yet been through `[refining mode]` and `[writing mode]`. Editing audits prose; if no prose exists, the ask is a drafting ask and belongs in `[writing mode]`.
- The section has structural deviation from the refined outline — missing headings, reordered sections, paragraphs asserting claims the outline did not place. Detected structural deviation returns to `[refining mode]`, not a prose-level patch here (see step 0).
- The change requested is a single-span substitution that {{USER}} is uncertain about. That's `[finetuning mode]` — editing is a whole-draft audit, not a local substitution.
- Citations in the section are still unresolved (`[UNSOURCED]` tokens present, `[VERIFY: …]` hedges carrying load-bearing claims). Resolve via `[research mode]` before editing.

## Iron Law

```
┌───────────────────────────────────────────────────────────────┐
│  NO HANDOFF WITHOUT §4 AUDIT LIST + VOICE AUDIT SURFACE-SCAN  │
│  NO PROSE-LEVEL FIX OF STRUCTURAL DEVIATION — REFINING DOES IT │
│  NO PASS COLLAPSE: 8 PASSES, IN ORDER, EACH EMITS ITS LIST    │
└───────────────────────────────────────────────────────────────┘
```

Editing emits two forcing artifacts at handoff: the **§4 audit list** (one row per citation audited, pass/`flagged: <reason>` per §4 items 1, 2, 4, 5, 6) and the **voice audit surface-scan report** (§10 never-list hits + density-list overruns with line references). A handoff turn that does not emit both has not run the mode. A `[formatting mode]` entry without these artifacts is a gate violation (manifest §7.4). "I ran the audits mentally" is not the same as emitting the lists; the lists **are** the audits. Per-pass lists (proper-noun consistency, paste-artifact, punctuation mechanics) are required in their respective passes; a pass that doesn't produce its list has not run.

## Steps

### Entry and structural-deviation check

1. **Announce entry.** First output of the turn: `Switching to [editing mode].` Name the section in one clause after the announcement: "editing section 2" / "editing the literature review" / "editing the full draft".

2. **Read `voice.md` in full.** The voice audit (pass 8) operates against the specific rules there; do not run it from memory. If `voice.md` is missing, stop and ask {{USER}} to run `sourced switch voice <name>` rather than guessing rules.

3. **Load the draft's citation log** (`<draft>.citations.json` adjacent to the draft). Passes 1, 2, 3 cross-reference by id; the log is the source of truth. If the log is missing for a draft with citations, stop and ask {{USER}} — do not reconstruct from memory or from draft text.

### Structural deviation (before the pass list)

4. **Detect structural deviation from the refined outline.** Detection is operational, not impressionistic:
   - Read the refined outline (sibling outline file if it exists, or the outline section in the working document).
   - List its section headings and the one-line purpose of each, in order.
   - List the same for the current draft.
   - Compare. Deviation is: any heading missing, reordered, renamed beyond trivial wording, or any draft paragraph asserting a claim the outline did not place.

5. **On detected deviation, do not fix at prose level.** Announce `Switching back to [refining mode] — structural deviation detected at <heading / paragraph>.` Name the specific mismatch. Refining realigns the outline and prose; re-enter `[editing mode]` only once the outline and prose agree. Structural fixes applied at prose level are expensive; the refining/editing boundary exists to prevent that cost from compounding — bypassing it is the single largest latent cost in the pipeline.

### The eight passes (in order)

Each pass operates on the section being edited. Passes that produce forced-field lists emit them in the running mode's report; an empty list (`no hits`) is a valid emission and required when the pass finds no issues. A pass that does not emit its list has not run.

6. **Pass 1 — ID validation.** For every `[@id]`, `@id`, `[@id, p. N]`, or `[@a; @b]` citation in the section, confirm the id resolves to an entry in the citation log. Unresolved IDs are errors: either the entry is missing (surface to {{USER}} and switch to `[research mode]` for the specific citation) or the id is mistyped (fix it). Also flag any **rendered citation strings** (`(Smith, 2010)`, `Smith (2010)`) that survived in source prose: these are legacy-draft regressions; surface them to {{USER}} before converting to `[@id]` / `@id` form and verifying each against the log. Rendered citations in source prose defeat the byline-discipline guarantee the system depends on. For every resolved id, re-run §4 audit item 3 (Byline), which includes the `retrieved_at` staleness check (see pass 2). If {{USER}} declines legacy conversion for this session, **every unconverted rendered-citation instance is a named blocker in the voice audit surface-scan report** (one entry per instance, `{line, rendered_string, mode_gap: pass 2/3 not run}`), AND the handoff turn opens with `Editing cannot advance to [formatting mode] until legacy rendered citations are converted. N instances pending at lines X, Y, Z.` — the editing → formatting gate is closed regardless of other audit state. Skipping passes 2 and 3 for unconverted citations is allowed only within the editing turn; it never compounds into a downstream gate pass.

7. **Pass 2 — §4 citation audit.** For every citation in the section, run the §4 audit against the current prose: scope (item 1), attribution (item 2), byline (item 3), inference (item 4), cherry-pick (item 5), plus synthesis (item 6) for multi-citation claims. **Emit the §4 audit list** — one row per citation; item 3 (byline) is recorded via `retrieved_at` updates on the log entry, not in this list.

   **Row grammar (canonical shape; `sourced check` I5 parses against this).** Each row is:

   ```
   <@id>: <item_1> ; <item_2> ; <item_4> ; <item_5> ; <item_6>
   ```

   Each item cell is exactly one of:
   - `pass` — audit item ran and found no issue.
   - `flagged: <one-line reason>` — audit item found an issue; resolution still pending.
   - `flagged → resolved: <action>` — audit item found an issue, resolved in this same turn (`action` is one of `prose revised`, `log updated`, `citation dropped`, `citation replaced with @<id>`, or a short equivalent).
   - `N/A` — permitted only for item 6 (synthesis) on single-source citations.

   No other cell values are valid. A row containing any `flagged: <reason>` (pending) closes the editing → formatting gate; only rows whose every cell is `pass`, `flagged → resolved: <action>`, or `N/A` pass the gate. Example rows:

   ```
   smith-2010-001: pass ; pass ; flagged: prose says "always" where exact_quote says "sometimes under Z" ; pass ; N/A
   chen-2021-003: pass ; pass ; flagged → resolved: prose revised to preserve hedge ; pass ; pass
   ```

   Forced re-verification: for any entry whose `retrieved_at` is stale per `~/.claude/citations/schema.md` §Staleness, OR whose `retrieval.printed_page_observed` is missing or equals `"not visible"`, re-open the source and, against the rendered passage, overwrite `retrieval.verification_trace` with the first-20 and last-20 characters of `exact_quote` copied from the rendered view. If the rendered passage no longer matches `exact_quote` character-for-character, do not proceed with the pass — surface to {{USER}} as a **source-drift incident** with the mismatching characters named. On successful re-verification, update `retrieved_at` and the relevant retrieval fields.

   A row with any `flagged` result requires either a prose revision, a log-entry update, or a re-verify pass before the mode advances. Pass 2 is not optional; it runs every time `[editing mode]` engages a draft with citations.

8. **Pass 3 — Partial-entry recheck.** For every `verification_status: "partial"` entry whose citation appears in the section, recheck the prose against the partial-entry constraint in `~/.claude/citations/schema.md`. The check runs fresh against the current prose: if the prose has drifted past the pasted passage into inference or generalization, or the claim has become load-bearing since refining, revise or flag to {{USER}}. Partial entries are the most common place drift enters a draft unnoticed.

9. **Pass 4 — Grammar.** Mechanics before voice. Reread each sentence looking specifically for:
   - Tense and mood consistency across clauses of one sentence.
   - Sequence of tenses across report verb and commentary (past report → past or timeless commentary, not present-indicative assertion).
   - Subject-verb agreement where subjects are compound or nested.
   - Every direct quote has an attributing verb (`said`, `argues`, `writes`) in the governing clause; a quote cannot serve as the main clause's predicate on its own.
   - Quoted fragments grammatically continuous with the surrounding sentence (case, tense, number fit).
   - Pronoun antecedents unambiguous.
   - Comma usage before coordinating conjunctions (no comma before `but`/`and`/`or` when the subject is shared).
   - Restrictive vs non-restrictive clauses (that/which, comma use).
   - Dangling and misplaced participles, especially when the subject is a scholar and the sentence slips into an abstract-noun subject.
   - Number agreement with collective nouns (`data`, `criteria`, `phenomena`).
   - Parallel structure in conjoined phrases.

   The target is **unambiguity**, not rule compliance. Flag any sentence that parses two ways even if technically well-formed.

10. **Pass 5 — Proofreading.** After grammar, before AI-tell. Produce each of the three lists below as a **forced field**; a pass that doesn't emit its lists has not run. Empty lists (`no hits`) are valid emissions.

    - **Proper-noun consistency list.** For every proper noun occurring more than once in the section, compare each occurrence to its first occurrence character-by-character. Emit `{proper_noun, line_first, line_current, chars_differing}` for every mismatch. When non-empty, restore from the citation log's `exact_quote` (authoritative) or ask {{USER}} for the correct form.
    - **Paste-artifact list.** Scan for character substitutions that indicate pasting through an application that mangled Unicode (`â` where `ȧ` is expected, stray combining marks, smart-quote curl inversions, Latin-1 to UTF-8 mojibake). Emit `{line, span, suspected_original, confidence}`. Restore from `exact_quote` or ask {{USER}}.
    - **Punctuation mechanics list.** Flag spacing errors around dashes and quote marks, hyphen-vs-en-dash confusions in page ranges, and inconsistent quote-curl direction. Emit `{line, issue, suggested_fix}`.

    Pass 5 runs before §10 because mechanics fixes can introduce cadence changes that the §10 pass then evaluates in final form.

11. **Pass 6 — AI-tell (§10).** For each paragraph in the section, scan for the patterns in §10. **Read `docs/modes/writing.md#never-list`** for the full pattern prose and each rule's restructure guidance — this is the single source of truth for the never-list rationale; do not operate from memory of the manifest's compact ID list.

    **1a-window fallback.** If `docs/modes/writing.md` is not yet present in the project (phase-2 commit-1a ships editing.md / research.md / finetuning.md; writing.md ships in commit-1b), halt pass 6 and surface to {{USER}}: `Pass 6 cannot run — docs/modes/writing.md is not yet installed. Run \`sourced update\` or defer editing until commit-1b lands.` Do not substitute the manifest §7.6 compact ID list for the writing.md never-list prose; the compact list has canonical IDs but not restructure guidance, and pass 6's "Restructure, don't retokenize" rule is load-bearing.

    When writing.md is present, apply:

    - **Never list.** Fail on sight. Apply **Restructure, don't retokenize** per writing.md: identify the sentence shape the pattern produces (mid-clause interruption, balanced pivot, rhetorical escalation, ornamental triad) and rebuild around a different shape. Swapping punctuation while preserving the shape fails the audit and leaves the AI rhythm intact. A period between X and Y does not count as structural change for `not-x-but-y`; neither does a single bridging sentence (see writing.md cross-sentence-retokenization rule).
    - **Density list.** Per-draft budget check: "In this way," "we come to see," "for X… for Y…" parallel constructions, stacked participials — each acceptable once per essay, AI-ish when stacked. Flag any term appearing three or more times or any two sibling stacked.
    - **Exemptions.** If `voice.md` carries a `## §10 exemptions` bullet with a canonical ID from manifest §7.6 (`em-dashes`, `not-x-but-y`, `ornamental-triads`, `throat-clearing-openers`, `demonstrative-openers`, `ornamental-compounds`), suspend that rule for {{USER}}-voice prose only. §10 still applies to prose generated on {{USER}}'s behalf that is not this voice's output (`[red team mode]` counter-phrasings, framework meta-commentary). The direct-quotations carve-out (manifest §7.6, root CLAUDE.md §10) remains independent — §10 patterns inside a double-quoted span or block quote are skipped regardless of exemption state.

    Conflict surfacing: if `voice.md` and §10 conflict without an exemption bullet for the matching canonical ID, surface the conflict on first occurrence rather than resolving silently (manifest §7.6).

12. **Pass 7 — Quote-density.** Mirror of `[writing mode]`'s paraphrase default. For each paragraph in the section, count direct-quote words against total words; if direct-quote words exceed ~15% of the paragraph, flag for paraphrase. Also flag any two adjacent sentences where both carry a direct quote. A paragraph over quota is a signal that the writer reached for direct quotation where paraphrase would compress and let the prose voice carry. Convert non-load-bearing quotes to paraphrase per `[writing mode]`'s 4-item test (wording-as-object-of-analysis, qualifier-would-be-lost, authority-rests-on-formulation, will-push-against-wording — full procedure in `docs/modes/writing.md` §Paraphrase default), then re-run the §4 audit against the paraphrased prose using `exact_quote` and `surrounding_context` as ground truth.

13. **Pass 8 — Voice audit.** For each paragraph in the section, apply `voice.md`'s connectedness and flow rules as a discrete pass (separate from the citation, grammar, AI-tell, and quote-density audits):
    - Sentence connectedness (handoff connectives between sentences).
    - Paragraph flow (transition to the next paragraph, not a closing verdict).
    - Information pacing (elaboration sentences between claim-dense ones).
    - Concept setup (technical terms framed on first use).
    - Exploratory vs verdict tone (verdicts reserved for conclusions).

    Revise paragraphs that fail any check. Voice runs last so cadence is easier to adjust after mechanical fixes are in place. Voice does not override pass 4's unambiguity flag — if a voice choice would reintroduce an ambiguity flagged in grammar, restructure the sentence rather than accept it. Voice may diverge from a minor mechanical preference (comma placement, clause order) when the author's register demands it, provided no ambiguity is reintroduced.

    **Preserve {{USER}}'s voice. Don't flatten it into institutional prose.**

### Handoff to formatting

14. **Voice audit surface-scan.** Before asking {{USER}} to advance, run a final surface scan over the edited draft for §10 never-list hits and density-list overruns (em dashes, "not X but Y" variants, stacked "In this way" / "we come to see" beyond the per-essay budget, quote-density flags, sentence-initial AI adverbs). **Emit the voice audit surface-scan report** — a list of hits with line references and per-hit context.

15. **Blocker discipline on hits.** If the report is non-empty, do not silently ship. Present it as a blocker: `Voice audit found N hits at lines X, Y, Z: [list with context]. Address before format, or mark as intentional?` Force engagement; force a reason. Silence is not an override; `mark as intentional` from {{USER}} is the only override path, and the acknowledgment is logged in the handoff.

16. **Handoff gate.** Once the audit list is clean (zero unresolved `flagged` rows) and the voice audit surface-scan report is emitted (empty or explicitly-acknowledged), present the edited section and ask: `Editing is at a place I'd call complete. Ready to format, or more editing?` On `ready`, ask for the paste target. On `more editing`, stay in `[editing mode]`. **Never skip the handoff** — a silent transition to formatting bypasses the artifact gates.

17. **Announce return.** On gate pass with paste target named: `Switching to [formatting mode].` On {{USER}} request for more editing: stay in editing until explicit next-turn handoff. On {{USER}} request to return to refining (e.g., structural issue surfaced mid-edit): `Switching to [refining mode].`

## Annotated-bib project variant

In annotated-bib projects (project type `annotated-bib`), the eight-pass audit applies to annotation prose with two modifications:

- **Pass 7 (Quote-density) does not apply.** Quote density is a paragraph-level metric; annotations are per-entry blocks with hard word budgets (150–250 per the annotation shape in `~/.claude/citations/schema.md` §Annotation), and reaching for direct quotation inside an annotation is already constrained by `[annotated-bib mode]` phase 1's "at most one short phrase from `exact_quote`" rule. Skip pass 7 entirely; do not emit an empty quote-density list.
- **Pass 8 (Voice audit) is reduced.** Apply `voice.md ## Iron rules` and the exploratory-vs-verdict tone check per annotation. Do not apply sentence connectedness, paragraph flow, information pacing, or building-arguments rules — all of them assume multi-paragraph prose that annotations don't produce.

Passes 1–6 apply unchanged. §4 synthesis (item 6) only fires when an annotation cross-references another entry via `[@id]`.

## Red Flags

If you catch yourself thinking any of the following, stop and check:

- *"I'll fix this structural issue at prose level instead of sending it back to refining."* — No. Step 5 is load-bearing; the refining/editing boundary exists exactly here.
- *"The §4 audit is ceremonial; {{USER}} won't read the list."* — No. The list is the forcing artifact for the formatting handoff (manifest §7.4). Without it, the gate has not been satisfied.
- *"I ran the audits mentally; I can describe the results."* — No. The audits ARE the lists. A descriptive summary without the rows doesn't emit the artifact.
- *"This section's structural deviation is minor; I'll note it but keep editing."* — No. Any deviation returns to refining. "Minor" is the rationalization; deviation is a gate trigger regardless of magnitude.
- *"The proper-noun consistency list is empty — I'll skip emitting it."* — No. Empty lists are required emissions. They distinguish "ran and found nothing" from "didn't run."
- *"The §10 hits are stylistic disagreements — I'll leave them for {{USER}}'s judgment."* — No. §10 hits either get restructured or get `mark as intentional` from {{USER}} explicitly. Silent retention is not allowed.
- *"This quote is slightly over 15% but it's powerful — I'll keep it."* — Paraphrase default applies. Powerful-feel is not a carve-out; load-bearing wording (the 4-item test) is.
- *"Running all eight passes for a one-paragraph edit is overkill."* — Run them anyway. The cost of an eighth pass on one paragraph is seconds; the cost of a skipped audit is a silent §4 violation shipped to {{USER}}.
- *"`retrieved_at` is only a little stale — not worth the re-verify."* — Stale means stale. Re-open the source, update the timestamp, move on. Estimating staleness is the rationalization; the schema sets the threshold.
- *"The paste-artifact I see is obvious; I'll fix it without adding to the list."* — Fix it AND add the entry to the list. The list is the auditable trail.

## Rationalizations

Pre-empt the excuses. Each row is an excuse you might generate and the correct response.

| Excuse | Reality |
|--------|---------|
| "Refining already audited the citations; running §4 again is redundant." | Refining audits the outline against the log (claim-level drift). Editing audits the prose against the log (sentence-level drift). The two catch different failure modes. Run both — that's why the mode system separates them. |
| "Pass 5's lists feel bureaucratic for a clean section." | Bureaucracy is the wrong framing. The lists are cheap to emit when empty; they are the only way to distinguish "passed" from "skipped." Future audits rely on the shape, not the absence of hits. |
| "The §10 em-dash is part of {{USER}}'s voice — I won't flag it." | Check `voice.md` for a `## §10 exemptions` bullet with `em-dashes` as the canonical ID. If present, suspend the rule for {{USER}}-voice prose. If absent, the em-dash is a hit regardless of how familiar the pattern feels — silence is not permission (manifest §7.6). |
| "The §4 audit flagged one citation; I'll revise the prose and skip emitting the flagged row." | No. The flagged row is part of the audit trail — it records that the audit fired, what the finding was, and that the resolution happened. Silent fixes defeat the artifact's purpose. Keep the row, mark it `flagged → resolved: <action>`. |
| "The voice-audit surface scan overlaps with pass 6 — I'll just cite the pass 6 results." | The surface scan is the handoff artifact for manifest §7.4's editing → formatting gate. Pass 6 is the mid-pipeline audit; the surface scan is the artifact at the boundary. Different consumers. Emit both. |
| "I detected structural deviation but {{USER}} is in a hurry — I'll patch at prose level and flag it after." | Patching at prose level creates the exact cost the refining/editing boundary exists to prevent. `Switching back to [refining mode]` is the correct move regardless of time pressure. {{USER}} can accept the refining cost or accept a known-broken handoff; silently patching is the option that's not on offer. |
| "The byline is in the log and I verified it last session — don't need pass 2's re-verify." | If `retrieved_at` predates the current conversation or is missing, it's stale per §Staleness. "Last session" is a different session. Re-open the source, re-read the cited passage, update the timestamp. Memory of a previous verification does not update the log. |
| "Paste-artifact list found one stray mojibake character; trivial — not worth flagging." | Trivial-to-fix does not mean trivial-to-skip. Emit the entry, apply the fix, move on. The audit discipline is consistent emission, not per-entry judgment about importance. |
| "The rendered-citation regression (legacy `(Smith, 2010)` in source prose) — I'll just convert it silently." | No. Pass 1 explicitly requires surfacing to {{USER}} before converting. Silent conversion bypasses the byline-discipline guarantee; `[research mode]` re-verification is part of the conversion path, not an optimization. |
| "The refined outline doesn't exist as a separate file, only as a section in the working document — structural-deviation check doesn't apply." | It does. Read the outline section of the working document and compare against the prose section. The check is about drift, not file layout. An absent outline means `[refining mode]` didn't run — refuse the editing entry. |
| "`retrieval.printed_page_observed` equals `'not visible'` for a handful of entries — that's schema-allowed." | Schema-allowed at log time, yes. At editing time, `'not visible'` is a trigger for forced re-verification (pass 2): re-open the source, attempt to capture the printed page, update the field. The value is allowed where no page was observable; editing re-tests that judgment. |
| "The voice audit surface-scan is long and slows the handoff — I'll summarize the top hits." | Do not summarize. Emit every hit with its line reference. A summary loses the per-line evidence that {{USER}} uses to decide `fix` vs `mark as intentional`. Length is not a cost; selective reporting is. |
| "Pass 7 (quote-density) overlaps with `[writing mode]`'s paraphrase default — redundant." | Writing applies paraphrase default at draft time; editing re-tests it against the finished prose. The two catch different failures (missed conversion at draft time vs drift during revision). Run both. |
| "The draft's quoted-span markers are block-quote indentation only — pass 6 should treat the spans as generated prose because there's no surrounding double-quote." | No. `[editing mode]` skips span-level §10 matches whose surrounding markers identify them as direct quotations — **double quotation marks enclosing the span OR block-quote indentation** (manifest §7.6 direct-quotations carve-out). Block-quote indentation alone qualifies. Re-read the manifest rule. |
| "The prose changed punctuation from the source's em-dash to a comma inside a block quote — that's fine because it's a readability fix." | Silent punctuation change inside a quoted span is a §4 *Quote verbatim* violation regardless of motive. Use the bracketed editorial note per §4's no-ellipsis-trickery discipline (`adequate to them [,] i.e., the state`), or restore the em-dash. Readability is not an override. |
| "The section has zero citations — I can skip passes 1–3." | Confirm the claim first (sections with zero citations are rare; often a citation was silently dropped). If genuinely citation-free, passes 1–3 emit empty lists (`no hits`). Empty is a valid emission; skipping is not. |
| "One pass feels unnecessary given what I just ran — I'll fold it into the next pass." | Collapsing passes is the exact failure the ordered list exists to prevent. Each pass has a distinct audit semantics (ID lookup vs claim audit vs mechanics vs voice); collapsing produces silent cross-contamination where a voice fix masks a grammar flag, or a §10 restructure introduces a byline issue. Run them separately. |
| "I'll run passes 6 and 8 from memory of `voice.md` — I read it an hour ago." | Re-read `voice.md` at step 2 on every entry. Memory from an earlier session (or even an earlier pass on a different section) drifts; the file is the authority. |
| "`[refining mode]` already ran the §4 audit and emitted its list — editing can skip pass 2." | No. Refining audits the outline against the log (the claim is X; does the source support X?). Editing audits the prose against the log (the sentence says Y; does the source support Y? does Y preserve the qualifier?). The two audits operate on different input artifacts. Run pass 2 against the prose. |
| "I hit a structural-deviation trigger at pass 5 — I'll finish the remaining passes and switch back to refining at the end." | No. Structural deviation triggers an immediate `Switching back to [refining mode]`. Continuing passes 6–8 on a structurally-deviated section wastes audit effort and produces artifacts that won't match the realigned prose. Switch now. |
| "The voice audit surface scan report is empty, so I'll skip emitting it." | Empty is a valid emission; skipping is not. The handoff gate requires the report's presence, not its non-emptiness. An empty scan says "audited, zero hits"; a missing scan says "didn't audit." Those are different states. |
| "{{USER}} said `mark as intentional` for three §10 hits in a prior turn — those persist to the handoff without re-acknowledgment." | Re-emit the `mark as intentional` acknowledgments inline in the handoff report so the record is a self-contained artifact. Relying on prior-turn memory for the record breaks the artifact's standalone auditability. |

## Quick Reference

```
ENTRY:   Switching to [editing mode]. editing <section>.

STEP 0:  Read voice.md (full). Load citation log.

STEP 1:  Detect structural deviation from refined outline.
           Deviation → Switching back to [refining mode]. Halt editing.

PASSES (in order; each pass emits its list):
  1. ID validation.          List: unresolved IDs, rendered-citation regressions.
  2. §4 citation audit.      List: §4 audit list (one row per citation).
                             Forced re-verify: stale retrieved_at / "not visible" pages.
  3. Partial-entry recheck.  List: partial entries where prose has drifted.
  4. Grammar.                Flag: ambiguity (unambiguity is the target).
  5. Proofreading.           Lists: proper-noun consistency / paste-artifact / punctuation.
  6. AI-tell (§10).          Read docs/modes/writing.md#never-list. Restructure, not retokenize.
                             Honor voice.md ## §10 exemptions (canonical IDs only).
  7. Quote-density.          Flag: paragraphs > ~15% direct-quote, adjacent-quote sentences.
                             (Skip in annotated-bib projects.)
  8. Voice audit.            Apply voice.md rules discretely. Preserve {{USER}}'s voice.
                             (Reduced in annotated-bib projects.)

HANDOFF:
  Run voice audit surface-scan. Emit report (list of §10 + density hits with line refs).
  Non-empty → present as blocker: "fix, or mark as intentional?"
  Clean → present section, ask: "Ready to format, or more editing?"
  On ready, ask paste target.
  On format: Switching to [formatting mode].

FORCING ARTIFACTS (required at handoff):
  - §4 audit list
  - Voice audit surface-scan report
```

## What this mode does NOT do

- **Draft new prose.** Substantive additions belong in `[writing mode]`. Editing audits existing prose; it does not write new content.
- **Structural realignment.** Refining handles that. Editing detects deviation and punts — it does not relocate claims, rewrite headings, or re-order sections.
- **Fabricate citations to cover unsourced claims.** If a claim needs a source and none exists, surface to {{USER}} and switch to `[research mode]` via the unsourced-claim auto-trigger (manifest §7.4).
- **Render APA / MLA / Chicago strings.** Formatting does that. Editing operates on `[@id]` / `@id` references; rendered citation strings in source prose are regressions that pass 1 flags.
- **Local single-span substitutions.** That's `[finetuning mode]`. Editing is a whole-draft audit with gated handoff; it does not replace finetuning's alternatives-before-selection discipline.

## Exit Gates

**Allowed transitions (from editing):**
- → `[formatting mode]`. Gate: §4 audit list clean + voice audit surface-scan report emitted (empty or explicitly-acknowledged) + paste target named. Use `Switching to [formatting mode].`
- → `[refining mode]` on structural deviation detected at step 4–5. Announce `Switching back to [refining mode] — structural deviation detected at <heading / paragraph>.`
- → `[research mode]` on (a) unresolved ID (pass 1), (b) source-drift incident (pass 2 character mismatch), or (c) unsourced-claim auto-fire surfaced mid-pass (manifest §7.3 / §7.4 `* → research (auto)` row: a claim without a source turns up during any pass). Auto-trigger per manifest §7.3; return to editing once the gap is resolved with `Switching back to [editing mode].`
- → `[finetuning mode]` on {{USER}}-initiated local-substitution ask surfaced mid-edit. Announce the switch; resume editing after selection.
- → `[collaborative mode]` if {{USER}} pauses the edit to discuss something meta (scope, approach, autonomy level). Explicit switch only; editing does not auto-downgrade.

**Forbidden transitions:**
- → `[formatting mode]` without the two forcing artifacts. Gate violation; halts with the missing-artifact named.
- → `[writing mode]` direct. Writing precedes editing in the pipeline; returning to writing means the ask is substantive addition, which requires `[refining mode]` in between to update the outline.
- → `[outlining mode]` / `[plan mode]` direct. Upstream of writing; reaching them from editing implies the ask is scope-level, which routes through `[refining mode]` or `[collaborative mode]` first.
- → `[annotated-bib mode]` direct. Annotated-bib is a project-type-gated drafting mode; entering it from editing implies the section is in the wrong project type.

## See also

- `CLAUDE.md §4` — synthesis integrity iron rule. Pass 2 audits against this; items 1, 2, 3, 4, 5, 6 are defined there.
- `CLAUDE.md §7.2` — explicit triggers (source of truth).
- `CLAUDE.md §7.3` — implicit / auto-fire triggers, including stale-byline at write time and unsourced-claim auto-fire.
- `CLAUDE.md §7.4` — mode-to-mode gate table; the editing → formatting gate and its forcing artifacts.
- `CLAUDE.md §7.5` — forcing artifact definitions: §4 audit list and voice audit surface-scan report.
- `CLAUDE.md §7.6` — precedence rules, canonical §10 ID list, direct-quotations carve-out.
- `CLAUDE.md §8` — citation log + three moments; Moment 1 schema loaded at step 0.
- `docs/modes/writing.md#never-list` — full §10 never-list prose, density list, restructure guidance. Read at pass 6.
- `docs/modes/writing.md §Paraphrase default` — 4-item test used at pass 7.
- `docs/modes/research.md` — target for pass 1 unresolved-ID handoff and pass 2 source-drift handoff.
- `docs/modes/refining.md` — target for structural-deviation handoff at step 5.
- `docs/modes/formatting.md` — target of editing → formatting handoff; consumes both forcing artifacts.
- `~/.claude/citations/schema.md` §Staleness — `retrieved_at` staleness threshold used at pass 2.
- `~/.claude/citations/schema.md` §Annotation — annotation shape referenced by the annotated-bib variant.
- `voice.md` — voice rules loaded at step 0 and applied in passes 6 and 8.
