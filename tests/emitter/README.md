# Emitter parity fixtures

Each subdirectory is one source-type case. To verify the emitter specification against a fixture:

1. Read `citations/csl-json-emitter.md` (the specification).
2. Open `input.citations.json` (log entries).
3. Apply the spec's field-mapping and type-inference rules mentally.
4. Compare your result to `expected.bib.json`.

The fallback fixture should also produce a warning message (format specified in the emitter spec). The warning is not in `expected.bib.json` — verify the message shape by reading the spec.

These fixtures are reference material for `[formatting mode]` when it emits `<draft>.bib.json` from a project's citation log (CLAUDE.md §7 step 4). They are not executable tests; the tool's procedures are LLM-followed. `test_fixtures_wellformed.py` only guards the fixture files against corruption (missing files, invalid JSON, entries without `id`/`type`).
