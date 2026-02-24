#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_cdl_ratification_verification_gate_phase_279.sh [--dry-run] [--help|-h]

Composed ratification verification gate for window 270-279.

Options:
  --dry-run   Print commands without executing them.
  --help,-h   Show this help message.
USAGE
}

DRY_RUN=0

while (($# > 0)); do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      print_usage >&2
      exit 2
      ;;
  esac
done

COMMANDS=(
  "bash tools/check_cdl_ratification_verification_gate_phase_269.sh"
  "python3 tools/check_cdl_ratified_state_phase_279.py"
  "python3 -m pytest tests/test_cdl_029_ratification_272.py -q"
  "python3 -m pytest tests/test_cdl_026_ratification_273.py -q"
  "python3 -m pytest tests/test_cdl_028_ratification_274.py -q"
  "python3 -m pytest tests/test_cdl_027_ratification_276.py -q"
  "python3 -m pytest tests/test_cdl_030_ratification_277.py -q"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 279 ratification verification gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/7] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 279 ratification verification gate execution:"
i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/7] $cmd"
  bash -lc "$cmd"
  ((i++))
done

echo "Phase 279 ratification verification gate: PASS"
