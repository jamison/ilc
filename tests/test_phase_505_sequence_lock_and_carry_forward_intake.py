from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_505_514_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_505_sequence_lock_and_carry_forward_intake.py')
PHASE_505_SUBJECT_TOKEN = 'phase 505 window 505-514 sequence lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Carry-forward freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and primary deliverables',
    '## 5. Entry conditions from Window 495-504',
)
REQUIRED_TOKENS = (
    're_admission_boundary is out of scope for the CDL-055 runtime in Window 505-514.',
    'CDL-058 opening is deferred to Window 515+.',
    'CDL-053 remains reserved and unopened throughout Window 505-514.',
    'Phase 514 is the closure gate.',
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_505_commit_ref() -> str:
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
        if PHASE_505_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_505_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_505_commit_not_present_in_local_history')


def test_sequence_lock_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sequence_lock_lists_all_ten_phases() -> None:
    text = _read(ARTIFACT_PATH)
    for phase in range(505, 515):
        assert f'| {phase} |' in text


def test_live_cdl_inventory_matches_entry_conditions() -> None:
    commit_ref = _resolve_phase_505_commit_ref()
    # The Phase-505 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert rows.get('CDL-057', {}).get('status') in {None, 'open', 'ratified'}
    assert 'CDL-058' not in rows


def test_phase_505_live_tree_has_no_validator_runtime_changes() -> None:
    validator_dir = Path('ilc_core/validator')
    if not validator_dir.exists():
        return
    assert (validator_dir / 'staking_liveness_runtime.py').exists()
    assert (validator_dir / 'trust_tier_runtime.py').exists()


def test_phase_505_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_505_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_505_main_commit_does_not_touch_cdl_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_505_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert 'CDL-053' not in rows
