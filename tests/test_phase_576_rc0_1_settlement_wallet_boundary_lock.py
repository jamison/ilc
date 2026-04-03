from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_576_rc0_1_settlement_wallet_boundary_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_576_g8_rc0_1_settlement_wallet_boundary_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_576_SUBJECT_TOKEN = 'phase 576 rc0.1 settlement wallet boundary lock'
PHASE_576_BACKFILL_SUBJECT_TOKEN = 'phase 576 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Bounded RC target',
    '## 2. Settlement meaning in RC0.1',
    '## 3. Balance-state classification',
    '## 4. Wallet boundary and authority split',
    '## 5. Replay and idempotency rule',
    '## 6. Explicit deferrals to RC0.1+',
)
REQUIRED_TOKENS = (
    'rc0_1_balance_visibility_does_not_imply_public_claimability',
    'ecu_accrual_reaches_ilc_balance_only_through_epoch_commit',
    'wallet_visibility_and_accounting_only',
    'wallet_has_no_ledger_write_authority',
    'wallet_signing_spend_transfer_deferred_post_rc0_1',
    'settlement_replay_must_fail_closed_or_noop_without_balance_drift',
    'founder_and_genesis_reward_split_deferred_to_public_rc_packet',
)
SETTLEMENT_RULES = (
    'RC0.1 ILC balance means a settled internal ledger balance produced by the',
    'A visible RC0.1 balance is operator-queryable and machine-queryable',
    'A visible RC0.1 balance does not, by itself, imply public withdrawal,',
)
WALLET_BOUNDARY_RULES = (
    'Wallet status, history, and export are read-only visibility and accounting',
    'Wallet queries must read settled ledger state deterministically.',
    'Wallet queries must not mutate ledger, graph, or settlement state.',
    '`balance_ilc`',
    '`last_settled_epoch_id`',
    '`reward_status`',
    'settled history receipts',
)
AUDIT_HISTORY_SURFACE_RULES = (
    '`history_digest`',
    '`latest_balance_receipt`',
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


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_contains_all_bounded_settlement_rules() -> None:
    text = _read(DOC_PATH)
    for rule in SETTLEMENT_RULES:
        assert rule in text


def test_section_four_contains_read_only_wallet_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for rule in WALLET_BOUNDARY_RULES:
        assert rule in text


def test_section_four_records_machine_auditable_history_surface() -> None:
    text = _read(DOC_PATH)
    for rule in AUDIT_HISTORY_SURFACE_RULES:
        assert rule in text


def test_phase_576_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_576_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_576_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_576_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_576_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_576_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_576_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_576_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
