from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_495_504_handoff_504_v0.1.md')
GATE_PATH = Path('tools/check_window_495_504_closure_gate_phase_504.sh')
TEST_PATH = Path('tests/test_window_495_504_closure_gate_504.py')
PHASE_504_SUBJECT_TOKEN = 'phase 504 window 495-504 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(GATE_PATH),
    str(HANDOFF_PATH),
    str(TEST_PATH),
}
EXPECTED_SELFTEST_GUARDS = (
    'ILC_PHASE_504_GATE_SELFTEST=1',
    'ILC_PHASE_494_GATE_SELFTEST=1',
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
    'ILC_PHASE_327_GATE_SELFTEST=1',
    'ILC_PHASE_317_GATE_SELFTEST=1',
    'ILC_PHASE_307_GATE_SELFTEST=1',
)
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_504_g8_window_495_504_closure_gate_and_handoff.md',
    '[2/6] lane_contract_tests',
    'python3 -m pytest tests/test_phase_495_sequence_lock_and_cdl_055_disposition.py tests/test_phase_496_validator_staking_liveness_ratification_evidence.py tests/test_phase_497_validator_trust_tier_governance_boundary_analysis.py tests/test_phase_498_epoch_boundary_enforcement_architectural_scoping.py tests/test_phase_499_validator_trust_tier_elevation_opening_stub.py tests/test_phase_500_validator_trust_tier_elevation_prelock_hardening.py tests/test_phase_501_validator_trust_tier_elevation_ratification_evidence.py tests/test_phase_502_adm_001_v0_3_validator_trust_tier_amendment.py tests/test_phase_503_coherence_report_and_capsule_v2_3.py -q',
    '[3/6] cross_window_regression',
    'python3 -m pytest tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q',
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_495_504_closure_gate_504.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]
MONITORING_PATHS = (
    Path('out/monitoring/d2e_risk_snapshot_phase_306.json'),
    Path('out/monitoring/infrastructure_risk_snapshot_phase_316.json'),
)


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_gate_env() -> dict[str, str]:
    blocked = {
        'ILC_PHASE_504_GATE_SELFTEST',
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
        'ILC_PHASE_327_GATE_SELFTEST',
        'ILC_PHASE_317_GATE_SELFTEST',
        'ILC_PHASE_307_GATE_SELFTEST',
        'ILC_PHASE_504_DECISION_LOG_PATH',
        'ILC_PHASE_504_SNAPSHOT_PATH',
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_504_commit_ref() -> str:
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
        if PHASE_504_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_504_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_504_commit_not_present_in_local_history')


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(['git', 'show', f'{ref}:{DECISION_LOG_PATH}'], capture_output=True, check=False, text=True)
    if result.returncode != 0:
        raise AssertionError(f'unable_to_read_decision_log_at_ref:{ref}:{result.stderr.strip()}')
    return result.stdout


def _set_decision_row_status(text: str, decision_id: str, new_status: str) -> str:
    updated_lines: list[str] = []
    found = False
    for line in text.splitlines():
        if not line.startswith(f'| {decision_id} |'):
            updated_lines.append(line)
            continue
        cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
        if len(cells) < 4:
            raise AssertionError(f'malformed_decision_row:{decision_id}')
        cells[3] = new_status
        updated_lines.append('| ' + ' | '.join(cells) + ' |')
        found = True
    if not found:
        raise AssertionError(f'decision_row_not_found:{decision_id}')
    return '\n'.join(updated_lines) + '\n'


def _monitoring_state() -> dict[Path, tuple[str, int, int]]:
    return {
        path: (path.read_text(encoding='utf-8'), path.stat().st_mtime_ns, path.stat().st_size)
        for path in MONITORING_PATHS
    }


def _decision_log_override_env(tmp_path: Path, scenario: str) -> dict[str, str]:
    text = DECISION_LOG_PATH.read_text(encoding='utf-8')
    if scenario == 'blocked_path':
        lines = [line for line in text.splitlines() if not line.startswith('| CDL-056 |')]
        text = '\n'.join(lines) + '\n'
    elif scenario == 'invalid_cdl_055_open':
        text = _set_decision_row_status(text, 'CDL-055', 'open')
    else:
        raise AssertionError(f'unknown_override_scenario:{scenario}')
    override_path = tmp_path / 'phase_504_decision_log_override.md'
    override_path.write_text(text, encoding='utf-8')
    snapshot_path = tmp_path / 'phase_504_snapshot.json'
    env = _clean_gate_env()
    env['ILC_PHASE_504_DECISION_LOG_PATH'] = str(override_path)
    env['ILC_PHASE_504_SNAPSHOT_PATH'] = str(snapshot_path)
    return env


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
        '## 3. CDL-055 ratification summary',
        '## 4. CDL-056 outcome summary',
        '## 5. ADM-001 v0.3 status',
        '## 6. Epoch-boundary carry-forward',
        '## 7. Next-window controls',
    ):
        assert heading in text
    for token in (
        'Window 495-504 is closed.',
        'CDL-055 is ratified at window close.',
        'CDL-053 remains reserved and unopened.',
        'Epoch-boundary CDL amendment is a Window 505+ carry-forward.',
        'CDL-055 runtime implementation is a Window 505+ carry-forward.',
        'CDL-056 is ratified at window close.',
        'ADM-001 v0.3 is published at window close.',
        'CDL-056 runtime implementation is a Window 505+ carry-forward.',
        'Phase 505+ requires a new sequence lock or amendment.',
    ):
        assert token in text


