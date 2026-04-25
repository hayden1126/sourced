"""Structural invariants I1-I10 over the bundled template + shipped mode bodies.

Invariants are defined in the phase-2 design spec §8 (`docs/superpowers/specs/
2026-04-23-claude-md-manifest-extraction-design.md`). Each invariant function
returns list[Finding]; callers decide how to surface.

Scope: I1 + I3-I9 shipped in commit 3. I2 activated in commit 4 (overlay scope).
I10 (cache-discipline auditing) activated in this follow-up via AST inspection
of `_pipeline.render_claude_md` and the cache-discipline primitives in §5.
"""
from __future__ import annotations
import ast
import inspect
import re
from pathlib import Path

from ..errors import ProjectError
from ..project import parse_user_additions
from ..render import bundled_path, read_template
from . import Finding


# Per spec §13.1: rigid modes require an Iron Law section.
RIGID_MODES = frozenset({"finetuning", "research", "formatting"})

# Per spec I2: overlays may patch only sections defined in the base manifest.
# Allowed `## Patches to ...` headings reference the base §§7.1–7.6.
ALLOWED_OVERLAY_PATCH_SECTIONS = frozenset({
    "7.1 Mode registry",
    "7.2 Explicit triggers",
    "7.3 Implicit and auto-fire triggers",
    "7.4 Mode-to-mode gates",
    "7.5 Forcing artifacts",
    "7.6 Precedence and canonical §10 IDs",
})

OVERLAY_PATCH_HEADING_RE = re.compile(r"^## Patches to §(.+?)\s*$", re.MULTILINE)

# Per spec §13.1: every non-inline mode body carries these sections in order.
REQUIRED_SECTIONS = (
    "Overview",
    "When to Use",
    "Steps",
    "Red Flags",
    "Rationalizations",
    "Exit Gates",
)

# Per spec I9: root CLAUDE.md §7 manifest block must not exceed this.
MAX_MANIFEST_LINES = 200

# Per spec I9 (mirrors Claude Code MEMORY.md entry-length convention).
MAX_REGISTRY_ENTRY_CHARS = 150

SECTION_HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
SUBSECTION_HEADING_RE = re.compile(r"^### (.+?)\s*$", re.MULTILINE)
MODE_HEADER_RE = re.compile(r"^#\s+\[(.+?)\s+mode\]\s*$", re.MULTILINE)
CANONICAL_ID_BULLET_RE = re.compile(
    r"^-\s+`([a-z][a-z0-9-]*)`\s*[—-]",
    re.MULTILINE,
)
NEVER_LIST_ID_TAG_RE = re.compile(r"\[id:\s*([a-z][a-z0-9-]*)\s*\]")


# ----- manifest parsing -----

def _load_bundled_template() -> str:
    """Return the bundled CLAUDE.md template text."""
    return read_template("templates/CLAUDE.md")


def _load_mode_body(name: str) -> str | None:
    """Return the bundled mode body text, or None if absent."""
    try:
        return read_template(f"templates/docs/modes/{name}.md")
    except FileNotFoundError:
        return None


def _slice_section(text: str, heading: str) -> tuple[str, int, int] | None:
    """Return (section_text, start_line_1based, end_line_1based) for the §{heading}
    block in text. Uses `^## ` boundaries.

    Returns None if heading not found. `section_text` INCLUDES the heading line.
    """
    lines = text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        m = SECTION_HEADING_RE.match(line)
        if m and m.group(1).strip() == heading:
            start_idx = i
            break
    if start_idx is None:
        return None
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if SECTION_HEADING_RE.match(lines[j]):
            end_idx = j
            break
    return "\n".join(lines[start_idx:end_idx]), start_idx + 1, end_idx


