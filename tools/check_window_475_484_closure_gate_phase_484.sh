#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_484_g8_window_475_484_closure_gate_and_handoff.md"
SNAPSHOT_PATH="${ILC_PHASE_484_SNAPSHOT_PATH:-out/monitoring/infrastructure_risk_snapshot_phase_316.json}"

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
  "python3 -m pytest tests/test_phase_475_window_sequence_lock.py tests/test_phase_476_cdl_052_epistemic_evaluation_contract_specification.py tests/test_phase_477_cdl_052_epistemic_node_submission_runtime.py tests/test_phase_478_cdl_052_epistemic_runtime_part_2.py tests/test_phase_479_genesis_validator_bootstrap_specification.py tests/test_phase_480_genesis_validator_bootstrap_runtime_part_1.py tests/test_phase_481_genesis_validator_bootstrap_runtime_part_2.py tests/test_phase_482_cdl_052_genesis_integration_findings_memo.py tests/test_phase_483_coherence_and_capsule_v2_2.py -q"
  "python3 -m pytest tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_475_484_closure_gate_484.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_475_484_closure_gate_phase_484.sh [--dry-run|--help]

Runs the Phase 484 window 475-484 closure gate.

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

snapshot_gate_state() {
  python3 - "$SNAPSHOT_PATH" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit('missing_snapshot')
payload = json.loads(path.read_text(encoding='utf-8'))
phase = str(payload.get('phase'))
scope = 'true' if payload.get('preflight_scope') is True else 'false'
verdict = str(payload.get('severity_summary', {}).get('verdict', 'missing'))
print(f"{phase}|{scope}|{verdict}")
PY
}

resolve_snapshot_gate() {
  local snapshot_phase="$1"
  local snapshot_scope="$2"
  local snapshot_verdict="$3"

  if [[ "$snapshot_phase" != "316" || "$snapshot_scope" != "true" ]]; then
    echo "phase_484_snapshot_gate=failed"
    echo "phase_484_snapshot_details=phase:${snapshot_phase},preflight_scope:${snapshot_scope}"
    return 1
  fi

  case "$snapshot_verdict" in
    pass)
      echo "phase_484_snapshot_gate=passed"
      return 0
      ;;
    conditional)
      echo "phase_484_snapshot_gate=conditional"
      return 3
      ;;
    blocked)
      echo "phase_484_snapshot_gate=failed"
      echo "phase_484_snapshot_details=verdict:${snapshot_verdict}"
      return 1
      ;;
    *)
      echo "phase_484_snapshot_gate=failed"
      echo "phase_484_snapshot_details=verdict:${snapshot_verdict}"
      return 1
      ;;
  esac
}

run_command() {
  local command="$1"
  shift || true
  env \
    -u ILC_PHASE_484_GATE_SELFTEST \
    -u ILC_PHASE_474_GATE_SELFTEST \
    -u ILC_PHASE_468_GATE_SELFTEST \
    -u ILC_PHASE_459_GATE_SELFTEST \
    -u ILC_PHASE_449_GATE_SELFTEST \
    -u ILC_PHASE_440_GATE_SELFTEST \
    -u ILC_PHASE_433_GATE_SELFTEST \
    -u ILC_PHASE_423_GATE_SELFTEST \
    -u ILC_PHASE_413_GATE_SELFTEST \
    -u ILC_PHASE_401_GATE_SELFTEST \
    -u ILC_PHASE_391_GATE_SELFTEST \
    -u ILC_PHASE_377_GATE_SELFTEST \
    -u ILC_PHASE_367_GATE_SELFTEST \
    -u ILC_PHASE_357_GATE_SELFTEST \
    -u ILC_PHASE_347_GATE_SELFTEST \
    -u ILC_PHASE_337_GATE_SELFTEST \
    -u ILC_PHASE_484_SNAPSHOT_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local before after total idx snapshot_info snapshot_phase snapshot_scope snapshot_verdict verdict_rc
  snapshot_info="$(snapshot_gate_state)"
  IFS='|' read -r snapshot_phase snapshot_scope snapshot_verdict <<<"${snapshot_info}"
  resolve_snapshot_gate "$snapshot_phase" "$snapshot_scope" "$snapshot_verdict" || verdict_rc=$?
  verdict_rc="${verdict_rc:-0}"
  if [[ "$verdict_rc" -ne 0 ]]; then
    return "$verdict_rc"
  fi

  before="$(snapshot_fingerprint)"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
        ILC_PHASE_474_GATE_SELFTEST=1 \
        ILC_PHASE_468_GATE_SELFTEST=1 \
        ILC_PHASE_459_GATE_SELFTEST=1 \
        ILC_PHASE_449_GATE_SELFTEST=1 \
        ILC_PHASE_440_GATE_SELFTEST=1 \
        ILC_PHASE_433_GATE_SELFTEST=1 \
        ILC_PHASE_423_GATE_SELFTEST=1 \
        ILC_PHASE_413_GATE_SELFTEST=1 \
        ILC_PHASE_401_GATE_SELFTEST=1 \
        ILC_PHASE_391_GATE_SELFTEST=1 \
        ILC_PHASE_377_GATE_SELFTEST=1 \
        ILC_PHASE_367_GATE_SELFTEST=1 \
        ILC_PHASE_357_GATE_SELFTEST=1 \
        ILC_PHASE_347_GATE_SELFTEST=1 \
        ILC_PHASE_337_GATE_SELFTEST=1
    elif [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_484_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done
  after="$(snapshot_fingerprint)"
  if [[ "$before" != "$after" ]]; then
    echo "phase_484_snapshot_isolation=failed"
    return 1
  fi
  echo "phase_484_verdict=pass"
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
