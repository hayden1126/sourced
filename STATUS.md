# STATUS: sourced

> Living state. Update at the end of every working block so a fresh session can resume from here after `/clear`.

Last updated: 2026-07-03
Branch / worktree: main

## Done

- 2026-07-03 cleanup pass, commit range `74c7f19..9efa9e0` (7 PRs, all merged with CI green):
  - PR #37 `b5c6207` — test unification: bare `pytest` runs everything (260 tests); parity goldens pinned to pandoc 3.1.3 via `tests/parity/PANDOC_VERSION`; bash runners deleted.
  - PR #38 `19e4358` — GitHub Actions CI (ruff + py3.10/3.13 matrix with pinned pandoc) + 15 ruff findings fixed.
  - PR #39 `9de1898` — mechanical doc fixes (broken links, flat paths, counts, wrong diagram annotations).
  - PR #40 `292907d` — `docs/superpowers/` collapsed into `docs/archive/` with Shipped banners.
  - PR #41 `e15f4e3` — dead code removed ({{VOICE}}/{{STYLE}} render paths), `facts.yml` and `audit_deferred.md` deleted, stale `install.sh` mentions swept.
  - PR #42 `d64b336` — ARCHITECTURE/MODES/INSTALL content refresh; canonical-source policy established.
  - PR #43 `4c48354` — VISION.md authored; ROADMAP re-triaged (Serves tags, statuses match PRs).
- Issue tracking migrated to GitHub Issues #29-#36; local `issues.md` and `audit_deferred.md` retired.
- Git admin: 3 merged remote branches deleted; `legacy/install-sh-final` tag deleted (pointed at `aa85da3ca883498f505a9057d276e2fb86f37b58`).

## In flight

- Nothing half-done. Clean boundary: cleanup complete, tree green.
- Next concrete step: pick the next development thread from ROADMAP's re-triaged `next` set (CLI phase-5 tail: doctor / --format=json / completion / config migration; annotated-bib phase 3; peer review mode; babble-as-ideation; extract-pdf-highlights; extract-jstor).

## Blocked / decisions needed

- Next-thread choice is Hayden's call (deliberately deferred out of the cleanup). Input for the call: issue #32 (mental-verb audit) is the only `priority:high` item, and a real paper session would generate the signal that parked/observe issues #29, #30, #31, #33 are waiting on.

## Notes for next session

- Verification target: `pytest` (260 tests; parity needs pandoc 3.1.3 on PATH, warns on version drift, skips without pandoc). `ruff check src tests` and `python3 -m sourced check --invariants` (11/11) should both be clean.
- CI runs on every PR and push to main; pandoc version in CI is read from `tests/parity/PANDOC_VERSION` with a hard assertion. Bumping the pin is a deliberate standalone PR (issue #35).
- Canonical-source policy (ARCHITECTURE intro): shipped bundle under `src/sourced/data/` owns protocol text; repo docs link, never restate. Keep new doc edits on that side of the line.
- ROADMAP entries now require a `Serves:` tag naming a VISION.md non-negotiable (or `ergonomics`); the contributing template at the bottom of ROADMAP.md has the format.
- CI actions annotate a Node 20 deprecation warning (checkout@v4, setup-python@v5, ruff-action@v3); harmless today, bump action majors whenever it starts failing.
