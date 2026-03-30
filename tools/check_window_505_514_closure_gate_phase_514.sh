#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_514_g8_window_505_514_closure_gate_and_handoff.md"
DECISION_LOG_PATH="${ILC_PHASE_514_DECISION_LOG_PATH:-docs/specs/ilc_constitutional_decision_log_v0.1.md}"
SNAPSHOT_PATH="${ILC_PHASE_514_SNAPSHOT_PATH:-}"

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_window_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

commands=(
  "python3 tools/validate_phase_prompt.py ${PROMPT_PATH}"
  "python3 -m pytest tests/test_phase_505_sequence_lock_and_carry_forward_intake.py tests/test_phase_506_validator_staking_liveness_runtime.py tests/test_phase_507_validator_trust_tier_runtime.py tests/test_phase_508_epoch_boundary_cdl_vehicle_selection.py tests/test_phase_509_epoch_boundary_cdl_opening_stub.py tests/test_phase_510_epoch_boundary_cdl_prelock_hardening.py tests/test_phase_511_epoch_boundary_cdl_ratification_evidence.py tests/test_phase_512_re_admission_boundary_cdl_scoping.py tests/test_phase_513_coherence_report_and_capsule_v2_4.py -q"
  "python3 -m pytest tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_505_514_closure_gate_514.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_505_514_closure_gate_phase_514.sh [--dry-run|--help]

Runs the Phase 514 window 505-514 closure gate.

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

resolve_window_state() {
  python3 - "$DECISION_LOG_PATH" <<'PY'
from pathlib import Path
import sys
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

text = Path(sys.argv[1]).read_text(encoding='utf-8')
rows = parse_decision_register_rows(text)
if 'CDL-053' in rows or 'CDL-058' in rows:
    print('invalid|unexpected_cdl_row_present')
elif rows.get('CDL-055', {}).get('status') != 'ratified':
    print('invalid|cdl_055_not_ratified')
elif rows.get('CDL-056', {}).get('status') != 'ratified':
    print('invalid|cdl_056_not_ratified')
elif rows.get('CDL-057', {}).get('status') == 'ratified':
    print('success|cdl_057_ratified')
elif 'CDL-057' not in rows:
    print('blocked|cdl_057_absent')
else:
    print('invalid|unexpected_epoch_boundary_state')
PY
}

write_snapshot() {
  local state="$1"
  local detail="$2"
  if [[ -z "$SNAPSHOT_PATH" ]]; then
    return 0
  fi
  python3 - "$SNAPSHOT_PATH" "$state" "$detail" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
payload = {
    'phase': 514,
    'window': '505-514',
    'state': sys.argv[2],
    'detail': sys.argv[3],
}
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
}

run_command() {
  local command="$1"
  shift || true
  env \
    -u ILC_PHASE_514_GATE_SELFTEST \
    -u ILC_PHASE_504_GATE_SELFTEST \
    -u ILC_PHASE_494_GATE_SELFTEST \
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
    -u ILC_PHASE_327_GATE_SELFTEST \
    -u ILC_PHASE_317_GATE_SELFTEST \
    -u ILC_PHASE_307_GATE_SELFTEST \
    -u ILC_PHASE_514_DECISION_LOG_PATH \
    -u ILC_PHASE_514_SNAPSHOT_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  case "$state" in
    success)
      echo "phase_514_window_state=success_path"
      ;;
    blocked)
      echo "phase_514_window_state=blocked_path"
      ;;
    invalid)
      echo "phase_514_window_state=invalid"
      echo "phase_514_window_state_details=${detail}"
      write_snapshot "$state" "$detail"
      return 1
      ;;
    *)
      echo "phase_514_window_state=invalid"
      echo "phase_514_window_state_details=unrecognized_state"
      write_snapshot "invalid" "unrecognized_state"
      return 1
      ;;
  esac

  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
        ILC_PHASE_504_GATE_SELFTEST=1 \
        ILC_PHASE_494_GATE_SELFTEST=1 \
        ILC_PHASE_484_GATE_SELFTEST=1 \
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
        ILC_PHASE_337_GATE_SELFTEST=1 \
        ILC_PHASE_327_GATE_SELFTEST=1 \
        ILC_PHASE_317_GATE_SELFTEST=1 \
        ILC_PHASE_307_GATE_SELFTEST=1
    elif [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_514_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done
  write_snapshot "$state" "$detail"
  echo "phase_514_verdict=pass"
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
