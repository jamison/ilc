from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
HANDOFF_PATH = Path('docs/specs/ilc_window_555_564_handoff_564_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v2.9.md')
COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_563_v0.1.md')
TRANSPORT_PATH = Path('ilc_core/network/d2d/gossip_transport.py')
REGISTRY_PATH = Path('ilc_core/network/d2d/gossip_peer_registry.py')
CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
GATE_PATH = Path('tools/check_window_555_564_closure_gate_phase_564.sh')
TEST_PATH = Path('tests/test_window_555_564_closure_gate_564.py')
PHASE_564_SUBJECT_TOKEN = 'phase 564 window 555-564 closure gate and handoff'
EXACT_REQUIRED_MAIN_PATHS = {
    str(GATE_PATH),
    str(HANDOFF_PATH),
    str(TEST_PATH),
}
EXPECTED_SELFTEST_GUARDS = (
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
PROMPT_VALIDATION_COMMAND = 'python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_555_g8_window_555_564_sequence_lock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_556_g8_adr_023_signal_floor_invariant_update.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_557_g8_cdl_061_prelock.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_558_g8_gossip_transport_adapter.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_559_g8_gossip_transport_hardening.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_560_g8_canary_transport_probes.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_561_g8_cdl_061_ratification.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_562_g8_gossip_peer_registry.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_563_g8_coherence_report_and_capsule_v2_9.md && python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_564_g8_window_555_564_closure_gate_and_handoff.md'
LANE_TEST_COMMAND = 'python3 -m pytest tests/test_phase_555_window_555_564_sequence_lock.py tests/test_phase_556_adr_023_signal_floor_invariant.py tests/test_phase_557_cdl_061_prelock.py tests/test_phase_558_gossip_transport_adapter.py tests/test_phase_559_gossip_transport_hardening.py tests/test_phase_560_canary_transport_probes.py tests/test_phase_561_cdl_061_ratification.py tests/test_phase_562_gossip_peer_registry.py tests/test_phase_563_coherence_report_and_capsule.py -q'
CROSS_PHASE_COMMAND = 'python3 -m pytest tests/test_window_545_554_closure_gate_554.py tests/test_window_535_544_closure_gate_544.py tests/test_window_525_534_closure_gate_534.py tests/test_window_515_524_closure_gate_524.py tests/test_window_505_514_closure_gate_514.py tests/test_window_495_504_closure_gate_504.py tests/test_window_485_494_closure_gate_494.py tests/test_window_475_484_closure_gate_484.py tests/test_window_469_474_closure_gate_474.py tests/test_window_460_468_closure_gate_468.py tests/test_window_450_459_closure_gate_459.py tests/test_window_441_449_closure_gate_449.py tests/test_window_434_440_closure_gate_440.py tests/test_window_424_433_closure_gate_433.py tests/test_window_414_423_closure_gate_423.py tests/test_window_402_413_closure_gate_413.py tests/test_window_392_401_closure_gate_401.py tests/test_window_378_391_closure_gate_391.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py tests/test_window_318_327_closure_gate_327.py tests/test_window_308_317_closure_gate_317.py tests/test_window_298_307_closure_gate_307.py -q'
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
    'python3 -m pytest tests/test_window_555_564_closure_gate_564.py -q',
    '[6/6] walkthrough_hygiene',
    'python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q',
]
CANONICAL_SNAPSHOT_PATH = Path('out/monitoring/d2e_risk_snapshot_phase_564.json')
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
        'ILC_PHASE_564_SNAPSHOT_PATH',
        'ILC_PHASE_564_ALLOW_SNAPSHOT_WRITE',
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
    override_path = tmp_path / f'phase_564_snapshot_{verdict}.json'
    override_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    env = _clean_gate_env()
    env['ILC_PHASE_564_SNAPSHOT_PATH'] = str(override_path)
    return env, _monitoring_state(), override_path


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_564_commit_ref() -> str:
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
        if PHASE_564_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_564_commit_subject_present_but_no_qualifying_closure_commit')
    raise AssertionError('phase_564_commit_not_present_in_local_history')


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
    assert len(EXPECTED_SELFTEST_GUARDS) == 27
    for token in EXPECTED_SELFTEST_GUARDS:
        assert token in text
    dry_run = _run_gate(['--dry-run'])
    assert dry_run.returncode == 0
    assert [line.strip() for line in dry_run.stdout.splitlines() if line.strip()] == EXPECTED_DRY_RUN_LINES


