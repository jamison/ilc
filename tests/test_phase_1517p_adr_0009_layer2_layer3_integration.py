"""Phase 1517p ADR-0009 Layer 2/3 encoding and CID-chain tests.

PUBLIC_RC_EXCLUDE: phase_1517p_private_runtime_selftest
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 integration test. Not a public RC artifact.
"""

from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
from ilc_core.bundle.layer1_genesis_bundle import generate_layer1_genesis_bundle
from ilc_core.bundle.layer2_epoch_snapshot import (
    ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION,
    generate_layer2_epoch_snapshot,
    verify_layer2_epoch_snapshot,
)
from ilc_core.bundle.layer3_wire_binding import (
    ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION,
    generate_layer3_wire_binding,
    verify_layer3_wire_binding,
)
from ilc_core.crypto.cose_sign1 import cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import validate_canonical_ilc_dag_cbor


def _private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _layer0_fixture():
    return generate_layer0_protocol_bundle(
        bundle_id="layer0-private",
        version="v0.1-private",
        schemas=[
            {"type_name": "Node", "required": ["node_id", "type"]},
            {"type_name": "WireMessage", "required": ["message_type", "payload_digest"]},
        ],
        parameters={"truth_primitives": 7},
    )


def _layer1_fixture(layer0):
    return generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-001"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"shards": [{"shard_id": "genesis"}]},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a"}],
    )


def _layer2_fixture(layer0, layer1):
    return generate_layer2_epoch_snapshot(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        layer1_cidv1=layer1.cidv1,
        graph_state_digest="graph:" + layer1.sha256,
        agent_state_digest="agent:" + "2" * 64,
        active_contract_digest="contract:" + "3" * 64,
    )


def _layer3_fixture(layer2):
    return generate_layer3_wire_binding(
        message_type="claim.submit",
        layer0_schema_ref="layer0:schema:WireMessage",
        sender_agent_id="agent-a",
        epoch_number=1,
        payload_digest="payload:" + layer2.sha256,
        layer2_cidv1=layer2.cidv1,
        signature_ref="signature:fixture-a",
    )


def _chain_is_consistent(layer0, layer1, layer2, layer3) -> bool:
    return (
        layer1.layer0_protocol_bundle_cidv1 == layer0.cidv1
        and layer2.layer0_protocol_bundle_cidv1 == layer0.cidv1
        and layer2.layer1_genesis_bundle_cidv1 == layer1.cidv1
        and layer3.layer2_epoch_snapshot_cidv1 == layer2.cidv1
        and layer1.cidv1 == node_id_from_bytes(layer1.dag_cbor)
        and layer2.cidv1 == node_id_from_bytes(layer2.dag_cbor)
        and layer3.cidv1 == node_id_from_bytes(layer3.dag_cbor)
    )


def test_layer2_generates_deterministic_cidv1_and_links_layer1() -> None:
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    layer2_a = _layer2_fixture(layer0, layer1)
    layer2_b = _layer2_fixture(layer0, layer1)

    assert ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION is False
    assert layer2_a.layer0_protocol_bundle_cidv1 == layer0.cidv1
    assert layer2_a.layer1_genesis_bundle_cidv1 == layer1.cidv1
    assert layer2_a.dag_cbor == layer2_b.dag_cbor
    assert layer2_a.cidv1 == layer2_b.cidv1
    assert layer2_a.cidv1 == node_id_from_bytes(layer2_a.dag_cbor)
    assert layer2_a.sha256 == hashlib.sha256(layer2_a.dag_cbor).hexdigest()
    assert parse_nodeid_strict(layer2_a.cidv1)["codec"] == 0x71
    validate_canonical_ilc_dag_cbor(layer2_a.dag_cbor)
    assert verify_layer2_epoch_snapshot(layer2_a) is True


def test_layer3_generates_deterministic_cidv1_and_links_layer2() -> None:
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    layer2 = _layer2_fixture(layer0, layer1)
    layer3_a = _layer3_fixture(layer2)
    layer3_b = _layer3_fixture(layer2)

    assert ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION is False
    assert layer3_a.layer2_epoch_snapshot_cidv1 == layer2.cidv1
    assert layer3_a.dag_cbor == layer3_b.dag_cbor
    assert layer3_a.cidv1 == layer3_b.cidv1
    assert layer3_a.cidv1 == node_id_from_bytes(layer3_a.dag_cbor)
    assert layer3_a.sha256 == hashlib.sha256(layer3_a.dag_cbor).hexdigest()
    validate_canonical_ilc_dag_cbor(layer3_a.dag_cbor)
    assert verify_layer3_wire_binding(layer3_a) is True


def test_four_layer_cid_chain_and_tamper_detection() -> None:
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    layer2 = _layer2_fixture(layer0, layer1)
    layer3 = _layer3_fixture(layer2)

    assert _chain_is_consistent(layer0, layer1, layer2, layer3) is True

    tampered_layer1 = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-002"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"shards": [{"shard_id": "genesis"}]},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a"}],
    )
    tampered_layer2 = generate_layer2_epoch_snapshot(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        layer1_cidv1=layer1.cidv1,
        graph_state_digest="graph:" + layer1.sha256,
        agent_state_digest="agent:" + "9" * 64,
        active_contract_digest="contract:" + "3" * 64,
    )

    assert _chain_is_consistent(layer0, tampered_layer1, layer2, layer3) is False
    assert _chain_is_consistent(layer0, layer1, tampered_layer2, layer3) is False


def test_layer2_and_layer3_cose_round_trip() -> None:
    private_key = _private_key()
    public_key = private_key.public_key()
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    layer2 = generate_layer2_epoch_snapshot(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        layer1_cidv1=layer1.cidv1,
        graph_state_digest="graph:" + layer1.sha256,
        agent_state_digest="agent:" + "2" * 64,
        active_contract_digest="contract:" + "3" * 64,
        signing_private_key=private_key,
        cose_kid=b"phase1517-layer2",
    )
    layer3 = generate_layer3_wire_binding(
        message_type="claim.submit",
        layer0_schema_ref="layer0:schema:WireMessage",
        sender_agent_id="agent-a",
        epoch_number=1,
        payload_digest="payload:" + layer2.sha256,
        layer2_cidv1=layer2.cidv1,
        signature_ref="signature:fixture-a",
        signing_private_key=private_key,
        cose_kid=b"phase1517-layer3",
    )

    layer2_verified = cose_sign1_verify(layer2.cose_sign1, public_key)
    layer3_verified = cose_sign1_verify(layer3.cose_sign1, public_key)
    assert layer2_verified["payload"] == layer2.dag_cbor
    assert layer2_verified["nodeid"] == layer2.cidv1
    assert layer3_verified["payload"] == layer3.dag_cbor
    assert layer3_verified["nodeid"] == layer3.cidv1
    assert verify_layer2_epoch_snapshot(layer2, public_key=public_key) is True
    assert verify_layer3_wire_binding(layer3, public_key=public_key) is True
