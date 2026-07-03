# `sourced` CLI: install.sh decomposition into a Python package

- **Date:** 2026-04-21
- **Status:** Shipped in four phases: PRs #19-#23 (phase 1, 2026-04-22), #24 (phase 2, manifest extraction), #25 (phase 3, voice pipeline), #26 (phase 4, directory restructure, 2026-04-25). Remaining phase-5 items (doctor diagnostics, `--format=json`, shell completion, config migration) tracked in ROADMAP §Python CLI; CI shipped 2026-07-03.
- **Scope:** Replace the 792-line `install.sh` with a Python CLI distributed via `pipx install` from the private GitHub repo. Phase 1 ships parity + Tier 1 + Tier 2 UX improvements. Phase 2 (separate plan, deferred) ships CI, structured output, and deeper diagnostics. C-Go static binary is a separate ROADMAP item, later.
- **Out of scope (this design):** New modes, new validators, schema changes, `~/.claude/` layout changes, template content edits beyond what install.sh already does. The Go/Rust binary port. Public PyPI distribution. Windows-native (WSL is fine).

## 1. Problem

`install.sh` has accumulated 11 functions and ~792 lines: prereq checks, template rendering, CSL validation, iron-rule extraction + normalization + validation, §10 exemption validation, project-type marker IO, skill/filter mirroring, brief rendering, plus inline flag parsing and orchestration. Every audit cycle surfaces 2-4 install.sh findings of varying severity (current cycle-3 carries 4 open sharp-edges: F27 pandoc parse, F28 sentinel awk, F29 marker whitespace, F34 dotglob portability). The file's primary failure mode is becoming a junk drawer where every new responsibility gets a few more lines and a few more sharp edges.

The decomposition reframes responsibilities into a structured codebase with proper testing, structured argument parsing, structured error handling, and a real test framework. Behavior parity is the floor; Tier 1 + Tier 2 UX improvements are the deliberate ceiling.

## 2. Decisions (locked through brainstorming)

### 2.1 Language: Python

Already a hard prereq. No new runtime dependency. Mature CLI tooling (argparse, importlib.resources). Matches the markdown-heavy work install.sh does. Locked over alternatives: bash (no testability win), Node (makes Node a hard dep), Go/Rust (great for end-user ergonomics but real upfront cost; deferred to a separate ROADMAP item).

### 2.2 Distribution: git-direct from the private repo

```bash
pipx install git+ssh://git@github.com/hayden1126/sourced.git
# or HTTPS for non-dev users / port-22-blocked networks:
pipx install 'git+https://<TOKEN>@github.com/hayden1126/sourced.git'
```

No PyPI publication. Repo stays private; only people with collaborator access can install. Same access model as today's `git clone`.

### 2.3 Templates bundled inside the package

Canonical location: `src/sourced/data/`. Top-level `templates/`, `agents/`, `citations/`, `skills/`, `filters/` directories move under there. Reasoning: `pyproject.toml`'s `force-include` is a build-time directive — in editable installs (the contributor workflow), it snapshots data once at install time and `importlib.resources.files()` resolves to that snapshot, not the working tree. Relocating to `src/sourced/data/` lets the standard editable-install `.pth` mechanism cover the data directories automatically, giving contributors live edits without rebuild.

This is a one-time `git mv` plus updates to `tests/parity/_render.sh` (CSL lookup path) and any docs that reference top-level template paths.

### 2.4 Delivery shape: C-loose (MVP-first, behavioral improvements allowed)

Phase 1 ships full parity with install.sh plus Tier 1 + Tier 2 UX improvements. Tier 3 (CI, JSON output, doctor, completion, user-defaults config) deferred to phase 2. Tier 4 (new modes, new validators, schema changes) explicitly out of scope.

### 2.5 Command surface: verb subcommands

Six subcommands in phase 1: `install`, `global-install`, `new`, `update`, `switch voice|style`, `check`. See §4 for full flag specs.

### 2.6 install.sh fate: deleted on phase-1 merge, preserved at tag

`install.sh` removed from the working tree. Tagged at `legacy/install-sh-final` on its last commit before deletion. Referenced in the README rollback note for one week post-merge. After one week the tag stays as historical record but the README rollback note is removed.

### 2.7 Improvements scope

Tier 1 (table-stakes for a proper CLI) + Tier 2 (cheap, visible wins) ship in phase 1. Tier 3 deferred. Concrete list per Tier in §5 and §8.

## 3. Architecture and package layout

Python package using src-layout. Entry point: `sourced` (registered via `pyproject.toml` `[project.scripts]`).

