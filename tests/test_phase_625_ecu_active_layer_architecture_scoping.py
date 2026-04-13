from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SCOPING_PATH = Path('docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_625_ecu_active_layer_architecture_scoping.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_625_g8_ecu_active_layer_architecture_scoping_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_624_TEST_PATH = Path('tests/test_phase_624_window_624_630_sequence_lock.py')
PHASE_624_SUBJECT_TOKEN = 'phase 624 window 624-630 sequence lock'
PHASE_625_SUBJECT_TOKEN = 'phase 625 ecu active layer architecture scoping and cdl-063 opening stub'
PHASE_625_BACKFILL_SUBJECT_TOKEN = 'phase 625 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SCOPING_PATH),
    str(TEST_PATH),
    str(DECISION_LOG_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Authorization basis and scoping target',
    '## 2. Earmark mechanics and balance accounting model',
    '## 3. Anti-gaming constraints',
    '## 4. Attribution non-inflation proof',
    '## 5. CDL-063 options evaluation',
    '## 6. Selected direction and forward pointer',
)
REQUIRED_TOKENS = (
    'ecu_active_layer_architecture_scoping_625_locked',
    'cdl_063_opened_as_stub',
    'earmark_mechanics_answered',
    'anti_gaming_constraints_answered',
    'attribution_non_inflation_answered',
    'cdl_063_option_b_selected_bounded_earmark_with_debit',
    'ecu_debit_not_ilc_payment_625',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f'commit_not_yet_present:{subject_token}')


def test_scoping_document_exists_and_contains_required_headings() -> None:
    text = _read(SCOPING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_scoping_document_contains_required_tokens() -> None:
    text = _read(SCOPING_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_defines_earmark_lifecycle_states_and_balance_invariant() -> None:
    text = _read(SCOPING_PATH)
    assert "`spendable_ecu(A) = total_accrued_ecu(A) - reserved_earmarks(A)`" in text
    assert 'where reserved means earmarks in `proposed`, `accepted`, or `delivered` state' in text
    for state in ('`proposed`', '`accepted`', '`delivered`', '`debited`', '`expired`'):
        assert state in text
    assert 'Agent A cannot earmark more than their current unearmarked accrued ECU balance at the time of proposal' in text


def test_section_three_defines_arms_length_popperian_and_expiry_constraints() -> None:
    text = _read(SCOPING_PATH)
    assert 'distinct canonical `agent_id` values' in text
    assert 'Same-key self-commission is prohibited' in text
    assert 'must enter through the standard authored-envelope' in text
    assert 'pass the full CDL-V7 Popperian gate' in text
    assert 'transitions to `expired` state' in text
    assert 'returns to Agent A' in text
    assert '`M` is a calibration parameter reserved for SIM-COMMISSION-01 in Phase 626' in text


def test_section_four_contains_formal_non_inflation_statements() -> None:
    text = _read(SCOPING_PATH)
    assert '`ecu_credit(B) = attribution_formula(contribution_W_e)`' in text
    assert '`ecu_debit(A) = earmark_amount`' in text
    assert 'The earmark is a coordination contract, not an attribution inflation mechanism.' in text


def test_section_five_evaluates_all_three_options_with_rejection_rationale() -> None:
    text = _read(SCOPING_PATH)
    assert 'Option A: earmark-only, no debit.' in text
    assert 'Rejected. This reproduces the Phase 622 topology without enforcement.' in text
    assert 'Option B: bounded earmark with debit on delivery.' in text
    assert 'Selected. This provides enforceable reservation and debit semantics' in text
    assert 'Option C: generalized ECU transfer.' in text
    assert 'Rejected. This exceeds `CDL-063` scope' in text


def test_cdl_063_row_exists_at_phase_625_commit_with_expected_open_state() -> None:
    _require_commit_or_skip(PHASE_625_SUBJECT_TOKEN)
    phase_624_ref = _resolve_commit_ref(
        subject_token=PHASE_624_SUBJECT_TOKEN,
        expected_paths={
            'docs/specs/ilc_phase_624_630_sequence_lock_v0.1.md',
            str(PHASE_624_TEST_PATH),
        },
    )
    phase_625_ref = _resolve_commit_ref(
        subject_token=PHASE_625_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    old_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), phase_624_ref))
    new_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), phase_625_ref))
    assert 'CDL-063' not in old_rows
    assert 'CDL-063' in new_rows
    assert new_rows['CDL-063']['status'] == 'open'
    assert new_rows['CDL-063']['related_clause'] == 'CDL-027 / CDL-044 / Phase-622 / Phase-550'
    assert new_rows['CDL-063']['decision_topic'] == 'ECU directed-commission earmark and bounded debit semantics for agent-commissioning-agent protocol-level coordination'
    assert new_rows['CDL-063']['options'] == 'earmark-only-no-debit, bounded-earmark-with-debit-on-delivery, generalized-ecu-transfer'
    assert new_rows['CDL-063']['current_candidate'] == 'bounded-earmark-with-debit-on-delivery'
    assert new_rows['CDL-063']['required_artifacts'] == (
        'docs/specs/ilc_phase_624_630_sequence_lock_v0.1.md, '
        'docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md, '
        'docs/specs/ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md'
    )
    assert 'ratified_phase' not in new_rows['CDL-063']
    assert 'ratified_date' not in new_rows['CDL-063']
    assert 'evidence_document' not in new_rows['CDL-063']
    for cdl_id, old_row in old_rows.items():
        assert new_rows[cdl_id] == old_row


def test_phase_625_main_and_backfill_commits_touch_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_625_BACKFILL_SUBJECT_TOKEN)
    main_ref = _resolve_commit_ref(
        subject_token=PHASE_625_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    backfill_ref = _resolve_commit_ref(
        subject_token=PHASE_625_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(main_ref) == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) in _changed_paths_for_commit(main_ref)
    assert not any(path.startswith('ilc_core/') for path in _changed_paths_for_commit(main_ref))
    assert _changed_paths_for_commit(backfill_ref) == EXACT_REQUIRED_BACKFILL_PATHS
    assert not any(path.startswith('ilc_core/') for path in _changed_paths_for_commit(backfill_ref))
