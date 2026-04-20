# IEEE fixture update — golden regeneration required

The files `fixture.pandoc.md` and `fixture.bib.json` in this directory were
rewritten on 2026-04-20 so that the parity harness actually exercises
IEEE-specific rendering (numeric bracketed citations, sequential assignment,
grouped citations, repeat-cite stability, and by-appearance bibliography
ordering). The previous fixtures were copies of the APA shape and used
author-date syntax, which IEEE accepts but does not stress.

What the new fixture exercises:

- Sequential numeric assignment on first appearance — `[1]`, `[2]`, `[3]`,
  `[4]`, `[5]`.
- `able-baker-chen-davies-2019` sorts first alphabetically but appears fourth
  in the prose; the bibliography must order it fourth (by appearance), not
  first (alphabetical).
- A grouped three-id citation `[@tang-2012; @patel-2014; @oduya-2016]` to
  confirm pandoc's IEEE multi-cite rendering.
- A repeat cite of `@tang-2012` with a locator to confirm the assigned
  number `[1]` stays stable across appearances.
- A four-author source to exercise et al. behavior in the rendered
  bibliography entry.

## Golden files need regeneration

The files under `golden/` still reflect the OLD fixture and WILL diverge
from the new actual output. They must be regenerated before this test can
pass again.

There is no dedicated regeneration script in the tree. To regenerate:

1. Run the harness once to populate `actual/`:
   ```bash
   cd tests/parity/ieee/
   ./run.sh || true   # diffs against the stale goldens and will fail
   ```
2. Hand-review each file in `actual/` against the IEEE Editorial Style Manual
   (https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/)
   and the sample papers it references. In particular, confirm:
   - the first four text citations render as `\[1\]` through `\[4\]`;
   - `@tang-2012` keeps the number `[1]` on its repeat appearance with
     `[1, p. 118]`;
   - the grouped cite renders as three separate bracketed numbers
     (pandoc's IEEE multi-cite convention; see the existing golden shape);
   - the bibliography lists entries in appearance order: `tang-2012`,
     `patel-2014`, `oduya-2016`, `able-baker-chen-davies-2019`,
     `ieee-std-2020` — NOT alphabetical;
   - the four-author entry uses `A. Able, B. Baker, C. Chen, and D. Davies`
     in the bibliography (IEEE typically lists all authors unless there
     are more than six).
3. Once the `actual/` output is correct, promote it:
   ```bash
   cp actual/plain-markdown.md golden/plain-markdown.md
   cp actual/google-docs.md    golden/google-docs.md
   cp actual/word.docx.md      golden/word.docx.md
   ```
4. Delete this `README-FIXTURE-UPDATE.md` once the goldens are in place and
   `./run.sh` exits 0.
