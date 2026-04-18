#!/usr/bin/env bash
#
# Sourced — install agents and schema into ~/.claude/
#
# Substitutes {{USER}} in template files with the name saved in
# ~/.claude/sourced.config. On first run, prompts for the name.
# On subsequent runs (after `git pull`), re-renders with saved name.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${HOME}/.claude/sourced.config"
CLAUDE_AGENTS_DIR="${HOME}/.claude/agents"
CLAUDE_CITATIONS_DIR="${HOME}/.claude/citations"

# Ensure ~/.claude/ exists
mkdir -p "${HOME}/.claude"

# Load or prompt for user name
if [[ -f "${CONFIG_FILE}" ]]; then
    # shellcheck source=/dev/null
    source "${CONFIG_FILE}"
    echo "Loaded config from ${CONFIG_FILE} (USER=${SOURCED_USER})"
else
    echo "First-time setup."
    read -rp "Your name (used inside agent instructions, e.g. 'Hayden' or 'Alice'): " SOURCED_USER
    if [[ -z "${SOURCED_USER}" ]]; then
        echo "Error: name cannot be empty." >&2
        exit 1
    fi
    printf 'SOURCED_USER=%q\n' "${SOURCED_USER}" > "${CONFIG_FILE}"
    echo "Saved to ${CONFIG_FILE}"
fi

# Create target directories
mkdir -p "${CLAUDE_AGENTS_DIR}"
mkdir -p "${CLAUDE_CITATIONS_DIR}"

# Escape user name for safe use in sed replacement
ESCAPED_USER=$(printf '%s\n' "${SOURCED_USER}" | sed 's/[&/\]/\\&/g')

render_and_install() {
    local src="$1"
    local dest="$2"
    sed "s/{{USER}}/${ESCAPED_USER}/g" "${src}" > "${dest}"
    echo "  installed ${dest}"
}

echo "Rendering templates..."
render_and_install "${REPO_DIR}/agents/academic-researcher.md" "${CLAUDE_AGENTS_DIR}/academic-researcher.md"
render_and_install "${REPO_DIR}/agents/source-finder.md" "${CLAUDE_AGENTS_DIR}/source-finder.md"
render_and_install "${REPO_DIR}/citations/schema.md" "${CLAUDE_CITATIONS_DIR}/schema.md"

echo ""
echo "Sourced installed."
echo "  Agents:  ${CLAUDE_AGENTS_DIR}/"
echo "  Schema:  ${CLAUDE_CITATIONS_DIR}/schema.md"
echo ""
echo "To update after 'git pull', re-run: ./install.sh"
echo "To change your name, edit or delete ${CONFIG_FILE} and re-run."