def _slice_subsection(text: str, heading: str) -> str | None:
    """Return the `### {heading}` block text (including the heading line), or
    None if absent. Uses `^### ` boundaries."""
    lines = text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        m = SUBSECTION_HEADING_RE.match(line)
        if m and m.group(1).strip() == heading:
            start_idx = i
            break
    if start_idx is None:
        return None
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if SUBSECTION_HEADING_RE.match(lines[j]) or SECTION_HEADING_RE.match(lines[j]):
            end_idx = j
            break
    return "\n".join(lines[start_idx:end_idx])


def _parse_markdown_table(block: str) -> list[dict[str, str]]:
    """Parse a GitHub-flavored markdown table. Returns list of {header: cell}.

    Expects the first `|...|` line to be the header, the second to be the
    separator (`|---|---|`), and subsequent lines to be data rows. Non-table
    lines are skipped.
    """
    rows = []
    header: list[str] | None = None
    for line in block.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(set(c) <= {"-", ":"} for c in cells) and cells:
            continue  # separator row
        if header is None:
            header = cells
            continue
        if len(cells) != len(header):
            continue  # malformed row; skip silently
        rows.append(dict(zip(header, cells)))
    return rows


def parse_registry(claude_md: str) -> list[dict[str, str]]:
    """Parse the `### 7.1 Mode registry` table into rows. Returns empty list
    if the subsection is missing or contains no table."""
    sub = _slice_subsection(claude_md, "7.1 Mode registry")
    if sub is None:
        return []
    return _parse_markdown_table(sub)


def parse_gate_table(claude_md: str) -> list[dict[str, str]]:
    """Parse the `### 7.4 Mode-to-mode gates` table."""
    sub = _slice_subsection(claude_md, "7.4 Mode-to-mode gates")
    if sub is None:
        return []
    return _parse_markdown_table(sub)


def parse_forcing_artifacts(claude_md: str) -> list[str]:
    """Parse §7.5 forcing-artifact names from the bulleted list.

    Artifact names are the bolded phrases at bullet starts, e.g.
    `- **§4 audit list.** One row per citation audited...` yields "§4 audit list".
    """
    sub = _slice_subsection(claude_md, "7.5 Forcing artifacts")
    if sub is None:
        return []
    names = []
    for line in sub.split("\n"):
        m = re.match(r"^\s*-\s+\*\*(.+?)\.\*\*", line)
        if m:
            names.append(m.group(1).strip())
    return names


def parse_precedence_rules(claude_md: str) -> list[tuple[int, str]]:
    """Parse §7.6 precedence as an ordered list. Returns [(rank, heading)].

    Expects numbered-list entries `N. **heading.** body...` per spec §8 I7.
    """
    sub = _slice_subsection(claude_md, "7.6 Precedence and canonical §10 IDs")
    if sub is None:
        return []
    rules = []
    for line in sub.split("\n"):
        m = re.match(r"^\s*(\d+)\.\s+\*\*(.+?)\.\*\*", line)
        if m:
            rules.append((int(m.group(1)), m.group(2).strip()))
    return rules


def parse_canonical_ids(claude_md: str) -> list[str]:
    """Parse §7.6 canonical §10 IDs from the bulleted list."""
    sub = _slice_subsection(claude_md, "7.6 Precedence and canonical §10 IDs")
    if sub is None:
        return []
    return [m.group(1) for m in CANONICAL_ID_BULLET_RE.finditer(sub)]


# ----- I1 mode body presence -----