def test_gate_script_passes_reports_success_path_and_preserves_canonical_monitoring(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_504_GATE_SELFTEST') == '1':
        pytest.skip('phase_504_selftest_context_skip_full_gate')
    before = _monitoring_state()
    env = _clean_gate_env()
    env['ILC_PHASE_504_SNAPSHOT_PATH'] = str(tmp_path / 'phase_504_snapshot.json')
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert 'phase_504_window_state=success_path' in result.stdout
    assert 'phase_504_verdict=pass' in result.stdout
    assert (tmp_path / 'phase_504_snapshot.json').exists()
    after = _monitoring_state()
    assert before == after


def test_gate_script_accepts_blocked_override_and_writes_override_snapshot(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_504_GATE_SELFTEST') == '1':
        pytest.skip('phase_504_selftest_context_skip_full_gate')
    env = _decision_log_override_env(tmp_path, 'blocked_path')
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert 'phase_504_window_state=blocked_path' in result.stdout
    assert 'phase_504_verdict=pass' in result.stdout
    snapshot_text = (tmp_path / 'phase_504_snapshot.json').read_text(encoding='utf-8')
    assert '"state": "blocked"' in snapshot_text


def test_gate_script_rejects_invalid_override(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_504_GATE_SELFTEST') == '1':
        pytest.skip('phase_504_selftest_context_skip_full_gate')
    env = _decision_log_override_env(tmp_path, 'invalid_cdl_055_open')
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert 'phase_504_window_state=invalid' in result.stdout
    assert 'phase_504_window_state_details=unexpected_validator_cdl_state' in result.stdout


def test_phase_504_cdl_inventory_is_historicalized() -> None:
    try:
        commit_ref = _resolve_phase_504_commit_ref()
    except AssertionError as exc:
        if str(exc) not in {
            'phase_504_commit_not_present_in_local_history',
            'phase_504_commit_subject_present_but_no_qualifying_closure_commit',
        }:
            raise
        historical_text = _decision_log_text_at_ref('HEAD')
    else:
        historical_text = _decision_log_text_at_ref(commit_ref)
    rows = parse_decision_register_rows(historical_text)
    success_state = rows.get('CDL-055', {}).get('status') == 'ratified' and rows.get('CDL-056', {}).get('status') == 'ratified' and 'CDL-053' not in rows
    blocked_state = rows.get('CDL-055', {}).get('status') == 'ratified' and 'CDL-056' not in rows and 'CDL-053' not in rows
    assert success_state or blocked_state


def test_phase_504_main_commit_touches_expected_paths_only() -> None:
    if os.environ.get('ILC_PHASE_504_GATE_SELFTEST') == '1':
        pytest.skip('phase_504_selftest_context_skip_commit_resolution')
    assert _changed_paths_for_commit(_resolve_phase_504_commit_ref()) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_504_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    if os.environ.get('ILC_PHASE_504_GATE_SELFTEST') == '1':
        pytest.skip('phase_504_selftest_context_skip_commit_resolution')
    changed_paths = _changed_paths_for_commit(_resolve_phase_504_commit_ref())
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert all(not path.startswith('ilc_core/') for path in changed_paths)
