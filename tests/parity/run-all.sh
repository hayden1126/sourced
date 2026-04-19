#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=0
for style_dir in "${SCRIPT_DIR}"/*/; do
  style=$(basename "${style_dir}")
  [[ -f "${style_dir}/run.sh" ]] || continue
  echo "=== ${style} ==="
  if ! (cd "${style_dir}" && ./run.sh); then
    failures=$((failures + 1))
  fi
done

if [[ ${failures} -gt 0 ]]; then
  echo ""
  echo "${failures} style(s) failed parity."
  exit 1
fi

echo ""
echo "All styles passed parity."
