"""Phase 570 node startup runtime.

This module turns operator-managed JSON config and a test-grade genesis import
reference into the minimum startup context required for the three-machine
transport testbed.

Phase 916 (CDL-079) extension: bootstrap mode via ILC_BOOTSTRAP_SEED_PEER +
ILC_BOOTSTRAP_BUNDLE_CID. When both env vars are set, bootstrap_node_startup()
fetches and verifies a bootstrap bundle via CDL-077 WANT-BLOCK rather than
loading a static peer config. Static mode (existing behavior) is preserved
when neither env var is set.
"""

from __future__ import annotations

import json
import os
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
from ilc_core.network.d2d.peer_fingerprint_cache import (
    PEER_FINGERPRINT_CACHE_VERSION as _PEER_FINGERPRINT_CACHE_CHECK,
    PeerFingerprintCache,
)
from ilc_core.network.d2d.spectral_beacon import (
    BEACON_EMISSION_MODE_TESTNET,
    BeaconSigningKeypair,
    SealedSpectralBeaconEnvelope,
    TerminalOpenResult,
    build_sealed_spectral_beacon,
    sign_spectral_beacon,
)
from ilc_core.analysis.spectral_utils import spectral_distance
from ilc_core.network.star_map.star_map_route_index_runtime import (
    RouteIndex,
    query_route_index_spectral,
)


NODE_STARTUP_RUNTIME_VERSION = "node_startup_runtime_570.v0.1"
GOSSIP_PEER_REGISTRY_DEPENDENCY = "gossip_peer_registry_562.v0.1"
HTTP_GOSSIP_TRANSPORT_DEPENDENCY = "http_gossip_transport_runtime_568.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
H013_PEER_FINGERPRINT_CACHE_DEPENDENCY = "peer_fingerprint_cache_931.v0.1"
H013_SEQUENCE_LOCK_DEPENDENCY = "h013_gossip_beacon_activation_sequence_lock_930.v0.1"
# H-013 Q2: testnet sigma (10× conservative vs CDL-080 planning figure of 0.005).
# H-013 Q4: change threshold — emit only if spectral_distance(prev, curr) > this value.
# Both are provisional; SIM-BEACON-01 calibrates the production figures.
H013_TESTNET_EMISSION_SIGMA: float = 0.05
H013_CHANGE_THRESHOLD: float = 0.15  # CDL-082 ratified Phase 950; SIM-BEACON-01 evidence Phase 939

if _GOSSIP_PEER_REGISTRY_CHECK != GOSSIP_PEER_REGISTRY_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "node_startup_dep_chain_mismatch",
                "dependency": "gossip_peer_registry",
                "expected": GOSSIP_PEER_REGISTRY_DEPENDENCY,
                "got": _GOSSIP_PEER_REGISTRY_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("node_startup_gossip_peer_registry_dependency_mismatch")

if _HTTP_GOSSIP_TRANSPORT_CHECK != HTTP_GOSSIP_TRANSPORT_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "node_startup_dep_chain_mismatch",
                "dependency": "http_gossip_transport_runtime",
                "expected": HTTP_GOSSIP_TRANSPORT_DEPENDENCY,
                "got": _HTTP_GOSSIP_TRANSPORT_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("node_startup_http_gossip_transport_dependency_mismatch")

if _PEER_FINGERPRINT_CACHE_CHECK != H013_PEER_FINGERPRINT_CACHE_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "node_startup_dep_chain_mismatch",
                "dependency": "peer_fingerprint_cache",
                "expected": H013_PEER_FINGERPRINT_CACHE_DEPENDENCY,
                "got": _PEER_FINGERPRINT_CACHE_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("node_startup_h013_peer_fingerprint_cache_dependency_mismatch")


@dataclass(frozen=True)
class NodeStartupContext:
    node_id: str
    peer_registry: GossipPeerRegistry
    transport_config: TransportRuntimeConfig
    genesis_import_reference: dict[str, str]
    config_path: str
    genesis_reference_path: str
    # H-013 Phase 934: rolling peer fingerprint cache (mutable; frozen only prevents
    # replacing the reference, not updating the cache in place).
    peer_fingerprint_cache: PeerFingerprintCache


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


def _optional_bool(raw: dict[str, Any], key: str, default: bool) -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise ValueError('peer_config_invalid_optional_bool')
    return value


