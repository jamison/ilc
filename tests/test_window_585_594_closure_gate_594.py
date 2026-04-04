from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

GATE_PATH = Path('tools/check_window_585_594_closure_gate_phase_594.sh')
HANDOFF_PATH = Path('docs/specs/ilc_window_585_594_handoff_594_v0.1.md')
TEST_PATH = Path('tests/test_window_585_594_closure_gate_594.py')
PROMPT_VALIDATION_COMMAND = 'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_585_g8_window_585_594_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_586_g8_public_receipt_representation_cluster_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_587_g8_public_identity_activation_namespace_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_588_g8_public_quorum_eligibility_genesis_lineage_authority_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_589_g8_settlement_linked_public_legitimacy_payout_traceability_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_590_g8_genesis_authority_sunset_fork_legitimacy_coherence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_591_g8_public_runtime_integration_over_receipt_boundary.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_592_g8_public_release_claim_and_operator_honesty_package.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_593_g8_coherence_report_and_public_rc_capsule_v3_1.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_594_g8_window_585_594_closure_gate_and_handoff.md'
CONSTITUTIONAL_TEST_COMMAND = 'python3 -m pytest tests/test_phase_585_window_585_594_sequence_lock.py tests/test_phase_586_public_receipt_representation_cluster_lock.py tests/test_phase_587_public_identity_activation_and_namespace_boundary_lock.py tests/test_phase_588_public_quorum_eligibility_and_genesis_lineage_authority_boundary_lock.py tests/test_phase_589_settlement_linked_public_legitimacy_and_payout_traceability_lock.py tests/test_phase_590_genesis_authority_sunset_and_fork_legitimacy_coherence_lock.py -q'
INTEGRATION_TEST_COMMAND = 'python3 -m pytest tests/test_phase_591_public_runtime_integration_over_receipt_boundary.py tests/test_phase_592_public_release_claim_and_operator_honesty_package.py tests/test_phase_593_coherence_report_and_public_rc_capsule_v3_1.py -q'
TOOLCHAIN_REGRESSION_COMMAND = 'python3 -m pytest tests/test_testbed_control_surface.py -q -k "readiness_delta or release_claim or release_candidate_manifest_records_optional_economic_state"'
CANARY_COMMAND = 'python3 tools/run_mutation_canary_phase_297.py'
CLI_CONTRACT_COMMAND = 'python3 -m pytest tests/test_window_585_594_closure_gate_594.py -q'
WALKTHROUGH_COMMAND = 'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs'
EXPECTED_DRY_RUN_LINES = [
    '[1/7] prompt_contract_validation',
    PROMPT_VALIDATION_COMMAND,
    '[2/7] constitutional_closure_band_tests',
    CONSTITUTIONAL_TEST_COMMAND,
    '[3/7] public_rc_integration_band_tests',
    INTEGRATION_TEST_COMMAND,
    '[4/7] public_rc_toolchain_regression',
    TOOLCHAIN_REGRESSION_COMMAND,
    '[5/7] mutation_canary',
    CANARY_COMMAND,
    '[6/7] closure_gate_cli_contract',
    CLI_CONTRACT_COMMAND,
    '[7/7] walkthrough_hygiene',
    WALKTHROUGH_COMMAND,
]


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, check=False)


def test_gate_categories_are_defined() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert GATE_PATH.exists()
    assert GATE_PATH.stat().st_mode & 0o111
    for label in (
        'prompt_contract_validation',
        'constitutional_closure_band_tests',
        'public_rc_integration_band_tests',
        'public_rc_toolchain_regression',
        'mutation_canary',
        'closure_gate_cli_contract',
        'walkthrough_hygiene',
    ):
        assert label in text
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_gate_rejects_prompt_count_only_file_count_only_or_honesty_package_only_pass_conditions() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert 'prompt counts' in text
    assert 'file counts' in text
    assert 'manifest presence without checked semantic assertions' in text
    assert 'honesty-package-only states' in text or 'honesty-package-only' in text
    assert 'Genesis carry-forward queue' in text
    assert 'capability-' in text


def test_full_run_passes_on_valid_state() -> None:
    if 'ILC_PHASE_594_GATE_SELFTEST' in subprocess.run(['env'], capture_output=True, text=True, check=True).stdout:
        pytest.skip('phase_594_selftest_context_skip_full_gate')
    if Path('.').joinpath('.git').exists() is False:
        pytest.skip('git_repository_required')
    if '1' == __import__('os').environ.get('ILC_PHASE_594_GATE_SELFTEST'):
        pytest.skip('phase_594_selftest_context_skip_full_gate')
    result = _run_gate([])
    assert result.returncode == 0
    assert 'phase_594_window_state=pass' in result.stdout
    assert 'phase_594_verdict=pass' in result.stdout


def test_gate_requires_all_ten_prompt_validations_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert PROMPT_VALIDATION_COMMAND in text
    assert text.count('tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_') == 10


def test_gate_requires_the_exact_closure_band_and_integration_band_test_file_lists_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert CONSTITUTIONAL_TEST_COMMAND in text
    assert INTEGRATION_TEST_COMMAND in text
    assert 'tests/test_phase_585_window_585_594_sequence_lock.py' in text
    assert 'tests/test_phase_593_coherence_report_and_public_rc_capsule_v3_1.py' in text


def test_gate_requires_the_public_rc_toolchain_regression_command_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert TOOLCHAIN_REGRESSION_COMMAND in text


def test_gate_requires_the_mutation_canary_command_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert CANARY_COMMAND in text


def test_gate_wires_the_selftest_recursion_guard_for_phase_594() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert 'ILC_PHASE_594_GATE_SELFTEST=1' in text
    assert 'run_command "${commands[$idx]}" ILC_PHASE_594_GATE_SELFTEST=1' in text


def test_prior_window_pattern_structure_and_handoff_contract_are_adapted_to_this_window() -> None:
    gate_text = GATE_PATH.read_text(encoding='utf-8')
    handoff_text = HANDOFF_PATH.read_text(encoding='utf-8')
    assert 'tests/test_window_565_574_closure_gate_574.py' in gate_text
    assert 'Do not assume naming or' in gate_text
    for heading in (
        '## 1. Window 585-594 completion summary',
        '## 2. Constitutional closure band record',
        '## 3. Public-runtime integration record',
        '## 4. Public release-claim and operator-honesty record',
        '## 5. Remaining Genesis carry-forward canon queue',
        '## 6. Deferred future lanes and implementation boundaries',
        '## 7. Context capsule reference and next strategic boundary',
    ):
        assert heading in handoff_text
    for token in (
        'phase_594_verdict=pass',
        'window_585_594_complete',
        'public_release_candidate_boundary_window_complete',
        'phases_587_590_constitutional_closure_passed',
        'phases_591_593_integration_and_honesty_lane_passed',
        'genesis_carry_forward_queue_explicit_at_handoff',
        'protocol_vs_harness_boundary_preserved_at_close',
        'window_595_plus_is_next_authorized_strategic_boundary',
    ):
        assert token in handoff_text
