from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_phase_460_468_sequence_lock_v0.1.md')
TEST_PATH = Path('tests/test_phase_460_window_sequence_lock.py')
PHASE_460_SUBJECT_TOKEN = 'phase 460 window 460-468 sequence lock and cdl-052 scope freeze'
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
    '## 5. Entry conditions from Window 450-459',
)
REQUIRED_TOKENS = (
    'Window 460-468 is open as of Phase 460.',
    'CDL-052 governs the three-mode epistemic evaluation architecture.',
    'CDL-052 does not govern CDL-050 implementation, CDL-051 consensus runtime, or temporal decay parameter calibration.',
    'Phase 460 does not open CDL-052.',
    'CDL-052 may not open unless Gate 1, Gate 2, and Gate 3 are all cleared.',
    'CDL-052 remains absent at Phase 460 completion.',
    'Phase 459 Post1 through Phase 459 Post5 do not amend the constitutional scope or authority of Window 460-468.',
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


def _show_file_at_commit(commit_ref: str, path: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_460_commit_ref() -> str:
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
        if PHASE_460_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError('phase_460_commit_subject_present_but_no_qualifying_sequence_lock_commit')
    raise AssertionError('phase_460_commit_not_present_in_local_history')


def test_sequence_lock_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_no_forbidden_treasury_mutation_token_in_artifact_or_test_file() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)


def test_sequence_lock_table_covers_all_phases_460_through_468() -> None:
    text = _read(ARTIFACT_PATH)
    for phase in ('460', '461', '462', '463', '464', '465', '466', '467', '468'):
        assert f'| {phase} |' in text


def test_phase_460_commit_touches_expected_paths_and_not_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_460_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    text = _show_file_at_commit(commit_ref, 'docs/specs/ilc_constitutional_decision_log_v0.1.md')
    rows = parse_decision_register_rows(text)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
    assert 'CDL-052' not in rows
    assert rows['CDL-050']['status'] == 'ratified'
    assert rows['CDL-051']['status'] == 'ratified'


def test_phase_460_commit_does_not_open_cdl_052() -> None:
    commit_ref = _resolve_phase_460_commit_ref()
    artifact_text = _show_file_at_commit(commit_ref, str(ARTIFACT_PATH))
    assert 'Phase 460 does not open CDL-052.' in artifact_text
    text = _show_file_at_commit(commit_ref, 'docs/specs/ilc_constitutional_decision_log_v0.1.md')
    rows = parse_decision_register_rows(text)
    assert 'CDL-052' not in rows