def load_static_peer_config(
    config_path: str | Path,
    *,
    allow_private_peer_endpoints_for_tests: bool = False,
) -> dict[str, Any]:
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
    transport_allow_private_peer_endpoints = _optional_bool(
        transport_raw,
        'allow_private_peer_endpoints_for_tests',
        False,
    )
    transport_verify_peer_tls = _optional_bool(
        transport_raw,
        'verify_peer_tls',
        True,
    )
    effective_allow_private = (
        allow_private_peer_endpoints_for_tests
        or transport_allow_private_peer_endpoints
    )

    peers_raw = raw.get('peers')
    if not isinstance(peers_raw, list):
        raise ValueError('peer_config_missing_required_key')
    normalized_peers = [
        validate_peer_endpoint(
            peer,
            allow_private_address_literals=effective_allow_private,
        )
        for peer in peers_raw
    ]
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
            'allow_private_peer_endpoints_for_tests': effective_allow_private,
            'verify_peer_tls': transport_verify_peer_tls,
        },
        'peers': normalized_peers,
        'config_path': str(path.resolve()),
    }


def load_genesis_import_reference(reference_path: str | Path) -> dict[str, str]:
    path = Path(reference_path)
    raw = _load_json_object(
        path,
        'genesis_import_reference_invalid',
        'genesis_import_reference_invalid'
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
    *,
    allow_private_peer_endpoints_for_tests: bool = False,
) -> NodeStartupContext:
    config = load_static_peer_config(
        config_path,
        allow_private_peer_endpoints_for_tests=allow_private_peer_endpoints_for_tests,
    )
    genesis_reference = load_genesis_import_reference(reference_path)
    peer_registry = GossipPeerRegistry(
        config['peers'],
        allow_private_address_literals=config['transport']['allow_private_peer_endpoints_for_tests'],
    )
    transport = config['transport']
    transport_config = TransportRuntimeConfig(
        transport_kind=transport['kind'],
        bind_host=transport['bind_host'],
        bind_port=transport['bind_port'],
        tls_cert_path=transport['tls_cert_path'],
        tls_key_path=transport['tls_key_path'],
        verify_peer_tls=transport['verify_peer_tls'],
        allow_private_peer_endpoints_for_tests=transport['allow_private_peer_endpoints_for_tests'],
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
        peer_fingerprint_cache=PeerFingerprintCache(),
    )


# ---------------------------------------------------------------------------
# H-013 Phase 934: peer fingerprint cache population
# ---------------------------------------------------------------------------


def populate_fingerprint_from_beacon(
    ctx: NodeStartupContext,
    terminal_result: TerminalOpenResult,
) -> None:
    """Record a peer's spectral fingerprint from an opened beacon.

    Called by the gossip receive path after peel_relay_layer + open_terminal_layer
    have verified and decrypted the sealed beacon. Overwrites any prior entry for
    the same peer (H-013 Q3 = Option D: overwrite-only, no epoch-based eviction).

    Args:
        ctx: node startup context carrying the peer fingerprint cache.
        terminal_result: decrypted terminal result from open_terminal_layer().
    """
    ctx.peer_fingerprint_cache.update(
        peer_endpoint=terminal_result.terminal_peer_id,
        lambda_local=terminal_result.beacon.lambda_local,
        noise_sigma=terminal_result.beacon.noise_sigma,
        epoch=terminal_result.beacon.epoch,
        agent_id=terminal_result.beacon.agent_id,
    )


# ---------------------------------------------------------------------------
# H-013 Phase 935: L3 spectral routing wired to live peer fingerprint cache
# ---------------------------------------------------------------------------


def get_live_peer_fingerprints(
    ctx: NodeStartupContext,
    current_epoch: int,
) -> dict[str, list[float]]:
    """Return live peer fingerprints for L3 spectral routing.

    Excludes peers silent for > DEFAULT_DEAD_PEER_SILENCE_EPOCHS epochs.
    Snapshot is consistent with the cache state at call time.

    Args:
        ctx: node startup context carrying the peer fingerprint cache.
        current_epoch: the current validation epoch (local node clock).

    Returns:
        {peer_endpoint: lambda_local} dict for query_route_index_spectral().
    """
    return ctx.peer_fingerprint_cache.live_fingerprint_dict(current_epoch)


