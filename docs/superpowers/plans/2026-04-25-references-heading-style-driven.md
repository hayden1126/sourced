# References Heading Style-Driven Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the silent ship-bug where switching styles mid-draft renders the new bibliography under a stale hand-authored `# References` / `# Bibliography` / `# Works Cited` heading. Make the heading style-driven via pandoc's `--metadata reference-section-title=` flag, sourced from each style.md's already-declared `List heading:` field.

**Architecture:** Two coordinated changes. (1) `[formatting mode]` (and the parity render harness) read `List heading:` from `style.md` §Style identity and pass `--metadata reference-section-title="<value>"` to pandoc; pandoc auto-emits the heading itself. (2) `[writing mode]` and `[editing mode]` instructions stop telling writers to hand-author the heading; `[editing mode]` gains a regex check that flags any surviving `^#\s+(References|Bibliography|Works Cited)\s*$` line as a legacy-draft regression. No schema change, no new mode, no new gate.

**Tech Stack:** pandoc + citeproc + CSL · bash (parity render script) · pytest + syrupy (golden snapshot suite at `tests/parity/`) · markdown mode docs at `src/sourced/data/templates/docs/modes/`

---

## File Structure

**Modify (parity infrastructure):**
- `tests/parity/_render.sh` — read `List heading:` from `src/sourced/data/templates/styles/<style>.md`; pass `--metadata reference-section-title="<value>"` to pandoc invocations (both branches: `latex` and the markdown-paste-target branch)

**Modify (fixtures — strip trailing heading):**
- `tests/parity/apa7/fixture.pandoc.md`
- `tests/parity/chicago17-ad/fixture.pandoc.md`
- `tests/parity/chicago17-nb/fixture.pandoc.md`
- `tests/parity/ieee/fixture.pandoc.md`
- `tests/parity/mla9/fixture.pandoc.md`

**Regenerate if pandoc-emitted heading differs (validate via parity suite — likely no diff for markdown targets):**
- `tests/parity/<style>/golden/<target>.<ext>` — 20 files (5 styles × 4 paste targets)

**Modify (mode docs — drop hand-authoring instruction, add formatting flag, add editing regression check):**
- `src/sourced/data/templates/docs/modes/writing.md` — drop any "end with `# References`" instruction
- `src/sourced/data/templates/docs/modes/formatting.md` — instruct pandoc invocation to include `--metadata reference-section-title="<List heading value>"`
- `src/sourced/data/templates/docs/modes/editing.md` — add regression check (regex against surviving hand-authored headings)
- `src/sourced/data/templates/CLAUDE.md` — verify §11 schema callout still aligns; touch only if it points at the now-retired hand-authoring step

**Add (test):**
- `tests/cli/unit/test_render_metadata.py` — assert `_render.sh` extracts `List heading:` correctly per style and produces matching pandoc output

---

## Branch Strategy

Work on a feature branch `fix-issue-15-references-heading` off `main`. Frequent commits per task; squash-or-merge at PR time per repo convention.

---

### Task 1: Set up branch and capture baseline parity output

**Files:** none modified — verification step

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b fix-issue-15-references-heading
```

- [ ] **Step 2: Run the full parity suite to confirm green baseline**

Run: `pytest tests/parity/ -v 2>&1 | tail -30`
Expected: all 20 parity tests pass (5 styles × 4 paste targets); `[<style>] <target> OK` lines for each.

- [ ] **Step 3: Capture baseline render of one fixture for byte-level comparison**

```bash
mkdir -p /tmp/issue-15-baseline
cp tests/parity/apa7/golden/plain-markdown.md /tmp/issue-15-baseline/apa7-baseline.md
```

No commit yet — pure verification step.

---

### Task 2: Verify pandoc behavior — source heading + metadata flag interaction

**Files:** none modified — exploratory test to lock the contract

- [ ] **Step 1: Empirically test what pandoc emits when source has `# References` AND `--metadata reference-section-title=References` is passed**

```bash
pandoc --citeproc \
  --bibliography=tests/parity/apa7/fixture.bib.json \
  --csl=src/sourced/data/templates/styles/apa7/apa.csl \
  --metadata reference-section-title=References \
  --wrap=preserve -t markdown-citations-header_attributes-smart \
  tests/parity/apa7/fixture.pandoc.md \
  > /tmp/issue-15-baseline/apa7-with-metadata-and-source-heading.md
diff /tmp/issue-15-baseline/apa7-baseline.md /tmp/issue-15-baseline/apa7-with-metadata-and-source-heading.md
```

