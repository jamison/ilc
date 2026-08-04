# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import pytest

import ilc_core.network.d2d.gossip_peer_registry as registry_module
import ilc_core.network.d2d.peer_discovery_manager as manager_module
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.peer_advertisement import MAX_TTL_EPOCHS, PeerAdvertisement
from ilc_core.network.d2d.peer_discovery_manager import PeerDiscoveryManager


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION_DOC = (
    ROOT / "docs/specs/ilc_cdl_103_dynamic_peer_discovery_ratification_1583_v0.1.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SPEC = ROOT / "docs/specs/ilc_dynamic_peer_discovery_spec_v0.1.md"
PUBLIC_PREFLIGHT = ROOT / "ilc_core/graph/sidecar_public_path_preflight.py"
TRANSPORT_ADMISSION = ROOT / "ilc_core/sidecars/transport_principal_admission.py"
GOSSIP_POLICY = ROOT / "ilc_core/sidecars/confidential_coordination_gossip_policy.py"

PUBKEY_HEX = "a" * 3328
SIG_HEX = "b" * 6618
AGENT_A = "1" * 96
DIGEST_A = "3" * 96


def _ad_dict(*, timestamp: int = 10, ttl: int = 4) -> dict[str, object]:
    return {
        "body": {
            "agent_id": AGENT_A,
            "content_availability_count": 7,
            "installed_slices_digest": DIGEST_A,
            "peer_timestamp_epoch": timestamp,
            "protocol_version": "ilc-d2d-gossip.v1",
            "transport_endpoint": {
                "host": "peer-a.example.com",
                "port": 443,
                "scheme": "https",
            },
            "ttl_epochs": ttl,
        },
        "key_binding_ref": "key-binding-a",
        "ml_dsa_signature": SIG_HEX,
        "schema_version": "peer_advertisement_cdl103.v0.1",
    }


def _ad(*, timestamp: int = 10, ttl: int = 4) -> PeerAdvertisement:
    return PeerAdvertisement.from_dict(_ad_dict(timestamp=timestamp, ttl=ttl))


def test_cdl_103_ratification_doc_exists() -> None:
    text = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "**Status:** RATIFIED" in text
    assert "GO Phase 1583 GAP-DISCOV-03 CDL-103-RATIFY" in text


def test_peer_discovery_enabled_default_false_in_sidecars() -> None:
    assert "peer_discovery_enabled: bool = False" in PUBLIC_PREFLIGHT.read_text(encoding="utf-8")
    assert "peer_discovery_enabled: bool = False" in TRANSPORT_ADMISSION.read_text(encoding="utf-8")
    assert '"public_peer_discovery_enabled": False' in GOSSIP_POLICY.read_text(encoding="utf-8")


def test_peer_advertisement_runtime_exists_and_testnet_guard_cleared() -> None:
    status = STATUS.read_text(encoding="utf-8")
    doc = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "peer_advertisement_module_committed_gap_discov_02" in status
    assert "peer_discovery_manager_committed_gap_discov_02" in status
    assert "peer_advertisement_runtime_committed_phase_1579" not in status
    assert "stale input-token spelling" in doc
    assert registry_module.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
    assert manager_module.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
    assert registry_module.PEER_DISCOVERY_MODE == "static_plus_dynamic_testnet_v1"


def test_peer_discovery_spec_doc_exists() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "PeerAdvertisement" in text
    assert "DHT" in text
    assert "not provide a formal eclipse-resistance guarantee" in text


def test_anti_eclipse_documented_not_solved() -> None:
    text = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "mitigation bounds only, not a solved" in text
    assert "cdl_103_signed_peer_table_roots_deferred_phase_1583" in text
    assert "cdl_103_multi_seed_comparison_deferred_phase_1583" in text


def test_cdl_103_ratified_token_in_status_and_register() -> None:
    status = STATUS.read_text(encoding="utf-8")
    register = REGISTER.read_text(encoding="utf-8")
    assert "cdl_103_ratified_phase_1583" in status
    assert "dynamic_peer_discovery_testnet_activated_phase_1583" in status
    assert "| CDL-103 |" in register
    assert "ratified_phase: GAP-DISCOV-03 / 1583" in register


def test_testnet_dynamic_discovery_accepts_valid_advertisement(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        "2" * 96,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )

    assert manager.handle_incoming_advertisement(_ad(timestamp=10), 10) is True
    assert registry.get_dynamic_peers(10)[0].agent_id == AGENT_A


def test_ratified_ttl_and_future_skew_bounds_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="peer_advertisement_ttl_epochs_invalid"):
        _ad(ttl=MAX_TTL_EPOCHS + 1)

    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        "2" * 96,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )
    with pytest.raises(ValueError, match="peer_advertisement_timestamp_future_skew"):
        manager.handle_incoming_advertisement(_ad(timestamp=12), 10)
