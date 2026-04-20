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
CSL_FILE="${CSL_FILES[0]}"
if [[ ! -f "${CSL_FILE}" ]]; then
  echo "[${STYLE_NAME}] ${TARGET} SKIP (no CSL found in templates/styles/${STYLE_NAME}/)" >&2
  exit 2
fi

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
  pandoc --citeproc \
    --bibliography="${STYLE_DIR}/fixture.bib.json" \
    --csl="${CSL_FILE}" \
    "${EXTRA_FLAGS[@]}" \
    -o "${ACTUAL}" \
    "${STYLE_DIR}/fixture.pandoc.md"
fi

if ! diff -u "${GOLDEN}" "${ACTUAL}"; then
  echo "[${STYLE_NAME}] ${TARGET} FAIL"
  exit 1
fi

echo "[${STYLE_NAME}] ${TARGET} OK"
