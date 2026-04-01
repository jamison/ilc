from __future__ import annotations

import os
import subprocess
from pathlib import Path


HARNESS_PATH = Path('tools/run_three_machine_smoke_phase_572.sh')
TEST_PATH = Path('tests/test_phase_572_three_machine_smoke_harness.py')
FIXTURE_DIR = Path('tests/fixtures/phase_572_three_machine_smoke')
FIXTURE_PATHS = {
    'tests/fixtures/phase_572_three_machine_smoke/node1_config.json',
    'tests/fixtures/phase_572_three_machine_smoke/node2_config.json',
    'tests/fixtures/phase_572_three_machine_smoke/node3_config.json',
    'tests/fixtures/phase_572_three_machine_smoke/genesis_ref.json',
    'tests/fixtures/phase_572_three_machine_smoke/genesis_bundle.json',
    'tests/fixtures/phase_572_three_machine_smoke/cert.pem',
    'tests/fixtures/phase_572_three_machine_smoke/key.pem',
}
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_572_SUBJECT_TOKEN = 'phase 572 deterministic three machine smoke harness'
EXACT_REQUIRED_MAIN_PATHS = {str(HARNESS_PATH), str(TEST_PATH), *FIXTURE_PATHS}
EXPECTED_SUCCESS_MARKERS = (
    'smoke_node_1_ready',
    'smoke_node_2_ready',
    'smoke_node_3_ready',
    'smoke_gossip_send_ok',
    'smoke_gossip_receive_ok',
    'smoke_explicit_http_fallback_ok',
    'smoke_genesis_import_ok',
    'smoke_restart_ok',
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_572_commit_ref() -> str:
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
        if PHASE_572_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_572_commit_not_present_in_local_history')


def _run_harness(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env['PYTHONPATH'] = str(Path.cwd())
    return subprocess.run(
        ['bash', str(HARNESS_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_harness_script_exists_and_is_executable() -> None:
    assert HARNESS_PATH.is_file()
    assert os.access(HARNESS_PATH, os.X_OK)


def test_fixture_directory_contains_deterministic_sample_configs_for_three_nodes() -> None:
    assert FIXTURE_DIR.is_dir()
    for relative_path in FIXTURE_PATHS:
        assert Path(relative_path).is_file()


def test_local_smoke_mode_emits_required_success_markers_on_success() -> None:
    result = _run_harness('--local-smoke')
    assert result.returncode == 0
    for marker in EXPECTED_SUCCESS_MARKERS:
        assert marker in result.stdout


def test_invalid_config_path_emits_smoke_config_failure() -> None:
    result = _run_harness('--local-smoke', '--config-dir', 'tests/fixtures/does-not-exist')
    assert result.returncode != 0
    assert 'smoke_config_failure' in result.stdout


def test_forced_transport_failure_emits_smoke_transport_failure() -> None:
    result = _run_harness('--local-smoke', '--force-transport-failure')
    assert result.returncode != 0
    assert 'smoke_transport_failure' in result.stdout


def test_explicit_http_fallback_path_is_represented_and_testable() -> None:
    text = HARNESS_PATH.read_text(encoding='utf-8')
    assert '--operator-guide' in text
    assert 'smoke_explicit_http_fallback_ok' in text


def test_phase_572_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_572_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_572_main_commit_touches_no_cdl_path_or_protected_contract_file() -> None:
    commit_ref = _resolve_phase_572_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip_transport.py' not in changed_paths
    assert 'ilc_core/network/d2d/gossip_peer_registry.py' not in changed_paths
    assert 'ilc_core/network/d2d/http_gossip_transport_runtime.py' not in changed_paths