def test_gate_exits_early_on_snapshot_conditional_or_blocked(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_564_GATE_SELFTEST') == '1':
        pytest.skip('phase_564_selftest_context_skip_snapshot_early_exit')
    conditional_env, _, _ = _snapshot_override_env(tmp_path, 'conditional')
    conditional = _run_gate([], env=conditional_env)
    assert conditional.returncode == 3
    assert 'phase_564_snapshot_verdict=conditional' in conditional.stdout
    assert '[1/6] prompt_contract_validation' not in conditional.stdout

    blocked_env, _, _ = _snapshot_override_env(tmp_path, 'blocked')
    blocked = _run_gate([], env=blocked_env)
    assert blocked.returncode == 1
    assert 'phase_564_snapshot_verdict=blocked' in blocked.stdout
    assert '[1/6] prompt_contract_validation' not in blocked.stdout


def test_gate_snapshot_override_env_is_honoured(tmp_path: Path) -> None:
    if os.environ.get('ILC_PHASE_564_GATE_SELFTEST') == '1':
        pytest.skip('phase_564_selftest_context_skip_snapshot_override')
    env, before, override_path = _snapshot_override_env(tmp_path, 'pass')
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert 'phase_564_snapshot_verdict=pass' in result.stdout
    assert override_path.exists()
    payload = json.loads(override_path.read_text(encoding='utf-8'))
    assert payload['phase'] == 564
    assert payload['window'] == '555-564'
    assert payload['verdict'] == 'pass'
    assert payload['state'] == 'pass'
    assert _monitoring_state() == before


def test_gate_full_run_passes_with_live_snapshot() -> None:
    if os.environ.get('ILC_PHASE_564_GATE_SELFTEST') == '1':
        pytest.skip('phase_564_selftest_context_skip_full_gate')
    before = _monitoring_state()
    result = _run_gate([], env=_clean_gate_env())
    assert result.returncode == 0
    assert 'phase_564_snapshot_verdict=pass' in result.stdout
    assert 'phase_564_window_state=pass' in result.stdout
    assert 'phase_564_verdict=pass' in result.stdout
    assert _monitoring_state() == before


def test_handoff_artifact_exists_with_required_headings_and_tokens() -> None:
    text = HANDOFF_PATH.read_text(encoding='utf-8')
    for heading in (
        '## 1. Window 555-564 completion summary',
        '## 2. CDL-061 ratification record',
        '## 3. Transport layer dep chain (final state)',
        '## 4. Module inventory (new files committed in this window)',
        '## 5. Canary probe inventory (final state — 8 probes)',
        '## 6. Open items carried forward to Window 565-574',
        '## 7. Context capsule reference',
    ):
        assert heading in text
    for token in (
        'phase_564_verdict=pass',
        'window_555_564_complete',
        'cdl_061_ratified_561_gossip_http_envelope_contract',
        'gossip_transport_dep_chain_complete_through_562',
        'window_565_574_ready_to_plan',
        'gossip_transport_runtime_558.v0.1',
        'gossip_peer_registry_562.v0.1',
    ):
        assert token in text


def test_gate_help_and_unknown_arg_contract() -> None:
    assert _run_gate(['--help']).returncode == 0
    assert _run_gate(['-h']).returncode == 0
    assert _run_gate(['--unknown-arg']).returncode == 2


def test_phase_564_main_commit_touches_expected_paths_only() -> None:
    if os.environ.get('ILC_PHASE_564_GATE_SELFTEST') == '1':
        pytest.skip('phase_564_selftest_context_skip_commit_scope')
    commit_ref = _resolve_phase_564_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_564_main_commit_does_not_touch_decision_log_or_ilc_core() -> None:
    if os.environ.get('ILC_PHASE_564_GATE_SELFTEST') == '1':
        pytest.skip('phase_564_selftest_context_skip_commit_scope')
    commit_ref = _resolve_phase_564_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert str(COHERENCE_PATH) not in changed_paths
    assert str(CAPSULE_PATH) not in changed_paths
    assert str(CANARY_PATH) not in changed_paths
    assert str(TRANSPORT_PATH) not in changed_paths
    assert str(REGISTRY_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
