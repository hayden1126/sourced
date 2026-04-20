#!/usr/bin/env bash
set -euo pipefail

# Note: -t markdown-citations forces citeproc to render citations into the
# markdown writer's output. Plain -t markdown round-trips the [@id] syntax
# unchanged and drops the bibliography body, which would make this harness
# trivially-passing. See run.sh comment in the design doc for the flag choice.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CSL_FILE="${REPO_DIR}/templates/styles/apa7/apa.csl"
STYLE_NAME="apa7"

mkdir -p "${SCRIPT_DIR}/actual"
failures=0

# plain-markdown
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  --wrap=preserve \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/plain-markdown.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/plain-markdown.md" "${SCRIPT_DIR}/actual/plain-markdown.md"; then
  echo "[${STYLE_NAME}] plain-markdown FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] plain-markdown OK"
fi

# google-docs
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  --wrap=none \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/google-docs.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/google-docs.md" "${SCRIPT_DIR}/actual/google-docs.md"; then
  echo "[${STYLE_NAME}] google-docs FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] google-docs OK"
fi

# word (intermediate markdown)
pandoc --citeproc \
  --bibliography="${SCRIPT_DIR}/fixture.bib.json" \
  --csl="${CSL_FILE}" \
  -t markdown-citations \
  -o "${SCRIPT_DIR}/actual/word.docx.md" \
  "${SCRIPT_DIR}/fixture.pandoc.md"

if ! diff -u "${SCRIPT_DIR}/golden/word.docx.md" "${SCRIPT_DIR}/actual/word.docx.md"; then
  echo "[${STYLE_NAME}] word.docx.md FAIL"
  failures=$((failures + 1))
else
  echo "[${STYLE_NAME}] word.docx.md OK"
fi

exit ${failures}
