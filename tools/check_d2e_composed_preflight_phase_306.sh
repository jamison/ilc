#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/check_d2e_composed_preflight_phase_306.sh [--dry-run|--help]

Runs the Phase 306 composed query/verify/bundle integration preflight.

Options:
  --dry-run   Print deterministic ordered category list and exit 0.
  --help      Print this help and exit 0.
EOF
}

print_categories() {
  local categories=(
    "query_lane_scenarios"
    "verify_lane_scenarios"
    "bundle_lane_scenarios"
    "cross_lane_envelope_regression"
    "kpi_snapshot"
  )
  local total="${#categories[@]}"
  local i=1
  for category in "${categories[@]}"; do
    printf '[%s/%s] %s\n' "$i" "$total" "$category"
    i=$((i + 1))
  done
}

if [[ $# -gt 1 ]]; then
  echo "unknown argument count: $#" >&2
  usage >&2
  exit 2
fi

if [[ $# -eq 1 ]]; then
  case "$1" in
    --help)
      usage
      exit 0
      ;;
    --dry-run)
      print_categories
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
fi

PYTHON_BIN="${PYTHON:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

"${PYTHON_BIN}" tools/run_d2e_composed_preflight_phase_306.py
