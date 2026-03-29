from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_sim_010_validator_incentive_economics_contract_486_v0.1.md')
TEST_PATH = Path('tests/test_phase_486_sim_010_validator_incentive_economics_contract_and_commissioning.py')
PHASE_486_SUBJECT_TOKEN = 'phase 486 sim-010 validator incentive economics contract and commissioning'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Scenarios',
    '## 2. Required outputs',
    '## 3. Pass and fail criteria',
    '## 4. Execution artifact contract',
    '## 5. Constitutional non-authorizations',
)
REQUIRED_TOKENS = (
    'recommended_validator_reward_fraction',
    'recommended_genesis_stake_amount',
    'recommended_liveness_miss_threshold',
    'SIM-010 does not authorize a CDL opening by itself.',
    'No `ilc_core/` implementation occurs in Phase 486.',
    'No decision-log mutation occurs in Phase 486.',
    'Phase 487 is the next authorized phase.',
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


def _resolve_phase_486_commit_ref() -> str:
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
        if PHASE_486_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_486_commit_subject_present_but_no_qualifying_contract_commit')
    raise AssertionError('phase_486_commit_not_present_in_local_history')


def test_contract_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_contract_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_contract_lists_all_four_scenarios() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Reward fraction scan' in text
    assert 'Staking sizing' in text
    assert 'Liveness threshold sensitivity' in text
    assert 'Participation equilibrium' in text


def test_contract_defines_phase_487_output_artifacts() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'out/sim_010/phase_487/' in text
    assert 'run_manifest.json' in text
    assert 'results.csv' in text
    assert 'summary_table.md' in text


def test_phase_486_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_486_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_486_main_commit_does_not_touch_ilc_core_or_decision_log() -> None:
    commit_ref = _resolve_phase_486_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
