# Mental-verb audit of the shipped bundle

Date: 2026-07-03. Closes issue [#32](https://github.com/hayden1126/sourced/issues/32). Point-in-time record: line numbers reference the bundle as of the commit this file lands in.

## Method

Grepped every `.md` under `src/sourced/data/` (32 files) for the mental-verb vocabulary: verify, confirm, cross-check, re-verify, audit, re-read, reread, check, re-check, ensure, make sure, double-check, review, inspect, examine, consider, remember, keep in mind, be careful. 450 matching lines. Each hit was classified:

- **(a) genuine mental-verb rule**: an instruction to perform an internal act, no artifact forced at the instruction site (~20 hits).
- **borderline**: the verb is silent but a forcing artifact exists downstream or nearby (~30 hits).
- **(b) already-artifacted**: the sentence forces a field, list, halt, flag, or validator output (~180 hits).
- **(c) not a rule**: prose examples, headings, rationalization tables, references to the `sourced check` CLI, metadata (~220 hits).

## Conversion principle

Convert only where skipping the verb produces output indistinguishable from doing it (invisible failure), especially across an agent or session boundary. If skipping already yields a visible anomaly (missing field, failed halt, malformed list), leave the verb and record the downstream artifact here. Prefer emissions whose content is spot-checkable (copy the count, name the ID) over bare counters: a self-reported "done" line is the same silent assent one level up.

The bundle was already ~90% artifacted (the 2026-04-20 fixes, the editing pass lists, the `retrieval.*` fields). This audit produced 9 surgical conversions, 1 follow-up issue, and left everything else with a recorded rationale.

## Conversions made (9)

| # | location | verb | form | conversion |
|---|---|---|---|---|
| 1 | `templates/CLAUDE.md` §6 ("Re-read the autonomy level...") | re-read | 1 | Restate the level at each of the three firing points (plan-mode entry restate, refining sign-off, any §5 ask). A firing point that does not state the level has not consulted it. |
| 2 | `templates/CLAUDE.md` §8 ("cross-check prose against each entry") | cross-check | ref | Names the artifact: the cross-check is editing Pass 2 and emits its row list. |
| 3 | `docs/modes/writing.md` step 3 (re-read Never-list on entry) | re-read | 1 | Step closes with a load line: `never-list: <N> entries, first <id>, last <id>`, copied from the file. Disagreement with the file is a failed load. |
| 4 | `docs/modes/writing.md` per-sentence audit checklist | check | 3 | Emit `parent-audit: <k> hits (<check names>)` or `parent-audit: no hits` per section. A skipped audit previously looked identical to a clean one, across the parent/drafter agent boundary. |
| 5 | `docs/modes/editing.md` Pass 4 (grammar) | reread | 3 | Emit one `{line, clause, issue}` row per hit, empty list valid. Pass 4 was the only editing pass with no emitted list. |
| 6 | `docs/modes/outlining.md` step 2 (confirm the brief) | confirm | 1 | Open the outlining turn with a three-line restate: thesis, scope, audience. An outline emitted without the restate has not read the brief. |
| 7 | `docs/modes/refining.md` step 3 (re-read the brief) | re-read | 1 | Step closes with `autonomy: <level>; question: <one clause>`. |
| 8 | `docs/modes/refining.md` step 4 (iterate until clean) | reread | 3 | Emit `refine-loop pass N: <k> hits (...)` or `no hits` per pass; sign-off package includes the pass lines. Checks 1, 2, 5, 6 previously revised silently (the §4 audit list only artifacts checks 3 and 4). |
| 9 | `citations/schema.md` §Author-field ("Verify it once... re-verify any time") | verify, re-verify | 1 | Rewritten to name the existing fields: logging-time verification is `author_evidence`; on-touch re-verification is a fresh `retrieved_at` plus the Pass 2 `verification_trace` overwrite. |

Form key: 1 = forced field, 2 = operational pattern-matcher, 3 = checkable output list, ref = names an existing artifact.

## Follow-up issue opened

**Reliability judgment (§3a) has no artifact** ([#45](https://github.com/hayden1126/sourced/issues/45)). §3(b) full-text verification is forced by the `retrieval.*` fields, but §3(a) reliability is still a mental verb at CLAUDE.md §3, research.md step 9, and source-finder.md step 3: nothing records why a source was judged reliable. Fix direction: a `source.reliability_basis` object required on `verified` entries, inspected by the merge protocol and eligible for the parent spot-check. Structural (touches the log format and the merge hard-fail list), so deferred per the issue's own scoping rule.

## Left as-is: class (a) and borderline hits, with rationale

| location | verb | disposition rationale |
|---|---|---|
| voices/{academic,casual,hybrid,journalistic,narrative,technical}.md iteration-loop block (academic:144-154 and equivalents; 6 copies + 6 snapshot mirrors) | reread, cross-check | Craft guidance, not a verification gate. The checkable subset (§10 never-list compliance) is already artifacted by the editing voice-audit report and the writing-mode parent audit (now conversion 4). The subjective questions ("does it earn its place") cannot name an artifact; a forced "pass N: no hits" line would be an unverifiable counter, the ritual output this audit exists to kill. Decision confirmed with the maintainer. |
| voices/academic.md:128 ("cut it and check whether the claim is weaker") | check | Decision heuristic inside the weak-adverbs rule; outcome caught by editing cut-pattern scans, which emit lists. |
| voices/journalistic.md:211 ("check house style") | check | Informational caveat, not a compliance rule. |
| CLAUDE.md:96 (read before citing) | read | Reading is forced by `exact_quote` + `retrieval.verification_trace`: neither can be produced without the rendered view. |
| CLAUDE.md:104 (synthesis across sources) | check | Item 6 (`synthesis`) in the §4 forced audit list; per-row result required. |
| CLAUDE.md:71 ("you verify two things") | verify | (b) full-text half artifacted by `retrieval.*`; (a) reliability half is the follow-up issue. |
| CLAUDE.md:156/:161 (collect or confirm the brief) | confirm | The brief file is the artifact; plan.md step 2 forces the read-back restate. |
| CLAUDE.md:364 (can't verify byline) | verify | Outcome-forcing already: reject and report. |
| CLAUDE.md:365 (verify byline at logging) | verify | `author_evidence` + provenance rules in schema.md are the artifact. |
| research.md:5 (apply §3 at every candidate) | verify | Overview prose; per-candidate artifacts are the retrieval fields. |
| research.md:96 (confirm reliability) | confirm | Reliability gap: follow-up issue. |
| research.md:112 (confirm byline, re-read passage) | confirm, re-read | The `retrieved_at` update is the artifact and the text says so. |
| writing.md:422 (check `retrieved_at` before `@id`) | check | Fires the §3 self-correction trigger, which forces a verbatim sentence. |
| formatting.md:39 (verify CSL resolves) | verify | Halt with named message is the outcome. |
| plan.md:30/:34-35 (confirm frame / gate) | confirm | Step :35 forces "State what is confirmed"; :30's artifact is the required user exchange. |
| prose-drafter.md:71/:89/:94 (check as you emit) | check, verify | Feed the forced `### Self-audit` and `### Flags` blocks; independently re-audited by the parent (conversion 4). |
| source-finder.md:31 (verify each candidate) | verify | Quote half artifacted by the verification trace; reliability half is the follow-up issue. |
| schema.md:189 (spot-check confirm) | confirm | Mismatch forces a `spot-check-failed` incident plus merge-report record. |
| annotated-bib.md:72 (check brief for ordering) | check | Outcome is ask-and-wait; unambiguous halt. |
| refining.md:57/:61 (checks 5, 7) | - | Covered by conversion 8's pass lines. |

## Class (b): already-artifacted (no edits, ~180 hits)

These are the pattern the conversions imitate. By file, with the forcing mechanism:

- **templates/CLAUDE.md** :108-122 (§4 audit list, forcing function), :167 (scope-delta list), :200, :256-257 (forced self-correction sentence), :271-304 (canonical IDs, `sourced check`), :366.
- **docs/modes/editing.md** (nine passes, each an empty-list-valid forced emission): :5-7, :27, :34, :60-91 (passes 0a-0e, 1-3), :103-105, :134-179 (passes 5-9), :189-196, :247-317.
- **docs/modes/refining.md** (the "list is the audit" mode): :5-7, :33-34, :45, :50-76 (checks + §4 row grammar), :87-98, :110-116, :152-171.
- **docs/modes/writing.md** :5-9, :25, :87, :102-103, :154-173 (self-audit consistency), :188-200, :250-278.
- **docs/modes/formatting.md** :25-65 (pre-flight checks 1-6, each halts and lists), :110-114, :152-161, :199-220.
- **docs/modes/research.md** :13-14 (forced verbatim sentence), :43 (false-positive check announces), :51, :89-113, :187-188.
- **docs/modes/plan.md** :22 (restate not optional), :34-35, :81, :109. **outlining.md** :26. **annotated-bib.md** :41, :134, :167, :222 (partial-entry list). **finetuning.md** :115, :126.
- **citations/schema.md** :28, :58 (design note stating the thesis), :63-66 (`verification_trace`, `per_entity_locators`, page-equality rule), :108-149, :183-220.
- **agents/source-finder.md** :31-58 (verification trace production), :88-120. **prose-drafter.md** :46-57, :83-96 (`### Self-audit`, `### Flags`, halt), :113 (`[VERIFY:]` token), :133-196. **voice-extractor.md** :40-54, :102-114, :167-175 (grep-back self-check, halt on miss), :222-303.
- **templates/docs/voice-extractor.md** :47-60 (caller-side iron-rule check, halt on miss), :76-85. **CLAUDE.d/20-project-type-annotated-bib.md** :52-53.

## Class (c): not a rule (no edits, ~220 hits)

- References to the **`sourced check` CLI command** (sourced-helper.md, voice footers, mode cross-refs, CLAUDE.d/README.md, SKILL.md).
- **Rationalization and red-flag tables** (arguing about a check, not issuing one): all mode bodies.
- **Voice prose examples** (sample sentences in academic, technical, narrative, casual, journalistic).
- **Cross-references, "See also" bullets, headings, banners** across mode bodies and agents.
- **Metadata**: style-card "Last reviewed" lines; `[VERIFY:]`/`[UNSOURCED]` token descriptions in the 5 style cards (real forced tokens, described, not instructed).
- **Brief template field prompts** ("check any that apply").

## Out of scope, recorded

- **No new Python invariant.** A "every pass names its emission" check is regex over prose: brittle, false-positive-prone. The new emissions are mode-body-level artifacts, deliberately not registered in manifest §7.5 (consistent with the editing pass lists).
- **Voice-loop hoisting** (6 physical copies) is issue [#34](https://github.com/hayden1126/sourced/issues/34) (template duplication), not this audit.
