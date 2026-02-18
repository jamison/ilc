#!/usr/bin/env bash
# check_phase_227_blocker_remediation_package.sh
# Deterministic gate for Phase 227 blocker remediation artifacts.
#
# Usage:
#   ./tools/check_phase_227_blocker_remediation_package.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_phase_227_blocker_remediation_package.sh [--dry-run] [--help|-h]

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

ARTIFACT_TEST_CMD=(
    python3 -m pytest
    tests/test_phase_227_blocker_remediation_artifacts.py
    -q
)
PHASE_226_REGRESSION_CMD=(
    python3 -m pytest
    tests/test_phase_226_security_triage_artifacts.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: phase-227 blocker remediation package commands"
    echo "  ${ARTIFACT_TEST_CMD[*]}"
    echo "  ${PHASE_226_REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== Phase 227 Blocker Remediation Package Gate ==="
echo "Step 1/2: validate phase-227 remediation artifact tests"
"${ARTIFACT_TEST_CMD[@]}"
echo "Step 2/2: run phase-226 security triage regression guardrail"
"${PHASE_226_REGRESSION_CMD[@]}"
echo "Phase 227 blocker remediation package gate: PASS"