def check_i1_mode_body_presence(claude_md: str) -> list[Finding]:
    """Every mode in §7.1 registry whose `Body` is not `inline` has a matching
    docs/modes/<name>.md in the bundled template."""
    findings: list[Finding] = []
    for row in parse_registry(claude_md):
        mode = row.get("Mode", "").strip()
        body = row.get("Body", "").strip()
        if not mode:
            continue
        if "inline" in body.lower():
            continue
        body_path = re.match(r"`?docs/modes/([a-z0-9-]+)\.md`?", body)
        if not body_path:
            findings.append(Finding(
                rule="I1",
                location=f"registry row {mode!r}",
                severity="error",
                message=f"Body column {body!r} is not 'inline' and does not match 'docs/modes/<name>.md'.",
            ))
            continue
        name = body_path.group(1)
        if _load_mode_body(name) is None:
            findings.append(Finding(
                rule="I1",
                location=f"registry row {mode!r}",
                severity="error",
                message=f"mode body file `templates/docs/modes/{name}.md` is missing from the bundle.",
                fix_hint=f"create `src/sourced/data/templates/docs/modes/{name}.md` or remove the row from §7.1.",
            ))
    return findings


# ----- I2 overlay scope -----

def _bundled_overlay_files() -> list[tuple[str, str]]:
    """Return [(filename, text)] for every bundled CLAUDE.d/*.md overlay,
    excluding README.md (which is documentation, not a patch file).

    Returns an empty list if the bundle carries no CLAUDE.d/ tree.
    """
    try:
        with bundled_path("templates/CLAUDE.d") as src:
            src_path = Path(src)
            if not src_path.exists():
                return []
            return [
                (f.name, f.read_text(encoding="utf-8"))
                for f in sorted(src_path.glob("*.md"))
                if f.name != "README.md"
            ]
    except (FileNotFoundError, ModuleNotFoundError):
        return []


def check_i2_overlay_scope(claude_md: str) -> list[Finding]:
    """Every shipped overlay under CLAUDE.d/ patches only sections defined in
    the base manifest (§§7.1–7.6). Overlays that introduce new patch headings
    fail.

    Dormant when the bundle carries no overlays — phase-2 commit 4 is the
    first commit shipping any overlay (annotated-bib).
    """
    findings: list[Finding] = []
    for filename, text in _bundled_overlay_files():
        for m in OVERLAY_PATCH_HEADING_RE.finditer(text):
            section = m.group(1).strip()
            if section not in ALLOWED_OVERLAY_PATCH_SECTIONS:
                findings.append(Finding(
                    rule="I2",
                    location=f"CLAUDE.d/{filename}",
                    severity="error",
                    message=(
                        f"overlay patches §{section!r}, which is not a "
                        f"base-manifest section (allowed: {sorted(ALLOWED_OVERLAY_PATCH_SECTIONS)})."
                    ),
                    fix_hint="patch only §7.1–7.6 headings; new categories require a base-manifest change first.",
                ))
    return findings


# ----- I3 canonical ID integrity -----

