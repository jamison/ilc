#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_357_g8_constitution_cluster_a_window_348_357_closure_verification_gate_and_358_plus_handoff.md"
SNAPSHOT_PATH="${ILC_PHASE_357_SNAPSHOT_PATH:-out/monitoring/infrastructure_risk_snapshot_phase_316.json}"

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
  "python3 -m pytest tests/test_phase_348_sequence_lock.py tests/test_adm_003_role_resolution_339.py tests/test_adm_003_reference_agent_architecture_292.py tests/test_adm_003_7_plus_1_panel_role_354.py tests/test_cdl_034_ratification_349.py tests/test_cdl_035_ratification_350.py tests/test_cdl_036_ratification_351.py tests/test_cdl_037_ratification_352.py tests/test_cdl_038_ratification_353.py tests/test_reputation_and_agent_profile_adjoint_contract_345.py tests/test_node_schema_coherence_capsule_and_implementation_authorization_355.py tests/test_node_schema_implementation_readiness_356.py -q"
  "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_348_357_closure_gate_357.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_348_357_closure_gate_phase_357.sh [--dry-run|--help]

Runs the Phase 357 window 348-357 closure verification gate.

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
    echo "phase_357_snapshot_gate=failed"
    echo "phase_357_snapshot_details=phase:${snapshot_phase},preflight_scope:${snapshot_scope}"
    return 1
  fi

  case "$snapshot_verdict" in
    pass)
      echo "phase_357_snapshot_gate=passed"
      return 0
      ;;
    conditional)
      echo "phase_357_override_required=human"
      echo "phase_357_snapshot_gate=failed"
      return 3
      ;;
    blocked|*)
      echo "phase_357_snapshot_gate=failed"
      return 1
      ;;
  esac
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
      tmp_snapshot="$(mktemp "${tmpdir%/}/ilc_phase_357_snapshot_XXXXXX")"
      if env -u ILC_PHASE_316_FORCE_VERDICT -u ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE ILC_PHASE_316_SNAPSHOT_PATH="${tmp_snapshot}" bash -c "${commands[$idx]}"; then
        :
      else
        local rc=$?
        rm -f "${tmp_snapshot}"
        return "${rc}"
      fi
      rm -f "${tmp_snapshot}"
    elif [[ "$idx" -eq 4 ]]; then
      ILC_PHASE_357_GATE_SELFTEST=1 bash -c "${commands[$idx]}"
    else
      bash -c "${commands[$idx]}"
    fi
  done

  echo "phase_357_verdict=pass"
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