Expected outcomes (record which one):
- **Outcome A** — diff is empty: pandoc treats them as equivalent. Safe to land the metadata flag *before* stripping fixtures (independent commits).
- **Outcome B** — diff shows duplicate heading or interleaved divs: must land the metadata flag and the fixture strip in the same commit, with goldens regenerated.

- [ ] **Step 2: Test fixture-stripped + metadata-flag scenario**

```bash
sed '/^# References$/d' tests/parity/apa7/fixture.pandoc.md > /tmp/apa7-fixture-stripped.md
pandoc --citeproc \
  --bibliography=tests/parity/apa7/fixture.bib.json \
  --csl=src/sourced/data/templates/styles/apa7/apa.csl \
  --metadata reference-section-title=References \
  --wrap=preserve -t markdown-citations-header_attributes-smart \
  /tmp/apa7-fixture-stripped.md > /tmp/issue-15-baseline/apa7-stripped-with-metadata.md
# strip the ::: fenced-divs the same way _render.sh does
sed -e '/^::: /d' -e '/^:::$/d' -i /tmp/issue-15-baseline/apa7-stripped-with-metadata.md
diff /tmp/issue-15-baseline/apa7-baseline.md /tmp/issue-15-baseline/apa7-stripped-with-metadata.md
```

Expected: empty diff (pandoc emits `# References` then the bibliography body; sed strips the divs; output matches existing golden character-for-character).

If non-empty diff, document the difference (likely a blank-line variance or attribute attachment) and decide whether goldens need regeneration.

- [ ] **Step 3: Record the locked contract**

Append a one-line note to the eventual commit message in Task 4 documenting which outcome held.

No commit yet — verification step only.

---

### Task 3: Add `extract_list_heading` helper to `_render.sh`

**Files:**
- Modify: `tests/parity/_render.sh` (add helper near top, before pandoc invocations)

- [ ] **Step 1: Add the helper function**

Insert after `STYLE_NAME="$(basename "${STYLE_DIR}")"` (around line 37):

```bash
# Extract the `List heading:` value from the corresponding shipped style.md.
# Source of truth: src/sourced/data/templates/styles/<style-name>.md §Style identity.
# Falls back to "References" if not found, matching pandoc's own default and the
# most common case across shipped styles. A missing field on a real ship is a
# style.md authoring bug surfaced by `sourced check`, not _render.sh's problem.
STYLE_MD="${REPO_DIR}/src/sourced/data/templates/styles/${STYLE_NAME}.md"
if [[ -f "${STYLE_MD}" ]]; then
  LIST_HEADING="$(awk -F': *' '/^- List heading:/ {print $2; exit}' "${STYLE_MD}" | tr -d '\r')"
fi
LIST_HEADING="${LIST_HEADING:-References}"
```

- [ ] **Step 2: Pass the metadata flag in both pandoc invocations**

Add `--metadata "reference-section-title=${LIST_HEADING}"` to both pandoc calls in `_render.sh`:

```bash
# In the latex branch (around line 63-69):
  pandoc --citeproc \
    --bibliography="${STYLE_DIR}/fixture.bib.json" \
    --csl="${CSL_FILE}" \
    --metadata "reference-section-title=${LIST_HEADING}" \
    --standalone --template="${TEMPLATE}" \
    "${EXTRA_FLAGS[@]}" \
    -o "${RAW}" \
    "${STYLE_DIR}/fixture.pandoc.md"

# In the markdown-target branch (around line 85-91):
  pandoc --citeproc \
    --bibliography="${STYLE_DIR}/fixture.bib.json" \
    --csl="${CSL_FILE}" \
    --metadata "reference-section-title=${LIST_HEADING}" \
    "${LUA_FILTER_FLAGS[@]}" \
    "${EXTRA_FLAGS[@]}" \
    -o "${ACTUAL}" \
    "${STYLE_DIR}/fixture.pandoc.md"
```

- [ ] **Step 3: Run the parity suite to confirm no regressions**

