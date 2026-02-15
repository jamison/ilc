#!/usr/bin/env bash
# check_domain_exception_migration_guardrails.sh
# Deterministic domain-exception migration guardrail gate.
#
# Usage:
#   ./tools/check_domain_exception_migration_guardrails.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_domain_exception_migration_guardrails.sh [--dry-run] [--help|-h]

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
    tests/test_domain_exception_migration_guardrail.py
    tests/test_protocol_schema.py
    tests/test_protocol_mapper.py
    tests/test_ilc_cluster_a_replay_proof_batch.py
    tests/test_ilc_cluster_a_replay_proof_package.py
    tests/test_ilc_cluster_a_replay_proof_ci_gate_baseline.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: domain exception migration guardrail gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Domain Exception Migration Guardrail Gate ==="
echo "Step 1/1: scoped migration guardrail tests"
"${PYTEST_CMD[@]}"
echo "Domain exception migration guardrail gate: PASS"
