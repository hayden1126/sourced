# [writing mode]

## Overview

Writing converts the refined outline into prose, one section at a time, holding every sentence against the citation log, the paraphrase default, and the §10 never-list as it is emitted. The failure mode this mode exists to prevent is **silent drift** — fluent academic phrasing that diverges from the source, introduces a §10 pattern, or elides a qualifier before [editing mode] ever sees it. Catching drift at write time is cheap; repairing it after a full draft exists is not.

Writing is not a rigid mode per spec §13.1, yet the §10 check-as-you-emit discipline is non-negotiable. There is no single Iron Law gate; compliance is enforced sentence-by-sentence as prose is emitted, and caught again in [editing mode]'s pass 6 if anything slipped through. Do not draft a sentence containing a never-list pattern and plan to fix it later.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} says "write this" / "put this into prose" / "write out X" or equivalent (see manifest §7.2).
- Project type must be `essay`. [writing mode] is not valid for `annotated-bib` projects (manifest §7.1).

**Do not enter when:**
- The refined outline has not been approved. The gate `refining → writing` requires the §4 audit list with zero unresolved `flagged` rows plus explicit outline approval from {{USER}} (manifest §7.4). Silence is not approval.
- `voice.md` is missing. Stop and ask {{USER}} to run `sourced switch voice <name>` (not `install.sh --voice` — the install.sh CLI was retired in phase 1). Do not guess voice rules.
- `[UNSOURCED]` tokens or unresolved `[VERIFY: …]` tokens appear in the outline where they carry load-bearing claims. Resolve via [research mode] first.

## Steps

1. **Announce entry.** First output of the turn: `Switching to [writing mode].` Name the section in one clause after the announcement: "writing section 2" / "writing the argument body."

2. **Read `voice.md` in full.** All voice rules apply strictly at write time — not only Paragraph Flow. Do not work from memory of prior sessions. If `voice.md` is missing, halt and ask {{USER}} to run `sourced switch voice <name>`.

3. **Read `docs/modes/writing.md §Never-list` (this section, below) in full.** On first entry per session, re-read it even if you believe you know it. The restructure-don't-retokenize rule and cross-sentence retokenization check are load-bearing and easy to misapply from memory.