def check_i3_canonical_id_integrity(claude_md: str) -> list[Finding]:
    """Every canonical §10 ID in §7.6 appears in `docs/modes/writing.md §Never-list`
    as `[id: <x>]`, and vice versa. Shipped voice library `## §10 exemptions`
    bullets resolve to canonical IDs."""
    findings: list[Finding] = []
    canonical = set(parse_canonical_ids(claude_md))

    writing_md = _load_mode_body("writing")
    if writing_md is None:
        findings.append(Finding(
            rule="I3",
            location="templates/docs/modes/writing.md",
            severity="error",
            message="writing.md is missing; cannot verify canonical §10 ID round-trip.",
        ))
        return findings

    never_list = _slice_section(writing_md, "Never-list")
    if never_list is None:
        findings.append(Finding(
            rule="I3",
            location="writing.md",
            severity="error",
            message="writing.md has no `## Never-list` section; editing.md pass 6 reference would break.",
        ))
        return findings
    never_ids = set(NEVER_LIST_ID_TAG_RE.findall(never_list[0]))

    for mid in sorted(canonical - never_ids):
        findings.append(Finding(
            rule="I3",
            location=f"§7.6 canonical ID {mid!r}",
            severity="error",
            message=f"canonical ID {mid!r} declared in manifest §7.6 but not tagged in writing.md §Never-list.",
            fix_hint=f"add an entry ending with `[id: {mid}]` under writing.md §Never-list.",
        ))
    for nid in sorted(never_ids - canonical):
        findings.append(Finding(
            rule="I3",
            location=f"writing.md §Never-list [id: {nid}]",
            severity="error",
            message=f"writing.md tags ID {nid!r} but manifest §7.6 does not list it as canonical.",
            fix_hint=f"add {nid!r} to §7.6 canonical ID list or drop the [id:] tag.",
        ))

    # Shipped voice library exemptions resolve to canonical IDs.
    try:
        with bundled_path("templates/voices") as voices_src:
            voices_path = Path(voices_src)
            for voice_file in voices_path.glob("*.md"):
                voice_text = voice_file.read_text(encoding="utf-8")
                exemptions_section = _slice_section(voice_text, "§10 exemptions")
                if exemptions_section is None:
                    continue
                for line in exemptions_section[0].split("\n"):
                    m = re.match(r"^\s*-\s+([a-z][a-z0-9-]*)\s*[:—-]", line)
                    if not m:
                        continue
                    vid = m.group(1)
                    if vid not in canonical:
                        findings.append(Finding(
                            rule="I3",
                            location=f"voices/{voice_file.name} §10 exemptions",
                            severity="error",
                            message=f"exemption bullet names {vid!r}, not in §7.6 canonical IDs.",
                            fix_hint="use a canonical ID or remove the bullet.",
                        ))
    except FileNotFoundError:
        pass

    return findings


# ----- I4 manifest syntactic validity -----

def check_i4_manifest_syntax(claude_md: str) -> list[Finding]:
    """§7.1 registry, §7.4 gate table, §7.5 forcing-artifact list all parse."""
    findings: list[Finding] = []

    registry = parse_registry(claude_md)
    if not registry:
        findings.append(Finding(
            rule="I4",
            location="§7.1 Mode registry",
            severity="error",
            message="§7.1 registry is empty or unparseable as a markdown table.",
        ))
    else:
        required_cols = {"Mode", "Body", "Project types", "Auto-enters from"}
        missing = required_cols - set(registry[0].keys())
        if missing:
            findings.append(Finding(
                rule="I4",
                location="§7.1 Mode registry",
                severity="error",
                message=f"registry header missing required columns: {sorted(missing)}.",
            ))

    gates = parse_gate_table(claude_md)
    if not gates:
        findings.append(Finding(
            rule="I4",
            location="§7.4 Mode-to-mode gates",
            severity="error",
            message="§7.4 gate table is empty or unparseable.",
        ))
    else:
        required_cols = {"Transition", "Gate condition", "Forcing artifact"}
        missing = required_cols - set(gates[0].keys())
        if missing:
            findings.append(Finding(
                rule="I4",
                location="§7.4 gate table",
                severity="error",
                message=f"gate table header missing required columns: {sorted(missing)}.",
            ))

    artifacts = parse_forcing_artifacts(claude_md)
    if not artifacts:
        findings.append(Finding(
            rule="I4",
            location="§7.5 Forcing artifacts",
            severity="error",
            message="§7.5 forcing-artifact list is empty or unparseable.",
        ))

    return findings


# ----- I5 forcing-artifact reachability -----

