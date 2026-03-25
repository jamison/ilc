from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)
from simulations import sim_treasury_scenario5_oscillator_recovery_rule as oscillator_module

MODULE_PATH = Path('simulations/sim_treasury_scenario5_oscillator_recovery_rule.py')
ATTESTATION_PATH = Path('docs/specs/ilc_phase_456_fix_6_oscillator_mechanism_surface_attestation_v0.1.md')
TEST_PATH = Path('tests/test_phase_456_fix_6_oscillator_mechanism_implementation.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_456_fix_6_g8_oscillator_mechanism_implementation_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_SUBJECT = 'feat(simulations): phase 456 fix 6 oscillator mechanism surface implementation'
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
EXACT_REQUIRED_PATHS = {
    str(MODULE_PATH),
    str(ATTESTATION_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_FILE_PATHS = (MODULE_PATH, ATTESTATION_PATH, TEST_PATH, WALKTHROUGH_PATH, STATUS_PATH)
EXPECTED_CANDIDATES = {
    'oscillating_production_band_short_period',
    'oscillating_production_band_tuned_period',
    'oscillating_production_band_long_period',
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
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}')
    return result.stdout


def _resolve_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject.strip() == PHASE_SUBJECT:
            matches.append(commit_hash)
    for commit_ref in matches:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == EXACT_REQUIRED_PATHS:
            return commit_ref
    if matches:
        raise AssertionError('phase_456_fix_6_commit_subject_present_but_no_qualifying_implementation_commit')
    raise AssertionError('phase_456_fix_6_commit_not_present_in_local_history')


def test_module_exists_and_exposes_callable_surface() -> None:
    assert MODULE_PATH.exists()
    assert hasattr(oscillator_module, 'evaluate_recovery_rule')
    assert callable(oscillator_module.evaluate_recovery_rule)
    assert oscillator_module.OSCILLATOR_MECHANISM_STATUS == 'implemented'


def test_candidate_registry_contains_required_ids() -> None:
    assert set(oscillator_module.CANDIDATE_REGISTRY) == EXPECTED_CANDIDATES
    assert set(oscillator_module.list_candidate_ids()) == EXPECTED_CANDIDATES


def test_all_runnable_candidates_return_required_metrics() -> None:
    for candidate_id in EXPECTED_CANDIDATES:
        candidate = oscillator_module.get_candidate_definition(candidate_id)
        outputs = oscillator_module.evaluate_recovery_rule(candidate_id, candidate.parameters)
        assert set(outputs) == set(oscillator_module.REQUIRED_OUTPUT_KEYS)
        assert 0.0 <= outputs['organic_ecu_production_rate'] <= 1.0
        assert 0.0 <= outputs['pe_clamp_respect_rate'] <= 1.0
        assert outputs['intervention_duration_epochs'] > 0
        assert outputs['intervention_cost_units'] >= 0


def test_parameter_surface_exists_and_supports_exact_overrides_only() -> None:
    built = oscillator_module.build_oscillator_parameters(5, 0.09, 'enforce_first')
    assert tuple(built) == oscillator_module.OSCILLATOR_PARAMETER_KEYS
    tuned = oscillator_module.evaluate_recovery_rule('oscillating_production_band_tuned_period', built)
    assert tuned['organic_ecu_production_rate'] == 0.95
    try:
        oscillator_module.evaluate_recovery_rule(
            'oscillating_production_band_tuned_period',
            oscillator_module.build_oscillator_parameters(3, 0.09, 'enforce_first'),
        )
    except ValueError as exc:
        assert 'unsupported_parameter_override:oscillating_production_band_tuned_period:oscillation_period=3' in str(exc)
    else:
        raise AssertionError('unsupported_override_not_rejected')


def test_attestation_doc_contains_required_headings_and_tokens() -> None:
    assert ATTESTATION_PATH.exists()
    text = _read(ATTESTATION_PATH)
    headings = (
        '## 1. Implemented module boundary',
        '## 2. Runnable oscillator candidates',
        '## 3. Weak-field challenger and field boundary',
        '## 4. Oscillator mechanism status',
        '## 5. Non-execution and non-authorization statement',
    )
    for heading in headings:
        body = _section_body(text, heading)
        assert body
        assert len([line for line in body.splitlines() if line.strip()]) >= 2
    for token in (
        'simulations/sim_treasury_scenario5_oscillator_recovery_rule.py',
        'oscillating_production_band_short_period',
        'oscillating_production_band_tuned_period',
        'oscillating_production_band_long_period',
        'mixed_queue_and_production',
        'oscillation_period',
        'oscillation_amplitude',
        'phase_offset',
        'oscillator_mechanism_status=implemented',
        'Legacy production-band carry-forwards are not automatically included in the oscillator execution field.',
        'No Scenario-5 execution occurs in Phase 456 Fix 6.',
        'No CDL-050 opening or ratification occurs in Phase 456 Fix 6.',
        'Fix 7 may freeze oscillator candidates because oscillator_mechanism_status=implemented.',
    ):
        assert token in text


def test_walkthrough_and_status_point_to_fix_7() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'oscillator_mechanism_status=implemented' in walkthrough
    assert 'No Scenario-5 execution was run in Phase 456 Fix 6.' in walkthrough
    assert 'No `ilc_core/` files were changed.' in walkthrough
    assert 'CDL-050 remains unopened.' in walkthrough
    assert 'Phase 456 Fix 7 — oscillator commission brief freeze' in walkthrough
    assert '## Phase 456 (Fix 6)' in status
    assert 'oscillator_mechanism_status=implemented' in status
    assert 'Phase 456 Fix 7 — oscillator commission brief freeze' in status


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert changed == EXACT_REQUIRED_PATHS
    assert_head_commit_touched_no_runtime_files(commit_ref)


def test_commit_does_not_open_cdl_050_and_preserves_cdl_051() -> None:
    commit_ref = _resolve_commit_ref()
    before_ref = f'{commit_ref}^'
    before_rows = parse_decision_register_rows(_read_file_at_ref(before_ref, str(DECISION_LOG_PATH)))
    assert before_rows['CDL-051']['status'] == 'ratified'
    assert 'CDL-050' not in before_rows
    assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, str(MODULE_PATH))
    assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, str(ATTESTATION_PATH))
    assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, str(TEST_PATH))
    assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, str(WALKTHROUGH_PATH))
    assert FORBIDDEN_TREASURY_TOKEN not in _read_file_at_ref(commit_ref, str(STATUS_PATH))
