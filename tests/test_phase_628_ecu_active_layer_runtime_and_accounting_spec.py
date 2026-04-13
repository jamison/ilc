from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md')
PHASE_TEST_PATH = Path('tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py')
RUNTIME_TEST_PATH = Path('tests/test_ecu_active_layer_runtime.py')
RUNTIME_PATH = Path('ilc_core/ledger/ecu_active_layer_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
WALKTHROUGH_PATH = Path('docs/phases/phase_628_g8_ecu_active_layer_runtime_and_accounting_spec_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_628_SUBJECT = 'phase 628 ecu active layer runtime and accounting spec'
PHASE_628_BACKFILL_SUBJECT = 'phase 628 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(PHASE_TEST_PATH),
    str(RUNTIME_TEST_PATH),
    str(RUNTIME_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Authorization basis — CDL-063 ratified',
    '## 2. Earmark state machine',
    '## 3. Epoch-settled accounting model',
    '## 4. Machine-legible interfaces',
    '## 5. Runtime implementation surface',
    '## 6. AG-gate assessment',
    '## 7. Wallet boundary confirmation',
)
REQUIRED_TOKENS = (
    'ecu_active_layer_runtime_spec_628_locked',
    'cdl_063_dependency_consumed',
    'earmark_state_machine_defined',
    'epoch_settled_accounting_model_defined',
    'machine_legible_interfaces_defined',
    'runtime_implementation_complete_in_phase_628',
    'wallet_boundary_576_581_unchanged_in_628',
    'ecu_debit_not_ilc_payment_628',
    'disposition_b_not_permitted_window_624_630',
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


def test_spec_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_spec_contains_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_defines_all_states_and_required_transitions() -> None:
    text = _read(SPEC_PATH)
    for state in ('`proposed`', '`accepted`', '`delivered`', '`debited`', '`expired`'):
        assert state in text
    for transition in (
        '`proposed -> accepted`',
        '`accepted -> delivered`',
        '`delivered -> debited`',
        '`proposed -> expired`',
        '`accepted -> expired`',
    ):
        assert transition in text


def test_section_three_defines_schema_and_reserved_balance_invariant() -> None:
    text = _read(SPEC_PATH)
    for field in (
        '`earmark_id`',
        '`commission_id`',
        '`commissioning_agent_id`',
        '`performing_agent_id`',
        '`earmark_amount`',
        '`state`',
        '`proposal_epoch`',
        '`expiry_epoch`',
        '`acceptance_epoch`',
        '`delivery_epoch`',
        '`debit_epoch`',
        '`task_description_hash`',
        '`contribution_id`',
    ):
        assert field in text
    assert '`spendable_ecu(A) = total_accrued_ecu(A) - sum(reserved_earmarks_by_A)`' in text
    assert 'where reserved means states `proposed`, `accepted`, or `delivered`' in text


def test_section_four_defines_interfaces_with_json_outputs_and_failure_tokens() -> None:
    text = _read(SPEC_PATH)
    for interface_name in (
        '`earmark_propose(...)`',
        '`earmark_accept(...)`',
        '`earmark_deliver(...)`',
        '`earmark_status(...)`',
        '`earmark_history(agent_id)`',
    ):
        assert interface_name in text
    for token in (
        '`earmark_proposed`',
        '`earmark_acceptance_recorded`',
        '`earmark_delivery_recorded`',
        '`earmark_status_found`',
        '`earmark_history_returned`',
        '`same_key_self_commission_prohibited`',
        '`performing_agent_mismatch`',
        '`earmark_past_expiry`',
        '`oversubscribed_earmark_blocked`',
        '`active_earmark_cap_exceeded`',
    ):
        assert token in text


def test_section_five_names_concrete_runtime_file() -> None:
    text = _read(SPEC_PATH)
    assert '`ilc_core/ledger/ecu_active_layer_runtime.py`' in text


def test_runtime_file_uses_ratified_expiry_and_runtime_cap_defaults() -> None:
    text = _read(RUNTIME_PATH)
    assert 'DEFAULT_FIXED_EXPIRY_VALIDATION_EPOCHS = 2880' in text
    assert 'DEFAULT_ACTIVE_EARMARK_CAP_PER_AGENT = 8' in text


def test_main_commit_touches_expected_paths_only_and_no_cdl_mutation_or_adr_path() -> None:
    _require_commit_or_skip(PHASE_628_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_628_SUBJECT,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_628_BACKFILL_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_628_BACKFILL_SUBJECT,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_and_runtime_tests_both_pass() -> None:
    _require_commit_or_skip(PHASE_628_SUBJECT)
    result = subprocess.run(
        [
            'bash',
            '-lc',
            "PATH=.venv/bin:$PATH .venv/bin/pytest "
            "tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py "
            "-q -k 'not test_phase_and_runtime_tests_both_pass' && "
            "PATH=.venv/bin:$PATH .venv/bin/pytest tests/test_ecu_active_layer_runtime.py -q",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert 'passed' in result.stdout