def query_spectral_route(
    ctx: NodeStartupContext,
    route_index: RouteIndex,
    query: str,
    local_fingerprint: list[float],
    current_epoch: int,
    top_k: int = 16,
) -> list:
    """Query the L3 spectral route index using live peer fingerprints.

    Thin convenience wrapper: fetches live fingerprints from the peer cache
    and passes them to query_route_index_spectral(). This closes the gap
    identified in the H-013 sequence lock — without live fingerprints from
    the cache, spectral routing fell back to manually-configured test data.

    CDL-080 §4.5: returned hints are advisory; L2 fetch is authoritative.

    Args:
        ctx: node startup context (supplies live peer fingerprint cache).
        route_index: the populated star-map route index to query.
        query: semantic query string.
        local_fingerprint: this node's spectral fingerprint (top-k eigenvalues).
        current_epoch: used to exclude dead peers from the fingerprint snapshot.
        top_k: maximum route hints to return.

    Returns:
        List of RouteHint ordered by combined N-gram + spectral proximity.
    """
    return query_route_index_spectral(
        route_index,
        query,
        local_fingerprint,
        peer_fingerprints=get_live_peer_fingerprints(ctx, current_epoch),
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# H-013 Phase 936: testnet beacon emission wiring
# ---------------------------------------------------------------------------


@dataclass
class SpectralEmissionState:
    """Mutable per-node state for epoch-cadenced beacon emission.

    Tracks the previously emitted fingerprint and the epoch of last emission
    so that maybe_emit_spectral_beacon() can apply the H-013 Q4 change-threshold
    gate without re-computing history.

    Attributes:
        prev_lambda: fingerprint emitted in the last beacon, or None if this
            node has never emitted. None forces emission on the first call
            (no prior baseline to compare against).
        last_emit_epoch: epoch of the last emission, or None if never emitted.
    """

    prev_lambda: list[float] | None = None
    last_emit_epoch: int | None = None


def maybe_emit_spectral_beacon(
    emission_state: SpectralEmissionState,
    signing_keypair: BeaconSigningKeypair,
    *,
    relay_peer_id: str,
    relay_public_key: bytes,
    terminal_peer_id: str,
    terminal_public_key: bytes,
    channel_id: str,
    current_epoch: int,
    lambda_local: list[float],
    mode: str = BEACON_EMISSION_MODE_TESTNET,
) -> SealedSpectralBeaconEnvelope | None:
    """Emit a sealed spectral beacon if the mode and change-threshold gate allows.

    H-013 Q1 (Option C): guarded by mode flag. Only BEACON_EMISSION_MODE_TESTNET
        is reachable here. BEACON_EMISSION_MODE_MAINNET requires SIM-BEACON-01
        completion and a separate mainnet activation path — that path is not
        opened in this window.
    H-013 Q2: sigma = H013_TESTNET_EMISSION_SIGMA (0.05); SIM-BEACON-01 calibrates.
    H-013 Q4 (Option D): emit once per epoch only if
        spectral_distance(prev, curr) > H013_CHANGE_THRESHOLD (0.15, CDL-082 ratified Phase 950).
        Stable nodes emit infrequently, reducing bandwidth and structural leakage.
    H-013 Q5 (Option A): sealed sender applied to beacon messages only.

    Args:
        emission_state: mutable state; updated in place on successful emission.
        signing_keypair: Ed25519 keypair for beacon authentication.
        relay_peer_id: the relay peer's peer ID string.
        relay_public_key: the relay peer's X25519 public key (32 bytes).
        terminal_peer_id: the terminal peer's peer ID string.
        terminal_public_key: the terminal peer's X25519 public key (32 bytes).
        channel_id: gossip channel ID for this emission.
        current_epoch: current validation epoch from the local node clock.
        lambda_local: this node's current spectral fingerprint (noise added here).
        mode: emission mode guard. Must equal BEACON_EMISSION_MODE_TESTNET.

    Returns:
        SealedSpectralBeaconEnvelope if the gate allowed emission; None otherwise.
    """
    if mode != BEACON_EMISSION_MODE_TESTNET:
        # Mainnet emission path is not open. BEACON_EMISSION_MODE_MAINNET
        # becomes reachable only after SIM-BEACON-01 completes.
        return None

    if emission_state.prev_lambda is not None:
        delta = spectral_distance(emission_state.prev_lambda, lambda_local)
        if delta <= H013_CHANGE_THRESHOLD:
            # Fingerprint has not changed enough — stable node, suppress emission.
            return None

    beacon = sign_spectral_beacon(
        epoch=current_epoch,
        lambda_local=lambda_local,
        noise_sigma=H013_TESTNET_EMISSION_SIGMA,
        signing_keypair=signing_keypair,
    )
    envelope = build_sealed_spectral_beacon(
        beacon=beacon,
        relay_peer_id=relay_peer_id,
        relay_public_key=relay_public_key,
        terminal_peer_id=terminal_peer_id,
        terminal_public_key=terminal_public_key,
        channel_id=channel_id,
    )
    emission_state.prev_lambda = list(lambda_local)
    emission_state.last_emit_epoch = current_epoch
    return envelope


# ---------------------------------------------------------------------------
# CDL-079 bootstrap mode (Phase 916)
# ---------------------------------------------------------------------------


class BootstrapError(Exception):
    """Bootstrap startup failure — bundle not found, invalid, or unverifiable."""

    def __init__(self, token: str, detail: str = "") -> None:
        super().__init__(detail or token)
        self.token = token


def bootstrap_node_startup(
    bootstrap_seed_peer: str,
    bootstrap_bundle_cid: str,
    genesis_authority_pubkey_hex: str,
) -> list[str]:
    """Fetch, verify, and extract peer endpoints from a bootstrap bundle.

    Fetches the bootstrap bundle (CDL-079 bootstrap_bundle_v1) from the seed
    peer via CDL-077 WANT-BLOCK, verifies the ML-DSA-65 signature against the
    genesis authority key (CDL-073), and returns the verified peer endpoint list.

    The caller is responsible for building a GossipPeerRegistry from the
    returned endpoints (explicit-promotion model preserved).

    Args:
        bootstrap_seed_peer:          HTTPS endpoint of the seed peer.
        bootstrap_bundle_cid:         CIDv1 of the bootstrap bundle.
        genesis_authority_pubkey_hex: ML-DSA-65 genesis authority pubkey (hex).

    Returns:
        List of normalized peer HTTPS endpoints from the verified bundle.

    Raises:
        BootstrapError: If bundle not found, signature invalid, or no peers extracted.
    """
    from ilc_core.network.d2d.bootstrap_fetch_runtime import (
        extract_peer_endpoints,
        fetch_bootstrap_bundle,
        verify_bootstrap_bundle_signature,
    )

    bundle = fetch_bootstrap_bundle(bootstrap_seed_peer, bootstrap_bundle_cid)
    if bundle is None:
        raise BootstrapError(
            "bootstrap_bundle_not_found",
            f"bundle_cid={bootstrap_bundle_cid} not found at seed peer {bootstrap_seed_peer}",
        )

    if not verify_bootstrap_bundle_signature(bundle, genesis_authority_pubkey_hex):
        raise BootstrapError(
            "bootstrap_bundle_signature_invalid",
            f"bundle_cid={bootstrap_bundle_cid}: signature verification failed",
        )

    endpoints = extract_peer_endpoints(bundle)
    if not endpoints:
        raise BootstrapError(
            "bootstrap_bundle_no_peers",
            f"bundle_cid={bootstrap_bundle_cid}: no valid peer endpoints after verification",
        )

    return endpoints


def detect_bootstrap_mode() -> tuple[str, str] | None:
    """Read ILC_BOOTSTRAP_SEED_PEER and ILC_BOOTSTRAP_BUNDLE_CID from env.

    Returns:
        (seed_peer, bundle_cid) tuple if both are set.
        None if neither is set (static mode).

    Raises:
        ValueError: With token 'bootstrap_mode_requires_both_seed_peer_and_bundle_cid'
                    if exactly one is set.
    """
    seed_peer = os.environ.get("ILC_BOOTSTRAP_SEED_PEER", "").strip()
    bundle_cid = os.environ.get("ILC_BOOTSTRAP_BUNDLE_CID", "").strip()

    if bool(seed_peer) != bool(bundle_cid):
        raise ValueError("bootstrap_mode_requires_both_seed_peer_and_bundle_cid")

    if seed_peer and bundle_cid:
        return seed_peer, bundle_cid
    return None
