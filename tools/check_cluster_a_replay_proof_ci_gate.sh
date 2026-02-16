#!/usr/bin/env bash
# check_cluster_a_replay_proof_ci_gate.sh
# Run the Cluster A Replay Proof CI Gate and optionally enforce baseline.
#
# Usage:
#   ./tools/check_cluster_a_replay_proof_ci_gate.sh [--baseline <path>] [--no-enforce] [--dry-run] [--help|-h]
#
# By default, if a baseline is found at the standard location, baseline
# enforcement is enabled. Pass --no-enforce to disable strict mode.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

FIXTURES_ROOT="${REPO_ROOT}/tests/fixtures"
OUTPUT_DIR="${REPO_ROOT}/output/ci_gate"
PROFILE="release_v0_1"

DEFAULT_BASELINE="${FIXTURES_ROOT}/cluster_a_replay_proof_ci_gate_v0_1/release_v0_1_baseline.json"
BASELINE=""
ENFORCE="true"
DRY_RUN="false"

print_usage() {
    cat <<'EOF'
Usage: check_cluster_a_replay_proof_ci_gate.sh [--baseline <path>] [--no-enforce] [--dry-run] [--help|-h]
EOF
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --baseline)
            if [ $# -lt 2 ] || [ -z "${2}" ]; then
                echo "Missing value for --baseline" >&2
                exit 2
            fi
            BASELINE="$2"
            shift 2
            ;;
        --no-enforce)
            ENFORCE="false"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

# Default baseline if not specified and file exists
if [ -z "${BASELINE}" ] && [ -f "${DEFAULT_BASELINE}" ]; then
    BASELINE="${DEFAULT_BASELINE}"
fi

REPORT_PATH="${OUTPUT_DIR}/ci_gate_report.json"

# Build command
CMD=(python3 -m ilc_core.cli.canon_cluster_a_replay_proof ci-gate
    --fixtures-root "${FIXTURES_ROOT}"
    --profile "${PROFILE}"
    --out "${REPORT_PATH}"
    --pretty)

if [ -n "${BASELINE}" ]; then
    CMD+=(--baseline "${BASELINE}")
    if [ "${ENFORCE}" = "true" ]; then
        CMD+=(--enforce-baseline)
    fi
fi

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: replay-proof ci-gate command plan"
    echo "  Fixtures: ${FIXTURES_ROOT}"
    echo "  Profile:  ${PROFILE}"
    echo "  Output:   ${REPORT_PATH}"
    if [ -n "${BASELINE}" ]; then
        echo "  Baseline: ${BASELINE}"
        echo "  Enforce:  ${ENFORCE}"
    fi
    echo "  Step-3: ${SCRIPT_DIR}/check_non_replay_domain_exception_migration_guardrails.sh"
    echo "  Step-2: ${SCRIPT_DIR}/check_domain_exception_migration_guardrails.sh"
    echo "  Step-1: ${SCRIPT_DIR}/check_replay_proof_schema_parity.sh"
    echo "  Step0:  ${SCRIPT_DIR}/check_track1_closure_guardrails.sh"
    echo "  Step1:  ${CMD[*]}"
    echo "Dry run complete: no commands executed"
    exit 0
fi

mkdir -p "${OUTPUT_DIR}"

# Step -3: Non-replay domain exception migration guardrail preflight
echo "=== CI Gate Step -3: Non-Replay Domain Exception Migration Guardrails ==="
"${SCRIPT_DIR}/check_non_replay_domain_exception_migration_guardrails.sh"
echo ""

# Step -2: Domain exception migration guardrail preflight
echo "=== CI Gate Step -2: Domain Exception Migration Guardrails ==="
"${SCRIPT_DIR}/check_domain_exception_migration_guardrails.sh"
echo ""

# Step -1: Replay-proof schema parity preflight
echo "=== CI Gate Step -1: Replay-Proof Schema Parity ==="
"${SCRIPT_DIR}/check_replay_proof_schema_parity.sh"
echo ""

# Step 0: Track 1 closure guardrail gate
echo "=== CI Gate Step 0: Track 1 Closure Guardrails ==="
"${SCRIPT_DIR}/check_track1_closure_guardrails.sh"
echo ""

echo "Running CI Gate..."
echo "  Fixtures: ${FIXTURES_ROOT}"
echo "  Profile:  ${PROFILE}"
echo "  Output:   ${REPORT_PATH}"
if [ -n "${BASELINE}" ]; then
    echo "  Baseline: ${BASELINE}"
    echo "  Enforce:  ${ENFORCE}"
fi
echo ""

# Capture non-zero gate exits while still honoring strict mode elsewhere.
set +e
"${CMD[@]}"
EXIT_CODE=$?
set -e

echo ""
echo "Exit code: ${EXIT_CODE}"
exit ${EXIT_CODE}
