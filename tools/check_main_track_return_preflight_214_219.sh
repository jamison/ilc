#!/usr/bin/env bash
# check_main_track_return_preflight_214_219.sh
# Deterministic preflight gate for main-track return phases 214-219.
#
# Usage:
#   ./tools/check_main_track_return_preflight_214_219.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_main_track_return_preflight_214_219.sh [--dry-run] [--help|-h]

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

PHASE_214_CMD=(
    python3 -m pytest
    tests/test_path_lift_counterfactual_phase_214.py
    -q
)
PHASE_215_CMD=(
    python3 -m pytest
    tests/test_cdl_011_015_ratification_evidence_phase_215.py
    -q
)
PHASE_216_CMD=(
    python3 -m pytest
    tests/test_reuse_diversity_invariants_phase_216.py
    -q
)
PHASE_217_CMD=(
    python3 -m pytest
    tests/test_freshness_gate_phase_217.py
    -q
)
PHASE_218_CMD=(
    python3 -m pytest
    tests/test_genesis_accrual_governor_phase_218.py
    -q
)
PHASE_219_CMD=(
    python3 -m pytest
    tests/test_node_value_governance_conformance_phase_219.py
    -q
)
CROSS_PHASE_CMD=(
    python3 -m pytest
    tests/test_node_value_kernel_phase_205.py
    tests/test_node_value_conformance_phase_206.py
    tests/test_utility_flow_rewards_phase_208.py
    tests/test_refutation_profitability_invariant_phase_212.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: main-track return preflight (phases 214-219) commands"
    echo "  ${PHASE_214_CMD[*]}"
    echo "  ${PHASE_215_CMD[*]}"
    echo "  ${PHASE_216_CMD[*]}"
    echo "  ${PHASE_217_CMD[*]}"
    echo "  ${PHASE_218_CMD[*]}"
    echo "  ${PHASE_219_CMD[*]}"
    echo "  ${CROSS_PHASE_CMD[*]}"
    exit 0
fi

echo "=== Main-Track Return Preflight Gate (214-219) ==="
echo "Step 1/7: phase-214 path-lift tests"
"${PHASE_214_CMD[@]}"
echo "Step 2/7: phase-215 evidence tests"
"${PHASE_215_CMD[@]}"
echo "Step 3/7: phase-216 diversity invariant tests"
"${PHASE_216_CMD[@]}"
echo "Step 4/7: phase-217 freshness gate tests"
"${PHASE_217_CMD[@]}"
echo "Step 5/7: phase-218 Genesis governor tests"
"${PHASE_218_CMD[@]}"
echo "Step 6/7: phase-219 conformance consolidation tests"
"${PHASE_219_CMD[@]}"
echo "Step 7/7: cross-phase regression subset"
"${CROSS_PHASE_CMD[@]}"
echo "Main-track return preflight gate: PASS"
