#!/usr/bin/env bash
set -euo pipefail

CANONICAL_SNAPSHOT_PATH="out/monitoring/infrastructure_risk_snapshot_phase_574.json"
PHASE_572_WALKTHROUGH_PATH="${ILC_PHASE_574_PHASE_572_WALKTHROUGH_PATH:-docs/phases/phase_572_g8_three_machine_smoke_harness_walkthrough.md}"
PROMPT_VALIDATION_COMMAND="python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_565_g8_window_565_574_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_566_g8_transport_operationalization_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_567_g8_genesis_package_lifecycle_scoping.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_568_g8_real_http_transport_wrapper_runtime.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_569_g8_transport_hardening_and_http2_fallback.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_570_g8_static_peer_config_json_loader_and_startup_wiring.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_571_g8_venv_systemd_packaging_and_lifecycle_runtime.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_572_g8_three_machine_smoke_harness.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_573_g8_coherence_report_and_capsule_v3_0.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_574_g8_window_565_574_closure_gate_and_handoff.md"
LANE_TEST_COMMAND="python3 -m pytest tests/test_phase_565_window_565_574_sequence_lock.py tests/test_phase_566_transport_operationalization_boundary_lock.py tests/test_phase_567_genesis_package_lifecycle_scoping.py tests/test_phase_568_real_http_transport_wrapper_runtime.py tests/test_phase_569_transport_hardening_and_http2_fallback.py tests/test_phase_570_static_peer_config_json_loader_and_startup_wiring.py tests/test_phase_571_venv_systemd_packaging_and_lifecycle_runtime.py tests/test_phase_572_three_machine_smoke_harness.py tests/test_phase_573_coherence_report_and_capsule_v3_0.py -q"
CROSS_PHASE_COMMAND="python3 -m pytest tests/test_window_555_564_closure_gate_564.py tests/test_window_545_554_closure_gate_554.py tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"
CANARY_COMMAND="python3 tools/run_mutation_canary_phase_297.py"
CLI_CONTRACT_COMMAND="python3 -m pytest tests/test_window_565_574_closure_gate_574.py -q"
WALKTHROUGH_COMMAND="python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
SNAPSHOT_PATH="${ILC_PHASE_574_SNAPSHOT_PATH:-$CANONICAL_SNAPSHOT_PATH}"
ALLOW_SNAPSHOT_WRITE="${ILC_PHASE_574_ALLOW_SNAPSHOT_WRITE:-0}"
SNAPSHOT_OVERRIDE_IS_SET=0
if [[ -n "${ILC_PHASE_574_SNAPSHOT_PATH+x}" ]]; then
  SNAPSHOT_OVERRIDE_IS_SET=1
fi

