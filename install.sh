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

# ---- flag parsing ----------------------------------------------------------
GLOBAL_ONLY=0
FORCE=0
UPDATE=0
BRIEF_NAME=""
TARGET_DIR="${PWD}"

usage() {
  cat <<EOF
Usage: install.sh [options]

Options:
  --global-only        Install/refresh only global files (source-finder + schema).
                       Skip per-project CLAUDE.md.
  --project <path>     Drop CLAUDE.md into <path> instead of the current directory.
  --force              Overwrite existing CLAUDE.md (and brief, if --brief is used)
                       without asking.
  --update             Refresh the managed block of an existing CLAUDE.md in place,
                       preserving content outside the sentinels.
  --brief <name>       Also drop <name>.brief.md into the project directory,
                       rendered from templates/brief.template.md.
  -h, --help           Show this message.
EOF
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
    --project)
      TARGET_DIR="${2:-}"
      [[ -z "${TARGET_DIR}" ]] && { echo "--project needs a path" >&2; exit 1; }
      shift 2
      ;;
    -h|--help)     usage; exit 0 ;;
    *)             echo "unknown flag: $1" >&2; usage; exit 1 ;;
  esac
done

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
mkdir -p "${CLAUDE_AGENTS_DIR}" "${CLAUDE_CITATIONS_DIR}"
echo "Rendering global files..."
render "${REPO_DIR}/agents/source-finder.md" "${CLAUDE_AGENTS_DIR}/source-finder.md"
render "${REPO_DIR}/citations/schema.md"     "${CLAUDE_CITATIONS_DIR}/schema.md"

# Clean up legacy academic-researcher.md from prior installs. Academic-researcher
# now lives in per-project CLAUDE.md, not as a subagent.
if [[ -f "${CLAUDE_AGENTS_DIR}/academic-researcher.md" ]]; then
  rm -f "${CLAUDE_AGENTS_DIR}/academic-researcher.md"
  echo "  removed legacy ${CLAUDE_AGENTS_DIR}/academic-researcher.md"
fi

if [[ ${GLOBAL_ONLY} -eq 1 ]]; then
  echo ""
  echo "Global install done. Skipping per-project CLAUDE.md (--global-only)."
  exit 0
fi

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

# ---- step 3: optional brief ------------------------------------------------
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
