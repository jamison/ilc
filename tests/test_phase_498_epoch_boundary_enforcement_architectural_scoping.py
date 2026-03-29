from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_epoch_boundary_enforcement_architectural_scoping_498_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_498_epoch_boundary_enforcement_architectural_scoping.py')
PHASE_498_SUBJECT_TOKEN = 'phase 498 epoch-boundary enforcement architectural scoping'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Surface description',
    '## 2. Constitutional amendment analysis',
    '## 3. Implementable without CDL amendment',
    '## 4. Carry-forward disposition',
)
REQUIRED_TOKENS = (
    'No CDL is opened in Phase 498.',
    'No decision-log mutation occurs in Phase 498.',
    'Epoch-boundary CDL amendment carry-forward is deferred to Window 505+.',
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


def _resolve_phase_498_commit_ref() -> str:
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
        if PHASE_498_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_498_commit_subject_present_but_no_qualifying_scoping_commit')
    raise AssertionError('phase_498_commit_not_present_in_local_history')


def test_scoping_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_scoping_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_scoping_artifact_records_dual_surface_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'provenance tags' in text
    assert 'constitutional gating conditions' in text
    assert 'requires a future CDL amendment in Window 505+' in text


def test_scoping_artifact_records_implementable_and_not_implementable_lists() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Implementable without a CDL amendment:' in text
    assert 'Not implementable without a CDL amendment:' in text
    assert 'validator witness quorum as a hard precondition' in text


def test_scoping_artifact_does_not_mutate_decision_log() -> None:
    assert DECISION_LOG_PATH.exists()
    text = _read(ARTIFACT_PATH)
    assert 'No decision-log mutation occurs in Phase 498.' in text


def test_phase_498_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_498_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_498_main_commit_snapshot_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_498_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
