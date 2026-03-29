from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_496_validator_staking_liveness_ratification_evidence.py')
PHASE_496_SUBJECT_TOKEN = 'phase 496 validator staking liveness ratification evidence'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Ratified lane identity',
    '## 2. Evidence anchors',
    '## 3. Rejected alternatives',
    '## 4. Constitutional boundary after ratification',
    '## 5. Governance tokens',
    '## 6. Section-5 ratification readiness evidence checklist satisfaction',
)
REQUIRED_TOKENS = (
    'CDL-055 is ratified in Phase 496.',
    'CDL-053 remains reserved and unopened.',
    'No ilc_core/ mutation occurs in Phase 496.',
    '## 6. Section-5 ratification readiness evidence checklist satisfaction',
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


def _resolve_phase_496_commit_ref() -> str:
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
        if PHASE_496_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_496_commit_subject_present_but_no_qualifying_ratification_commit')
    raise AssertionError('phase_496_commit_not_present_in_local_history')


def test_ratification_evidence_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_ratification_evidence_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_ratification_evidence_records_expected_evidence_anchors() -> None:
    text = _read(ARTIFACT_PATH)
    for anchor in (
        'docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_prelock_hardening_493_v0.1.md',
        'docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md',
        'docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md',
    ):
        assert anchor in text


def test_live_decision_log_marks_cdl_055_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-055']['ratified_phase'] == '496'


def test_live_decision_log_keeps_cdl_053_absent() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert 'CDL-053' not in rows


def test_phase_496_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_496_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_496_main_commit_snapshot_ratifies_cdl_055() -> None:
    commit_ref = _resolve_phase_496_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-055']['ratified_phase'] == '496'
    assert 'CDL-053' not in rows
