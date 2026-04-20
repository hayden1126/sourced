# LaTeX paste target: ship `latex` as a 5th paste target per style

- **Date:** 2026-04-20
- **Status:** Approved
- **Scope:** Add `latex` to the shipped paste-target set across all 5 styles (apa7, chicago17-ad, chicago17-nb, ieee, mla9), using the existing pandoc + citeproc + CSL pipeline. Ship a per-style `preamble.tex` scaffold. Extend parity coverage.
- **Out of scope:** PDF compilation (user owns `pdflatex`). Figure/table handling beyond pandoc defaults. biblatex / natbib pathways. arXiv-ready submission (separate ROADMAP item).

## 1. Problem

The ROADMAP `### LaTeX` entry is marked `next · M · open`. STEM workflows (math, physics, CS, engineering) default to LaTeX, but `sourced` currently renders to `plain-markdown`, `google-docs`, and `word` only — STEM students either copy-paste markdown and then convert by hand, or route through `word` and lose LaTeX's native math/references. IEEE and MLA 9 are already shipped as styles, so the bibliography side is ready; what's missing is a paste target that emits `.tex`.

## 2. Decisions

### 2.1 Output artifact: `.tex` source, user compiles

Pandoc emits a standalone `.tex` file. The user runs `pdflatex` (or `xelatex` / `lualatex`) themselves. Rationale: STEM students already have a LaTeX toolchain; owning compilation inside `sourced` would require `texlive` in prereqs and turn runtime edge cases (missing fonts, package conflicts, bib backend mismatches) into `sourced` problems. The `word` target's "shipped binary" ergonomics do not generalize — Word users typically don't have a `.docx`-to-PDF pipeline; LaTeX users do.

### 2.2 Pipeline: pandoc + citeproc + CSL (same as every other shipped target)

No biblatex, no natbib, no new bibliography ecosystem. Pandoc's citeproc renders bibliography entries as formatted text inline in the `.tex` body, identical to how it handles `word` / `google-docs` / `plain-markdown`. Matches the CSL direct-consumption architecture shipped 2026-04-19; keeps the invariant "style behavior lives in the CSL file." A biblatex pathway would require per-style biblatex analogs (5 more vendored bibliography artifacts) and a parallel style-vs-style matrix — not worth it for v1, and materially dupes the CSL work.

### 2.3 Per-style `preamble.tex` scaffold

Each style ships `templates/styles/<name>/preamble.tex` alongside its `.csl`. Contents are style-appropriate (document class, geometry, fonts, spacing). Per-style matches the existing per-style-asset pattern (`reference-styled.docx` for `word`; CSL for bibliography). An IEEE paper landing in `\documentclass{article}` instead of `\documentclass{IEEEtran}` would be instantly wrong to any STEM reviewer.

### 2.4 Figures and tables: pandoc defaults only

Markdown `![caption](path)` passes through as `\includegraphics{path}` via pandoc's default rules. No `--resource-path` tuning, no `\label` / `\ref` semantics in v1, no float-positioning heuristics. Matches how figures are handled in `word` / `google-docs` / `plain-markdown` today (untested, passthrough). Figure polish is a downstream ROADMAP item (adjacent to arXiv-ready submission).

### 2.5 Install-time changes: none

Pandoc is already a prereq for the three shipped targets. `pdflatex` is the user's responsibility. The existing install.sh per-style mirroring already copies the whole `templates/styles/<name>/` directory into `~/.claude/style/<name>/`, so new `preamble.tex` files install automatically with no script changes.

## 3. Per-style preamble contents

Each preamble is ~15-30 lines. Same document-class choice drives most of the decision; the rest is style-matching geometry and typography.

| Style | documentclass | Key preamble contents |
|---|---|---|
| apa7 | `article` | 12pt Times, 1in margins, double-spaced body (`setspace`), APA-matching title-block `\usepackage{titling}`, hanging-indent bibliography via pandoc's `CSLReferences` environment |
| chicago17-ad | `article` | 12pt Times, 1in margins, single-spaced body, CMOS-17 typographic defaults |
| chicago17-nb | `article` | Same as `-ad`; notes are rendered by citeproc into `.tex` as inline footnote text (no `\footnote` machinery needed) |
| ieee | `IEEEtran` | `conference` option (default), `\IEEEsetup{...}` for captions, IEEE-matching column / spacing defaults |
| mla9 | `article` | 12pt Times, 1in margins, double-spaced, Works Cited hanging-indent compatible |

Every preamble includes `\usepackage{hyperref}` (pandoc citeproc emits hyperlinks), `\usepackage{csquotes}` (quote handling), and `\usepackage[T1]{fontenc}` (UTF-8 punctuation). `geometry` and `setspace` are loaded where the style needs them.

## 4. Style.md `§Paste target expression rules` additions

Each style.md gets a `### latex` subsection under `## Paste target expression rules`. The subsection carries:

