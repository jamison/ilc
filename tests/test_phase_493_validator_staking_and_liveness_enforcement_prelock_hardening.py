from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_prelock_hardening_493_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py')
PHASE_493_SUBJECT_TOKEN = 'phase 493 validator staking and liveness enforcement prelock hardening'
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


def _resolve_phase_493_commit_ref() -> str:
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
        if PHASE_493_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_493_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_493_commit_not_present_in_local_history')


def test_prelock_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in (
        '## 1. Liveness boundary',
        '## 2. Equivocation boundary',
        '## 3. Re-admission boundary',
        '## 4. Future ratification conditions',
    ):
        assert heading in text


def test_prelock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        'CDL-055 remains status: open in Phase 493.',
        'No decision-log mutation occurs in Phase 493.',
        'Phase 494 is the next authorized phase.',
    ):
        assert token in text


def test_prelock_artifact_records_equivocation_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'signing conflicting `canonical_block_hash` values for the same epoch' in text


def test_prelock_artifact_records_re_admission_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'not ratified in this window' in text


def test_phase_493_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_493_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_493_main_commit_snapshot_preserves_open_cdl_055() -> None:
    commit_ref = _resolve_phase_493_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'open'