```
sourced/                          # repo root
├── pyproject.toml                # Hatchling + hatch-vcs (no force-include — data lives under src/sourced/)
├── src/
│   └── sourced/
│       ├── __init__.py           # __version__ via importlib.metadata
│       ├── __main__.py           # python -m sourced → cli:main
│       ├── cli.py                # argparse root, subcommand dispatch, exit-code mapping
│       ├── context.py            # Context dataclass: dry_run, verbose, quiet, color, strict
│       ├── errors.py             # SourcedError + 7 typed subclasses
│       ├── ui.py                 # color/tty + error formatting; dry-run lives in Context, not here
│       ├── config.py             # ~/.claude/sourced.config (user-global only)
│       ├── project.py            # .sourced-project-type marker + project detection + sentinel parsing
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── _pipeline.py      # shared install pipeline (run_install, run_global_install)
│       │   ├── install.py        # `sourced install` — calls _pipeline.run_install
│       │   #                       (and global_install.py / new.py likewise)
│       │   ├── global_install.py # `sourced global-install`
│       │   ├── new.py            # `sourced new <name>`
│       │   ├── update.py         # `sourced update`
│       │   ├── switch.py         # `sourced switch voice|style`
│       │   └── check.py          # `sourced check`
│       ├── render.py             # template-string substitution; pure functions
│       ├── mirror.py             # file-tree mirroring; shutil.copytree wrapper
│       ├── validators/
│       │   ├── __init__.py       # shared Finding dataclass
│       │   ├── csl.py            # validate_csl_title (PRE-render: template-static)
│       │   ├── iron_rules.py     # extract + normalize + validate (POST-render)
│       │   └── exemptions.py     # §10 exemption syntax (POST-render)
│       └── data/                 # CANONICAL — also auto-included by editable install
│           ├── templates/
│           ├── agents/
│           ├── citations/
│           ├── skills/
│           ├── filters/
│           └── facts.yml         # invariant registry (§7)
├── tests/
│   ├── conftest.py               # tmp_home, tmp_project, bundled_data_root, clean_ansi
│   ├── cli/
│   │   ├── unit/                 # pure-function tests
│   │   ├── integration/          # end-to-end subcommand invocations
│   │   ├── parity/               # CLI vs install.sh — DELETED on merge
│   │   └── golden/               # rendered-template snapshots
│   ├── emitter/                  # existing, unchanged
│   └── parity/                   # existing, unchanged (style × paste-target goldens)
├── docs/
│   └── superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md  # this file
├── ARCHITECTURE.md
├── README.md
└── ROADMAP.md
```

### Module-boundary principles (enforced)

1. **`cli.py` is the only module that touches argparse.** `commands/*.py` accept plain Python args, not `argparse.Namespace`.
2. **`commands/*.py` is user-facing orchestration only.** Composes `render`, `mirror`, `validators`, `config`. No I/O policy (color, exit codes) — that's `ui.py`.
3. **`validators/*.py` are pure.** Input → `list[Finding]`. Never raise. Pre-render validators (`csl.py`) check static template invariants; post-render validators (`iron_rules.py`, `exemptions.py`) check rendered prose.
4. **`data/` is read-only package data.** Never written. Never used as a scratch path.
5. **No module imports from `tests/`.** No test imports from `data/` (use `bundled_data_root` fixture).
6. **Context flows from `cli.py` to commands as an explicit dataclass.** No module globals for dry-run / verbose / quiet / strict / color.

### Build configuration

```toml
[build-system]
requires = ["hatchling>=1.24", "hatch-vcs>=0.4"]
build-backend = "hatchling.build"

[project]
name = "sourced"
description = "Claude Code framework for academic papers"
requires-python = ">=3.10"
dynamic = ["version"]
dependencies = []  # keep empty; add rich only if we commit to colored output

[project.scripts]
sourced = "sourced.cli:main"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/sourced/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/sourced"]
# Note: no force-include needed because templates live under src/sourced/data/
```

`__init__.py`:
```python
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("sourced")
except PackageNotFoundError:  # editable/uninstalled fallback
    from ._version import __version__
```

## 4. Command surface

### 4.1 Global flags (apply to all subcommands)

| Flag | Effect |
|---|---|
| `-h`, `--help` | argparse-generated help for root or current subcommand |
| `--version` | `sourced <version> (git <sha>)` |
| `-v`, `--verbose` | `action='count'` — `-v` = progress, `-vv` = diffs + tracebacks |
| `-q`, `--quiet` | Suppress success output only; errors always surface; wins over `-v` if both |
| `--color=auto\|always\|never` | Color control; `--no-color` is alias for `--color=never` |
| `--dry-run` | Show what would change without mutating; validators still run; no-op on `check` |
| `--strict` | Promote `severity="warning"` findings to errors (exit 4 per §5.8) |

Color suppression precedence: `--color=always` > `NO_COLOR` env > `--color=never` / `--no-color` > non-tty > default on. Stderr follows the same rules independently of stdout.

