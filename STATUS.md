# STATUS: sourced

> Living state. Update at the end of every working block so a fresh session can resume from here after `/clear`.

Last updated: 2026-07-03 (second block of the day)
Branch / worktree: main

## Done

- 2026-07-03 (block 2) mental-verb audit, issue #32, commit range `0fbae06..6f5e135` (PR #46, merged, CI green):
  - `87209b5` audit record at `docs/archive/audits/2026-07-03-mental-verb-audit.md` (all 450 hits dispositioned; the record is the primary deliverable).
  - `03e53db` seven mode-body/schema conversions (writing never-list load line + parent-audit emission, editing Pass 4 grammar list, outlining brief restate, refining restate line + refine-loop pass lines, schema author-verification names its fields).
  - `2ff0224` two CLAUDE.md conversions (autonomy level stated at its three firing points; pre-edit cross-check names editing Pass 2's row list) + golden snapshot regen.
  - Issue #32 closed with a summary comment; follow-up #45 opened (reliability_basis, structural); VISION.md enforcement-principle link repointed from #32 to the audit record + #45.
- 2026-07-03 (block 1) cleanup pass, `74c7f19..9efa9e0` (PRs #37-#43, all merged): test unification under bare `pytest`, GitHub Actions CI, doc fixes, docs/superpowers archived, dead code removed, ARCHITECTURE/MODES/INSTALL refresh, VISION.md + ROADMAP re-triage. Tracking migrated to GitHub Issues #29-#36. Details in git and in the PR #44 handoff.

## In flight

- Nothing half-done. Clean boundary: audit merged, tree green, docs reconciled.
- Next concrete step: pick the next thread. Candidates: issue #45 (reliability_basis field; natural continuation of #32 but structural, changes the citation-log format and the merge hard-fail list) or the ROADMAP `next` set (CLI phase-5 tail: doctor / --format=json / completion / config migration; annotated-bib phase 3; peer review mode; babble-as-ideation; extract-pdf-highlights; extract-jstor).

## Blocked / decisions needed

- Next-thread choice is Hayden's call. With #32 done there is no `priority:high` item left; a real paper session would both exercise the new forced emissions (parent-audit line, refine-loop pass lines, grammar list) and generate the signal that parked/observe issues #29, #30, #31, #33 are waiting on.

## Notes for next session

- Verification target unchanged: `pytest` (260 tests; parity needs pandoc 3.1.3 on PATH, warns on drift, skips without pandoc), `ruff check src tests`, `python3 -m sourced check --invariants` (11/11). All green at handoff.
- Conversion principle for any future rule edits (from the audit record): convert only where skipping the verb is invisible, especially across agent/session boundaries; prefer spot-checkable emissions over bare counters; a forced "no hits" counter on subjective guidance is ritual, not enforcement. The voice iteration-loop was deliberately left as craft guidance.
- The new emissions are mode-body-level artifacts, deliberately NOT registered in manifest §7.5 (consistent with the editing pass lists; keeps I9 headroom).
- Golden snapshot (`tests/cli/golden/__snapshots__/test_render_golden.ambr`) mirrors CLAUDE.md, briefs, voices, styles only; mode bodies, agents, and citations/schema.md are single-source. Edit choreography lives in the audit-branch plan and the audit record.
- Canonical-source policy holds: bundle under `src/sourced/data/` owns protocol text; repo docs link, never restate. docs/archive/ is exempt (point-in-time records).
- CI actions still carry the Node 20 deprecation warning (checkout@v4, setup-python@v5, ruff-action@v3); bump action majors when it starts failing.
