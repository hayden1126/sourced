# Installation

[← Back to README](../README.md)

## First-time install (end user)

Prerequisites:
- Python 3.10+
- `pipx` (install via `brew install pipx` on macOS, `sudo apt install pipx python3-venv` on Ubuntu/WSL, `winget install pipx` on Windows-not-WSL)
- After installing pipx: `pipx ensurepath`, then **open a new terminal** (don't `source ~/.zshrc` — `ensurepath` may write to `.zprofile` instead)
- Read access to `github.com/hayden1126/sourced` (request from maintainer)

Install:

```bash
# HTTPS (default for non-dev users; works through corporate firewalls):
pipx install 'git+https://<TOKEN>@github.com/hayden1126/sourced.git'

# SSH (power-user path; pre-seed known_hosts on a fresh machine):
ssh-keyscan github.com >> ~/.ssh/known_hosts
pipx install git+ssh://git@github.com/hayden1126/sourced.git
```

Verify:

```bash
sourced --version
sourced check
```

`sourced check` verifies prerequisites (`pdftotext`, `pdfinfo`, `pdftoppm`, `pandoc`, `python3`) and the `~/.claude/` baseline. It does not run sudo or touch system packages.

First-run global setup:

```bash
sourced global-install   # populates ~/.claude/; prompts for user name on first run
```

Per-project:

```bash
cd ~/writing/new-paper
sourced install --brief my_paper --voice academic --style apa7

# or sugar:
cd ~/writing
sourced new my-paper --voice academic --style apa7
```

Run `sourced <subcommand> --help` for the full flag set on each command.

## Note for contributors with an existing clone

The bundled templates moved under `src/sourced/data/` in phase 1. If you had
muscle memory for `templates/CLAUDE.md` or `agents/source-finder.md`, those
paths now live at `src/sourced/data/templates/CLAUDE.md` and
`src/sourced/data/agents/source-finder.md`. Editable installs (`pipx install -e .`)
hot-reload edits to these paths.

## Optional: TeX Live for the `latex` paste target

The `latex` paste target emits a standalone `.tex` file. Compiling that `.tex` to a PDF is outside `sourced`'s scope — `sourced check` does not verify a TeX distribution, and `sourced` never invokes `pdflatex` from any mode. If you plan to use the `latex` target, install TeX Live (or an equivalent) yourself.

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

## Updates

```bash
pipx upgrade sourced
sourced global-install   # idempotent; refresh shipped files

cd ~/writing/my-paper
sourced update           # refresh managed block of CLAUDE.md
```

**Known pitfall:** `pipx upgrade` may silently no-op if `pyproject.toml`'s version doesn't bump (pip's resolver sees same version → already-satisfied). Mitigation: `hatch-vcs` derives version from git tag; the maintainer must tag releases. Reliable alternative: `pipx install --force 'git+https://...@main'`.

## Version pinning / rollback

```bash
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@v0.3.0'
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@<sha>'
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@main'
```

For rollback testing where pip's wheel cache may serve stale: add `--pip-args="--no-cache-dir"`.

## Uninstall

```bash
pipx uninstall sourced
# Manually remove ~/.claude/ if desired:
rm -rf ~/.claude/{agents,citations,templates,voice,style,skills,filters}
rm ~/.claude/sourced.config
# preserve ~/.claude/settings.json and any user-added directories
```

## Contributor onboarding

```bash
git clone git@github.com:hayden1126/sourced.git
cd sourced
pipx install --force -e .
```

Edits to `src/sourced/*.py` AND `src/sourced/data/*` take effect immediately (the `.pth` editable-install mechanism covers the data directory because it lives under `src/sourced/`).

If `pipx install --force -e .` leaves stale metadata:
```bash
pipx uninstall sourced && pipx install -e .
```

Tests:
```bash
pytest                       # everything: unit + integration + golden + parity + emitter well-formedness
pytest -m "not parity"       # skip the 20 pandoc goldens (for machines without pandoc)
```

Parity goldens are pinned to the pandoc version in `tests/parity/PANDOC_VERSION`; see `tests/parity/README.md`.

## Migration from the legacy installer

If you previously used `install.sh`, install the CLI and migrate your projects:

1. `pipx install --force git+ssh://git@github.com/hayden1126/sourced.git@main` — install the new CLI.
2. `sourced check` — verify prereqs + `~/.claude/` baseline; debug failures before any project work.
3. **For each active project, dry-run first:**
   ```bash
   cd <project>
   sourced update --dry-run    # surfaces sentinel-regex mismatches without mutation
   ```
4. For each project that dry-runs cleanly: `sourced update` (no flag) to apply. Each first-touch writes a `<file>.sourced.bak` sibling for rollback safety.
5. For any project that fails dry-run: inspect, decide whether to `sourced install --force` (recreate; user re-applies any unmanaged content) or hand-fix the sentinels.

## Change your name

Edit or delete `~/.claude/sourced.config` then re-run `sourced global-install`.

## File layout

Global files (installed once, shared across projects) and per-project files (rendered per-paper):

| Path | Scope |
|------|-------|
| `~/.claude/agents/source-finder.md` | global subagent (parallel source research) |
| `~/.claude/agents/voice-extractor.md` | global subagent (one-shot voice calibration from samples) |
| `~/.claude/citations/schema.md` | global citation log schema |
| `~/.claude/templates/brief.template.md` | global brief template (essay) |
| `~/.claude/templates/brief.template.annotated-bib.md` | global brief template (annotated bibliography) |
| `~/.claude/voice/<name>.md` | voice library (shipped + custom voices available for project selection) |
| `~/.claude/style/<name>.md` | style library (shipped + custom styles) |
| `~/.claude/style/<name>/<asset>` | per-style asset dir (CSL file, reference.docx, on-demand reference tables like `classical-abbreviations.md`) |
| `~/.claude/skills/<name>/` | skill library; Claude Code auto-discovers skills globally (currently ships `browser-reader-extract`) |
| `<project>/CLAUDE.md` | per-project; contains the inlined academic-researcher rules |
| `<project>/config/voice.md` | per-project; the active voice for this project |
| `<project>/config/style.md` | per-project; the active citation style for this project |
| `<project>/config/<draft>.brief.md` | per-project; sibling to voice/style under config/ |
| `<project>/sources/<draft>.citations.json` | per-project; under sources/ next to other source artifacts |
| `<project>/<draft>.<target>.md` | formatted output written by `[formatting mode]` (e.g., `<draft>.gdocs.md`, `<draft>.docx.md`) |
| `<project>/<draft>.docx` | submission binary when `[formatting mode for word]` runs pandoc on the intermediate |
| `<project>/<draft>.bib.json` | CSL-JSON bibliography emitted for `word` target against collapsed source-level IDs |
| `<project>/.claude/citations/working.citations.json` | per-project, pre-draft |
| `<project>/.claude/citations/working.<finder-id>.json` | per-project, source-finder shards |

## pipx gotchas

| Symptom | Cause | Remediation |
|---|---|---|
| `pipx: command not found` | `~/.local/bin` not on PATH | `pipx ensurepath` + new terminal |
| Python version mismatch | Multiple python3 on system | `pipx install --python python3.11 ...` |
| `Permission denied (publickey)` | SSH agent missing the key | `ssh-add ~/.ssh/id_ed25519`, or use HTTPS+PAT |
| `Are you sure you want to continue connecting?` hang | First-time SSH to github.com in detached TTY | `ssh-keyscan github.com >> ~/.ssh/known_hosts` first |
| `pipx upgrade` no-ops | Version not bumped | `pipx install --force ...@main` |
| Stale `sourced` from `pip install --user sourced` | Pre-pipx remnant | `which -a sourced`, `pip uninstall sourced` |
| Conda env active during install | pipx picked up conda's python | `conda deactivate && pipx install ...` |
| Port 22 blocked (corporate / campus wifi) | Firewall | Use HTTPS+PAT path; or `~/.ssh/config` with `Host github.com / HostName ssh.github.com / Port 443` |

## Repo structure

```
sourced/
├── ARCHITECTURE.md              # surface-area map (read first)
├── README.md                    # landing page, quickstart
├── pyproject.toml               # package metadata + hatch-vcs versioning
├── docs/
│   ├── INSTALL.md               # this file
│   ├── MODES.md
│   ├── SKILLS.md                # shipped skills (e.g. browser-reader-extract)
│   ├── VOICES.md
│   └── STYLES.md
├── src/
│   └── sourced/
│       ├── cli.py               # argparse root; subcommand registration + dispatch
│       ├── commands/            # one module per subcommand (install, update, check, …)
│       ├── validators/          # stateless validators (CSL title, iron rules, exemptions, invariants)
│       ├── render.py            # {{USER}} substitution + bundled-data resolution (importlib.resources)
│       ├── project.py           # per-project state (voice, style, type markers)
│       ├── mirror.py            # ~/.claude/ mirroring logic
│       ├── config.py            # sourced.config read/write
│       ├── context.py           # runtime-state dataclass (dry-run, verbose, quiet, color, strict)
│       ├── errors.py            # structured error types
│       ├── ui.py                # ANSI color/print helpers
│       └── data/
│           ├── agents/
│           │   ├── source-finder.md
│           │   └── voice-extractor.md
│           ├── citations/
│           │   └── schema.md
│           ├── filters/         # Pandoc Lua filters (promoted from templates/filters/)
│           ├── skills/
│           │   └── browser-reader-extract/
│           │       ├── SKILL.md
│           │       ├── package.json
│           │       └── overdrive.mjs
│           └── templates/
│               ├── CLAUDE.md
│               ├── brief.template.md
│               ├── brief.template.annotated-bib.md
│               ├── styles/
│               │   ├── apa7.md
│               │   ├── apa7/
│               │   │   ├── apa.csl
│               │   │   └── template.tex
│               │   ├── chicago17-ad.md
│               │   ├── chicago17-ad/
│               │   │   ├── chicago-author-date-17th-edition.csl
│               │   │   ├── classical-abbreviations.md
│               │   │   └── template.tex
│               │   ├── chicago17-nb.md
│               │   ├── chicago17-nb/
│               │   │   ├── chicago-notes-bibliography-17th-edition.csl
│               │   │   ├── classical-abbreviations.md
│               │   │   └── template.tex
│               │   ├── ieee.md
│               │   ├── ieee/
│               │   │   ├── ieee.csl
│               │   │   └── template.tex
│               │   ├── mla9.md
│               │   └── mla9/
│               │       ├── classical-abbreviations.md
│               │       ├── modern-language-association.csl
│               │       └── template.tex
│               └── voices/
│                   ├── academic.md
│                   ├── casual.md
│                   ├── hybrid.md
│                   ├── journalistic.md
│                   ├── narrative.md
│                   └── technical.md
└── tests/
    ├── cli/
    │   ├── unit/
    │   ├── integration/
    │   └── golden/
    ├── emitter/
    └── parity/
        └── run-all.sh
```
