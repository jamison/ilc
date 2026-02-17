#!/usr/bin/env bash
# check_reuse_diversity_invariants_phase_216.sh
# Deterministic gate for anti-Sybil and reuse-diversity weighting invariants.
#
# Usage:
#   ./tools/check_reuse_diversity_invariants_phase_216.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_reuse_diversity_invariants_phase_216.sh [--dry-run] [--help|-h]

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

FOCUSED_CMD=(
    python3 -m pytest
    tests/test_reuse_diversity_invariants_phase_216.py
    -q
)

REGRESSION_CMD=(
    python3 -m pytest
    tests/test_node_value_kernel_phase_205.py
    tests/test_utility_flow_rewards_phase_208.py
    tests/test_refutation_profitability_invariant_phase_212.py
    tests/test_devnet_multi_epoch.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: reuse-diversity invariants gate commands"
    echo "  ${FOCUSED_CMD[*]}"
    echo "  ${REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== Reuse-Diversity Invariants Gate (Phase 216) ==="
echo "Step 1/2: focused invariants and gate tests"
"${FOCUSED_CMD[@]}"
echo "Step 2/2: regression subset"
"${REGRESSION_CMD[@]}"
echo "Reuse-diversity invariants gate: PASS"
