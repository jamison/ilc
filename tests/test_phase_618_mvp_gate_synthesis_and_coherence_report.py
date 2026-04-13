from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

COHERENCE_REPORT_PATH = Path('docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v3.3.md')
TEST_PATH = Path('tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_618_g8_mvp_gate_synthesis_and_coherence_report_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_618_SUBJECT_TOKENS = ('phase 618', 'coherence')
PHASE_618_BACKFILL_SUBJECT_TOKENS = ('phase 618', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_REPORT_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity and synthesis basis',
    '## 2. MVP gate spec lane synthesis (Phases 614-617)',
    '## 3. MVP gate verdict',
    '## 4. Canonical boundary inheritance',
    '## 5. Open questions and residual blockers',
    '## 6. Carry-forward for Phase 619 closure gate',
)
REQUIRED_GOVERNANCE_TOKENS = (
    'window_613_619_coherence_report_phase_618',
    'mvp_gate_synthesis_verdict_issued',
    'phase_612_five_touchpoints_evaluated',
    'option_d_posture_confirmed',
    'cdl_062_remains_not_authorized',
    'wallet_boundary_576_581_confirmed_unchanged',
    'agent_skills_deferred_per_phase_612_priority_rule',
)
TOUCHPOINT_TOKENS = (
    'public_init_admission_contract_spec_614_locked',
    'public_receipt_schema_and_query_contract_spec_locked',
    'ecu_to_ilc_lifecycle_contract_spec_615_locked',
    'public_wallet_surface_contract_spec_locked',
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(
    *, subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_tokens}')


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f'commit_not_yet_present:{subject_tokens}')


def test_coherence_report_exists_and_contains_all_required_section_headings() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_coherence_report_contains_all_required_governance_tokens() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    for token in REQUIRED_GOVERNANCE_TOKENS:
        assert token in text


def test_coherence_report_section_2_evaluates_all_five_mvp_touchpoints_by_token() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    for token in TOUCHPOINT_TOKENS:
        assert token in text
    assert text.count('ecu_to_ilc_lifecycle_contract_spec_615_locked') >= 2
    assert 'Touchpoints 3 and 4 are both covered by the single Phase 615 lifecycle packet' in text


def test_coherence_report_section_3_contains_explicit_mvp_gate_verdict_token() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    assert (
        'mvp_gate_spec_verdict=pass' in text
        or 'mvp_gate_spec_verdict=conditional' in text
    )


def test_coherence_report_section_3_does_not_imply_broader_public_rc_claims_may_now_proceed() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    assert 'may now proceed' not in text.lower()
    assert 'Interface/runtime form (Window 623+) is' in text
    assert 'Broader public RC claims remain blocked until both spec form' in text


def test_capsule_v33_exists_and_contains_v33_version_marker() -> None:
    text = _read(CAPSULE_PATH)
    assert 'v3.3' in text
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v3.2.md' in text


def test_capsule_v33_contains_agent_skills_deferred_reference_and_does_not_claim_agent_skills_accepted_or_implemented() -> None:
    text = _read(CAPSULE_PATH)
    assert 'agent_skills_deferred_per_phase_612_priority_rule' in text
    assert 'Agent Skills deferred to post-619 window' in text
    assert 'Agent Skills accepted' not in text
    assert 'Agent Skills implemented' not in text


def test_phase_618_main_commit_touches_exactly_report_capsule_and_test_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_618_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_618_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_618_backfill_commit_touches_exactly_walkthrough_and_status_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_618_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_618_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
