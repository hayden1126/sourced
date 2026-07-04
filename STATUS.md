# STATUS: sourced

> Living state. Update at the end of every working block so a fresh session can resume from here after `/clear`.

Last updated: 2026-07-04 (quick-fix batch shipped)
Branch / worktree: main

## Done

- 2026-07-04 (block 2) quick-fix batch: the five issues the paper session made actionable, five PRs (#62-#66, all merged, CI green; issues #53, #58, #59, #60, #61 closed). Landing order #61 -> #59 -> #58 -> #60 -> #53. Plans were adversarially critiqued before implementation; the critics' catches are in the PR bodies.
  - PR #62 (issue #61): `sourced --version` appends live `git describe` state when running from the checkout, computed lazily via a custom argparse action (no subprocess on normal commands), frozen-stamp fallback everywhere else. Output: `sourced <stamp> (checkout <sha>[-dirty])`. 5 new unit tests + strengthened smoke test (TDD, red first).
  - PR #63 (issue #59): canonical page form "p. N" / "pp. N-M" in `location` and `printed_page_observed`; merge bullet compares the page token (Arabic or Roman), writes back canonical form, skips "not visible"; finder dispatch names the form.
  - PR #64 (issue #58): `retrieval.access_mode` (rendered-html / pdf-render / ocr-fulltext / snippet; snippet+verified hard-fails; ocr-fulltext force-surfaced via `ocr-fulltext-merged` report line + preferred spot-check + page-provenance rule) and `retrieval.context_trace` (first/last-20 of surrounding_context). Critic-added containment hard-fail: string-shape exact_quote must appear verbatim inside surrounding_context (kills placeholders at merge without opening the source). CLAUDE.md §3(b) admits OCR full text and bans snippets in the same commit as the golden regen.
  - PR #65 (issue #60): `conflict-of-interest` rejection category; `predatory` tightened to venue failures. No use-with-framing disposition (Hayden's call; `### Alternative framings` is the routing).
  - PR #66 (issue #53): optional `source.type` (closed 8-value enum), emitter rule 0 + §Explicit-only types + 2 worked examples + 2 reference fixtures; merge-time publication parseability check (4 tokens, `publication-parse-risk` report line, surfaced not blocking); doi_or_url discipline (canonical DOI there, retrieval URL in `retrieval.source_path`). Style-coverage claims verified against the vendored .csl files.
  - `sourced global-install` re-run after the batch; ~/.claude mirror is current (23 files).

- 2026-07-04 real paper session (the thread chosen from the three options below): full pipeline exercised end to end in a fresh project at `~/papers/cross-sex-empathy` (voice=hayden_essay, style=apa7), essay finished and rendered (md + docx). The essay is instrumental; the yield is framework evidence, distilled from `~/papers/cross-sex-empathy/notes/observations.md` into GitHub:
  - Comments posted on #53 (emitter mis-typed 3 of 12 bibliography entries; observe trigger met, recommend act), #29 (two evidence pieces: prose-drafter structural self-audit passed a content contradiction only the parent §4 check caught; a staged 3-persona blind reader review found reader-load and term-order defects no editing pass audits), and #51 (no direct voice failures logged and readers found no AI-signature, but section-scale density failures shipped despite sentence-level pacing rules: the decomposition diagnosis at a new level; staged reader review is a candidate fidelity-measure primitive).
  - New issues #58 (snippet-only access reaches "verified"; surrounding_context accepts placeholders), #59 (page-format canonicalization across finders), #60 (rejection enum lacks conflict-of-interest; Science got tagged "predatory"), #61 (--version stale on editable installs).
  - reliability_basis (#48) validated in the field: sibling-consistency rule caught real within-finder author-spelling drift; parent spot-check caught the snippet-verified entry (#58 is the fix for the gap it exposed).
  - Reader review verdict on the essay itself: unanimous minor revision; deliberately not applied (essay is a probe, not a product).
- 2026-07-03 (block 4) issue batch + quick fixes, commit range `66f06dd..3006c80` (PRs #55, #56, #57, all merged, CI green; issues #50, #52, #54 closed):
  - Issues #50-#54 filed. #51 is the big one: voice extraction v2 design spike (fidelity measure, representation, stylometry, coverage; in-repo vs standalone-tool fork is the spike's OUTPUT). It carries Hayden's core diagnosis, added after filing: the failure is decomposition, not shallowness (rules and atomized exemplars are marginals; voice lives in the joint distribution; cut patterns only subtract). #53 (source.type escape hatch) is observe-labeled: act when a real bibliography emits a wrong type.
  - PR #55 (issue #50): voice-extractor intake honesty. Per-file skip manifest in preflight, `### Sample stats`, and inside `under-sample` rejections, with a conversion pointer when skips dominate; floor runs on the matched set and reads 3-file consistently (was self-contradicting 3-vs-5); report format gained `### Excluded files` and `### Corpus contamination notes` (the dispatch doc referenced both; the agent never defined them); stale workflow step numbers fixed. Agents are single-source, no goldens touched.
  - PR #56 (issue #54): CI actions bumped to checkout@v7, setup-python@v6, ruff-action@v4.0.0. Gotcha: upstream ships no moving v4 tag for ruff-action, so the exact pin is deliberate; bump to a major alias when one appears. Node 20 deprecation warning gone.
  - PR #57 (issue #52): docs/VOICES.md truth-up to phase-3 behavior (multi_register split-halt semantics, `### Multi-register routing` report section at the real 85% threshold, 8 H2 sections / 3 rule axes, sibling `## §10 exemptions`, aphoristic-closures added to the canonical ID table, iron-rule step numbers). Same commit: all six skeletons' dangling `§ Multi-register corpora` refs now point at `§ Multi-register routing`; 6 goldens regenerated per convention.
  - Handoff drift pass: ARCHITECTURE.md voice-system paragraph and README.md voice-preservation line updated from the old "4 axes" framing to 8 sections / 3 rule axes + multi_register routing.
  - Outside the repo, same block: `~/.claude` global surface restored (it was missing entirely, config included). `sourced.config` copied from `~/.claude-old` (user=Hayden), `sourced global-install` mirrored 23 files, and the 4 custom voices (hayden_essay, hayden_personal, hayden-essay-2, leo-cc-essay) were copied from `~/.claude-old/voice/`.
- 2026-07-03 (block 3) reliability_basis, issue #45, commit range `8e1daf3..b8abcce` (PR #48 merged, handoff PR #49 merged, issue closed): `source.reliability_basis` (venue_type closed 9-value enum, venue_basis named checkable fact, author_credentials verbatim) required on every verified entry; four merge hard-fail bullets; producers in lockstep (source-finder, research.md, CLAUDE.md §3(a), emitter, VISION, ARCHITECTURE).
- 2026-07-03 (block 2) mental-verb audit, issue #32, commit range `0fbae06..6f5e135` (PR #46 merged): audit record at `docs/archive/audits/2026-07-03-mental-verb-audit.md`, nine conversions, snapshot regen. Follow-up #45 implemented in block 3.
- 2026-07-03 (block 1) cleanup pass, `74c7f19..9efa9e0` (PRs #37-#43 merged): bare `pytest` unification, GitHub Actions CI, docs restructure, dead code removed, tracking migrated to GitHub Issues.

## In flight

- Nothing half-done. Clean boundary: quick-fix batch merged, issues closed, mirror refreshed, tree has only this STATUS update to commit.
- Next concrete step: pick the next thread (see Blocked below).

## Blocked / decisions needed

- Next-thread choice is Hayden's call, options now: (1) the #51 spike, with real evidence attached (see the 2026-07-04 comment: the fidelity-measure question has a candidate primitive in staged reader review); (2) the #29 editing-critic design, which the paper session gave two concrete requirements (independent re-read of paraphrase vs exact_quote; staged reader-simulation pass after formatting); (3) the ROADMAP `next` set; (4) the remaining observe-labeled and parked issues (#30, #31, #33, #34, #35, #36).
- Observation-logging lesson for any future session: modes in flow do not log at-the-moment; evidence lands at gates (merge, format, post-review). #30/#31/#33 sections came back empty for this reason, not because nothing happened.

## Notes for next session

- Verification target: `pytest` (267 tests after the batch: 260 base + 5 version tests + 2 emitter fixtures; parity needs pandoc 3.1.3 on PATH), `ruff check src tests`, `python3 -m sourced check --invariants` (11/11). All green on main at the batch wrap-up (HEAD `20d0d65`).
- CI actions are current: checkout@v7, setup-python@v6, ruff-action@v4.0.0 (exact pin; no moving v4 major tag upstream yet).
- Golden snapshot policy unchanged: skeletons/voices/styles/CLAUDE.md are snapshotted, mode bodies and agents are single-source. Skeleton edits regen via `pytest tests/cli/golden/ --snapshot-update`, folded into the same commit (held in #57).
- `~/writing` is the evidence base for #50/#51: stale and slightly broken by Hayden's description, but its `config/voice.md` (hayden_essay, phase-3 render) is real extraction output, and its `hayden_personal` sibling reference resolves again now that the voice library is restored.
- Issue #51 is the deep thread: the decomposition diagnosis and the representation question (rules hold constraints, whole passages drive generation; scaled worked paragraphs or corpus retrieval at draft time). The spike's question 3 (needs real code?) leans yes since passage retrieval is mechanical.
- Bundle and repo-doc prose: no em dashes in new text (held through #55/#57); older text keeps them until touched.
- Canonical-source policy holds: bundle owns protocol text; VOICES.md and ARCHITECTURE.md describe and link (both re-verified against the agent this block).
