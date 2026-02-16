#!/usr/bin/env bash
# check_non_replay_domain_exception_migration_guardrails.sh
# Deterministic non-replay domain-exception migration guardrail gate.
#
# Usage:
#   ./tools/check_non_replay_domain_exception_migration_guardrails.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_non_replay_domain_exception_migration_guardrails.sh [--dry-run] [--help|-h]

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
    tests/test_non_replay_domain_exception_migration_guardrail.py
    tests/test_event_log_validators.py
    tests/test_ilc_cluster_a_clause_binding.py
    tests/test_governance_ingest_helper_domain_exceptions.py
    tests/test_ledger_export_domain_exceptions.py
    tests/test_mcp_cli_domain_exceptions.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: non-replay domain exception migration guardrail gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Non-Replay Domain Exception Migration Guardrail Gate ==="
echo "Step 1/1: scoped migration guardrail tests"
"${PYTEST_CMD[@]}"
echo "Non-replay domain exception migration guardrail gate: PASS"
