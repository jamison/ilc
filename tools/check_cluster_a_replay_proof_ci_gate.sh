#!/bin/bash
# Helper script to run the Cluster A Replay Proof CI Gate
# Usage: ./check_cluster_a_replay_proof_ci_gate.sh [OUTPUT_DIR]

set -e

# Default output dir to automation/reports if not provided
OUT_DIR="${1:-automation/reports}"
mkdir -p "$OUT_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H%M%SZ")
REPORT_PATH="${OUT_DIR}/cluster_a_replay_proof_ci_gate_report_${TIMESTAMP}.json"

# Resolve absolute path to fixtures
# Assuming script is in tools/ and root is ..
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_ROOT="${REPO_ROOT}/tests/fixtures"

echo "Running Cluster A Replay Proof CI Gate..."
echo "Fixtures Root: ${FIXTURES_ROOT}"
echo "Report Path: ${REPORT_PATH}"

# We invoke the module directly using python -m
# This ensures we use the current python env
python3 -m ilc_core.cli.canon_cluster_a_replay_proof ci-gate \
    --fixtures-root "$FIXTURES_ROOT" \
    --out "$REPORT_PATH" \
    --pretty

EXIT_CODE=$?

echo "CI Gate finished with exit code: ${EXIT_CODE}"
exit $EXIT_CODE
