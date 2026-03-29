from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_056_validator_trust_tier_elevation_prelock_hardening_500_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_500_validator_trust_tier_elevation_prelock_hardening.py')
PHASE_500_SUBJECT_TOKEN = 'phase 500 validator trust-tier elevation prelock hardening'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Evidence ladder',
    '## 2. Tiebreaker design boundary',
    '## 3. Liveness-threshold coupling',
    '## 4. Rejected alternatives',
    '## 5. Ratification readiness evidence checklist',
)
REQUIRED_TOKENS = (
    'CDL-056 remains status: open in Phase 500.',
    'No decision-log mutation occurs in Phase 500.',
    'Phase 501 is the next authorized phase.',
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


def _resolve_phase_500_commit_ref() -> str:
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
        if PHASE_500_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_500_commit_subject_present_but_no_qualifying_prelock_commit')
    raise AssertionError('phase_500_commit_not_present_in_local_history')


def test_prelock_artifact_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_prelock_artifact_records_tiebreaker_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'not an extra panel seat' in text
    assert 'not a weighted quorum expansion' in text
    assert 'not a quorum-ladder redesign' in text


def test_prelock_artifact_records_liveness_coupling_and_rejected_alternatives() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'ratified CDL-055 liveness threshold' in text
    assert 'using ADM-001 as a substitute for constitutional ratification' in text


def test_phase_500_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_500_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_500_main_commit_snapshot_preserves_open_cdl_056() -> None:
    commit_ref = _resolve_phase_500_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-056']['status'] == 'open'


def test_phase_500_main_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_500_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
