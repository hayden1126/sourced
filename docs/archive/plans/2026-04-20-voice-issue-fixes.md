# Voice-issue fixes (Issues 1–4) Implementation Plan

**Status:** Shipped 2026-04-20/21 (finetuning mode, §10 cross-sentence rules, and citation-log verification fields are all in the shipped bundle). Follow-up mental-verb audit: issue #32.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply framework fixes for the four issues in `voice_issue.md` — §10 cross-sentence blind spot, citation-log integrity, `[editing mode]` phase gaps, and new `[finetuning mode]` — with PE-revised wording that uses externalized fields instead of mental-verb checks.

**Architecture:** This plan edits prompt/rule files, not runtime code. The three files that actually bind LLM behavior (`templates/CLAUDE.md`, `agents/source-finder.md`, `citations/schema.md`) carry new language and new schema fields. Verification is by grep + dispatch test against the real audit-caught log (`report_3.citations.json`). Changes are grouped into three PRs so correctness-critical fixes ship first.

**Tech Stack:** Markdown prompt files; JSON citation-log schema; bash grep for verification; the existing `source-finder` subagent as a dispatch target for behavior validation.

**Scope note:** No new subagent. `citation-auditor` was considered and rejected in design discussion — the audit-at-logging-time job folds into `source-finder.md`'s workflow, and the audit-at-edit-time job folds into `[editing mode]` pass 2.

**PR grouping:**
- **PR 1 (correctness-critical):** Tasks 1–4 (Issue 1 + Issue 2 in full).
- **PR 2 (usability addition):** Task 5 (Issue 4 `[finetuning mode]`).
- **PR 3 (editing-mode tightening):** Task 6 (Issue 3 one-pass + handoff).

**Budget summary:**
- `templates/CLAUDE.md`: +~45 lines (from ~690 to ~735).
- `citations/schema.md`: +~40 lines.
- `agents/source-finder.md`: +~35 lines.
- `templates/voices/academic.md`: +~2 lines.

---

## Task 1: Issue 1 — §10 cross-sentence blind spot

**Files:**
- Modify: `templates/CLAUDE.md` §10 *Restructure, don't retokenize* paragraph (around line 678)
- Modify: `templates/voices/academic.md` iteration loop (lines 83–91)

**Root cause:** §10's phrase `relocated to its own clause` reads as license to promote X to its own sentence; the failure list doesn't name period-split variants. Fix tightens the permissive clause and adds one bullet naming the period-split.

- [ ] **Step 1.1: Tighten the "relocated to its own clause" clause in §10**

Use Edit on `templates/CLAUDE.md`:

```
old_string: a "not X but Y" becomes a direct assertion of Y with X dropped or relocated to its own clause; an ornamental triad is reduced to the one item that carries the argument.
new_string: a "not X but Y" becomes a direct assertion of Y with X dropped, or restructured so that X and Y are no longer adjacent in the argument's surface rhythm (a period between them does not count; neither does a single bridging sentence); an ornamental triad is reduced to the one item that carries the argument.
```

- [ ] **Step 1.2: Extend the retokenization failure list with the period-split variant**

Use Edit on `templates/CLAUDE.md`:

```
old_string: Substituting commas for em-dashes, or reordering "not X but Y" into "Y, not X," preserves the rhythm that reads as AI.
new_string: Substituting commas for em-dashes, or reordering "not X but Y" into "Y, not X," preserves the rhythm that reads as AI. Splitting X and Y across sentence boundaries while preserving the X→Y contrastive sequence is the same failure: "X. Y." where X negates and Y asserts the alternative functions as the same contrastive pivot as "not X but Y." A period is not structural change. Concretely: any two adjacent sentences where sentence 1 contains a clausal negation ("does not X," "is not X," "X never Y") and sentence 2 opens with a positive assertion that stands as the alternative to the negated content (often beginning with "It," "Instead," a pronoun co-referring to sentence 1's subject, or a noun phrase naming the alternative). The fix is to drop X, merge X into Y as a positive assertion, or place at least one sentence of unrelated content between them.
```

- [ ] **Step 1.3: Add the iteration-loop bullet to academic.md**

Use Edit on `templates/voices/academic.md`:

```
old_string: - **Does it read fluidly aloud, or does the reader trip on it?** A clipped fragment ("none of the three resolves"), a stranded preposition that lands awkwardly ("where is the 'there' the stem points at?"), or a register-high verb where a plain one would carry the meaning ("legible" where "visible" works) all signal over-compression. Restore the word or restructure around a different shape.
- Does the section flow when read start to finish?
new_string: - **Does it read fluidly aloud, or does the reader trip on it?** A clipped fragment ("none of the three resolves"), a stranded preposition that lands awkwardly ("where is the 'there' the stem points at?"), or a register-high verb where a plain one would carry the meaning ("legible" where "visible" works) all signal over-compression. Restore the word or restructure around a different shape.
- **Does a negation sentence sit immediately before an affirmation that asserts the alternative?** That is §10's "not X but Y" pattern retokenized with a period; break the adjacency or drop the negation.
- Does the section flow when read start to finish?
```

- [ ] **Step 1.4: Verify all three edits landed**

