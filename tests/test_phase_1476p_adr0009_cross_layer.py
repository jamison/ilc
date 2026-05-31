from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
from ilc_core.bundle.layer1_genesis_bundle import generate_layer1_genesis_bundle
from ilc_core.bundle.layer2_epoch_snapshot import generate_layer2_epoch_snapshot
from ilc_core.bundle.layer3_wire_binding import generate_layer3_wire_binding


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


def test_cross_layer_layer1_references_layer0_sha256() -> None:
    layer0 = _layer0_fixture()
    layer1 = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        seed_claims=[{"claim_id": "seed-001"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"shards": [{"shard_id": "genesis"}]},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a"}],
    )

    assert layer1.layer0_protocol_bundle_sha256 == layer0.sha256


def test_cross_layer_layer2_references_layer0_sha256() -> None:
    layer0 = _layer0_fixture()
    layer2 = generate_layer2_epoch_snapshot(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=layer0.sha256,
        graph_state_digest="graph:" + "1" * 64,
        agent_state_digest="agent:" + "2" * 64,
        active_contract_digest="contract:" + "3" * 64,
    )

    assert layer2.layer0_protocol_bundle_sha256 == layer0.sha256


def test_cross_layer_layer3_references_layer0_schema_ref() -> None:
    layer0_schema_ref = "layer0:schema:WireMessage"
    layer3 = generate_layer3_wire_binding(
        message_type="claim.submit",
        layer0_schema_ref=layer0_schema_ref,
        sender_agent_id="agent-a",
        epoch_number=1,
        payload_digest="payload:" + "4" * 64,
        signature_ref="signature:fixture-a",
    )

    assert layer3.layer0_schema_ref == layer0_schema_ref


def test_cross_layer_chain_integrity() -> None:
    layer0 = _layer0_fixture()
    layer1 = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256=layer0.sha256,
        seed_claims=[{"claim_id": "seed-001"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"shards": [{"shard_id": "genesis"}]},
        genesis_signing_key_refs=[{"key_ref": "genesis-key-a"}],
    )
    layer2 = generate_layer2_epoch_snapshot(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=layer0.sha256,
        graph_state_digest="graph:" + layer1.sha256,
        agent_state_digest="agent:" + "2" * 64,
        active_contract_digest="contract:" + "3" * 64,
    )
    layer3 = generate_layer3_wire_binding(
        message_type="claim.submit",
        layer0_schema_ref="layer0:schema:WireMessage",
        sender_agent_id="agent-a",
        epoch_number=1,
        payload_digest="payload:" + layer2.sha256,
        signature_ref="signature:fixture-a",
    )

    assert layer1.layer0_protocol_bundle_sha256 == layer0.sha256
    assert layer2.layer0_protocol_bundle_sha256 == layer0.sha256
    assert layer3.layer0_schema_ref == "layer0:schema:WireMessage"
    assert layer0.sha256
    assert layer1.sha256
    assert layer2.sha256
    assert layer3.sha256
