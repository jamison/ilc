#!/usr/bin/env bash
# check_main_track_return_closure_202_210.sh
# Deterministic closure gate for main-track return phases 202-210.
#
# Usage:
#   ./tools/check_main_track_return_closure_202_210.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_main_track_return_closure_202_210.sh [--dry-run] [--help|-h]

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
    tests/test_main_track_return_sequence_phase_202.py
    tests/test_node_value_input_canon_phase_203.py
    tests/test_node_value_extraction_phase_204.py
    tests/test_node_value_kernel_phase_205.py
    tests/test_node_value_conformance_phase_206.py
    tests/test_governance_weight_phase_207.py
    tests/test_utility_flow_rewards_phase_208.py
    tests/test_node_value_policy_migration_phase_209.py
    tests/test_main_track_return_preflight_gate_phase_210.py
    tests/test_ci_workflow_regression_gate.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: main-track return closure gate (202-210) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Main-Track Return Closure Gate (202-210) ==="
echo "Step 1/1: consolidated closure regression subset"
"${PYTEST_CMD[@]}"
echo "Main-track return closure gate: PASS"
