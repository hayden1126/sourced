# LaTeX paste target: ship `latex` as a 5th paste target per style

- **Date:** 2026-04-20
- **Status:** Shipped 2026-04-20 via PR #11.
- **Scope:** Add `latex` to the shipped paste-target set across all 5 styles (apa7, chicago17-ad, chicago17-nb, ieee, mla9), using the existing pandoc + citeproc + CSL pipeline. Ship a per-style pandoc template. Extend parity coverage.
- **Out of scope:** PDF compilation (user owns `pdflatex` / `xelatex` / `lualatex`). Figure/table handling beyond pandoc defaults. biblatex / natbib pathways. arXiv-ready submission (separate ROADMAP item).

## 1. Problem

The ROADMAP `### LaTeX` entry is marked `next · M · open`. STEM workflows (math, physics, CS, engineering) default to LaTeX, but `sourced` currently renders to `plain-markdown`, `google-docs`, and `word` only — STEM students either copy-paste markdown and then convert by hand, or route through `word` and lose LaTeX's native math/references. IEEE and MLA 9 are already shipped as styles, so the bibliography side is ready; what's missing is a paste target that emits `.tex`.

## 2. Decisions

### 2.1 Output artifact: `.tex` source, user compiles

Pandoc emits a standalone `.tex` file. The user runs `pdflatex` (or `xelatex` / `lualatex`) themselves. Rationale: STEM students already have a LaTeX toolchain; owning compilation inside `sourced` would require `texlive` in prereqs and turn runtime edge cases (missing fonts, package conflicts, bib backend mismatches) into `sourced` problems. The `word` target's "shipped binary" ergonomics do not generalize — Word users typically don't have a `.docx`-to-PDF pipeline; LaTeX users do.

### 2.2 Pipeline: pandoc + citeproc + CSL

No biblatex, no natbib, no new bibliography ecosystem. Pandoc's citeproc renders bibliography entries as formatted text inline in the `.tex` body via the `CSLReferences` environment, identical to how it handles `word` / `google-docs` / `plain-markdown`. Matches the CSL direct-consumption architecture shipped 2026-04-19; keeps the invariant "style behavior lives in the CSL file." A biblatex pathway would require per-style biblatex analogs (5 more vendored bibliography artifacts) and a parallel style-vs-style matrix — not worth it for v1, and materially dupes the CSL work.

### 2.3 Per-style pandoc **template** (not preamble)

Each style ships `templates/styles/<name>/template.tex` alongside its `.csl`. This is a full pandoc template — a superset of a preamble that includes `$body$`, `$title$`, conditional `$if(title)$` blocks, and the `\begin{document}` / `\end{document}` wrappers. Rationale (revised from pre-review draft): `--include-in-header` injects *after* pandoc's default preamble, so `\documentclass{article}` is already set before the injected content runs — which means IEEE styles that need `\documentclass{IEEEtran}` cannot override the class from an include-in-header file. `--template=<template.tex>` replaces pandoc's default template entirely, giving per-style control over documentclass, package load order, and document structure.

### 2.4 Figures, math, cross-references: pandoc defaults only

- **Figures.** Markdown `![caption](path)` passes through as `\includegraphics{path}` via pandoc's default rules. No `--resource-path` tuning, no float-positioning heuristics. Figure polish is a downstream ROADMAP item.
- **Math.** Inline `$...$` and display `$$...$$` pass through pandoc's default LaTeX writer unchanged. Already works; no configuration.
- **Cross-references.** `{#sec:foo}` anchors and `[text](#sec:foo)` links pass through as `\label{sec:foo}` / `\hyperref[sec:foo]{text}` (pandoc default). No special v1 handling.
- **Custom LaTeX.** Raw LaTeX inside markdown (`\command{...}`) passes through pandoc's raw-block mechanism. Writers who need arbitrary LaTeX write it directly.

Silence on any of the above would invite drift; all are explicitly "pandoc defaults, no project-level treatment."

### 2.5 Install-time changes: none

Pandoc is already a prereq for the three shipped targets (≥ 3.1, per the CSL-direct spec). `pdflatex` / `xelatex` / `lualatex` is the user's responsibility. The existing install.sh per-style mirroring already copies the whole `templates/styles/<name>/` directory, so new `template.tex` files install automatically with no script changes.

### 2.6 Pandoc version

Inherits the **pandoc ≥ 3.1** requirement from the CSL direct-consumption spec. The `CSLReferences` environment requires pandoc ≥ 2.11; project floor is higher. No new version gate introduced here.

### 2.7 LaTeX engine support

