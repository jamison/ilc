# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import ilc_core.network.d2d.gossip_peer_registry as registry_module
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH, _MLDSA_SIG_HEX_LENGTH
from ilc_core.network.connectivity_mode import ConnectivityMode, ConnectivityReceipt
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.peer_advertisement import TransportEndpoint
from ilc_core.sidecars.connectivity_advertisement import (
    CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED,
    CONNECTIVITY_ADVERTISEMENT_RUNTIME_TOKEN,
    CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
    ConnectivityAdvertisement,
    ConnectivityAdvertisementValidationError,
    ConnectivityAdvertisementValidator,
    VerifiedConnectivityAdvertisement,
    connectivity_advertisement_from_receipt,
    connectivity_advertisement_sidecar_manifest,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/connectivity_advertisement.py"

AGENT_ID = "1" * 96
DIGEST = "2" * 96
PROBE_REF = "3" * 96
SIG_HEX = "a" * _MLDSA_SIG_HEX_LENGTH
PUBKEY_HEX = "b" * _MLDSA_PK_HEX_LENGTH


def _endpoint(host: str = "node.example.com", port: int = 443) -> TransportEndpoint:
    return TransportEndpoint.from_mapping({"host": host, "port": port, "scheme": "https"})


def _ad_dict(
    *,
    mode: str = "direct_public",
    candidate_list: list[dict[str, object]] | None = None,
    relay_endpoint: dict[str, object] | None = None,
    relay_slot_ref: str | None = None,
    timestamp: int = 10,
    ttl: int = 4,
) -> dict[str, object]:
    body = {
        "agent_id": AGENT_ID,
        "candidate_list": [] if candidate_list is None else candidate_list,
        "connectivity_mode": mode,
        "content_availability_count": 7,
        "installed_slices_digest": DIGEST,
        "peer_timestamp_epoch": timestamp,
        "probe_receipt_ref": PROBE_REF,
        "protocol_version": "ilc-d2d-gossip.v1",
        "relay_endpoint": relay_endpoint,
        "relay_slot_ref": relay_slot_ref,
        "schema_version": CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
        "transport_endpoint": _endpoint().to_dict(),
        "ttl_epochs": ttl,
    }
    return {
        "body": body,
        "key_binding_ref": "key-binding-a",
        "ml_dsa_signature": SIG_HEX,
        "schema_version": CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
    }


def _ad(
    *,
    mode: str = "direct_public",
    candidate_list: list[dict[str, object]] | None = None,
    relay_endpoint: dict[str, object] | None = None,
    relay_slot_ref: str | None = None,
    timestamp: int = 10,
    ttl: int = 4,
) -> ConnectivityAdvertisement:
    return ConnectivityAdvertisement.from_dict(
        _ad_dict(
            mode=mode,
            candidate_list=candidate_list,
            relay_endpoint=relay_endpoint,
            relay_slot_ref=relay_slot_ref,
            timestamp=timestamp,
            ttl=ttl,
        )
    )


def test_connectivity_advertisement_sidecar_imports_guarded_and_manifested() -> None:
    assert CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED is True
    assert CONNECTIVITY_ADVERTISEMENT_RUNTIME_TOKEN == (
        "connectivity_advertisement_runtime_committed_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_IMPL_00"
    )
    manifest = connectivity_advertisement_sidecar_manifest()
    assert manifest["sidecar_id"] == "connectivity-advertisement"
    assert manifest["candidate_endpoint_cap"] == 3
    assert manifest["connectivity_advertisement_activated"] is False
    assert manifest["public_gossip_propagation_enabled"] is False


def test_connectivity_advertisement_canonical_json_excludes_signature_and_is_stable() -> None:
    ad = _ad()
    canonical = ad.to_canonical_json()
    assert canonical == json.dumps(
        ad.body_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    assert SIG_HEX.encode("ascii") not in canonical
    assert ad.to_dict()["body"]["schema_version"] == CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION


def test_connectivity_advertisement_verifier_accepts_valid_signature_context() -> None:
    seen: dict[str, bytes] = {}

    def verify(message: bytes, signature_hex: str, pubkey_hex: str) -> bool:
        seen["message"] = message
        return signature_hex == SIG_HEX and pubkey_hex == PUBKEY_HEX

    verified = ConnectivityAdvertisementValidator(
        ml_dsa_verify_fn=verify,
        pubkey_hex=PUBKEY_HEX,
        current_epoch=10,
    ).validate(_ad_dict())

    assert isinstance(verified, VerifiedConnectivityAdvertisement)
    assert verified.advertisement.agent_id == AGENT_ID
    assert seen["message"] == verified.advertisement.to_canonical_json()


def test_connectivity_advertisement_rejects_candidate_list_over_three() -> None:
    candidates = [
        _endpoint(f"candidate-{index}.example.com", 443).to_dict()
        for index in range(4)
    ]
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="candidate_list_exceeds_max_3",
    ):
        _ad(candidate_list=candidates)


def test_connectivity_advertisement_rejects_non_iterable_candidate_list() -> None:
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="candidate_list_invalid",
    ):
        ConnectivityAdvertisement(
            agent_id=AGENT_ID,
            transport_endpoint=_endpoint(),
            protocol_version="ilc-d2d-gossip.v1",
            installed_slices_digest=DIGEST,
            content_availability_count=7,
            peer_timestamp_epoch=10,
            ttl_epochs=4,
            connectivity_mode=ConnectivityMode.DIRECT_PUBLIC,
            relay_endpoint=None,
            candidate_list=None,  # type: ignore[arg-type]
            probe_receipt_ref=PROBE_REF,
            relay_slot_ref=None,
            ml_dsa_signature=SIG_HEX,
            key_binding_ref="key-binding-a",
        )


