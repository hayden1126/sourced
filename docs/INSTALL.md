# Installation

[← Back to README](../README.md)

## Install

Clone wherever you keep repos. `install.sh` finds itself via `$BASH_SOURCE`, so the clone path doesn't matter.

```bash
git clone https://github.com/hayden1126/sourced.git
cd sourced
./install.sh --global-only      # first time, from inside the repo
```

On first run you'll be prompted for your name. It gets saved to `~/.claude/sourced.config` and substituted into the templates on every render.

After `--global-only`, the global files are available to Claude Code from any working directory:

- `~/.claude/agents/source-finder.md`
- `~/.claude/agents/voice-extractor.md`
- `~/.claude/citations/schema.md`
- `~/.claude/citations/csl-json-emitter.md`
- `~/.claude/templates/brief.template.md`
- `~/.claude/templates/brief.template.annotated-bib.md`
- `~/.claude/voice/<name>.md` (voice library; shipped voices land here, custom voices can be added alongside)
- `~/.claude/style/<name>.md` (style library; same pattern)
- `~/.claude/style/<name>/<asset>` (per-style asset directory; e.g., `chicago17-ad/chicago-author-date-17th-edition.csl`, `chicago17-ad/classical-abbreviations.md`, `chicago17-ad/reference-styled.docx` when shipped)
- `~/.claude/skills/<name>/` (skill library; Claude Code auto-discovers skills from this path across every session under the home directory)

These paths are fixed; the install targets always go to `~/.claude/`, regardless of where the repo itself lives.

## Prerequisite check

`install.sh` runs `check_prerequisites` before any per-project file writes. It verifies `pdftotext`, `pandoc`, and `python3` are on PATH and aborts with the apt/brew install commands if any is missing. `--global-only` intentionally skips the check: that code path only copies voices, agents, skills, filters, and styles into `~/.claude/` and never invokes pandoc, python3, or pdftotext, so a fresh machine can bootstrap global files without the formatting/research toolchain installed. This is check-only; the installer does not run sudo or touch system packages. See the README Prerequisites section for what each tool does and how to install it.

## Optional: TeX Live for the `latex` paste target

The `latex` paste target emits a standalone `.tex` file. Compiling that `.tex` to a PDF is outside `sourced`'s scope — `install.sh` does not check for a TeX distribution, does not depend on one, and does not invoke `pdflatex` from any mode. If you plan to use the `latex` target, install TeX Live (or an equivalent) yourself.

### Minimum vs. full

- **`article`-class styles (APA, Chicago author-date, Chicago notes-bibliography, MLA):** `texlive-latex-base` + `texlive-latex-recommended` + `texlive-latex-extra` + `texlive-fonts-recommended`. Provides `pdflatex`, the `article` class, `geometry`, `setspace`, `hyperref`, `iftex`, `calc`, `mathptmx` (Times-family font), and `csquotes` (the last lives in `texlive-latex-extra` on current Debian / Ubuntu, not in `-recommended`).
- **IEEE style:** additionally requires `texlive-publishers` (contains `IEEEtran`). A minimal install without this package will fail to compile the IEEE latex output.
- **`xelatex` / `lualatex` engines** (optional — `pdflatex` is the default and works with the shipped templates): `texlive-xetex` / `texlive-luatex` packages. The shipped templates compile under all three engines via an `iftex` guard.
- **Full (~5 GB):** `texlive-full` installs everything and eliminates per-style package questions.

### Install commands

**Debian / Ubuntu / WSL:**

```bash
# Minimum for article-class styles (note: csquotes lives in texlive-latex-extra)
sudo apt-get install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended

# Add IEEEtran for the IEEE style
sudo apt-get install -y texlive-publishers

# One-shot: everything
sudo apt-get install -y texlive-full
```

**macOS:**

```bash
brew install --cask basictex   # ~100 MB, then `sudo tlmgr install <package>` for anything missing
# or
brew install --cask mactex     # ~4 GB, full distribution
```

