# CLAUDE.md manifest extraction: slim the shipped template without breaking triggers

**Status:** Shipped 2026-04-24 via PR #24 (dispatch manifest + 9 externalized mode bodies + update-preservation fix + invariants I1-I10; I11 added in phase 4, PR #26). Open threads: §12 OQ6 phase-3 skills spike (issue #36); phase-5 CLI items (ROADMAP §Python CLI). · **Date:** 2026-04-23 · **Target:** Phase 2 of the `sourced` CLI line · **Author:** {{USER}} + agent (see conversation thread `cli-phase2-planning`)

---

## 1. Problem

The shipped `src/sourced/data/templates/CLAUDE.md` is 733 lines / ~13,200 words / ~34k tokens. It loads into every Claude Code session that opens a `sourced`-initialized project. Most of the bulk is 12 mutually-exclusive mode protocols in §7 (7,708 words) plus §10 generation signatures (1,287 words) — material that isn't relevant to any single turn but is always paid into context.

A first pass proposed splitting mode protocols into sibling files loaded via `Read` on mode entry. Pressure-testing (four adversarial agent consults, conversation `cli-phase2-planning`) surfaced three blockers:

1. **Correctness (Agent 1).** The mode switching table at lines 536–552 is a **partial dispatcher**. It captures only explicit user-spoken triggers. It doesn't express §3 self-correction auto-fires (lines 79–81, 360), [finetuning]'s 3-part implicit trigger (lines 454–456), §4's audit forcing-function (line 117), §10 precedence with "silence is not permission" (lines 682–684), or gated mode-to-mode handoffs (plan→outlining→refining→writing→editing→formatting). Naive externalization of mode bodies leaves these rules stranded in prose that's no longer in context.
2. **Cost (Agent 2).** Claude Code caches the system+CLAUDE.md prefix at ~10% read cost, 5-min TTL. `Read` tool results land outside the cached block for the turn they arrive. Break-even is ~1 mode switch per cache window; typical sessions exceed it. The claimed "~24k token savings" was largely illusory for active sessions.
3. **Migration (Agent 3).** `src/sourced/commands/update.py:33–45` refreshes only the managed block by default; `--force` discards the whole file. Neither preserves writer customizations inside the managed block. A split amplifies this: moving mode definitions out means update-time refresh would silently lose any hand-added custom mode.

Web research (conversation `cli-phase2-planning`, third agent round) grounded the problem in prior art:

- **Roo Code** ships mutually-exclusive mode protocols as per-mode rule directories (`.roo/rules-{modeSlug}/`), swapped on mode switch. Direct analogue to our 12-mode problem.
- **Claude Code Skills** use three-level progressive disclosure: name+description always-on (~50 tokens each), body loaded on invocation, bundled files read on-demand. Anthropic's own line: *"If certain contexts are mutually exclusive or rarely used together, keeping the paths separate will reduce the token usage."*
- **LSP capability negotiation** declares a structured `ServerCapabilities` manifest at initialize. Clients never invoke features that weren't declared. Translation: the triggers/gates/forcing-rules Agent 1 flagged as un-externalizable aren't prose — they're a capability table.
- **Linux kernel** splits by *reachability*: code callable from arbitrary contexts (interrupt handlers) stays resident; code owned by one context (filesystem drivers) is a loadable module.
- **systemd drop-ins** express variation as additive overlays layered onto an immutable base, preserving upgradability.

## 2. Design decisions (locked)

**D1. Split by reachability, not by mode.** The always-on core declares the full dispatch surface (every trigger, gate, forcing artifact, precedence rule). Mode *bodies* (step-by-step procedures, examples, prose conventions) are sibling files loaded on mode entry. Directly from the Linux LKM analogue.

**D2. Extract a capability manifest as the load-bearing change.** The current §7 mode-switching-table becomes a fuller **dispatch manifest** that names every trigger (explicit, implicit, auto-fire), every gate (mode-to-mode handoff condition), every forcing artifact (what must be emitted for a gate to pass), and every precedence rule. This is the LSP pattern. The manifest is markdown tables for human readability and `sourced check --invariants`-parseable for mechanical verification.

**D3. Mode bodies ship as `docs/modes/<name>.md` inside the template.** `sourced new` deploys them alongside root `CLAUDE.md`. Root CLAUDE.md instructs `Read docs/modes/<name>.md` on mode entry. We do *not* skills-ify in phase 2 — that's a phase-3 option once the split proves out.

