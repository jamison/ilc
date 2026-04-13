from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md')
TEST_PATH = Path('tests/test_phase_615_ecu_to_ilc_lifecycle_contract_spec.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_615_g8_ecu_to_ilc_lifecycle_contract_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_615_SUBJECT_TOKENS = ('phase 615', 'ecu to ilc lifecycle')
PHASE_615_BACKFILL_SUBJECT_TOKENS = ('phase 615', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. ECU-to-ILC lifecycle touchpoint target',
    '## 2. Dependency and inherited canon',
    '## 3. ECU layer boundary and attribution surface',
    '## 4. Epoch-commit and ILC settlement lifecycle',
    '## 5. Participant-visible surfaces',
    '## 6. Conversion cadence and deadline',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_GOVERNANCE_TOKENS = (
    'ecu_to_ilc_lifecycle_contract_spec_615_locked',
    'ecu_is_local_productive_credit_ilc_is_hard_settlement_asset',
    'ecu_ilc_layers_must_not_recollapse',
    'ecu_accrual_reaches_ilc_balance_only_through_epoch_commit',
    'issuance_epoch_cadence_cdl_027_one_month',
    'participant_visible_ecu_balance_is_read_only_visibility_only',
    'delayed_ilc_visibility_is_read_only_not_transfer_authority',
    'spec_form_closure_necessary_but_not_sufficient_for_mvp_gate',
    'interface_runtime_form_required_window_623_plus',
    'broader_public_rc_claims_remain_blocked_until_spec_and_runtime_both_complete',
    'no_public_claimability_or_spend_in_lifecycle_spec',
    'wallet_boundary_phase_576_and_581_preserved',
)
REQUIRED_SECTION_3_ITEMS = (
    'ECU is the local protocol-internal productive-credit layer.',
    '`rate = 0.20`',
    '`decay_floor = 0.05`',
    '`attribution_cap = 0.15`',
    'Participant-visible ECU balance is read-only accounting only.',
    'no write authority',
    'no transfer authority',
)
REQUIRED_SECTION_4_ITEMS = (
    'ECU accrual reaches ILC balance only through epoch commit.',
    'The settled internal balance is the only ILC balance class exposed as',
    '`balance_ilc`',
    'Deferred public-claimability state remains outside the current testnet scope.',
)
REQUIRED_VISIBLE_FIELDS = (
    '`balance_ilc`',
    '`last_settled_epoch_id`',
    '`reward_status`',
    '`history_digest`',
    '`latest_balance_receipt`',
)
REQUIRED_EXCLUSIONS = (
    'collapsing ECU and ILC into one undifferentiated layer',
    'treating participant-visible balance as public claimability',
    'any wallet widening beyond the read-only boundary from Phases 576 and 581',
    'any payment runtime or chain implementation reference as if authorized here',
    'reopening the ECU attribution rate as a governance target in this spec',
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


def test_spec_document_contains_required_governance_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_GOVERNANCE_TOKENS:
        assert token in text


def test_section_1_states_spec_form_only_target_window_623_plus_and_blocked_broader_public_rc_claims() -> None:
    text = _read(SPEC_PATH)
    assert 'This Phase 615 packet is a spec-form artifact only.' in text
    assert 'Interface/runtime form is deferred to Window 623+' in text
    assert (
        'Broader public RC claims remain blocked until both spec and runtime '
        'forms complete.'
    ) in text
    assert 'The Phase 609 ECU/ILC layer separation is controlling.' in text


def test_section_3_defines_ecu_layer_boundary_with_no_write_authority_assertion() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_SECTION_3_ITEMS:
        assert item in text


def test_section_4_defines_epoch_commit_lifecycle_and_ilc_balance_semantics() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_SECTION_4_ITEMS:
        assert item in text


def test_section_5_defines_participant_visible_surfaces_with_read_only_constraint() -> None:
    text = _read(SPEC_PATH)
    assert 'Participant-visible surfaces are limited to read-only accounting and visibility' in text
    assert 'ECU balance visibility:' in text
    assert 'ILC balance visibility:' in text
    for field_name in REQUIRED_VISIBLE_FIELDS:
        assert field_name in text
    assert 'No spend, transfer, withdrawal, or signing authority is exposed' in text


def test_section_6_states_cdl_027_issuance_epoch_cadence_one_month() -> None:
    text = _read(SPEC_PATH)
    assert 'The issuance epoch cadence is one month under the locked CDL-027 rule.' in text
    assert 'No amendment to the issuance cadence or the conversion deadline is authorized by' in text


def test_phase_615_main_commit_touches_expected_paths_only_and_no_cdl_adr_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_615_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_615_SUBJECT_TOKENS,
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


def test_phase_615_backfill_commit_subject_and_exact_path_set() -> None:
    _require_commit_or_skip(PHASE_615_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_615_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_615_backfill_commit_touches_no_cdl_adr_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_615_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_615_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
