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
- `run.sh` — invokes pandoc per target, writes output under `actual/`, diffs against `golden/`.

## Running

To run one style:
```bash
cd tests/parity/<style>/
./run.sh
```

To run all styles:
```bash
cd tests/parity/
./run-all.sh
```

Requires pandoc 3.1+ on PATH.

## Acceptance

`diff` returns empty, or the only differences are in the tolerated-diff allowlist (trailing newlines, hard-wrap line breaks where `--wrap=preserve` is set). Any difference in ordering, punctuation, bibliography content, or rendered citation text is a failure.

## Authoring goldens

Build each golden file by hand from the style's authoritative reference (e.g., MLA Style Center examples, IEEE sample paper, Chicago NB sample paper), applied to the fixture's sources. If you cannot find a reference example for a case, mark the case in the golden with a comment and exclude it from the fixture; a harness that always passes because it ignores hard cases is worse than no harness.
