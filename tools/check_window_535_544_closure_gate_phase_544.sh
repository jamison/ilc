#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_544_g8_window_535_544_closure_gate_and_handoff.md"
DECISION_LOG_PATH="${ILC_PHASE_544_DECISION_LOG_PATH:-docs/specs/ilc_constitutional_decision_log_v0.1.md}"
SIM_PATH="${ILC_PHASE_544_SIM_PATH:-docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md}"
RUNTIME_PATH="${ILC_PHASE_544_RUNTIME_PATH:-ilc_core/epistemic/reuse_centrality_runtime.py}"
CAPSULE_PATH="${ILC_PHASE_544_CAPSULE_PATH:-docs/specs/ilc_antigravity_context_capsule_v2.7.md}"
SNAPSHOT_PATH="${ILC_PHASE_544_SNAPSHOT_PATH:-}"

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_window_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

lane_command="python3 -m pytest tests/test_phase_535_sequence_lock_and_carry_forward_intake.py tests/test_phase_536_cdl_060_gossip_extension_scoping.py tests/test_phase_537_reuse_centrality_runtime_algorithm.py tests/test_phase_538_sim_centrality_02_gossip_propagation.py tests/test_phase_539_cdl_060_opening_stub.py tests/test_phase_540_cdl_060_prelock_hardening.py tests/test_phase_541_cdl_060_ratification_evidence.py tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py tests/test_phase_543_coherence_report_and_capsule_v2_7.py -q"
cross_window_command="python3 -m pytest tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"

usage() {
  cat <<'USAGE'
Usage: tools/check_window_535_544_closure_gate_phase_544.sh [--dry-run|--help]

Runs the Phase 544 window 535-544 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

resolve_window_state() {
  python3 - "$DECISION_LOG_PATH" "$SIM_PATH" "$RUNTIME_PATH" "$CAPSULE_PATH" <<'PY'
from pathlib import Path
import sys
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

decision_log = Path(sys.argv[1])
sim_path = Path(sys.argv[2])
runtime_path = Path(sys.argv[3])
capsule_path = Path(sys.argv[4])
rows = parse_decision_register_rows(decision_log.read_text(encoding='utf-8'))
sim_text = sim_path.read_text(encoding='utf-8') if sim_path.exists() else ''
runtime_text = runtime_path.read_text(encoding='utf-8') if runtime_path.exists() else ''

if rows.get('CDL-036', {}).get('status') != 'ratified':
    print('invalid|cdl_036_not_ratified')
elif rows.get('CDL-039', {}).get('status') != 'ratified':
    print('invalid|cdl_039_not_ratified')
elif rows.get('CDL-052', {}).get('status') != 'ratified':
    print('invalid|cdl_052_not_ratified')
elif rows.get('CDL-059', {}).get('status') != 'ratified':
    print('invalid|cdl_059_not_ratified')
elif rows.get('CDL-060', {}).get('status') != 'ratified':
    print('invalid|cdl_060_not_ratified')
elif not capsule_path.exists():
    print('invalid|capsule_v2_7_missing')
elif 'sim_passive_ecu_01_sufficient' not in sim_text:
    print('invalid|sim_passive_ecu_01_not_sufficient')
elif 'REUSE_CENTRALITY_RUNTIME_VERSION = "reuse_centrality_runtime_537.v0.1"' not in runtime_text:
    print('invalid|reuse_centrality_runtime_version_mismatch')
elif 'COMPUTATION_BACKEND_V1 = "incremental_direct_use_v1"' not in runtime_text:
    print('invalid|reuse_centrality_runtime_not_advanced')
else:
    print('pass|window_535_544_complete')
PY
}

build_commands() {
  commands=(
    "python3 tools/validate_phase_prompt.py ${PROMPT_PATH}"
    "$lane_command"
    "$cross_window_command"
    "python3 tools/run_mutation_canary_phase_297.py"
    "python3 -m pytest tests/test_window_535_544_closure_gate_544.py -q"
    "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
  )
}

print_dry_run() {
  local total idx
  build_commands
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
    'phase': 544,
    'window': '535-544',
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
    -u ILC_PHASE_544_GATE_SELFTEST \
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
    -u ILC_PHASE_544_DECISION_LOG_PATH \
    -u ILC_PHASE_544_SIM_PATH \
    -u ILC_PHASE_544_RUNTIME_PATH \
    -u ILC_PHASE_544_CAPSULE_PATH \
    -u ILC_PHASE_544_SNAPSHOT_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_544_window_state=fail"
    echo "phase_544_window_state_details=${detail}"
    write_snapshot "fail" "$detail"
    return 1
  fi

  echo "phase_544_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
        ILC_PHASE_534_GATE_SELFTEST=1 \
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
      run_command "${commands[$idx]}" ILC_PHASE_544_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  write_snapshot "pass" "$detail"
  echo "phase_544_verdict=pass"
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
