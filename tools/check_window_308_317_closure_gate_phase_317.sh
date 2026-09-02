#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/antigravity_tasks/antigravity_prompt__phase_317_g8_constitution_cluster_a_window_308_317_closure_verification_gate_and_318_plus_handoff.md"
SNAPSHOT_PATH="${ILC_PHASE_317_SNAPSHOT_PATH:-out/monitoring/infrastructure_risk_snapshot_phase_316.json}"

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
  "python3 -m pytest tests/test_phase_308_sequence_lock.py tests/test_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309.py tests/test_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311.py tests/test_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313.py tests/test_infrastructure_economic_risk_monitoring_update_315.py -q"
  "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_mutation_canary_phase_297.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_composed_preflight_316.py -q"
  "python3 tools/run_mutation_canary_phase_297.py"
  "python3 -m pytest tests/test_window_308_317_closure_gate_317.py -q"
  "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q"
)

PYTHON_BIN="${PYTHON:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  if [[ -x ".venv/bin/python3" ]]; then
    PYTHON_BIN=".venv/bin/python3"
  elif [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

PYTHON_DIR="$(dirname "${PYTHON_BIN}")"
if [[ "${PYTHON_DIR}" != "." ]]; then
  export PATH="${PYTHON_DIR}:${PATH}"
fi

usage() {
  cat <<'USAGE'
Usage: tools/check_window_308_317_closure_gate_phase_317.sh [--dry-run|--help]

Runs the Phase 317 window 308-317 closure verification gate.

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
    echo "phase_317_snapshot_gate=failed"
    echo "phase_317_snapshot_details=phase:${snapshot_phase},preflight_scope:${snapshot_scope}"
    return 1
  fi

  case "$snapshot_verdict" in
    pass)
      echo "phase_317_snapshot_gate=passed"
      return 0
      ;;
    conditional)
      echo "phase_317_override_required=human"
      echo "phase_317_snapshot_gate=failed"
      return 3
      ;;
    blocked|*)
      echo "phase_317_snapshot_gate=failed"
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
      if [[ "${ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE:-0}" == "1" ]]; then
        bash -c "${commands[$idx]}"
      else
        local tmp_snapshot
        tmp_snapshot="$(mktemp "${TMPDIR%/}/ilc_phase_317_snapshot_XXXXXX")"
        if ILC_PHASE_316_GATE_SELFTEST=1 ILC_PHASE_316_SNAPSHOT_PATH="${tmp_snapshot}" bash -c "${commands[$idx]}"; then
          :
        else
          local rc=$?
          rm -f "${tmp_snapshot}"
          return "${rc}"
        fi
        rm -f "${tmp_snapshot}"
      fi
    elif [[ "$idx" -eq 4 ]]; then
      ILC_PHASE_317_GATE_SELFTEST=1 bash -c "${commands[$idx]}"
    else
      bash -c "${commands[$idx]}"
    fi
  done

  echo "phase_317_verdict=pass"
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
