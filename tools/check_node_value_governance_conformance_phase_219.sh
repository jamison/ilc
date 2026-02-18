#!/usr/bin/env bash
# check_node_value_governance_conformance_phase_219.sh
# Additive consolidated preflight for node-value/governance conformance surfaces.
#
# Usage:
#   ./tools/check_node_value_governance_conformance_phase_219.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_node_value_governance_conformance_phase_219.sh [--dry-run] [--help|-h]

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
    tests/test_node_value_governance_conformance_phase_219.py
    -q
)

BASE_CONFORMANCE_CMD=(
    python3 -m pytest
    tests/test_node_value_conformance_phase_206.py
    -q
)

PHASE_212_GATE_CMD=(bash tools/check_refutation_profitability_invariant_phase_212.sh)
PHASE_216_GATE_CMD=(bash tools/check_reuse_diversity_invariants_phase_216.sh)
PHASE_217_GATE_CMD=(bash tools/check_freshness_gate_invariants_phase_217.sh)
PHASE_218_GATE_CMD=(bash tools/check_genesis_accrual_governor_phase_218.sh)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: node-value governance conformance consolidated gate commands"
    echo "  ${FOCUSED_CMD[*]}"
    echo "  ${BASE_CONFORMANCE_CMD[*]}"
    echo "  ${PHASE_212_GATE_CMD[*]}"
    echo "  ${PHASE_216_GATE_CMD[*]}"
    echo "  ${PHASE_217_GATE_CMD[*]}"
    echo "  ${PHASE_218_GATE_CMD[*]}"
    exit 0
fi

echo "=== Node Value + Governance Conformance Gate (Phase 219) ==="
echo "Step 1/6: focused phase-219 conformance tests"
"${FOCUSED_CMD[@]}"
echo "Step 2/6: baseline phase-206 conformance tests"
"${BASE_CONFORMANCE_CMD[@]}"
echo "Step 3/6: phase-212 refutation gate"
"${PHASE_212_GATE_CMD[@]}"
echo "Step 4/6: phase-216 reuse-diversity gate"
"${PHASE_216_GATE_CMD[@]}"
echo "Step 5/6: phase-217 freshness gate"
"${PHASE_217_GATE_CMD[@]}"
echo "Step 6/6: phase-218 Genesis accrual governor gate"
"${PHASE_218_GATE_CMD[@]}"
echo "Node value + governance conformance gate: PASS"
