# Deferred architectural decisions — pick up when ready

Two cross-cutting patterns surfaced by the 2026-04-21 `/audit` cycle that need one-time decisions rather than per-finding fixes. Each topic collects the evidence (findings, locations, costs) and lists the concrete options with tradeoffs. Blank **Decision:** line at the bottom of each topic.

**State as of 2026-04-21 (end of cycle 3 mini-pass):**
- Branch: `gdocs-smart-quotes-filter`. Cycle-3 mini-pass shipped in `5b2a18b` (F37 archive, F26 comma fix, 14 cycle-2 deferred decisions).
- Cycle-3 `/audit` surfaced 39 findings total. 14 cycle-2 decisions applied; 2 cycle-3 fixes applied; ~20 design-issue findings auto-deferred per `/audit-fix` class-routing. This file covers the two cross-cutting patterns from that set — the remaining ~15 single-file design-issues (e.g., "word-cap teethlessness") are individually minor and can be addressed one-by-one later or ignored.

---

## T1 — install.sh hardening: dedicated pass, or absorb incrementally?

Cycle-3 surfaced four open design-issue findings on `install.sh` in one audit pass, plus one blocker (already fixed as the comma change). That's higher density than any other file. Either `install.sh` is overdue for a consolidated hardening pass, or agents over-flag on shell scripts — this decision picks one interpretation.

### The open findings

- **F27** [sharp-edge]. Pandoc version parse (~L98-107): a single-integer version like `pandoc 3` would false-pass the <3.1 check because `minor=${pandoc_version#*.}` returns the unchanged string when no `.` is present. Defensive-only today — the upstream regex already requires `N.N` — but the parser itself is fragile if the regex ever relaxes.
- **F28** [sharp-edge]. `--update` awk (~L660-690) triggers on any `<!-- sourced:begin managed -->` occurrence in the file. A user who quotes the sentinel token inside their own prose (e.g., documenting the sentinel mechanism, or mentioning it in a brief) gets silent content corruption: awk toggles `skip=1` at the first match and eats everything until any `end` sentinel, which might be the real managed-block terminator much later.
- **F29** [sharp-edge]. `head -n1 "${TYPE_MARKER}" 2>/dev/null` on a whitespace-only or zero-byte marker produces `EXISTING_MARKER=" "` (or a soft-whitespace string) that passes `[[ -n ... ]]` but fails the type-comparison check, firing "refusing to silently switch" for what's effectively an empty marker. No trim.
- **F34** [nit]. `"${skill_dir}".[!.]*` dotglob pattern is nonportable without `shopt -s dotglob`; any dotfile-shaped asset in a skill (e.g. `.skillrc`) gets silently skipped on some bash configurations.

Plus one recent blocker-shape cleanup (already applied in `5b2a18b`):
- **F26 cycle-3** (shipped): poppler-missing aggregation prints comma-separated list now — cosmetic, but the kind of small-surface bug the density pattern produces.

### The background

`install.sh` is 782 lines, touches 7 path categories, enforces iron-rule discipline, handles project-type markers, validates CSL titles, does string-substitution rendering, and gates on prereqs. It's also the crux of every discussion around propagation-drift (the prereq list, shipped voices, etc. all flow through it). Every audit cycle surfaces 2-4 install.sh findings of varying severity. Historical issues: #3 `-ef` guard (fixed), #4 multi-line iron rule (fixed), #10 prereq check (fixed — cycle 1), #14 orphan cleanup (observe), #18 awk 2-space indent (observe). The file keeps growing and keeps accruing sharp edges.

### Options

**A — Dedicated hardening pass.** Block one session purely on install.sh: audit every `head`/`awk`/`grep`/`sed` invocation, add `shopt -s nullglob dotglob` where appropriate, convert `cat | head -n1` patterns to a trimmed helper, tighten the awk sentinel match to require start-of-managed-block position, add defensive assertions on version parsers. Cost: one 2-3 hour session. Benefit: closes the 4 open sharp-edges and preempts the next cycle's findings of the same shape. Risk: touching install.sh in bulk can introduce regressions that only surface at install time.

