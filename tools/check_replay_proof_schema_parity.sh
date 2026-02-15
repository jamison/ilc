#!/usr/bin/env bash
# check_replay_proof_schema_parity.sh
# Deterministic replay-proof schema parity preflight.
#
# Usage:
#   ./tools/check_replay_proof_schema_parity.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

while [ $# -gt 0 ]; do
    case "$1" in
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

cd "${REPO_ROOT}"

PARITY_CMD=(python3 -m pytest tests/test_replay_proof_schema_parity.py -q)

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: replay-proof schema parity preflight commands"
    echo "  ${PARITY_CMD[*]}"
    exit 0
fi

echo "=== Replay-Proof Schema Parity Preflight ==="
"${PARITY_CMD[@]}"
echo "Replay-proof schema parity preflight: PASS"