Run:
```
grep -n "no longer adjacent in the argument's surface rhythm" templates/CLAUDE.md
grep -n "A period is not structural change" templates/CLAUDE.md
grep -n "retokenized with a period" templates/voices/academic.md
```
Expected: each returns exactly one line match.

- [ ] **Step 1.5: Commit**

```bash
git add templates/CLAUDE.md templates/voices/academic.md
git commit -m "$(cat <<'EOF'
Close §10 cross-sentence retokenization blind spot

Tightens the "relocated to its own clause" clause so "X. Y." period-splits
of "not X but Y" no longer read as permitted. Adds one iteration-loop
bullet in academic.md as self-audit insurance.
EOF
)"
```

---

## Task 2: Issue 2A — Schema changes for externalized verification fields

**Files:**
- Modify: `citations/schema.md`

**Root cause:** Existing rules are phrased as mental acts (`verify`, `cross-check`). LLMs rationalize past them. Fix moves verification to externalized fields that the merge-protocol validator inspects.

- [ ] **Step 2.1: Tighten the `exact_quote` field definition**

Use Edit on `citations/schema.md` to replace the short definition embedded in the JSON block comment. The current definition is on the `exact_quote` line of the entry structure:

```
old_string:   "exact_quote": "verbatim text from the source that supports the claim",
new_string:   "exact_quote": "a single contiguous verbatim span copied from the rendered source at the location this entry records (see §Verification fields); never a paraphrase, synthesis across passages, or reconstruction from memory",
```

- [ ] **Step 2.2: Add a new `## Verification fields` section after the `## Author-field provenance` section**

Use Edit on `citations/schema.md`:

```
old_string: ## `citation_string` is informational
new_string: ## Verification fields

Four sub-fields inside `retrieval` force externalized, validator-checkable evidence that `exact_quote` and `location` are grounded in the rendered source. These exist because discipline-level rules ("verify," "cross-check") are rationalized past by logging agents; a field conspicuously missing or malformed is not.

- `retrieval.printed_page_observed` — string. The printed page number visible on the rendered page header/footer, copied verbatim from the rendered view, OR the literal string `"not visible"` if the header/footer does not show one (scanned image, missing header, digital-only). Required on every entry whose source is paginated.
- `retrieval.tool_page_index` — integer. The tool-reported page index (PDF page number, sequential page in a reader). Recorded alongside `printed_page_observed` so the offset between them is explicit.
- `retrieval.pdf_page_offset` — integer. The difference between `tool_page_index` and `printed_page_observed`, recorded once per source. Subsequent entries from the same source reuse the recorded offset rather than recomputing it.
- `retrieval.verification_trace` — object. `{"first_20": "...", "last_20": "..."}` — the first 20 and last 20 characters of `exact_quote` as they appeared in the rendered view, verbatim. Lets the parent's merge-protocol validator spot-check that the span is a real copy, not a reconstruction. Required on every entry with `verification_status: "verified"` whose `exact_quote` is not in list-shape (reference works, see below).
- `retrieval.per_entity_locators` — array of `{entity: string, locator: string}`. Required when `exact_quote` enumerates multiple named entities, terms, or claims. Each object records the rendered locator (URL anchor, page, section) where that specific entity is attested. Forces the multi-entity scope check.

`location` must equal `retrieval.printed_page_observed` for paginated sources (or the corresponding value for section-/chapter-/timestamp-keyed sources). The merge-protocol validator rejects entries where they disagree.

## `citation_string` is informational
```

- [ ] **Step 2.3: Add list-shape for reference works — new subsection after the `## Verification fields` section**

Use Edit on `citations/schema.md`:

```
old_string: ## Allowed enum values
new_string: ## Reference-work shape for `exact_quote`

For sources where no prose can be quoted verbatim (dictionaries, wordlists, gazetteers, structured glossaries), `exact_quote` may be a JSON array of objects instead of a string:

```json
"exact_quote": [
  {"headword": "Ma'heo'o", "definition": "sacred mystery; sacred power", "locator": "entry M, p. 312"},
  {"headword": "Voestaa'e", "definition": "white woman (proper name)", "locator": "entry V, p. 489"}
]
```

Each item's fields are verbatim from the source. When `exact_quote` is in list-shape, `retrieval.verification_trace` is not required (the locators inside each item serve the same forcing function), but `retrieval.per_entity_locators` is also not required (the list itself carries locators). Whitespace, a paraphrase, a descriptive summary, or a placeholder is never an acceptable substitute for the list-shape; if you cannot populate the list, reject per section 3.

## Allowed enum values
```

- [ ] **Step 2.4: Tighten the merge-protocol validator**

Use Edit on `citations/schema.md` to replace the current step-2 validation line in the merge protocol:

