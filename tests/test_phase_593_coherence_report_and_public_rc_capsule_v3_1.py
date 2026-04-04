from __future__ import annotations

import subprocess
from pathlib import Path

REPORT_PATH = Path('docs/specs/ilc_integration_coherence_report_593_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v3.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_593_coherence_report_and_public_rc_capsule_v3_1.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_593_g8_coherence_report_and_public_rc_capsule_v3_1_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
EXACT_REQUIRED_MAIN_PATHS = {
    str(REPORT_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
PHASE_593_SUBJECT_TOKEN = 'phase 593 coherence report and capsule v3.1'
PHASE_593_BACKFILL_SUBJECT_TOKEN = 'phase 593 walkthrough and status backfill'
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_REPORT_TOKENS = (
    'public_boundary_closure_band_587_590_complete',
    'public_runtime_integration_boundary_591_complete',
    'operator_honesty_package_592_complete',
    'public_rc_claim_bounded_and_honesty_disciplined',
    'genesis_dilution_freshness_and_accrual_items_still_open',
    'capability_proof_lane_still_separate_future_work',
    'harness_boundary_and_protocol_boundary_preserved',
    'window_585_594_closure_gate_next',
    'phase_594_closure_gate_must_consume_phase_593_coherence_state',
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


def test_coherence_report_exists_and_contains_all_required_tokens() -> None:
    text = _read(REPORT_PATH)
    for token in REQUIRED_REPORT_TOKENS:
        assert token in text


def test_capsule_exists_and_is_versioned_v3_1() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Capsule v3.1 supersedes v3.0.' in text
    assert 'Window 585-594 is at closure-gate stage.' in text


def test_report_records_closure_band_runtime_integration_and_honesty_package_as_complete() -> None:
    text = _read(REPORT_PATH)
    assert 'The public constitutional closure band is complete.' in text
    assert 'The runtime/proof lane now records itself as a bounded bridge' in text
    assert 'The public release-claim package is coherent with the runtime bridge packet.' in text


def test_report_records_remaining_genesis_carry_forward_items_and_separate_capability_proof_lane_correctly() -> None:
    text = _read(REPORT_PATH)
    for item in (
        '- Genesis governance dilution closure',
        '- freshness-gate provenance closure',
        '- Genesis accrual-governor provenance reconciliation',
        'The post-Genesis capability-proof lane remains separate future work.',
    ):
        assert item in text


def test_capsule_states_phase_594_as_next_authorized_step_and_does_not_authorize_window_595_plus_by_itself() -> None:
    text = _read(CAPSULE_PATH)
    assert 'Phase 594 is the next authorized phase.' in text
    assert 'Window 595+ is not authorized by capsule v3.1 by itself.' in text


def test_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_593_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_main_commit_touches_no_cdl_path_no_adr_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_593_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_593_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_backfill_commit_touches_no_cdl_path_no_adr_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_593_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
