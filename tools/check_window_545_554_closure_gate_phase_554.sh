#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_554_g8_window_545_554_closure_gate_and_handoff.md"
DECISION_LOG_PATH="${ILC_PHASE_554_DECISION_LOG_PATH:-docs/specs/ilc_constitutional_decision_log_v0.1.md}"
CAPSULE_PATH="${ILC_PHASE_554_CAPSULE_PATH:-docs/specs/ilc_antigravity_context_capsule_v2.8.md}"
SIM_PATH="${ILC_PHASE_554_SIM_PATH:-docs/specs/ilc_sim_multi_hop_01_centrality_calibration_552_v0.1.md}"
FLOOR_POLICY_PATH="${ILC_PHASE_554_FLOOR_POLICY_PATH:-docs/specs/ilc_signal_floor_policy_consistency_scoping_547_v0.1.md}"
GOSSIP_RUNTIME_PATH="${ILC_PHASE_554_CDL_GOSSIP_RUNTIME_PATH:-ilc_core/network/d2d/centrality_delta_gossip_runtime.py}"
PASSIVE_ECU_RUNTIME_PATH="${ILC_PHASE_554_PASSIVE_ECU_RUNTIME_PATH:-ilc_core/economics/passive_ecu_attribution_runtime.py}"
SNAPSHOT_PATH="${ILC_PHASE_554_SNAPSHOT_PATH:-}"
ALLOW_SNAPSHOT_WRITE="${ILC_PHASE_554_ALLOW_SNAPSHOT_WRITE:-0}"

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_window_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

lane_command="python3 -m pytest tests/test_phase_545_sequence_lock_and_carry_forward_intake.py tests/test_phase_546_epoch_boundary_commit_semantics.py tests/test_phase_547_signal_floor_policy_scoping.py tests/test_phase_548_centrality_delta_gossip_runtime.py tests/test_phase_549_centrality_delta_gossip_runtime_hardening.py tests/test_phase_550_passive_ecu_attribution_runtime.py tests/test_phase_551_passive_ecu_attribution_hardening.py tests/test_phase_552_sim_multi_hop_01_centrality.py tests/test_phase_553_coherence_report_and_capsule_v2_8.py -q"
cross_window_command="python3 -m pytest tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"

usage() {
  cat <<'USAGE'
Usage: tools/check_window_545_554_closure_gate_phase_554.sh [--dry-run|--help]

Runs the Phase 554 window 545-554 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

resolve_window_state() {
  python3 - "$DECISION_LOG_PATH" "$CAPSULE_PATH" "$SIM_PATH" "$FLOOR_POLICY_PATH" "$GOSSIP_RUNTIME_PATH" "$PASSIVE_ECU_RUNTIME_PATH" <<'PY'
from pathlib import Path
import sys
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

decision_log = Path(sys.argv[1])
capsule_path = Path(sys.argv[2])
sim_path = Path(sys.argv[3])
floor_policy_path = Path(sys.argv[4])
gossip_runtime_path = Path(sys.argv[5])
passive_runtime_path = Path(sys.argv[6])
rows = parse_decision_register_rows(decision_log.read_text(encoding='utf-8'))
sim_text = sim_path.read_text(encoding='utf-8') if sim_path.exists() else ''
floor_policy_text = floor_policy_path.read_text(encoding='utf-8') if floor_policy_path.exists() else ''
gossip_text = gossip_runtime_path.read_text(encoding='utf-8') if gossip_runtime_path.exists() else ''
passive_text = passive_runtime_path.read_text(encoding='utf-8') if passive_runtime_path.exists() else ''

if 'CDL-053' in rows:
    print('invalid|cdl_053_present')
elif rows.get('CDL-036', {}).get('status') != 'ratified':
    print('invalid|cdl_036_not_ratified')
elif rows.get('CDL-039', {}).get('status') != 'ratified':
    print('invalid|cdl_039_not_ratified')
elif rows.get('CDL-052', {}).get('status') != 'ratified':
    print('invalid|cdl_052_not_ratified')
elif rows.get('CDL-059', {}).get('status') != 'ratified':
    print('invalid|cdl_059_not_ratified')
elif rows.get('CDL-060', {}).get('status') != 'ratified':
    print('invalid|cdl_060_not_ratified')
elif 'CDL-061' in rows:
    print('invalid|cdl_061_present')
elif not capsule_path.exists():
    print('invalid|capsule_v2_8_missing')
elif 'sim_multi_hop_01_insufficient' not in sim_text and 'sim_multi_hop_01_sufficient' not in sim_text:
    print('invalid|sim_multi_hop_01_disposition_missing')
elif 'signal_floor_governance_adm_only' not in floor_policy_text and 'signal_floor_cdl_warranted' not in floor_policy_text:
    print('invalid|signal_floor_disposition_missing')
elif 'CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"' not in gossip_text:
    print('invalid|cdl_060_gossip_runtime_missing_or_mismatch')
elif 'PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"' not in passive_text:
    print('invalid|passive_ecu_runtime_missing_or_mismatch')
else:
    print('pass|window_545_554_complete')
PY
}

build_commands() {
  commands=(
    "python3 tools/validate_phase_prompt.py ${PROMPT_PATH}"
    "$lane_command"
    "$cross_window_command"
    "python3 tools/run_mutation_canary_phase_297.py"
    "python3 -m pytest tests/test_window_545_554_closure_gate_554.py -q"
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
  if [[ "$SNAPSHOT_PATH" == out/monitoring/* && "$ALLOW_SNAPSHOT_WRITE" != "1" ]]; then
    echo "snapshot_write_blocked_for_canonical_monitoring" >&2
    return 1
  fi
  python3 - "$SNAPSHOT_PATH" "$state" "$detail" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
payload = {
    'phase': 554,
    'window': '545-554',
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
    -u ILC_PHASE_554_GATE_SELFTEST \
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
    -u ILC_PHASE_554_DECISION_LOG_PATH \
    -u ILC_PHASE_554_CAPSULE_PATH \
    -u ILC_PHASE_554_SIM_PATH \
    -u ILC_PHASE_554_FLOOR_POLICY_PATH \
    -u ILC_PHASE_554_CDL_GOSSIP_RUNTIME_PATH \
    -u ILC_PHASE_554_PASSIVE_ECU_RUNTIME_PATH \
    -u ILC_PHASE_554_SNAPSHOT_PATH \
    -u ILC_PHASE_554_ALLOW_SNAPSHOT_WRITE \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_554_window_state=fail"
    echo "phase_554_window_state_details=${detail}"
    write_snapshot "fail" "$detail"
    return 1
  fi

  echo "phase_554_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
        ILC_PHASE_544_GATE_SELFTEST=1 \
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
      run_command "${commands[$idx]}" ILC_PHASE_554_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  write_snapshot "pass" "$detail"
  echo "phase_554_verdict=pass"
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