### 4.2 `sourced install` — per-project install

```
sourced install [--project <path>]
                [--voice <name>]      # default: academic
                [--style <name>]      # default: apa7
                [--type <kind>]       # essay (default) | annotated-bib
                [--brief <name>]      # also create <name>.brief.md
                [--force]             # overwrite existing files
```

Replaces `./install.sh --brief X --voice Y --style Z`. No `--update` flag — use `sourced update`. Errors if files exist without `--force`.

### 4.3 `sourced global-install` — refresh `~/.claude/`

```
sourced global-install [--force]      # overwrite custom files in ~/.claude/voice/ etc.
```

Skips prereq check (same carve-out as `install.sh --global-only`). Prompts for user name on first run; persists to `~/.claude/sourced.config`.

### 4.4 `sourced new <project-name>` — create project + brief (sugar)

```
sourced new <project-name>            # positional, required
           [--voice <name>]
           [--style <name>]
           [--type <kind>]
           [--brief <alt-name>]       # override brief filename (default: <project-name>)
           [--force]
```

Creates `./<project-name>/` directory, runs `sourced install --brief <project-name>` there.

### 4.5 `sourced update` — refresh managed block

```
sourced update [--project <path>]
               [--force]              # replace entire CLAUDE.md, not just managed block
```

No `--voice` / `--style` flags — use `sourced switch` for those.

### 4.6 `sourced switch voice <name>` / `sourced switch style <name>`

```
sourced switch voice <name>           # positional, required
              [--project <path>]

sourced switch style <name>           # positional, required
              [--project <path>]
```

Errors with `ProjectError` (exit 5; see §5.8 table) if no marker found in `voice.md` / `style.md`. Recovery hint: `sourced install --force --voice <name>`.

### 4.7 `sourced check` — diagnose prereqs and `~/.claude/` health

```
sourced check [--project <path>]      # also check a specific project
```

Default verbosity inverted: per-check detail only on **failures**, one-line summary per section on **passes** (matches `brew doctor`). `-v` shows full per-check detail for passes too. `-q` shows only the exit code. Exit 0 if all pass, **exit 4 if any check fails** (matches `ValidationError` code per §5.8 — `check` aggregates across multiple validators, so a unified code is cleaner than mapping to whichever typed error fired first).

Phase-1 checks performed (one-line surface):
- Prereqs: `pdftotext`, `pdfinfo`, `pdftoppm`, `pandoc` (≥ 3.1), `python3` on PATH.
- `~/.claude/` is writable; expected dirs present.
- Iron-rule integrity across every voice in `~/.claude/voice/`.
- §10 exemption syntax valid across every voice.
- CSL title match for every shipped style.
- If `--project` given: CLAUDE.md sentinels well-formed; voice.md / style.md markers resolve.
- One-line warning if `CONDA_PREFIX` was active during pipx install (full conda-env diagnostics: phase 2 `doctor`).
- One-line warning if multiple `sourced` on PATH (full PATH/duplicate diagnostics: phase 2 `doctor`).

Boundary with phase-2 `sourced doctor`: `check` ships one-line surface warnings for these conditions; `doctor` (phase 2) is the interactive deeper-diagnostics command with remediation walkthroughs, orphan-file detection, and structured reports. Phase 1 `check` is meant for CI / scripting; phase 2 `doctor` is meant for an interactive user troubleshooting a broken setup.

### 4.8 install.sh flag → new surface

| install.sh today | sourced equivalent |
|---|---|
| `./install.sh` | `sourced install` |
| `./install.sh --global-only` | `sourced global-install` |
| `./install.sh --brief X --voice Y` | `sourced install --brief X --voice Y` (or `sourced new X --voice Y`) |
| `./install.sh --force` | `sourced install --force` |
| `./install.sh --update` | `sourced update` |
| `./install.sh --update --voice new` | `sourced switch voice new` |
| `./install.sh --force --voice new` | `sourced install --force --voice new` |
| `./install.sh --project ~/p --brief paper` | `sourced install --project ~/p --brief paper` |

## 5. Template bundling and rendering pipeline

### 5.1 Resource access

```python
# src/sourced/render.py
from importlib.resources import files, as_file
from functools import cache

@cache
def _data_root():
    return files("sourced") / "data"

def read_template(subpath: str) -> str:
    return (_data_root() / subpath).read_text(encoding="utf-8")

def bundled_path(subpath: str):
    """Context manager yielding a real filesystem Path. For shutil.copytree."""
    return as_file(_data_root() / subpath)
```

`@cache` avoids recomputing the `Traversable` per call. `as_file()` is a context manager so the code stays portable to future zipped-distribution cases (Go-binary-with-embedded-archive).