Templates support `pdflatex`, `xelatex`, and `lualatex` via an `iftex` guard (§3 below). Pinning to one engine would be simpler but cuts off the modern-TeX users that a STEM skeleton should accommodate. The guard is 3–5 lines per template; cost is negligible.

## 3. Per-style template contents

Each `template.tex` is ~40–70 lines (longer than a preamble because it includes `$body$`, `$title$`, the `\begin{document}` wrapper, and pandoc variable handling). Per-style differences below.

| Style | documentclass | Key template contents |
|---|---|---|
| apa7 | `article` | 12pt Times, 1in margins, double-spaced body (`setspace`), APA-matching title block, hanging-indent for `CSLReferences` |
| chicago17-ad | `article` | 12pt Times, 1in margins, single-spaced body, CMOS-17 typographic defaults |
| chicago17-nb | `article` | Same as `-ad`; notes are rendered by citeproc into `.tex` as inline footnote text (no `\footnote` machinery needed) |
| ieee | `IEEEtran` | `conference` option (default), `\IEEEsetup{...}` for captions, IEEE-matching column / spacing defaults; `CSLReferences` explicitly redefined to play with IEEEtran's two-column layout |
| mla9 | `article` | 12pt Times, 1in margins, double-spaced, Works Cited hanging-indent compatible |

Every template includes the `iftex` guard for encoding:

```latex
\usepackage{iftex}
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
\else
  \usepackage{fontspec}
\fi
\usepackage{csquotes}
\usepackage{hyperref}
```

Plus pandoc's standard variable plumbing (`$title$`, `$author$`, `$date$`, `$body$`, `$for(header-includes)$`).

## 4. Style.md `§Paste target expression rules` additions

Each style.md gets a `### latex` subsection under `## Paste target expression rules`. The subsection carries:

- **Pandoc recipe:** `pandoc --citeproc --standalone --template=<template.tex> --csl <csl> --bibliography <bib.json> -o <draft>.tex <draft>.pandoc.md`
- **File output:** `<draft>.tex` (compilable standalone file).
- **Paste-time instructions:** "User compiles with `pdflatex <draft>.tex` (or `xelatex` / `lualatex`)." No post-pandoc hook; no post-processing step.
- **Known quirks:** per-style notes where pandoc's default behavior collides with the style's LaTeX conventions (e.g., IEEEtran's title-block expects `\IEEEauthorblockN{}` — noted in `ieee.md`).

## 5. Parity coverage

### 5.1 Harness refactor (precursor)

Before adding the 4th target, factor the repeated pandoc block in each `tests/parity/<style>/run.sh` into a shared helper at `tests/parity/_render.sh`. Current per-style `run.sh` contains three near-identical pandoc invocations differing only by `--wrap`, `-t`, and output name. At 4 targets the copy-paste becomes maintenance burden; at 5+ (ROADMAP tier-2 rollout) it compounds. This is a no-behavior-change refactor; suite stays 15/15 green.

`_render.sh` interface:

```
_render.sh <style-dir> <target-name> <output-ext> [--extra-flag ...]
# Reads fixture.pandoc.md and fixture.bib.json from <style-dir>.
# Emits actual/<target-name>.<output-ext>; diffs against golden/<target-name>.<output-ext>.
# Extra flags pass through to pandoc (e.g., --template=<path> for latex).
# For the `latex` target, additionally extracts the body between \begin{document}
# and \end{document} before writing to actual/ (see §5.2).
```

Targets and their invocation shapes:

| Target | Output ext | Extra flags | Post-process |
|---|---|---|---|
| plain-markdown | `md` | `-t markdown --wrap=none` | none |
| google-docs | `md` | `-t markdown --wrap=preserve` | none |
| word | `docx.md` | (markdown intermediate of docx) | none |
| latex | `tex` | `--standalone --template=<template>` | extract body |

### 5.2 Body-extraction golden (revised from fragment-mode)

Parity tests the same invocation the user gets (standalone render with the actual template). After pandoc finishes, the harness extracts the content between `\begin{document}` and `\end{document}` (exclusive of the wrappers themselves) and writes it to `actual/latex.tex`. The golden compares against this extracted body.

Rationale: the pre-review draft used fragment mode (`-t latex` without `--standalone` / `--template`) for the golden, which guaranteed the harness-verified recipe diverged from the user-facing recipe — a latent drift risk. Body extraction closes that gap: the parity harness runs the exact production recipe, and only the preamble (non-body content) is excluded from the diff surface. Preamble edits no longer cascade into golden diffs; body-level CSL behavior is verified precisely.

Extraction is a one-line `sed` or `awk`:

```bash
awk '/\\begin\{document\}/,/\\end\{document\}/' actual/latex.tex.full \
  | sed '1d;$d' > actual/latex.tex
```

### 5.3 Compilation smoke check

`_render.sh` (or a separate smoke step in `run-all.sh`) does not run `pdflatex` — that's deliberately out of scope for the harness (doubles the test prereqs, introduces cross-platform compile variance). But commit 2 (§8) includes a **manual** `pdflatex` smoke run for at least the IEEE target during PR development. If compilation fails, the template fix is part of commit 2 before merge, not a post-ship fix. Elevating this from the pre-review draft's "post-ship verification" framing.

### 5.4 Suite size

After shipping: 5 styles × 4 targets = 20 parity assertions per `run-all.sh` invocation. Each style dir has 4 goldens and a `run.sh` that calls `_render.sh` four times.

## 6. CLAUDE.md changes

One small change: `§7 [formatting mode]`'s supported-paste-target list adds `latex` alongside `plain-markdown`, `google-docs`, `word`. The formatting-mode procedure itself is target-agnostic (reads style.md's §Paste target expression rules for the chosen target), so no procedural changes beyond the target name appearing in the list.