After installing BasicTeX, you may need `sudo tlmgr update --self && sudo tlmgr install IEEEtran` (or whichever package LaTeX reports missing) before compiling.

**Windows:** install [MiKTeX](https://miktex.org) or [TeX Live](https://www.tug.org/texlive/). MiKTeX fetches missing packages on-demand during the first compile.

### Compiling

Once installed, compile with:

```bash
pdflatex <draft>.tex
```

Or `xelatex` / `lualatex` — the shipped templates compile under all three.

## Per-project setup

Each writing project gets its own `CLAUDE.md` (the academic-researcher definition, rendered with your name), `voice.md`, and `style.md`. Run `install.sh` from inside the project:

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh
```

This re-renders global files (cheap, idempotent) and drops `CLAUDE.md`, `voice.md`, and `style.md` into the project directory. With `--brief <name>` it also drops an empty `<name>.brief.md`:

```bash
/path/to/sourced/install.sh --brief my_paper
# → creates CLAUDE.md, voice.md, style.md, and my_paper.brief.md in the current directory
```

## Updating

### Updating the sourced install

When you pull new changes to the `sourced` repo, re-render the global files:

```bash
cd /path/to/sourced
git pull
./install.sh --global-only
```

Then refresh each project (see below).

### Updating a project

To refresh a project's CLAUDE.md in place without losing content you've added outside the managed block (project-specific notes, active briefs, TODO lists):

```bash
cd ~/writing/my-paper
/path/to/sourced/install.sh --update
```

`--update` does three things. First, it replaces only the content between the `<!-- sourced:begin managed -->` and `<!-- sourced:end managed -->` sentinels in CLAUDE.md; everything outside those sentinels is preserved. Second, it refreshes `voice.md` from the library voice the project was installed with (read from the marker on voice.md line 1). Third, it refreshes `style.md` from the library style the project was installed with. Upstream rule changes propagate via `--update`.

To switch to a different voice or style on an existing project, pass `--update --voice <new>` (explicit voice switch), `--update --style <new>` (explicit style switch), or `--force` (replace everything).

### Overwriting outright

If a CLAUDE.md exists but you want a fresh render regardless:

```bash
/path/to/sourced/install.sh --force
```

## Flags reference

| Flag | Effect |
|------|--------|
| `--global-only` | Install or refresh global files only (source-finder, voice-extractor, schema, brief template, voice library, style library). Skip per-project files. |
| `--project <path>` | Drop per-project files into `<path>` instead of `$PWD`. |
| `--force` | Overwrite existing CLAUDE.md, voice.md, style.md, and brief (if `--brief`) without asking. |
| `--update` | Refresh the managed block of CLAUDE.md (preserving content outside sentinels) and refresh `voice.md` and `style.md` from the project's installed voice and style. |
| `--voice <name>` | Pick the voice rendered into this project's `voice.md` (default: `academic`). Shipped voices live in `templates/voices/`; custom voices can be placed at `~/.claude/voice/<name>.md`. |
| `--style <name>` | Pick the citation/document style rendered into this project's `style.md` (default: `apa7`). Shipped styles live in `templates/styles/`; custom styles can be placed at `~/.claude/style/<name>.md`. |
| `--brief <name>` | Also drop `<name>.brief.md` into the project, rendered from the brief template that matches `--type` (`brief.template.md` for `essay`, `brief.template.annotated-bib.md` for `annotated-bib`). |
| `--type <kind>` | Pick the project kind: `essay` (default) or `annotated-bib`. Default writes no marker and leaves the project on the standard essay mode graph. `annotated-bib` writes a `.sourced-project-type` marker at the project root, selects `templates/brief.template.annotated-bib.md` when paired with `--brief`, and switches the project onto the annotated-bibliography mode graph (see `docs/MODES.md`). Switching the type on an existing project requires `--force` or `--update`. |

## File layout

Global files (installed once, shared across projects) and per-project files (rendered per-paper):

| Path | Scope |
|------|-------|
| `~/.claude/agents/source-finder.md` | global subagent (parallel source research) |
| `~/.claude/agents/voice-extractor.md` | global subagent (one-shot voice calibration from samples) |
| `~/.claude/citations/schema.md` | global citation log schema |
| `~/.claude/templates/brief.template.md` | global brief template |
| `~/.claude/voice/<name>.md` | voice library (shipped + custom voices available for project selection) |
| `~/.claude/style/<name>.md` | style library (shipped + custom styles) |
| `~/.claude/style/<name>/<asset>` | per-style asset dir (CSL file, reference.docx, on-demand reference tables like `classical-abbreviations.md`) |
| `~/.claude/skills/<name>/` | skill library; Claude Code auto-discovers skills globally (currently ships `browser-reader-extract`) |
| `<project>/CLAUDE.md` | per-project; contains the inlined academic-researcher rules |
| `<project>/voice.md` | per-project; the active voice for this project |
| `<project>/style.md` | per-project; the active citation style for this project |
| `<project>/<draft>.brief.md` | per-project, next to the draft |
| `<project>/<draft>.citations.json` | per-project, next to the draft |
| `<project>/<draft>.<target>.md` | formatted output written by `[formatting mode]` (e.g., `<draft>.gdocs.md`, `<draft>.docx.md`) |
| `<project>/<draft>.docx` | submission binary when `[formatting mode for word]` runs pandoc on the intermediate |
| `<project>/<draft>.bib.json` | CSL-JSON bibliography emitted for `word` target against collapsed source-level IDs |
| `<project>/.claude/citations/working.citations.json` | per-project, pre-draft |
| `<project>/.claude/citations/working.<finder-id>.json` | per-project, source-finder shards |

## Change your name

Edit or delete `~/.claude/sourced.config` and re-run `./install.sh --global-only`.

## Repo structure

```
sourced/
├── ARCHITECTURE.md              # surface-area map (read first)
├── README.md                    # landing page, quickstart
├── docs/
│   ├── INSTALL.md               # this file
│   ├── MODES.md
│   ├── SKILLS.md                # shipped skills (e.g. browser-reader-extract)
│   ├── VOICES.md
│   └── STYLES.md
├── install.sh                   # global + per-project install; check_prerequisites + voice/style/skill mirroring
├── agents/
│   ├── source-finder.md
│   └── voice-extractor.md
├── citations/
│   └── schema.md
├── skills/
│   └── browser-reader-extract/  # extract text + [p. N] markers from DRM'd browser readers
│       ├── SKILL.md
│       ├── package.json
│       └── overdrive.mjs
└── templates/
    ├── CLAUDE.md
    ├── brief.template.md
    ├── brief.template.annotated-bib.md
    ├── styles/
    │   ├── apa7.md
    │   ├── apa7/                # per-style assets
    │   │   ├── apa.csl
    │   │   └── template.tex
    │   ├── chicago17-ad.md
    │   ├── chicago17-ad/
    │   │   ├── chicago-author-date-17th-edition.csl
    │   │   ├── classical-abbreviations.md
    │   │   └── template.tex
    │   ├── chicago17-nb.md
    │   ├── chicago17-nb/
    │   │   ├── chicago-notes-bibliography-17th-edition.csl
    │   │   ├── classical-abbreviations.md
    │   │   └── template.tex
    │   ├── ieee.md
    │   ├── ieee/
    │   │   ├── ieee.csl
    │   │   └── template.tex
    │   ├── mla9.md
    │   └── mla9/
    │       ├── classical-abbreviations.md
    │       ├── modern-language-association.csl
    │       └── template.tex
    └── voices/
        ├── academic.md
        ├── casual.md
        ├── hybrid.md
        ├── journalistic.md
        ├── narrative.md
        └── technical.md
```
