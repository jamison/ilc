from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

EVIDENCE_PATH = Path('docs/specs/ilc_cdl_063_ecu_directed_commission_ratification_evidence_627_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_627_cdl_063_ecu_directed_commission_ratification.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_627_g8_cdl_063_ratification_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_627_EVIDENCE_SUBJECT = 'phase 627 cdl-063 ecu directed commission ratification evidence'
PHASE_627_RATIFIED_SUBJECT = 'phase 627 cdl-063 ratified'
PHASE_627_BACKFILL_SUBJECT = 'phase 627 walkthrough and status backfill'
EXACT_REQUIRED_EVIDENCE_PATHS = {str(EVIDENCE_PATH), str(TEST_PATH)}
EXACT_REQUIRED_CDL_PATHS = {str(DECISION_LOG_PATH)}
EXACT_REQUIRED_BACKFILL_PATHS = {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
REQUIRED_HEADINGS = (
    '## 1. Ratification identity and prelock lineage',
    '## 2. Final constitutional clause text',
    '## 3. SIM-COMMISSION-01 expiry parameter resolution',
    '## 4. Ratification readiness evidence checklist satisfaction',
    '## 5. Mutation scope and invariants',
)
REQUIRED_TOKENS = (
    'cdl_063_ratified_627',
    'cdl_063_earmark_semantics_ratified',
    'cdl_063_debit_authority_ratified',
    'cdl_063_anti_gaming_invariants_ratified',
    'cdl_063_attribution_non_inflation_ratified',
    'cdl_063_expiry_parameter_locked: fixed_2880_validation_epochs',
    'cdl_063_not_ilc_payment_ratified',
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


def test_evidence_document_exists_and_contains_required_headings() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_evidence_document_contains_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_contains_all_four_constitutional_clauses_and_invariants() -> None:
    text = _read(EVIDENCE_PATH)
    assert '**Clause A — Earmark semantics**' in text
    for state in ('`proposed`', '`accepted`', '`delivered`', '`debited`', '`expired`'):
        assert state in text
    assert '**Clause B — Debit authority**' in text
    assert 'No manual override, rollover, or extension is permitted.' in text
    assert '**Clause C — Anti-gaming invariants**' in text
    assert 'CDL-042' in text
    assert 'key-derivation roots' in text
    assert 'full CDL-V7 Popperian' in text
    assert '**Clause D — Attribution non-inflation**' in text
    assert '`ecu_credit(performing_agent) = attribution_formula(contribution_W_e)`' in text
    assert '`ecu_debit(commissioning_agent) = earmark_amount`' in text


def test_section_three_records_ratified_expiry_parameter() -> None:
    text = _read(EVIDENCE_PATH)
    assert 'minimum viable expiry: `240` validation epochs' in text
    assert 'nominal recommended fixed expiry: `2880` validation epochs' in text
    assert 'maximum sensible expiry: `10080` validation epochs' in text
    assert 'cdl_063_expiry_parameter_locked: fixed_2880_validation_epochs' in text


def test_section_four_heading_is_exact_and_checklist_items_are_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert '## 4. Ratification readiness evidence checklist satisfaction' in text
    assert 'ecu_active_layer_architecture_scoping_625_locked' in text
    assert 'cdl_063_prelock_626_locked' in text
    assert 'sim_commission_01_expiry_calibration_complete' in text
    assert 'cdl_063_option_b_selected_bounded_earmark_with_debit' in text
    assert 'cdl_063_not_ilc_payment_ratified' in text


def test_cdl_063_row_is_ratified_after_commit_2() -> None:
    _require_commit_or_skip(PHASE_627_RATIFIED_SUBJECT)
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-063']['status'] == 'ratified'
    assert rows['CDL-063']['ratified_phase'] == '627'
    assert rows['CDL-063']['evidence_document'] == str(EVIDENCE_PATH)


def test_commit_1_evidence_touches_expected_paths_only_and_no_cdl_mutation() -> None:
    _require_commit_or_skip(PHASE_627_EVIDENCE_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_627_EVIDENCE_SUBJECT,
        expected_paths=EXACT_REQUIRED_EVIDENCE_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_EVIDENCE_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_commit_2_cdl_update_touches_decision_log_only() -> None:
    _require_commit_or_skip(PHASE_627_RATIFIED_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_627_RATIFIED_SUBJECT,
        expected_paths=EXACT_REQUIRED_CDL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_CDL_PATHS
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-063']['status'] == 'ratified'
    assert rows['CDL-063']['ratified_phase'] == '627'


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_627_BACKFILL_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_627_BACKFILL_SUBJECT,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
