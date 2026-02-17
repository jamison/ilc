#!/usr/bin/env bash
# check_nodeid_strict_canonical_closure_1014.sh
# Deterministic closure gate for strict canonical NodeID cutover.
#
# Usage:
#   ./tools/check_nodeid_strict_canonical_closure_1014.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_nodeid_strict_canonical_closure_1014.sh [--dry-run] [--help|-h]

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
    tests/test_node_id_dual_contract_phase_1002.py
    tests/test_node_id_runtime_bridge_phase_1003.py
    tests/test_node_id_migration_utility_phase_1004.py
    tests/test_task_primitive.py
    tests/test_api.py
    tests/test_server_gossip_exception_contracts.py
    tests/test_server_instance_isolation_phase_199.py
    tests/test_genesis_readiness_audit_reverification_gate_phase_1012.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: nodeid strict canonical closure gate (phase 1014) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== NodeID Strict Canonical Closure Gate (Phase 1014) ==="
echo "Step 1/1: strict canonical nodeid closure subset"
"${PYTEST_CMD[@]}"
echo "NodeID strict canonical closure gate: PASS"
