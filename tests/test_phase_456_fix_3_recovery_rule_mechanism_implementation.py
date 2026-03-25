from __future__ import annotations

import importlib
import re
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

MODULE_NAME = 'simulations.sim_treasury_scenario5_recovery_rule'
MODULE_PATH = Path('simulations/sim_treasury_scenario5_recovery_rule.py')
ATTESTATION_PATH = Path('docs/specs/ilc_phase_456_fix_3_recovery_rule_mechanism_surface_attestation_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_3_recovery_rule_mechanism_implementation.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_3_g8_recovery_rule_mechanism_implementation_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_456_FIX_3_SUBJECT = 'feat(simulations): phase 456 fix 3 recovery-rule mechanism surface implementation'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(MODULE_PATH),
    str(ATTESTATION_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (
    MODULE_PATH,
    ATTESTATION_PATH,
    TEST_PATH,
    WALKTHROUGH_PATH,
    STATUS_PATH,
)
EXPECTED_CANDIDATES = {
    'production_band_5_epoch',
    'production_band_6_epoch',
    'production_band_7_epoch',
    'production_band_8_epoch',
    'production_band_10_epoch',
    'production_band_5_epoch_with_clamp_floor_low',
    'production_band_5_epoch_with_clamp_floor_high',
    'mixed_queue_and_production',
}


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_body(text: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(rf'{escaped}\n\n(.*?)(?=\n## |\Z)', text, flags=re.S)
    if not match:
        raise AssertionError(f'section_not_found:{heading}')
    return match.group(1).strip()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _resolve_phase_456_fix_3_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_456_FIX_3_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref

    if matches:
        raise AssertionError('phase_456_fix_3_commit_subject_present_but_no_qualifying_mechanism_surface_commit')
    raise AssertionError('phase_456_fix_3_commit_not_present_in_local_history')


def test_module_imports_and_exposes_callable_surface() -> None:
    module = importlib.import_module(MODULE_NAME)
    assert hasattr(module, 'evaluate_recovery_rule')
    assert callable(module.evaluate_recovery_rule)
    assert tuple(module.REQUIRED_OUTPUT_KEYS) == (
        'organic_ecu_production_rate',
        'pe_clamp_respect_rate',
        'intervention_duration_epochs',
        'intervention_cost_units',
    )


def test_candidate_registry_contains_fix2_candidates_and_mixed_queue_anchor() -> None:
    module = importlib.import_module(MODULE_NAME)
    assert set(module.CANDIDATE_REGISTRY.keys()) == EXPECTED_CANDIDATES
    assert set(module.list_candidate_ids()) == EXPECTED_CANDIDATES


def test_runnable_non_oscillator_candidates_return_required_keys_and_valid_ranges() -> None:
    module = importlib.import_module(MODULE_NAME)
    for candidate_id in sorted(EXPECTED_CANDIDATES):
        candidate = module.get_candidate_definition(candidate_id)
        result = module.evaluate_recovery_rule(candidate_id, candidate.parameters)
        assert set(result.keys()) == set(module.REQUIRED_OUTPUT_KEYS)
        assert 0.0 <= result['organic_ecu_production_rate'] <= 1.0
        assert 0.0 <= result['pe_clamp_respect_rate'] <= 1.0
        assert result['intervention_duration_epochs'] > 0
        assert result['intervention_cost_units'] >= 0.0


def test_oscillator_interface_exists_and_status_is_allowed() -> None:
    module = importlib.import_module(MODULE_NAME)
    assert tuple(module.OSCILLATOR_PARAMETER_KEYS) == (
        'oscillation_period',
        'oscillation_amplitude',
        'phase_offset',
    )
    assert module.OSCILLATOR_MECHANISM_STATUS in {'implemented', 'stubbed', 'deferred'}
    parameters = module.build_oscillator_parameters(3, 0.05, 'enforcement_first')
    assert set(parameters.keys()) == set(module.OSCILLATOR_PARAMETER_KEYS)
    if module.OSCILLATOR_MECHANISM_STATUS == 'stubbed':
        with pytest.raises(NotImplementedError):
            module.evaluate_recovery_rule('oscillating_production_band_short_period', parameters)


def test_attestation_doc_exists_contains_required_headings_and_confirms_pre1_exit_criteria() -> None:
    assert ATTESTATION_PATH.exists()
    text = _read(ATTESTATION_PATH)
    headings = (
        '## 1. Implemented module boundary',
        '## 2. Runnable carry-forward candidates',
        '## 3. Oscillator mechanism status',
        '## 4. Non-execution statement',
        '## 5. Non-authorization statement',
    )
    for heading in headings:
        assert heading in text
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'simulations/sim_treasury_scenario5_recovery_rule.py',
        'mixed_queue_and_production',
        'oscillator_mechanism_status=',
        'oscillator_mechanism_status=stubbed',
        'No Scenario-5 execution occurs in Phase 456 Fix 3.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 3.',
        'Fix 4 may not freeze oscillator candidates unless oscillator_mechanism_status=implemented.',
        'named executable Scenario-5 recovery-rule abstraction',
        'runnable uniform production-band surface',
        'runnable clamp-floor surface',
    ):
        assert token in text


def test_walkthrough_and_status_point_to_fix4_and_preserve_non_authorization_boundary() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    for path in REQUIRED_FILE_PATHS:
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)
    assert 'implementation lives in `simulations/`, not `ilc_core/`' in walkthrough
    assert 'No Scenario-5 execution was run in Phase 456 Fix 3.' in walkthrough
    assert 'No `ilc_core/` runtime files were changed.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'Phase 456 Fix 4 — recovery-rule commission brief freeze' in walkthrough
    assert '## Phase 456 (Fix 3)' in status
    assert 'oscillator_mechanism_status=stubbed' in status
    assert 'Phase 456 Fix 4 — recovery-rule commission brief freeze' in status


def test_phase_456_fix_3_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_456_fix_3_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_456_fix_3_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_phase_456_fix_3_commit_ref()
    before_rows = parse_decision_register_rows(_read_file_at_ref(f'{commit_ref}^1', str(DECISION_LOG_PATH)))
    after_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert before_rows == after_rows
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert 'CDL-050' not in after_rows
