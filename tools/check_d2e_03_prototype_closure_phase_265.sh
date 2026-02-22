#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_d2e_03_prototype_closure_phase_265.sh [--dry-run] [--help|-h]

Composed closure gate for D2e-03 prototype readiness.

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
  "python3 -m pytest tests/test_d2e_03_cli_prototype_264.py -q"
  "python3 -m pytest tests/test_d2e_03_prototype_contract_263.py -q"
  "python3 -m ilc_core.cli.main --help"
  "python3 tools/run_phase_236_preflight.py"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 265 D2e-03 closure gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/4] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 265 D2e-03 closure gate execution:"

i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/4] $cmd"
  eval "$cmd"
  ((i++))
done

echo "Phase 265 D2e-03 closure gate: PASS"