def check_i5_forcing_artifact_reachability(claude_md: str) -> list[Finding]:
    """Every forcing artifact named in §7.5 is referenced somewhere in the
    dispatch surface: in a mode body OR in root CLAUDE.md outside §7.5 itself.

    Some artifacts (e.g. Scope-delta list emitted by §6 scope-growth soft-stop)
    originate in root-level rules, not mode-specific procedures; the spec §3.5
    attributes emission to those root rules directly, so mode-body-only
    reachability would be over-strict.
    """
    findings: list[Finding] = []
    artifacts = parse_forcing_artifacts(claude_md)
    if not artifacts:
        return findings

    mode_bodies: dict[str, str] = {}
    for row in parse_registry(claude_md):
        body = row.get("Body", "").strip()
        m = re.match(r"`?docs/modes/([a-z0-9-]+)\.md`?", body)
        if not m:
            continue
        text = _load_mode_body(m.group(1))
        if text is not None:
            mode_bodies[m.group(1)] = text

    # Reachability haystack: every mode body + root CLAUDE.md with §7.5 excised
    # (so the artifact's own declaration doesn't count as a reference to itself).
    haystacks = list(mode_bodies.values())
    s75 = _slice_subsection(claude_md, "7.5 Forcing artifacts")
    if s75 is not None:
        haystacks.append(claude_md.replace(s75, ""))
    else:
        haystacks.append(claude_md)

    for artifact in artifacts:
        needle = artifact.lower()
        if any(needle in h.lower() for h in haystacks):
            continue
        findings.append(Finding(
            rule="I5",
            location=f"§7.5 artifact {artifact!r}",
            severity="error",
            message=f"forcing artifact {artifact!r} is not referenced in any mode body or root rule.",
            fix_hint="add a reference in the emitting mode body / root rule, or remove the artifact from §7.5.",
        ))
    return findings


# ----- I6 user-addition marker integrity -----

def check_i6_user_addition_markers(claude_md: str) -> list[Finding]:
    """User-addition markers in the bundled template parse cleanly."""
    findings: list[Finding] = []
    try:
        parse_user_additions(claude_md)
    except ProjectError as e:
        findings.append(Finding(
            rule="I6",
            location="templates/CLAUDE.md",
            severity="error",
            message=str(e),
        ))
    return findings


# ----- I7 precedence ordering -----

def check_i7_precedence_ordering(claude_md: str) -> list[Finding]:
    """§7.6 precedence is an ordered list, each rule is positionally unique."""
    findings: list[Finding] = []
    rules = parse_precedence_rules(claude_md)
    if not rules:
        findings.append(Finding(
            rule="I7",
            location="§7.6 Precedence",
            severity="error",
            message="§7.6 precedence has no parseable numbered rules.",
        ))
        return findings
    ranks = [r for r, _ in rules]
    if ranks != sorted(ranks):
        findings.append(Finding(
            rule="I7",
            location="§7.6 Precedence",
            severity="error",
            message=f"precedence ranks are not in ascending order: {ranks}.",
        ))
    if len(set(ranks)) != len(ranks):
        findings.append(Finding(
            rule="I7",
            location="§7.6 Precedence",
            severity="error",
            message=f"precedence ranks have duplicates: {ranks}. Rank IS precedence; ties forbidden.",
        ))
    return findings


# ----- I8 mode body template compliance -----

def check_i8_mode_body_compliance(claude_md: str) -> list[Finding]:
    """Every non-inline mode body has required sections per spec §13.1.
    Rigid modes additionally carry Iron Law."""
    findings: list[Finding] = []
    for row in parse_registry(claude_md):
        mode = row.get("Mode", "").strip()
        body = row.get("Body", "").strip()
        if "inline" in body.lower() or not mode:
            continue
        m = re.match(r"`?docs/modes/([a-z0-9-]+)\.md`?", body)
        if not m:
            continue
        name = m.group(1)
        text = _load_mode_body(name)
        if text is None:
            continue  # I1 reports the missing file
        headings = [m2.group(1).strip() for m2 in SECTION_HEADING_RE.finditer(text)]
        header_line = MODE_HEADER_RE.search(text)
        if header_line is None:
            findings.append(Finding(
                rule="I8",
                location=f"docs/modes/{name}.md",
                severity="error",
                message="missing `# [<mode> mode]` top header.",
            ))
        for required in REQUIRED_SECTIONS:
            if required not in headings:
                findings.append(Finding(
                    rule="I8",
                    location=f"docs/modes/{name}.md",
                    severity="error",
                    message=f"missing required section `## {required}`.",
                    fix_hint=f"add `## {required}` per spec §13.1.",
                ))
        if name in RIGID_MODES and "Iron Law" not in headings:
            findings.append(Finding(
                rule="I8",
                location=f"docs/modes/{name}.md",
                severity="error",
                message=f"rigid mode {name!r} missing required `## Iron Law` section per spec §13.1.",
            ))
    return findings


