from __future__ import annotations

import subprocess
from pathlib import Path

REPORT_PATH = Path('docs/specs/ilc_integration_coherence_report_604_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v3.2.md')
TEST_PATH = Path('tests/test_phase_604_coherence_report_and_capsule_v3_2.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_604_g8_coherence_report_and_capsule_v3_2_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_604_SUBJECT_TOKEN = 'phase 604 coherence report'
PHASE_604_BACKFILL_SUBJECT_TOKEN = 'phase 604 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(REPORT_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window 596-605 coherence target',
    '## 2. Closure-state intake from phases 597-603',
    '## 3. Frozen inherited boundaries from phases 585-595',
    '## 4. Remaining later-lane defers and non-goals',
    '## 5. Next approved closure step',
)
REQUIRED_REPORT_TOKENS = (
    'window_596_605_genesis_closure_band_recorded_in_coherence',
    'phase_597_602_genesis_closure_band_complete',
    'phase_603_synthesis_addendum_complete',
    'frozen_585_595_boundaries_preserved_in_coherence',
    'remaining_later_lane_defers_explicit_after_602',
    'phase_605_closure_gate_must_consume_phase_604_coherence_state',
)
SECTION_TWO_ITEMS = (
    '`docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`',
    '`docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`',
    '`docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`',
    '`docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`',
    '`docs/specs/ilc_post_genesis_capability_proof_disposition_and_bootstrap_transition_boundary_601_v0.1.md`',
    '`docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`',
    '`docs/specs/ilc_genesis_carry_forward_synthesis_and_readiness_delta_addendum_603_v0.1.md`',
)
SECTION_THREE_RULES = (
    'frozen_585_595_boundaries_preserved_in_coherence',
    'the 585-594 public boundary window recorded in',
    'the bounded RC0.1 closure packet recorded in',
    'does not reopen the public identity, quorum, settlement, release-claim, or fork-legitimacy surfaces',
)
SECTION_FOUR_RULES = (
    'remaining_later_lane_defers_explicit_after_602',
    'completion of the Phase 305 canonical output package',
    'any Genesis economics runtime-alignment packet beyond bounded Phase 600',
    'any Genesis-only ECU realization-controller implementation packet',
    'the actual capability-proof runtime lane and post-bootstrap non-privileged',
    'the Phase 605 closure gate and handoff',
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


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def test_report_exists_and_contains_all_required_section_headings() -> None:
    text = _read(REPORT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_report_contains_all_required_report_tokens() -> None:
    text = _read(REPORT_PATH)
    for token in REQUIRED_REPORT_TOKENS:
        assert token in text


def test_report_section_two_references_phases_597_603() -> None:
    text = _read(REPORT_PATH)
    for item in SECTION_TWO_ITEMS:
        assert item in text


def test_report_section_three_records_the_frozen_585_595_boundary_rule() -> None:
    text = _read(REPORT_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_report_section_four_records_remaining_later_lane_defers() -> None:
    text = _read(REPORT_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_capsule_v3_2_exists_and_references_phase_605_as_next_only() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Capsule v3.2 supersedes v3.1.' in text
    assert 'Window 596-605 is at coherence-report stage.' in text
    assert 'Phase 605 is the only next authorized closure step for Window 596-605.' in text
    assert 'Window 606+ is not authorized by capsule v3.2 by itself.' in text


def test_main_commit_touches_exactly_report_capsule_and_test() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_604_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_adr_path_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_604_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_exactly_walkthrough_and_status_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_604_BACKFILL_SUBJECT_TOKEN, expected_paths=EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
