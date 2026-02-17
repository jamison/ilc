#!/usr/bin/env bash
# check_cdl_011_015_ratification_evidence_phase_215.sh
# Deterministic gate for CDL-011..015 ratification evidence closure contracts.
#
# Usage:
#   ./tools/check_cdl_011_015_ratification_evidence_phase_215.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_cdl_011_015_ratification_evidence_phase_215.sh [--dry-run] [--help|-h]

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

EVIDENCE_CMD=(
    python3 -m pytest
    tests/test_cdl_011_015_ratification_evidence_phase_215.py
    -q
)

REGRESSION_CMD=(
    python3 -m pytest
    tests/test_node_value_kernel_phase_205.py
    tests/test_node_value_conformance_phase_206.py
    tests/test_governance_weight_phase_207.py
    tests/test_utility_flow_rewards_phase_208.py
    tests/test_node_value_policy_migration_phase_209.py
    tests/test_path_lift_counterfactual_phase_214.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: CDL-011..015 ratification evidence gate commands"
    echo "  ${EVIDENCE_CMD[*]}"
    echo "  ${REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== CDL-011..015 Ratification Evidence Gate (Phase 215) ==="
echo "Step 1/2: decision-log and evidence bundle contract checks"
"${EVIDENCE_CMD[@]}"
echo "Step 2/2: RA regression subset"
"${REGRESSION_CMD[@]}"
echo "CDL-011..015 ratification evidence gate: PASS"
