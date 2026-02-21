#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
usage: check_cdl_ratification_window_closure_250_258_phase_259.sh [--dry-run] [--help|-h]

Composed closure gate for window 250-258.

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
  "python3 tools/run_phase_252_security_ratification_gate.py"
  "python3 -m pytest tests/test_cdl_032_ratification_253.py -q"
  "python3 -m pytest tests/test_cli_output_schemas_254.py -q"
  "python3 -m pytest tests/test_d2_minimal_schema_spec_255.py -q"
  "python3 -m pytest tests/test_integration_coherence_258.py -q"
)

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Phase 259 closure gate dry-run:"
  i=1
  for cmd in "${COMMANDS[@]}"; do
    echo "[$i/5] $cmd"
    ((i++))
  done
  exit 0
fi

echo "Phase 259 closure gate execution:"

i=1
for cmd in "${COMMANDS[@]}"; do
  echo "[$i/5] $cmd"
  eval "$cmd"
  ((i++))
done

echo "Phase 259 closure gate: PASS"
