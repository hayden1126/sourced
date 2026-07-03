# STATUS: sourced

> Living state. Update at the end of every working block so a fresh session can resume from here after `/clear`.

Last updated: 2026-07-03 (third block of the day)
Branch / worktree: main (feature branch `reliability-basis` pushed, PR #48 open)

## Done

- 2026-07-03 (block 3) reliability_basis, issue #45, commit range `8e1daf3..b8abcce` on branch `reliability-basis` (PR #48, OPEN at handoff, lint green, test matrix was pending):
  - `source.reliability_basis` added to the citation-log schema (new §Reliability basis section): `venue_type` (closed 9-value enum, no other/unknown, peer-review status folded into the venue class), `venue_basis` (one named checkable venue fact; generic vouching hard-fails), `author_credentials` (verbatim credential + where observed; escape literals "group author: <standing>" / "none stated"). Recency deliberately unrecorded (its inputs are already logged; a forced "recency ok" is a ritual counter).
  - Scope: required on every verified entry, list-shape included, {{USER}}-pasted partial exempt. Per-source, set-once; legacy entries backfilled on next source re-open, never from memory.
  - Enforcement: four new merge hard-fail bullets, lookup-only fix-in-place, spot-check extension (verifies the recorded facts exist; sufficiency stays Hayden's call), three forced merge-report surfacing lines. Deliberately NOT in CLAUDE.md §7.5 and no new Python invariant (retrieval.* precedent).
  - Producers in lockstep: source-finder step 3, research.md main-thread discipline (five forcing fields now), CLAUDE.md §3(a) names the artifact (golden snapshot regenerated same commit), emitter not-emitted list, VISION.md records #45 closed, ARCHITECTURE.md field enumeration (drift caught at handoff).
  - Also on main directly: `8e1daf3` (one-line STATUS cleanup, pushed).
- 2026-07-03 (block 2) mental-verb audit, issue #32, commit range `0fbae06..6f5e135` (PR #46, merged, CI green): audit record at `docs/archive/audits/2026-07-03-mental-verb-audit.md` (all 450 hits dispositioned), seven mode-body/schema conversions, two CLAUDE.md conversions + snapshot regen. Issue #32 closed; follow-up #45 opened (now implemented, see block 3).
- 2026-07-03 (block 1) cleanup pass, `74c7f19..9efa9e0` (PRs #37-#43, all merged): test unification under bare `pytest`, GitHub Actions CI, doc fixes, docs/superpowers archived, dead code removed, ARCHITECTURE/MODES/INSTALL refresh, VISION.md + ROADMAP re-triage. Tracking migrated to GitHub Issues #29-#36.

## In flight

- PR #48 (`reliability-basis`) open at handoff: lint passed, py3.10/3.13 test jobs were still pending. Next concrete step: confirm CI green, merge PR #48 (body says "Closes #45", so the issue closes on merge), then delete branches `reliability-basis` and `handoff-reliability-basis` once merged (deletion needs Hayden's OK; `/clean_gone` handles the [gone] ones after remote deletion).

## Blocked / decisions needed

- Next-thread choice after #48 merges is Hayden's call: the ROADMAP `next` set (CLI phase-5 tail: doctor / --format=json / completion / config migration; annotated-bib phase 3; peer review mode; babble-as-ideation; extract-pdf-highlights; extract-jstor), or a real paper session, which would now exercise both the #46 forced emissions and the new reliability_basis + merge-report lines, and generate the signal parked/observe issues #29, #30, #31, #33 are waiting on.

## Notes for next session

- Verification target unchanged: `pytest` (260 tests; parity needs pandoc 3.1.3 on PATH, warns on drift, skips without pandoc), `ruff check src tests`, `python3 -m sourced check --invariants` (11/11). All green locally on the feature branch at handoff.
- Design record for reliability_basis: PR #48 description + schema §Reliability basis itself. Ratified choices: 3 sub-fields over 2 (venue_basis is the anti-predatory prong), closed enum over an "other" bucket, verified-only scope.
- Bundle prose style: new text carries no em dashes (matches the #46 commits), even though older bundle text has them. Keep that for future bundle edits.
- Golden snapshot (`tests/cli/golden/__snapshots__/test_render_golden.ambr`) mirrors CLAUDE.md, briefs, voices, styles only; mode bodies, agents, and citations/schema.md are single-source. CLAUDE.md edits regen via `pytest tests/cli/golden/ --snapshot-update`, folded into the same commit.
- Canonical-source policy holds: bundle under `src/sourced/data/` owns protocol text; repo docs link, never restate (ARCHITECTURE.md's citation field enumeration is the one sanctioned summary; it gained the reliability_basis bullet in PR #48). docs/archive/ is exempt.
- CI actions still carry the Node 20 deprecation warning (checkout@v4, setup-python@v5, ruff-action@v3); bump action majors when it starts failing.
