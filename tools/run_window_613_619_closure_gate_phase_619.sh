#!/usr/bin/env bash
set -euo pipefail

PROMPT_VALIDATION_COMMAND='.venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_613_g8_window_613_619_sequence_lock.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_614_g8_public_init_admission_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_615_g8_ecu_to_ilc_lifecycle_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_616_g8_public_receipt_schema_and_query_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_617_g8_public_wallet_surface_contract_spec.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_618_g8_mvp_gate_synthesis_and_coherence_report.md && .venv/bin/python3.14 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_619_g8_window_613_619_closure_gate_and_handoff.md'
MVP_SPEC_BAND_TEST_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_614_public_init_admission_contract_spec.py tests/test_phase_615_ecu_to_ilc_lifecycle_contract_spec.py tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py tests/test_phase_617_public_wallet_surface_contract_spec.py -q'
SYNTHESIS_COHERENCE_TEST_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_613_window_613_619_sequence_lock.py tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py -q'
CANARY_COMMAND='.venv/bin/python3.14 tools/run_mutation_canary_phase_297.py'
CLI_CONTRACT_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_619_window_613_619_closure_gate.py -q'
WALKTHROUGH_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs'

labels=(
  "prompt_contract_validation"
  "mvp_spec_band_tests"
  "synthesis_and_coherence_tests"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

usage() {
  cat <<'USAGE'
Usage: tools/run_window_613_619_closure_gate_phase_619.sh [--dry-run|--help]

Runs the Phase 619 window 613-619 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

build_commands() {
  commands=(
    "$PROMPT_VALIDATION_COMMAND"
    "$MVP_SPEC_BAND_TEST_COMMAND"
    "$SYNTHESIS_COHERENCE_TEST_COMMAND"
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

resolve_window_state() {
  .venv/bin/python3.14 - <<'PY'
from pathlib import Path

checks = [
    (
        Path('docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md'),
        'mvp_gate_spec_lane_window_613_619_primary_gate',
        'phase_613_sequence_lock_missing',
    ),
    (
        Path('docs/specs/ilc_public_init_admission_contract_spec_614_v0.1.md'),
        'public_init_admission_contract_spec_614_locked',
        'phase_614_init_spec_missing',
    ),
    (
        Path('docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md'),
        'ecu_to_ilc_lifecycle_contract_spec_615_locked',
        'phase_615_lifecycle_spec_missing',
    ),
    (
        Path('docs/specs/ilc_public_receipt_schema_and_query_contract_spec_616_v0.1.md'),
        'public_receipt_schema_and_query_contract_spec_locked',
        'phase_616_receipt_spec_missing',
    ),
    (
        Path('docs/specs/ilc_public_wallet_surface_contract_spec_617_v0.1.md'),
        'public_wallet_surface_contract_spec_locked',
        'phase_617_wallet_spec_missing',
    ),
    (
        Path('docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md'),
        'mvp_gate_synthesis_verdict_issued',
        'phase_618_coherence_missing',
    ),
    (
        Path('docs/specs/ilc_antigravity_context_capsule_v3.3.md'),
        'option_d_active_posture_inherited_from_phase_612',
        'capsule_v3_3_missing_or_stale',
    ),
    (
        Path('docs/specs/ilc_window_613_619_handoff_619_v0.1.md'),
        'window_613_619_handoff_619_v0_1_closed',
        'handoff_619_missing_or_incomplete',
    ),
    (
        Path('docs/specs/ilc_window_613_619_handoff_619_v0.1.md'),
        'handoff_records_option_b_graduation_checklist_delta',
        'handoff_619_missing_option_b_delta',
    ),
]

for path, token, failure in checks:
    if not path.exists():
        print(f'fail|{failure}')
        raise SystemExit(0)
    text = path.read_text(encoding='utf-8')
    if token not in text:
        print(f'fail|{failure}')
        raise SystemExit(0)

coherence_text = Path(
    'docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md'
).read_text(encoding='utf-8')
if (
    'mvp_gate_spec_verdict=pass' not in coherence_text
    and 'mvp_gate_spec_verdict=conditional' not in coherence_text
):
    print('fail|phase_618_verdict_missing')
    raise SystemExit(0)

print('pass|window_613_619_complete')
PY
}

run_command() {
  local command="$1"
  shift || true
  env -u ILC_PHASE_619_GATE_SELFTEST "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx

  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_619_window_state=fail"
    echo "phase_619_window_state_details=${detail}"
    return 1
  fi

  echo "phase_619_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_619_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  echo "phase_619_verdict=pass"
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