- **Pandoc recipe.** `pandoc --citeproc --standalone --include-in-header=<preamble.tex> --csl <csl> --bibliography <bib.json> -o <draft>.tex <draft>.pandoc.md`
- **File outputs.** `<draft>.tex` (compilable standalone file); no `<draft>.docx.md` sibling.
- **Paste-time instructions.** "User compiles with `pdflatex <draft>.tex`." No post-pandoc hook; no post-processing step.
- **Known quirks** (per-style, if any — e.g., IEEEtran requires specific title-block formatting that pandoc's default `\maketitle` may not match; note in style.md).

## 5. Parity coverage

### 5.1 Harness refactor (precursor)

Before adding the 4th target, factor the repeated pandoc block in each `tests/parity/<style>/run.sh` into a shared helper at `tests/parity/_render.sh`. Current per-style `run.sh` contains three near-identical pandoc invocations differing only by `--wrap`, `-t`, and output name. At 4 targets the copy-paste becomes maintenance burden; at 5+ (ROADMAP tier-2 rollout) it compounds. This is a no-behavior-change refactor; suite stays 15/15 green.

`_render.sh` interface (draft):

```
_render.sh <style-dir> <target-name> <pandoc-flags...>
# Emits actual/<target-name>.<ext>; diffs against golden/; returns pass/fail
```

Each `run.sh` becomes a list of three (later four) `_render.sh` calls.

### 5.2 Fragment-mode golden for `latex`

`golden/latex.tex` captures pandoc's **fragment** output (`-t latex` without `--standalone` and without `--include-in-header`). Fragment = body content + citeproc bibliography block only. No `\documentclass`, no `\begin{document}`, no preamble. Rationale: preamble is a shipped asset, edited when a style's typography needs tuning. If preamble edits cascaded into golden diffs, every preamble tweak would force 5 golden regenerations — the "always-red on cosmetic edits" failure mode `tests/parity/README.md` explicitly warns against.

Fragment mode verifies exactly what the harness should verify: the CSL pipeline's body output is stable per style.

### 5.3 User-facing recipe vs. parity-tested recipe

The user-facing recipe in `style.md` runs pandoc in **standalone** mode (produces compilable `.tex`). The parity-tested recipe runs pandoc in **fragment** mode (produces just the body). Both use the same CSL and the same fixture. The only flags that differ are `--standalone` and `--include-in-header`. The difference is explicit in each style.md (to avoid confusion between what the test checks and what the user gets).

### 5.4 Suite size

After shipping: 5 styles × 4 targets = 20 parity assertions per `run-all.sh` invocation. Each style dir has 4 goldens and 4 lines in its run.sh.

## 6. CLAUDE.md changes

One small change: `§7 [formatting mode]`'s supported-paste-target list adds `latex` alongside `plain-markdown`, `google-docs`, `word`. The formatting-mode procedure itself is target-agnostic (reads style.md's §Paste target expression rules for the chosen target), so no procedural changes beyond the target name appearing in the list.

## 7. Docs updates

- `docs/STYLES.md`: `latex` appears in the shipped-paste-targets table for each style.
- `ARCHITECTURE.md`: §Paste targets enumerates `latex` as a 4th target; the parity count updates from "5×3=15" to "5×4=20."
- `docs/INSTALL.md`: no changes (no new prereqs).
- `ROADMAP.md`: `### LaTeX` entry's status flips from `open` to `shipped (<commit>)`. Text can stay mostly intact — the "pipeline translates directly" framing is correct.

## 8. Delivery plan

Three commits on branch `latex-paste-target`, one PR against `main`:

1. **Refactor `run.sh` → `_render.sh` helper.** No behavior change. Suite stays 15/15. Establishes the pattern needed by commit 2.
2. **Add `latex` target.** 5 new `preamble.tex` files; `latex` subsection added to each `style.md`; `latex` appended to CLAUDE.md §7's target list; 5 new `golden/latex.tex` files; run.sh per-style calls `_render.sh` for latex. Suite goes to 20/20.
3. **Docs.** STYLES.md, ARCHITECTURE.md, ROADMAP.md updates per §7 above.

Post-merge hygiene: move this spec to `docs/archive/specs/` with a Shipped banner (matches the convention from the CSL-direct-consumption and voice-extractor-decoupling shipments).

## 9. Risks and open questions

- **IEEEtran output may need title-block tuning.** Pandoc's default `\maketitle` renders author/affiliation in `article`-class style, which IEEEtran overrides with its own `\author{\IEEEauthorblockN{...}}` conventions. If the fragment-mode parity golden is stable (and we expect it will be — the body is just citations + references), the preamble can evolve independently. Flagging as a post-ship verification item rather than a blocker.
- **Bibliography block placement.** Pandoc citeproc emits a `CSLReferences` environment at the end of the document. IEEEtran's template expects `\bibliography{...}` or equivalent. Verify at golden-regeneration time that the fragment `.tex` doesn't trigger class-specific warnings when compiled standalone. If it does, the preamble adds a silencing package or redefines the environment.
- **UTF-8 in fixtures.** Chicago17-nb fixture contains `Fernández`, `Bibliothèque`, `palaeographic` — unicode that must survive the latex-body render. `\usepackage[T1]{fontenc}` + `\usepackage[utf8]{inputenc}` covers this on all 5 preambles; verify once during golden regeneration that no diacritic is mangled.

## 10. Follow-up (not this spec)

- **arXiv-ready submission** (ROADMAP `later`). Builds on this target; adds preprint metadata, figure handling, and a `make arxiv` recipe.
- **biblatex pathway** (ROADMAP scope-boundary candidate). Possible if a STEM user needs native `\cite` commands; re-scope then.
- **Tier-2 style rollout with latex.** Once Vancouver / AMA / Harvard / ACM / ACS / Turabian 9 / CSE / MHRA land as styles (ROADMAP tier-2 table), each inherits this target automatically: add a `preamble.tex` (or reuse `article`-class where appropriate) and a `latex` block in its `style.md`.
