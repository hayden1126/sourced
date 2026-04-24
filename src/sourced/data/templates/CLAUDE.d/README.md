# CLAUDE.d drop-in overlays

Files under this directory layer additional rules on top of the base `CLAUDE.md`
manifest. The pattern follows systemd drop-ins: each file is self-contained, the
order of application is lexicographic, and later files take precedence on conflict.

## How overlays load

On session start:

1. Read root `CLAUDE.md` in full.
2. Read every `CLAUDE.d/*.md` file in lexicographic order (excluding this README).
3. Apply each overlay's patches to the in-memory manifest state.

The agent does not cache overlay state across sessions; every session loads
fresh from disk. Overlays are declarative patches against base-manifest sections
and are safe to re-read idempotently.

## Overlay file naming

`NN-scope-name.md` where:

- `NN` is a two-digit priority. Higher numbers apply later; later overlays win
  on conflict.
- `scope-name` describes the drop-in's scope. Conventions:
  - `10-local-*` for writer-hand-written overlays (lowest-priority group).
  - `20-project-type-*` for `sourced install --type <type>` overlays.
  - `30-*` and above are reserved for future sourced-shipped categories.

## Overlay content rules

Overlays patch only sections defined in the base manifest (§§7.1–7.6). Each
overlay file uses standard `## Patches to §<N> <heading>` subsections:

- `## Patches to §7.1 Mode registry`
- `## Patches to §7.2 Explicit triggers`
- `## Patches to §7.3 Implicit and auto-fire triggers`
- `## Patches to §7.4 Mode-to-mode gates`
- `## Patches to §7.5 Forcing artifacts`
- `## Patches to §7.6 Precedence and canonical §10 IDs`

Under each patch subsection, use plain bullet lists with the action as the leading
verb:

- `Remove:` bullets drop a registry row, trigger, gate, artifact, or rule.
- `Override:` bullets replace a base-manifest row in place.
- `Add:` bullets introduce a new row (permitted only when the base manifest's
  category supports project-type-gated additions).

Introducing new section headings outside §§7.1–7.6 is a `sourced check
--invariants` I2 violation. Overlays that add new trigger categories (e.g., a
`## Patches to §99 Custom overlay rules` section) fail the install-time check.

## Lifecycle

- `sourced install --project-type <type>` writes the matching shipped overlay
  (e.g., `20-project-type-annotated-bib.md`) on first install.
- `sourced update` refreshes the shipped overlays from the bundled templates
  on every run, idempotently.
- Writer-authored overlays in the `10-local-*` priority band are preserved by
  `sourced update` as long as they don't collide on filename with shipped overlays.
- `sourced install --force` and the `.sourced.bak` fallback cover the recovery
  paths if a writer-authored overlay is ever overwritten.

## Why overlays, not template specialization

The base `CLAUDE.md` manifest is the same for every project. Project-type
variants (e.g., annotated-bib dropping `[outlining]` / `[refining]` / `[writing]`)
ship as drop-in overlays so:

- The base is upgradable per-project without re-running `sourced install --force`.
- Project-type constraints are reversible: delete the overlay file, and the project
  returns to the base manifest.
- Debugging is explicit: `sourced check --invariants` can validate overlay scope
  independently of the base template.
- Writer-hand-written customizations in the `10-local-*` band stay orthogonal
  to shipped overlays in the `20-*` band.
