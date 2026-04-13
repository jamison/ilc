from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_public_wallet_surface_contract_spec_617_v0.1.md')
TEST_PATH = Path('tests/test_phase_617_public_wallet_surface_contract_spec.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_617_g8_public_wallet_surface_contract_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_617_SUBJECT_TOKENS = ('phase 617', 'wallet')
PHASE_617_BACKFILL_SUBJECT_TOKENS = ('phase 617', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Wallet surface contract target and inherited boundary',
    '## 2. Permitted wallet query operations',
    '## 3. Wallet status and balance visibility contract',
    '## 4. Wallet history and attribution query contract',
    '## 5. Wallet export and accounting contract',
    '## 6. Prohibited wallet operations',
    '## 7. Explicit exclusions and deferred items',
)
REQUIRED_GOVERNANCE_TOKENS = (
    'public_wallet_surface_contract_spec_locked',
    'wallet_surface_is_read_only_and_accounting_only',
    'wallet_query_anchors_to_phase_576_and_phase_581',
    'wallet_status_exposes_settled_ilc_balance_only',
    'wallet_write_spend_transfer_withdrawal_explicitly_prohibited',
    'wallet_surface_does_not_widen_phase_576_boundary',
    'phase_617_carries_phase_612_mvp_gate_dependency',
    'wallet_query_is_fifth_of_five_mvp_touchpoints',
    'no_cdl_062_opening_in_wallet_surface_contract',
)
REQUIRED_OP_LINES = (
    '`wallet_status`: returns the participant\'s current settled ILC balance and',
    '`wallet_history`: returns the participant\'s settled balance history by epoch',
    '`wallet_export`: returns a machine-legible export of the participant\'s',
    '`ledger_summary`: returns a summary of the settlement ledger state for the',
)
REQUIRED_PROHIBITIONS = (
    '- wallet write operations of any kind',
    '- spend operations',
    '- transfer operations',
    '- withdrawal operations',
    '- minting operations',
    '- any operation that implies public claimability',
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


def test_spec_document_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_all_required_governance_tokens_are_present() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_GOVERNANCE_TOKENS:
        assert token in text


def test_section_1_states_governing_inputs_and_no_new_surfaces_beyond_current_bounded_posture() -> None:
    text = _read(SPEC_PATH)
    assert 'wallet/query touchpoint of the Phase 612 minimum' in text
    assert 'This packet specifies the public wallet query surface that already exists' in text
    assert 'It does not create new wallet surfaces' in text
    assert 'Phase 576 wallet boundary as the primary authority' in text
    assert 'Phase 581 settlement integration and wallet-query proof' in text
    assert 'Phase 615 lifecycle contract for delayed ILC visibility' in text
    assert 'ADR-0026 for the protocol-vs-harness product boundary' in text
    assert 'CDL-062 is not opened by this spec.' in text


def test_section_2_locks_exactly_four_permitted_operations_and_no_others() -> None:
    text = _read(SPEC_PATH)
    for line in REQUIRED_OP_LINES:
        assert line in text
    assert 'No other operations are permitted.' in text
    assert 'Any operation not in this list is prohibited' in text


def test_section_3_locks_wallet_status_response_with_claimability_state_deferred_as_mandatory() -> None:
    text = _read(SPEC_PATH)
    assert '`wallet_status` returns a JSON object with fields:' in text
    assert '- `agent_id` (key-derived)' in text
    assert '- `balance_ilc` (settled internal balance)' in text
    assert '- `ecu_accrual` (current-epoch ECU accrual, advisory)' in text
    assert '- `claimability_state` (string: `deferred`)' in text
    assert '`claimability_state` must always be `deferred` in the current bounded posture.' in text
    assert '`balance_ilc` is the only balance class exposed.' in text


def test_section_6_explicitly_prohibits_write_spend_transfer_withdrawal_and_minting_operations() -> None:
    text = _read(SPEC_PATH)
    for line in REQUIRED_PROHIBITIONS:
        assert line in text
    assert '- any operation that interacts with an external chain, blockchain, or rollup' in text
    assert '- any wallet UX flow that silently widens the bounded accounting surface' in text


def test_section_7_defers_runtime_implementation_and_claimability_resolution() -> None:
    text = _read(SPEC_PATH)
    assert '- runtime implementation of the wallet query surface' in text
    assert '- public claimability posture resolution' in text
    assert '- wallet create/import/export UX flows' in text
    assert '- any reputation portability or cross-epoch balance transfer mechanism' in text


def test_phase_617_main_commit_touches_exactly_spec_and_test_paths() -> None:
    _require_commit_or_skip(PHASE_617_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_617_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_617_main_commit_touches_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_617_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_617_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_617_backfill_commit_touches_exactly_walkthrough_and_status_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_617_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_617_BACKFILL_SUBJECT_TOKENS,
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
