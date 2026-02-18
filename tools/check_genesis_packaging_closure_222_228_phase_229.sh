#!/usr/bin/env bash
# check_genesis_packaging_closure_222_228_phase_229.sh
# Deterministic closure gate for Genesis packaging sequence 222-228.
#
# Usage:
#   ./tools/check_genesis_packaging_closure_222_228_phase_229.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_genesis_packaging_closure_222_228_phase_229.sh [--dry-run] [--help|-h]

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

PHASE_226_GATE_CMD=(bash tools/check_phase_226_security_triage_artifacts.sh)
PHASE_227_GATE_CMD=(bash tools/check_phase_227_blocker_remediation_package.sh)
PHASE_225_GATE_CMD=(bash tools/check_genesis_distribution_surface_phase_225.sh)
PHASE_228_GATE_CMD=(bash tools/check_genesis_release_artifacts_phase_228.sh)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: genesis packaging closure gate (222-228) commands"
    echo "  ${PHASE_226_GATE_CMD[*]}"
    echo "  ${PHASE_227_GATE_CMD[*]}"
    echo "  ${PHASE_225_GATE_CMD[*]}"
    echo "  ${PHASE_228_GATE_CMD[*]}"
    exit 0
fi

echo "=== Genesis Packaging Closure Gate (222-228) ==="
echo "Step 1/4: phase-226 triage artifact gate"
"${PHASE_226_GATE_CMD[@]}"
echo "Step 2/4: phase-227 remediation package gate"
"${PHASE_227_GATE_CMD[@]}"
echo "Step 3/4: phase-225 distribution surface gate"
"${PHASE_225_GATE_CMD[@]}"
echo "Step 4/4: phase-228 release artifact gate"
"${PHASE_228_GATE_CMD[@]}"
echo "Genesis packaging closure gate (222-228): PASS"