## 7. Docs updates

- `docs/STYLES.md`: `latex` appears in the shipped-paste-targets table for each style.
- `ARCHITECTURE.md`: §Paste targets enumerates `latex` as a 4th target; the parity count updates from "5×3=15" to "5×4=20."
- `docs/INSTALL.md`: no changes to prereqs; optionally note that IEEEtran lives in `texlive-publishers` (not in `texlive-base`), so IEEE users need to install a fuller TeX Live set. One sentence.
- `ROADMAP.md`: `### LaTeX` entry's status flips from `open` to `shipped`. Text can stay mostly intact — the "pipeline translates directly" framing is correct.

## 8. Delivery plan

Three commits on branch `latex-paste-target`, one PR against `main`:

1. **Refactor `run.sh` → `_render.sh` helper.** No behavior change. Suite stays 15/15. Establishes the pattern needed by commit 2.
2. **Add `latex` target.** 5 new `template.tex` files; `latex` subsection added to each `style.md`; `latex` appended to CLAUDE.md §7's target list; 5 new `golden/latex.tex` files (body-extracted); run.sh per-style calls `_render.sh` for latex. Suite goes to 20/20. **Includes manual `pdflatex` smoke verification for IEEE** (and for any other style where the template deviates meaningfully from `article`-class defaults). If smoke fails, template fix lands in this commit.
3. **Docs.** STYLES.md, ARCHITECTURE.md, ROADMAP.md, INSTALL.md updates per §7 above.

Post-merge hygiene: move this spec to `docs/archive/specs/` with a Shipped banner (matches the convention from the CSL-direct-consumption and voice-extractor-decoupling shipments).

## 9. Risks

- **IEEEtran + pandoc `CSLReferences` compilation (pre-merge blocker).** IEEEtran redefines `\bibliography`-ish machinery and expects numeric `[N]` references via BibTeX/biblatex. Pandoc citeproc emits the `CSLReferences` environment with `\CSLLeftMargin` / `\CSLRightInline` commands. These need to compile cleanly under IEEEtran's two-column layout; the IEEE template may need to redefine or wrap `CSLReferences` to cooperate. Verified at commit-2 time via the manual `pdflatex` smoke run (§5.3); not a post-ship item.
- **TeX Live collection coverage.** IEEEtran ships in `collection-publishers` (TeX Live's `texlive-publishers` Debian package), not in `texlive-base`. An IEEE user on a minimal TeX Live install gets a compile error. `docs/INSTALL.md` should call this out; not something `install.sh` can check because it's a runtime dependency, not an install-time one.
- **UTF-8 diacritics in fixtures.** Chicago17-nb fixture contains `Fernández`, `Bibliothèque`, `palaeographic` — unicode that must survive the latex-body render. The `iftex` guard handles this (pdflatex uses `inputenc`; xe/lualatex uses native UTF-8). Verify once during golden regeneration that no diacritic is mangled.

## 10. Follow-up (not this spec)

- **arXiv-ready submission** (ROADMAP `later`). Builds on this target; adds preprint metadata, figure handling, and a `make arxiv` recipe.
- **biblatex pathway** (ROADMAP scope-boundary candidate). Possible if a STEM user needs native `\cite` commands; re-scope then.
- **Tier-2 style rollout with latex.** Once Vancouver / AMA / Harvard / ACM / ACS / Turabian 9 / CSE / MHRA land as styles (ROADMAP tier-2 table), each inherits this target automatically: author a `template.tex` (or reuse `article`-class where appropriate) and add a `latex` block in its `style.md`.
