#!/usr/bin/env bash
# check_refutation_profitability_invariant_phase_212.sh
# Deterministic gate for the refutation-profitability invariant contracts.
#
# Usage:
#   ./tools/check_refutation_profitability_invariant_phase_212.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_refutation_profitability_invariant_phase_212.sh [--dry-run] [--help|-h]

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
    tests/test_refutation_profitability_invariant_phase_212.py
    tests/test_utility_flow_rewards_phase_208.py
    tests/test_devnet_multi_epoch.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: refutation-profitability invariant gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Refutation-Profitability Invariant Gate (Phase 212) ==="
echo "Step 1/1: invariant and regression subset"
"${PYTEST_CMD[@]}"
echo "Refutation-profitability invariant gate: PASS"

