"""Phase 1560 Agent INIT live-ceremony evidence tests.

PUBLIC_RC_EXCLUDE: phase_1560_private_live_ceremony_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC live-ceremony evidence validation. Does not perform live network calls or activate public P2P.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CEREMONY = ROOT / "out/agent_init_ceremony_1560.json"
RECEIPTS = ROOT / "out/serving_receipts"

EXPECTED_HOSTS = {
    "ilc-node-2": {
        "ip": "100.112.32.42",
        "agent_ids": {
            "d6592166bf9c15841e8c249007f261760b9808b5a85f3c0ebb8b7cd3527155cca279870dca142eb3bc9f42eb2f20b36c",
            "bfc75431f3941080d4723063b17c6c7086f5b010952b5273839d250b30d70ab0f1799c0831a4ba6b1ad7ea8f09793c74",
        },
        "receipt": "genesis_to_vps_node2_1560.json",
    },
    "ilc-node-3": {
        "ip": "100.91.33.46",
        "agent_ids": {
            "4842b1bee669793b03e7cfbb01f3b5ae7e54a34a093bd7c88f95539d67ce973c084029e00abc79e4410398f6f712dec1",
            "dc6f1d4775c9c0a6c40ec57dd81c1fc0741d924013060ad0c9323099f12196ddabe007e0f4ba3fd89aed0e397c622ad7",
        },
        "receipt": "genesis_to_vps_node3_1560.json",
    },
    "ilc-node-6": {
        "ip": "100.72.17.38",
        "agent_ids": set(),
        "receipt": "genesis_to_vps_node6_1560.json",
    },
}


def _ceremony() -> list[dict[str, object]]:
    payload = json.loads(CEREMONY.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return payload


def test_phase_1560_ceremony_evidence_shape_and_hosts() -> None:
    rows = _ceremony()

    assert len(rows) == 3
    assert {row["host_label"] for row in rows} == set(EXPECTED_HOSTS)
    for row in rows:
        host = str(row["host_label"])
        expected = EXPECTED_HOSTS[host]
        assert row["tailscale_ip"] == expected["ip"]
        assert row["epoch"] == "0"
        assert row["custody_mode"] == "genesis_operator_held"
        assert row["serving_verified"] is True
        assert row["public_p2p_not_activated_phase_1560"] is True
        assert row["production_economics_not_activated_phase_1560"] is True
        assert row["public_path_remains_blocked_phase_1560"] is True
        assert row["genesis_operator_held_custody_used_phase_1560"] is True


def test_phase_1560_agent_assignments_and_node6_receiver_boundary() -> None:
    rows = {str(row["host_label"]): row for row in _ceremony()}

    for host in ("ilc-node-2", "ilc-node-3"):
        agents = rows[host]["agents"]
        assert isinstance(agents, list)
        assert {agent["agent_id"] for agent in agents} == EXPECTED_HOSTS[host]["agent_ids"]
        for agent in agents:
            assert agent["custody_mode"] == "genesis_operator_held"
            assert agent["epoch"] == "0"
            assert isinstance(agent["init_artifact_hash"], str)
            assert len(agent["init_artifact_hash"]) == 64
            assert isinstance(agent["attestation_receipt_hash"], str)
            assert len(agent["attestation_receipt_hash"]) == 64

    node6 = rows["ilc-node-6"]
    assert node6["receiver_only"] is True
    assert node6["node6_receiver_only_not_init_participant_phase_1560"] is True
    assert node6["agents"] == []


def test_phase_1560_serving_receipts_exist_and_match_layer0_cid() -> None:
    rows = _ceremony()
    layer0_cids = {row["bundle_layer0_cidv1"] for row in rows}
    assert len(layer0_cids) == 1
    expected_cid = next(iter(layer0_cids))

    for host, expected in EXPECTED_HOSTS.items():
        receipt_path = RECEIPTS / str(expected["receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["serving_receipt_id"].startswith("serving_receipt:")
        assert receipt["layer0_protocol_bundle_cidv1"] == expected_cid
        assert receipt["serving_epoch"] == 0
        assert receipt["served_peer_url"] == f"https://{expected['ip']}:8443"
        assert host in {row["host_label"] for row in rows}


def test_phase_1560_evidence_omits_private_material_terms() -> None:
    text = CEREMONY.read_text(encoding="utf-8").lower()
    for forbidden in ("private_key", "identity_seed", "mnemonic", "recovery"):
        assert forbidden not in text