```
old_string: 2. For each entry, validate against the schema (required fields present, enum values legal, `exact_quote` and `surrounding_context` non-empty).
new_string: 2. For each entry, validate against the schema. Required fields present; enum values legal. Hard-fail each of the following:
   - `exact_quote` and `surrounding_context` empty, whitespace-only, or punctuation-only. "Non-empty" means at least one non-whitespace, non-punctuation character.
   - Paginated source (entry's `source.volume_issue_pages` is set) without `retrieval.printed_page_observed`.
   - `verification_status: "verified"` with string-shape `exact_quote` lacking `retrieval.verification_trace`.
   - `exact_quote` enumerating more than one named entity (names, terms, distinct claims) without `retrieval.per_entity_locators` covering each.
   - `location` disagreeing with `retrieval.printed_page_observed` on paginated sources.
   A hard-fail entry is surfaced to {{USER}} with the specific rule that fired; do not merge it. The three resolution paths below (fix in place, drop and merge rest, abandon) apply, with one carve-out: when the hard-fail is `verification_trace missing`, `per_entity_locators missing`, or `exact_quote enumerating multiple entities`, the "fix in place" path is NOT available. The source must be re-opened and the entry re-logged; reconstructing verification_trace from memory is exactly the failure these fields exist to block. Fix-in-place is reserved for formatting-only issues (whitespace trim, location-offset recorded incorrectly against an already-correct printed_page_observed).
```

- [ ] **Step 2.5a: Add a correct-entry exemplar in schema.md**

Agents pattern-match to examples more reliably than to prose rules. Add a positive exemplar alongside the existing `{...}` entry structure. Use Edit on `citations/schema.md` to insert a new subsection after the `## Reference-work shape for exact_quote` section you added in Step 2.3:

```
old_string: ## Allowed enum values
new_string: ## Correct-entry exemplar

A valid entry under the new schema looks like this. Every externalized verification field is populated; `location` equals `retrieval.printed_page_observed`; multi-entity entries carry per-entity locators.

```json
{
  "id": "smith-2010-001",
  "source": {
    "authors": ["Smith, Jane A."],
    "year": 2010,
    "title": "Title of Work",
    "publication": "Journal Name",
    "volume_issue_pages": "42(3), 12–34",
    "doi_or_url": "https://doi.org/10.xxxx/yyyy"
  },
  "location": "p. 24",
  "exact_quote": "inhibitory control, the cognitive capacity to suppress a dominant response in favor of a context-appropriate alternative",
  "surrounding_context": "Subjects high on measures of executive function consistently outperform controls on tasks requiring inhibitory control, the cognitive capacity to suppress a dominant response in favor of a context-appropriate alternative. This effect replicates across age groups.",
  "context_description": "Smith is defining inhibitory control as part of her executive-function framework",
  "claim_supported": "inhibitory control is the capacity to suppress a dominant response",
  "citation_string": "(Smith, 2010, p. 24)",
  "provisional_reference": "subtopic:executive-function",
  "draft_reference": null,
  "verification_status": "verified",
  "retrieval": {
    "source_path": "https://doi.org/10.xxxx/yyyy",
    "printed_page_observed": "p. 24",
    "tool_page_index": 38,
    "pdf_page_offset": 14,
    "verification_trace": {
      "first_20": "inhibitory control, ",
      "last_20": "riate alternative"
    }
  },
  "retrieved_at": "2026-04-20T09:00:00Z",
  "added_at": "2026-04-20T09:03:00Z"
}
```

A multi-entity entry additionally carries `retrieval.per_entity_locators` — one object per named entity with its own `locator` field.

## Allowed enum values
```

- [ ] **Step 2.5b: Add spot-check rule for verification_trace**

An agent can still fabricate `first_20` and `last_20` from memory. Adding parent-thread spot-checking as the outer-layer defense. Use Edit on `citations/schema.md`:

```
old_string: A hard-fail entry is surfaced to {{USER}} with the specific rule that fired; do not merge it. The three resolution paths below (fix in place, drop and merge rest, abandon) apply, with one carve-out: when the hard-fail is `verification_trace missing`, `per_entity_locators missing`, or `exact_quote enumerating multiple entities`, the "fix in place" path is NOT available. The source must be re-opened and the entry re-logged; reconstructing verification_trace from memory is exactly the failure these fields exist to block. Fix-in-place is reserved for formatting-only issues (whitespace trim, location-offset recorded incorrectly against an already-correct printed_page_observed).
new_string: A hard-fail entry is surfaced to {{USER}} with the specific rule that fired; do not merge it. The three resolution paths below (fix in place, drop and merge rest, abandon) apply, with one carve-out: when the hard-fail is `verification_trace missing`, `per_entity_locators missing`, or `exact_quote enumerating multiple entities`, the "fix in place" path is NOT available. The source must be re-opened and the entry re-logged; reconstructing verification_trace from memory is exactly the failure these fields exist to block. Fix-in-place is reserved for formatting-only issues (whitespace trim, location-offset recorded incorrectly against an already-correct printed_page_observed).

**Parent-thread spot-check.** The `verification_trace` field can be fabricated by an agent from memory, which defeats its purpose. The academic-researcher (parent thread), on every merge pass, picks up to 3 entries randomly (or by highest-stakes: verified entries cited in a load-bearing paragraph). For each picked entry, open the source at `retrieval.source_path` (or `source.doi_or_url`), locate `exact_quote`, and confirm that the actual first-20 and last-20 characters match `verification_trace`. Mismatches are surfaced as `spot-check-failed` incidents and the entry is unmerged. Spot-checks scale with batch size: 1 entry per 4 merged, capped at 3. Record spot-check outcomes in the merge report to {{USER}}.
```
- [ ] **Step 2.6: Verify all schema edits landed**

