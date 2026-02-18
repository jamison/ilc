#!/usr/bin/env bash
# check_genesis_distribution_surface_phase_225.sh
# Deterministic gate for Phase 225 distribution surface validation.
#
# Usage:
#   ./tools/check_genesis_distribution_surface_phase_225.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_genesis_distribution_surface_phase_225.sh [--dry-run] [--help|-h]

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

DISTRIBUTION_TEST_CMD=(
    python3 -m pytest
    tests/test_genesis_distribution_surface_phase_225.py
    -q
)
PHASE_224_REGRESSION_CMD=(
    python3 -m pytest
    tests/test_genesis_integration_smoke_phase_224.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: phase-225 distribution surface commands"
    echo "  ${DISTRIBUTION_TEST_CMD[*]}"
    echo "  ${PHASE_224_REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== Phase 225 Distribution Surface Gate ==="
echo "Step 1/2: validate phase-225 distribution tests"
"${DISTRIBUTION_TEST_CMD[@]}"
echo "Step 2/2: run phase-224 integration regression guardrail"
"${PHASE_224_REGRESSION_CMD[@]}"
echo "Phase 225 distribution surface gate: PASS"
