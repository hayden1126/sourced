# Overlay: annotated-bib project type

Applies to projects where `.sourced-project-type` contains `annotated-bib`. Shipped
by `sourced install --type annotated-bib`; refreshed by `sourced update`.

The base `CLAUDE.md §7.1` registry already carries a `Project types` column that
names the valid project types per mode. This overlay makes the annotated-bib
exclusions explicit at dispatch time so the agent does not re-filter the full
registry every turn, and documents the project-type-specific gates that are
otherwise implicit.

## Patches to §7.1 Mode registry

Remove (essay-only; unreachable in annotated-bib projects):

- `outlining`
- `refining`
- `writing`

The base-manifest `Project types` column for each of these modes names `essay`
only; this overlay removes the rows from the allowed-modes list for this project
so dispatch reads a filtered registry directly.

## Patches to §7.2 Explicit triggers

Remove triggers for the removed modes:

- `"draft this" / "outline this" / "structure this"` → `[outlining mode]`
- `"refine this" / "tighten the outline" / "stress-test this"` → `[refining mode]`
- `"write this" / "put this into prose" / "write out X"` → `[writing mode]`

Triggers for `[annotated-bib mode]` come from the base manifest §7.2 and are
unaffected by this overlay.

## Patches to §7.4 Mode-to-mode gates

Remove gates involving the removed modes:

- `outlining → refining`
- `refining → writing`
- `writing → editing`

The `research → annotated-bib` transition path is governed by the base manifest's
`→ annotated-bib` row and does not require an overlay-level addition. The
transition fires on explicit {{USER}} request after research returns; the full
procedure lives in `docs/modes/annotated-bib.md` step 1 (entry).

## Patches to §7.5 Forcing artifacts

No patches. The base-manifest forcing artifacts apply unchanged:

- §4 audit list still fires at `[editing mode]` pass 2 against annotation prose.
- Voice audit surface-scan report still gates `editing → formatting`.
- Inline-quote-threshold list still gates `formatting → (terminal)`.
- Scope-delta list still fires on §6 scope-growth soft-stop during any mode.

The annotated-bib variant's modified pass application (Pass 8 skipped; Pass 9
reduced) is documented in `docs/modes/editing.md` and `docs/modes/annotated-bib.md`;
it does not change which artifacts are emitted, only which passes fire.

## Patches to §7.6 Precedence and canonical §10 IDs

No patches. §10 canonical IDs are framework-wide; the §4 verbatim > §10 carve-out
applies to all prose-emitting modes including `[annotated-bib mode]` annotations.
