#!/usr/bin/env bash
# check_genesis_readiness_remediation_closure_996_1008.sh
# Deterministic closure gate for Genesis-readiness remediation phases 996-1008.
#
# Usage:
#   ./tools/check_genesis_readiness_remediation_closure_996_1008.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_genesis_readiness_remediation_closure_996_1008.sh [--dry-run] [--help|-h]

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

PYTHON_BIN="${PYTHON:-}"
if [ -z "${PYTHON_BIN}" ]; then
    if [ -x ".venv/bin/python" ]; then
        PYTHON_BIN=".venv/bin/python"
    else
        PYTHON_BIN="python3"
    fi
fi

PYTEST_CMD=(
    "${PYTHON_BIN}" -m pytest
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
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: genesis readiness remediation closure gate (996-1008) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Genesis Readiness Remediation Closure Gate (996-1008) ==="
echo "Step 1/1: consolidated remediation regression subset"
"${PYTEST_CMD[@]}"
echo "Genesis readiness remediation closure gate: PASS"