`tests/conftest.py` overrides `_data_root` via `monkeypatch.setattr` to point at the in-tree `src/sourced/data/` during tests, so parity tests don't silently read the installed wheel.

### 5.2 Render is pure string-manipulation

```python
@dataclass(frozen=True)
class RenderContext:
    user: str
    voice_name: str | None
    style_name: str | None

def render(template: str, ctx: RenderContext) -> str:
    """Pure function — no I/O, no side effects.
    Substitutions: {{USER}} → ctx.user; {{VOICE}} → ctx.voice_name (if non-None);
    {{STYLE}} → ctx.style_name (if non-None). Unknown tokens kept verbatim."""
```

No I/O inside `render()`. Trivially unit-testable.

### 5.3 Pipeline composition

Each `commands/*.py` runs the pipeline linearly:

```
1. config.load_user_name()                          → str
2. read_template(subpath)                           → str
2.5. validators.validate_template(template)         → list[Finding]   (PRE-render)
                                                    # delegates to validators.csl.validate_csl_title
                                                    # (template-static; placeholder + sentinel checks
                                                    # are also handled here in phase 2 if added)
3. render(template, ctx)                            → str
4. validators.validate_rendered(rendered)           → list[Finding]   (POST-render)
                                                    # delegates to validators.iron_rules.* +
                                                    # validators.exemptions.*; checks rendered prose
5. if findings (severity="error"): raise ValidationError(msg, findings)  (see §5.8 for shape)
   if findings (severity="warning") and ctx.strict: raise ValidationError(msg, findings)
6. if ctx.dry_run: print diff vs existing file, return
7. write_atomic(output_path, rendered)
   OR  mirror_tree(subpath, dest, dry_run=ctx.dry_run)
```

Pre-render vs post-render split: catches malformed placeholders (e.g., `{{USERR}}` typo) and template-static invariants before substitution silently leaves them as literal text. Post-render catches content invariants in the final output.

**Where the warning→error promotion lives:** step 5, in the pipeline orchestrator. NOT in validators (per §3 boundary principle 3 — validators always return `list[Finding]` and never raise). The pipeline is the single place that consults `ctx.strict` and decides whether warnings become errors.

**Validator → step mapping:**
- `validators.csl.validate_csl_title` → step 2.5 (PRE-render): static template fact.
- `validators.iron_rules.validate` → step 4 (POST-render): checks the rendered voice file.
- `validators.exemptions.validate` → step 4 (POST-render): checks rendered §10 exemption block.

**Pure-function discipline at each effect boundary:** `render()` (§5.2), `mirror_tree()` (§5.4), and `write_atomic()` (§5.6) all accept primitive args (str, Path, bool) — not `Context`. Only the orchestrating `_pipeline.py` and the `commands/*.py` see `Context`; they unpack `ctx.dry_run` etc. and pass primitives down. Keeps the effect functions trivially testable and Context-agnostic.

### 5.4 Mirror trees

```python
# src/sourced/mirror.py
import shutil
from .render import bundled_path

def mirror_tree(subpath: str, dest: Path, dry_run: bool = False) -> None:
    with bundled_path(subpath) as src:
        if dry_run:
            # Walk src and print what would copy; no writes.
            return
        shutil.copytree(src, dest, dirs_exist_ok=True,
                        copy_function=shutil.copy2, symlinks=True)
```

`symlinks=True` future-proofs against bundled symlinks (none today; locks the contract). `copy2` preserves mtimes so `npm install` doesn't re-run unnecessarily under mirrored skill dirs. `dirs_exist_ok=True` matches install.sh's "no-delete, overwrite-per-file" behavior.

Known limitation (documented, deferred to phase 2): mirror trees never delete stale files — if a skill or filter is removed from the bundle, stale files persist in `~/.claude/`. Same as install.sh today. Manifest-based cleanup is a phase-2 task, connected to issues.md #14.

### 5.5 Marker lines on rendered output

`voice.md` and `style.md` carry `<!-- sourced: voice=<name> -->` / `<!-- sourced: style=<name> -->` markers on the first line. `project.py` parses these on `update` and `switch` to know the current library voice/style.

`CLAUDE.md` carries `<!-- sourced:begin managed -->` / `<!-- sourced:end managed -->` sentinels around the managed block. **Strict regex (F28 fix from cycle 3):**

```python
BEGIN_RE = re.compile(r"^<!-- sourced:begin managed -->$", re.MULTILINE)
END_RE   = re.compile(r"^<!-- sourced:end managed -->$",   re.MULTILINE)
```

