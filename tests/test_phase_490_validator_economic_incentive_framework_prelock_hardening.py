from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_054_validator_economic_incentive_framework_prelock_hardening_490_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_490_validator_economic_incentive_framework_prelock_hardening.py')
PHASE_490_SUBJECT_TOKEN = 'phase 490 validator economic incentive framework prelock hardening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
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


def _resolve_phase_490_commit_ref() -> str:
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
        if PHASE_490_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_490_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_490_commit_not_present_in_local_history')


def test_prelock_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in (
        '## 1. Evidence ladder',
        '## 2. Routing boundary',
        '## 3. Rejected alternatives',
        '## 4. Ratification-readiness conditions',
    ):
        assert heading in text


def test_prelock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        'CDL-054 remains status: open in Phase 490.',
        'No decision-log mutation occurs in Phase 490.',
        'Phase 491 is the next authorized phase.',
    ):
        assert token in text


def test_prelock_artifact_records_rejected_alternatives() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'standalone treasury primitive for validator rewards' in text
    assert 'validator rewards detached from write-fee-burn' in text


def test_prelock_artifact_preserves_treasury_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'existing CDL-047 treasury framework only' in text


def test_phase_490_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_490_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_490_main_commit_snapshot_preserves_open_cdl_054() -> None:
    commit_ref = _resolve_phase_490_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-054']['status'] == 'open'
