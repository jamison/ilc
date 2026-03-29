from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_opening_stub_492_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_492_validator_staking_and_liveness_enforcement_opening_stub.py')
PHASE_492_SUBJECT_TOKEN = 'phase 492 validator staking and liveness enforcement opening stub'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}


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


def _resolve_phase_492_commit_ref() -> str:
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
        if PHASE_492_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_492_commit_subject_present_but_no_qualifying_opening_commit')
    raise AssertionError('phase_492_commit_not_present_in_local_history')


def test_opening_stub_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        'CDL-055 opens in Phase 492.',
        'CDL-054 is already ratified before CDL-055 opens.',
        'CDL-046 remains the orphan-policy authority outside validator participation.',
        'No `ilc_core/` mutation occurs in Phase 492.',
    ):
        assert token in text


def test_opening_stub_has_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in (
        '## 1. Lane identity',
        '## 2. CDL-046 amendment boundary',
        '## 3. Evidence dependencies',
        '## 4. Non-goals',
    ):
        assert heading in text


def test_live_decision_log_contains_open_cdl_055_row() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'open'


def test_live_decision_log_keeps_cdl_054_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-054']['status'] == 'ratified'


def test_phase_492_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_492_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_492_main_commit_snapshot_opens_cdl_055_with_cdl_054_already_ratified() -> None:
    commit_ref = _resolve_phase_492_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'open'
    assert rows['CDL-054']['status'] == 'ratified'
    assert 'CDL-053' not in rows
