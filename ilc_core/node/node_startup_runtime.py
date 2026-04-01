"""Phase 570 node startup runtime.

This module turns operator-managed JSON config and a test-grade genesis import
reference into the minimum startup context required for the three-machine
transport testbed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ilc_core.network.d2d.gossip_peer_registry import (
    GOSSIP_PEER_REGISTRY_VERSION as _GOSSIP_PEER_REGISTRY_CHECK,
    GossipPeerRegistry,
    validate_peer_endpoint,
)
from ilc_core.network.d2d.http_gossip_transport_runtime import (
    HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION as _HTTP_GOSSIP_TRANSPORT_CHECK,
    TransportRuntimeConfig,
)


NODE_STARTUP_RUNTIME_VERSION = "node_startup_runtime_570.v0.1"
GOSSIP_PEER_REGISTRY_DEPENDENCY = "gossip_peer_registry_562.v0.1"
HTTP_GOSSIP_TRANSPORT_DEPENDENCY = "http_gossip_transport_runtime_568.v0.1"

assert _GOSSIP_PEER_REGISTRY_CHECK == GOSSIP_PEER_REGISTRY_DEPENDENCY, (
    f"dep chain mismatch: {_GOSSIP_PEER_REGISTRY_CHECK}"
)
assert _HTTP_GOSSIP_TRANSPORT_CHECK == HTTP_GOSSIP_TRANSPORT_DEPENDENCY, (
    f"dep chain mismatch: {_HTTP_GOSSIP_TRANSPORT_CHECK}"
)


@dataclass(frozen=True)
class NodeStartupContext:
    node_id: str
    peer_registry: GossipPeerRegistry
    transport_config: TransportRuntimeConfig
    genesis_import_reference: dict[str, str]
    config_path: str
    genesis_reference_path: str


def _load_json_object(path: Path, missing_token: str, invalid_token: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(missing_token)
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ValueError(invalid_token) from exc
    if not isinstance(raw, dict):
        raise ValueError(invalid_token)
    return raw


def _require_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value.strip()


def _resolve_path(value: str, base_dir: Path) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def load_static_peer_config(config_path: str | Path) -> dict[str, Any]:
    path = Path(config_path)
    raw = _load_json_object(path, 'peer_config_file_not_found', 'peer_config_invalid_json')
    base_dir = path.parent

    node_id = _require_string(raw.get('node_id'), 'peer_config_missing_required_key')

    transport_raw = raw.get('transport')
    if not isinstance(transport_raw, dict):
        raise ValueError('peer_config_missing_required_key')

    try:
        bind_port = int(transport_raw.get('bind_port'))
    except (TypeError, ValueError) as exc:
        raise ValueError('peer_config_missing_required_key') from exc

    kind = _require_string(transport_raw.get('kind'), 'peer_config_missing_required_key')
    bind_host = _require_string(transport_raw.get('bind_host'), 'peer_config_missing_required_key')
    tls_cert_path = _require_string(transport_raw.get('tls_cert_path'), 'peer_config_missing_required_key')
    tls_key_path = _require_string(transport_raw.get('tls_key_path'), 'peer_config_missing_required_key')

    peers_raw = raw.get('peers')
    if not isinstance(peers_raw, list):
        raise ValueError('peer_config_missing_required_key')
    normalized_peers = [validate_peer_endpoint(peer) for peer in peers_raw]
    if len(normalized_peers) != len(set(normalized_peers)):
        raise ValueError('peer_config_duplicate_peer')

    return {
        'node_id': node_id,
        'transport': {
            'kind': kind,
            'bind_host': bind_host,
            'bind_port': bind_port,
            'tls_cert_path': _resolve_path(tls_cert_path, base_dir),
            'tls_key_path': _resolve_path(tls_key_path, base_dir),
        },
        'peers': normalized_peers,
        'config_path': str(path.resolve()),
    }


def load_genesis_import_reference(reference_path: str | Path) -> dict[str, str]:
    path = Path(reference_path)
    raw = _load_json_object(
        path,
        'genesis_import_reference_invalid',
        'genesis_import_reference_invalid',
    )
    base_dir = path.parent
    try:
        network_id = _require_string(raw.get('network_id'), 'genesis_import_reference_invalid')
        genesis_bundle_path = _require_string(raw.get('genesis_bundle_path'), 'genesis_import_reference_invalid')
        genesis_bundle_sha256 = _require_string(raw.get('genesis_bundle_sha256'), 'genesis_import_reference_invalid')
    except ValueError as exc:
        raise ValueError('genesis_import_reference_invalid') from exc

    resolved_bundle_path = Path(_resolve_path(genesis_bundle_path, base_dir))
    if not resolved_bundle_path.is_file():
        raise ValueError('genesis_import_reference_invalid')
    if not re.fullmatch(r'[0-9a-f]{64}', genesis_bundle_sha256):
        raise ValueError('genesis_import_reference_invalid')

    return {
        'network_id': network_id,
        'genesis_bundle_path': str(resolved_bundle_path),
        'genesis_bundle_sha256': genesis_bundle_sha256,
        'genesis_reference_path': str(path.resolve()),
    }


def build_node_startup_context(
    config_path: str | Path,
    reference_path: str | Path,
) -> NodeStartupContext:
    config = load_static_peer_config(config_path)
    genesis_reference = load_genesis_import_reference(reference_path)
    peer_registry = GossipPeerRegistry(config['peers'])
    transport = config['transport']
    transport_config = TransportRuntimeConfig(
        transport_kind=transport['kind'],
        bind_host=transport['bind_host'],
        bind_port=transport['bind_port'],
        tls_cert_path=transport['tls_cert_path'],
        tls_key_path=transport['tls_key_path'],
    )
    return NodeStartupContext(
        node_id=config['node_id'],
        peer_registry=peer_registry,
        transport_config=transport_config,
        genesis_import_reference={
            'network_id': genesis_reference['network_id'],
            'genesis_bundle_path': genesis_reference['genesis_bundle_path'],
            'genesis_bundle_sha256': genesis_reference['genesis_bundle_sha256'],
        },
        config_path=config['config_path'],
        genesis_reference_path=genesis_reference['genesis_reference_path'],
    )
