from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

RECONCILIATION_PATH = Path('docs/specs/ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_609_ecu_ilc_runtime_boundary_reconciliation.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_609_g8_window_607_612_ecu_ilc_runtime_boundary_reconciliation_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_609_SUBJECT_TOKEN = 'phase 609 ecu ilc runtime boundary reconciliation'
PHASE_609_BACKFILL_SUBJECT_TOKEN = 'phase 609 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RECONCILIATION_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Reconciliation target and inherited authority stack',
    '## 2. ECU layer and local/protocol-internal semantics',
    '## 3. ILC layer and hard-settlement semantics',
    '## 4. Current RC/runtime posture versus final-substrate non-closure',
    '## 5. Public auditability versus identity/privacy boundary',
    '## 6. Carry-forward constraints into Phase 610 and Phase 611',
)
REQUIRED_TOKENS = (
    'phase_609_reconciliation_separates_ecu_ilc_and_current_runtime_without_selecting_final_substrate',
    'ecu_is_local_protocol_internal_productive_credit_layer',
    'ilc_is_hard_settlement_asset_with_final_substrate_still_unresolved',
    'current_rc_runtime_internal_ledger_is_bounded_current_posture_not_forever_substrate',
    'wallet_handoff_line_12_ilc_ecu_conflation_rejected_as_stable_authority',
    'wallet_agnostic_signing_is_signing_provider_compatibility_not_substrate_closure',
    'public_auditability_is_not_public_identity_exposure',
    'phase_609_reconciliation_does_not_authorize_payment_lane_or_wallet_widening',
    'phase_610_options_matrix_must_consume_phase_609_layer_separation',
)
SECTION_2_STRINGS = (
    '`ECU` is the local/protocol-internal productive-credit layer',
    'may describe ECU circulation without implying public-chain settlement',
    'does not reopen transfer or write-authority boundaries fixed by Phases 576 and 581',
)
SECTION_3_STRINGS = (
    '`ILC` is the hard settlement asset in the design corpus',
    'final long-run public settlement substrate for `ILC` remains unresolved',
    'December 2025 later-chain direction remains legitimate historical strategy',
    'line-12 `ILC coin (ECU)` sentence in the wallet handoff is rejected as',
    'line-105 anti-blockchain sentence in the wallet handoff is not sufficient',
)
SECTION_4_STRINGS = (
    'current RC/runtime is an internal epoch-settled ledger with read-only',
    'bounded current implementation truth, not forever-substrate closure by implication',
    'Phase 600 remains a bounded evidence surface only',
    'Phase 602 remains a bounded current public-claims surface only',
)
SECTION_5_STRINGS = (
    'Public auditability is not identical to public identity exposure.',
    'directly correlatable public identity artifacts are not assumed by default',
    'mandatory input to Phase 610',
)
SECTION_6_STRINGS = (
    'Phase 610 must consume the `ECU` / `ILC` / runtime separation from this memo.',
    'Phase 611 remains conditional and may not be pre-opened here.',
    'No payment-lane progress or wallet-authority widening is authorized by Phase',
)
FORBIDDEN_SCOPE_STRINGS = (
    'does not pick a public-ledger path',
    'not forever-substrate closure',
    'No payment-lane progress or wallet-authority widening is authorized',
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


def test_reconciliation_memo_exists_and_contains_required_headings() -> None:
    text = _read(RECONCILIATION_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_reconciliation_memo_contains_required_tokens() -> None:
    text = _read(RECONCILIATION_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_2_explicitly_classifies_ecu_as_local_protocol_internal_productive_credit() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in SECTION_2_STRINGS:
        assert item in text


def test_section_3_explicitly_classifies_ilc_as_hard_settlement_asset_with_final_substrate_unresolved() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in SECTION_3_STRINGS:
        assert item in text


def test_section_4_explicitly_records_current_runtime_posture_as_bounded_current_implementation() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in SECTION_4_STRINGS:
        assert item in text


def test_section_5_explicitly_separates_public_auditability_from_public_identity_exposure() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in SECTION_5_STRINGS:
        assert item in text


def test_section_6_explicitly_routes_phase_610_and_preserves_phase_611_as_conditional_only() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in SECTION_6_STRINGS:
        assert item in text


def test_reconciliation_memo_explicitly_preserves_forbidden_scope_boundaries() -> None:
    text = _read(RECONCILIATION_PATH)
    for item in FORBIDDEN_SCOPE_STRINGS:
        assert item in text


def test_phase_609_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_609_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_609_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_609_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_609_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_609_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_609_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_609_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_609_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_609_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_609_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_609_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
