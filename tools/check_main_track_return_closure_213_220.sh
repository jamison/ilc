#!/usr/bin/env bash
# check_main_track_return_closure_213_220.sh
# Deterministic closure gate for main-track return phases 213-220.
#
# Usage:
#   ./tools/check_main_track_return_closure_213_220.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_main_track_return_closure_213_220.sh [--dry-run] [--help|-h]

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

PHASE_219_GATE_CMD=(bash tools/check_node_value_governance_conformance_phase_219.sh)
PHASE_220_GATE_CMD=(bash tools/check_main_track_return_preflight_214_219.sh)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: main-track return closure gate (213-220) commands"
    echo "  ${PHASE_219_GATE_CMD[*]}"
    echo "  ${PHASE_220_GATE_CMD[*]}"
    exit 0
fi

echo "=== Main-Track Return Closure Gate (213-220) ==="
echo "Step 1/2: run phase-219 consolidated conformance gate"
"${PHASE_219_GATE_CMD[@]}"
echo "Step 2/2: run phase-220 preflight gate"
"${PHASE_220_GATE_CMD[@]}"
echo "Main-track return closure gate: PASS"
