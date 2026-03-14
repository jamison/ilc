#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_413_g8_d2e_window_402_413_closure_gate_and_414_plus_handoff.md"
SNAPSHOT_PATH="${ILC_PHASE_413_SNAPSHOT_PATH:-out/monitoring/infrastructure_risk_snapshot_phase_316.json}"

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
  "python3 -m pytest tests/test_phase_402_cdl_042_and_cdl_045_opening.py tests/test_phase_403_cdl_042_prelock_hardening.py tests/test_phase_404_cdl_045_prelock_hardening.py tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py tests/test_phase_406_sim_008_commissioning.py tests/test_phase_407_cdl_042_ratification.py tests/test_phase_408_cdl_045_ratification.py tests/test_phase_409_cdl_046_ratification.py tests/test_phase_410_d2e_agent_identity_runtime.py tests/test_phase_411_d2e_timed_out_lifecycle_runtime.py tests/test_phase_412_coherence_and_capsule_v1_5.py -q"
  "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_392_401_closure_gate_401.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_402_413_closure_gate_413.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_402_413_closure_gate_phase_413.sh [--dry-run|--help]

Runs the Phase 413 window 402-413 closure verification gate.

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

read_snapshot_fields() {
  python3 - "$SNAPSHOT_PATH" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit("missing_snapshot")
obj = json.loads(path.read_text(encoding="utf-8"))
phase = str(obj.get("phase", ""))
is_preflight = obj.get("preflight_scope") is True
verdict = str(obj.get("severity_summary", {}).get("verdict", ""))
scope = "true" if is_preflight else "false"
print(f"{phase}|{scope}|{verdict}")
PY
}

resolve_gate_verdict() {
  local snapshot_phase="$1"
  local snapshot_scope="$2"
  local snapshot_verdict="$3"

  if [[ "$snapshot_phase" != "316" || "$snapshot_scope" != "true" ]]; then
    echo "phase_413_snapshot_gate=failed"
    echo "phase_413_snapshot_details=phase:${snapshot_phase},preflight_scope:${snapshot_scope}"
    return 1
  fi

  case "$snapshot_verdict" in
    pass)
      echo "phase_413_snapshot_gate=passed"
      return 0
      ;;
    conditional)
      echo "phase_413_override_required=human"
      echo "phase_413_snapshot_gate=failed"
      return 3
      ;;
    blocked|*)
      echo "phase_413_snapshot_gate=failed"
      return 1
      ;;
  esac
}

run_sanitized_command() {
  local command="$1"
  env \
    -u ILC_PHASE_413_SNAPSHOT_PATH \
    -u ILC_PHASE_401_SNAPSHOT_PATH \
    -u ILC_PHASE_316_SNAPSHOT_PATH \
    -u ILC_PHASE_316_FORCE_VERDICT \
    -u ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE \
    -u ILC_PHASE_413_GATE_SELFTEST \
    -u ILC_PHASE_401_GATE_SELFTEST \
    -u ILC_PHASE_391_GATE_SELFTEST \
    -u ILC_PHASE_377_GATE_SELFTEST \
    -u ILC_PHASE_367_GATE_SELFTEST \
    -u ILC_PHASE_357_GATE_SELFTEST \
    -u ILC_PHASE_347_GATE_SELFTEST \
    bash -c "$command"
}

run_full_gate() {
  local snapshot_info
  snapshot_info="$(read_snapshot_fields)"
  local snapshot_phase snapshot_scope snapshot_verdict
  IFS='|' read -r snapshot_phase snapshot_scope snapshot_verdict <<<"${snapshot_info}"

  local verdict_rc=0
  resolve_gate_verdict "$snapshot_phase" "$snapshot_scope" "$snapshot_verdict" || verdict_rc=$?
  if [[ "$verdict_rc" -ne 0 ]]; then
    return "$verdict_rc"
  fi

  local total="${#labels[@]}"
  local idx
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"

    if [[ "$idx" -eq 2 ]]; then
      local tmpdir tmp_snapshot
      tmpdir="${TMPDIR:-/tmp}"
      tmp_snapshot="$(mktemp "${tmpdir%/}/ilc_phase_413_snapshot_XXXXXX")"
      if env \
        -u ILC_PHASE_413_SNAPSHOT_PATH \
        -u ILC_PHASE_401_SNAPSHOT_PATH \
        -u ILC_PHASE_316_SNAPSHOT_PATH \
        -u ILC_PHASE_316_FORCE_VERDICT \
        -u ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE \
        -u ILC_PHASE_413_GATE_SELFTEST \
        -u ILC_PHASE_401_GATE_SELFTEST \
        -u ILC_PHASE_391_GATE_SELFTEST \
        -u ILC_PHASE_377_GATE_SELFTEST \
        -u ILC_PHASE_367_GATE_SELFTEST \
        -u ILC_PHASE_357_GATE_SELFTEST \
        -u ILC_PHASE_347_GATE_SELFTEST \
        ILC_PHASE_316_SNAPSHOT_PATH="${tmp_snapshot}" \
        ILC_PHASE_401_GATE_SELFTEST=1 \
        ILC_PHASE_391_GATE_SELFTEST=1 \
        ILC_PHASE_377_GATE_SELFTEST=1 \
        ILC_PHASE_367_GATE_SELFTEST=1 \
        ILC_PHASE_357_GATE_SELFTEST=1 \
        ILC_PHASE_347_GATE_SELFTEST=1 \
        bash -c "${commands[$idx]}"; then
        :
      else
        local rc=$?
        rm -f "${tmp_snapshot}"
        return "${rc}"
      fi
      rm -f "${tmp_snapshot}"
    elif [[ "$idx" -eq 4 ]]; then
      env \
        -u ILC_PHASE_413_SNAPSHOT_PATH \
        -u ILC_PHASE_401_SNAPSHOT_PATH \
        -u ILC_PHASE_316_SNAPSHOT_PATH \
        -u ILC_PHASE_316_FORCE_VERDICT \
        -u ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE \
        -u ILC_PHASE_401_GATE_SELFTEST \
        -u ILC_PHASE_391_GATE_SELFTEST \
        -u ILC_PHASE_377_GATE_SELFTEST \
        -u ILC_PHASE_367_GATE_SELFTEST \
        -u ILC_PHASE_357_GATE_SELFTEST \
        -u ILC_PHASE_347_GATE_SELFTEST \
        ILC_PHASE_413_GATE_SELFTEST=1 \
        bash -c "${commands[$idx]}"
    else
      run_sanitized_command "${commands[$idx]}"
    fi
  done

  echo "phase_413_verdict=pass"
  return 0
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
exit $?