Column-0, exact form, no whitespace tolerance. Sentinels are machine-written and always at column 0; tolerance only admits prose-documentation false positives. Documented limitation: a sentinel inside a fenced ```` ``` ```` code block would still match (regex doesn't know about fences). `sourced check` warns on suspicious sentinel placements (more than one pair, mid-file).

### 5.6 Atomic writes

```python
def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent,
        prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
```

Avoids stale-tmpfile collisions after a crash (each run picks a unique name). Skip explicit `fsync` — overkill for config files. Windows: `path.replace()` fails if target is open in another process; surface as a clear `PermissionError` not raw stack trace.

### 5.7 Migration-day `.sourced.bak` fallback

On first phase-1 run against an existing project, write a `<file>.sourced.bak` sibling alongside any file before `write_atomic` replaces it. `sourced check` warns about leftover `*.sourced.bak` files. Bounded-cost rollback in case of sentinel-regex bugs. Auto-cleared after the second successful run on the same project. (The `.sourced.bak` suffix — not bare `.bak` — is explicit so it doesn't collide with the user's own backup conventions.)

### 5.8 Error hierarchy

```python
# src/sourced/errors.py
class SourcedError(Exception):
    exit_code: int = 1

class UsageError(SourcedError):           exit_code = 2  # bad flag combination (matches argparse)
class PrereqError(SourcedError):          exit_code = 3
class ValidationError(SourcedError):
    exit_code = 4
    def __init__(self, msg: str, findings: list[Finding]) -> None:
        assert findings, "ValidationError requires at least one finding"
        super().__init__(msg)
        self.findings = findings
class ProjectError(SourcedError):         exit_code = 5
class RenderError(SourcedError):          exit_code = 6  # own code, not 1
class ExternalToolError(SourcedError):    exit_code = 7  # pandoc/git non-zero
class ValidatorCrashError(SourcedError):  exit_code = 70  # EX_SOFTWARE — distinguishable from project bugs
# 130 = KeyboardInterrupt (handled in cli.main)
```

`Finding` shared dataclass:
```python
from typing import Literal
@dataclass(frozen=True)
class Finding:
    rule: str
    location: str
    severity: Literal["error", "warning"]
    message: str
    fix_hint: str | None = None
    rule_url: str | None = None       # always None in phase 1; phase 2 wires up if/when
                                       # docs/rules/ ships with stable anchors
```

`Literal` prevents typo bugs (`severity="errror"` fails at type-check time, not runtime). `rule_url` is reserved future-state; phase 1 validators leave it as `None` and `ui.py` ignores it. Adding the field now (defaulted) avoids a frozen-dataclass retrofit later.

### 5.9 cli.main top-level

```python
def main():
    try:
        cli()  # argparse + dispatch
    except SourcedError as e:
        ui.print_error(e)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        if os.environ.get("SOURCED_DEBUG") or "-vv" in sys.argv or "--verbose" in sys.argv:
            raise  # re-raise for stack trace
        ui.print_unexpected(e)
        sys.exit(70)
```

Order matters: `KeyboardInterrupt` catch precedes `except Exception` or finally paths can swallow it. `SOURCED_DEBUG` env var lets contributors force tracebacks.

## 6. Error handling and UX

Covered above (§5.8, §5.9). Summary of the user-facing surface:

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Generic error (nothing else fit) |
| 2 | Usage error (argparse + manual `UsageError`) |
| 3 | Prereq missing |
| 4 | Validation failure |
| 5 | Project state broken |
| 6 | Render error |
| 7 | External tool failure |
| 70 | Validator crash / unexpected (EX_SOFTWARE) |
| 130 | SIGINT |

### Error message format

```
sourced: <short description>
    <remediation hint>

  # for ValidationError, findings inlined:
  missing from rendered voice.md at ~/.claude/voice/academic.md:
    - "No em dashes (—). Use parentheses, commas, or colons."
    - …
  remediation: re-run with --force, or edit src/sourced/data/templates/voices/academic.md and retry.
```

### Verbosity

| Level | Default | `-v` | `-vv` | `-q` |
|---|---|---|---|---|
| Per-subcommand summary | ✓ | ✓ | ✓ | — |
| Per-step progress | — | ✓ | ✓ | — |
| Per-file substitution diff | — | — | ✓ | — |
| Validator findings (failure only) | ✓ | ✓ | ✓ | ✓ |
| Stack trace on unexpected | — | — | ✓ | — |
| Errors on stderr | ✓ | ✓ | ✓ | ✓ |

### `sourced check` output

```
$ sourced check
Prerequisites:  4/5 passing
  ✗ pdftoppm (poppler-utils) — not on PATH
Global install: 27/27 passing

1 failed, 31 passed.
```

Default: per-check detail only on failures. `-v` shows all checks.

### `sourced install --dry-run` output

```
DRY RUN — no files will be written.

