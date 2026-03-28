#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_474_g8_window_469_474_closure_gate_and_handoff.md"
SNAPSHOT_PATH="${ILC_PHASE_474_SNAPSHOT_PATH:-out/monitoring/infrastructure_risk_snapshot_phase_316.json}"

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_phase_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

commands=(
  "python3 tools/validate_phase_prompt.py ${PROMPT_PATH}"
  "python3 -m pytest tests/test_phase_469_window_sequence_lock.py tests/test_phase_470_consensus_diversity_floor_finality_runtime.py tests/test_phase_471_distributed_degraded_measurement_harness.py tests/test_phase_472_bridge_realism_and_adversarial_transport.py tests/test_phase_473_consensus_adversarial_hardening_and_findings.py -q"
  "python3 -m pytest tests/test_window_460_468_closure_gate_468.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_469_474_closure_gate_474.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_469_474_closure_gate_phase_474.sh [--dry-run|--help]

Runs the Phase 474 window 469-474 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

print_dry_run() {
  local total="${#labels[@]}"
  local idx
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
  done
}

snapshot_fingerprint() {
  python3 - "$SNAPSHOT_PATH" <<'PY'
import hashlib
import sys
from pathlib import Path
path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit('missing_snapshot')
raw = path.read_bytes()
print(f"{hashlib.sha256(raw).hexdigest()}|{path.stat().st_mtime_ns}")
PY
}

run_command() {
  local command="$1"
  shift || true
  env -u ILC_PHASE_474_GATE_SELFTEST -u ILC_PHASE_468_GATE_SELFTEST "$@" bash -c "$command"
}

run_full_gate() {
  local before after total idx
  before="$(snapshot_fingerprint)"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_468_GATE_SELFTEST=1
    elif [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_474_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done
  after="$(snapshot_fingerprint)"
  if [[ "$before" != "$after" ]]; then
    echo "phase_474_snapshot_isolation=failed"
    return 1
  fi
  echo "phase_474_verdict=pass"
}

if [[ $# -gt 1 ]]; then
  echo "unknown argument count: $#" >&2
  usage >&2
  exit 2
fi

if [[ $# -eq 1 ]]; then
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --dry-run)
      print_dry_run
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
fi

run_full_gate
