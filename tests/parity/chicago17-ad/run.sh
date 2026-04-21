#!/usr/bin/env bash
# Parity runner for the chicago17-ad style. Delegates to ../_render.sh.
#
# -t markdown-citations forces citeproc to render citations into the markdown
# writer's output. Plain -t markdown round-trips the [@id] syntax unchanged
# and drops the bibliography body, which would make this harness trivially-
# passing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDER="${SCRIPT_DIR}/../_render.sh"

failures=0

if ! "${RENDER}" "${SCRIPT_DIR}" plain-markdown md --wrap=preserve -t markdown-citations-header_attributes-smart; then
  failures=$((failures + 1))
fi

if ! "${RENDER}" "${SCRIPT_DIR}" google-docs md --wrap=none -t markdown-citations-header_attributes-smart; then
  failures=$((failures + 1))
fi

if ! "${RENDER}" "${SCRIPT_DIR}" word docx.md -t markdown-citations; then
  failures=$((failures + 1))
fi

if ! "${RENDER}" "${SCRIPT_DIR}" latex tex -t latex; then
  failures=$((failures + 1))
fi

exit ${failures}
