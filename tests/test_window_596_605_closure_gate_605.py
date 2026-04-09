from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

GATE_PATH = Path('tools/check_window_596_605_closure_gate_phase_605.sh')
HANDOFF_PATH = Path('docs/specs/ilc_window_596_605_handoff_605_v0.1.md')
PROMPT_VALIDATION_COMMAND = 'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_596_g8_window_596_605_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_597_g8_genesis_governance_dilution_and_brake_semantics_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_598_g8_freshness_gate_provenance_and_genesis_exemption_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_599_g8_genesis_accrual_governor_provenance_reconciliation.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_600_g8_deterministic_genesis_economics_evidence_and_parameter_closure.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_601_g8_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_602_g8_topological_exemption_boundary_and_public_tokenomics_statement.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_603_g8_genesis_carry_forward_synthesis_and_readiness_delta_addendum.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_604_g8_coherence_report_and_capsule_v3_2.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_605_g8_window_596_605_closure_gate_and_handoff.md'
GENESIS_CLOSURE_TEST_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_596_window_596_605_sequence_lock.py tests/test_phase_597_genesis_governance_dilution_and_brake_semantics_closure.py tests/test_phase_598_freshness_gate_provenance_and_genesis_exemption_closure.py tests/test_phase_599_genesis_accrual_governor_provenance_reconciliation.py tests/test_phase_600_deterministic_genesis_economics_evidence_and_parameter_closure.py tests/test_phase_601_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary.py tests/test_phase_602_topological_exemption_boundary_and_public_tokenomics_statement.py -q'
SYNTHESIS_COHERENCE_TEST_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_phase_603_genesis_carry_forward_synthesis_and_readiness_delta_addendum.py tests/test_phase_604_coherence_report_and_capsule_v3_2.py -q'
CANARY_COMMAND = 'python3 tools/run_mutation_canary_phase_297.py'
CLI_CONTRACT_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_window_596_605_closure_gate_605.py -q'
WALKTHROUGH_COMMAND = 'PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_no_ellipses_in_walkthroughs.py -q -k phase_walkthroughs'
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    PROMPT_VALIDATION_COMMAND,
    '[2/6] genesis_closure_band_tests',
    GENESIS_CLOSURE_TEST_COMMAND,
    '[3/6] synthesis_and_coherence_tests',
    SYNTHESIS_COHERENCE_TEST_COMMAND,
    '[4/6] mutation_canary',
    CANARY_COMMAND,
    '[5/6] closure_gate_cli_contract',
    CLI_CONTRACT_COMMAND,
    '[6/6] walkthrough_hygiene',
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
        'genesis_closure_band_tests',
        'synthesis_and_coherence_tests',
        'mutation_canary',
        'closure_gate_cli_contract',
        'walkthrough_hygiene',
    ):
        assert label in text
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_gate_rejects_prompt_count_only_file_count_only_or_synthesis_only_pass_conditions() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert 'prompt counts' in text
    assert 'file counts' in text
    assert 'summary prose' in text
    assert 'synthesis/coherence as substitute for' in text
    assert 'remaining later-lane defers' in text


def test_full_run_passes_on_valid_state() -> None:
    if os.environ.get('ILC_PHASE_605_GATE_SELFTEST') == '1':
        pytest.skip('phase_605_selftest_context_skip_full_gate')
    result = _run_gate([])
    assert result.returncode == 0
    assert 'phase_605_window_state=pass' in result.stdout
    assert 'phase_605_verdict=pass' in result.stdout


def test_gate_requires_all_ten_prompt_validations_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert PROMPT_VALIDATION_COMMAND in text
    assert text.count('tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_') == 10


def test_gate_requires_the_exact_closure_band_and_synthesis_coherence_test_file_lists_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert GENESIS_CLOSURE_TEST_COMMAND in text
    assert SYNTHESIS_COHERENCE_TEST_COMMAND in text
    assert 'tests/test_phase_596_window_596_605_sequence_lock.py' in text
    assert 'tests/test_phase_604_coherence_report_and_capsule_v3_2.py' in text


def test_gate_requires_the_mutation_canary_command_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert CANARY_COMMAND in text


def test_gate_wires_the_selftest_recursion_guard_for_phase_605() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert 'ILC_PHASE_605_GATE_SELFTEST=1' in text
    assert 'run_command "${commands[$idx]}" ILC_PHASE_605_GATE_SELFTEST=1' in text


def test_prior_window_pattern_structure_is_adapted_to_this_window() -> None:
    gate_text = GATE_PATH.read_text(encoding='utf-8')
    handoff_text = HANDOFF_PATH.read_text(encoding='utf-8')
    assert 'tests/test_window_585_594_closure_gate_594.py' in gate_text
    assert 'Do not assume naming or category shape' in gate_text
    headings = (
        '## 1. Window 596-605 completion summary',
        '## 2. Genesis closure band record',
        '## 3. Synthesis and coherence record',
        '## 4. Remaining later-lane defers',
        '## 5. Frozen inherited boundaries preserved',
        '## 6. Context capsule reference and next strategic boundary',
    )
    for heading in headings:
        assert heading in handoff_text
    tokens = (
        'phase_605_verdict=pass',
        'window_596_605_complete',
        'genesis_carry_forward_window_complete',
        'phases_597_602_genesis_closure_band_passed',
        'phases_603_604_synthesis_and_coherence_lane_passed',
        'frozen_585_595_boundaries_preserved_at_handoff',
        'window_606_plus_or_next_approved_lane_is_next_authorized_strategic_boundary',
        'future_window_gates_consuming_phase_605_tests_must_set_ilc_phase_605_gate_selftest',
    )
    for token in tokens:
        assert token in handoff_text
    assert 'completion of the Phase 305 canonical output package' in handoff_text
    assert 'the frozen 585-594 public boundary' in handoff_text
    assert 'the frozen 595 bounded RC0.1 closure' in handoff_text


def test_handoff_preserves_frozen_boundaries_and_later_lane_defers_explicitly() -> None:
    text = HANDOFF_PATH.read_text(encoding='utf-8')
    assert 'inbound HTTP machine-payment ingress remains a separate later lane unless closed elsewhere by explicit later work.' in text
    assert 'any Genesis-only ECU realization-controller implementation packet' in text
    assert 'the actual capability-proof runtime lane and post-bootstrap non-privileged reference-state implementation' in text
    assert 'docs/specs/ilc_antigravity_context_capsule_v3.2.md' in text
    assert 'Any future closure gate invoking `tests/test_window_596_605_closure_gate_605.py`' in text