4. **Load the citation log** (`<draft>.citations.json`). Every claim you draft will need an ID. If the log is absent for a section with citations in the outline, stop and ask {{USER}.

5. **Draft section by section, paragraph by paragraph.** Apply all four disciplines as you emit:
   - **Voice** (`voice.md` — all rules, strictly). See §Voice below.
   - **§10 never-list.** Check every sentence as you emit it. Restructure before committing; do not draft the pattern and defer. See §Never-list below.
   - **Paraphrase default.** Default to paraphrase; direct quotation is the exception. See §Paraphrase default below.
   - **Pandoc citation IDs.** Drop every citation as `[@id]`, `@id`, or `[@id, p. N]` — never as a rendered string. See §In-prose IDs below.

6. **Apply synthesis integrity (§4) as you write.** The outline did the mapping, but rewriting a claim into prose can drift it from the source. Check paraphrase scope, qualifier preservation, and attribution as each sentence goes in — not as a post-draft pass.

7. **Stale-byline check for narrative IDs.** Before emitting `@id` for narrative use (e.g., `@leman-nda-001 shows...`), check the log entry's `retrieved_at`. If it predates the current conversation's start or is missing, fire the §3 self-correction trigger: say "wait... I'm about to render an author I haven't verified from the source, let me check the page." Then announce `Switching to [research mode] (invoked from [writing mode])` and re-verify the byline. Return and continue once `retrieved_at` is updated. See manifest §7.3.

8. **First drafts are raw material, not output.** Cut filler as you go. Do not substitute generic academic phrasing for {{USER}}'s voice.

9. **On completion of a section,** present the prose and ask {{USER}} whether to continue to the next section or stop. Do not advance to [editing mode] on your own; the gate is {{USER}}-initiated only (manifest §7.4).

## Red Flags

- *"I'll draft this pattern and fix it in editing."* — No. §10 is a check-as-you-emit discipline. If the sentence wants a never-list pattern, rebuild the shape before committing the line.
- *"The outline claim says X; I'll round it up to Y in prose."* — Scope drift. Hold the qualifier. Check the log entry's `exact_quote` and `surrounding_context` as you write the sentence.
- *"This quote is strong — I'll use it directly."* — Run the 4-item test first. If none of (a)–(d) applies, paraphrase. Powerful-feel is not a carve-out.
- *"voice.md from earlier in the session is probably still accurate."* — Re-read it on every entry. Different projects carry different voices; memory from a prior session is not the file.
- *"I haven't verified the byline — I'll wrap it as `@id` and check later."* — No. The §3 self-correction trigger fires at write time for narrative IDs. Switch to [research mode] now.
- *"The refined outline is approved so I can skip re-reading the never-list."* — Re-read it. Restructure guidance is the part that degrades most from memory.

## Rationalizations

| Excuse | Reality |
|--------|---------|
| "The refined outline is the source of truth — I'll match it and trust [editing mode] for §10." | [editing mode] pass 6 re-audits §10, but catching a pattern there is more expensive: it interrupts the editing pass, requires restructuring in the middle of an eight-pass audit, and means the pattern survived into the draft. Check as you emit. |
| "The voice rule says X and §10 says the opposite — I'll go with the voice rule." | §10 > voice.md prose (manifest §7.6). The only override is a `## §10 exemptions` bullet in `voice.md` naming the canonical ID. Absence of a bullet is not permission. Surface the conflict on first occurrence. |
| "Paraphrase risks losing the source's precision — better to quote." | Run the 4-item test. If the wording is not the object of analysis, a qualifier is not lost, authority does not rest on formulation, and you will not push against the exact phrasing, paraphrase is both sufficient and preferable. |
| "The outline had a bare id (`smith-2010-001`) — I'll leave it bare in prose too." | Bare IDs are an outlining shorthand. At write time, every citation in prose wraps into Pandoc syntax (`[@id]`, `@id`, `[@id, p. N]`). See §In-prose IDs. |
| "The gate passed — [refining mode] approved the outline, so structural decisions are settled." | Structural decisions are settled. Citation scope and qualifier preservation are not — rewriting a claim into prose can still drift it from the source. Run §4 as you write, not only at editing time. |
| "This is a first draft; §10 is a second-pass concern." | §10 is a check-as-you-emit discipline in writing mode. A first draft that contains never-list patterns is not raw material; it is a §10 violation waiting in queue. |

## Quick Reference

```
ENTRY:   Switching to [writing mode]. writing <section>.

STEP 0:  Read voice.md (full). Read §Never-list (full). Load citation log.

EMIT EACH SENTENCE THROUGH:
  1. Voice (voice.md — all rules).
  2. §10 never-list — restructure before emitting, not after.
  3. Paraphrase default — 4-item test; quote only on (a)–(d).
  4. Pandoc IDs — [@id] / @id / [@id, p. N]. Never (Smith, 2010).
  5. §4 synthesis — scope, qualifiers, attribution as you write.

STALE BYLINE:  @id narrative → check retrieved_at → if stale, fire §3 trigger.

EXIT:    {{USER}}-initiated only → Switching to [editing mode].
```

## Exit Gates

**Allowed transitions (from writing):**
- → `[editing mode]`. Gate: {{USER}}-initiated only. Use `Switching to [editing mode].`
- → `[research mode]` via §3 self-correction auto-trigger (stale byline or unverified citation surfaced during drafting). Use `Switching to [research mode] (invoked from [writing mode]).` Return to writing once the gap is resolved with `Switching back to [writing mode].`
- → `[finetuning mode]` on {{USER}}-initiated local-substitution ask mid-draft. Announce the switch; resume writing after selection.
- → `[refining mode]` if writing reveals a structural problem the outline does not resolve. Surface the structural question and let {{USER}} direct the switch; do not restructure at prose level.

**Forbidden transitions:**
- → `[editing mode]` on your own. The gate is {{USER}}-initiated only (manifest §7.4).
- → `[formatting mode]` direct. Formatting requires edit-complete gate; writing does not produce a paste-ready artifact.
- → `[outlining mode]` direct. Upstream; if the outline is wrong, the path is through [refining mode], not back to outlining from here.

---

## Never-list

**Canonical source of truth for §10 pattern prose.** [editing mode] pass 6 reads this section directly. Each entry carries `[id: <canonical-id>]` for `sourced check` I3 parsing and for `voice.md`'s `## §10 exemptions` mechanism. The canonical ID list in manifest §7.6 is the mechanical validation source of truth; the prose here is the operational source of truth.

These patterns are not claims about bad prose in general. A human author may use any of them with control. The concern is reproduction: when this agent pads, transitions, or performs analytical depth, these are the shapes it reaches for by default. A reader familiar with AI output clocks them as machine rhythm even when a human author would deploy the same pattern cleanly.

### Pattern entries

**Em dashes** [id: em-dashes]

Em dashes (—) used for appositives, interruptions, or ranges. The problem is the mid-clause interruption rhythm, not the character itself. Do not substitute commas or parentheses while keeping the interruption rhythm; that preserves the shape the reader notices. Restructure: make the gloss a standalone sentence, relocate it to a natural position, or cut it entirely if it is not load-bearing.

**"Not X but Y"** [id: not-x-but-y]

The contrastive pivot shape: "not X but Y," "X, not Y," "less X than Y," "not merely X but Y," "it is not that X, but that Y." When contrast is load-bearing, make Y the direct assertion and position X in a separate clause or drop it. Reordering to "Y, not X" preserves the comparative-pivot shape and fails the audit. See also the cross-sentence retokenization rule below — splitting X and Y across a sentence boundary does not escape the pattern.

**Ornamental triads** [id: ornamental-triads]

Triadic or tetradic lists ("X, Y, and Z"; "X, Y, Z, and W") where items are parallel for rhythm rather than argument. A genuine enumeration whose three or four items each carry independent argumentative weight is not flagged. An ornamental cadence that exists to sound thorough is. Reduce to the one item that carries the argument; cut the others, or name them only if each does distinct work.

**Throat-clearing openers** [id: throat-clearing-openers]

Sentence-initial: "Crucially," "Ultimately," "Fundamentally," "Importantly," "In essence," "It is worth noting that," "It bears mentioning that," "What is striking is." These perform emphasis without adding content. The emphasis claim should be carried by the sentence itself: by what it says and where it sits in the paragraph. An adverbial endorsement prepended to the sentence performs emphasis without adding content. Cut the opener and let the sentence stand.

**Demonstrative-noun paragraph openers** [id: demonstrative-openers]

Paragraph openers such as "This tension," "These dynamics," "This shift," "Such patterns" where the demonstrative is doing work the prior paragraph did not earn. The antecedent must be specific and recent — the immediately preceding paragraph's conclusion, stated precisely, not a gestural summary of a section's theme. If the demonstrative does not have a specific recent antecedent, name the antecedent directly or restructure the opening.

**Ornamental compounds** [id: ornamental-compounds]

Hyphenated conceptual compounds that disappear after one use: "state-as-universal-life," "recognition-work," "meaning-disclosure-practice." Coining a compound is acceptable when the term recurs and carries argumentative weight across the essay. Coining one for a single paragraph is AI ornamentation — the compound exists to sound conceptually dense rather than to do analytic work. Use standard phrasing for single-use concepts; reserve compounds for terms that earn their coinage through recurrence.

### Density list

Acceptable once per essay; AI-ish when stacked. [editing mode] pass 6 flags any term appearing three or more times or any two sibling instances.

- **Abstract nominalizations**: "the convergence of," "the divergence over," "the question of where" — a verb clause reads more directly.
- **"For X… for Y…" parallel constructions** between clauses or sentences.
- **"As we shall see," "we come to see," "we can return to," "we must begin."**
- **Stacked sentence-initial participials**: "Drawing on X…", "Building on Y…", "Extending Z…" — two in a row is a signature.
- **"In this way" as a transition** — common in academic prose; becomes a tell at three or more occurrences per essay.

### Restructure, don't retokenize

Removing a never-list pattern requires changing the sentence **shape**, not swapping punctuation or reordering words.

When a pattern is flagged, identify the shape it produces — mid-clause interruption, balanced pivot, rhetorical escalation, ornamental triad — and rebuild around a different shape:

- An em-dashed appositive becomes a standalone sentence or is cut.
- A "not X but Y" becomes a direct assertion of Y, with X dropped or placed in a preceding sentence as independent background.
- An ornamental triad is reduced to the single item that carries the argument.

Substituting commas for em-dashes while keeping the interruption preserves the rhythm. Reordering "not X but Y" to "Y, not X" preserves the contrastive pivot. Neither counts as restructuring.

### Cross-sentence retokenization rule

Splitting X and Y across a sentence boundary does not escape the `not-x-but-y` pattern. "X. Y." where sentence 1 contains a clausal negation ("does not X," "is not X," "X never Y") and sentence 2 opens with a positive assertion that stands as the alternative — beginning with "It," "Instead," a pronoun co-referring to sentence 1's subject, or a noun phrase naming the alternative — is the same contrastive pivot as "not X but Y." A period is not structural change. The fix is to drop X, merge X into Y as a positive assertion, or place at least one sentence of unrelated content between them.

### Exemptions

A `## §10 exemptions` bullet in `voice.md` naming a canonical ID from the list above is the only override mechanism. Silence is not permission. Inline prose in `voice.md` arguing for a pattern without a matching exemption bullet has no runtime effect at write time or edit time (manifest §7.6). Unknown IDs fail `sourced check` install-time validation.

**Scope of an exemption.** An exemption suspends one never-list rule for this voice's writer prose. Each ID is independent. An exemption does not extend to prose generated on {{USER}}'s behalf that is not this voice's output ([red team mode] counter-phrasings, framework meta-commentary). The direct-quotations carve-out (root CLAUDE.md §10) is independent of exemptions.

**Runtime.** On entry to [writing mode] and [editing mode], scan `voice.md`'s `## §10 exemptions` section. If `voice.md` is missing, halt (see When to Use).

**Conflict surfacing.** If `voice.md` and §10 conflict without a matching exemption bullet, surface the conflict on first occurrence rather than resolving silently (manifest §7.6).

### Framework-meta carve-out

§10 governs generated academic prose: {{USER}}'s essay sentences, and agent-generated prose on {{USER}}'s behalf (drafts, paraphrases, counterphrasings, annotation blocks). §10 does not govern descriptive framework documentation written about the rules themselves — this file's own body prose, mode-body procedural prose in `docs/modes/`, and root `CLAUDE.md` manifest prose are framework meta, not academic prose. An em-dash appositive inside this file's description of the em-dash rule is not a rule violation; it is explanation. The carve-out is narrow: it covers framework files shipped by `sourced`, not any prose produced during a writing session. Read `editing mode`'s pass 6 accordingly — pass 6 audits the writer's draft against §10, not the framework's own documentation.

---

## Paraphrase default

Default to paraphrase. Direct quotation is the exception, not the standard option.

**Quote directly only when at least one of the following holds:**

- **(a) Wording as object of analysis.** The prose is analyzing the source's language itself — examining word choice, rhetorical structure, or specific phrasing as evidence.
- **(b) Qualifier or coined term lost in paraphrase.** Paraphrase would drop a hedge, condition, or coined term the argument depends on, and no paraphrase preserves it without adding your own words to carry what the original said in one.
- **(c) Authority rests on specific formulation.** The source's claim carries weight in this field because of how it is stated, and paraphrase would strip that force.
- **(d) You will push against the exact phrasing.** The prose will contest, qualify, or complicate the precise wording, making the original text itself the subject of the sentence.

In all other cases, paraphrase and run the §4 audit against the paraphrase using `exact_quote` and `surrounding_context` as ground truth.

**Flags that paraphrase is underused:**
- Direct-quote words exceed approximately 15% of a paragraph's word count.
- Two adjacent sentences both carry a direct quotation.

When a paragraph trips either flag, identify which quotes pass items (a)–(d) and convert the rest to paraphrase. Powerful-feel and vivid phrasing are not items (e) and (f); they are the rationalization for over-quoting.

**[editing mode] pass 7** re-applies this test to the finished prose and references this section by anchor. The 4-item test is the same at both write time and edit time; catching over-quoting at write time is cheaper.

---

## Voice

`voice.md` rules apply **strictly and in full** at write time — not only Paragraph Flow. [outlining mode] applies Paragraph Flow only; [writing mode] applies every section of `voice.md`. Do not elide sections.

**Read `voice.md` in full on every entry.** Memory from a prior session drifts. The file is the canonical source for this project's voice; different projects carry different voices.

**If `voice.md` is missing,** stop and ask {{USER}} to run `sourced switch voice <name>`. Do not guess rules and proceed.

**Interaction with §10.** §10 > voice.md prose (manifest §7.6, precedence rule 2). A voice rule that conflicts with a §10 pattern has no runtime effect unless `voice.md` carries a `## §10 exemptions` bullet naming the canonical ID. Inline voice prose — even prose that says "em dashes are acceptable in this voice" — is not an exemption unless it appears as a bullet under `## §10 exemptions` with a canonical ID. Conflict surfacing: if voice.md and §10 conflict without an exemption, surface the conflict on first occurrence.

**Sections to apply at write time** (all of them, but emphasize):
- `voice.md §Paragraph Flow` — handoff connectives between sentences; transition logic between paragraphs.
- All other sections your `voice.md` carries. The full set is calibrated per-author; the names vary across voice libraries. Apply every section.

**At write time, voice rules are generative**, not just corrective: draft sentences toward the voice, not against §10. The edit-time voice audit (editing.md pass 8) is corrective; the write-time discipline is to build sentences that already fit both.

---

## In-prose IDs

Citations in source prose carry as Pandoc-style ID references. [formatting mode] resolves each ID against the citation log and emits a style-compliant string. Prose stays decoupled from style.

**This is Moment 2 of the three-citation-moment system** (manifest §8). [outlining mode] may carry bare IDs (`smith-2010-001`) attached to paragraph claims; wrapping into Pandoc syntax happens at write time as the claim becomes prose.

### Pandoc syntax table

| Pandoc syntax | Use | APA-7 example output |
|---------------|-----|----------------------|
| `[@id]` | Parenthetical, paraphrase | `(Smith, 2010)` |
| `@id` | Narrative, paraphrase | `Smith (2010)` |
| `[@id, p. N]` | Parenthetical, single page locator | `(Smith, 2010, p. 42)` |
| `[@id, pp. N–M]` | Parenthetical, page range (en-dash between numbers) | `(Smith, 2010, pp. 42–44)` |
| `[@a; @b]` | Multiple sources, parenthetical | `(AuthorA, YearA; AuthorB, YearB)` |

### Rules

**Never emit a rendered citation string in source prose.** A string like `(Smith, 2010)` or `Smith (2010)` in source prose is a regression. It short-circuits the renderer, defeats the byline-discipline guarantee (rendered author names bypass the log-verified `source.authors` field), and will be flagged in [editing mode] pass 1. [editing mode] pass 1 requires surfacing rendered-citation regressions to {{USER}} before converting — silent conversion is not allowed.

**Narrative IDs and stale-byline check.** `@id` (narrative) will produce a visible author name when [formatting mode] renders. Before wrapping a citation as `@id` for narrative use, check the log entry's `retrieved_at`. If it predates the current conversation's start or is missing, fire the §3 self-correction trigger and switch to [research mode] for byline re-verification. See Steps 7 and manifest §7.3.

### Special tokens

Two special tokens may appear in source prose during drafting:

- **`[VERIFY: ...]`** — a bibliographic detail you are not certain of (page number, year, DOI). Resolve before format time.
- **`[UNSOURCED]`** — a claim that has no source yet. Resolve before format time.

Both are format-time blockers per [formatting mode]'s pre-flight. Do not leave either token in prose you present as ready for editing without surfacing it to {{USER}}.

---

## Block quotes

Direct quotes longer than roughly 40 words go in a block quote. Format at source-prose level:

- Indent the quoted text.
- No quotation marks enclosing the block.
- Place the Pandoc citation at the closing position, after the closing punctuation of the quoted text: e.g., `[@smith-2010-001, p. 42]`.

The block-quote convention is style-agnostic at source-prose level. [formatting mode] delegates citation rendering for block-quoted passages to pandoc+CSL; the CSL encodes the style's direct-quote conventions.

**Direct-quotations carve-out (§4 governing rule).** §10 never-list patterns inside a direct quotation are not flagged. The quoted text is evidence, not generated prose. Preserve the source's punctuation verbatim inside the quoted span, including em dashes, ornamental triads, and any other pattern §10 would otherwise catch. §4 *Quote verbatim* is the governing rule; §10 is suspended inside the quoted span. See root CLAUDE.md §10 *Direct quotations carve-out* for the full carve-out definition and its limits (it is narrow: it covers the quoted span, not the writer's framing sentence next to it).

