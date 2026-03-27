from __future__ import annotations

import subprocess
from pathlib import Path

from simulations import sim_treasury_scenario5_waggle_oscillator_hybrid_contrast_recovery_rule as contrast_module


SURFACE_PATH = Path('simulations/sim_treasury_scenario5_waggle_oscillator_hybrid_contrast_recovery_rule.py')
ARTIFACT_PATH = Path(
    'docs/specs/ilc_phase_459_post2_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze_v0.1.md'
)
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_459_post2_g8_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
TEST_PATH = Path('tests/test_phase_459_post2_waggle_oscillator_hybrid_contrast_field_attestation_and_brief_freeze.py')
PHASE_459_POST2_SUBJECT_TOKEN = 'phase 459 post2 hybrid contrast field attestation and brief freeze'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SURFACE_PATH),
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
EXPECTED_IDS = {
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100',
    'hybrid_nonlinear_curve_k85_g35_f44_backpressure_first_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120',
    'hybrid_nonlinear_curve_k20_g35_f06_backpressure_first_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120',
    'hybrid_nonlinear_curve_k85_g06_f06_uniform_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120',
    'mixed_queue_and_production',
}
REQUIRED_TOKENS = (
    'Window 450-459 is closed.',
    'CDL-050 is ratified.',
    'CDL-051 is ratified.',
    'Phase 459 Post2 supersedes the scheduling clause in Phase 459 Post1 without reopening Window 450-459.',
    'simulations/sim_treasury_scenario5_waggle_oscillator_hybrid_contrast_recovery_rule.py',
    'HYBRID_CODENAME=Waggle-Oscillator Hybrid',
    'HYBRID_MECHANISM_STATUS=implemented',
    'waggle_oscillator_hybrid_recovery_rule',
    'The contrast execution field is frozen to four hybrid candidates plus mixed_queue_and_production.',
    'No Scenario-5 execution occurs in Phase 459 Post2.',
    'No new constitutional authority is inferred from Strike Path evidence alone.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_459_post2_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_459_POST2_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_459_post2_commit_subject_present_but_no_qualifying_hybrid_contrast_commit')
    raise AssertionError('phase_459_post2_commit_not_present_in_local_history')


def test_artifact_contains_required_boundary_and_freeze_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert 'intentionally high-separation' in text


def test_contrast_surface_registry_and_constants_are_exact() -> None:
    assert contrast_module.HYBRID_CODENAME == 'Waggle-Oscillator Hybrid'
    assert contrast_module.HYBRID_MECHANISM_STATUS == 'implemented'
    assert contrast_module.HYBRID_MECHANISM_LABEL == 'waggle_oscillator_hybrid_recovery_rule'
    assert contrast_module.CONTRAST_FIELD_SIZE == 4
    assert set(contrast_module.CANDIDATE_REGISTRY) == EXPECTED_IDS


def test_contrast_surface_outputs_match_expected_leader_and_weak_probe_values() -> None:
    leader = contrast_module.evaluate_recovery_rule(
        'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100'
    )
    weak = contrast_module.evaluate_recovery_rule(
        'hybrid_nonlinear_curve_k85_g35_f44_backpressure_first_p7_a13_release_first_rq085_ab115_dc075_cp105_ss200_rb065_bs080_adj120'
    )
    assert leader == {
        'organic_ecu_production_rate': 0.992,
        'pe_clamp_respect_rate': 0.933,
        'intervention_duration_epochs': 10,
        'intervention_cost_units': 0.277,
    }
    assert weak == {
        'organic_ecu_production_rate': 0.823,
        'pe_clamp_respect_rate': 0.856,
        'intervention_duration_epochs': 14,
        'intervention_cost_units': 0.314,
    }


def test_walkthrough_and_status_record_post_window_boundary() -> None:
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    assert 'Window 450-459 remains closed.' in walkthrough
    assert 'CDL-050 remains ratified and unchanged.' in walkthrough
    assert 'CDL-051 remains ratified and unchanged.' in walkthrough
    assert 'No Scenario-5 execution occurred.' in walkthrough
    assert 'high-separation' in walkthrough
    assert '## Phase 459 Post2' in status
    assert 'HYBRID_CODENAME=Waggle-Oscillator Hybrid' in status
    assert 'Phase 459 Post3 — Waggle-Oscillator Hybrid Contrast Execution and Post-window Blocker Reassessment' in status


def test_phase_459_post2_commit_touches_exact_required_paths() -> None:
    commit_ref = _resolve_phase_459_post2_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('docs/specs/ilc_constitutional_decision_log') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_459_post2_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_459_post2_commit_ref()
