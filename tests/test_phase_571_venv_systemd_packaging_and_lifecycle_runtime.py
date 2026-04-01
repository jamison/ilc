from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools import run_ilc_node_service_v1 as runner
from tests.test_phase_568_real_http_transport_wrapper_runtime import _write_tls_material
from tests.test_phase_570_static_peer_config_json_loader_and_startup_wiring import (
    _write_bundle_and_reference,
    _write_config,
)


RUNNER_PATH = Path('tools/run_ilc_node_service_v1.py')
UNIT_PATH = Path('deploy/systemd/ilc-node-v1.service')
TEST_PATH = Path('tests/test_phase_571_venv_systemd_packaging_and_lifecycle_runtime.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_571_SUBJECT_TOKEN = 'phase 571 venv systemd packaging and lifecycle runtime'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNNER_PATH),
    str(UNIT_PATH),
    str(TEST_PATH),
}


def _write_service_inputs(tmp_path: Path) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = _write_config(tmp_path)
    source_cert, source_key = _write_tls_material(tmp_path)
    (tmp_path / 'cert.pem').write_text(Path(source_cert).read_text(encoding='utf-8'), encoding='utf-8')
    (tmp_path / 'key.pem').write_text(Path(source_key).read_text(encoding='utf-8'), encoding='utf-8')
    reference_path = _write_bundle_and_reference(tmp_path)
    return config_path, reference_path


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_571_commit_ref() -> str:
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
        if PHASE_571_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_571_commit_not_present_in_local_history')


def _run_service(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_service_runner_imports_and_exposes_deterministic_lifecycle_markers() -> None:
    assert runner.NODE_SERVICE_STARTING == 'node_service_starting'
    assert runner.NODE_SERVICE_READY == 'node_service_ready'
    assert runner.NODE_SERVICE_STOPPING == 'node_service_stopping'
    assert runner.NODE_SERVICE_RESTART_REQUESTED == 'node_service_restart_requested'
    assert runner.NODE_SERVICE_FAILED == 'node_service_failed'


def test_unit_file_exists_and_contains_required_fields() -> None:
    text = UNIT_PATH.read_text(encoding='utf-8')
    assert 'WorkingDirectory=/opt/ilc/current' in text
    assert 'EnvironmentFile=-/etc/ilc/ilc-node-v1.env' in text
    assert 'ExecStart=/opt/ilc/venv/bin/python /opt/ilc/current/tools/run_ilc_node_service_v1.py start' in text
    assert 'ExecStop=/opt/ilc/venv/bin/python /opt/ilc/current/tools/run_ilc_node_service_v1.py stop' in text
    assert 'ExecReload=/opt/ilc/venv/bin/python /opt/ilc/current/tools/run_ilc_node_service_v1.py restart' in text
    assert 'Restart=on-failure' in text


def test_config_and_startup_failures_map_to_deterministic_exit_codes(tmp_path: Path) -> None:
    missing_config = _run_service('start', '--config', str(tmp_path / 'missing.json'), '--genesis-ref', str(tmp_path / 'missing-ref.json'))
    assert missing_config.returncode == runner.CONFIG_EXIT_CODE

    config_path, reference_path = _write_service_inputs(tmp_path / 'quic-config')
    raw = json.loads(config_path.read_text(encoding='utf-8'))
    raw['transport']['kind'] = 'quic'
    config_path.write_text(json.dumps(raw), encoding='utf-8')
    transport_failure = _run_service('start', '--config', str(config_path), '--genesis-ref', str(reference_path))
    assert transport_failure.returncode == runner.TRANSPORT_EXIT_CODE

    config_path, _ = _write_service_inputs(tmp_path / 'bad-ref')
    bad_reference = tmp_path / 'bad-ref' / 'genesis_ref.json'
    bad_reference.parent.mkdir(parents=True, exist_ok=True)
    bad_reference.write_text(json.dumps({'network_id': 'testnet-0'}), encoding='utf-8')
    genesis_failure = _run_service('start', '--config', str(config_path), '--genesis-ref', str(bad_reference))
    assert genesis_failure.returncode == runner.GENESIS_EXIT_CODE


def test_runner_invokes_startup_runtime_rather_than_duplicating_config_parsing() -> None:
    text = RUNNER_PATH.read_text(encoding='utf-8')
    assert 'build_node_startup_context' in text
    assert 'json.loads' not in text


def test_log_output_contains_lifecycle_markers(tmp_path: Path) -> None:
    config_path, reference_path = _write_service_inputs(tmp_path)
    result = _run_service(
        'start',
        '--config', str(config_path),
        '--genesis-ref', str(reference_path),
        '--stay-alive-seconds', '0.01',
    )
    assert result.returncode == 0
    assert 'node_service_starting' in result.stdout
    assert 'node_service_ready' in result.stdout
    assert 'node_service_stopping' in result.stdout


def test_restart_path_is_represented_explicitly_in_service_layer(tmp_path: Path) -> None:
    config_path, reference_path = _write_service_inputs(tmp_path)
    result = _run_service(
        'restart',
        '--config', str(config_path),
        '--genesis-ref', str(reference_path),
        '--stay-alive-seconds', '0.01',
    )
    assert result.returncode == 0
    assert 'node_service_restart_requested' in result.stdout
    assert 'node_service_ready' in result.stdout


def test_phase_571_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_571_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_571_main_commit_touches_no_cdl_path_or_protected_contract_file() -> None:
    commit_ref = _resolve_phase_571_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip_transport.py' not in changed_paths
    assert 'ilc_core/network/d2d/gossip_peer_registry.py' not in changed_paths
    assert 'ilc_core/node/node_v0.py' not in changed_paths
