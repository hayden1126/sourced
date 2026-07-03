# Parity harness

Verifies that `pandoc --citeproc` + the vendored CSL file produces the expected output for each shipped style × paste-target combination.

## Scope

Tests the pandoc+CSL middle of CLAUDE.md §7 (steps 4-5) with deterministic inputs. Does not test the LLM-driven pre-flight, threshold check, or post-pandoc classical-abbreviations rewrite. Those are validated by the LLM reading the spec and applying it.

## Per-style structure

Each `tests/parity/<style>/` contains:

- `fixture.pandoc.md` — hand-authored collapsed markdown (shape: what §7 step 3 would emit from a representative source draft). Uses Pandoc citation syntax `[@id]`, `@id`, `[@id, p. N]`, etc.
- `fixture.bib.json` — hand-authored CSL-JSON bibliography matching the ids in `fixture.pandoc.md`.
- `golden/<target>.<ext>` — hand-authored expected output per paste target:
  - `golden/plain-markdown.md`
  - `golden/google-docs.md`
  - `golden/word.docx.md` — the intermediate markdown pandoc emits for the word target, before docx binarization. Storing `.docx` binaries in git is hostile to review; compare the markdown intermediate instead.
  - `golden/latex.tex` — document body only (between `\begin{document}` and `\end{document}`), so preamble edits don't cascade into golden diffs.

`test_parity.py` parametrizes every style × target pair (20 tests) and delegates to `_render.sh`, which invokes pandoc, writes output under `actual/`, and diffs against `golden/`.

## Running

```bash
pytest tests/parity/               # all 20 style × target pairs
pytest tests/parity/ -k mla9       # one style
pytest -m "not parity"             # everything else, on a machine without pandoc
```

Tests skip when pandoc is absent.

## Pandoc version pin

Goldens are byte-compared pandoc output, so they are pinned to the exact pandoc version in `PANDOC_VERSION`. CI installs that version; locally, `test_parity.py` warns on mismatch so golden diffs can be told apart from pandoc drift.

Upgrading the pin is a deliberate, standalone PR: install the new pandoc, regenerate all 20 goldens, update `PANDOC_VERSION`, and review the diffs. Policy details in issue #35.

## Acceptance

`diff` returns empty, or the only differences are in the tolerated-diff allowlist (trailing newlines, hard-wrap line breaks where `--wrap=preserve` is set). Any difference in ordering, punctuation, bibliography content, or rendered citation text is a failure.

## Authoring goldens

Build each golden file by hand from the style's authoritative reference (e.g., MLA Style Center examples, IEEE sample paper, Chicago NB sample paper), applied to the fixture's sources. If you cannot find a reference example for a case, mark the case in the golden with a comment and exclude it from the fixture; a harness that always passes because it ignores hard cases is worse than no harness.
