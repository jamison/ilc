#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_cdl_031_ratification_verification_gate_phase_289.sh [--dry-run] [--help|-h]

Composed verification gate for CDL-031 closure (phase 289).

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
  "bash tools/check_cdl_ratification_verification_gate_phase_279.sh"
  "python3 -m pytest tests/test_cdl_031_ratification_288.py -q"
  "python3 -m pytest tests/test_ratification_mutation_scope_261.py -q"
  "python3 -m pytest tests/test_crypto_migration_initial_tranche_283.py -q"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 289 CDL-031 verification gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/4] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 289 CDL-031 verification gate execution:"
i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/4] $cmd"
  bash -lc "$cmd"
  ((i++))
done

echo "Phase 289 CDL-031 verification gate: PASS"
