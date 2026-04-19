#!/usr/bin/env bash
#
# sourced — install global agent files, and drop CLAUDE.md into the current
# project directory. Single entry point for first-time setup, updates, and
# per-project initialization.
#
# First run:   prompts for your name, installs global files, drops CLAUDE.md.
# Later runs:  skips the prompt, re-renders global files (idempotent), and
#              drops or updates CLAUDE.md in $PWD.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${HOME}/.claude/sourced.config"
CLAUDE_AGENTS_DIR="${HOME}/.claude/agents"
CLAUDE_CITATIONS_DIR="${HOME}/.claude/citations"
CLAUDE_TEMPLATES_DIR="${HOME}/.claude/templates"
CLAUDE_VOICE_DIR="${HOME}/.claude/voice"
CLAUDE_STYLE_DIR="${HOME}/.claude/style"

# ---- flag parsing ----------------------------------------------------------
GLOBAL_ONLY=0
FORCE=0
UPDATE=0
BRIEF_NAME=""
VOICE="academic"
VOICE_EXPLICIT=0
STYLE="apa7"
STYLE_EXPLICIT=0
TARGET_DIR="${PWD}"

usage() {
  cat <<EOF
Usage: install.sh [options]

Options:
  --global-only        Install/refresh only global files (source-finder,
                       voice-extractor, schema, brief template, voice library,
                       style library). Skip per-project files.
  --project <path>     Drop CLAUDE.md, voice.md, and style.md into <path>
                       instead of $PWD.
  --force              Overwrite existing CLAUDE.md, voice.md, style.md, and
                       brief (if --brief is used) without asking.
  --update             Refresh the managed block of an existing CLAUDE.md in place
                       (preserving content outside the sentinels) and refresh
                       voice.md and style.md from the project's installed voice
                       and style.
  --voice <name>       Pick the voice for this project (default: academic). The
                       choice is recorded inside voice.md; --update reuses it.
                       Shipped voices live in templates/voices/; custom voices
                       can be placed at ~/.claude/voice/<name>.md. Switching to
                       a different --voice on an existing project requires
                       --force or --update.
  --style <name>       Pick the citation/document style for this project
                       (default: apa7). The choice is recorded inside
                       style.md; --update reuses it. Shipped styles live in
                       templates/styles/; custom styles can be placed at
                       ~/.claude/style/<name>.md. Switching to a different
                       --style on an existing project requires --force or
                       --update.
  --brief <name>       Also drop <name>.brief.md into the project directory,
                       rendered from templates/brief.template.md.
  -h, --help           Show this message.
EOF
}

check_prerequisites() {
  # Tools required by the framework at runtime (not at install). pdftotext and
  # pdftoppm come from poppler-utils; Claude Code's built-in Read calls
  # pdftoppm for PDF rendering, and [research mode] reads PDFs via pdftotext.
  # pandoc 3.0+ with citeproc is required for the word/docx paste target and
  # for any future latex target.
  local missing=()
  command -v pdftotext >/dev/null 2>&1 || missing+=("poppler-utils (pdftotext, pdfinfo, pdftoppm)")
  command -v pandoc    >/dev/null 2>&1 || missing+=("pandoc (3.0+)")

  [[ ${#missing[@]} -eq 0 ]] && return 0

  echo "Missing prerequisites:" >&2
  for tool in "${missing[@]}"; do
    echo "  - ${tool}" >&2
  done
  echo "" >&2
  echo "Install on Debian/Ubuntu/WSL:" >&2
  echo "  sudo apt-get install -y poppler-utils pandoc" >&2
  echo "" >&2
  echo "Install on macOS:" >&2
  echo "  brew install poppler pandoc" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --global-only) GLOBAL_ONLY=1; shift ;;
    --force)       FORCE=1; shift ;;
    --update)      UPDATE=1; shift ;;
    --brief)
      BRIEF_NAME="${2:-}"
      [[ -z "${BRIEF_NAME}" ]] && { echo "--brief needs a name" >&2; exit 1; }
      shift 2
      ;;
    --voice)
      VOICE="${2:-}"
      [[ -z "${VOICE}" ]] && { echo "--voice needs a name" >&2; exit 1; }
      VOICE_EXPLICIT=1
      shift 2
      ;;
    --style)
      STYLE="${2:-}"
      [[ -z "${STYLE}" ]] && { echo "--style needs a name" >&2; exit 1; }
      STYLE_EXPLICIT=1
      shift 2
      ;;
    --project)
      TARGET_DIR="${2:-}"
      [[ -z "${TARGET_DIR}" ]] && { echo "--project needs a path" >&2; exit 1; }
      shift 2
      ;;
    -h|--help)     usage; exit 0 ;;
    *)             echo "unknown flag: $1" >&2; usage; exit 1 ;;
  esac