# ----- I9 dispatch-block size limits -----

def check_i9_size_limits(claude_md: str) -> list[Finding]:
    """Root §7 block ≤ MAX_MANIFEST_LINES; each §7.1 registry row ≤ MAX_REGISTRY_ENTRY_CHARS."""
    findings: list[Finding] = []

    lines = claude_md.split("\n")
    s7_start = None
    s8_start = None
    for i, line in enumerate(lines):
        if SECTION_HEADING_RE.match(line) and line.strip() == "## 7. Modes (dispatch manifest)":
            s7_start = i
        elif s7_start is not None and SECTION_HEADING_RE.match(line):
            s8_start = i
            break
    if s7_start is None:
        findings.append(Finding(
            rule="I9",
            location="CLAUDE.md",
            severity="error",
            message="could not locate §7 manifest block by its canonical heading.",
        ))
    else:
        size = (s8_start if s8_start is not None else len(lines)) - s7_start
        if size > MAX_MANIFEST_LINES:
            findings.append(Finding(
                rule="I9",
                location=f"§7 manifest block (lines {s7_start + 1}-{(s8_start or len(lines))})",
                severity="error",
                message=f"manifest block is {size} lines; exceeds limit of {MAX_MANIFEST_LINES}.",
                fix_hint="move content into a mode body or compress the block.",
            ))

    for row in parse_registry(claude_md):
        serialized = " | ".join(f"{k}: {v}" for k, v in row.items())
        if len(serialized) > MAX_REGISTRY_ENTRY_CHARS:
            mode = row.get("Mode", "<?>")
            findings.append(Finding(
                rule="I9",
                location=f"§7.1 registry row {mode!r}",
                severity="error",
                message=f"registry row is {len(serialized)} chars; exceeds {MAX_REGISTRY_ENTRY_CHARS}.",
            ))
    return findings


# ----- I10 cache-discipline auditing -----

# Names of the cache primitives in `_pipeline.py`. Calls to these are auditable
# at the AST level; calls to anything else that returns always-on content
# are bare-string assembly.
CACHE_PRIMITIVES = frozenset({"cache_stable_section", "uncached_section"})


