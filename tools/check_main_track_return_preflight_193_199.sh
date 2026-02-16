#!/usr/bin/env bash
# check_main_track_return_preflight_193_199.sh
# Deterministic preflight gate for main-track return phases 193-199.
#
# Usage:
#   ./tools/check_main_track_return_preflight_193_199.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_main_track_return_preflight_193_199.sh [--dry-run] [--help|-h]

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
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: main-track return preflight (phases 193-199) commands"
    echo "  ${PYTEST_CMD[*]}"
    exit 0
fi

echo "=== Main-Track Return Preflight Gate (193-199) ==="
echo "Step 1/1: focused phase preflight regression subset"
"${PYTEST_CMD[@]}"
echo "Main-track return preflight gate: PASS"
