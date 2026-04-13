from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_613_window_613_619_sequence_lock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_613_g8_window_613_619_sequence_lock_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_613_SUBJECT_TOKEN = 'phase 613 window 613-619 sequence lock'
PHASE_613_BACKFILL_SUBJECT_TOKEN = 'phase 613 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window summary',
    '## 2. Hard pass condition',
    '## 3. Mandatory dependency bundle',
    '## 4. Pre-lock blockers',
    '## 5. Phase table',
    '## 6. Locked implementation decisions',
    '## 7. Protected boundaries and anti-pattern exclusions',
    '## 8. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'mvp_gate_spec_lane_window_613_619_primary_gate',
    'spec_form_closure_necessary_but_not_sufficient_for_mvp_gate',
    'interface_runtime_form_required_window_623_plus',
    'broader_public_rc_claims_blocked_until_spec_and_runtime_both_complete',
    'agent_skills_deferred_per_phase_612_priority_rule',
    'no_wallet_widening_in_window_613_619',
    'no_payment_runtime_in_window_613_619',
    'no_chain_implementation_in_window_613_619',
    'post_612_priority_rule_receipts_lifecycle_wallet_init_precede_new_sub_lanes',
)
EXPECTED_PHASE_ROWS = (
    '| 613 | Window 613-619 sequence lock | `ilc_phase_613_619_sequence_lock_v0.1.md` | YES |',
    '| 614 | Public init/admission contract spec | init/admission contract spec | YES |',
    '| 615 | Visible ECU-to-ILC lifecycle contract spec | ECU lifecycle contract spec | YES |',
    '| 616 | Public receipt schema and query contract spec | receipt schema/query contract spec | No |',
    '| 617 | Public wallet surface contract spec | wallet surface contract spec | YES |',
    '| 618 | MVP gate spec synthesis + coherence report + capsule v3.3 | coherence report + capsule v3.3 | No |',
    '| 619 | Window 613-619 closure gate and handoff | gate script + handoff | YES |',
)
REQUIRED_REFERENCES = (
    '`docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`',
    '`docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md`',
    '`docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`',
    '`docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`',
    '`docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`',
    '`docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`',
    '`docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`',
    '`docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
)
REQUIRED_BLOCKERS = (
    'the Phase 612 closure memo is the governing input; it may not be silently',
    'the locked wallet boundary from Phase 576 and Phase 581 is not widened',
    'Agent Skills is explicitly deferred per the Phase 612 priority rule and may',
    'spec-form closure in this window does NOT open broader public RC claims',
    'the interface/runtime gate (Window 623+) remains required before broader',
)
LOCKED_DECISION_RULES = (
    'Window 613-619 is an MVP spec lane, not an implementation or runtime window',
    'Agent Skills is deferred to a post-619 window per the Phase 612 priority',
    'spec-form closure is necessary but NOT sufficient for the full MVP gate',
    'interface/runtime form (Window 623+) is still required',
    'broader public RC claims remain blocked until both spec AND runtime forms',
    'no wallet write, transfer, withdrawal, or spend authority is introduced',
    'the current read-only posture from Phase 576 and Phase 581 is preserved',
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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f'commit_not_yet_present:{subject_token}')


def test_sequence_lock_document_exists_and_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_seven_rows_for_phases_613_619_in_order() -> None:
    text = _read(SEQ_LOCK_PATH)
    rows: list[str] = []
    in_phase_table = False
    for line in text.splitlines():
        if line == '| Phase | Description | Primary output | Sensitive? |':
            in_phase_table = True
            continue
        if not in_phase_table:
            continue
        if line in EXPECTED_PHASE_ROWS:
            rows.append(line)
            continue
        if rows:
            break
    assert tuple(rows) == EXPECTED_PHASE_ROWS


def test_mandatory_dependency_bundle_contains_all_required_references() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_REFERENCES:
        assert item in text


def test_pre_lock_blockers_section_contains_all_required_blockers() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_BLOCKERS:
        assert item in text


def test_locked_implementation_decisions_record_agent_skills_deferral_and_interface_runtime_requirement() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in LOCKED_DECISION_RULES:
        assert item in text


def test_phase_613_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_613_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_613_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_613_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_613_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_613_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_613_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_613_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_613_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_613_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_613_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_613_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
