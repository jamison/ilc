"""Phase 1516p ADR-0009 Layer 0/1 encoding integration tests.

PUBLIC_RC_EXCLUDE: phase_1516p_private_runtime_selftest
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 integration test. Not a public RC artifact.
"""

from __future__ import annotations

import hashlib

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.layer0_protocol_bundle import (
    ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION,
    generate_layer0_protocol_bundle,
    verify_layer0_protocol_bundle,
)
from ilc_core.bundle.layer1_genesis_bundle import (
    ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION,
    generate_layer1_genesis_bundle,
    verify_layer1_genesis_bundle,
)
from ilc_core.crypto.cose_sign1 import cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import validate_canonical_ilc_dag_cbor


def _private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def test_layer0_generates_deterministic_cidv1_from_dag_cbor() -> None:
    bundle_a = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[
            {"type_name": "Node", "required": ["node_id", "type"]},
            {"type_name": "Edge", "required": ["source", "target"]},
        ],
        parameters={"truth_primitives": 7},
    )
    bundle_b = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[
            {"type_name": "Edge", "required": ["source", "target"]},
            {"type_name": "Node", "required": ["node_id", "type"]},
        ],
        parameters={"truth_primitives": 7},
    )

    assert ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION is False
    assert bundle_a.dag_cbor == bundle_b.dag_cbor
    assert bundle_a.cidv1 == bundle_b.cidv1
    assert bundle_a.cidv1 == node_id_from_bytes(bundle_a.dag_cbor)
    assert bundle_a.sha256 == hashlib.sha256(bundle_a.dag_cbor).hexdigest()
    assert parse_nodeid_strict(bundle_a.cidv1)["codec"] == 0x71
    validate_canonical_ilc_dag_cbor(bundle_a.dag_cbor)
    assert verify_layer0_protocol_bundle(bundle_a) is True


def test_layer1_generates_deterministic_cidv1_and_links_layer0_cid() -> None:
    layer0 = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
    )
    layer1_a = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"truth_primitive": "assert.truth", "claim_id": "seed-001"}],
        initial_agent_roster=[{"identity_anchor": "anchor-a", "agent_id": "agent-a"}],
        initial_shard_topology={"version": "v0.1-private", "shards": []},
        genesis_signing_key_refs=[{"purpose": "private_fixture", "key_ref": "genesis-key-a"}],
    )
    layer1_b = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-001", "truth_primitive": "assert.truth"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"shards": [], "version": "v0.1-private"},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a", "purpose": "private_fixture"}],
    )

    assert ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION is False
    assert layer1_a.layer0_protocol_bundle_sha256 == layer0.sha256
    assert layer1_a.layer0_protocol_bundle_cidv1 == layer0.cidv1
    assert layer1_a.dag_cbor == layer1_b.dag_cbor
    assert layer1_a.cidv1 == layer1_b.cidv1
    assert layer1_a.cidv1 == node_id_from_bytes(layer1_a.dag_cbor)
    assert layer1_a.sha256 == hashlib.sha256(layer1_a.dag_cbor).hexdigest()
    validate_canonical_ilc_dag_cbor(layer1_a.dag_cbor)
    assert verify_layer1_genesis_bundle(layer1_a) is True


def test_layer0_cose_sign1_round_trip_verifies_payload_cid() -> None:
    private_key = _private_key()
    public_key = private_key.public_key()
    bundle = generate_layer0_protocol_bundle(
        bundle_id="layer0-signed",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
        signing_private_key=private_key,
        cose_kid=b"phase1516-layer0",
    )

    verified = cose_sign1_verify(bundle.cose_sign1, public_key)
    assert verified["payload"] == bundle.dag_cbor
    assert verified["nodeid"] == bundle.cidv1
    assert verify_layer0_protocol_bundle(bundle, public_key=public_key) is True
    assert verify_layer0_protocol_bundle(bundle) is False


def test_layer1_cose_sign1_round_trip_verifies_payload_cid() -> None:
    private_key = _private_key()
    public_key = private_key.public_key()
    layer0 = generate_layer0_protocol_bundle(
        bundle_id="layer0-fixture",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
    )
    bundle = generate_layer1_genesis_bundle(
        bundle_id="layer1-signed",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-001"}],
        initial_agent_roster=[{"agent_id": "agent-a"}],
        initial_shard_topology={"shards": [{"shard_id": "genesis"}]},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a"}],
        signing_private_key=private_key,
        cose_kid=b"phase1516-layer1",
    )

    verified = cose_sign1_verify(bundle.cose_sign1, public_key)
    assert verified["payload"] == bundle.dag_cbor
    assert verified["nodeid"] == bundle.cidv1
    assert verify_layer1_genesis_bundle(bundle, public_key=public_key) is True
    assert verify_layer1_genesis_bundle(bundle) is False
