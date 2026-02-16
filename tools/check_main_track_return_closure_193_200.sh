#!/usr/bin/env bash
# check_main_track_return_closure_193_200.sh
# Deterministic closure gate for main-track return phases 193-200.
#
# Usage:
#   ./tools/check_main_track_return_closure_193_200.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_main_track_return_closure_193_200.sh [--dry-run] [--help|-h]

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
    tests/test_commit_epoch_emission_phase_193.py
    tests/test_epoch_summary_emission_phase_194.py
    tests/test_event_log_envelope_guardrail_phase_195.py
    tests/test_event_log_retention_rotation_phase_196.py
    tests/test_known_records_migration_phase_197.py
    tests/test_server_lifecycle_phase_198.py
    tests/test_server_instance_isolation_phase_199.py
    tests/test_main_track_return_preflight_gate_phase_200.py
    tests/test_ci_workflow_regression_gate.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: main-track return closure gate (193-200) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Main-Track Return Closure Gate (193-200) ==="
echo "Step 1/1: consolidated closure regression subset"
"${PYTEST_CMD[@]}"
echo "Main-track return closure gate: PASS"
