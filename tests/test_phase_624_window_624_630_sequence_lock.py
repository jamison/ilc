from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_624_630_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_624_window_624_630_sequence_lock.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_624_g8_window_624_630_sequence_lock_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_624_SUBJECT_TOKEN = 'phase 624 window 624-630 sequence lock'
PHASE_624_BACKFILL_SUBJECT_TOKEN = 'phase 624 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window identity and authorization basis',
    '## 2. Phase map and hard pass conditions',
    '## 3. AG-gate design basis',
    '## 4. CDL-063 vehicle declaration',
    '## 5. Inherited boundary state',
    '## 6. Per-phase scope constraints',
    '## 7. Window-level exclusions',
)
REQUIRED_TOKENS = (
    'window_624_630_sequence_lock_primary_gate',
    'cdl_063_named_as_vehicle_for_ecu_directed_commission',
    'ag8_named_vehicle_rule_satisfied_window_624_630',
    'window_624_630_parallel_to_window_623_plus',
    'cdl_062_remains_not_authorized_in_window_624_630',
    'option_d_posture_active_in_window_624_630',
    'wallet_boundary_576_581_unchanged_in_window_624_630',
    'ecu_debit_not_ilc_payment_window_624_630',
    'window_624_630_requires_window_620_622_complete',
    'sim_commission_01_required_in_phase_626',
    'disposition_b_not_permitted_window_624_630',
    'runtime_hardening_gate_required_in_phase_629',
)
REQUIRED_AUTHORIZATION_SNIPPETS = (
    'Human authorization 2026-04-13: the debit-side gap in Phase 622 was approved',
    'Human authorization 2026-04-13: `Disposition B` is rejected for this lane',
    'Phase 622 `bounded_ecu_exchange_model_622_locked` established the topology',
    'AG-8 named-vehicle rule applies from Window 624 forward',
)
REQUIRED_HARD_PASS_SNIPPETS = (
    '`CDL-063` is opened as a stub row in Phase 625 and ratified in Phase 627',
    'SIM-COMMISSION-01 runs in Phase 626 and produces calibrated expiry guidance',
    'Phase 628 runtime implementation and accounting spec both exist and pass tests',
    'Phase 629 runtime hardening gate passes with no wallet widening and no ILC transferability',
    'Phase 630 handoff records ratification, runtime implementation, hardening verdict, and deferred items',
)
AG_GATE_ROWS = (
    '| AG-1 Co-flourishing mission |',
    '| AG-2 W_e increase |',
    '| AG-3 Epistemic integrity |',
    '| AG-4 ECU-ILC separation |',
    '| AG-5 Harness-agnostic |',
    '| AG-6 Near-infinite scale |',
    '| AG-7 Machine-legible first |',
    '| AG-8 Outbound economic loop |',
)
REQUIRED_VEHICLE_SNIPPETS = (
    '`CDL-063` title: *ECU Directed-Commission Earmark and Bounded Debit Semantics*.',
    'CDL-027 epoch issuance boundary',
    'CDL-044 local-first wallet/account surfacing boundary',
    'Phase 622 bounded commission topology',
    'Phase 550 passive ECU proxy values',
    'option A: earmark-only with no debit',
    'option B: bounded earmark with debit on delivery',
    'option C: generalized ECU transfer',
    'The selected direction for this window is option B.',
)
REQUIRED_EXCLUSION_SNIPPETS = (
    'No decision-log mutation except the `CDL-063` row in Phase 625 and Phase 627.',
    'No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_624_630`.',
    'No `Option B` selection claim.',
    'No ILC transferability or wallet-write widening.',
    'No generalized ECU transfer between arbitrary parties.',
    'No external purchasing power claim.',
    'No prescription about Window 623+ runtime sequencing.',
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


def test_sequence_lock_exists_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_contains_all_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_one_states_authorization_basis_and_no_disposition_b_stance() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_AUTHORIZATION_SNIPPETS:
        assert item in text


def test_section_two_states_all_hard_pass_conditions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_HARD_PASS_SNIPPETS:
        assert item in text


def test_section_three_contains_ag_gate_table_all_rows_and_no_fail() -> None:
    text = _read(SEQ_LOCK_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    ag_rows = [line for line in text.splitlines() if line.startswith('| AG-')]
    assert ag_rows
    assert not any('| FAIL |' in line or ' FAIL ' in line for line in ag_rows)


def test_section_four_names_cdl_063_scope_dependencies_options_and_selected_direction() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_VEHICLE_SNIPPETS:
        assert item in text


def test_section_seven_lists_required_exclusions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_EXCLUSION_SNIPPETS:
        assert item in text


def test_phase_624_main_commit_touches_expected_paths_only_and_no_prohibited_paths() -> None:
    _require_commit_or_skip(PHASE_624_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_624_SUBJECT_TOKEN,
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


def test_phase_624_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_624_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_624_BACKFILL_SUBJECT_TOKEN,
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