done

# ---- prerequisites check ---------------------------------------------------
check_prerequisites

# ---- repo-self-guard -------------------------------------------------------
if [[ ${GLOBAL_ONLY} -eq 0 ]]; then
  TARGET_ABS="$(cd "${TARGET_DIR}" 2>/dev/null && pwd || echo "${TARGET_DIR}")"
  if [[ "${TARGET_ABS}" == "${REPO_DIR}" && ${FORCE} -eq 0 ]]; then
    echo "Refusing to drop CLAUDE.md into the sourced repo itself (${REPO_DIR})." >&2
    echo "Run this from a writing project directory, or pass --force, or --global-only." >&2
    exit 1
  fi
fi

# ---- config (prompt on first run only) -------------------------------------
mkdir -p "${HOME}/.claude"
if [[ -f "${CONFIG_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${CONFIG_FILE}"
else
  echo "First-time setup."
  read -rp "Your name (used inside agent instructions, e.g. 'Hayden'): " SOURCED_USER
  if [[ -z "${SOURCED_USER}" ]]; then
    echo "Error: name cannot be empty." >&2
    exit 1
  fi
  printf 'SOURCED_USER=%q\n' "${SOURCED_USER}" > "${CONFIG_FILE}"
  echo "Saved ${CONFIG_FILE}"
fi

# Escape user name for sed replacement (handles &, /, \)
ESCAPED_USER=$(printf '%s\n' "${SOURCED_USER}" | sed 's/[&/\]/\\&/g')

render() {
  local src="$1" dest="$2"
  sed "s/{{USER}}/${ESCAPED_USER}/g" "${src}" > "${dest}"
  echo "  ${dest}"
}

# ---- step 1: global files (always) -----------------------------------------
mkdir -p "${CLAUDE_AGENTS_DIR}" "${CLAUDE_CITATIONS_DIR}" "${CLAUDE_TEMPLATES_DIR}" "${CLAUDE_VOICE_DIR}" "${CLAUDE_STYLE_DIR}"
echo "Rendering global files..."
render "${REPO_DIR}/agents/source-finder.md"     "${CLAUDE_AGENTS_DIR}/source-finder.md"
render "${REPO_DIR}/agents/voice-extractor.md"   "${CLAUDE_AGENTS_DIR}/voice-extractor.md"
render "${REPO_DIR}/citations/schema.md"         "${CLAUDE_CITATIONS_DIR}/schema.md"
render "${REPO_DIR}/templates/brief.template.md" "${CLAUDE_TEMPLATES_DIR}/brief.template.md"

# Voice library: copy each shipped voice to ~/.claude/voice/<name>.md verbatim
# (no {{USER}} substitution). Library files are treated as templates; the
# per-project step substitutes {{USER}} and prepends the voice marker when
# rendering into <project>/voice.md. Keeping the library unrendered means
# user-authored voices with {{USER}} tokens work the same way as shipped
# voices. User-authored voices at names that don't collide with shipped ones
# are left untouched.
for voice_file in "${REPO_DIR}"/templates/voices/*.md; do
  [[ -e "${voice_file}" ]] || continue
  voice_name=$(basename "${voice_file}" .md)
  cp "${voice_file}" "${CLAUDE_VOICE_DIR}/${voice_name}.md"
  echo "  ${CLAUDE_VOICE_DIR}/${voice_name}.md"
done

# Style library: copy each shipped style to ~/.claude/style/<name>.md verbatim
# (no {{USER}} substitution). Library files are templates; the per-project
# step substitutes {{USER}} and prepends the style marker when rendering into
# <project>/style.md. Same pattern as the voice library above.
for style_file in "${REPO_DIR}"/templates/styles/*.md; do
  [[ -e "${style_file}" ]] || continue
  style_name=$(basename "${style_file}" .md)
  cp "${style_file}" "${CLAUDE_STYLE_DIR}/${style_name}.md"
  echo "  ${CLAUDE_STYLE_DIR}/${style_name}.md"
done

# Per-style asset directories (CSL files, reference docx, etc.): mirror
# templates/styles/<name>/ into ~/.claude/style/<name>/. These are read by
# [formatting mode] when a paste target needs external assets (e.g., the
# word target invokes pandoc with --csl and --reference-doc). Assets are
# copied verbatim; they are not templates.
for style_assets in "${REPO_DIR}"/templates/styles/*/; do
  [[ -d "${style_assets}" ]] || continue
  style_name=$(basename "${style_assets}")
  mkdir -p "${CLAUDE_STYLE_DIR}/${style_name}"
  cp -R "${style_assets}." "${CLAUDE_STYLE_DIR}/${style_name}/"
  echo "  ${CLAUDE_STYLE_DIR}/${style_name}/ (assets)"
done

# Clean up legacy academic-researcher.md from prior installs. Academic-researcher
# now lives in per-project CLAUDE.md, not as a subagent.
if [[ -f "${CLAUDE_AGENTS_DIR}/academic-researcher.md" ]]; then
  rm -f "${CLAUDE_AGENTS_DIR}/academic-researcher.md"
  echo "  removed legacy ${CLAUDE_AGENTS_DIR}/academic-researcher.md"
fi

# Clean up legacy style.md from the previous voice install pattern (single
# active voice). Voice is now project-local; ~/.claude/voice/style.md is not
# read by the agent anymore.
if [[ -f "${CLAUDE_VOICE_DIR}/style.md" ]]; then
  rm -f "${CLAUDE_VOICE_DIR}/style.md"
  echo "  removed legacy ${CLAUDE_VOICE_DIR}/style.md"
fi

if [[ ${GLOBAL_ONLY} -eq 1 ]]; then
  echo ""
  echo "Global install done. Skipping per-project CLAUDE.md (--global-only)."
  exit 0
fi

# ---- voice preflight: resolve and validate before touching project files --
# Priority for which voice to use:
#   1. --voice <name> passed explicitly
#   2. marker in the project's existing voice.md
#   3. default ("academic")
DEST_VOICE="${TARGET_DIR}/voice.md"
MARKER_VOICE=""
if [[ -f "${DEST_VOICE}" ]]; then
  MARKER_VOICE=$(sed -n '1s/^<!-- sourced:voice=\([a-zA-Z0-9_-]*\) -->$/\1/p' "${DEST_VOICE}")
fi
if [[ ${VOICE_EXPLICIT} -eq 0 && -n "${MARKER_VOICE}" ]]; then
  VOICE="${MARKER_VOICE}"
fi

VOICE_SOURCE="${CLAUDE_VOICE_DIR}/${VOICE}.md"
if [[ ! -f "${VOICE_SOURCE}" ]]; then
  echo "Error: voice '${VOICE}' not found at ${VOICE_SOURCE}." >&2
  echo "Available voices in ${CLAUDE_VOICE_DIR}:" >&2
  for f in "${CLAUDE_VOICE_DIR}"/*.md; do
    [[ -e "$f" ]] && echo "  $(basename "$f" .md)" >&2
  done
  exit 1
fi

# ---- style preflight: resolve and validate before touching project files --
# Priority for which style to use:
#   1. --style <name> passed explicitly
#   2. marker in the project's existing style.md
#   3. default ("apa7")
DEST_STYLE="${TARGET_DIR}/style.md"
MARKER_STYLE=""
if [[ -f "${DEST_STYLE}" ]]; then
  MARKER_STYLE=$(sed -n '1s/^<!-- sourced:style=\([a-zA-Z0-9_-]*\) -->$/\1/p' "${DEST_STYLE}")
fi
if [[ ${STYLE_EXPLICIT} -eq 0 && -n "${MARKER_STYLE}" ]]; then
  STYLE="${MARKER_STYLE}"
fi

STYLE_SOURCE="${CLAUDE_STYLE_DIR}/${STYLE}.md"
if [[ ! -f "${STYLE_SOURCE}" ]]; then
  echo "Error: style '${STYLE}' not found at ${STYLE_SOURCE}." >&2
  echo "Available styles in ${CLAUDE_STYLE_DIR}:" >&2
  for f in "${CLAUDE_STYLE_DIR}"/*.md; do
    [[ -e "$f" ]] && echo "  $(basename "$f" .md)" >&2
  done
  exit 1
fi

# Extracts iron rules from a voice library file. Iron rules are rules that must
# pass through to every derived voice verbatim, regardless of corpus evidence.
# A rule is iron if either:
#   - it sits under a section heading "## Iron rules", "## AI-tells", or
#     "## Generation signatures" (until the next "## " heading), OR
#   - its line contains the literal token "[iron]".
# Prints each iron rule on its own line. Blank lines are filtered.
#
# Single-line assumption: each iron rule is expected to be a single line (a
# one-line paragraph or bullet). Multi-line iron rules would fragment into
# per-line pseudo-rules because normalize_rule operates per extracted line. If
# a future iron rule needs multi-line form, switch this to paragraph-mode awk
# (RS="") first.
extract_iron_rules() {
  local src="$1"
  {
    awk '
      /^## (Iron rules|AI-tells|Generation signatures)([[:space:]]|$)/ { in_iron = 1; next }
      /^## / && in_iron { in_iron = 0 }
      in_iron { print }
    ' "${src}"
    grep -F '[iron]' "${src}" || true
  } | grep -v '^[[:space:]]*$' || true
}

# Normalizes a rule string for substring matching: lowercase, collapse runs of
# whitespace to a single space, strip leading/trailing whitespace and trailing
# sentence-terminal punctuation.
normalize_rule() {
  echo "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr -s '[:space:]' ' ' \
    | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/[.!?]*$//'
}

# Validates that every iron rule from the skeleton voice library file appears
# (normalized-substring) in the candidate voice file about to be rendered.
# Arguments: candidate voice source path, skeleton voice path.
# Returns 0 if all iron rules are present (or the skeleton has none), 1 if any
# iron rule is missing. Prints missing rules to stderr on failure.
validate_iron_rules() {
  local voice_source="$1" skeleton_path="$2"
  [[ -f "${skeleton_path}" ]] || return 0
  # Canonicalize both paths so the self-validation short-circuit survives install
  # flow refactors (cp -l, mv, symlinks). -ef checked inode equality, which
  # depended on plain cp creating a fresh inode.
  if [[ "$(readlink -f "${voice_source}")" == "$(readlink -f "${skeleton_path}")" ]]; then
    return 0
  fi

  local iron_rules
  iron_rules=$(extract_iron_rules "${skeleton_path}")
  [[ -z "${iron_rules}" ]] && return 0

  local voice_normalized
  voice_normalized=$(tr '[:upper:]' '[:lower:]' < "${voice_source}" | tr -s '[:space:]' ' ')

  local missing=0
  while IFS= read -r rule; do
    [[ -z "${rule}" ]] && continue
    local normalized
    normalized=$(normalize_rule "${rule}")
    [[ -z "${normalized}" ]] && continue
    if [[ "${voice_normalized}" != *"${normalized}"* ]]; then
      if [[ ${missing} -eq 0 ]]; then
        echo "Error: iron rule(s) from ${skeleton_path} missing in ${voice_source}:" >&2
      fi
      echo "  - ${rule}" >&2
      missing=$((missing + 1))
    fi
  done <<< "${iron_rules}"

  if [[ ${missing} -gt 0 ]]; then
    echo "" >&2
    echo "Iron rules must appear verbatim in every derived voice library file." >&2
    echo "If voice-extractor dropped or reworded these rules, regenerate the voice with overwrite: true and re-run install." >&2
    return 1
  fi
  return 0
}

# Renders a voice library file to the project with the voice marker prepended.
# Runs iron-rule validation against the shipped academic skeleton first; aborts
# the install if any iron rule from the skeleton is missing in the candidate.
render_voice() {
  local src="$1" dest="$2" voice_name="$3"
  if ! validate_iron_rules "${src}" "${CLAUDE_VOICE_DIR}/academic.md"; then
    echo "Aborting install: voice '${voice_name}' failed iron-rule validation." >&2
    exit 1
  fi
  {
    echo "<!-- sourced:voice=${voice_name} -->"
    echo ""
    sed "s/{{USER}}/${ESCAPED_USER}/g" "${src}"
  } > "${dest}"
}

# Renders a style library file to the project with the style marker prepended.
render_style() {
  local src="$1" dest="$2" style_name="$3"
  {
    echo "<!-- sourced:style=${style_name} -->"
    echo ""
    sed "s/{{USER}}/${ESCAPED_USER}/g" "${src}"
  } > "${dest}"
}

# ---- step 2: per-project CLAUDE.md -----------------------------------------
DEST_CLAUDE="${TARGET_DIR}/CLAUDE.md"
TMP_RENDERED="$(mktemp)"
TMP_MANAGED="$(mktemp)"
TMP_NEW="$(mktemp)"
trap 'rm -f "${TMP_RENDERED}" "${TMP_MANAGED}" "${TMP_NEW}"' EXIT

sed "s/{{USER}}/${ESCAPED_USER}/g" "${REPO_DIR}/templates/CLAUDE.md" > "${TMP_RENDERED}"

echo "Rendering per-project CLAUDE.md..."

if [[ ! -f "${DEST_CLAUDE}" ]]; then
  cp "${TMP_RENDERED}" "${DEST_CLAUDE}"
  echo "  ${DEST_CLAUDE}"
elif [[ ${FORCE} -eq 1 ]]; then
  cp "${TMP_RENDERED}" "${DEST_CLAUDE}"
  echo "  ${DEST_CLAUDE} (overwrote with --force)"
elif [[ ${UPDATE} -eq 1 ]]; then
  if ! grep -q '<!-- sourced:begin managed -->' "${DEST_CLAUDE}"; then
    echo "Error: ${DEST_CLAUDE} has no <!-- sourced:begin managed --> sentinel." >&2
    echo "Cannot --update a CLAUDE.md that wasn't rendered by sourced. Use --force to overwrite." >&2
    exit 1
  fi

  if ! grep -q '<!-- sourced:end managed -->' "${DEST_CLAUDE}"; then
    echo "Error: ${DEST_CLAUDE} has a begin sentinel but no <!-- sourced:end managed --> sentinel." >&2
    echo "The awk splice would eat everything after the begin sentinel. Restore the end sentinel manually, or use --force to overwrite entirely." >&2
    exit 1
  fi

  # Extract the whole managed block (including sentinels) from the fresh render.
  awk '/<!-- sourced:begin managed -->/,/<!-- sourced:end managed -->/' "${TMP_RENDERED}" > "${TMP_MANAGED}"

  # Splice: keep everything outside the existing sentinels; replace everything
  # inside with the new managed block.
  awk -v managed_file="${TMP_MANAGED}" '
    /<!-- sourced:begin managed -->/ {
      while ((getline line < managed_file) > 0) print line
      close(managed_file)
      skip = 1
      next
    }
    /<!-- sourced:end managed -->/ {
      skip = 0
      next
    }
    !skip { print }
  ' "${DEST_CLAUDE}" > "${TMP_NEW}"

  cp "${TMP_NEW}" "${DEST_CLAUDE}"
  echo "  ${DEST_CLAUDE} (updated managed block)"
else
  echo "Error: ${DEST_CLAUDE} already exists." >&2
  echo "Use --update to refresh the managed block, or --force to overwrite entirely." >&2
  exit 1
fi

# ---- step 3: per-project voice ---------------------------------------------
# VOICE, VOICE_SOURCE, DEST_VOICE, MARKER_VOICE are set in the preflight above.
echo "Rendering per-project voice.md..."
if [[ ! -f "${DEST_VOICE}" ]]; then
  render_voice "${VOICE_SOURCE}" "${DEST_VOICE}" "${VOICE}"
  echo "  ${DEST_VOICE} (voice: ${VOICE})"
elif [[ ${FORCE} -eq 1 ]]; then
  render_voice "${VOICE_SOURCE}" "${DEST_VOICE}" "${VOICE}"
  echo "  ${DEST_VOICE} (overwrote with --force, voice: ${VOICE})"
elif [[ ${UPDATE} -eq 1 ]]; then
  render_voice "${VOICE_SOURCE}" "${DEST_VOICE}" "${VOICE}"
  echo "  ${DEST_VOICE} (refreshed via --update, voice: ${VOICE})"
elif [[ ${VOICE_EXPLICIT} -eq 1 && "${VOICE}" != "${MARKER_VOICE}" ]]; then
  echo "Error: ${DEST_VOICE} is installed with voice '${MARKER_VOICE:-unknown}'; refusing to silently switch to '${VOICE}'." >&2
  echo "Pass --force to replace, or --update to refresh with the new voice." >&2
  exit 1
else
  echo "  ${DEST_VOICE} already exists; skipping (pass --update to refresh, --force to replace)."
fi

# ---- step 4: per-project style ---------------------------------------------
# STYLE, STYLE_SOURCE, DEST_STYLE, MARKER_STYLE are set in the preflight above.
echo "Rendering per-project style.md..."
if [[ ! -f "${DEST_STYLE}" ]]; then
  render_style "${STYLE_SOURCE}" "${DEST_STYLE}" "${STYLE}"
  echo "  ${DEST_STYLE} (style: ${STYLE})"
elif [[ ${FORCE} -eq 1 ]]; then
  render_style "${STYLE_SOURCE}" "${DEST_STYLE}" "${STYLE}"
  echo "  ${DEST_STYLE} (overwrote with --force, style: ${STYLE})"
elif [[ ${UPDATE} -eq 1 ]]; then
  render_style "${STYLE_SOURCE}" "${DEST_STYLE}" "${STYLE}"
  echo "  ${DEST_STYLE} (refreshed via --update, style: ${STYLE})"
elif [[ ${STYLE_EXPLICIT} -eq 1 && "${STYLE}" != "${MARKER_STYLE}" ]]; then
  echo "Error: ${DEST_STYLE} is installed with style '${MARKER_STYLE:-unknown}'; refusing to silently switch to '${STYLE}'." >&2
  echo "Pass --force to replace, or --update to refresh with the new style." >&2
  exit 1
else
  echo "  ${DEST_STYLE} already exists; skipping (pass --update to refresh, --force to replace)."
fi

# ---- step 5: optional brief ------------------------------------------------
if [[ -n "${BRIEF_NAME}" ]]; then
  BRIEF_PATH="${TARGET_DIR}/${BRIEF_NAME}.brief.md"
  if [[ -f "${BRIEF_PATH}" && ${FORCE} -eq 0 ]]; then
    echo "  ${BRIEF_PATH} already exists; skipping (pass --force to overwrite)."
  else
    render "${REPO_DIR}/templates/brief.template.md" "${BRIEF_PATH}"
  fi
fi

echo ""
echo "Done."
