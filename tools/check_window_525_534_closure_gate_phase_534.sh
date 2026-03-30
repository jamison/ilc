#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_534_g8_window_525_534_closure_gate_and_handoff.md"
DECISION_LOG_PATH="${ILC_PHASE_534_DECISION_LOG_PATH:-docs/specs/ilc_constitutional_decision_log_v0.1.md}"
SYNTHESIS_PATH="${ILC_PHASE_534_SYNTHESIS_PATH:-docs/specs/ilc_adr_0023_simulation_synthesis_528_v0.1.md}"
AESTHETIC_RUNTIME_PATH="${ILC_PHASE_534_RUNTIME_PATH:-ilc_core/epistemic/aesthetic_panel_runtime.py}"
SNAPSHOT_PATH="${ILC_PHASE_534_SNAPSHOT_PATH:-}"

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_window_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

lane_command_success="python3 -m pytest tests/test_phase_525_sequence_lock_and_carry_forward_intake.py tests/test_phase_526_sim_aesthetic_01_panel_composition.py tests/test_phase_527_sim_centrality_01_and_novelty_01.py tests/test_phase_528_adr_0023_simulation_synthesis.py tests/test_phase_529_cdl_059_opening_stub.py tests/test_phase_530_cdl_059_prelock_hardening.py tests/test_phase_531_cdl_059_ratification_evidence.py tests/test_phase_532_aesthetic_panel_runtime.py tests/test_phase_533_coherence_report_and_capsule_v2_6.py -q"
lane_command_blocked="python3 -m pytest tests/test_phase_525_sequence_lock_and_carry_forward_intake.py tests/test_phase_526_sim_aesthetic_01_panel_composition.py tests/test_phase_527_sim_centrality_01_and_novelty_01.py tests/test_phase_528_adr_0023_simulation_synthesis.py tests/test_phase_533_coherence_report_and_capsule_v2_6.py -q"
cross_window_command="python3 -m pytest tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"

usage() {
  cat <<'USAGE'
Usage: tools/check_window_525_534_closure_gate_phase_534.sh [--dry-run|--help]

Runs the Phase 534 window 525-534 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

resolve_window_state() {
  python3 - "$DECISION_LOG_PATH" "$SYNTHESIS_PATH" "$AESTHETIC_RUNTIME_PATH" <<'PY'
from pathlib import Path
import sys
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

decision_log = Path(sys.argv[1])
synthesis = Path(sys.argv[2])
runtime_path = Path(sys.argv[3])
rows = parse_decision_register_rows(decision_log.read_text(encoding='utf-8'))
text = synthesis.read_text(encoding='utf-8')
authorized = 'cdl_059_opening_authorized' in text
deferred = 'cdl_059_opening_deferred' in text
runtime_exists = runtime_path.exists()
cdl_059_status = rows.get('CDL-059', {}).get('status')

if 'CDL-053' in rows:
    print('invalid|cdl_053_present')
elif authorized == deferred:
    print('invalid|phase_528_disposition_invalid')
elif rows.get('CDL-055', {}).get('status') != 'ratified':
    print('invalid|cdl_055_not_ratified')
elif rows.get('CDL-056', {}).get('status') != 'ratified':
    print('invalid|cdl_056_not_ratified')
elif rows.get('CDL-057', {}).get('status') != 'ratified':
    print('invalid|cdl_057_not_ratified')
elif rows.get('CDL-058', {}).get('status') != 'ratified':
    print('invalid|cdl_058_not_ratified')
elif authorized and cdl_059_status == 'ratified' and runtime_exists:
    print('success|cdl_059_ratified_and_runtime_present')
elif deferred and cdl_059_status is None and not runtime_exists:
    print('blocked|cdl_059_opening_deferred')
elif authorized and cdl_059_status == 'ratified' and not runtime_exists:
    print('invalid|cdl_059_ratified_but_runtime_missing')
elif deferred and cdl_059_status is not None:
    print('invalid|deferred_path_has_cdl_059_artifact')
elif deferred and runtime_exists:
    print('invalid|deferred_path_has_runtime_artifact')
else:
    print('invalid|cdl_059_authorized_but_not_complete')
PY
}

build_commands() {
  local state="$1"
  local lane_command
  if [[ "$state" == "success" ]]; then
    lane_command="$lane_command_success"
  else
    lane_command="$lane_command_blocked"
  fi
  commands=(
    "python3 tools/validate_phase_prompt.py ${PROMPT_PATH}"
    "$lane_command"
    "$cross_window_command"
    "python3 tools/run_mutation_canary_phase_297.py"
    "python3 -m pytest tests/test_window_525_534_closure_gate_534.py -q"
    "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
  )
}

print_dry_run() {
  local state_info state detail total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  if [[ "$state" == "invalid" ]]; then
    state="success"
  fi
  build_commands "$state"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
  done
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
    'phase': 534,
    'window': '525-534',
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
    -u ILC_PHASE_534_GATE_SELFTEST \
    -u ILC_PHASE_524_GATE_SELFTEST \
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
    -u ILC_PHASE_534_DECISION_LOG_PATH \
    -u ILC_PHASE_534_SYNTHESIS_PATH \
    -u ILC_PHASE_534_RUNTIME_PATH \
    -u ILC_PHASE_534_SNAPSHOT_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands "$state"
  case "$state" in
    success)
      echo "phase_534_window_state=success_path"
      ;;
    blocked)
      echo "phase_534_window_state=blocked_path"
      ;;
    invalid)
      echo "phase_534_window_state=invalid"
      echo "phase_534_window_state_details=${detail}"
      write_snapshot "$state" "$detail"
      return 1
      ;;
    *)
      echo "phase_534_window_state=invalid"
      echo "phase_534_window_state_details=unrecognized_state"
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
        ILC_PHASE_524_GATE_SELFTEST=1 \
        ILC_PHASE_514_GATE_SELFTEST=1 \
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
      run_command "${commands[$idx]}" ILC_PHASE_534_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done
  write_snapshot "$state" "$detail"
  echo "phase_534_verdict=pass"
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
