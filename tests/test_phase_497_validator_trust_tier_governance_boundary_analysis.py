from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_cdl_056_validator_trust_tier_governance_boundary_analysis_497_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_497_validator_trust_tier_governance_boundary_analysis.py')
PHASE_497_SUBJECT_TOKEN = 'phase 497 validator trust-tier governance boundary analysis'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Analysis scope',
    '## 2. Constitutional pathway determination',
    '## 3. Eligibility criteria',
    '## 4. CDL-V3 and CDL-055 compatibility',
    '## 5. Tiebreaker design boundary',
    '## 6. Ratification readiness pre-conditions for CDL-056',
)
REQUIRED_TOKENS = (
    'CDL-056 is the required constitutional lane for trust-tier elevation.',
    'ADM-001 v0.3 is a companion amendment, not a substitute for CDL-056.',
    'No decision-log mutation occurs in Phase 497.',
    'Phase 498 is the next authorized phase.',
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


def _resolve_phase_497_commit_ref() -> str:
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
        if PHASE_497_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_497_commit_subject_present_but_no_qualifying_analysis_commit')
    raise AssertionError('phase_497_commit_not_present_in_local_history')


def test_governance_boundary_analysis_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_governance_boundary_analysis_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_governance_boundary_analysis_records_non_inheritable_liveness_based_eligibility() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'non-inheritable' in text
    assert 'CDL-055 liveness threshold' in text
    assert 'automatic revocation' in text


def test_governance_boundary_analysis_records_diversity_and_tiebreaker_boundaries() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'CDL-V3 remains the governing diversity-floor constraint' in text
    assert 'not an extra panel seat' in text
    assert 'not a redesigned quorum ladder' in text


def test_governance_boundary_analysis_does_not_require_decision_log_mutation() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'No decision-log mutation occurs in Phase 497.' in text
    assert DECISION_LOG_PATH.exists()


def test_phase_497_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_497_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_497_main_commit_snapshot_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_497_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