**B — Absorb incrementally via audit loop.** Each of the 4 findings is individually small; `/audit-fix` routes them to needs-judgment which you address one by one as they matter. F28 (the sentinel awk) is the only one with realistic user impact; the others are hardening against hypothetical failures. Accepts that install.sh will always have 2-4 sharp-edge findings per audit cycle and treats that as the file's natural signal-to-noise ratio. Cost: zero upfront. Benefit: no new risk. Risk: the findings pile up in `issues.md` observe rows without converging.

**C — Shrink install.sh by moving responsibilities into a `sourced` CLI.** The ROADMAP entry "Installable `sourced` executable on `$PATH`" (referenced in issues.md #14) would carry project-type marker handling, voice/style validation, and maybe the prereq check into a proper tool with its own test surface. `install.sh` reduces to bootstrap-only. Cost: significant — new ROADMAP item's worth of work. Benefit: install.sh stops being the framework's junk drawer. Risk: scope creep; the CLI becomes another place to maintain.

### Recommendation

**B for now.** The 4 open findings are real but not urgent — F28 is the only one that breaks a live use case (and it requires a user who quotes the sentinel token in their own prose, which is unusual). A hardening pass before the `sourced` CLI exists just pre-polishes a file that option C would retire. Revisit if the next cycle surfaces install.sh findings with user impact, or if you decide option C isn't happening.

**Decision:** C-broad — full decomposition (CLI carries project-type marker handling, voice/style validation, prereq check; install.sh shrinks to bootstrap-only). ROADMAP entry will need to be expanded from current S sizing. `superpowers:brainstorming` session in flight (2026-04-21) to scope properly before any code lands.

**Status: SHIPPED 2026-04-22 → 2026-04-25.** C-broad decision delivered across four phases:
- Phase 1 (PRs #19-#23, merged 2026-04-22) — Python CLI port, `install.sh` deleted, six subcommands replace it.
- Phase 2 (PR #24, merged 2026-04-24) — CLAUDE.md manifest extraction, `sourced check --invariants` rules I1-I10.
- Phase 3 (PR #25, merged 2026-04-24) — voice pipeline, prose-drafter, register-aware extraction.
- Phase 4 (PR #26, merged 2026-04-25) — per-project directory restructure, I11 invariant.

T1's four sharp-edge findings (F27 pandoc parse, F28 awk sentinel, F29 head trim, F34 dotglob) are all retired with `install.sh`. Ongoing CLI hardening continues under ROADMAP §Python CLI Phase 5 (CI, doctor diagnostics, json output, completion, config migration).

---

## T2 — Duplication-without-include: template-fragment system, or accept?

Three cycle-3 clusters (plus an infra-cluster) all point at the same missing abstraction: verbatim copies of prose fragments across multiple files with no include or generation mechanism. Deciding once gets multiple findings resolved at once.

### The evidence

**Cluster A (I3 propagation — styles, 5 files):**
- **F12** `templates/CLAUDE.md` §11 Style note lists only mla9/chicago17 but 5 styles ship — doc drift that keeps needing manual update when new styles arrive.
- **F17** `templates/styles/*.md` — 3-line "Special tokens" block duplicated across all 5 styles (apa7, chicago17-ad, chicago17-nb, ieee, mla9).
- **F18** `templates/styles/{chicago17-ad,chicago17-nb,mla9}/classical-abbreviations.md` — 3 byte-identical copies of the same file.

**Cluster B (I4 propagation — voices):**
- **F3 Agent 1** `agents/voice-extractor.md` L158 — "Rejection category `shipped-name-collision` ... matches a shipped voice (currently: academic, casual, technical, journalistic, narrative, hybrid)". Hardcoded list alongside the step-3 preflight list that I just made dynamic (F17 cycle-2). Same sync obligation.
- **F14 Agent 1** `templates/voices/*.md` — iron-rule preamble (3 paragraphs) duplicated verbatim across all 6 voice files.

**Infra (F33 Agent 2 cycle-3):**
- `tests/parity/{apa7,chicago17-ad,chicago17-nb,ieee,mla9}/run.sh` — 5 byte-equivalent per-style runners differing only in the leading comment. Adding a 5th paste target required editing 5 files.

### The shape of the cost

Today: **5+5+3+1+6+5 = 25 file-locations** carrying duplicated content. Every fix that touches the shared fact edits N files; every audit cycle finds the drift between any N-1 that got updated and the last one that didn't. That's exactly the recurrence pattern Layer 1 was built to surface (and it did — these are all cluster findings now). But Layer 1 only *surfaces* the duplication; the fix is still manual N-file updates.

### Options

**A — Install.sh-time template assembly.** `install.sh` reads shared fragments from `templates/fragments/*.md` and splices them into each style.md / voice.md / run.sh at render time. Source of truth is the fragment; per-file copies become generated output under `~/.claude/{voice,style,...}/`. Cost: adds a rendering step to install.sh (medium); requires fragment syntax (simplest: `<!-- @include templates/fragments/iron-rule-preamble.md -->` sentinel that install.sh expands). Benefit: fragments become editable in one place; no per-file drift possible. Risk: install.sh grows another responsibility (compare with T1 option C). Also, the source files become less readable on disk — an editor opening `templates/voices/academic.md` sees `@include` sentinels rather than the iron-rule text.

**B — Shared-fragment files referenced from each mirror.** `templates/fragments/iron-rule-preamble.md` exists as a real file; each voice.md says something like `> See templates/fragments/iron-rule-preamble.md — this applies verbatim.` No rendering step; consumers (model, human reader) follow the link. Cost: near-zero — just add the fragment file and trim the mirrors. Benefit: sync is one file. Risk: consumers who don't follow references miss the content. For prompts read by the model this is a real risk — the model sees the link but doesn't fetch the target unless explicitly told to.

**C — Accept duplication, add a parity test.** `tests/fragments/` carries canonical fragments; a test asserts that each "mirror site" contains the canonical text verbatim (at a minimum, a strict-substring check). CI-style blocking: if the test fails, the diff shows which mirror drifted. Cost: small — one test file, one grep-against-canonical script. Benefit: keeps files readable; turns drift from silent to loud. Risk: relies on the test actually being run; doesn't prevent the drift, just catches it.

**D — Mixed approach.** Use A for runtime-critical duplication (iron-rule preamble: wrong content ships a broken voice), B or C for human-facing duplication (classical-abbreviations.md: mostly documentation). The "right" answer depends on what you do with each piece of duplication — the iron rules protect production behavior, the Special tokens block is documentation.

### Recommendation

**D, leaning C for the current clusters and A for whatever arrives next.** Here's why:
- **C covers everything today** at low cost. A test that asserts `templates/voices/*.md` all contain the iron-rule preamble verbatim catches F14. A test that asserts `classical-abbreviations.md` copies are byte-identical catches F18. A test that asserts each style.md contains the "Special tokens" block catches F17. The parity test suite already exists (tests/parity/ is 20 goldens of exactly this shape); this is adding 3-5 simpler assertions in the same spirit.
- **A is right for the next duplication that appears**, when and if you ship something new where runtime behavior depends on the consistency (e.g., if a new category of fragment shows up that's load-bearing at render time).
- **B is tempting for human-facing docs** but the model-consumer problem is real. Skip.

The C fix is ~50 lines of bash in a new `tests/duplication/check.sh`. I can draft it if you greenlight.

**Decision:** Logged for later — pending. Revisit once T1 (CLI decomposition) lands, since C-broad will likely change which duplications still exist (some may collapse into the CLI's runtime assembly, others remain as documentation-only mirrors that need a parity test or include).

---

## Notes

- **Layer 1 skill edits in `~/.claude/commands/audit.md` and `~/.claude/commands/audit-fix.md`** are on disk but `~/.claude/` is not a git repo, so they're not version-tracked. Options: (a) `git init` in `~/.claude/` and commit, (b) copy them into a dotfiles repo if you have one, (c) leave as-is (they're saved; just not tracked). My recommendation: (c) for now, (a) or (b) when you next clean up your `~/.claude/` setup.
- **Cycle-3 design-issue findings NOT in this file**: the single-file design-issues (F1, F2, F4, F5, F6, F7, F8, F11, F13, F15, F16, F19, F20, F21, F22, F23, F24, F25, F30, F31, F32, F35 from cycle-3 `/audit`) were auto-deferred by the new `/audit-fix` class-routing. Most are minor prompt-engineering improvements (word caps, decorative rules, trigger calibration). Work through them selectively when you want; not urgent.
