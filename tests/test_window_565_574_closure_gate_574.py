from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest


DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_565_574_handoff_574_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v3.0.md')
COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_573_v0.1.md')
WALKTHROUGH_PATH = Path('docs/phases/phase_0572_g8_three_machine_smoke_harness_walkthrough.md')
TRANSPORT_PATH = Path('ilc_core/network/d2d/http_gossip_transport_runtime.py')
STARTUP_PATH = Path('ilc_core/node/node_startup_runtime.py')
SERVICE_PATH = Path('tools/run_ilc_node_service_v1.py')
CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
GATE_PATH = Path('tools/check_window_565_574_closure_gate_phase_574.sh')
TEST_PATH = Path('tests/test_window_565_574_closure_gate_574.py')
PHASE_574_SUBJECT_TOKEN = 'phase 574 window 565-574 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(GATE_PATH),
    str(HANDOFF_PATH),
    str(TEST_PATH),
}
EXPECTED_SELFTEST_GUARDS = (
    'ILC_PHASE_574_GATE_SELFTEST=1',
    'ILC_PHASE_564_GATE_SELFTEST=1',
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
PROMPT_VALIDATION_COMMAND = 'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_565_g8_window_565_574_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_566_g8_transport_operationalization_boundary_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_567_g8_genesis_package_lifecycle_scoping.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_568_g8_real_http_transport_wrapper_runtime.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_569_g8_transport_hardening_and_http2_fallback.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_570_g8_static_peer_config_json_loader_and_startup_wiring.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_571_g8_venv_systemd_packaging_and_lifecycle_runtime.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_572_g8_three_machine_smoke_harness.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_573_g8_coherence_report_and_capsule_v3_0.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_574_g8_window_565_574_closure_gate_and_handoff.md'
LANE_TEST_COMMAND = 'python3 -m pytest tests/test_phase_565_window_565_574_sequence_lock.py tests/test_phase_566_transport_operationalization_boundary_lock.py tests/test_phase_567_genesis_package_lifecycle_scoping.py tests/test_phase_568_real_http_transport_wrapper_runtime.py tests/test_phase_569_transport_hardening_and_http2_fallback.py tests/test_phase_570_static_peer_config_json_loader_and_startup_wiring.py tests/test_phase_571_venv_systemd_packaging_and_lifecycle_runtime.py tests/test_phase_572_three_machine_smoke_harness.py tests/test_phase_573_coherence_report_and_capsule_v3_0.py -q'
CROSS_PHASE_COMMAND = 'python3 -m pytest tests/test_window_555_564_closure_gate_564.py tests/test_window_545_554_closure_gate_554.py tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q'
EXPECTED_DRY_RUN_LINES = [
    '[1/6] prompt_contract_validation',
    PROMPT_VALIDATION_COMMAND,
    '[2/6] lane_contract_tests',
    LANE_TEST_COMMAND,
    '[3/6] cross_phase_regression',
    CROSS_PHASE_COMMAND,
    '[4/6] mutation_canary',
    'python3 tools/run_mutation_canary_phase_297.py',
    '[5/6] closure_gate_cli_contract',
    'python3 -m pytest tests/test_window_565_574_closure_gate_574.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]
CANONICAL_SNAPSHOT_PATH = Path('out/monitoring/infrastructure_risk_snapshot_phase_574.json')
SNAPSHOT_TEMPLATE_PATH = Path('out/monitoring/infrastructure_risk_snapshot_phase_316.json')
MONITORING_PATHS = (
    CANONICAL_SNAPSHOT_PATH,
    Path('out/monitoring/d2e_risk_snapshot_phase_306.json'),
    Path('out/monitoring/infrastructure_risk_snapshot_phase_316.json'),
)


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['bash', str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_gate_env() -> dict[str, str]:
    blocked = {
        'ILC_PHASE_574_GATE_SELFTEST',
        'ILC_PHASE_564_GATE_SELFTEST',
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
        'ILC_PHASE_574_SNAPSHOT_PATH',
        'ILC_PHASE_574_ALLOW_SNAPSHOT_WRITE',
        'ILC_PHASE_574_PHASE_572_WALKTHROUGH_PATH',
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _sha256_state(path: Path) -> tuple[str, int, int]:
    if not path.exists():
        return ('__missing__', -1, -1)
    raw = path.read_bytes()
    return (hashlib.sha256(raw).hexdigest(), path.stat().st_mtime_ns, len(raw))


def _monitoring_state() -> dict[Path, tuple[str, int, int]]:
    return {path: _sha256_state(path) for path in MONITORING_PATHS}


def _snapshot_override_env(tmp_path: Path, verdict: str) -> tuple[dict[str, str], dict[Path, tuple[str, int, int]], Path]:
    payload = json.loads(SNAPSHOT_TEMPLATE_PATH.read_text(encoding='utf-8'))
    payload['verdict'] = verdict
    override_path = tmp_path / f'phase_574_snapshot_{verdict}.json'
    override_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    env = _clean_gate_env()
    env['ILC_PHASE_574_SNAPSHOT_PATH'] = str(override_path)
    return env, _monitoring_state(), override_path


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_574_commit_ref() -> str:
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
        if PHASE_574_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_574_commit_not_present_in_local_history')


def test_gate_categories_are_defined() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert GATE_PATH.exists()
    assert GATE_PATH.stat().st_mode & 0o111
    for label in (
        'prompt_contract_validation',
        'lane_contract_tests',
        'cross_phase_regression',
        'mutation_canary',
        'closure_gate_cli_contract',
        'walkthrough_hygiene',
    ):
        assert label in text
    assert len(EXPECTED_SELFTEST_GUARDS) == 28
    for token in EXPECTED_SELFTEST_GUARDS:
        assert token in text
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_gate_rejects_missing_operator_proof_state(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_574_GATE_SELFTEST') == '1':
        pytest.skip('phase_574_selftest_context_skip_operator_proof')
    walkthrough_copy = tmp_path / 'phase_572_walkthrough_without_token.md'
    text = WALKTHROUGH_PATH.read_text(encoding='utf-8').replace('phase_572_real_three_machine_operator_proof_recorded', 'phase_572_token_removed_for_test')
    walkthrough_copy.write_text(text, encoding='utf-8')
    env, before, _ = _snapshot_override_env(tmp_path, 'pass')
    env['ILC_PHASE_574_PHASE_572_WALKTHROUGH_PATH'] = str(walkthrough_copy)
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert 'phase_574_window_state=fail' in result.stdout
    assert 'phase_574_window_state_details=phase_572_operator_proof_missing' in result.stdout
    assert _monitoring_state() == before


def test_gate_snapshot_override_env_is_honoured_and_canonical_monitoring_is_unchanged(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_574_GATE_SELFTEST') == '1':
        pytest.skip('phase_574_selftest_context_skip_snapshot_override')
    env, before, override_path = _snapshot_override_env(tmp_path, 'pass')
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert 'phase_574_snapshot_verdict=pass' in result.stdout
    assert 'phase_574_verdict=pass' in result.stdout
    assert override_path.exists()
    payload = json.loads(override_path.read_text(encoding='utf-8'))
    assert payload['phase'] == 574
    assert payload['window'] == '565-574'
    assert payload['verdict'] == 'pass'
    assert payload['state'] == 'pass'
    assert _monitoring_state() == before


def test_gate_full_run_passes_on_valid_state() -> None:
    if os.environ.get('ILC_PHASE_574_GATE_SELFTEST') == '1':
        pytest.skip('phase_574_selftest_context_skip_full_gate')
    before = _monitoring_state()
    result = _run_gate([], env=_clean_gate_env())
    assert result.returncode == 0
    assert 'phase_574_snapshot_verdict=pass' in result.stdout
    assert 'phase_574_window_state=pass' in result.stdout
    assert 'phase_574_verdict=pass' in result.stdout
    assert _monitoring_state() == before


def test_gate_requires_all_ten_prompt_validations_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert PROMPT_VALIDATION_COMMAND in text
    assert text.count('tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_') == 10


def test_gate_requires_the_exact_lane_test_file_list_explicitly() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert LANE_TEST_COMMAND in text
    assert 'tests/test_phase_565_window_565_574_sequence_lock.py' in text
    assert 'tests/test_phase_573_coherence_report_and_capsule_v3_0.py' in text


def test_gate_wires_the_selftest_recursion_guard_for_phase_574() -> None:
    text = GATE_PATH.read_text(encoding='utf-8')
    assert 'run_command "${commands[$idx]}" ILC_PHASE_574_GATE_SELFTEST=1' in text
    assert 'ILC_PHASE_574_GATE_SELFTEST=1' in text


def test_prior_window_pattern_structure_and_handoff_contract_are_adapted_to_this_window() -> None:
    gate_text = GATE_PATH.read_text(encoding='utf-8')
    handoff_text = HANDOFF_PATH.read_text(encoding='utf-8')
    assert 'manifest counts' in gate_text
    assert 'file counts' in gate_text
    assert 'placeholder mode output' in gate_text
    assert 'phase_572_real_three_machine_operator_proof_recorded' in gate_text
    assert 'Read each prior gate test file before omitting a selftest flag' in gate_text or 'Read each prior gate test file before omitting a selftest flag.' in gate_text
    for heading in (
        '## 1. Window 565-574 completion summary',
        '## 2. Real transport operationalization record',
        '## 3. Startup, config, and packaging record',
        '## 4. Smoke harness and operator-proof record',
        '## 5. Canary probe inventory (final state - 9 probes)',
        '## 6. Open items carried forward to Window 575-584',
        '## 7. Context capsule reference',
    ):
        assert heading in handoff_text
    for token in (
        'phase_574_verdict=pass',
        'window_565_574_complete',
        'three_machine_testbed_primary_gate_passed',
        'packaging_and_genesis_support_lane_passed',
        'window_575_584_ready_to_plan',
    ):
        assert token in handoff_text
    if os.environ.get('ILC_PHASE_574_GATE_SELFTEST') == '1':
        return
    commit_ref = _resolve_phase_574_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert str(COHERENCE_PATH) not in changed_paths
    assert str(CAPSULE_PATH) not in changed_paths
    assert str(WALKTHROUGH_PATH) not in changed_paths
    assert str(CANARY_PATH) not in changed_paths
    assert str(TRANSPORT_PATH) not in changed_paths
    assert str(STARTUP_PATH) not in changed_paths
    assert str(SERVICE_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
