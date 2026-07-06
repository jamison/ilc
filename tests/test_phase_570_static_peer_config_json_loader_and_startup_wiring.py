from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.http_gossip_transport_runtime import TransportRuntimeConfig
from ilc_core.node import node_startup_runtime as runtime


RUNTIME_PATH = Path('ilc_core/node/node_startup_runtime.py')
TEST_PATH = Path('tests/test_phase_570_static_peer_config_json_loader_and_startup_wiring.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_570_SUBJECT_TOKEN = 'phase 570 static peer config json loader and startup wiring'
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(TEST_PATH),
}


def _write_bundle_and_reference(tmp_path: Path) -> Path:
    bundle_path = tmp_path / 'genesis_bundle.json'
    bundle_bytes = b'{"bundle_id":"genesis-testbed-0"}'
    bundle_path.write_bytes(bundle_bytes)
    reference_path = tmp_path / 'genesis_ref.json'
    reference_path.write_text(
        json.dumps(
            {
                'network_id': 'testnet-0',
                'genesis_bundle_path': bundle_path.name,
                'genesis_bundle_sha256': hashlib.sha256(bundle_bytes).hexdigest(),
            }
        ),
        encoding='utf-8',
    )
    return reference_path


def _write_config(tmp_path: Path, *, peers: list[str] | None = None) -> Path:
    if peers is None:
        peers = ['https://a.example.com', 'https://b.example.com']
    (tmp_path / 'cert.pem').write_text('cert', encoding='utf-8')
    (tmp_path / 'key.pem').write_text('key', encoding='utf-8')
    config_path = tmp_path / 'node_config.json'
    config_path.write_text(
        json.dumps(
            {
                'node_id': 'node-alpha',
                'transport': {
                    'kind': 'http',
                    'bind_host': '127.0.0.1',
                    'bind_port': 18570,
                    'tls_cert_path': 'cert.pem',
                    'tls_key_path': 'key.pem',
                },
                'peers': peers,
            }
        ),
        encoding='utf-8',
    )
    return config_path


def _write_testbed_config(tmp_path: Path) -> Path:
    config_path = _write_config(
        tmp_path,
        peers=['https://100.112.32.42:443'],
    )
    payload = json.loads(config_path.read_text(encoding='utf-8'))
    payload['transport']['allow_private_peer_endpoints_for_tests'] = True
    payload['transport']['verify_peer_tls'] = False
    config_path.write_text(json.dumps(payload), encoding='utf-8')
    return config_path


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_570_commit_ref() -> str:
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
        if PHASE_570_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_570_commit_not_present_in_local_history')


def test_module_imports_and_exposes_exact_constants() -> None:
    assert runtime.NODE_STARTUP_RUNTIME_VERSION == 'node_startup_runtime_570.v0.1'
    assert runtime.GOSSIP_PEER_REGISTRY_DEPENDENCY == 'gossip_peer_registry_1571.v0.1'
    assert runtime.HTTP_GOSSIP_TRANSPORT_DEPENDENCY == 'http_gossip_transport_runtime_568.v0.1'


def test_valid_json_config_produces_gossip_peer_registry(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    reference_path = _write_bundle_and_reference(tmp_path)
    context = runtime.build_node_startup_context(config_path, reference_path)
    assert isinstance(context.peer_registry, GossipPeerRegistry)
    assert context.peer_registry.get_peers() == ['https://a.example.com', 'https://b.example.com']


def test_invalid_json_fails_with_deterministic_token(tmp_path: Path) -> None:
    config_path = tmp_path / 'node_config.json'
    config_path.write_text('{not-valid-json', encoding='utf-8')
    with pytest.raises(ValueError, match='peer_config_invalid_json'):
        runtime.load_static_peer_config(config_path)


def test_missing_required_key_fails_with_deterministic_token(tmp_path: Path) -> None:
    config_path = tmp_path / 'node_config.json'
    config_path.write_text(json.dumps({'node_id': 'node-alpha'}), encoding='utf-8')
    with pytest.raises(ValueError, match='peer_config_missing_required_key'):
        runtime.load_static_peer_config(config_path)


def test_duplicate_peer_entry_fails_with_deterministic_token(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        peers=['https://A.EXAMPLE.com', 'https://a.example.com'],
    )
    with pytest.raises(ValueError, match='peer_config_duplicate_peer'):
        runtime.load_static_peer_config(config_path)


def test_tailscale_peer_endpoint_requires_explicit_testbed_opt_in(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, peers=['https://100.112.32.42:443'])

    with pytest.raises(ValueError, match='peer_endpoint_private_address_forbidden_phase_1332_fix4'):
        runtime.load_static_peer_config(config_path)


def test_testbed_opt_in_allows_tailscale_peer_and_disables_peer_tls_verification(tmp_path: Path) -> None:
    config_path = _write_testbed_config(tmp_path)
    reference_path = _write_bundle_and_reference(tmp_path)

    context = runtime.build_node_startup_context(config_path, reference_path)

    assert context.peer_registry.get_peers() == ['https://100.112.32.42:443']
    assert context.transport_config.allow_private_peer_endpoints_for_tests is True
    assert context.transport_config.verify_peer_tls is False


def test_valid_genesis_import_reference_loads_successfully(tmp_path: Path) -> None:
    reference_path = _write_bundle_and_reference(tmp_path)
    loaded = runtime.load_genesis_import_reference(reference_path)
    assert loaded['network_id'] == 'testnet-0'
    assert loaded['genesis_bundle_path'].endswith('genesis_bundle.json')


def test_invalid_genesis_import_reference_fails_deterministically(tmp_path: Path) -> None:
    reference_path = tmp_path / 'genesis_ref.json'
    reference_path.write_text(json.dumps({'network_id': 'testnet-0'}), encoding='utf-8')
    with pytest.raises(ValueError, match='genesis_import_reference_invalid'):
        runtime.load_genesis_import_reference(reference_path)


def test_startup_context_contains_expected_fields_and_types(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    reference_path = _write_bundle_and_reference(tmp_path)
    context = runtime.build_node_startup_context(config_path, reference_path)
    assert isinstance(context, runtime.NodeStartupContext)
    assert context.node_id == 'node-alpha'
    assert isinstance(context.peer_registry, GossipPeerRegistry)
    assert isinstance(context.transport_config, TransportRuntimeConfig)
    assert context.transport_config.transport_kind == 'http'
    assert context.genesis_import_reference['network_id'] == 'testnet-0'


def test_startup_context_surfaces_h013_sigma_policy_status(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    reference_path = _write_bundle_and_reference(tmp_path)
    context = runtime.build_node_startup_context(config_path, reference_path)

    assert context.sigma_policy_status['obl_id'] == 'OBL-046'
    assert context.sigma_policy_status['pre_public_rc_blocker'] is True
    assert context.sigma_policy_status['sigma_dp_calibration_validated'] is False
    assert (
        context.sigma_policy_status['sigma_mainnet_provisional_status']
        == 'genesis_authorized_provisional_mainnet_sigma_obl_046_open'
    )


def test_phase_570_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_570_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_570_main_commit_touches_no_cdl_path_or_protected_file() -> None:
    commit_ref = _resolve_phase_570_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert 'ilc_core/network/d2d/gossip_peer_registry.py' not in changed_paths
    assert 'ilc_core/network/d2d/gossip_transport.py' not in changed_paths
    assert 'ilc_core/node/node_v0.py' not in changed_paths
    assert 'ilc_core/node/devnet.py' not in changed_paths