def test_connectivity_advertisement_direct_constructor_rejects_untrimmed_protocol_strings() -> None:
    base = {
        "agent_id": AGENT_ID,
        "transport_endpoint": _endpoint(),
        "protocol_version": "ilc-d2d-gossip.v1",
        "installed_slices_digest": DIGEST,
        "content_availability_count": 7,
        "peer_timestamp_epoch": 10,
        "ttl_epochs": 4,
        "connectivity_mode": ConnectivityMode.RELAY_REACHABLE,
        "relay_endpoint": _endpoint("relay.example.com", 51151),
        "candidate_list": (),
        "probe_receipt_ref": PROBE_REF,
        "relay_slot_ref": "slot-001",
        "ml_dsa_signature": SIG_HEX,
        "key_binding_ref": "key-binding-a",
    }
    for field, token in (
        ("protocol_version", "protocol_version_invalid"),
        ("key_binding_ref", "key_binding_ref_invalid"),
        ("relay_slot_ref", "relay_slot_ref_invalid"),
    ):
        kwargs = dict(base)
        kwargs[field] = f" {kwargs[field]} "
        with pytest.raises(ConnectivityAdvertisementValidationError, match=token):
            ConnectivityAdvertisement(**kwargs)


def test_connectivity_advertisement_rejects_duplicate_candidates_and_primary() -> None:
    duplicate = [_endpoint("dup.example.com", 443).to_dict()] * 2
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="candidate_endpoint_duplicate",
    ):
        _ad(candidate_list=duplicate)

    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="candidate_endpoint_duplicate",
    ):
        _ad(candidate_list=[_endpoint("node.example.com", 443).to_dict()])


def test_connectivity_advertisement_rejects_unknown_relay_candidate_mode() -> None:
    with pytest.raises(ConnectivityAdvertisementValidationError, match="mode_invalid"):
        _ad(mode="relay_candidate")


def test_connectivity_advertisement_relay_modes_require_relay_endpoint() -> None:
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="relay_mode_requires_relay_endpoint",
    ):
        _ad(mode="relay_reachable")

    relay = _endpoint("relay.example.com", 51151).to_dict()
    ad = _ad(
        mode="relay_reachable",
        relay_endpoint=relay,
        relay_slot_ref="slot-001",
    )
    assert ad.relay_endpoint is not None
    assert ad.connectivity_mode is ConnectivityMode.RELAY_REACHABLE


def test_connectivity_advertisement_direct_modes_reject_relay_endpoint_and_slot() -> None:
    relay = _endpoint("relay.example.com", 51151).to_dict()
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="non_relay_mode_relay_endpoint_forbidden",
    ):
        _ad(relay_endpoint=relay)

    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="non_relay_mode_slot_ref_forbidden",
    ):
        _ad(relay_slot_ref="slot-001")


def test_connectivity_advertisement_non_reachable_modes_are_not_advertisable() -> None:
    for mode in ("local_only", "outbound_only"):
        with pytest.raises(
            ConnectivityAdvertisementValidationError,
            match="mode_not_advertisable",
        ):
            _ad(mode=mode)