def check_i10_cache_discipline(claude_md: str) -> list[Finding]:
    """Verify `_pipeline.render_claude_md` routes through the cache-discipline
    primitives:

      (a) The function body uses `cache_stable_section(...)` or
          `uncached_section(..., reason=...)` for every value-producing
          expression that contributes to the return.
      (b) Every `uncached_section(...)` call carries a `reason=` kwarg whose
          value is a non-empty string literal at static analysis time.

    The check inspects the function's source via `ast`. Bare-string assembly
    (string concatenation, f-strings, format() calls) at the return path
    fails with a finding citing the line.
    """
    findings: list[Finding] = []
    try:
        from ..commands import _pipeline
    except ImportError as e:
        findings.append(Finding(
            rule="I10",
            location="_pipeline import",
            severity="error",
            message=f"could not import _pipeline for AST inspection: {e}",
        ))
        return findings

    try:
        source = inspect.getsource(_pipeline.render_claude_md)
    except OSError as e:
        findings.append(Finding(
            rule="I10",
            location="_pipeline.render_claude_md",
            severity="error",
            message=f"could not read source: {e}",
        ))
        return findings

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        findings.append(Finding(
            rule="I10",
            location="_pipeline.render_claude_md",
            severity="error",
            message=f"AST parse failed: {e}",
        ))
        return findings

    # Find the function definition (single top-level def in the slice).
    func_def = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "render_claude_md":
            func_def = node
            break
    if func_def is None:
        findings.append(Finding(
            rule="I10",
            location="_pipeline.render_claude_md",
            severity="error",
            message="render_claude_md not found at AST top level.",
        ))
        return findings

    # Walk the body for return-producing expressions and uncached_section calls.
    return_nodes: list[ast.Return] = []
    uncached_calls: list[ast.Call] = []
    cache_primitive_calls: list[ast.Call] = []

    for node in ast.walk(func_def):
        if isinstance(node, ast.Return):
            return_nodes.append(node)
        elif isinstance(node, ast.Call):
            fn_name = _call_name(node)
            if fn_name == "uncached_section":
                uncached_calls.append(node)
                cache_primitive_calls.append(node)
            elif fn_name == "cache_stable_section":
                cache_primitive_calls.append(node)

    # (a) Each return must originate from a cache-primitive call.
    if not return_nodes:
        findings.append(Finding(
            rule="I10",
            location="_pipeline.render_claude_md",
            severity="error",
            message="function has no return statement.",
        ))
    for ret in return_nodes:
        if ret.value is None:
            continue
        if not _is_cache_primitive_expr(ret.value):
            findings.append(Finding(
                rule="I10",
                location=f"_pipeline.render_claude_md (return at line {ret.lineno})",
                severity="error",
                message=(
                    "return value is not a cache-primitive call. Always-on "
                    "content must route through cache_stable_section() or "
                    "uncached_section(..., reason=...)."
                ),
                fix_hint="wrap the return expression in cache_stable_section('<name>', lambda: ...).",
            ))

    # (b) Every uncached_section call carries a non-empty `reason` kwarg.
    for call in uncached_calls:
        reason_kw = next((kw for kw in call.keywords if kw.arg == "reason"), None)
        if reason_kw is None:
            findings.append(Finding(
                rule="I10",
                location=f"_pipeline.render_claude_md (line {call.lineno})",
                severity="error",
                message="uncached_section() call missing required `reason=` kwarg.",
            ))
            continue
        if not isinstance(reason_kw.value, ast.Constant) or not isinstance(reason_kw.value.value, str):
            findings.append(Finding(
                rule="I10",
                location=f"_pipeline.render_claude_md (line {call.lineno})",
                severity="error",
                message="uncached_section(..., reason=...) value must be a string literal at static analysis time.",
            ))
            continue
        if not reason_kw.value.value.strip():
            findings.append(Finding(
                rule="I10",
                location=f"_pipeline.render_claude_md (line {call.lineno})",
                severity="error",
                message="uncached_section(..., reason=...) literal is empty or whitespace-only.",
            ))

    return findings


def _call_name(node: ast.Call) -> str | None:
    """Return the simple name of the called function, or None if not a Name/Attribute."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_cache_primitive_expr(expr: ast.AST) -> bool:
    """An expression is cache-primitive-rooted iff it is itself a
    cache_stable_section / uncached_section call. We do not unwrap conditional
    expressions or subscripts — the contract is "the return value is the
    primitive's return," not "somewhere a primitive is called."""
    if isinstance(expr, ast.Call):
        return _call_name(expr) in CACHE_PRIMITIVES
    return False


# ----- I11 no flat-path references -----

# Paths to scan, grouped by bundled subpath key. Globs are relative to
# the subpath root (e.g. "templates" resolves to src/sourced/data/templates/).
I11_SCAN_TARGETS: dict[str, tuple[str, ...]] = {
    "templates": (
        "CLAUDE.md",
        "docs/modes/*.md",
        "docs/voice-extractor.md",
        "brief.template.md",
        "brief.template.annotated-bib.md",
    ),
    "agents": ("*.md",),
    "citations": ("schema.md",),
}

