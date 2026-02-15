#!/usr/bin/env bash
# check_cluster_a_replay_proof_release_gate.sh
# Combined release-oriented CI gate script.
# Runs:
#   1. replay-proof CI gate with baseline enforcement,
#   2. verify-and-compare against canonical fixtures.
# Exits non-zero on any drift, security, or contract violation.
#
# Usage:
#   ./tools/check_cluster_a_replay_proof_release_gate.sh [--no-enforce]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

FIXTURES_ROOT="${REPO_ROOT}/tests/fixtures"
OUTPUT_DIR="${REPO_ROOT}/output/release_gate"
PROFILE="release_v0_1"
ENFORCE="true"
DRY_RUN="false"
OVERALL_EXIT=0

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --no-enforce)
            ENFORCE="false"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

mkdir -p "${OUTPUT_DIR}"

# --- Step 0: Track 1 closure guardrail gate ---
if [ "${DRY_RUN}" = "true" ]; then
    BASELINE="${FIXTURES_ROOT}/cluster_a_replay_proof_ci_gate_v0_1/release_v0_1_baseline.json"
    GATE_REPORT_PATH="${OUTPUT_DIR}/ci_gate_report.json"

    GATE_CMD=(python3 -m ilc_core.cli.canon_cluster_a_replay_proof ci-gate
        --fixtures-root "${FIXTURES_ROOT}"
        --profile "${PROFILE}"
        --out "${GATE_REPORT_PATH}"
        --pretty)

    if [ -f "${BASELINE}" ]; then
        GATE_CMD+=(--baseline "${BASELINE}")
        if [ "${ENFORCE}" = "true" ]; then
            GATE_CMD+=(--enforce-baseline)
        fi
    fi

    OPS_FIXTURES="${FIXTURES_ROOT}/cluster_a_replay_proof_batch_ops_v0_1"
    MANIFEST="${OPS_FIXTURES}/manifest.txt"
    EXPECTED_REPORT="${OPS_FIXTURES}/report_match.json"
    V_AND_C_REPORT="${OUTPUT_DIR}/verify_and_compare_batch.json"
    V_AND_C_COMPARE="${OUTPUT_DIR}/verify_and_compare_compare.json"

    VC_CMD=(python3 -m ilc_core.cli.canon_cluster_a_replay_proof verify-and-compare
        --manifest "${MANIFEST}"
        --expected "${EXPECTED_REPORT}"
        --out-report "${V_AND_C_REPORT}"
        --out-compare "${V_AND_C_COMPARE}"
        --pretty)

    echo "Dry run: replay-proof release gate command plan"
    echo "  Fixtures: ${FIXTURES_ROOT}"
    echo "  Output:   ${OUTPUT_DIR}"
    echo "  Enforce:  ${ENFORCE}"
    echo "  Step0: ${SCRIPT_DIR}/check_track1_closure_guardrails.sh"
    echo "  Step1: ${GATE_CMD[*]}"
    if [ -f "${MANIFEST}" ] && [ -f "${EXPECTED_REPORT}" ]; then
        echo "  Step2: ${VC_CMD[*]}"
    else
        echo "  Step2: skipped (fixtures not found)"
    fi
    echo "Dry run complete: no commands executed"
    exit 0
fi

# --- Step 0: Track 1 closure guardrail gate ---
echo "=== Release Gate Step 0: Track 1 Closure Guardrails ==="
"${SCRIPT_DIR}/check_track1_closure_guardrails.sh"
echo ""

# --- Step 1: CI Gate with baseline enforcement ---

BASELINE="${FIXTURES_ROOT}/cluster_a_replay_proof_ci_gate_v0_1/release_v0_1_baseline.json"
GATE_REPORT_PATH="${OUTPUT_DIR}/ci_gate_report.json"

GATE_CMD=(python3 -m ilc_core.cli.canon_cluster_a_replay_proof ci-gate
    --fixtures-root "${FIXTURES_ROOT}"
    --profile "${PROFILE}"
    --out "${GATE_REPORT_PATH}"
    --pretty)

if [ -f "${BASELINE}" ]; then
    GATE_CMD+=(--baseline "${BASELINE}")
    if [ "${ENFORCE}" = "true" ]; then
        GATE_CMD+=(--enforce-baseline)
    fi
fi

echo "=== Release Gate Step 1: CI Gate ==="
echo "  Fixtures: ${FIXTURES_ROOT}"
echo "  Profile:  ${PROFILE}"
echo "  Baseline: ${BASELINE}"
echo "  Enforce:  ${ENFORCE}"
echo ""

set +e
"${GATE_CMD[@]}"
GATE_EXIT=$?
set -e

echo ""
echo "CI Gate exit code: ${GATE_EXIT}"

if [ "${GATE_EXIT}" -ne 0 ]; then
    OVERALL_EXIT=${GATE_EXIT}
fi

echo ""

# --- Step 2: Verify-and-compare against canonical fixtures ---

OPS_FIXTURES="${FIXTURES_ROOT}/cluster_a_replay_proof_batch_ops_v0_1"
MANIFEST="${OPS_FIXTURES}/manifest.txt"
EXPECTED_REPORT="${OPS_FIXTURES}/report_match.json"
V_AND_C_REPORT="${OUTPUT_DIR}/verify_and_compare_batch.json"
V_AND_C_COMPARE="${OUTPUT_DIR}/verify_and_compare_compare.json"

if [ -f "${MANIFEST}" ] && [ -f "${EXPECTED_REPORT}" ]; then
    VC_CMD=(python3 -m ilc_core.cli.canon_cluster_a_replay_proof verify-and-compare
        --manifest "${MANIFEST}"
        --expected "${EXPECTED_REPORT}"
        --out-report "${V_AND_C_REPORT}"
        --out-compare "${V_AND_C_COMPARE}"
        --pretty)

    echo "=== Release Gate Step 2: Verify-and-Compare ==="
    echo "  Manifest: ${MANIFEST}"
    echo "  Expected: ${EXPECTED_REPORT}"
    echo ""

    set +e
    "${VC_CMD[@]}"
    VC_EXIT=$?
    set -e

    echo ""
    echo "Verify-and-Compare exit code: ${VC_EXIT}"

    if [ "${VC_EXIT}" -ne 0 ]; then
        if [ "${OVERALL_EXIT}" -eq 0 ]; then
            OVERALL_EXIT=${VC_EXIT}
        fi
    fi
else
    echo "=== Release Gate Step 2: SKIPPED (fixtures not found) ==="
fi

echo ""
echo "=== Release Gate Summary ==="
echo "  CI Gate:            exit ${GATE_EXIT}"
if [ -f "${MANIFEST}" ] && [ -f "${EXPECTED_REPORT}" ]; then
    echo "  Verify-and-Compare: exit ${VC_EXIT}"
fi
echo "  Overall:            exit ${OVERALL_EXIT}"
exit ${OVERALL_EXIT}
