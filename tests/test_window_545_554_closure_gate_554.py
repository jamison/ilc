from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_545_554_handoff_554_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.8.md')
GOSSIP_RUNTIME_PATH = Path('ilc_core/network/d2d/centrality_delta_gossip_runtime.py')
PASSIVE_ECU_RUNTIME_PATH = Path('ilc_core/economics/passive_ecu_attribution_runtime.py')
GATE_PATH = Path('tools/check_window_545_554_closure_gate_phase_554.sh')
TEST_PATH = Path('tests/test_window_545_554_closure_gate_554.py')
PHASE_554_SUBJECT_TOKEN = 'phase 554 window 545-554 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(GATE_PATH),
    str(HANDOFF_PATH),
    str(TEST_PATH),
}
EXPECTED_SELFTEST_GUARDS = (
    'ILC_PHASE_554_GATE_SELFTEST=1',
    'ILC_PHASE_544_GATE_SELFTEST=1',
    'ILC_PHASE_534_GATE_SELFTEST=1',
    'ILC_PHASE_524_GATE_SELFTEST=1',
    'ILC_PHASE_514_GATE_SELFTEST=1',
    'ILC_PHASE_504_GATE_SELFTEST=1',
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
    'ILC_PHASE_327_GATE_SELFTEST=1',
    'ILC_PHASE_317_GATE_SELFTEST=1',
    'ILC_PHASE_307_GATE_SELFTEST=1',
)
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_554_g8_window_545_554_closure_gate_and_handoff.md',
    '[2/6] lane_contract_tests',
    'python3 -m pytest tests/test_phase_545_sequence_lock_and_carry_forward_intake.py tests/test_phase_546_epoch_boundary_commit_semantics.py tests/test_phase_547_signal_floor_policy_scoping.py tests/test_phase_548_centrality_delta_gossip_runtime.py tests/test_phase_549_centrality_delta_gossip_runtime_hardening.py tests/test_phase_550_passive_ecu_attribution_runtime.py tests/test_phase_551_passive_ecu_attribution_hardening.py tests/test_phase_552_sim_multi_hop_01_centrality.py tests/test_phase_553_coherence_report_and_capsule_v2_8.py -q',
    '[3/6] cross_window_regression',
    'python3 -m pytest tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q',
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_545_554_closure_gate_554.py -q',
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
        'ILC_PHASE_554_GATE_SELFTEST',
        'ILC_PHASE_544_GATE_SELFTEST',
        'ILC_PHASE_534_GATE_SELFTEST',
        'ILC_PHASE_524_GATE_SELFTEST',
        'ILC_PHASE_514_GATE_SELFTEST',
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
        'ILC_PHASE_554_DECISION_LOG_PATH',
        'ILC_PHASE_554_CAPSULE_PATH',
        'ILC_PHASE_554_SIM_PATH',
        'ILC_PHASE_554_FLOOR_POLICY_PATH',
        'ILC_PHASE_554_CDL_GOSSIP_RUNTIME_PATH',
        'ILC_PHASE_554_PASSIVE_ECU_RUNTIME_PATH',
        'ILC_PHASE_554_SNAPSHOT_PATH',
        'ILC_PHASE_554_ALLOW_SNAPSHOT_WRITE',
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


def _resolve_phase_554_commit_ref() -> str:
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
        if PHASE_554_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_554_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_554_commit_not_present_in_local_history')


def _monitoring_state() -> dict[Path, tuple[bytes, int, int]]:
    return {path: (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_size) for path in MONITORING_PATHS}


def test_gate_script_exists_is_executable_and_dry_run_matches_expected_output() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert GATE_PATH.exists()
    assert GATE_PATH.stat().st_mode & 0o111
    assert len(EXPECTED_SELFTEST_GUARDS) == 26
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
        '## 3. CDL-060 gossip runtime outcome',
        '## 4. Passive ECU attribution runtime outcome',
        '## 5. Deferred carry-forwards',
        '## 6. Closure gate result',
        '## 7. Next-window controls',
    ):
        assert heading in text
    for token in (
        'Window 545-554 is closed.',
        'CDL-053 remains reserved and unopened.',
        'CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"',
        'CDL-060 gossip runtime is implemented in Phase 548.',
        'PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"',
        'Passive ECU attribution runtime is implemented in Phase 550.',
        'Authorship primacy invariant holds: passive_ecu < base_reward for all valid inputs.',
        'SIM-MULTI-HOP-01 disposition: `sim_multi_hop_01_insufficient`.',
        'Signal-floor policy disposition: `signal_floor_governance_adm_only`.',
        'Phase 555+ requires a new sequence lock or amendment.',
        'The closure gate passed.',
    ):
        assert token in text


def test_gate_runs_successfully_and_preserves_canonical_monitoring(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_full_gate')
    before = _monitoring_state()
    env = _clean_gate_env()
    env['ILC_PHASE_554_SNAPSHOT_PATH'] = str(tmp_path / 'phase_554_snapshot.json')
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert 'phase_554_window_state=pass' in result.stdout
    assert 'phase_554_verdict=pass' in result.stdout
    assert (tmp_path / 'phase_554_snapshot.json').exists()
    after = _monitoring_state()
    assert before == after


def test_cdl_inventory_is_historicalized_for_phase_554() -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_inventory')
    commit_ref = _resolve_phase_554_commit_ref()
    text = subprocess.run(
        ['git', 'show', f'{commit_ref}:{DECISION_LOG_PATH}'],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    rows = parse_decision_register_rows(text)
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows


def test_cdl_060_gossip_runtime_is_implemented() -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_gossip_runtime')
    override = os.environ.get('ILC_PHASE_554_CDL_GOSSIP_RUNTIME_PATH')
    target = Path(override) if override else GOSSIP_RUNTIME_PATH
    text = target.read_text(encoding='utf-8')
    assert 'CDL_060_GOSSIP_RUNTIME_VERSION = "centrality_delta_gossip_runtime_GAP_CDL060.v0.2"' in text


def test_passive_ecu_attribution_runtime_is_implemented() -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_passive_runtime')
    override = os.environ.get('ILC_PHASE_554_PASSIVE_ECU_RUNTIME_PATH')
    target = Path(override) if override else PASSIVE_ECU_RUNTIME_PATH
    text = target.read_text(encoding='utf-8')
    assert 'PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"' in text


def test_gate_rejects_invalid_state_when_gossip_runtime_is_absent(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_invalid_gate')
    override = tmp_path / 'phase_554_gossip_override.py'
    override.write_text('CDL_060_GOSSIP_RUNTIME_VERSION = "wrong_runtime.v0.1"\n', encoding='utf-8')
    env = _clean_gate_env()
    env['ILC_PHASE_554_CDL_GOSSIP_RUNTIME_PATH'] = str(override)
    env['ILC_PHASE_554_SNAPSHOT_PATH'] = str(tmp_path / 'phase_554_invalid_snapshot.json')
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert 'phase_554_window_state=fail' in result.stdout
    assert 'phase_554_window_state_details=cdl_060_gossip_runtime_missing_or_mismatch' in result.stdout


def test_phase_554_main_commit_touches_expected_paths_only() -> None:
    if os.environ.get('ILC_PHASE_554_GATE_SELFTEST') == '1':
        pytest.skip('phase_554_selftest_context_skip_commit_scope')
    commit_ref = _resolve_phase_554_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
