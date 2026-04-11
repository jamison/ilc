#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_494_g8_window_485_494_closure_gate_and_handoff.md"
DECISION_LOG_PATH="${ILC_PHASE_494_DECISION_LOG_PATH:-docs/specs/ilc_constitutional_decision_log_v0.1.md}"

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
  "python3 -m pytest tests/test_phase_485_window_sequence_lock.py tests/test_phase_486_sim_010_validator_incentive_economics_contract_and_commissioning.py tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py tests/test_phase_488_cdl_045_validator_circuit_breaker_surface_runtime.py tests/test_phase_489_validator_economic_incentive_framework_opening_stub.py tests/test_phase_490_validator_economic_incentive_framework_prelock_hardening.py tests/test_phase_491_validator_economic_incentive_framework_ratification_evidence.py tests/test_phase_492_validator_staking_and_liveness_enforcement_opening_stub.py tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py -q"
  "python3 -m pytest tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_485_494_closure_gate_494.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_485_494_closure_gate_phase_494.sh [--dry-run|--help]

Runs the Phase 494 window 485-494 closure gate.

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
  python3 - "${ILC_PHASE_494_DECISION_LOG_PATH:-}" <<'PY'
import subprocess
import sys
from pathlib import Path
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

override_path = sys.argv[1]
if override_path:
    text = Path(override_path).read_text(encoding='utf-8')
else:
    # Read CDL at Phase 494 historical commit to preserve window-close CDL state
    result = subprocess.run(
        ['git', 'show', 'ed953403:docs/specs/ilc_constitutional_decision_log_v0.1.md'],
        capture_output=True, check=False, text=True,
    )
    text = result.stdout
rows = parse_decision_register_rows(text)
if 'CDL-053' in rows:
    print('invalid|cdl_053_present')
elif 'CDL-054' not in rows and 'CDL-055' not in rows:
    print('blocked|no_validator_cdls_opened')
elif rows.get('CDL-054', {}).get('status') == 'ratified' and rows.get('CDL-055', {}).get('status') == 'open':
    print('success|cdl_054_ratified_cdl_055_open')
else:
    print('invalid|unexpected_validator_cdl_state')
PY
}

run_command() {
  local command="$1"
  shift || true
  env \
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
    -u ILC_PHASE_494_DECISION_LOG_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state kind total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state kind <<<"${state_info}"
  case "$state" in
    success)
      echo "phase_494_window_state=success_path"
      ;;
    blocked)
      echo "phase_494_window_state=blocked_path"
      ;;
    invalid)
      echo "phase_494_window_state=invalid"
      echo "phase_494_window_state_details=${kind}"
      return 1
      ;;
    *)
      echo "phase_494_window_state=invalid"
      echo "phase_494_window_state_details=unrecognized_state"
      return 1
      ;;
  esac

  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
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
        ILC_PHASE_337_GATE_SELFTEST=1
    elif [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_494_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done
  echo "phase_494_verdict=pass"
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