Run:
```
grep -n "contiguous span of verbatim text" citations/schema.md
grep -n "^## Verification fields" citations/schema.md
grep -n "^## Reference-work shape" citations/schema.md
grep -n "printed_page_observed" citations/schema.md
grep -n "verification_trace" citations/schema.md
grep -n "per_entity_locators" citations/schema.md
grep -n "non-whitespace, non-punctuation" citations/schema.md
```
Expected: `printed_page_observed` appears 5+ times; `verification_trace` 3+ times; `per_entity_locators` 3+ times; each heading and tightened definition returns one match. Also run `grep -n "^## Correct-entry exemplar" citations/schema.md` and `grep -n "Parent-thread spot-check" citations/schema.md` — one match each.

- [ ] **Step 2.7: Commit**

```bash
git add citations/schema.md
git commit -m "$(cat <<'EOF'
Add externalized verification fields to citation schema

Introduces retrieval.printed_page_observed, tool_page_index,
pdf_page_offset, verification_trace, and per_entity_locators.
Tightens exact_quote definition to reject paraphrase-as-verbatim.
Adds list-shape for reference works and a correct-entry exemplar.
Hardens the merge-protocol validator to reject whitespace-only
strings, missing verification fields, and multi-entity quotes
without per-entity locators. Adds parent-thread spot-check (1 per
4 merged, cap 3) to catch fabricated verification traces.
EOF
)"
```

---

## Task 3: Issue 2B — source-finder workflow + negative exemplars

**Files:**
- Modify: `agents/source-finder.md`

**Root cause:** source-finder's current workflow says "verify" and "read the relevant passage" but never forces externalized output, never prohibits synthesis explicitly, and never pattern-matches against known failure modes.

- [ ] **Step 3.1: Tighten the "Never fabricate" rule**

Use Edit on `agents/source-finder.md`:

```
old_string: - **Never fabricate.** If you can't access a source's full text, reject it and report. Don't guess, don't paraphrase an abstract as if it were the source.
new_string: - **Never fabricate.** If you can't access a source's full text, reject and report. If you are not looking at the rendered passage at the moment you type the `exact_quote` field, you are composing from memory — re-open the source. Never write a synthesized, summarized, or reconstructed quote into `exact_quote`; that field is for contiguous verbatim spans only. If the rendered passage is truncated or returned with render warnings, reject under `subagent-render-failed` rather than completing the span from prior knowledge of the work. If multiple passages could support the claim, log the one with the most specific wording, not the first match.
```

- [ ] **Step 3.2: Add a new workflow step 4.5 between steps 4 and 5**

Use Edit on `agents/source-finder.md`:

```
old_string: 5. **Log each verified citation** using the schema below.
new_string: 5. **Produce a verification trace before marking `verification_status: "verified"`.** Populate these `retrieval` sub-fields in the same pass as `exact_quote`, copying verbatim from the rendered view:
   - `printed_page_observed`: the printed page number from the rendered page header/footer, or the literal string `"not visible"`.
   - `tool_page_index`: the tool-reported page index (PDF page number or reader sequential index).
   - `verification_trace`: `{"first_20": "...", "last_20": "..."}`, the first and last 20 characters of your `exact_quote` exactly as they appeared in the rendered view.
   - `per_entity_locators`: required when `exact_quote` enumerates multiple names, terms, or claims — one locator per entity, copied verbatim from where that entity appears in the rendered view.

   `location` must equal `printed_page_observed` for paginated sources. If the two differ, record the offset once in `pdf_page_offset` and reuse for subsequent entries from this source.

   **Default action on uncertainty is reject, not revise.** Revising is allowed only when you can re-open the source and produce the corrected span in one pass; otherwise reject.

   If `exact_quote` cannot be populated with a verbatim contiguous span (reference works — dictionaries, wordlists, gazetteers), use the list-shape defined in `~/.claude/citations/schema.md` §Reference-work shape. Do not populate with whitespace, a description of the passage, or a placeholder — those fail merge-protocol validation.

6. **Log each verified citation** using the schema below.
```

(Note: this insert renumbers the existing step 5 to step 6; the existing step 6 "Stop when you have 2 to 4 strong sources…" becomes step 7.)

- [ ] **Step 3.3: Renumber the old step 6**

Use Edit on `agents/source-finder.md`:

```
old_string: 6. **Stop when you have 2 to 4 strong sources**
new_string: 7. **Stop when you have 2 to 4 strong sources**
```

- [ ] **Step 3.4: Add a "Negative exemplars" section before the "Rules" section**

Use Edit on `agents/source-finder.md`:

