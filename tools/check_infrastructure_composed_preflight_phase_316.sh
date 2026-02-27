#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: tools/check_infrastructure_composed_preflight_phase_316.sh [--dry-run|--help]

Runs the Phase 316 composed schema/genesis/epoch infrastructure preflight.

Options:
  --dry-run   Print deterministic ordered category list and exit 0.
  --help      Print this help and exit 0.
USAGE
}

print_categories() {
  local categories=(
    "schema_lane_scenarios"
    "genesis_lane_scenarios"
    "epoch_lane_scenarios"
    "cross_lane_dependency_regression"
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

python3 tools/run_infrastructure_composed_preflight_phase_316.py
