from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

MATRIX_PATH = Path('docs/specs/ilc_public_ledger_substrate_options_and_rejection_matrix_610_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_610_public_ledger_substrate_options_and_rejection_matrix.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_610_g8_window_607_612_public_ledger_substrate_options_and_rejection_matrix_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_610_SUBJECT_TOKEN = 'phase 610 public ledger substrate options matrix'
PHASE_610_BACKFILL_SUBJECT_TOKEN = 'phase 610 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(MATRIX_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Matrix target and inherited reconciliation state',
    '## 2. Evaluation criteria and non-goals',
    '## 3. Option A - Internal-ledger-final posture',
    '## 4. Option B - Custom minimal L1',
    '## 5. Option C - External rollup or L2 substrate',
    '## 6. Option D - Deferred-substrate ledger-interface path',
    '## 7. Comparative matrix and keep/defer/reject rationale',
    '## 8. Carry-forward constraints into Phase 611',
)
REQUIRED_TOKENS = (
    'phase_610_options_matrix_evaluates_substrate_paths_without_selecting_runtime_implementation',
    'internal_ledger_final_path_explicitly_evaluated',
    'custom_minimal_l1_path_explicitly_evaluated',
    'external_rollup_or_l2_path_explicitly_evaluated',
    'deferred_substrate_ledger_interface_path_explicitly_evaluated',
    'every_substrate_option_carries_keep_defer_or_reject_rationale',
    'public_auditability_and_identity_privacy_constraints_apply_to_every_option',
    'phase_610_does_not_authorize_wallet_widening_chain_implementation_or_payment_runtime',
    'phase_611_must_choose_governance_vehicle_from_phase_610_outcome',
)
OPTION_SECTION_STRINGS = (
    '## 3. Option A - Internal-ledger-final posture',
    '## 4. Option B - Custom minimal L1',
    '## 5. Option C - External rollup or L2 substrate',
    '## 6. Option D - Deferred-substrate ledger-interface path',
    'Keep/defer/reject rationale:',
)
SECTION_2_STRINGS = (
    'compatibility with the current locked runtime and wallet boundary',
    'compatibility with the ECU/ILC separation established in Phase 609',
    'compatibility with bounded current public-claims and evidence surfaces from',
    'accepted-boundary precedence established in Phase 608',
    'preservation of the distinction between public auditability and public',
    'no implementation work,',
    'no wallet widening,',
    'no payment-lane widening,',
)
SECTION_7_STRINGS = (
    '| Option | Authority compatibility | Runtime-boundary compatibility | Auditability/privacy compatibility | Implementation risk | Public-legitimacy implications | Outcome |',
    'internal-ledger-final posture',
    'custom minimal L1',
    'external rollup or L2',
    'deferred-substrate ledger-interface',
    'reject',
    'defer',
    'keep',
)
SECTION_8_STRINGS = (
    'Phase 611 remains the governance-vehicle selection lane only.',
    'Phase 610 does not open or ratify any ADR or CDL.',
    'Phase 611 must therefore choose the governance vehicle without pretending the',
    'memo, ADR, or CDL routing is required before any implementation',
)
FORBIDDEN_SCOPE_STRINGS = (
    'does not open or ratify any ADR or CDL',
    'does not authorize wallet widening, chain implementation, or payment runtime',
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


def test_matrix_document_exists_and_contains_required_headings() -> None:
    text = _read(MATRIX_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_matrix_document_contains_required_tokens() -> None:
    text = _read(MATRIX_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sections_3_through_6_each_evaluate_required_option_and_contain_keep_defer_reject_rationale() -> None:
    text = _read(MATRIX_PATH)
    for item in OPTION_SECTION_STRINGS:
        assert item in text
    assert text.count('Keep/defer/reject rationale:') == 4


def test_section_2_contains_required_evaluation_criteria_and_non_goals() -> None:
    text = _read(MATRIX_PATH)
    for item in SECTION_2_STRINGS:
        assert item in text


def test_section_7_contains_comparative_matrix_covering_required_dimensions() -> None:
    text = _read(MATRIX_PATH)
    for item in SECTION_7_STRINGS:
        assert item in text


def test_section_8_explicitly_preserves_phase_611_as_governance_vehicle_selection_only() -> None:
    text = _read(MATRIX_PATH)
    for item in SECTION_8_STRINGS:
        assert item in text


def test_matrix_document_explicitly_states_phase_610_does_not_authorize_wallet_widening_chain_implementation_or_payment_runtime() -> None:
    text = _read(MATRIX_PATH)
    for item in FORBIDDEN_SCOPE_STRINGS:
        assert item in text


def test_phase_610_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_610_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_610_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_610_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_610_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_610_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_610_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_610_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_610_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_610_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_610_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_610_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