def test_connectivity_advertisement_validator_rejects_future_expired_and_bad_signature() -> None:
    validator = ConnectivityAdvertisementValidator(
        ml_dsa_verify_fn=lambda *_args: True,
        pubkey_hex=PUBKEY_HEX,
        current_epoch=10,
    )
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="timestamp_future_skew",
    ):
        validator.validate(_ad_dict(timestamp=12))
    with pytest.raises(ConnectivityAdvertisementValidationError, match="expired"):
        validator.validate(_ad_dict(timestamp=5, ttl=4))

    bad_sig_validator = ConnectivityAdvertisementValidator(
        ml_dsa_verify_fn=lambda *_args: False,
        pubkey_hex=PUBKEY_HEX,
        current_epoch=10,
    )
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="signature_invalid",
    ):
        bad_sig_validator.validate(_ad_dict())


def test_connectivity_advertisement_from_receipt_builds_direct_and_relay_ads() -> None:
    direct = ConnectivityReceipt(
        mode=ConnectivityMode.DIRECT_PUBLIC,
        observed_endpoint="peer.example.com:443",
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    direct_ad = connectivity_advertisement_from_receipt(
        direct,
        agent_id=AGENT_ID,
        protocol_version="ilc-d2d-gossip.v1",
        installed_slices_digest=DIGEST,
        content_availability_count=0,
        peer_timestamp_epoch=10,
        ttl_epochs=4,
        ml_dsa_signature=SIG_HEX,
        key_binding_ref="key-binding-a",
        probe_receipt_ref=PROBE_REF,
    )
    assert direct_ad.endpoint_url == "https://peer.example.com:443"
    assert direct_ad.relay_endpoint is None

    relay = ConnectivityReceipt(
        mode=ConnectivityMode.RELAY_REACHABLE,
        observed_endpoint=None,
        relay_endpoint="relay.example.com:51151",
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    relay_ad = connectivity_advertisement_from_receipt(
        relay,
        agent_id=AGENT_ID,
        protocol_version="ilc-d2d-gossip.v1",
        installed_slices_digest=DIGEST,
        content_availability_count=0,
        peer_timestamp_epoch=10,
        ttl_epochs=4,
        ml_dsa_signature=SIG_HEX,
        key_binding_ref="key-binding-a",
        probe_receipt_ref=PROBE_REF,
        relay_slot_ref="slot-001",
    )
    assert relay_ad.endpoint_url == "https://relay.example.com:51151"
    assert relay_ad.relay_endpoint is not None


def test_connectivity_advertisement_from_receipt_rejects_local_only() -> None:
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.LOCAL_ONLY,
        observed_endpoint=None,
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="receipt_endpoint_required",
    ):
        connectivity_advertisement_from_receipt(
            receipt,
            agent_id=AGENT_ID,
            protocol_version="ilc-d2d-gossip.v1",
            installed_slices_digest=DIGEST,
            content_availability_count=0,
            peer_timestamp_epoch=10,
            ttl_epochs=4,
            ml_dsa_signature=SIG_HEX,
            key_binding_ref="key-binding-a",
        )


def test_gossip_registry_connectivity_advertisement_path_is_guarded() -> None:
    registry = GossipPeerRegistry([])
    with pytest.raises(RuntimeError, match="connectivity_advertisement_not_activated"):
        registry.add_connectivity_advertisement(
            VerifiedConnectivityAdvertisement(_ad()),
            current_epoch=10,
        )
    assert registry.get_connectivity_advertisements(current_epoch=10) == []


def test_gossip_registry_can_store_connectivity_ads_when_guard_is_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = GossipPeerRegistry([])
    monkeypatch.setattr(registry_module, "CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED", False)

    assert registry.add_connectivity_advertisement(
        VerifiedConnectivityAdvertisement(_ad(timestamp=10)),
        current_epoch=10,
    ) is True
    assert len(registry.get_connectivity_advertisements(current_epoch=10)) == 1
    assert registry.expire_connectivity_ads(current_epoch=14) == 1
    assert registry.get_connectivity_advertisements(current_epoch=14) == []


def test_sidecar_registry_includes_connectivity_advertisement_default_off() -> None:
    manifest = build_sidecar_registry_manifest()
    sidecars = {sidecar["sidecar_id"]: sidecar for sidecar in manifest["sidecars"]}

    assert "connectivity-advertisement" in sidecars
    assert sidecars["connectivity-advertisement"]["public_serving_enabled"] is False
    integrity = manifest["package_profile_integrity"][
        "connectivity_advertisement_sidecar_manifest"
    ]
    assert integrity["public_gossip_propagation_enabled"] is False
    assert integrity["connectivity_advertisement_activated"] is False


def test_connectivity_advertisement_sidecar_uses_no_wall_clock_imports() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = {alias.name.split(".")[0] for alias in node.names}
            assert "datetime" not in imported
            assert "time" not in imported
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in {"datetime", "time"}
