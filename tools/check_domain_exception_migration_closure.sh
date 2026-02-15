#!/usr/bin/env bash
# check_domain_exception_migration_closure.sh
# Deterministic closure gate for domain-exception migration phases 172-180.
#
# Usage:
#   ./tools/check_domain_exception_migration_closure.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_domain_exception_migration_closure.sh [--dry-run] [--help|-h]

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
    tests/test_domain_exception_migration_guardrail_gate.py
    tests/test_track1_closure_guardrail_gate_ops.py
    tests/test_ci_workflow_regression_gate.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: domain exception migration closure gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Domain Exception Migration Closure Gate ==="
echo "Step 1/1: closure guardrail and integration contract tests"
"${PYTEST_CMD[@]}"
echo "Domain exception migration closure gate: PASS"
