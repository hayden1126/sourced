# Skills

[← Back to README](../README.md)

Skills are self-contained helpers Claude Code auto-discovers from `~/.claude/skills/<name>/`. Each shipped skill is a directory with a `SKILL.md` (instructions the model reads on activation) plus any scripts or assets. `sourced global-install` mirrors `src/sourced/data/skills/<name>/` into `~/.claude/skills/<name>/` on every run, so shipping a skill via sourced makes it available across every project and session under the home directory.

## When a skill vs. when CLAUDE.md?

Skills are for **conditional, self-contained helpers** the model invokes only when the task reaches for them. CLAUDE.md is for **always-on operating law** that loads every turn.

Right shape for a skill:
- Platform-specific tooling the model needs only sometimes (browser extraction, external API calls).
- Reference material (lookup tables) too large to carry inline but small to load conditionally.
- Self-contained procedures where invocation cost is lower than always-loaded context cost.

Wrong shape for a skill:
- Always-applied rules (§3 source verification, §4 synthesis integrity).
- Mode definitions (§7); the model needs these before announcing mode switches.
- Cross-mode infrastructure (§8 citations).

## Shipped skills

### `browser-reader-extract`

**Use when:** a primary source sits behind a DRM'd browser reader (library OverDrive loan, Kindle Cloud Reader, Scribd) and regular `Read` or `WebFetch` cannot reach it, but the writer holds legitimate access.

**What it does.** Connects `puppeteer-core` to a user-launched Chrome instance with `--remote-debugging-port=9222`, finds the open book tab, auto-detects the content iframe (via `[id^="page-"]` page-anchor presence), and extracts the currently-visible spine item as text with `[p. N]` markers inserted at each page boundary. Page markers preserve Roman front matter (i, ii, xii) and Arabic page numbers. Range filtering (`--range 5-20`) and page-list filtering (`--pages i,ii,1,5`) supported.

**Prerequisites.** Node 18+ and `puppeteer-core`. `sourced` does not install Node; on first use of the skill, run `npm install` inside `~/.claude/skills/browser-reader-extract/` to fetch `puppeteer-core`. Writers who never need browser-reader extraction pay zero setup cost.

**Platform coverage.** OverDrive Read ships as the proven extractor (`overdrive.mjs`). The same pattern extends to other readers (Kindle Cloud Reader, Scribd, etc.) via auto-detection or a `--iframe-pattern` override; the SKILL.md's *Adding a new reader* section walks through identifying tab URL, content iframe, and page-anchor selector for a new platform.

**How citations map back.** Each `[p. N]` in the extract becomes a `location` value in the citation log (`"p. 42"`, Roman or Arabic preserved). `exact_quote` and `surrounding_context` come from the extract text directly; no separate fetch needed. Record provenance in the log entry's `retrieval` field as `"browser-reader-extract: <platform>, <date>"`.

**Scope and limits.** The skill does not launch Chrome, log into accounts, or bypass access controls. Launch, login, and book navigation are user actions. The skill assumes legitimate access; that check is the user's, not the agent's.

See `~/.claude/skills/browser-reader-extract/SKILL.md` for the full setup and operational walkthrough.

### `staged-reader-review`

**Use when:** a multi-section draft is about to leave the writer's hands and whole-document review would smooth over per-section pacing problems, undefined terms, and scope drift. In a sourced project, run it after `[formatting mode]` completes, on the rendered output (`<draft>.gdocs.md`, `<draft>.plain.md`), invoked from `[collaborative mode]`.

**What it does.** N blind reader personas (default 3, at least one outsider to the field) read the rendered draft one section at a time, in lockstep, with no peek ahead. Each writes a reaction, then rates clarity and coherence 1–5 per section on anchored scales; reading is sequential and stateful, so a reader lost early struggles later, and surfacing that cascade is the instrument. The parent consolidates convergent findings (`RR` ids), single-reader notes (`RN` ids), and a fixed three-value verdict (`accept | minor revision | major revision`) into the forced artifact `<draft>.reader-review.md`: a review that produced no file has not run.

**Pre-flight record.** Before reading starts, the skill records in the artifact whether each editing-gate artifact was emitted where `[editing mode]` requires it (`present` or `absent`): the revision report, §4 audit list, citation-payload re-read list, and voice audit surface-scan report at handoff, plus the three pass-5 lists in their pass turns. It records; it does not halt (issue [#33](https://github.com/hayden1126/sourced/issues/33)'s option-2 record, one gate downstream).

**Field evidence.** The prototype run on the 2026-07-04 paper session (3 readers, 6 sections) converged on cumulative-load, term-order, and unjoined-strand defects that the editing-mode audit, which works sentence by sentence, never flags.

**Scope and limits.** Read-only over the rendered sibling; produces exactly one artifact; never self-triggers and never blocks formatting. Measures reader experience, not authorial voice.

See `~/.claude/skills/staged-reader-review/SKILL.md` for the full protocol and artifact schema.

## Authoring a new skill

A skill is a directory under `src/sourced/data/skills/<name>/` with at minimum a `SKILL.md`. The model discovers the skill via its frontmatter when Claude Code loads `~/.claude/skills/`:

```markdown
---
name: my-skill
description: Use when <trigger condition>. <One-sentence summary of what it does.>
---

# My skill

## When to use
<conditions that should trigger the skill>

## Prerequisites
<runtime deps, installation steps>

## Usage
<concrete invocation examples>

## Scope and limits
<what the skill does not do>
```

Add any scripts, config files, or asset directories alongside `SKILL.md`. `sourced global-install`'s skill-mirror step (`src/sourced/data/skills/<name>/` → `~/.claude/skills/<name>/`) preserves a local `node_modules/` tree on update so npm-installed deps survive subsequent `sourced global-install` re-renders.

For skills depending on external CLIs (like `pandoc` or `pdftotext`), consider whether the dependency belongs in `sourced check`'s prerequisite check (if needed by the core framework) or only surfaced at skill-activation time (if specific to this skill). Node is currently skill-specific, so `sourced check` does not check for it.