# Each tuple is (regex_pattern, rule_label, fix_hint).
# Patterns use negative lookbehind to allow the correctly-prefixed form.
FLAT_PATH_RULES: tuple[tuple[str, str, str], ...] = (
    (r"(?<!/)\bvoice\.md\b", "flat voice.md reference", "prefix with `config/`"),
    (r"(?<!/)\bstyle\.md\b", "flat style.md reference", "prefix with `config/`"),
    (r"(?<!sources/)<draft[^>]*>\.citations\.json", "flat <draft>.citations.json reference", "prefix with `sources/`"),
    (r"(?<!config/)<(?:draft|name)[^>]*>\.brief\.md", "flat <draft>.brief.md reference", "prefix with `config/`"),
    (r"\.claude/briefs/working\.brief\.md", "obsolete .claude/briefs/ ref", "rewrite to `config/working.brief.md`"),
    (r"\.claude/citations/working\.citations\.json", "obsolete .claude/citations/ main-log ref", "rewrite to `sources/working.citations.json`"),
)

# Substrings that mark a line as exempt from I11 scanning.
I11_LINE_ALLOWLIST_SUBSTRINGS: tuple[str, ...] = (
    "<!-- sourced:voice=",
    "<!-- sourced:style=",
    "phase-3 layout",
    "phase-4 migration",
)


def _i11_line_exempt(line: str) -> bool:
    """Return True if the line is exempt from I11 flat-path scanning."""
    s = line.lstrip()
    # File-tree diagram lines (box-drawing characters used by `tree`).
    if s.startswith("├──") or s.startswith("│") or s.startswith("└──"):
        return True
    return any(marker in line for marker in I11_LINE_ALLOWLIST_SUBSTRINGS)


def check_i11_no_flat_paths(claude_md: str) -> list[Finding]:
    """Scan bundled templates for flat-path references that phase-4 migrated.

    Globs over templates/**/*.md, agents/*.md, and citations/schema.md.
    Lines matching FLAT_PATH_RULES emit an error finding, unless the line
    is exempted by _i11_line_exempt().
    """
    import re as _re

    findings: list[Finding] = []
    for subpath, globs in I11_SCAN_TARGETS.items():
        try:
            with bundled_path(subpath) as base:
                base_path = Path(base)
                for glob in globs:
                    for target in base_path.glob(glob):
                        if not target.is_file():
                            continue
                        rel = Path(subpath) / target.relative_to(base_path)
                        for lineno, line in enumerate(
                            target.read_text(encoding="utf-8").splitlines(), 1
                        ):
                            if _i11_line_exempt(line):
                                continue
                            for regex, rule_label, fix in FLAT_PATH_RULES:
                                if _re.search(regex, line):
                                    findings.append(Finding(
                                        rule="I11",
                                        location=f"{rel}:{lineno}",
                                        severity="error",
                                        message=f"{rule_label}: {line.strip()[:100]}",
                                        fix_hint=fix,
                                    ))
        except (FileNotFoundError, ModuleNotFoundError):
            continue
    return findings


# ----- Aggregator -----

INVARIANT_CHECKERS = [
    ("I1", check_i1_mode_body_presence),
    ("I2", check_i2_overlay_scope),
    ("I3", check_i3_canonical_id_integrity),
    ("I4", check_i4_manifest_syntax),
    ("I5", check_i5_forcing_artifact_reachability),
    ("I6", check_i6_user_addition_markers),
    ("I7", check_i7_precedence_ordering),
    ("I8", check_i8_mode_body_compliance),
    ("I9", check_i9_size_limits),
    ("I10", check_i10_cache_discipline),
    ("I11", check_i11_no_flat_paths),
]


def run_all_invariants() -> list[tuple[str, list[Finding]]]:
    """Run every shipped invariant check. Returns [(rule_id, findings)]."""
    claude_md = _load_bundled_template()
    return [(rule_id, checker(claude_md)) for rule_id, checker in INVARIANT_CHECKERS]