Would render CLAUDE.md from src/sourced/data/templates/CLAUDE.md (user=Hayden, voice=casual, style=apa7).
Would render voice.md from src/sourced/data/templates/voices/casual.md (iron-rule validation: pass).
…

3 files would be written to /home/hayden/writing/ (project).
13 files would be mirrored to ~/.claude/ (global).
1 file already exists and would be overwritten (use --force, or remove --dry-run).
```

Validators run during dry-run. Real exit codes on dry-run errors (not "would have failed"). Final summary line is greppable.

### `--strict` mode

Promotes `severity="warning"` findings to errors. Per-rule graduation is documented in each validator's docstring (e.g., "this rule is warning today; will be error in vNext"). Without `--strict`, "warnings will be errors in vNext" stays visible until vNext breaks users' CI.

## 7. Migration and install story

### 7.1 First-time install (end user)

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

### 7.2 Updates

```bash
pipx upgrade sourced
sourced global-install   # idempotent; refresh shipped files

cd ~/writing/my-paper
sourced update           # refresh managed block of CLAUDE.md
```

**Known pitfall:** `pipx upgrade` may silently no-op if `pyproject.toml`'s version doesn't bump (pip's resolver sees same version → already-satisfied). Mitigation: `hatch-vcs` derives version from git tag; the maintainer must tag releases. Reliable alternative: `pipx install --force 'git+https://...@main'`.

### 7.3 Version pinning / rollback

```bash
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@v0.3.0'
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@<sha>'
pipx install --force 'git+ssh://git@github.com/hayden1126/sourced.git@main'
```

For rollback testing where pip's wheel cache may serve stale: add `--pip-args="--no-cache-dir"`.

### 7.4 Uninstall

```bash
pipx uninstall sourced
# Manually remove ~/.claude/ if desired:
rm -rf ~/.claude/{agents,citations,templates,voice,style,skills,filters}
rm ~/.claude/sourced.config
# preserve ~/.claude/settings.json and any user-added directories
```

### 7.5 Contributor onboarding

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
pytest tests/cli/                          # unit + integration + parity (during dev) + golden
pytest tests/emitter/ tests/parity/        # existing; unchanged
bash tests/parity/run-all.sh               # 20 style × paste-target goldens
```

### 7.6 Migration day (maintainer checklist)

1. `pipx install --force git+ssh://git@github.com/hayden1126/sourced.git@main` — install the new CLI.
2. `sourced check` — verify prereqs + `~/.claude/` baseline; debug failures before any project work.
3. **For each active project, dry-run first:**
   ```bash
   cd <project>
   sourced update --dry-run    # surfaces sentinel-regex mismatches without mutation
   ```
   Watch for failures (the F28 fix's column-0 sentinel regex is stricter than install.sh's awk; see §5.5).