**D4. Project-type gating is a drop-in overlay, not template specialization.** `sourced new --project-type=annotated-bib` writes a `CLAUDE.d/20-annotated-bib.md` overlay alongside the base CLAUDE.md. The base is the same for all project types; overlays add constraints (e.g., annotated-bib drops `[outlining]`/`[refining]`/`[writing]` from the manifest's allowed-modes list). This follows systemd drop-in precedence. Reversible, debuggable, upgrade-safe.

*On directory choice.* Claude Code ships a path-scoped rules loader at `.claude/rules/*.md` (`src/utils/claudemd.ts:254-279, 1354-1397`) — initially a candidate for our overlays. Rejected because that loader is *additive* ("when editing Python files, also apply these rules"); our overlays need *patch* semantics (remove modes from the registry, override gates). Append-only doesn't express removal. We keep `CLAUDE.d/` under sourced's own loader with explicit patch verbs; Claude Code's directory informs naming conventions only.

**D5. `sourced update` preserves hand-edits inside the managed block by default.** Current behavior clobbers it. New behavior: diff the old managed block against the rendered-fresh managed block; conflicting user edits surface as a merge prompt or are preserved verbatim in a `<!-- sourced:user-addition -->` region. `--force` remains as the "discard everything" escape hatch. Spec in §7.

**D6. Anchors stay §-numbered; subagents updated in the same PR.** Existing references from `source-finder.md:43`, `voice-extractor.md:26,69,125`, `sourced-helper.md:49,57`, and `browser-reader-extract/SKILL.md:13,75,104` point at CLAUDE.md §N. Post-split, §N headings remain in root where they refer to rules that stayed resident (§§1–6, §8 logging, §10 precedence). For §7 (modes), the root's §7 becomes the manifest + pointer table; deep-content references get updated to `docs/modes/<name>.md` in the same commit. No anchor-migration shim.

*Sub-decision D6.1 — `omit-claude-md` eligibility audit.* Claude Code's Agent tool supports an `omitClaudeMd` flag for read-only subagents (`src/tools/AgentTool/loadAgentsDir.ts:128-132`) — drops the host project's CLAUDE.md from the spawned agent's context. Candidates for sourced: `source-finder` and `voice-extractor`, both read-only and both currently rely on §-references into CLAUDE.md. **Precondition before setting the flag:** each subagent's own prompt must be self-contained for the rules it invokes (§3 verification rules inlined into `source-finder`; §10 canonical-ID list inlined into `voice-extractor`). Flip the flag *after* the inlining, not before. Sequence this as a follow-up PR, not part of commit 1.

**D7. `sourced check --invariants` verifies manifest-to-body coherence.** Two new rules: (a) every mode named in the manifest's allowed-modes list has a corresponding `docs/modes/<name>.md` file, and (b) every overlay in `CLAUDE.d/` declares only modes the base manifest lists. Custom modes added by the writer are exempt via an explicit `<!-- sourced:custom-mode -->` marker.

**D8. §10 compresses in place as part of the extraction.** The 1,287-word never-list becomes a declarative table in the manifest (canonical ID, pattern shape, one-line "why flagged"). The full prose rationale for each pattern moves to `docs/modes/writing.md` and `docs/modes/editing.md` where it's actually consulted. Direct-quotations carve-out stays in root because it governs §4's verbatim rule.

## 3. The capability manifest

Lives at the top of root `CLAUDE.md`, after §1–§6 (iron rules stay first). Five subsections, all always-on. Estimated size: ~1,200 words / ~3,000 tokens.

### 3.1 Mode registry

```markdown
### Modes

| Mode | Body | Project types | Auto-enters from |
|------|------|---------------|-------------------|
| collaborative | inline (default) | all | session start |
| research | docs/modes/research.md | all | §3 self-correction; unsourced-claim in any prose mode |
| plan | docs/modes/plan.md | all | explicit trigger only |
| outlining | docs/modes/outlining.md | essay | explicit trigger; gated by brief |
| refining | docs/modes/refining.md | essay | explicit trigger; gated by outline sign-off |
| writing | docs/modes/writing.md | essay | explicit trigger; gated by refined-outline approval |
| editing | docs/modes/editing.md | all | explicit trigger |
| formatting | docs/modes/formatting.md | all | explicit trigger; gated by edit-complete + paste target |
| annotated-bib | docs/modes/annotated-bib.md | annotated-bib | explicit trigger |
| finetuning | docs/modes/finetuning.md | all | explicit trigger; implicit trigger (§3.3) |
| red-team | inline | all | explicit trigger |
| babble | inline | all | explicit trigger |
```

Trivially-small modes (collaborative 73w, red-team 92w, babble 32w) stay inline in root because the bodies are smaller than the `Read` overhead.

### 3.2 Explicit triggers

The current table at lines 538–551 moves here verbatim. No shape change.

### 3.3 Implicit triggers

Declarative list. Each entry names the shape the trigger matches and cites the mode body for full procedure:

- **[finetuning] 3-part match**: (a) message names a span in the draft AND (b) carries a negative-evaluation phrase ("feels wrong", "is off", "not quite", "something's off about", "not sure about", "can you try") AND NOT (c) asks for a specific named change. Announce entry; false positives are cheap. Full procedure: `docs/modes/finetuning.md`.
- **§3 self-correction — unverified citation**: about to cite without full-text access verified. Say `"wait... I haven't actually verified the full text is accessible, let me do that first."` then announce `Switching to [research mode].` Full procedure: `docs/modes/research.md`.
- **§3 self-correction — stale byline at write time**: rendering `@id` for narrative use where log entry's `retrieved_at` predates session start. Say `"wait... I'm about to render an author I haven't verified from the source, let me check the page."` then re-verify, update `retrieved_at`. Full procedure: `docs/modes/research.md`.
- **§3 self-correction — stale byline at format time**: [formatting mode] pre-flight finds missing/stale `retrieved_at`. Surface to {{USER}} before rendering. Full procedure: `docs/modes/formatting.md` step 2.
- **Finetuning missed-trigger self-correction**: prior turn matched (a)+(b)+(c-not) but no entry announced. Open next turn with `"wait — that was a finetuning trigger I missed..."`. Full procedure: `docs/modes/finetuning.md`.

### 3.4 Mode-to-mode gates

```markdown
| Transition | Gate condition | Forcing artifact (§3.5) |
|------------|----------------|--------------------------|
| → plan | brief present OR skip-brief escape active | — |
| plan → outlining | brief complete enough for outlining | — |
| outlining → refining | outline sign-off from {{USER}} | — |
| refining → writing | §4 audit list emitted with zero unresolved `flagged` rows | §4 audit list |
| writing → editing | {{USER}}-initiated only | — |
| editing → formatting | edit-complete gate + paste target named + voice audit clean | voice audit surface-scan report |
| formatting → (terminal) | pre-flight pass (all 6 checks in §7 step 2 of formatting body) | inline-quote-threshold list |
| * → research (auto) | §3 self-correction trigger | — |
| research → (return) | source logged OR gap accepted | — |
| skip-brief → (continue) | scope-growth check each turn | scope-delta list (if drift) |
```

A gate whose forcing artifact is missing has not been satisfied. Forcing artifacts are defined in §3.5.

### 3.5 Forcing artifacts

A gate that requires an artifact has not been satisfied unless the artifact is emitted in the same turn as the claim of completion. Rules:

- **§4 audit list.** One row per citation audited, each row recording pass/`flagged: <reason>` for items 1, 2, 4, 5, 6 of §4. Emitted by `[refining]` on outline and `[editing]` pass 2 on prose. Gates: refining → writing, editing → formatting.
- **Scope-delta list.** Emitted by §6 scope-growth soft-stop. Entries of form `{trigger_observed, original_scope, proposed_scope_change, load_bearing?}`. Gate: none (continuation is a choice, not a gate), but absence of the list on a triggered self-check means the self-check didn't run.
- **Inline-quote-threshold list.** Emitted by `[formatting]` pre-flight step 2. Per flagged span: `{paragraph_ref, quote_word_count, threshold, @id}`. Empty list required on zero hits. Gate: formatting pre-flight.
- **Voice audit surface-scan report.** Emitted by `[editing]` handoff before formatting. Lists §10 never-list hits and density-list overruns with line references. Gate: editing → formatting.

### 3.6 Precedence

- **§4 verbatim > §10 inside quoted spans.** Punctuation, word-order, and patterns inside a direct quote are preserved as the source prints them. §10 applies to the writer's framing sentence, not the quote.
- **§10 > voice.md prose.** Inline prose in voice.md arguing for a §10 pattern without a matching `## §10 exemptions` bullet has no runtime effect. Silence is not permission.
- **§10 exemption IDs are machine-read.** Unknown IDs fail `sourced check` install-time validation. Canonical ID list: `em-dashes`, `not-x-but-y`, `ornamental-triads`, `throat-clearing-openers`, `demonstrative-openers`, `ornamental-compounds`. (Source of truth in this manifest, not in mode bodies.)
- **Conflict surfacing.** If voice.md and §10 conflict without an exemption, surface the conflict on first occurrence rather than resolving silently.

## 4. File layout post-split

```
src/sourced/data/templates/
  CLAUDE.md                           # ~3,500w / ~9k tokens; §1–§6, §7 manifest, §8 logging-only, §10 precedence, §11 pointer
  CLAUDE.d/                           # empty in base template; populated by sourced new per project type
    README.md                         # explains drop-in precedence
  docs/
    modes/
      research.md                     # §7 [research] + full dispatch template
      plan.md                         # §7 [plan]
      outlining.md                    # §7 [outlining]
      refining.md                     # §7 [refining]
      writing.md                      # §7 [writing] + §9 voice application + §10 full never-list rationale
      editing.md                      # §7 [editing] (8-pass) + §10 rationale references
      finetuning.md                   # §7 [finetuning]
      annotated-bib.md                # §7 [annotated-bib]
      formatting.md                   # §7 [formatting] + §8 Moments 2-3 + §11 style application
```

Writer projects after `sourced new` get the same layout at project root. Relative paths in root CLAUDE.md (`Read docs/modes/writing.md`) are resolved from the project root. Claude Code's working directory convention handles this; no substitution needed.

**Overlays.** `sourced new --project-type=annotated-bib` writes:

```
CLAUDE.d/
  20-project-type-annotated-bib.md    # removes outlining/refining/writing from mode registry; adds annotated-bib-specific gates
```

Overlay precedence follows systemd's lexicographic rule. Overlay format: same manifest subsections, but marked as patches ("remove these modes from §3.1"; "override this gate").

## 5. Cache-discipline primitives

Claude Code's own prompt assembly exposes two primitives (`src/constants/systemPromptSections.ts`):

```typescript
systemPromptSection(name, compute)
  // Memoized. Cached until /clear or /compact. Default for all always-on content.

DANGEROUS_uncachedSystemPromptSection(name, compute, _reason)
  // Recomputes every turn. The name and required `_reason` string make
  // cache-breaking a reviewable sin at the API level.
```

Adopt this shape in `src/sourced/_pipeline.py`. Every always-on section declared by the manifest renderer is a `cache_stable_section(name, compute)` by default; any section that legitimately changes mid-session must go through `uncached_section(name, compute, reason=...)` with a non-empty reason string. `sourced check --invariants` verifies (a) no bare string assembly in `_pipeline.render_claude_md`, (b) every `uncached_section` call carries a reason string.

This **resolves OQ2** without a hot/cold structural split. Every section carries its cache classification; the manifest's dispatch block is `cache_stable_section("dispatch-manifest", ...)` with no exceptions. Attempts to inject dynamic content (e.g., a session-timestamp header) would require the `uncached_section` wrapper, making them auditable in code review.

## 6. Always-on content (root CLAUDE.md) detailed inventory

Stays in root:

- §1 Partnership model (305w)
- §2 Boundaries (178w)
- §3 Source verification (483w) — iron rule
- §4 Synthesis integrity (838w) — iron rule; audit fields referenced by manifest §3.5
- §5 Decision threshold (430w) — load-bearing for autonomy
- §6 Intake brief schema (745w) — structures session state
- §7 Manifest (~1,200w new) — the LSP-style dispatch surface
- §7 meta: announcement rule, decomposition, project type (400w) — kept as intro to manifest
- §8.1 Citation log schema (Moment 1 only) (~400w from original §8's 1,210) — §4 audits read log fields by name; must be resident
- §9 pointer (~30w) — "read voice.md on outline/write/edit entry; application rules in docs/modes/{writing,editing}.md"
- §10 precedence subsection only (~200w from original 1,287) — canonical ID list + conflict-surfacing rule; never-list prose moves to drafting bodies
- §11 pointer (~30w) — "read style.md at format entry; rules in docs/modes/formatting.md"

Projected root size: ~4,200 words / ~10.5k tokens. Down from ~34k.

Removed to mode bodies:

- §7 [research]/[plan]/[outlining]/[refining]/[writing]/[editing]/[finetuning]/[annotated-bib]/[formatting] bodies
- §8 Moments 2 and 3 (in-prose ID syntax, formatting moment) — consulted only in writing/editing/formatting
- §9 voice application body — consulted only in outlining/writing/editing
- §10 never-list prose and rationale — consulted only in writing/editing

Inlined because too small to externalize:

- §7 [collaborative] 73w · [red-team] 92w · [babble] 32w

## 7. `sourced update` preservation fix

`src/sourced/commands/update.py` currently:

```python
old_text = claude_md_path.read_text(encoding="utf-8")
extract_managed_block(old_text)  # raises if bad
fresh_full = _pipeline.render_claude_md(user, ctx)
fresh_managed = extract_managed_block(fresh_full)
new_claude = replace_managed_block(old_text, fresh_managed)
```

`replace_managed_block` wholesale-replaces the managed region. Writer customizations inside it (custom modes, inline notes) are lost silently.

**New behavior (phase 2):**

1. Extract old managed block.
2. Render fresh managed block.
3. Run a structural diff (not text diff — parse both into manifest + section tree).
4. **Auto-merge** sections where fresh-only changes are additions (new mode registry entry in fresh, not in old → add).
5. **Preserve** sections marked `<!-- sourced:user-addition -->` in old verbatim.
6. **Surface conflicts** where old and fresh both modify the same section (e.g., writer tweaked §3.6 precedence and fresh changed it): print both, ask {{USER}} to pick, abort if non-interactive.
7. `--force` retains current discard-everything behavior as the escape hatch.

Writer opt-in customization pattern:

```markdown
<!-- sourced:user-addition start -->
### Custom modes

| Mode | Body | Project types | Auto-enters from |
|------|------|---------------|-------------------|
| debugging | docs/modes/debugging.md | all | explicit trigger |
<!-- sourced:user-addition end -->
```

`sourced check --invariants` recognizes `user-addition` regions and exempts them from the base-mode-registry check.

## 8. `sourced check --invariants` rules (phase 2 additions)

New invariants:

- **I1 (mode-body presence).** For every mode in the base manifest's §3.1 registry that is not marked `inline`, `docs/modes/<name>.md` exists.
- **I2 (overlay scope).** Every file in `CLAUDE.d/` modifies only sections defined in the base manifest. Overlays that introduce new trigger categories fail.
- **I3 (§10 ID integrity).** Every canonical ID in §3.6 precedence corresponds to a never-list entry in `docs/modes/writing.md` and vice versa. `voice.md`'s `## §10 exemptions` bullets name only IDs from this list.
- **I4 (manifest syntactic validity).** §3.1 registry parses as a markdown table with the expected columns; §3.4 gate table parses; §3.5 forcing-artifact list parses.
- **I5 (forcing-artifact reachability).** Every forcing artifact named in §3.5 is referenced in at least one mode body (`docs/modes/<name>.md`). Orphaned artifacts fail.
- **I6 (user-addition marker integrity).** Every `<!-- sourced:user-addition start -->` has a matching `end`. Unclosed markers fail.
- **I7 (precedence ordering).** The §3.6 precedence rules parse as an ordered list where each rule names one canonical ID. Cross-rule ties fail. Rank in the list IS the precedence — no "higher than" / "lower than" prose.
- **I8 (mode body template compliance).** Every `docs/modes/<name>.md` contains the required sections named in §13 (Overview, When to Use, Steps, Red Flags, Rationalizations, Exit Gates). Rigid modes also carry an Iron Law section. Missing sections fail with a line-accurate error.
- **I9 (dispatch-block size limits).** Root CLAUDE.md's §7 manifest block is ≤200 lines (mirrors Claude Code's `MAX_ENTRYPOINT_LINES` convention in `src/memdir/memdir.ts:38-108`); each §3.1 registry entry is ≤150 characters (mirrors Claude Code's MEMORY.md entry-length guidance). Exceedances fail with the over-budget section cited.
- **I10 (cache-discipline auditing).** `_pipeline.render_claude_md` contains zero bare-string assembly for always-on content. Every section resolves through either `cache_stable_section(...)` or `uncached_section(..., reason=...)` with a non-empty reason. Raw string concatenation of always-on content fails.

## 9. Migration path for existing projects

Existing projects (created phase 1, have the monolithic CLAUDE.md): running `sourced update` post-phase-2 deploys the new layout.

Strategy:

1. **First-run detection.** `sourced update` checks whether the project has `docs/modes/` already. If not, treat as a phase-1→phase-2 migration.
2. **Rename monolith.** Move existing `CLAUDE.md` to `CLAUDE.md.phase1.bak` (atomic, alongside the existing `.sourced.bak` mechanism in `commands/update.py:65–70`).
3. **Deploy new layout.** Render fresh root CLAUDE.md + `docs/modes/*.md`.
4. **Detect custom modes in the backup.** Grep `CLAUDE.md.phase1.bak` for §7 additions not in the base mode registry. Surface to {{USER}} with a migration prompt: "Your phase-1 CLAUDE.md had a `[debugging mode]` section not in the base. Move it to `docs/modes/debugging.md` as a custom mode, or drop it?" Default: preserve as a `user-addition` region in the new root.
5. **Keep `.phase1.bak` for one release cycle** so writers can rollback.

`docs/MODES.md` (the repo's user-facing reference) gets a one-line update post-split: link target changes from `templates/CLAUDE.md §7` to `templates/docs/modes/<name>.md`.

## 10. Rollout plan

Phase 2 is five separable commits, merged in order:

1. **Commit 1a — seed mode bodies + pressure test.** Write the new root CLAUDE.md with the full dispatch manifest, plus three mode bodies: `docs/modes/finetuning.md` (the implicit-trigger mode most at risk of silent drift), `docs/modes/research.md` (carries the §3 self-correction auto-trigger surface), and `docs/modes/editing.md` (largest body, 8-pass audit, §10 + §4 integration — the hardest to get right). Pressure-test each with an adversarial subagent transcript *before* the remaining modes are written. This mirrors the `writing-skills:533-561` RED-GREEN-REFACTOR pattern: if the mode body doesn't survive a hostile transcript, iterate before scaling. Do not proceed to commit 1b until the three seed bodies clear pressure-testing.
2. **Commit 1b — remaining mode bodies.** Once the template is proven, write the remaining six non-trivial mode bodies (`plan`, `outlining`, `refining`, `writing`, `annotated-bib`, `formatting`). All follow the §13 template.
3. **Commit 2 — `sourced update` preservation fix.** Rewrite `commands/update.py` structural-diff path using `marked` (CommonMark lexer, `gfm: false` — see §7). Independent of the manifest extraction — solves Agent 3's migration finding even if the manifest slips.
4. **Commit 3 — `sourced check --invariants` rules I1–I10.** Depends on the manifest format being stable (post-commit 1b) and the cache-discipline primitives (§5) being in place.
5. **Commit 4 — project-type drop-in overlays.** `sourced new --project-type=<type>` populates `CLAUDE.d/`. Lowest-priority of the five; annotated-bib is the only clear first customer. Depends on commit 3 (invariant I2 verifies overlay scope).

Commits 1a and 2 can land in parallel PRs. Commit 1b depends on 1a. Commit 3 depends on 1b. Commit 4 depends on 3. D6.1 (`omit-claude-md` subagent flag) lands as a follow-up PR after commit 1b, gated on each subagent's rule-inlining.

## 11. Non-goals

- **Not skills-ifying in phase 2.** Claude Code's skill system is the right ultimate pattern (per Anthropic's own design docs, and validated against Superpowers' shipped skills at `/home/hayden/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/`) but adds discovery machinery and per-skill frontmatter (~50 tokens × 12 modes = ~600 tokens always-on, larger than our compressed manifest registry). Phase 3 spike — see §12 OQ6 for the evaluation criteria.
- **Subagent-ified modes: deferred, not rejected.** A `[writing mode]` subagent with isolated context was initially rejected because modes share conversation state with {{USER}} (outline, brief, pending revisions). However, Claude Code's `context: fork` skill option (`src/utils/frontmatterParser.ts:42-49`) supports forks that inherit parent cache and share context — which preserves the state access the initial rejection was worried about. Revisit in phase 3 alongside the skills-ification spike.
- **Not introducing a runtime config file.** The manifest is prose with tables, parseable by `sourced check` regex + `marked` lexer. No YAML/TOML dependency.
- **Not migrating §N anchors to new labels.** Subagents and skills reference §N; we keep §N in root for resident sections and update callers for moved sections in the same PR.
- **Not compressing §§3–6.** A separate deletion/compression pass on the iron rules was considered; verdict is that correctness rules shouldn't be shortened under a context-budget lens. Token savings come from §7 and §10, not §3/§4.

## 12. Open questions

- **OQ1.** Does `Read docs/modes/<name>.md` resolve reliably when Claude Code is launched from a subdirectory of the project? Current template uses intra-project paths like `voice.md` and absolute paths like `~/.claude/citations/schema.md`; relative `docs/modes/` is new. **Mitigation if broken:** `sourced install` writes an absolute path into root CLAUDE.md at render time (`{{PROJECT_ROOT}}/docs/modes/<name>.md`) using the existing template-substitution pipeline.
- ~~**OQ2.** Should the manifest be a single always-on block, or split into a "hot" part and a "cold" part?~~ **Resolved in §5 (cache-discipline primitives).** Every section tagged cache-stable or uncached-with-reason; no structural split needed. The dispatch manifest is a single `cache_stable_section`.
- ~~**OQ3.** `sourced update` structural diff: implement as a full AST parse of the manifest, or as a simpler section-header-based diff? Phase-2 default: section-header diff using the `marked` lexer (`gfm: false`), matching Claude Code's `claudemd.ts:300` convention. Full AST parse is heavier engineering and phase-3 material.~~ **Resolved in commit 2 (Python regex, no lexer).** The `sourced` CLI is Python; `marked` is a JS-only lexer. Shipping `marked` as a runtime dep would require a subprocess shell-out or a WASM build — both heavier than the problem warrants. `src/sourced/project.py:parse_user_additions / merge_managed_block` use `re.compile(r"^## (.+)$")` for section detection, `re.compile(r"^<!-- sourced:user-addition start -->$")` for region markers, column-0 strict (matching the existing sentinel discipline at `BEGIN_RE` / `END_RE`). Granularity: `##` only — `###` subsections inside a `##` section are treated as atomic body content (a user-addition region under `### 7.1 Mode registry` is attributed to `## §7` in phase 2). Finer-grained placement is phase-3 material, deferred with no current consumer. Tests in `tests/cli/unit/test_project.py::parse_user_additions*` + `tests/cli/integration/test_update_preservation.py` cover the contract.
- **OQ4.** Mode body size variance: `docs/modes/editing.md` projects to ~1,800w after absorbing the §10 rationale; `docs/modes/plan.md` at 333w. Does it matter? Not for correctness; possibly for writer readability. No action phase 2.
- ~~**OQ5.** Duplicate or cross-reference §10 rationale across writing.md / editing.md?~~ **Resolved: neither — use explicit Read-step in the procedure.** `editing.md`'s pass-6 procedure reads "Read `docs/modes/writing.md#never-list` and apply each rule." Single source of truth (like cross-reference), deterministic load (like duplicate), no unstated dependency. Relies on headings staying stable; `sourced check` I3 anchors the invariant.
- **OQ6 (new).** Phase-3 skills-ification spike — evaluation criteria: (a) does the manifest's implicit-trigger machinery (§3.3) fire reliably across writer sessions, or do we see missed-trigger reports in the wild? (b) does `<SUBAGENT-STOP>` semantics (per `using-superpowers/SKILL.md:6-8`) close the subagent-dispatch-from-mode problem that `context: fork` opens? (c) does the ~600-token frontmatter overhead pay for itself in reduced drift? Decision point: after 4–8 weeks of phase-2 writer usage. Open the spike with its own spec if criteria lean toward flip.
- **OQ7 (new).** `sourced-helper` agent doc-reflection (per ROADMAP.md:261 — "phase 2 could have it `Read` shipped docs on demand"): does its phase-1 self-contained prompt survive the split? The agent references `CLAUDE.md §7` which post-split means "the manifest" and no longer "the mode bodies." Needs prompt update in commit 1a to redirect to `docs/modes/<name>.md`. Low-risk but not free.

## 13. Mode body template

Every `docs/modes/<name>.md` conforms to the structure below, lifted from Superpowers' shipped skill convention (validated against `test-driven-development/SKILL.md`, `systematic-debugging/SKILL.md`, `verification-before-completion/SKILL.md`, `brainstorming/SKILL.md`, and `writing-skills/SKILL.md`). Required sections in required order; optional sections marked. Invariant I8 enforces this.

### 13.1 Required structure

```markdown
# [<mode-name> mode]

## Overview
<1–2 sentences. The core principle the mode embodies. Not a workflow summary — a principle statement. e.g., "[refining mode] stress-tests the outline against the citation log before prose exists. Every claim gets a row in the audit list before the gate passes.">

## When to Use
**Enter when:**
- <explicit trigger from manifest §3.2, verbatim>
- <implicit trigger from manifest §3.3, verbatim>

**Do not enter when:**
- <forbidden entry conditions — e.g., "brief is missing and skip-brief escape is not active">

## Iron Law   <!-- REQUIRED for rigid modes only: finetuning, research (§3 self-correction path), formatting (pre-flight) -->

```
┌─────────────────────────────────────────────┐
│  NO <action X> WITHOUT <preceding action Y> │
└─────────────────────────────────────────────┘
```

<One sentence explaining what skipping Y costs.>

## Steps
<Numbered list. Each step 2–5 minutes of wall-clock work when executed. Steps reference forcing artifacts from manifest §3.5 by name.>

1. Announce entry: `Switching to [<mode-name> mode].`
2. <step>
3. <step>
...
N. Announce return or handoff: `Switching to [<next mode> mode].` or `Ready to advance to [<next mode>]?`

## Red Flags
<Bullet list of thoughts/behaviors that mean the mode is being skipped or shortcut. Modelled after `verification-before-completion/SKILL.md:53-62`.>

- "This is obviously fine, I can skip step <N>." — no, run step <N>.
- "The audit list is ceremonial; {{USER}} won't read it." — no, it's the forcing artifact.
- ...

## Rationalizations
<Pre-empt excuses. Table format from `test-driven-development/SKILL.md:256-270`.>

| Excuse | Reality |
|--------|---------|
| "The change is trivial, no need to announce the switch." | Announce anyway. False positives are cheap; silent substitution is the failure mode this mode exists to prevent. |
| "§4 audit is for peer review, not this session." | §4 audit fires at refining and editing regardless of session audience. |
| ... | ... |

## Quick Reference
<Compact one-screen checklist for re-entry.>

## Exit Gates
<Restates relevant rows from manifest §3.4 at point-of-use. Names allowed next-modes AND forbidden next-modes explicitly.>

**Allowed transitions (after handoff gate):**
- → [<next mode>]: when <gate condition from §3.4>

**Forbidden transitions:**
- → [<mode>]: <reason — e.g., "[writing] cannot be entered from [outlining] directly; [refining] sign-off is required">
- → [<mode>]: <reason>
```

### 13.2 Optional sections

- **`## Flowchart`** — Graphviz `digraph` for decision points. **Only include if non-obvious** (per `writing-skills/SKILL.md:292-316`). Linear procedures don't get flowcharts.
- **`## What this mode does NOT do`** — already present in several current §7 mode bodies (e.g., `[finetuning]` lines 471–475, `[formatting]` lines 528–532); preserve where it exists.

### 13.3 Anti-patterns to avoid

- **Description-as-workflow-summary trap** (per `writing-skills/SKILL.md:150-172`). The `Body` column in §3.1 is a file path and nothing else. If we add a "what this mode does procedurally" column, Claude reads the description and skips the body. Don't.
- **`@docs/modes/<name>.md` eager include.** Claude Code's `@` syntax in CLAUDE.md eagerly loads files at session start (`src/utils/claudemd.ts:451-535`), defeating the whole extraction. Use `Read` tool invocation on mode entry, never `@`.
- **Cross-reference instead of explicit Read.** Per OQ5 resolution: if mode body A needs content from mode body B, the procedure step says "Read `docs/modes/B.md#anchor`" — not "see B.md for details." Prose cross-references create unstated dependencies.
- **Batching mode bodies without pressure-test** (per `writing-skills/SKILL.md:583-594`). Ship 2–3, pressure-test, then ship the rest. Commit plan §10 enforces this.

## 14. Appendix: evidence trail

- Conversation thread: `cli-phase2-planning` (2026-04-23). Eight read-only consult agents dispatched across four rounds; findings synthesized here.
- Round 1 (structural): CLAUDE.md section map, docs + subagent coupling.
- Round 2 (pressure test): runtime-completeness, prompt-caching cost, migration/UX, alternative approaches.
- Round 3 (prior art, web research): agent frameworks (Roo Code, Cursor, Cline, Aider, GitHub Copilot, Codex, MCP), Anthropic caching docs, systems analogues (Linux LKM, LSP, systemd, VSCode activation events, Kconfig).
- Round 4 (leaked repo inspiration): `hayden1126/claude-code` (cache-discipline primitives, rules-loader pattern, `omitClaudeMd` flag, `MEMORY.md` index sizing, `context: fork` skills), `hayden1126/superpowers` (mode-body template, rationalization-table convention, Iron Law ASCII-box, exit-gate terminal section, batching anti-pattern, description-as-workflow trap).
- Prior spec (reference style): `docs/superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md`.
- Memory entry (updated post-merge): `/home/hayden/.claude/projects/-home-hayden-sourced/memory/project_phase1_cli_port.md` — add phase-2 surface update on merge.

External sources cited during the research:
- [Anthropic — Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Roo Code — Custom Instructions](https://docs.roocode.com/features/custom-instructions)
- [LSP Specification 3.17 — capability negotiation](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
- [systemd.unit — drop-in precedence](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)
- [Linux Kernel Module Programming Guide](https://sysprog21.github.io/lkmpg/)

Internal code references (from leaked repos, round 4):
- Claude Code: `src/constants/systemPromptSections.ts`, `src/utils/systemPrompt.ts:38-118`, `src/utils/claudemd.ts:254-279,282-334,451-535,1249-1318,1354-1397`, `src/tools/AgentTool/loadAgentsDir.ts:128-132`, `src/tools/AgentTool/prompt.ts:48-63`, `src/memdir/memdir.ts:38-108`, `src/skills/loadSkillsDir.ts:96-401`, `src/utils/frontmatterParser.ts:42-49`.
- Superpowers v5.0.7: `skills/using-superpowers/SKILL.md:6-8,30,70,108-113`, `skills/test-driven-development/SKILL.md:32-45,256-270,327-340`, `skills/systematic-debugging/SKILL.md:17-23,46-213,247-257`, `skills/verification-before-completion/SKILL.md:17-23,25-38,53-62,65-75`, `skills/writing-skills/SKILL.md:30-46,76-80,93-137,150-172,282-288,292-316,374-393,533-561,564-576,583-594`, `skills/brainstorming/SKILL.md:65-66`, `skills/writing-plans/SKILL.md:37-44,137-152`, `skills/executing-plans/SKILL.md:33-37`, `hooks/session-start:18-38`.
