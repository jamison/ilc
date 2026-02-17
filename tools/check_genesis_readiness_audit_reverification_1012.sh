#!/usr/bin/env bash
# check_genesis_readiness_audit_reverification_1012.sh
# Deterministic post-remediation re-verification gate for Genesis-readiness audit claims.
#
# Usage:
#   ./tools/check_genesis_readiness_audit_reverification_1012.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_genesis_readiness_audit_reverification_1012.sh [--dry-run] [--help|-h]

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
    tests/test_license_presence_phase_997.py
    tests/test_quickstart_parity_phase_998.py
    tests/test_cli_key_loader_dedupe_phase_999.py
    tests/test_no_silent_exception_pass_phase_1000.py
    tests/test_server_app_factory_phase_1001.py
    tests/test_node_id_dual_contract_phase_1002.py
    tests/test_node_id_runtime_bridge_phase_1003.py
    tests/test_node_id_migration_utility_phase_1004.py
    tests/test_package_hygiene_phase_1005.py
    tests/test_config_dependency_policy_phase_1006.py
    tests/test_edge_link_boundary_phase_1007.py
    tests/test_operator_config_docs_phase_1008.py
    tests/test_genesis_readiness_remediation_closure_gate_phase_1009.py
    tests/test_getting_started_docs_phase_1010.py
    tests/test_broad_exception_boundary_policy_phase_1011.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: genesis readiness audit reverification gate (post-1011) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Genesis Readiness Audit Reverification Gate (post-1011) ==="
echo "Step 1/1: consolidated post-remediation audit subset"
"${PYTEST_CMD[@]}"
echo "Genesis readiness audit reverification gate: PASS"
