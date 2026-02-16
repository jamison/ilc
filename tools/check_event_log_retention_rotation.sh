#!/usr/bin/env bash
# check_event_log_retention_rotation.sh
# Deterministic gate for event-log retention and rotation contracts.
#
# Usage:
#   ./tools/check_event_log_retention_rotation.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_event_log_retention_rotation.sh [--dry-run] [--help|-h]

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
    tests/test_event_log_retention_rotation_phase_196.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: event-log retention/rotation gate commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Event Log Retention and Rotation Gate ==="
echo "Step 1/1: retention and rotation contract tests"
"${PYTEST_CMD[@]}"
echo "Event log retention and rotation gate: PASS"
