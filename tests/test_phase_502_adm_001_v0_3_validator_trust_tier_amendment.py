from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path('docs/specs/ilc_adm_001_v0_3_validator_trust_tier_amendment_502_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_502_adm_001_v0_3_validator_trust_tier_amendment.py')
PHASE_502_SUBJECT_TOKEN = 'phase 502 adm-001 v0.3 validator trust-tier amendment'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Amendment authority',
    '## 2. Trust-tier elevation flag',
    '## 3. Eligibility and revocation',
    '## 4. Dispute tiebreaker rule',
    '## 5. Non-changes to quorum ladder',
)
REQUIRED_TOKENS = (
    'ADM-001 advances to v0.3 in Phase 502.',
    'CDL-056 is the constitutional authority for validator trust-tier elevation.',
    'No CDL mutation occurs in Phase 502.',
    'The 7+1 panel quorum ladder is unchanged by this amendment.',
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


def _resolve_phase_502_commit_ref() -> str:
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
        if PHASE_502_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_502_commit_subject_present_but_no_qualifying_adm_commit')
    raise AssertionError('phase_502_commit_not_present_in_local_history')


def test_adm_amendment_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_adm_amendment_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_adm_amendment_records_trust_tier_flag_and_tiebreaker_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'non-inheritable' in text
    assert 'bounded tiebreaker in consensus-related disputes' in text
    assert 'not a weighted-vote multiplier' in text


def test_adm_amendment_records_non_changes_to_quorum_and_diversity() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'L-tier requirements remain unchanged.' in text
    assert 'CDL-V3 diversity-floor protections remain unchanged.' in text


def test_live_decision_log_keeps_cdl_056_ratified() -> None:
    rows = parse_decision_register_rows(DECISION_LOG_PATH.read_text(encoding='utf-8'))
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-056']['ratified_phase'] == '501'
    assert 'CDL-053' not in rows


def test_phase_502_main_commit_snapshot_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_502_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_502_main_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_502_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
