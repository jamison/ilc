#!/usr/bin/env bash
set -euo pipefail

CANONICAL_SNAPSHOT_PATH="out/monitoring/d2e_risk_snapshot_phase_564.json"
PROMPT_VALIDATION_COMMAND="python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_555_g8_window_555_564_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_556_g8_adr_023_signal_floor_invariant_update.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_557_g8_cdl_061_prelock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_558_g8_gossip_transport_adapter.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_559_g8_gossip_transport_hardening.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_560_g8_canary_transport_probes.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_561_g8_cdl_061_ratification.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_562_g8_gossip_peer_registry.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_563_g8_coherence_report_and_capsule_v2_9.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_564_g8_window_555_564_closure_gate_and_handoff.md"
LANE_TEST_COMMAND="python3 -m pytest tests/test_phase_555_window_555_564_sequence_lock.py tests/test_phase_556_adr_023_signal_floor_invariant.py tests/test_phase_557_cdl_061_prelock.py tests/test_phase_558_gossip_transport_adapter.py tests/test_phase_559_gossip_transport_hardening.py tests/test_phase_560_canary_transport_probes.py tests/test_phase_561_cdl_061_ratification.py tests/test_phase_562_gossip_peer_registry.py tests/test_phase_563_coherence_report_and_capsule.py -q"
CROSS_PHASE_COMMAND="python3 -m pytest tests/test_window_545_554_closure_gate_554.py tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q"
CANARY_COMMAND="python3 tools/run_mutation_canary_phase_297.py"
CLI_CONTRACT_COMMAND="python3 -m pytest tests/test_window_555_564_closure_gate_564.py -q"
WALKTHROUGH_COMMAND="python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
SNAPSHOT_PATH="${ILC_PHASE_564_SNAPSHOT_PATH:-$CANONICAL_SNAPSHOT_PATH}"
ALLOW_SNAPSHOT_WRITE="${ILC_PHASE_564_ALLOW_SNAPSHOT_WRITE:-0}"
SNAPSHOT_OVERRIDE_IS_SET=0
if [[ -n "${ILC_PHASE_564_SNAPSHOT_PATH+x}" ]]; then
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
Usage: tools/check_window_555_564_closure_gate_phase_564.sh [--dry-run|--help]

Runs the Phase 564 window 555-564 closure gate.

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
  python3 - <<'PY'
from pathlib import Path
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

rows = parse_decision_register_rows(Path('docs/specs/ilc_constitutional_decision_log_v0.1.md').read_text(encoding='utf-8'))
capsule_path = Path('docs/specs/ilc_antigravity_context_capsule_v2.9.md')
coherence_path = Path('docs/specs/ilc_integration_coherence_report_563_v0.1.md')
transport_path = Path('ilc_core/network/d2d/gossip_transport.py')
registry_path = Path('ilc_core/network/d2d/gossip_peer_registry.py')

coherence_text = coherence_path.read_text(encoding='utf-8') if coherence_path.exists() else ''
transport_text = transport_path.read_text(encoding='utf-8') if transport_path.exists() else ''
registry_text = registry_path.read_text(encoding='utf-8') if registry_path.exists() else ''

if rows.get('CDL-060', {}).get('status') != 'ratified':
    print('invalid|cdl_060_not_ratified')
elif rows.get('CDL-061', {}).get('status') != 'ratified':
    print('invalid|cdl_061_not_ratified')
elif rows.get('CDL-061', {}).get('ratified_phase') != '561':
    print('invalid|cdl_061_ratified_phase_mismatch')
elif not capsule_path.exists():
    print('invalid|capsule_v2_9_missing')
elif not coherence_path.exists():
    print('invalid|coherence_report_563_missing')
elif 'window_565_multi_machine_packaging_carry_forward' not in coherence_text:
    print('invalid|coherence_forward_obligation_missing')
elif 'GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_1572.v0.1"' not in transport_text:
    print('invalid|gossip_transport_runtime_missing_or_mismatch')
elif 'CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"' not in transport_text:
    print('invalid|gossip_transport_dep_not_ratified')
elif 'GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_1571.v0.1"' not in registry_text:
    print('invalid|gossip_peer_registry_missing_or_mismatch')
elif 'PEER_DISCOVERY_MODE = "static_v1"' not in registry_text:
    print('invalid|peer_discovery_mode_mismatch')
else:
    print('pass|window_555_564_complete')
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
    'phase': 564,
    'window': '555-564',
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
    -u ILC_PHASE_564_SNAPSHOT_PATH \
    -u ILC_PHASE_564_ALLOW_SNAPSHOT_WRITE \
    "$@" bash -c "$command"
}

run_full_gate() {
  local snapshot_info snapshot_state snapshot_detail
  local state_info state detail total idx

  snapshot_info="$(resolve_snapshot_verdict)"
  IFS='|' read -r snapshot_state snapshot_detail <<<"${snapshot_info}"
  echo "phase_564_snapshot_verdict=${snapshot_state}"
  echo "phase_564_snapshot_detail=${snapshot_detail}"
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
    echo "phase_564_window_state=fail"
    echo "phase_564_window_state_details=${detail}"
    write_snapshot "fail" "$detail"
    return 1
  fi

  echo "phase_564_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 2 ]]; then
      run_command "${commands[$idx]}" \
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
      run_command "${commands[$idx]}" ILC_PHASE_564_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  write_snapshot "pass" "$detail"
  echo "phase_564_verdict=pass"
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
