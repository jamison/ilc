#!/usr/bin/env bash
set -euo pipefail

PROMPT_VALIDATION_COMMAND="python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_585_g8_window_585_594_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_586_g8_public_receipt_representation_cluster_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_587_g8_public_identity_activation_namespace_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_588_g8_public_quorum_eligibility_genesis_lineage_authority_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_589_g8_settlement_linked_public_legitimacy_payout_traceability_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_590_g8_genesis_authority_sunset_fork_legitimacy_coherence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_591_g8_public_runtime_integration_over_receipt_boundary.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_592_g8_public_release_claim_and_operator_honesty_package.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_593_g8_coherence_report_and_public_rc_capsule_v3_1.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_594_g8_window_585_594_closure_gate_and_handoff.md"
CONSTITUTIONAL_TEST_COMMAND="python3 -m pytest tests/test_phase_585_window_585_594_sequence_lock.py tests/test_phase_586_public_receipt_representation_cluster_lock.py tests/test_phase_587_public_identity_activation_and_namespace_boundary_lock.py tests/test_phase_588_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock.py tests/test_phase_589_settlement_linked_public_legitimacy_and_payout_traceability_lock.py tests/test_phase_590_genesis_authority_sunset_and_fork_legitimacy_coherence_lock.py -q"
INTEGRATION_TEST_COMMAND="python3 -m pytest tests/test_phase_591_public_runtime_integration_over_receipt_boundary.py tests/test_phase_592_public_release_claim_and_operator_honesty_package.py tests/test_phase_593_coherence_report_and_public_rc_capsule_v3_1.py -q"
TOOLCHAIN_REGRESSION_COMMAND='python3 -m pytest tests/test_testbed_control_surface.py -q -k "readiness_delta or release_claim or release_candidate_manifest_records_optional_economic_state"'
CANARY_COMMAND="python3 tools/run_mutation_canary_phase_297.py"
CLI_CONTRACT_COMMAND="python3 -m pytest tests/test_window_585_594_closure_gate_594.py -q"
WALKTHROUGH_COMMAND="python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs"

labels=(
  "prompt_contract_validation"
  "constitutional_closure_band_tests"
  "public_rc_integration_band_tests"
  "public_rc_toolchain_regression"
  "mutation_canary"
  "closure_gate_cli_contract"
  "walkthrough_hygiene"
)

usage() {
  cat <<'USAGE'
Usage: tools/check_window_585_594_closure_gate_phase_594.sh [--dry-run|--help]

Runs the Phase 594 window 585-594 closure gate.

Options:
  --dry-run   Print deterministic category + command lines and exit 0.
  --help      Print this help and exit 0.
USAGE
}

build_commands() {
  commands=(
    "$PROMPT_VALIDATION_COMMAND"
    "$CONSTITUTIONAL_TEST_COMMAND"
    "$INTEGRATION_TEST_COMMAND"
    "$TOOLCHAIN_REGRESSION_COMMAND"
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
    (Path('docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md'), 'public_receipt_representation_cluster_locked', 'phase_586_receipt_cluster_missing'),
    (Path('docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md'), 'public_identity_activation_requires_settled_admission_or_stake_binding_receipt', 'phase_587_identity_boundary_missing'),
    (Path('docs/specs/ilc_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock_588_v0.1.md'), 'public_quorum_authority_requires_eligibility_receipt_or_proof', 'phase_588_quorum_boundary_missing'),
    (Path('docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md'), 'settlement_linked_public_legitimacy_requires_settled_receipt_chain', 'phase_589_settlement_boundary_missing'),
    (Path('docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md'), 'genesis_rooted_artifact_lineage_required_for_canonical_public_network', 'phase_590_genesis_boundary_missing'),
    (Path('docs/specs/ilc_public_runtime_integration_over_receipt_boundary_591_v0.1.md'), 'public_runtime_integration_must_consume_frozen_587_590_boundary', 'phase_591_runtime_boundary_missing'),
    (Path('docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md'), 'public_release_claim_must_bind_to_phase_591_runtime_boundary', 'phase_592_honesty_package_missing'),
    (Path('docs/specs/ilc_integration_coherence_report_593_v0.1.md'), 'phase_594_closure_gate_must_consume_phase_593_coherence_state', 'phase_593_coherence_missing'),
    (Path('docs/specs/ilc_antigravity_context_capsule_v3.1.md'), 'Phase 594 is the next authorized phase.', 'capsule_v3_1_missing_or_stale'),
    (Path('docs/specs/ilc_window_585_594_handoff_594_v0.1.md'), 'window_595_plus_is_next_authorized_strategic_boundary', 'handoff_594_missing_or_incomplete'),
]
for path, token, failure in checks:
    if not path.exists():
        print(f'fail|{failure}')
        raise SystemExit(0)
    text = path.read_text(encoding='utf-8')
    if token not in text:
        print(f'fail|{failure}')
        raise SystemExit(0)
print('pass|window_585_594_complete')
PY
}

run_command() {
  local command="$1"
  shift || true
  env \
    -u ILC_PHASE_594_GATE_SELFTEST \
    "$@" bash -c "$command"
}

run_full_gate() {
  local state_info state detail total idx

  # Prior gate pattern reference: tests/test_window_565_574_closure_gate_574.py
  # Read that earlier gate test before dropping any inherited expectation.
  # Do not assume naming or category shape without checking the earlier gate test directly.

  # Reject pass criteria based only on prompt counts, file counts, manifest presence without checked semantic assertions, honesty-package-only states, or silent omission of the Genesis carry-forward queue and separate capability-proof lane.
  state_info="$(resolve_window_state)"
  IFS='|' read -r state detail <<<"${state_info}"
  build_commands

  if [[ "$state" != "pass" ]]; then
    echo "phase_594_window_state=fail"
    echo "phase_594_window_state_details=${detail}"
    return 1
  fi

  echo "phase_594_window_state=pass"
  total="${#labels[@]}"
  for idx in "${!labels[@]}"; do
    printf '[%s/%s] %s\n' "$((idx + 1))" "$total" "${labels[$idx]}"
    printf '%s\n' "${commands[$idx]}"
    if [[ "$idx" -eq 5 ]]; then
      run_command "${commands[$idx]}" ILC_PHASE_594_GATE_SELFTEST=1
    else
      run_command "${commands[$idx]}"
    fi
  done

  echo "phase_594_verdict=pass"
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