```
old_string: ## Rules
new_string: ## Negative exemplars (reject on sight)

Two patterns observed in a real audit of a logged citation file on 2026-04-20. Both passed `verification_status: "verified"` under the old workflow. Under the new workflow (step 5), both hard-fail.

**Rejected — synthesis posing as verbatim.** The source page asserted only that the deity name lacked high pitch. The logging agent wrote a quote combining the pitch claim with an unrelated morphological claim from elsewhere on the page:

```json
"exact_quote": "The deity name Ma'heo'o lacks both high pitch and the morpheme-final /h/ of the -héh stem"
```

The `/h/ / -héh` half was inferred across passages. Synthesis-as-verbatim is the most common logging failure; the contiguous-verbatim rule in step 5 and the verification_trace field exist to catch it.

**Rejected — entities off-page.** The logging agent cited `names1.htm` (an A–K wordlist page) but included in `exact_quote` three names starting with V and P, which live on `names3.htm` (O–X):

```json
"source.doi_or_url": "https://cdkc.edu/names1.htm",
"exact_quote": "... Voestaa'e, Pȧhoevotona'e, Ve'kėseha'e ..."
```

The entities are real, just not at the cited URL. The `per_entity_locators` requirement for multi-entity quotes in step 5 catches this: each entity must carry its own rendered locator, and if the locator points away from `source.doi_or_url`, either log the entity to its actual URL or exclude it.

**Rejected — abstract-body conflation (general-domain case).** The source article's abstract summarizes one claim; the body discussion develops a nuanced qualified version. The logging agent conflated them into a single `exact_quote`:

```json
"location": "p. 1142",  // abstract page
"exact_quote": "Minimum-wage increases reduce employment in low-skill sectors, though the magnitude depends on local labor-market slack and the pre-shock wage distribution"
```

The abstract on p. 1142 states only the first clause; the qualifier about labor-market slack appears on p. 1149 and the wage-distribution point is in a footnote on p. 1151. All three statements exist in the source, but not contiguously at the cited location. The contiguous-span rule rejects this; `verification_trace` would not match because the full span does not appear anywhere in the rendered source.

## Rules
```

- [ ] **Step 3.5: Verify source-finder edits landed**

Run:
```
grep -n "not looking at the rendered passage at the moment you type" agents/source-finder.md
grep -n "verification_trace" agents/source-finder.md
grep -n "per_entity_locators" agents/source-finder.md
grep -n "^## Negative exemplars" agents/source-finder.md
grep -n "Default action on uncertainty is reject" agents/source-finder.md
grep -n "^7. \*\*Stop when you have" agents/source-finder.md
```
Expected: each query returns exactly one line match; the old "6. Stop when…" no longer appears.

- [ ] **Step 3.6: Commit**

```bash
git add agents/source-finder.md
git commit -m "$(cat <<'EOF'
Force externalized verification in source-finder workflow

Adds workflow step 5 requiring per-entry retrieval.printed_page_observed,
verification_trace, and per_entity_locators before marking verified.
Tightens the Never-fabricate rule to prohibit memory-composed quotes
and first-match anchoring. Adds two negative exemplars drawn from
the 2026-04-20 report_3.citations.json audit.
EOF
)"
```

---

## Task 4: Issue 2C — CLAUDE.md `[editing mode]` re-verification trigger

**Files:**
- Modify: `templates/CLAUDE.md` §7 `[editing mode]` pass 2 (around line 412)

**Root cause:** `[editing mode]` already audits the log on pass 2 but only against the log, not against the source. Entries logged before the new verification fields existed, or whose `retrieved_at` is stale, or whose printed_page_observed is "not visible" all need a source re-open on draft touch.

- [ ] **Step 4.1: Extend pass 2 with the re-verification trigger**

Use Edit on `templates/CLAUDE.md`. The current pass 2 text ends with: "This audit is not optional. It runs every time [editing mode] engages with a draft that has citations." Replace:

```
old_string: **2. §4 citation audit.** For every citation in the section being edited, run the section 4 audit against the current prose (scope, attribution, byline, inference, cherry-pick, plus synthesis for multi-citation claims). If a check fails, either revise the prose or update the log entry's `claim_supported` and flag the change to {{USER}}. This audit is not optional. It runs every time [editing mode] engages with a draft that has citations.
new_string: **2. §4 citation audit.** For every citation in the section being edited, run the section 4 audit against the current prose (scope, attribution, byline, inference, cherry-pick, plus synthesis for multi-citation claims). If a check fails, either revise the prose or update the log entry's `claim_supported` and flag the change to {{USER}}. For any entry whose `retrieved_at` is stale per schema.md §Staleness, OR whose `retrieval.printed_page_observed` is missing or equals `"not visible"`, OR whose audit surfaces scope/attribution/byline drift: re-open the source and, against the rendered passage, overwrite `retrieval.verification_trace` with the first-20 and last-20 characters of `exact_quote` copied from the rendered view. If the rendered passage no longer matches `exact_quote` character-for-character, do not proceed with the pass — surface to {{USER}} as a source-drift incident with the mismatching characters named. On successful re-verification, update `retrieved_at` and the relevant retrieval fields. This audit is not optional. It runs every time [editing mode] engages with a draft that has citations.
```

- [ ] **Step 4.2: Verify the edit landed**

Run:
```
grep -n "re-open the source and re-verify" templates/CLAUDE.md
```
Expected: one line match inside the `[editing mode]` pass 2.

- [ ] **Step 4.3: Dry-run the new rules against the real audit log**

