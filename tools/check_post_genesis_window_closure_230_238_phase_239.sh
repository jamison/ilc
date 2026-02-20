#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: tools/check_post_genesis_window_closure_230_238_phase_239.sh [--dry-run] [--help|-h]

Runs composed closure checks for post-genesis window 230-238.

Options:
  --dry-run   Print commands without executing
  --help      Show this help message
  -h          Show this help message
USAGE
}

DRY_RUN="false"
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

CMD1=(python3 tools/run_phase_236_preflight.py)
CMD2=(python3 -m pytest tests/test_integration_coherence_237.py -q)
CMD3=(python3 -m pytest tests/test_release_readiness_package_238.py -q)

if [ "${DRY_RUN}" = "true" ]; then
  echo "Phase 239 closure dry-run:"
  echo "1. ${CMD1[*]}"
  echo "2. ${CMD2[*]}"
  echo "3. ${CMD3[*]}"
  exit 0
fi

echo "Phase 239 closure execution:"
echo "[1/3] ${CMD1[*]}"
"${CMD1[@]}"
echo "[2/3] ${CMD2[*]}"
"${CMD2[@]}"
echo "[3/3] ${CMD3[*]}"
"${CMD3[@]}"

echo "Phase 239 closure: PASS"