Run: `pytest tests/parity/ -v 2>&1 | tail -30`
Expected:
- If Task 2 outcome A (empty diff) held: all 20 tests still pass — fixtures still have the source heading, metadata flag is redundantly correct.
- If Task 2 outcome B held: some tests fail with duplicate heading; proceed directly to Task 4 in the same commit (don't commit between Task 3 and Task 4).

- [ ] **Step 4: Commit (only if Task 2 outcome A and tests pass)**

```bash
git add tests/parity/_render.sh
git commit -m "feat(parity): pass reference-section-title metadata to pandoc

Read List heading: from each style.md and emit it via
--metadata reference-section-title=<value>. No fixture or golden
changes yet; this commit makes the flag redundantly correct while
fixtures still carry the source heading. Strips in next commit.

Refs issue #15."
```

If Task 2 outcome B held, defer the commit and bundle with Task 4.

---

### Task 4: Strip trailing reference headings from all 5 parity fixtures

**Files:**
- Modify: `tests/parity/apa7/fixture.pandoc.md` (drop trailing `# References` line)
- Modify: `tests/parity/chicago17-ad/fixture.pandoc.md` (drop trailing `# References` line)
- Modify: `tests/parity/chicago17-nb/fixture.pandoc.md` (drop trailing `# Bibliography` line)
- Modify: `tests/parity/ieee/fixture.pandoc.md` (drop trailing `# References` line)
- Modify: `tests/parity/mla9/fixture.pandoc.md` (drop trailing `# Works Cited` line)

- [ ] **Step 1: Verify which heading each fixture currently carries**

```bash
for f in tests/parity/*/fixture.pandoc.md; do
  echo "=== $f ===" && tail -3 "$f"
done
```

Record the trailing heading per file. Each ends with the heading on the last line and a single trailing newline.

- [ ] **Step 2: Strip the trailing heading from each fixture**

For each fixture, remove the final two lines: the `# <heading>` line and the trailing blank line that precedes it. Use the Edit tool with the literal `old_string` matching the end-of-file pattern (e.g., for apa7):

```
similar themes (Perennial, n.d.).

# References
```

becomes:

```
similar themes (Perennial, n.d.).
```

Repeat per fixture with the appropriate heading. Do not use `sed -i` for this — Edit tool produces verifiable diffs and the line context guards against accidental matches if a fixture ever discusses `# References` in body prose.

- [ ] **Step 3: Run the parity suite — expect all 20 tests to pass with no golden changes**

Run: `pytest tests/parity/ -v 2>&1 | tail -30`
Expected: all 20 tests pass. The `_render.sh` metadata flag emits the heading; sed strips the divs; output matches existing goldens character-for-character.

If any tests fail with non-trivial diffs, the per-target diff will show in stderr — inspect, decide whether the golden needs regeneration (Task 4b), or whether `_render.sh` needs adjustment.

- [ ] **Step 4: Commit**

```bash
git add tests/parity/*/fixture.pandoc.md
git commit -m "fix(parity): strip hand-authored reference-list heading from fixtures

Pandoc now emits the heading via --metadata reference-section-title.
Source fixtures end at the last body paragraph. Goldens unchanged
(rendered output is identical character-for-character on the existing
post-pandoc strip pipeline).

Refs issue #15."
```

If Task 3 was deferred, include `tests/parity/_render.sh` in this commit and update the message.

---

### Task 4b: Regenerate goldens (skip if Task 4 step 3 was green)

**Files:**
- Modify: `tests/parity/<style>/golden/<target>.<ext>` — only the files whose diff is non-empty after Task 4

Only execute if Task 4 step 3 surfaced golden mismatches.

- [ ] **Step 1: For each failing target, copy actual to golden**

```bash
# Example for apa7/plain-markdown only — adapt per failing target:
cp tests/parity/apa7/actual/plain-markdown.md tests/parity/apa7/golden/plain-markdown.md
```

- [ ] **Step 2: Inspect every regenerated golden by hand**

Run `git diff tests/parity/<style>/golden/<target>.<ext>` and confirm:
- The reference-list heading text matches `List heading:` from style.md.
- No body content changed beyond the heading area.
- No new attribute strings (`{#references .unnumbered}`) leaked through — the writer flag `-header_attributes` should already strip these for markdown targets.

- [ ] **Step 3: Run the parity suite to confirm green**

Run: `pytest tests/parity/ -v 2>&1 | tail -30`
Expected: all 20 tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/parity/*/golden/
git commit -m "chore(parity): regenerate goldens after style-driven heading shift

Pandoc emits the reference-list heading via --metadata
reference-section-title. Diff vs prior goldens limited to the
heading line itself (and adjacent blank-line spacing in <list affected
targets>).

Refs issue #15."
```

---

### Task 5: Update `[formatting mode]` to instruct the pandoc metadata flag

**Files:**
- Modify: `src/sourced/data/templates/docs/modes/formatting.md` (find the pandoc invocation example block; add the metadata flag and a one-line note)

- [ ] **Step 1: Locate the current pandoc invocation block in formatting.md**

```bash
grep -n "pandoc --citeproc\|reference-section-title\|List heading\|# References\|# Bibliography\|# Works Cited" src/sourced/data/templates/docs/modes/formatting.md
```

- [ ] **Step 2: Add the metadata flag to the pandoc invocation**

Update the documented pandoc command in formatting.md to include:

```
--metadata reference-section-title="<value from style.md §Style identity 'List heading:'>"
```

Add a one-line authoring note above the invocation:

```markdown
Read `List heading:` from the project's `config/style.md` §Style identity block. Pass it to pandoc via `--metadata reference-section-title=<value>` so pandoc emits the heading itself. Do **not** hand-author `# References` / `# Bibliography` / `# Works Cited` in the source `.md` — that pattern is a legacy-draft regression flagged by `[editing mode]` (see issue #15).
```

- [ ] **Step 3: Run the invariants check to confirm no template breakage**

Run: `python -m sourced check --invariants 2>&1 | tail -20`
Expected: all I1-I11 invariants pass (no flat-path leak from the new line; no broken cross-reference).

- [ ] **Step 4: Commit**

```bash
git add src/sourced/data/templates/docs/modes/formatting.md
git commit -m "docs(formatting): instruct pandoc metadata flag for reference heading

Source the heading from style.md's List heading: field rather than
asking writers to hand-author it. Closes the silent style-switch bug
where a stale source-prose heading shipped under a new style's
bibliography.

Refs issue #15."
```

---

### Task 6: Update `[writing mode]` to drop hand-authoring instruction

**Files:**
- Modify: `src/sourced/data/templates/docs/modes/writing.md` (locate any directive that ends a draft with the reference-list heading; remove)

- [ ] **Step 1: Locate the writing-mode directive**

```bash
grep -n "# References\|# Bibliography\|# Works Cited\|reference-list heading\|reference list heading" src/sourced/data/templates/docs/modes/writing.md
```

- [ ] **Step 2: Remove the hand-authoring instruction**

Drop any line or paragraph that tells the model to append the reference-list heading at the end of the draft. The draft ends at the final body paragraph; pandoc emits the heading at format time.

If the existing instruction is wrapped in a multi-step procedure (e.g., "after the last paragraph, write `# References`"), edit the procedure to remove just that step. Preserve the surrounding context.

- [ ] **Step 3: Run the invariants check**

Run: `python -m sourced check --invariants 2>&1 | tail -20`
Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add src/sourced/data/templates/docs/modes/writing.md
git commit -m "docs(writing): drop hand-authored reference-list heading

Heading is now style-driven via pandoc metadata in [formatting mode].
Drafts end at the final body paragraph.

Refs issue #15."
```

---

### Task 7: Add legacy-draft regression check to `[editing mode]`

**Files:**
- Modify: `src/sourced/data/templates/docs/modes/editing.md` (add a regex check, ideally folded into the existing ID-validation pass per issue #15 fix direction)

- [ ] **Step 1: Locate the existing pass that handles citation-rendering checks**

```bash
grep -n "rendered citation string\|ID-validation\|verify.*citation\|citation.*pass" src/sourced/data/templates/docs/modes/editing.md
```

Find the pass §8 already references (the rendered-citation-string regression check), per issue #15's "same shape as §8" hint.

- [ ] **Step 2: Add the heading-regression check**

Append (or fold into the §8 pass) a check of this form:

```markdown
**Legacy-draft heading check.** Scan the draft for any line matching the regex `^#\s+(References|Bibliography|Works Cited)\s*$`. If found, this is a legacy-draft regression — `[formatting mode]` now emits the reference-list heading itself via `--metadata reference-section-title=<List heading>`. Surface the finding to the writer; ask whether the heading should be removed (typical case) or kept (rare: writer is documenting an example heading inside body prose); convert per response. Same remediation path as the §8 rendered-citation-string regression check.
```

- [ ] **Step 3: Run the invariants check**

Run: `python -m sourced check --invariants 2>&1 | tail -20`
Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add src/sourced/data/templates/docs/modes/editing.md
git commit -m "docs(editing): flag hand-authored reference-list heading as regression

Pass scans for ^#\s+(References|Bibliography|Works Cited)\s*$ and
surfaces the legacy-draft pattern. Same shape as the §8 rendered-
citation-string regression check.

Refs issue #15."
```

---

### Task 8: Run full test suite + invariants + smoke

**Files:** none modified — full verification

- [ ] **Step 1: Run the entire pytest surface**

Run: `pytest 2>&1 | tail -30`
Expected: all tests pass (238+ tests per phase-4 baseline; parity suite green; integration suite green).

- [ ] **Step 2: Run sourced check --invariants on a fresh tmp project**

```bash
tmpdir=$(mktemp -d)
python -m sourced new "${tmpdir}/issue-15-smoke" --voice academic --style apa7 --type essay --no-edit
python -m sourced check --project "${tmpdir}/issue-15-smoke" 2>&1 | tail -10
rm -rf "${tmpdir}"
```

Expected: install + check both green.

- [ ] **Step 3: Manual smoke — switch style mid-draft on the smoke project**

```bash
tmpdir=$(mktemp -d)
python -m sourced new "${tmpdir}/issue-15-stylesmoke" --voice academic --style apa7 --type essay --no-edit
# Verify config/style.md has List heading: References
grep "List heading" "${tmpdir}/issue-15-stylesmoke/config/style.md"
# Switch to chicago17-nb
python -m sourced switch --project "${tmpdir}/issue-15-stylesmoke" --style chicago17-nb
grep "List heading" "${tmpdir}/issue-15-stylesmoke/config/style.md"
rm -rf "${tmpdir}"
```

Expected: first grep prints `- List heading: References`; second prints `- List heading: Bibliography`. Confirms the field flips on style switch — which is the point of moving the heading off source prose.

- [ ] **Step 4: Mark the issue closed in `issues.md`**

Edit `issues.md` Summary table: flip row 15 from `🔴 open` to `🟢 fixed`. Edit the detail section header from `### 15. References/Bibliography heading hand-authored instead of style-driven 🔴` to `🟢` and append a `**Fix shipped.**` paragraph mirroring the closed-issue convention.

`issues.md` is gitignored — local edit only, no commit needed.

- [ ] **Step 5: Push branch and open PR**

```bash
git push -u origin fix-issue-15-references-heading
gh pr create --title "fix: style-driven reference-list heading (issue #15)" --body "$(cat <<'EOF'
## Summary
- Pandoc now emits the reference-list heading itself via `--metadata reference-section-title=<List heading>`, sourced from each `style.md`'s §Style identity declaration.
- Drafts no longer hand-author `# References` / `# Bibliography` / `# Works Cited`; `[writing mode]` instruction removed.
- `[editing mode]` flags any surviving hand-authored heading as a legacy-draft regression (regex `^#\s+(References|Bibliography|Works Cited)\s*$`).
- Closes the silent ship-bug where switching styles mid-draft rendered the new style's bibliography under the prior style's stale heading.

## Test plan
- [x] Parity suite green: 20/20 tests pass (5 styles × 4 paste targets).
- [x] Goldens unchanged (or regenerated with documented diff confined to heading line).
- [x] `sourced check --invariants` green on shipped templates.
- [x] Smoke: `sourced new` + `sourced switch --style` flips `List heading:` in `config/style.md` correctly.
- [ ] Reviewer-side: skim `formatting.md` / `editing.md` updates for tone consistency with surrounding mode docs.

Refs issue #15.
EOF
)"
```

---

## Self-Review Checklist

After plan completion, before execution:

**Spec coverage:** issue #15's fix direction §1 (writing/editing drop instruction + editing-mode regex) → Tasks 6 + 7. §2 (formatting pandoc metadata + parity render update + fixture/golden regen) → Tasks 3, 4, 4b, 5. ✅

**Placeholder scan:** All step bodies contain executable commands or concrete edit instructions. The "if Task 2 outcome B" branch in Task 4b carries actual commands; `<value from style.md>` in Task 5 is a placeholder for the writer to substitute at runtime, which is correct for a docs string.

**Type consistency:** `LIST_HEADING` shell variable name, `reference-section-title` pandoc metadata key, `^#\s+(References|Bibliography|Works Cited)\s*$` regex are all reused identically across tasks. ✅

**Risk-tier note:** Task 4b is conditional on Task 4 step 3 outcome. If goldens require regeneration, a separate commit for the regeneration keeps the diff readable in PR review. If they don't, Task 4b is skipped entirely — that's the optimistic path empirical verification (Task 2 step 2) supports.
