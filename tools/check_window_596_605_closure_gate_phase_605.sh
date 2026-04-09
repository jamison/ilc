#!/usr/bin/env bash
set -euo pipefail

PROMPT_VALIDATION_COMMAND='python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_596_g8_window_596_605_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_597_g8_genesis_governance_dilution_and_brake_semantics_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_598_g8_freshness_gate_provenance_and_genesis_exemption_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_599_g8_genesis_accrual_governor_provenance_reconciliation.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_600_g8_deterministic_genesis_economics_evidence_and_parameter_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_601_g8_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_602_g8_topological_exemption_boundary_and_public_tokenomics_statement.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_603_g8_genesis_carry_forward_synthesis_and_readiness_delta_addendum.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_604_g8_coherence_report_and_capsule_v3_2.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_605_g8_window_596_605_closure_gate_and_handoff.md'
GENESIS_CLOSURE_TEST_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_596_window_596_605_sequence_lock.py tests/test_phase_597_genesis_governance_dilution_and_brake_semantics_closure.py tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py tests/test_phase_599_genesis_accrual_governor_provenance_reconciliation.py tests/test_phase_600_deterministic_genesis_economics_evidence_and_parameter_closure.py tests/test_phase_601_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.py tests/test_phase_602_topological_exemption_boundary_and_public_tokenomics_statement.py -q'
SYNTHESIS_COHERENCE_TEST_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_603_genesis_carry_forward_synthesis_and_readiness_delta_addendum.py tests/test_phase_604_coherence_report_and_capsule_v3_2.py -q'
CANARY_COMMAND='python3 tools/run_mutation_canary_phase_297.py'
CLI_CONTRACT_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_window_596_605_closure_gate_605.py -q'
WALKTHROUGH_COMMAND='PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs'

labels=(
  "prompt_contract_validation"
  "genesis_closure_band_tests"
  "synthesis_and_coherence_tests"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_596_605_closure_gate_phase_605.sh [--dry-run|--help]

Runs the Phase 605 window 596-605 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

build_commands() {
  commands=(
    "$PROMPT_VALIDATION_COMMAND"
    "$GENESIS_CLOSURE_TEST_COMMAND"
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
  python3 - <<'PY'
from pathlib import Path

checks = [
    (Path('docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md'), 'window_596_605_preserves_585_595_frozen_public_and_rc_boundaries', 'phase_596_sequence_lock_missing'),
    (Path('docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md'), 'no_standing_genesis_governance_bonus_survives_closure', 'phase_597_governance_closure_missing'),
    (Path('docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md'), 'freshness_closure_must_not_reopen_phase_597_governance_rules', 'phase_598_freshness_closure_missing'),
    (Path('docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md'), 'genesis_fixed_tranche_against_cmax_is_authoritative_realization_surface', 'phase_599_accrual_closure_missing'),
    (Path('docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md'), 'phase_600_genesis_economics_parameter_closure_ok', 'phase_600_evidence_closure_missing'),
    (Path('docs/specs/ilc_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_601_v0.1.md'), 'phase_602_public_tokenomics_statement_must_consume_phase_601_capability_boundary', 'phase_601_capability_boundary_missing'),
    (Path('docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md'), 'phase_603_synthesis_must_consume_phase_597_602_closure_state', 'phase_602_tokenomics_boundary_missing'),
    (Path('docs/specs/ilc_genesis_carry_forward_synthesis_and_readiness_delta_addendum_603_v0.1.md'), 'phase_604_coherence_report_must_consume_phase_603_synthesis', 'phase_603_synthesis_missing'),
    (Path('docs/specs/ilc_integration_coherence_report_604_v0.1.md'), 'phase_605_closure_gate_must_consume_phase_604_coherence_state', 'phase_604_coherence_missing'),
    (Path('docs/specs/ilc_antigravity_context_capsule_v3.2.md'), 'Phase 605 is the only next authorized closure step for Window 596-605.', 'capsule_v3_2_missing_or_stale'),
    (Path('docs/specs/ilc_window_596_605_handoff_605_v0.1.md'), 'window_606_plus_or_next_approved_lane_is_next_authorized_strategic_boundary', 'handoff_605_missing_or_incomplete'),
]
for path, token, failure in checks:
    if not path.exists():
        print(f'fail|{failure}')
        raise SystemExit(0)
    text = path.read_text(encoding='utf-8')
    if token not in text:
        print(f'fail|{failure}')
        raise SystemExit(0)
print('pass|window_596_605_complete')
PY
}

run_command() {
  local command="$1"
  shift || true
  env -u ILC_PHASE_605_GATE_SELFTEST "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx

  # Prior gate pattern reference: tests/test_window_585_594_closure_gate_594.py
  # Read that earlier gate test before dropping any inherited expectation.
  # Do not assume naming or category shape without checking the earlier gate test directly.

  # Reject pass criteria based only on prompt counts, file counts, summary prose
  # without checked semantic assertions, synthesis/coherence as substitute for
  # closure-band completion, or silent omission of remaining later-lane defers.
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_605_window_state=fail"
    echo "phase_605_window_state_details=${detail}"
    return 1
  fi

  echo "phase_605_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 4 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_605_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  echo "phase_605_verdict=pass"
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