Run against the log that surfaced the original errors:
```
jq '.[] | select(.id | test("leman-nda-00[12]|leman-ndc-001|moore-1984-005|grinnell-1923-001|fisher-2024-001")) | {id, has_trace: (.retrieval | type == "object" and has("verification_trace")), has_printed_page: (.retrieval | type == "object" and has("printed_page_observed")), has_per_entity: (.retrieval | type == "object" and has("per_entity_locators"))}' /home/hayden/writing/report_3.citations.json
```
Expected: every named entry returns `false` for all three flags, confirming that under the new merge validator all five would hard-fail and be surfaced to {{USER}}. (This is not a code test; it's a sanity check that the new rules would have caught the real errors.)

- [ ] **Step 4.4: Commit**

```bash
git add templates/CLAUDE.md
git commit -m "$(cat <<'EOF'
Extend [editing mode] pass 2 to re-open source on staleness/drift

Triggers source re-fetch and verification-field population when an
entry's retrieved_at is stale, printed_page_observed is missing or
"not visible", or the audit surfaces scope/attribution/byline drift.
Closes the audit-at-edit-time gap that would have caught the 2026-04-20
report_3 errors before they shipped.
EOF
)"
```

---

## Task 5: Issue 4 — Add `[finetuning mode]`

**Files:**
- Modify: `templates/CLAUDE.md` §7 (new mode between `[editing mode]` and `[formatting mode]`)
- Modify: `templates/CLAUDE.md` §7 mode-switching table (around line 494)

**Root cause:** No existing mode handles the "user wants 3–5 alternatives for a local substitution" interaction. `[editing mode]` is too heavy; `[collaborative mode]` is too loose; `[writing mode]` collapses the decision.

- [ ] **Step 5.1: Insert `### [finetuning mode]` between `[editing mode]` and `[formatting mode]`**

Use Edit on `templates/CLAUDE.md`. Anchor on the `### [formatting mode]` heading:

```
old_string: ### [formatting mode]

*On entry, read `./style.md` in full. If style.md is missing, stop and ask {{USER}} to run `install.sh --style <name>`. Re-read on every entry; do not work from memory of prior sessions.*
new_string: ### [finetuning mode]

*Activation: {{USER}}-only, via explicit or implicit trigger. **Explicit:** {{USER}} names the mode (`[finetune: title]`, `[finetune paragraph 3 sentence 2]`, `[finetune this word]`). **Implicit trigger function:** fires when a message (a) names a specific phrase, word, or sentence in the draft AND (b) expresses negative evaluation ("feels wrong," "is off," "not quite," "doesn't work," "something's off about," "not sure about," "can you try") AND NOT (c) asks for a specific named change. Any message meeting all three is an implicit trigger; announce entry and let {{USER}} correct if the read was wrong. When in doubt, announce entry — false positives are cheap; implicit substitution (the failure mode this mode exists to prevent) is expensive.*

Purpose: produce a bounded range of alternatives for a targeted local substitution so {{USER}} chooses before anything is committed.

Scope: one word to one paragraph. Anything larger goes through `[refining mode]` or `[editing mode]`.

**Procedure.**

1. Announce entry: `Switching to [finetuning mode].` Name the scope in one sentence ("finetuning the title" / "finetuning the verb in paragraph 3 sentence 2").
2. Produce 3–5 alternatives. Each alternative declares a distinct **tradeoff axis** from: **scope** (what it covers), **register** (formal/casual, academic/plain), **emphasis** (what the phrase foregrounds), **structure** (sentence shape, syntactic frame), **rhythm** (cadence, syllable pattern), **diction** (which semantic neighborhood of meaning the word lands in — near-synonym substitution with different semantic shade, e.g., "legible" vs "visible" vs "discernible"). Each axis appears at most once per batch; if two alternatives share an axis, collapse them. An alternative without a declared axis is a protocol violation.
3. For each alternative, name its tradeoff in one clause: what it gains, what it gives up.
4. **Do not implement.** Inside `[finetuning mode]`, a single-option substitution is never a "small call" regardless of scope. §5's small-call list (polish, obvious prose fixes, merging redundant sentences, APA formatting, weak-adverb cuts) does NOT apply; all substitutions are gated on explicit selection. Silent acknowledgement ("hm," "ok") is not approval; neither is {{USER}}'s next message on an unrelated topic. If {{USER}}'s request overflows the mode's one-word-to-one-paragraph scope (e.g., alternatives for a whole-section restructure), announce entry to `[refining mode]` instead and punt — do not try to handle the overflow in this mode.
5. On selection, apply the chosen alternative. On variant request ("C but with X instead of Y"), generate the variant and confirm before applying.
6. Announce return: `Switching back to [<prior mode>].` Read the prior mode from the earlier mode-switch line (same discipline as `[research mode]`'s return protocol).

**What `[finetuning mode]` does NOT do:**
- Audit citations, §10, or voice. Those belong in `[editing mode]`.
- Restructure the argument. That belongs in `[refining mode]`.
- Regenerate beyond the scope named. Word-level finetuning does not rewrite the sentence.
- Pick a single option and ship it. That is the failure mode this mode exists to prevent.

### [formatting mode]

*On entry, read `./style.md` in full. If style.md is missing, stop and ask {{USER}} to run `install.sh --style <name>`. Re-read on every entry; do not work from memory of prior sessions.*
```

- [ ] **Step 5.2: Add the mode to the mode-switching table**

Use Edit on `templates/CLAUDE.md`:

```
old_string: | "red team this" | [red team mode] |
new_string: | "finetune this" / "give me alternatives for X" / "[finetune: ...]" | [finetuning mode] |
| "red team this" | [red team mode] |
```

- [ ] **Step 5.3: Verify the mode was added correctly**

Run:
```
grep -n "^### \[finetuning mode\]" templates/CLAUDE.md
grep -n "tradeoff axis" templates/CLAUDE.md
grep -n "finetune this" templates/CLAUDE.md
```
Expected: one heading match, one axis-rule match, one table-row match.

- [ ] **Step 5.4: Commit**

```bash
git add templates/CLAUDE.md
git commit -m "$(cat <<'EOF'
Add [finetuning mode] for bounded local-substitution alternatives

New mode for the "user wants 3–5 options for a specific phrasing"
interaction. Requires distinct tradeoff axis per alternative (scope,
register, emphasis, structure, rhythm). Explicitly suspends §5
medium-autonomy small-call discretion inside the mode so no
substitution lands without explicit selection.
EOF
)"
```

---

## Task 6: Issue 3 — `[editing mode]` proofreading pass + structural-deviation handoff

**Files:**
- Modify: `templates/CLAUDE.md` §7 `[editing mode]` (passes 4 and 5; top of mode block)

**Scope decision:** Do not import the UofT three-phase model. Most of Phase A (Revision) duplicates `[refining mode]`; most of Phase C (Proofreading) overlaps `[formatting mode]`'s pre-flight. The two genuine gaps are (a) spelling/diacritic/paste-artifact detection between grammar and AI-tell, and (b) an explicit return-to-refining rule for structural deviation.

- [ ] **Step 6.1: Add the structural-deviation handoff rule at the top of `[editing mode]`**

Use Edit on `templates/CLAUDE.md`:

```
old_string: ### [editing mode]

*On entry, read `./voice.md` in full (voice audit runs the rules there). If voice.md is missing, stop and ask {{USER}} to run `install.sh --voice <name>`.*

Reread each sentence of the written prose, cut filler, merge repetitions, check flow, repeat until a full reread surfaces no issues. The voice audit below operates against the specific rules in voice.md.
new_string: ### [editing mode]

*On entry, read `./voice.md` in full (voice audit runs the rules there). If voice.md is missing, stop and ask {{USER}} to run `install.sh --voice <name>`.*

**Before the pass list, detect structural deviation from the refined outline.** Detection is operational, not impressionistic: read the refined outline (sibling outline file if it exists, or the outline section in the working document), list its section headings and the one-line purpose of each in order, then list the same for the current draft. If any heading is missing, reordered, renamed beyond trivial wording, or any draft paragraph asserts a claim the outline did not place, the draft has deviated structurally. **On detected deviation, do not fix it here** — return to `[refining mode]` for structural realignment, then re-enter `[editing mode]` once the outline and prose agree. Structural fixes at prose level are expensive; the refining/editing boundary exists to prevent that cost from compounding.

Reread each sentence of the written prose, cut filler, merge repetitions, check flow, repeat until a full reread surfaces no issues. The voice audit below operates against the specific rules in voice.md.
```

- [ ] **Step 6.2: Insert a new proofreading pass between pass 4 (Grammar) and pass 5 (AI-tell), renumbering**

Use Edit on `templates/CLAUDE.md`:

```
old_string: **5. AI-tell pass (§10).** For each paragraph in the section being edited, scan for the patterns in section 10.
new_string: **5. Proofreading pass.** After grammar, before AI-tell, scan for mechanics the grammar pass does not cover. Produce each list as a forced field; a pass that doesn't produce its lists has not run.
- **Proper-noun consistency list.** For every proper noun occurring more than once in the section, compare each occurrence to its first occurrence character-by-character. Produce a list: `{proper_noun, line_first, line_current, chars_differing}` for every mismatch. Empty list = no drift. When the list has entries, restore from the citation log's `exact_quote` (authoritative) or ask {{USER}} for the correct form.
- **Paste-artifact list.** Scan for character substitutions that indicate the text was pasted through an application that mangled Unicode (`â` where `ȧ` is expected, stray combining marks, smart-quote curl inversions, Latin-1 to UTF-8 mojibake). Produce a list: `{line, span, suspected_original, confidence}`. Restore from `exact_quote` or ask {{USER}}.
- **Punctuation mechanics list.** Flag spacing errors around dashes and quote marks, hyphen-vs-en-dash confusions in page ranges, and inconsistent quote-curl direction. Produce a list of `{line, issue, suggested_fix}`.

This pass runs before §10 because mechanics fixes can introduce cadence changes the §10 pass then evaluates in final form.

**6. AI-tell pass (§10).** For each paragraph in the section being edited, scan for the patterns in section 10.
```

- [ ] **Step 6.3: Renumber the remaining passes (6→7, 7→8)**

Use Edit on `templates/CLAUDE.md`:

```
old_string: **6. Quote-density pass.**
new_string: **7. Quote-density pass.**
```

Use Edit on `templates/CLAUDE.md`:

```
old_string: **7. Voice audit.**
new_string: **8. Voice audit.**
```

- [ ] **Step 6.4: Update the in-mode references to the renumbered passes**

The in-annotated-bib carve-out at the bottom of `[editing mode]` refers to "Pass 6" and "Pass 7." Renumber those too.

Use Edit on `templates/CLAUDE.md`:

```
old_string: - **Pass 6 (Quote-density)** does not apply.
new_string: - **Pass 7 (Quote-density)** does not apply.
```

Use Edit on `templates/CLAUDE.md`:

```
old_string: - **Pass 7 (Voice audit)** is reduced.
new_string: - **Pass 8 (Voice audit)** is reduced.
```

Use Edit on `templates/CLAUDE.md`:

```
old_string: Passes 1–5 apply unchanged. §4 synthesis (item 6) only fires when an annotation cross-references another entry via `[@id]`.
new_string: Passes 1–6 apply unchanged. §4 synthesis (item 6) only fires when an annotation cross-references another entry via `[@id]`.
```

Also update the handoff scan reference in the same mode block:

Use Edit on `templates/CLAUDE.md`:

```
old_string: Before asking {{USER}} to advance, run a final surface scan over the draft for §10 Never-list hits
new_string: Before asking {{USER}} to advance, run a final surface scan over the draft for §10 Never-list hits (covered by pass 6)
```

- [ ] **Step 6.5: Verify all edits landed and the pass numbering is consistent**

Run:
```
grep -n "If the draft deviates structurally" templates/CLAUDE.md
grep -n "\*\*[0-9]\. " templates/CLAUDE.md | grep -i "pass\|audit"
grep -n "Pass [0-9] (Quote-density)" templates/CLAUDE.md
grep -n "Pass [0-9] (Voice audit)" templates/CLAUDE.md
grep -n "Passes 1–[0-9] apply unchanged" templates/CLAUDE.md
```
Expected: pass list shows 1,2,3,4,5,6,7,8 in order; in-annotated-bib block references Pass 7 and Pass 8; "Passes 1–6 apply unchanged."

- [ ] **Step 6.6: Commit**

```bash
git add templates/CLAUDE.md
git commit -m "$(cat <<'EOF'
Add proofreading pass and structural-deviation handoff to [editing mode]

Adds one new pass (spelling/diacritic consistency, paste-artifact
detection, punctuation mechanics) between grammar and §10 AI-tell.
Adds an explicit return-to-[refining mode] rule at the top of the
mode for drafts that deviate structurally from the refined outline —
the one genuine gap the UofT three-phase model surfaced that isn't
already covered by refining or formatting.
EOF
)"
```

---

## Cross-task verification

After Tasks 1–6 land, run one sanity pass across the whole set:

- [ ] **Step 7.1: Cross-file consistency check**

Run:
```
grep -c "printed_page_observed" citations/schema.md agents/source-finder.md templates/CLAUDE.md
grep -c "verification_trace" citations/schema.md agents/source-finder.md
grep -c "per_entity_locators" citations/schema.md agents/source-finder.md
```
Expected: `printed_page_observed` appears in all three files; `verification_trace` and `per_entity_locators` appear in both schema.md and source-finder.md. If any is missing from a file it should be in, the cross-file inheritance is broken.

- [ ] **Step 7.2: Framework audit**

Run the repo's existing audit skill on the project to confirm nothing broke:

```
# from /home/hayden/sourced
ls tests/
# existing tests are emitter + parity; run whichever apply
```

(Note: emitter and parity tests cover CSL-JSON + pandoc rendering, not schema/prompt rules. They should continue to pass because this plan does not touch emitter or rendering code. If any fail, the edit introduced an unintended regression — investigate.)

- [ ] **Step 7.3: Behavior validation (optional, after PR 1 merges)**

Dispatch one source-finder against a sub-topic covered in `report_3.citations.json` using the new workflow. Verify the returned shard:
- Every entry has populated `retrieval.printed_page_observed`, `tool_page_index`, `verification_trace`.
- Multi-entity entries carry `per_entity_locators`.
- Any entry the old workflow would have produced in a fabricated or multi-entity-off-page shape is instead rejected with a named failure category.

If the new workflow still produces an entry that a hand-audit would reject, the rule language needs another iteration — flag it rather than accepting the behavior as "probably close enough."

---

## Self-review (done before PE handoff)

**Spec coverage:** Issue 1 → Task 1. Issue 2 → Tasks 2, 3, 4. Issue 3 → Task 6. Issue 4 → Task 5. No gaps.

**Placeholder scan:** No TBDs, TODOs, or "similar to" references. Every code block is copy-pasteable. Every grep command is exact.

**Type consistency:** Field names (`printed_page_observed`, `tool_page_index`, `pdf_page_offset`, `verification_trace`, `per_entity_locators`) are identical across schema.md, source-finder.md, and CLAUDE.md. Pass numbers in `[editing mode]` are consistent after renumbering (new pass 5, shifted 5→6, 6→7, 7→8, with in-mode references to Pass 7/8 updated).

**Known residual risk:** Behavior validation in Step 7.3 is the only way to confirm the LLM actually produces the new fields. Rule language was PE-reviewed (see `/home/hayden/sourced/voice_issue.md` and PE report inline in this plan's design discussion), and the "force externalized field" approach is strictly stronger than mental-verb phrasing. Remaining risk is cases where the rendered source itself is ambiguous (no printed page number, silent URL redirect) — handled by `[editing mode]` pass 2's re-open trigger at draft-touch time.
