#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_security_runtime_window_closure_240_248_phase_249.sh [--dry-run] [--help|-h]

Composed closure gate for window 240-248.

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
  "python3 tools/run_phase_244_security_runtime_gate.py"
  "python3 -m pytest tests/test_d2e_bootstrap_phase_245.py -q"
  "python3 -m pytest tests/test_integration_coherence_248.py -q"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 249 closure gate dry-run:"
  echo "(composes Phase-244 gate and Phase-245/248 tests)"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/3] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 249 closure gate execution:"

i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/3] $cmd"
  eval "$cmd"
  ((i++))
done

echo "Phase 249 closure gate: PASS"
