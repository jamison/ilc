#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_window_286_295_closure_gate_phase_295.sh [--dry-run] [--help|-h]

Composed closure gate for window 286-295.

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
  "bash tools/check_cdl_031_ratification_verification_gate_phase_289.sh"
  "python3 -m pytest tests/test_cdl_033_ratification_291.py -q"
  "python3 -m pytest tests/test_adm_003_reference_agent_architecture_292.py -q"
  "python3 -m pytest tests/test_d2e_04_identity_subsystem_contract_293.py -q"
  "python3 -m pytest tests/test_d2e_04_identity_subsystem_294.py -q"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 295 window closure gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/5] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 295 window closure gate execution:"
i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/5] $cmd"
  bash -lc "$cmd"
  ((i++))
done

echo "Phase 295 window closure gate: PASS"
