from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_485_494_handoff_494_v0.1.md')
GATE_PATH = Path('tools/check_window_485_494_closure_gate_phase_494.sh')
TEST_PATH = Path('tests/test_window_485_494_closure_gate_494.py')
PHASE_494_SUBJECT_TOKEN = 'phase 494 window 485-494 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(Path('tools/check_window_485_494_closure_gate_phase_494.sh')),
    str(TEST_PATH),
    str(HANDOFF_PATH),
}
EXPECTED_SELFTEST_GUARDS = (
    'ILC_PHASE_494_GATE_SELFTEST=1',
    'ILC_PHASE_484_GATE_SELFTEST=1',
    'ILC_PHASE_474_GATE_SELFTEST=1',
    'ILC_PHASE_468_GATE_SELFTEST=1',
    'ILC_PHASE_459_GATE_SELFTEST=1',
    'ILC_PHASE_449_GATE_SELFTEST=1',
    'ILC_PHASE_440_GATE_SELFTEST=1',
    'ILC_PHASE_433_GATE_SELFTEST=1',
    'ILC_PHASE_423_GATE_SELFTEST=1',
    'ILC_PHASE_413_GATE_SELFTEST=1',
    'ILC_PHASE_401_GATE_SELFTEST=1',
    'ILC_PHASE_391_GATE_SELFTEST=1',
    'ILC_PHASE_377_GATE_SELFTEST=1',
    'ILC_PHASE_367_GATE_SELFTEST=1',
    'ILC_PHASE_357_GATE_SELFTEST=1',
    'ILC_PHASE_347_GATE_SELFTEST=1',
    'ILC_PHASE_337_GATE_SELFTEST=1',
)
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_494_g8_window_485_494_closure_gate_and_handoff.md',
    '[2/6] lane_contract_tests',
    'python3 -m pytest tests/test_phase_485_window_sequence_lock.py tests/test_phase_486_sim_010_validator_incentive_economics_contract_and_commissioning.py tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py tests/test_phase_488_cdl_045_validator_circuit_breaker_surface_runtime.py tests/test_phase_489_validator_economic_incentive_framework_opening_stub.py tests/test_phase_490_validator_economic_incentive_framework_prelock_hardening.py tests/test_phase_491_validator_economic_incentive_framework_ratification_evidence.py tests/test_phase_492_validator_staking_and_liveness_enforcement_opening_stub.py tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py -q',
    '[3/6] cross_window_regression',
    'python3 -m pytest tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py -q',
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_485_494_closure_gate_494.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]
PRIOR_PHASE_TESTS = (
    'tests/test_phase_485_window_sequence_lock.py',
    'tests/test_phase_486_sim_010_validator_incentive_economics_contract_and_commissioning.py',
    'tests/test_phase_487_sim_010_validator_incentive_economics_execution_and_evidence.py',
    'tests/test_phase_488_cdl_045_validator_circuit_breaker_surface_runtime.py',
    'tests/test_phase_489_validator_economic_incentive_framework_opening_stub.py',
    'tests/test_phase_490_validator_economic_incentive_framework_prelock_hardening.py',
    'tests/test_phase_491_validator_economic_incentive_framework_ratification_evidence.py',
    'tests/test_phase_492_validator_staking_and_liveness_enforcement_opening_stub.py',
    'tests/test_phase_493_validator_staking_and_liveness_enforcement_prelock_hardening.py',
)


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_gate_env() -> dict[str, str]:
    blocked = {
        'ILC_PHASE_494_GATE_SELFTEST',
        'ILC_PHASE_484_GATE_SELFTEST',
        'ILC_PHASE_474_GATE_SELFTEST',
        'ILC_PHASE_468_GATE_SELFTEST',
        'ILC_PHASE_459_GATE_SELFTEST',
        'ILC_PHASE_449_GATE_SELFTEST',
        'ILC_PHASE_440_GATE_SELFTEST',
        'ILC_PHASE_433_GATE_SELFTEST',
        'ILC_PHASE_423_GATE_SELFTEST',
        'ILC_PHASE_413_GATE_SELFTEST',
        'ILC_PHASE_401_GATE_SELFTEST',
        'ILC_PHASE_391_GATE_SELFTEST',
        'ILC_PHASE_377_GATE_SELFTEST',
        'ILC_PHASE_367_GATE_SELFTEST',
        'ILC_PHASE_357_GATE_SELFTEST',
        'ILC_PHASE_347_GATE_SELFTEST',
        'ILC_PHASE_337_GATE_SELFTEST',
        'ILC_PHASE_494_DECISION_LOG_PATH',
    }
    return {key: value for key, value in __import__('os').environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_494_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_494_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_494_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_494_commit_not_present_in_local_history')


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{ref}:{DECISION_LOG_PATH}'],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_decision_log_at_ref:{ref}:{result.stderr.strip()}')
    return result.stdout


