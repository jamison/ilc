#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <walkthrough_path>"
  exit 2
fi

WALKTHROUGH_PATH="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

if [[ ! -f "${WALKTHROUGH_PATH}" ]]; then
  echo "Walkthrough not found: ${WALKTHROUGH_PATH}"
  exit 2
fi

TEMPLATE="${ROOT_DIR}/automation/templates/codex_review_prompt.md"
if [[ ! -f "${TEMPLATE}" ]]; then
  echo "Template not found: ${TEMPLATE}"
  exit 2
fi

PROMPT="$(TEMPLATE_ENV="${TEMPLATE}" WALKTHROUGH_PATH_ENV="${WALKTHROUGH_PATH}" python3 - <<'PY'
import os
from pathlib import Path
template = Path(os.environ["TEMPLATE_ENV"]).read_text(encoding="utf-8")
print(template.replace("{{WALKTHROUGH_PATH}}", os.environ["WALKTHROUGH_PATH_ENV"]))
PY
)"

codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  --cd "${ROOT_DIR}" \
  "${PROMPT}"
