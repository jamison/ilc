#!/usr/bin/env bash
# check_phase_226_security_triage_artifacts.sh
# Deterministic gate for Phase 226 triage artifacts.
#
# Usage:
#   ./tools/check_phase_226_security_triage_artifacts.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

usage() {
    cat <<'USAGE'
Usage: check_phase_226_security_triage_artifacts.sh [--dry-run] [--help|-h]

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
    tests/test_phase_226_security_triage_artifacts.py
    -q
)
SEQUENCE_REGRESSION_CMD=(
    python3 -m pytest
    tests/test_genesis_packaging_distribution_sequence_phase_222.py
    -q
)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: phase-226 security triage artifact commands"
    echo "  ${ARTIFACT_TEST_CMD[*]}"
    echo "  ${SEQUENCE_REGRESSION_CMD[*]}"
    exit 0
fi

echo "=== Phase 226 Security Triage Artifact Gate ==="
echo "Step 1/2: validate phase-226 artifact tests"
"${ARTIFACT_TEST_CMD[@]}"
echo "Step 2/2: run phase-222 sequence regression guardrail"
"${SEQUENCE_REGRESSION_CMD[@]}"
echo "Phase 226 security triage artifact gate: PASS"
