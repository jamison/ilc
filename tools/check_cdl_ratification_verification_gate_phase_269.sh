#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_cdl_ratification_verification_gate_phase_269.sh [--dry-run] [--help|-h]

Composed ratification verification gate for window 260-269.

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
  "python3 -m pytest tests/test_cdl_025_ratification_267.py -q"
  "python3 -m pytest tests/test_cdl_019_ratification_268.py -q"
  "python3 -m pytest tests/test_ratification_mutation_scope_261.py -q"
  "python3 -m pytest tests/test_cdl_032_ratification_253.py tests/test_security_cdl_ratification_251.py -q"
  "bash tools/check_d2e_03_prototype_closure_phase_265.sh"
  "bash tools/check_refutation_profitability_invariant_phase_212.sh"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 269 ratification verification gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/6] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 269 ratification verification gate execution:"
i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/6] $cmd"
  eval "$cmd"
  ((i++))
done

echo "Phase 269 ratification verification gate: PASS"