---

## What this mode does NOT do

- **Audit the full draft for §10 hits.** [editing mode] pass 6 does that. Write-time discipline is check-as-you-emit; pass 6 is the systematic audit over finished prose. The two are complementary, not redundant.
- **Render APA / MLA / Chicago strings.** [formatting mode] does that. Source prose carries Pandoc IDs only.
- **Make structural decisions unilaterally.** If writing reveals a structural problem, surface it and let {{USER}} direct the path back to [refining mode].
- **Advance to [editing mode] without {{USER}}'s initiation.** The writing → editing gate is {{USER}}-initiated only (manifest §7.4).
- **Run citation audits as a post-draft pass.** §4 synthesis integrity applies sentence by sentence during drafting, not as a sweep after the section is done.

## See also

- `CLAUDE.md §3` — source verification; stale-byline self-correction trigger at write time (§7.3).
- `CLAUDE.md §4` — synthesis integrity; paraphrase scope, qualifier preservation, attribution.
- `CLAUDE.md §7.2` — explicit triggers (source of truth).
- `CLAUDE.md §7.4` — mode-to-mode gate table; `refining → writing` gate and `writing → editing` gate.
- `CLAUDE.md §7.5` — forcing artifacts: §4 audit list (emitted by [refining mode] before the gate here).
- `CLAUDE.md §7.6` — precedence rules, canonical §10 ID list, direct-quotations carve-out.
- `CLAUDE.md §8` — citation three-moment system; Moment 2 in-prose IDs (this file's §In-prose IDs).
- `docs/modes/refining.md` — predecessor; the §4 audit list this mode requires at entry.
- `docs/modes/editing.md` — successor; pass 6 reads `docs/modes/writing.md#never-list`; pass 7 reads `docs/modes/writing.md §Paraphrase default`.
- `docs/modes/research.md` — target for stale-byline and unsourced-claim auto-triggers fired during writing.
- `voice.md` — voice rules loaded at step 2; `## §10 exemptions` bullets read at step 3.
- `~/.claude/citations/schema.md §Staleness` — `retrieved_at` staleness threshold used in the stale-byline check.