4. For each project that dry-runs cleanly: `sourced update` (no flag) to apply. Each first-touch writes a `<file>.sourced.bak` sibling (per §5.7) for rollback safety.
5. For any project that fails dry-run: inspect, decide whether to `sourced install --force` (recreate; user re-applies any unmanaged content) or hand-fix the sentinels. The `.sourced.bak` from a previous run on the same project (if any) is the rollback path.
6. `git tag legacy/install-sh-final HEAD~1` (the last commit before deletion) for one-week rollback availability. Reference in the README rollback note.
7. `git rm install.sh` in the phase-1 PR.
8. Update README + docs/INSTALL.md + ARCHITECTURE.md + ROADMAP.md (task #17). Specifically: README + INSTALL must call out the data-directory relocation (`templates/` etc. moved under `src/sourced/data/`) so contributors and anyone who maintained their own clone-of-sourced workflow knows the path changed.

### 7.7 pipx gotchas (documented)

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

## 8. Testing strategy

Four test categories under `tests/cli/`. Plus existing `tests/emitter/` and `tests/parity/` (unchanged).

### 8.1 Unit (`tests/cli/unit/`)

~25-35 tests, <2s runtime. Pure-function tests for render, validators, config, project, ui, errors.

### 8.2 Integration (`tests/cli/integration/`)

~15-20 tests, ~15s runtime. End-to-end subcommand invocations against `tmp_path` HOME + project. Uses `subprocess.run(["sourced", ...])` so the full argparse → cli → command path is exercised.

### 8.3 Parity (`tests/cli/parity/`) — development-only

For each flag combination, diffs `bash install.sh <flags>` output against `sourced <subcommand> <mapped-flags>` output. Allowed differences are named explicitly. **Deleted in the same PR that removes install.sh.** Purpose-limited to migration validation.

### 8.4 Golden (`tests/cli/golden/`)

Rendered-template snapshots for 15 variants (CLAUDE.md essay/annotated-bib, 6 voices, 5 styles, 2 brief templates). `syrupy` for snapshot management. Catches silent template drift; accepted intentionally via `--snapshot-update`.

### 8.5 Shared fixtures (`tests/conftest.py`)

```python
@pytest.fixture
def tmp_home(tmp_path, monkeypatch): ...      # redirect HOME
@pytest.fixture
def tmp_project(tmp_path): ...                # fresh project PWD
@pytest.fixture
def bundled_data_root(monkeypatch): ...       # point _data_root at in-tree templates
@pytest.fixture
def clean_ansi(monkeypatch): ...              # NO_COLOR=1 for deterministic stdout
```

### 8.6 CI

**Phase 1: none.** Manual pre-push:
```bash
pytest tests/                              # full suite
bash tests/parity/run-all.sh               # 20-golden style suite
sourced check                              # self-health check
```

**Phase 2:** GitHub Actions on push runs the same.

## 9. Drift-prevention during implementation

Four layers, cheapest first.

### 9.1 Test-gated

- Golden suite catches silent template drift.
- Parity suite catches behavioral drift from install.sh.
- After each meaningful commit during phase-1 dev, `/audit` on `git diff HEAD~1` to surface invariant drift inline.

### 9.2 Specialist agent dispatch

| Change type | Agent | Purpose |
|---|---|---|
| New `commands/*.py` or `validators/*.py` | `code-reviewer` | boundary principles + error model |
| Edit to `src/sourced/data/templates/*.md` | `prompt-engineer` | CLAUDE.md §4, §9, §10 conventions |
| Edit to `docs/*.md`, README, ARCHITECTURE, ROADMAP | `general-purpose` | doc-coherence + cross-links |
| New test file | none (inline) | pytest is the gate |
| Cross-cutting change | `general-purpose` | reviews full diff |

### 9.3 Invariant registry (`src/sourced/data/facts.yml`)

Phase 1 ships the registry file with the 8 invariants surfaced in cycle 3 (I1-I8) plus any new ones emerging from the port. Phase 2 adds `sourced check --invariants` to verify mirrors at runtime.

### 9.4 Docs-as-code tight loop

Every PR shipping a user-visible change ships doc updates in the same commit. Pre-push checklist:
- [ ] `pytest` passes
- [ ] `/audit` on the diff returns no new findings
- [ ] README / docs updated for any changed surface
- [ ] `facts.yml` updated if any mirrored fact changed

Manual in phase 1; git hook in phase 2.

## 10. Phase boundary

### 10.1 In phase 1

- Python package, all 11 install.sh functions ported, 6 subcommands.
- Templates relocated to `src/sourced/data/`.
- Tier 1 + Tier 2 UX improvements (exit codes, --help, --version, --color, --dry-run, --strict, -v/-q stackable, colorized output, --no-color, NO_COLOR respect, two-line stderr errors with remediation, pip-style graceful catch-all).
- Error hierarchy with 7 typed subclasses + `Finding` dataclass with `fix_hint` + `rule_url`.
- Pre-render + post-render validator split.
- Atomic writes via `tempfile.NamedTemporaryFile`.
- Strict column-0 sentinel regex (closes F28).
- Mirror via `shutil.copytree(symlinks=True, copy_function=copy2, dirs_exist_ok=True)`.
- Migration-day `.bak` fallback.
- Tests: unit + integration + parity (dev-only) + golden snapshots (15 variants).
- `install.sh` deleted; preserved at tag `legacy/install-sh-final`.
- Docs updated (README, INSTALL, ARCHITECTURE, ROADMAP).
- `facts.yml` invariant registry seeded.
- Drift-prevention: golden tests, parity tests, per-commit audit, agent dispatch map, pre-push checklist.
- Post-merge `/audit` + `/audit-fix` (task #16).

### 10.2 Out of phase 1 (Tier 3 → phase 2)

- `~/.config/sourced/config.toml` user defaults migration.
- Shell completion (bash/zsh/fish).
- `--format=json` structured output for `check` and others.
- `sourced doctor` deeper diagnostics.
- `sourced check --invariants` runtime verification.
- GitHub Actions CI.
- Manifest-based orphan cleanup (closes issues.md #14).

### 10.3 Out of phase 1 (Tier 4 explicit exclusions)

- No new modes.
- No new validators beyond install.sh's set.
- No `~/.claude/` layout changes.
- No schema or mode-definition changes.
- No template content edits.

### 10.4 Phase 2 sizing

| PR | Scope | Sizing |
|---|---|---|
| A | GitHub Actions CI + `sourced check --invariants` + facts.yml runtime wiring | S |
| B | `sourced doctor` + `--format=json` + shell completion | M |
| C | Manifest-based orphan cleanup + user-defaults config migration | M |

Each independently mergeable. Probably one week of intermittent work after phase 1 settles.

### 10.5 Phase 1 effort estimate

5-8 days focused work:

| Area | Days |
|---|---|
| Scaffolding + pyproject + first subcommand | 1 |
| Render + mirror + all validators (with unit tests) | 2 |
| Commands with integration tests | 2 |
| Parity suite vs install.sh | 1 |
| Golden snapshots + 15 fixtures | 0.5 |
| Docs + README updates | 0.5 |
| Drift-prevention seed (facts.yml, pre-push checklist doc) | 0.5 |
| Buffer (reviewer-flagged issues, migration-day dry-runs) | 1-2 |

Writing-plans skill produces the phased implementation plan with checkpoints.

## 11. ROADMAP updates

Replace the current entry at `ROADMAP.md` L218-221:

```
### Installable `sourced` executable on `$PATH`
**Priority:** later · **Effort:** S · **Status:** open.
Ship a user-facing executable...
```

With two entries:

```
### Python CLI (`sourced`) — install.sh decomposition
**Priority:** next · **Effort:** L · **Status:** in progress (phase 1 started 2026-04-21).

Phase 1: Python package at `src/sourced/`, pipx-installed from private git URL.
Ports all install.sh responsibilities. Replaces install.sh entirely. Six
subcommands (install, global-install, new, update, switch, check). Tier 1 +
Tier 2 UX improvements.

Design spec: `docs/superpowers/specs/2026-04-21-sourced-cli-decomposition-design.md`.

Phase 2 (follow-on): GitHub Actions CI, `sourced check --invariants` wiring
facts.yml into runtime verification, `sourced doctor` deeper diagnostics
(conda poisoning, PATH duplicates, orphan file detection per issues.md #14),
`--format=json` structured output, shell completion (bash/zsh/fish),
user-defaults config migration from `~/.claude/sourced.config` to
`~/.config/sourced/config.toml`.

### Single-binary distribution (Go or Rust)
**Priority:** later · **Effort:** L · **Status:** open. Depends on Python CLI phase 1+2.

Rewrite the Python CLI as a statically-linked single binary (Go or Rust, pick
per migration-time language maturity). Distribute via GitHub releases +
Homebrew formula + `curl | sh` installer. Eliminates pipx + Python 3 as a user
prereq — for non-dev writers who stumble on Python tooling, reduces install
to a single shell command. Behavior-identical to Python CLI; just a
distribution upgrade. Migration: ship Go binary alongside pipx for one release
cycle, then document the binary as the primary path.
```

Cross-references:
- `issues.md` #14 (orphan cleanup): add line — "Phase 2 of the Python CLI provides the implementation surface; promote when CLI phase 1 ships."
- `audit_deferred.md` T2 (duplication-without-include): revisit after phase 1; the `src/sourced/data/` relocation may collapse some of Cluster A/B's duplication.

## 12. Implementation note

This design is intentionally complete enough to hand off to `superpowers:writing-plans`, which will produce the phase-1 implementation plan with PR checkpoints, gated handoffs, and per-task verification criteria. The plan will reference this spec as the canonical source for architecture, command surface, error contract, test categories, and migration discipline.

---

## Appendix A — Reviewer synthesis log

Eight specialist agents reviewed sections 1, 3, 4, 5 in two-agent parallel rounds:

- **Section 1** (architecture): packaging-expert + code-reviewer → 5 design changes (config split, Finding dataclass, three-layer error contract, Context object, shared install pipeline).
- **Section 3** (pipeline): Python-idioms + pipeline+migration → 8 refinements (atomic-write tempfile pattern, sentinel column-0 strictness, pre-render+post-render split, migration-day .bak, symlinks=True, validator severity Literal, fenced-code-block gotcha, KeyboardInterrupt order).
- **Section 4** (error/UX): UX-conventions + error-handling → 13 refinements (`--color=auto|always|never`, `-v` stackable, `-q` semantics, default check verbosity inverted, ExternalToolError, exit 6 for RenderError, exit 70 for ValidatorCrashError, `--strict`, fix_hint+rule_url fields, ValidationError invariant, UsageError vs ProjectError principle, pip-style graceful catch-all, --format=json deferred).
- **Section 5** (install/migration): pipx-reality + contributor-onboarding → 1 big finding (force-include not editable-install-compatible → relocate templates to `src/sourced/data/`) + 11 refinements (pipx upgrade no-op pitfall, ssh-keyscan pre-seed, HTTPS as default for non-devs, `pipx install --force -e .` recovery recipe, dry-run gate before migration, install.sh kept at legacy tag, conda env warning, read-only `~/.claude/` preflight, shell-restart-after-ensurepath, port-22-blocked workaround, pip cache purge for rollback testing).

A full-design coherence review will follow this spec write-up before user review.
