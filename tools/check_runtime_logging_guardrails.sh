#!/usr/bin/env bash
# check_runtime_logging_guardrails.sh
# Deterministic runtime logging guardrail gate.
#
# Usage:
#   ./tools/check_runtime_logging_guardrails.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_runtime_logging_guardrails.sh [--dry-run] [--help|-h]

Options:
  --dry-run  Print deterministic command plan without executing.
  --help     Show this help text.
  -h         Show this help text.
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

cd "${REPO_ROOT}"

PYTEST_CMD=(
    python3 -m pytest
    tests/test_runtime_logging_contracts.py
    tests/test_logging_entry_surface_contracts.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: runtime logging guardrail gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Runtime Logging Guardrail Gate ==="
echo "Step 1/1: scoped logging guardrail tests"
"${PYTEST_CMD[@]}"
echo "Runtime logging guardrail gate: PASS"
