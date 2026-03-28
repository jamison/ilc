from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_469_474_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_469_window_sequence_lock.py')
PHASE_469_SUBJECT_TOKEN = 'phase 469 window 469-474 sequence lock and consensus diversity scope freeze'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
FORBIDDEN_TREASURY_TOKEN = 'ILC_CDL_MUTATION_' + 'AUTHORIZED'
REQUIRED_HEADINGS = (
    '## 1. Window identity',
    '## 2. Scope freeze',
    '## 3. Non-goals',
    '## 4. Phase sequence and gate dependencies',
    '## 5. Entry conditions from Window 460-468',
)
REQUIRED_TOKENS = (
    'Window 469-474 is open as of Phase 469.',
    'This window is the canonical sequence lock for the post-468 consensus follow-on lane.',
    'CDL-052 implementation remains out of scope for Window 469-474.',
    'No decision-log mutation occurs in Phase 469.',
    'Phase 474 closes the window and publishes handoff.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(['git', 'show', '--name-only', '--pretty=', commit_ref], capture_output=True, check=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_469_commit_ref() -> str:
    result = subprocess.run(['git', 'log', '--format=%H%x09%s'], capture_output=True, check=True, text=True)
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_469_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_469_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_469_commit_not_present_in_local_history')


def test_sequence_lock_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_live_decision_log_preserves_cdl_050_cdl_051_cdl_052_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_phase_469_main_commit_touches_expected_paths_and_does_not_touch_decision_log() -> None:
    commit_ref = _resolve_phase_469_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_469_main_commit_does_not_touch_ilc_core() -> None:
    commit_ref = _resolve_phase_469_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