labels=(
  "prompt_contract_validation"
  "lane_contract_tests"
  "cross_phase_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_565_574_closure_gate_phase_574.sh [--dry-run|--help]

Runs the Phase 574 window 565-574 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

build_commands() {
  commands=(
    "$PROMPT_VALIDATION_COMMAND"
    "$LANE_TEST_COMMAND"
    "$CROSS_PHASE_COMMAND"
    "$CANARY_COMMAND"
    "$CLI_CONTRACT_COMMAND"
    "$WALKTHROUGH_COMMAND"
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

resolve_snapshot_verdict() {
  if [[ ! -e "$SNAPSHOT_PATH" ]]; then
    echo "pass|snapshot_missing_live_read_only"
    return 0
  fi
  python3 - "$SNAPSHOT_PATH" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    payload = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    print('blocked|snapshot_read_error')
    raise SystemExit(0)

verdict = str(payload.get('verdict', payload.get('state', 'pass'))).strip().lower() or 'pass'
detail = str(payload.get('detail', 'snapshot_verdict_not_provided')).strip() or 'snapshot_verdict_not_provided'
if verdict not in {'pass', 'conditional', 'blocked'}:
    print('blocked|snapshot_verdict_invalid')
else:
    print(f'{verdict}|{detail}')
PY
}

resolve_window_state() {
  python3 - "$PHASE_572_WALKTHROUGH_PATH" <<'PY'
import sys
from pathlib import Path
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

walkthrough_path = Path(sys.argv[1])
rows = parse_decision_register_rows(Path('docs/specs/ilc_constitutional_decision_log_v0.1.md').read_text(encoding='utf-8'))
capsule_path = Path('docs/specs/ilc_antigravity_context_capsule_v3.0.md')
coherence_path = Path('docs/specs/ilc_integration_coherence_report_573_v0.1.md')
transport_path = Path('ilc_core/network/d2d/http_gossip_transport_runtime.py')
startup_path = Path('ilc_core/node/node_startup_runtime.py')
service_path = Path('tools/run_ilc_node_service_v1.py')
unit_path = Path('deploy/systemd/ilc-node-v1.service')
smoke_script_path = Path('tools/run_three_machine_smoke_phase_572.sh')
canary_path = Path('tools/run_mutation_canary_phase_297.py')

coherence_text = coherence_path.read_text(encoding='utf-8') if coherence_path.exists() else ''
capsule_text = capsule_path.read_text(encoding='utf-8') if capsule_path.exists() else ''
transport_text = transport_path.read_text(encoding='utf-8') if transport_path.exists() else ''
startup_text = startup_path.read_text(encoding='utf-8') if startup_path.exists() else ''
service_text = service_path.read_text(encoding='utf-8') if service_path.exists() else ''
walkthrough_text = walkthrough_path.read_text(encoding='utf-8') if walkthrough_path.exists() else ''
canary_text = canary_path.read_text(encoding='utf-8') if canary_path.exists() else ''

if rows.get('CDL-061', {}).get('status') != 'ratified':
    print('invalid|cdl_061_not_ratified')
elif not capsule_path.exists():
    print('invalid|capsule_v3_0_missing')
elif not coherence_path.exists():
    print('invalid|coherence_report_573_missing')
elif 'three_machine_transport_wrapper_lane_complete' not in coherence_text:
    print('invalid|transport_wrapper_lane_incomplete')
elif 'json_static_peer_config_and_startup_lane_complete' not in coherence_text:
    print('invalid|startup_lane_incomplete')
elif 'venv_systemd_testbed_packaging_lane_complete' not in coherence_text:
    print('invalid|packaging_lane_incomplete')
elif 'three_machine_smoke_gate_complete' not in coherence_text:
    print('invalid|smoke_gate_incomplete')
elif not walkthrough_path.exists():
    print('invalid|phase_572_walkthrough_missing')
elif 'phase_572_real_three_machine_operator_proof_recorded' not in walkthrough_text:
    print('invalid|phase_572_operator_proof_missing')
elif 'HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_568.v0.1"' not in transport_text:
    print('invalid|transport_runtime_missing_or_mismatch')
elif 'NODE_STARTUP_RUNTIME_VERSION = "node_startup_runtime_570.v0.1"' not in startup_text:
    print('invalid|startup_runtime_missing_or_mismatch')
elif 'NODE_SERVICE_READY' not in service_text or 'NODE_SERVICE_FAILED' not in service_text:
    print('invalid|service_runner_markers_missing')
elif not unit_path.exists():
    print('invalid|systemd_unit_missing')
elif not smoke_script_path.exists():
    print('invalid|smoke_harness_missing')
elif canary_text.count('Probe(') != 9:
    print('invalid|canary_probe_count_mismatch')
elif 'Window 575-584' not in capsule_text:
    print('invalid|capsule_forward_priority_missing')
else:
    print('pass|window_565_574_complete')
PY
}

write_snapshot() {
  local state="$1"
  local detail="$2"
  if [[ "$SNAPSHOT_OVERRIDE_IS_SET" != "1" && "$ALLOW_SNAPSHOT_WRITE" != "1" ]]; then
    return 0
  fi
  if [[ "$SNAPSHOT_PATH" == out/monitoring/* && "$ALLOW_SNAPSHOT_WRITE" != "1" ]]; then
    echo 'snapshot_write_blocked_for_canonical_monitoring' >&2
    return 1
  fi
  python3 - "$SNAPSHOT_PATH" "$state" "$detail" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
payload = {
    'phase': 574,
    'window': '565-574',
    'verdict': sys.argv[2],
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
    -u ILC_PHASE_574_GATE_SELFTEST \
    -u ILC_PHASE_564_GATE_SELFTEST \
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
    -u ILC_PHASE_574_SNAPSHOT_PATH \
    -u ILC_PHASE_574_ALLOW_SNAPSHOT_WRITE \
    -u ILC_PHASE_574_PHASE_572_WALKTHROUGH_PATH \
    "$@" bash -c "$command"
}

run_full_gate() {
  local snapshot_info snapshot_state snapshot_detail
  local state_info state detail total idx

  # Reject pass criteria based only on manifest counts, file counts,
  # placeholder mode output, or local-only smoke output without the recorded
  # phase_572_real_three_machine_operator_proof_recorded token.
  snapshot_info="$(resolve_snapshot_verdict)"
  IFS='|' read -r snapshot_state snapshot_detail <<<"${snapshot_info}"
  echo "phase_574_snapshot_verdict=${snapshot_state}"
  echo "phase_574_snapshot_detail=${snapshot_detail}"
  if [[ "$snapshot_state" == "conditional" ]]; then
    return 3
  fi
  if [[ "$snapshot_state" == "blocked" ]]; then
    return 1
  fi

  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_574_window_state=fail"
    echo "phase_574_window_state_details=${detail}"
    write_snapshot "fail" "$detail"
    return 1
  fi

  echo "phase_574_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      # Read each prior gate test file before omitting a selftest flag. Older
      # windows do not use perfectly consistent naming.
      run_command "${commands[$idx]}" \
        ILC_PHASE_564_GATE_SELFTEST=1 \
        ILC_PHASE_554_GATE_SELFTEST=1 \
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
      run_command "${commands[$idx]}" ILC_PHASE_574_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  write_snapshot "pass" "$detail"
  echo "phase_574_verdict=pass"
}

main() {
  case "${1:-}" in
    --dry-run)
      print_dry_run
      ;;
    --help|-h)
      usage
      ;;
    "")
      run_full_gate
      ;;
    *)
      usage >&2
      return 2
      ;;
  esac
}

main "$@"
