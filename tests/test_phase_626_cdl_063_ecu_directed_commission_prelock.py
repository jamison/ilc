from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

PRELOCK_PATH = Path('docs/specs/ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md')
SIM_PATH = Path('docs/specs/ilc_sim_commission_01_earmark_expiry_calibration_626_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_626_cdl_063_ecu_directed_commission_prelock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_626_g8_cdl_063_prelock_and_sim_commission_01_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_626_SUBJECT_TOKEN = 'phase 626 cdl-063 prelock hardening and sim-commission-01'
PHASE_626_BACKFILL_SUBJECT_TOKEN = 'phase 626 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(PRELOCK_PATH),
    str(SIM_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Prelock identity and CDL-063 open state verification',
    '## 2. Earmark mechanics constitutional clause (prelock form)',
    '## 3. Anti-gaming constitutional clause (prelock form)',
    '## 4. Attribution non-inflation constitutional clause (prelock form)',
    '## 5. SIM-COMMISSION-01 expiry parameter dependency',
    '## 6. Mutation scope and invariants',
)
REQUIRED_TOKENS = (
    'cdl_063_prelock_626_locked',
    'cdl_063_open_state_verified_at_626',
    'earmark_mechanics_constitutional_clause_prelocked',
    'anti_gaming_constitutional_clause_prelocked',
    'attribution_non_inflation_constitutional_clause_prelocked',
    'cdl_063_ratification_requires_sim_commission_01_expiry_value',
    'cdl_063_prelock_mutation_scope_additive_only',
)
SIM_REQUIRED_TOKENS = (
    'sim_commission_01_expiry_calibration_complete',
    'sim_commission_01_minimum_expiry_validation_epochs: 240',
    'sim_commission_01_nominal_expiry_validation_epochs: 1440',
    'sim_commission_01_maximum_expiry_validation_epochs: 10080',
    'sim_commission_01_tiered_expiry_disposition: reject_tiered_keep_fixed_v1',
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


def test_prelock_document_exists_and_contains_required_headings() -> None:
    text = _read(PRELOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_document_contains_required_tokens() -> None:
    text = _read(PRELOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_one_contains_explicit_open_state_verification() -> None:
    text = _read(PRELOCK_PATH)
    assert 'CDL-063 was read at Phase 626 and confirmed `status: open`.' in text


def test_section_two_contains_all_lifecycle_states_and_balance_invariant() -> None:
    text = _read(PRELOCK_PATH)
    for state in ('proposed', 'accepted', 'delivered', 'debited', 'expired'):
        assert state in text
    assert "earmarked ECU may not exceed A's current unearmarked accrued balance at" in text
    assert 'Debit occurs at the epoch commit following delivery' in text


def test_section_three_contains_all_anti_gaming_invariants() -> None:
    text = _read(PRELOCK_PATH)
    assert 'distinct canonical agent_ids' in text
    assert 'same-key' in text
    assert 'full CDL-V7' in text
    assert 'automatically released' in text
    assert 'No rollover or extension is permitted without a new earmark proposal.' in text


def test_section_four_contains_formal_non_inflation_statements() -> None:
    text = _read(PRELOCK_PATH)
    assert '`ecu_credit(B) = attribution_formula(contribution_W_e)`' in text
    assert '`ecu_debit(A) = earmark_amount`' in text


def test_sim_document_contains_required_tokens_and_recommended_values() -> None:
    text = _read(SIM_PATH)
    assert '## 1. Simulation identity and question' in text
    assert '## 2. Parameters and assumptions' in text
    assert '## 3. Analysis' in text
    assert '## 4. Results' in text
    assert '## 5. Governance dispositions' in text
    assert '## 6. Forward pointer' in text
    for token in SIM_REQUIRED_TOKENS:
        assert token in text
    assert '`recommended_fixed_expiry_validation_epochs = 1440`' in text


def test_phase_626_main_commit_touches_expected_paths_only_and_cdl_063_remains_open() -> None:
    _require_commit_or_skip(PHASE_626_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_626_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-063']['status'] == 'open'
    assert 'ratified_phase' not in rows['CDL-063']


def test_phase_626_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_626_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_626_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
