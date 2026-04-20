# chicago17-nb fixture update — golden regeneration required

The files `fixture.pandoc.md` and `fixture.bib.json` in this directory were
rewritten on 2026-04-19 so that the parity harness actually exercises
chicago17-nb-specific rendering (footnote-style first cite, short-form
repeat, block-quote citation, and multi-author note behavior). The previous
fixtures were copies of the APA shape and used author-date syntax, which the
NB style nominally accepts but which does not stress its note machinery.

What the new fixture exercises:

- A first citation of `@fernandez-2011` that should render as a FULL-FORM
  footnote: author, title, publisher, year, and (for later cites) page.
- A later cite of the same source that should render in SHORT FORM —
  either `Fernández, Liturgical Continuity, 214.` or the style's exact
  shortened form. The 17th edition prefers the short form over "Ibid."
- A block-quoted passage followed by a citation to exercise how pandoc +
  chicago17-nb handle the block-quote note attachment. (The block-quote
  threshold is controlled inside the CSL file; this fixture only provides
  the input shape — the golden must reflect whatever the style emits.)
- A two-author source (`herrmann-schulz-2021`) to exercise the
  "Herrmann and Schulz" joining in notes (no ampersand in NB style).
- A four-author source (`okafor-lindqvist-tanaka-rossi-2018`) to exercise
  the "Okafor et al." collapse in notes while the bibliography entry
  still lists all four authors.
- An institutional-author entry (`bnf-guide-2022`) to confirm literal
  author handling in both notes and bibliography.

## Golden files need regeneration

The files under `golden/` still reflect the OLD fixture and WILL diverge
from the new actual output. They must be regenerated before this test can
pass again.

There is no dedicated regeneration script in the tree. To regenerate:

1. Run the harness once to populate `actual/`:
   ```bash
   cd tests/parity/chicago17-nb/
   ./run.sh || true   # diffs against the stale goldens and will fail
   ```
2. Hand-review each file in `actual/` against the Chicago Manual of Style,
   17th edition (Notes-Bibliography system), §14. In particular, confirm:
   - the first note for `@fernandez-2011` is FULL-FORM (author given name
     first in the note, title in italics for a book, publisher and year,
     no page on the first appearance since the first cite has no locator);
   - the second and third cites of `@fernandez-2011` render in SHORT FORM
     with the page number, not as "Ibid.";
   - the two-author note uses "Klaus Herrmann and Annika Schulz" (not
     "Herrmann & Schulz");
   - the four-author note collapses to "Chidinma Okafor et al." while the
     bibliography entry spells out all four names with the first author
     inverted;
   - the block-quoted passage produces a single footnote marker at the
     end of the quote (not inline inside the blockquote body), matching
     the pandoc default behavior for `[@id]` that immediately follows a
     block quote;
   - the institutional-author entry uses "Bibliothèque nationale de France"
     verbatim in both note and bibliography positions.
3. Once the `actual/` output is correct, promote it:
   ```bash
   cp actual/plain-markdown.md golden/plain-markdown.md
   cp actual/google-docs.md    golden/google-docs.md
   cp actual/word.docx.md      golden/word.docx.md
   ```
4. Delete this `README-FIXTURE-UPDATE.md` once the goldens are in place and
   `./run.sh` exits 0.
