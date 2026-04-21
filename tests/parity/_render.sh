#!/usr/bin/env bash
# Shared parity render for sourced style harness.
#
# Usage: _render.sh <style-dir> <target-name> <output-ext> [extra pandoc args...]
#
# Reads:  <style-dir>/fixture.pandoc.md
#         <style-dir>/fixture.bib.json
# Writes: <style-dir>/actual/<target-name>.<output-ext>
# Diffs:  against <style-dir>/golden/<target-name>.<output-ext>
# Exits:  0 on match, 1 on diff; emits "[<style>] <target-name> OK|FAIL"
#
# The CSL file is auto-discovered from templates/styles/<style-name>/*.csl.
#
# For the `latex` target, the helper extracts the body between \begin{document}
# and \end{document} from pandoc's standalone render before diffing, so that
# preamble edits do not cascade into golden diffs. See spec §5.2.

set -euo pipefail

# Tempfiles created by this run get cleaned up on any exit path (success or
# set-e abort). Keeps BSD/GNU sed tempfile plumbing from leaking artifacts
# into tests/parity/<style>/actual/ on failed runs.
__tmpfiles=()
trap 'rm -f "${__tmpfiles[@]:+${__tmpfiles[@]}}"' EXIT

if [[ $# -lt 3 ]]; then
  echo "Usage: _render.sh <style-dir> <target-name> <output-ext> [extra pandoc args...]" >&2
  exit 2
fi

STYLE_DIR="$1"
TARGET="$2"
OUTPUT_EXT="$3"
shift 3
EXTRA_FLAGS=("$@")

STYLE_NAME="$(basename "${STYLE_DIR}")"
REPO_DIR="$(cd "${STYLE_DIR}/../../.." && pwd)"

CSL_FILES=("${REPO_DIR}/templates/styles/${STYLE_NAME}"/*.csl)
if [[ ! -f "${CSL_FILES[0]}" ]]; then
  echo "[${STYLE_NAME}] ${TARGET} SKIP (no CSL found in templates/styles/${STYLE_NAME}/)" >&2
  exit 2
fi
if (( ${#CSL_FILES[@]} > 1 )); then
  echo "[${STYLE_NAME}] ${TARGET} FAIL (multiple CSL files in templates/styles/${STYLE_NAME}/; expected exactly one)" >&2
  exit 2
fi
CSL_FILE="${CSL_FILES[0]}"

mkdir -p "${STYLE_DIR}/actual"

ACTUAL="${STYLE_DIR}/actual/${TARGET}.${OUTPUT_EXT}"
GOLDEN="${STYLE_DIR}/golden/${TARGET}.${OUTPUT_EXT}"

if [[ "${TARGET}" == "latex" ]]; then
  TEMPLATE="${REPO_DIR}/templates/styles/${STYLE_NAME}/template.tex"
  if [[ ! -f "${TEMPLATE}" ]]; then
    echo "[${STYLE_NAME}] latex SKIP (no template.tex in templates/styles/${STYLE_NAME}/)" >&2
    exit 2
  fi
  RAW="${ACTUAL}.full"
  pandoc --citeproc \
    --bibliography="${STYLE_DIR}/fixture.bib.json" \
    --csl="${CSL_FILE}" \
    --standalone --template="${TEMPLATE}" \
    "${EXTRA_FLAGS[@]}" \
    -o "${RAW}" \
    "${STYLE_DIR}/fixture.pandoc.md"
  awk '/\\begin\{document\}/,/\\end\{document\}/' "${RAW}" \
    | sed '1d;$d' > "${ACTUAL}"
else
  # Smart-quote Lua filter for markdown paste targets. Filter preserves ASCII
  # apostrophes inside italic spans (linguistic glottal-stop notation) so the
  # `-smart` pandoc writer extension doesn't curl them. See
  # templates/filters/smart-quotes.lua for the filter and each style.md's
  # `### google-docs` / `### plain-markdown` lua-filter: bullet for declaration.
  LUA_FILTER_FLAGS=()
  case "${TARGET}" in
    google-docs|plain-markdown)
      LUA_FILTER_FLAGS+=("--lua-filter=${REPO_DIR}/templates/filters/smart-quotes.lua")
      ;;
  esac

  pandoc --citeproc \
    --bibliography="${STYLE_DIR}/fixture.bib.json" \
    --csl="${CSL_FILE}" \
    "${LUA_FILTER_FLAGS[@]}" \
    "${EXTRA_FLAGS[@]}" \
    -o "${ACTUAL}" \
    "${STYLE_DIR}/fixture.pandoc.md"

  # Post-pandoc strip for markdown paste targets. Pandoc's markdown-citations
  # writer wraps each citeproc-rendered References entry in ::: fenced-div
  # syntax, which most destinations (Google Docs' "Paste as markdown",
  # Obsidian, Notion, GitHub render, Reddit) paste as literal text. Stripping
  # the ::: lines keeps italics and links in the bibliography entries while
  # producing clean markdown. The -header_attributes pandoc extension (passed
  # via run.sh) handles the heading-attribute counterpart
  # (`# References {#references .unnumbered}`). The pattern matches only
  # pandoc's emitted forms (`::: {...}` open, `:::` close) to avoid clobbering
  # user-authored `:::` strings that might slip into source prose.
  # word and latex targets don't need this — pandoc's docx/latex writers
  # consume divs internally.
  case "${TARGET}" in
    google-docs|plain-markdown)
      __tmp=$(mktemp "${ACTUAL}.XXXXXX")
      __tmpfiles+=("${__tmp}")
      sed -e '/^::: /d' -e '/^:::$/d' "${ACTUAL}" > "${__tmp}"
      mv "${__tmp}" "${ACTUAL}"
      ;;
  esac
fi

if ! diff -u "${GOLDEN}" "${ACTUAL}"; then
  echo "[${STYLE_NAME}] ${TARGET} FAIL"
  exit 1
fi

echo "[${STYLE_NAME}] ${TARGET} OK"
