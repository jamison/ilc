#!/usr/bin/env bash
# check_genesis_integration_smoke_phase_224.sh
# Deterministic gate for phase 224 end-to-end integration and install-import smoke.
#
# Usage:
#   ./tools/check_genesis_integration_smoke_phase_224.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_genesis_integration_smoke_phase_224.sh [--dry-run] [--help|-h]

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

INTEGRATION_CMD=(
    python3 -m pytest
    tests/test_genesis_integration_smoke_phase_224.py
    -q
)

INSTALL_CMD=(
    python3 -m pytest
    tests/test_genesis_install_smoke_phase_224.py
    -q
)

REGRESSION_CMD=(
    python3 -m pytest
    tests/test_node_value_governance_conformance_phase_219.py
    tests/test_refutation_profitability_invariant_phase_212.py
    tests/test_genesis_accrual_governor_phase_218.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: genesis integration smoke gate commands"
    echo "  ${INTEGRATION_CMD[*]}"
    echo "  ${INSTALL_CMD[*]}"
    echo "  ${REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== Genesis Integration Smoke Gate (Phase 224) ==="
echo "Step 1/3: end-to-end integration smoke"
"${INTEGRATION_CMD[@]}"
echo "Step 2/3: post-install import smoke"
"${INSTALL_CMD[@]}"
echo "Step 3/3: focused regression subset"
"${REGRESSION_CMD[@]}"
echo "Genesis integration smoke gate: PASS"