def _decision_log_override_env(tmp_path: Path, scenario: str) -> dict[str, str]:
    text = DECISION_LOG_PATH.read_text(encoding='utf-8')
    if scenario == 'invalid_cdl_055_ratified':
        updated_lines: list[str] = []
        for line in text.splitlines():
            if line.startswith('| CDL-055 |'):
                updated_lines.append(line.replace('| open |', '| ratified |', 1))
            else:
                updated_lines.append(line)
        text = '\n'.join(updated_lines) + '\n'
    else:
        raise AssertionError(f'unknown_override_scenario:{scenario}')
    override_path = tmp_path / 'phase_494_decision_log_override.md'
    override_path.write_text(text, encoding='utf-8')
    env = _clean_gate_env()
    env['ILC_PHASE_494_DECISION_LOG_PATH'] = str(override_path)
    return env


def _assert_valid_window_state(rows: dict[str, dict[str, str]]) -> None:
    success_state = rows.get('CDL-054', {}).get('status') == 'ratified' and rows.get('CDL-055', {}).get('status') == 'open' and 'CDL-053' not in rows
    blocked_state = 'CDL-053' not in rows and 'CDL-054' not in rows and 'CDL-055' not in rows
    assert success_state or blocked_state


def test_gate_script_exists_is_executable_and_includes_full_selftest_guard_chain() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert GATE_PATH.exists()
    assert GATE_PATH.stat().st_mode & 0o111
    for token in EXPECTED_SELFTEST_GUARDS:
        assert token in text
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_window_handoff_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    text = HANDOFF_PATH.read_text(encoding='utf-8')
    for heading in (
        '## 1. Window summary',
        '## 2. Deliverable matrix',
        '## 3. SIM-010 summary',
        '## 4. Validator economic lane summary',
        '## 5. Validator staking carry-forward summary',
        '## 6. Next-window controls',
    ):
        assert heading in text
    for token in (
        'Window 485-494 is closed.',
        'CDL-053 remains reserved and unopened.',
        'CDL-054 is ratified at window close.',
        'CDL-055 remains status: open at window close.',
        'Phase 495+ requires a new sequence lock or amendment.',
    ):
        assert token in text


def test_gate_script_passes_and_reports_success_path() -> None:
    if __import__('os').environ.get('ILC_PHASE_494_GATE_SELFTEST') == '1':
        pytest.skip('phase_494_selftest_context_skip_full_gate')
    result = _run_gate([])
    assert result.returncode == 0
    assert 'phase_494_window_state=success_path' in result.stdout
    assert 'phase_494_verdict=pass' in result.stdout


def test_gate_script_rejects_invalid_decision_log_override(tmp_path: Path) -> None:
    if __import__('os').environ.get('ILC_PHASE_494_GATE_SELFTEST') == '1':
        pytest.skip('phase_494_selftest_context_skip_full_gate')
    env = _decision_log_override_env(tmp_path, 'invalid_cdl_055_ratified')
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert 'phase_494_window_state=invalid' in result.stdout


def test_phase_494_cdl_inventory_is_historicalized() -> None:
    try:
        commit_ref = _resolve_phase_494_commit_ref()
    except AssertionError as exc:
        if str(exc) not in {
            'phase_494_commit_not_present_in_local_history',
            'phase_494_commit_subject_present_but_no_qualifying_closure_commit',
        }:
            raise
        historical_text = _decision_log_text_at_ref('HEAD')
    else:
        historical_text = _decision_log_text_at_ref(commit_ref)
    rows = parse_decision_register_rows(historical_text)
    _assert_valid_window_state(rows)


def test_all_nine_prior_phase_test_suites_exist_as_files() -> None:
    for path in PRIOR_PHASE_TESTS:
        assert Path(path).exists(), f'missing_prior_phase_suite:{path}'


def test_phase_494_main_commit_touches_expected_paths() -> None:
    if __import__('os').environ.get('ILC_PHASE_494_GATE_SELFTEST') == '1':
        pytest.skip('phase_494_selftest_context_skip_commit_resolution')
    assert _changed_paths_for_commit(_resolve_phase_494_commit_ref()) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_494_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    if __import__('os').environ.get('ILC_PHASE_494_GATE_SELFTEST') == '1':
        pytest.skip('phase_494_selftest_context_skip_commit_resolution')
    changed_paths = _changed_paths_for_commit(_resolve_phase_494_commit_ref())
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert all(not path.startswith('ilc_core/') for path in changed_paths)
