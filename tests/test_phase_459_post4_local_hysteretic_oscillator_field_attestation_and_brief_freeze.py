from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_phase_459_post4_local_hysteretic_oscillator_field_attestation_and_brief_freeze_v0.1.md')
WALKTHROUGH_PATH = Path('docs/phases/phase_459_post4_g8_local_hysteretic_oscillator_field_attestation_and_brief_freeze_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
TEST_PATH = Path('tests/test_phase_459_post4_local_hysteretic_oscillator_field_attestation_and_brief_freeze.py')
PHASE_459_POST4_SUBJECT_TOKEN = 'phase 459 post4 local field attestation and brief freeze'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_TOKENS = (
    'Window 450-459 is closed.',
    'CDL-050 is ratified.',
    'CDL-051 is ratified.',
    'Phase 459 Post4 records the reduced-attack-surface local solution without reopening Window 450-459.',
    'simulations/sim_treasury_scenario5_local_hysteretic_oscillator_recovery_rule.py',
    'LOCAL_CODENAME=Shard Thermostat',
    'LOCAL_MECHANISM_STATUS=implemented',
    'local_hysteretic_oscillator_recovery_rule',
    'one rule for all shards',
    'The contrast execution field is frozen to four local-hysteretic candidates plus mixed_queue_and_production.',
    'No Scenario-5 execution occurs in Phase 459 Post4.',
    'No new constitutional authority is inferred from Strike Path evidence alone.',
    'Phase 459 Post4 does not reopen, prelock, amend, or ratify any CDL row.',
    'Phase 459 Post4 preserves the ratified CDL-050 and CDL-051 record unchanged.',
    'local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2',
    'local_hysteretic_oscillator_t55_l30_g15_f04_e4_r4',
    'local_hysteretic_oscillator_t55_l30_g15_f20_e4_r4',
    'local_hysteretic_oscillator_t55_l30_g15_f04_e1_r4',
    'mixed_queue_and_production',
    'Bounded randomized graph jumping is excluded from the default local rule.',
    'Optional later experimental extension: weak bounded local smoothing.',
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


def _resolve_phase_459_post4_commit_ref() -> str:
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
        if PHASE_459_POST4_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_459_post4_commit_subject_present_but_no_qualifying_local_field_commit')
    raise AssertionError('phase_459_post4_commit_not_present_in_local_history')


def test_attestation_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_attestation_artifact_records_frozen_field_and_attack_surface_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'intentionally high-separation' in text
    assert 'minimizes attack surface relative to the graph-aware Waggle families and the post-window hybrid supplements' in text
    assert 'randomized nonlocal shard jumping' in text


def test_walkthrough_records_boundary_and_next_pointer() -> None:
    text = _read(WALKTHROUGH_PATH)
    assert 'Window 450-459 remains closed.' in text
    assert 'CDL-050 remains ratified and unchanged.' in text
    assert 'CDL-051 remains ratified and unchanged.' in text
    assert 'No Scenario-5 execution occurred.' in text
    assert 'No ilc_core files changed.' in text
    assert 'Randomized nonlocal graph jumping is excluded from the default local rule.' in text
    assert 'Phase 459 Post5 - Local Hysteretic Oscillator Execution and Post-window Blocker Reassessment' in text


def test_status_records_post4_entry_and_next_pointer() -> None:
    text = _read(STATUS_PATH)
    assert '## Phase 459 Post4' in text
    assert 'LOCAL_CODENAME=Shard Thermostat' in text
    assert 'Phase 459 Post5 - Local Hysteretic Oscillator Execution and Post-window Blocker Reassessment' in text


def test_phase_459_post4_commit_touches_exact_required_paths() -> None:
    commit_ref = _resolve_phase_459_post4_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('docs/specs/ilc_constitutional_decision_log') for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_459_post4_commit_subject_is_present_in_local_history() -> None:
    assert _resolve_phase_459_post4_commit_ref()
