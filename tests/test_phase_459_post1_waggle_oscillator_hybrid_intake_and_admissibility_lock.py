from __future__ import annotations

import subprocess
from pathlib import Path

from simulations import sim_treasury_scenario5_waggle_oscillator_hybrid_recovery_rule as hybrid_module


ARTIFACT_PATH = Path(
    'docs/specs/ilc_phase_459_post1_waggle_oscillator_hybrid_intake_and_admissibility_lock_v0.1.md'
)
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_459_post1_g8_waggle_oscillator_hybrid_intake_and_admissibility_lock_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
TEST_PATH = Path('tests/test_phase_459_post1_waggle_oscillator_hybrid_intake_and_admissibility_lock.py')
PHASE_459_POST1_SUBJECT_TOKEN = 'phase 459 post1 hybrid intake and admissibility lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Post-window boundary',
    '## 2. Surface reference and source basis',
    '## 3. Frozen hybrid neighborhood',
    '## 4. Admissibility and scheduling rule',
    '## 5. Non-reopening and non-authorization statement',
)
REQUIRED_TOKENS = (
    'Window 450-459 is closed.',
    'CDL-050 is ratified.',
    'CDL-051 is ratified.',
    'simulations/sim_treasury_scenario5_waggle_oscillator_hybrid_recovery_rule.py',
    'HYBRID_CODENAME=Waggle-Oscillator Hybrid',
    'HYBRID_MECHANISM_STATUS=strike_path_frozen',
    'waggle_oscillator_hybrid_recovery_rule',
    'The constrained field is frozen to the six Strike Path hybrid candidates plus mixed_queue_and_production.',
    'No Scenario-5 execution occurs in Phase 459 Post1.',
    'No new constitutional authority is inferred from Strike Path evidence alone.',
    'Phase 459 Post1 does not reopen Window 450-459.',
    'Phase 459 Post1 does not reopen, prelock, amend, or ratify any CDL row.',
    'The hybrid lane is admitted only as a future 460+ scheduling candidate.',
    'Any formal hybrid execution requires a new explicit numbered authorization in the 460+ window.',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100',
    'mixed_queue_and_production',
)
REQUIRED_WALKTHROUGH_TOKENS = (
    '## Files touched in the main commit',
    '## Main commit command',
    '## Pre-commit diagnostic',
    '## Main results',
    '## Post-main verification',
    'Window 450-459 remains closed.',
    'CDL-050 remains ratified and unchanged.',
    'CDL-051 remains ratified and unchanged.',
    'No Scenario-5 execution occurred in Phase 459 Post1.',
    'No `simulations/` or `ilc_core/` files changed in Phase 459 Post1.',
    'The hybrid surface was reused as an intake basis only.',
    'Phase 460 — Window 460-468 sequence lock and CDL-052 scope freeze',
)
REQUIRED_STATUS_TOKENS = (
    '## Phase 459 Post1',
    'HYBRID_CODENAME=Waggle-Oscillator Hybrid',
    'post-window supplement',
    'Phase 460 — Window 460-468 sequence lock and CDL-052 scope freeze',
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


def _resolve_phase_459_post1_commit_ref() -> str:
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
        if PHASE_459_POST1_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_459_post1_commit_subject_present_but_no_qualifying_hybrid_intake_commit')
    raise AssertionError('phase_459_post1_commit_not_present_in_local_history')


def test_intake_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_intake_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_intake_artifact_records_boundary_and_diagnostic_limitations() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'The leader is a candidate neighborhood, not a ratified constitutional mechanism.' in text
    assert 'Frontier/core diagnostics are informative support only, not a constitutional threshold substitute.' in text
    assert 'This admissibility lock preserves the exact constrained neighborhood already frozen by the Strike Path surface and does not reopen the unconstrained search space.' in text


def test_hybrid_surface_state_matches_frozen_intake_boundary() -> None:
    assert hybrid_module.HYBRID_CODENAME == 'Waggle-Oscillator Hybrid'
    assert hybrid_module.HYBRID_MECHANISM_STATUS == 'strike_path_frozen'
    assert hybrid_module.HYBRID_MECHANISM_LABEL == 'waggle_oscillator_hybrid_recovery_rule'
    assert hybrid_module.CONSTRAINED_FIELD_SIZE == 6
    assert 'mixed_queue_and_production' in hybrid_module.CANDIDATE_REGISTRY
    assert len(hybrid_module.CANDIDATE_REGISTRY) == 7


def test_walkthrough_exists_and_contains_required_tokens() -> None:
    text = _read(WALKTHROUGH_PATH)
    for token in REQUIRED_WALKTHROUGH_TOKENS:
        assert token in text


def test_status_records_phase_459_post1_boundary_and_next_pointer() -> None:
    text = _read(STATUS_PATH)
    for token in REQUIRED_STATUS_TOKENS:
        assert token in text


def test_phase_459_post1_commit_touches_exact_required_paths() -> None:
    commit_ref = _resolve_phase_459_post1_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('simulations/') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_459_post1_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_459_post1_commit_ref()
