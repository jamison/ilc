from __future__ import annotations

import hashlib

import pytest

from ilc_core.bundle.epoch_state_root import (
    DAG_CBOR_SHA2_256_CIDV1_PREFIX_HEX,
    layer2_v2_to_state_root_cidv1_hex,
    state_root_cidv1_bytes_from_layer2_v2,
    validate_state_root_cidv1_hex,
)
from ilc_core.bundle.layer2_epoch_snapshot import (
    MAX_EPOCH_PUBLIC_DELTAS,
    MAX_VALIDATOR_SET_MEMBERS,
    PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1,
    build_public_consensus_graph_snapshot_manifest,
    build_validator_set_manifest,
    generate_layer2_epoch_snapshot_v2,
    graph_state_digest_from_manifest,
    validator_set_root_from_manifest,
    verify_layer2_epoch_snapshot_v2,
)
from ilc_core.encoding.cidv1 import cidv1_from_str, node_id_from_obj, parse_nodeid_strict


SHA256_A = "a" * 64
SHA256_B = "b" * 64
SHA256_C = "c" * 64
SHA384_1 = "1" * 96
SHA384_2 = "2" * 96
SHA384_3 = "3" * 96


def _validator_manifest() -> dict[str, object]:
    return build_validator_set_manifest(
        quorum_threshold=2,
        validators=[
            {
                "validator_id": 2,
                "validator_agent_cidv1": node_id_from_obj({"validator": 2}),
                "bls_public_key_sha256": SHA256_B,
            },
            {
                "validator_id": 1,
                "validator_agent_cidv1": node_id_from_obj({"validator": 1}),
                "bls_public_key_sha256": SHA256_A,
            },
        ],
    )


def _graph_manifest() -> dict[str, object]:
    return build_public_consensus_graph_snapshot_manifest(
        epoch_number=1,
        slice_0_sha384=SHA384_1,
        slice_1_sha384=SHA384_2,
        epoch_public_deltas=[SHA384_3],
    )


def _snapshot():
    return generate_layer2_epoch_snapshot_v2(
        epoch_number=1,
        previous_snapshot_sha256="",
        layer0_sha256=SHA256_A,
        graph_state_digest=graph_state_digest_from_manifest(_graph_manifest()),
        agent_state_digest="sha256:" + SHA256_B,
        active_contract_digest="sha256:" + SHA256_C,
        economic_settlement_root_sha256=SHA256_B,
        previous_epoch_state_root_cidv1_hex="",
        validator_set_root_sha256=validator_set_root_from_manifest(_validator_manifest()),
    )


def test_layer2_v2_snapshot_is_deterministic_and_verifiable() -> None:
    first = _snapshot()
    second = _snapshot()

    assert first.dag_cbor == second.dag_cbor
    assert first.cidv1 == second.cidv1
    assert first.graph_state_scope == PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1
    assert verify_layer2_epoch_snapshot_v2(first) is True


def test_graph_manifest_digest_is_outer_sha256_ref_over_canonical_manifest() -> None:
    manifest = _graph_manifest()
    digest = graph_state_digest_from_manifest(manifest)

    assert digest.startswith("sha256:")
    assert len(digest.removeprefix("sha256:")) == 64
    assert manifest["scope"] == PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1
    assert manifest["epoch_public_delta_count"] == 1


def test_validator_manifest_is_sorted_and_rooted_by_sha256() -> None:
    manifest = _validator_manifest()
    root = validator_set_root_from_manifest(manifest)

    assert [record["validator_id"] for record in manifest["validators"]] == [1, 2]  # type: ignore[index]
    assert len(root) == 64
    assert root == hashlib.sha256(
        b'{"quorum_threshold":2,"schema":"validator_set_manifest_v1","validator_count":2,'
        + (
            b'"validators":[{"bls_public_key_sha256":"'
            + SHA256_A.encode("ascii")
            + b'","validator_agent_cidv1":"'
            + node_id_from_obj({"validator": 1}).encode("ascii")
            + b'","validator_id":1},{"bls_public_key_sha256":"'
            + SHA256_B.encode("ascii")
            + b'","validator_agent_cidv1":"'
            + node_id_from_obj({"validator": 2}).encode("ascii")
            + b'","validator_id":2}]}'
        )
    ).hexdigest()


def test_graph_digest_rejects_wrong_scope_manifest() -> None:
    manifest = _graph_manifest()
    manifest["scope"] = "full_local_lmdb"

    with pytest.raises(ValueError, match="graph_manifest_scope_invalid"):
        graph_state_digest_from_manifest(manifest)


def test_graph_manifest_rejects_epoch_public_delta_count_above_cap() -> None:
    with pytest.raises(ValueError, match="epoch_public_deltas_exceeds_cap"):
        build_public_consensus_graph_snapshot_manifest(
            epoch_number=1,
            slice_0_sha384=SHA384_1,
            slice_1_sha384=SHA384_2,
            epoch_public_deltas=[SHA384_3] * (MAX_EPOCH_PUBLIC_DELTAS + 1),
        )


def test_graph_digest_rejects_manifest_delta_count_above_cap() -> None:
    manifest = _graph_manifest()
    manifest["epoch_public_delta_count"] = MAX_EPOCH_PUBLIC_DELTAS + 1
    manifest["epoch_public_deltas"] = [SHA384_3] * (MAX_EPOCH_PUBLIC_DELTAS + 1)

    with pytest.raises(ValueError, match="epoch_public_deltas_exceeds_cap"):
        graph_state_digest_from_manifest(manifest)


def test_validator_root_rejects_noncanonical_manifest_order() -> None:
    manifest = _validator_manifest()
    manifest["validators"] = list(reversed(manifest["validators"]))  # type: ignore[index]

    with pytest.raises(ValueError, match="validator_manifest_not_canonical"):
        validator_set_root_from_manifest(manifest)


def test_validator_manifest_rejects_validator_count_above_cap() -> None:
    validators = [
        {
            "validator_id": validator_id,
            "validator_agent_cidv1": node_id_from_obj({"validator": validator_id}),
            "bls_public_key_sha256": SHA256_A,
        }
        for validator_id in range(1, MAX_VALIDATOR_SET_MEMBERS + 2)
    ]

    with pytest.raises(ValueError, match="validator_set_exceeds_cap"):
        build_validator_set_manifest(validators=validators, quorum_threshold=1)


def test_layer2_v2_to_state_root_cidv1_hex_returns_raw_36_byte_hex() -> None:
    snapshot = _snapshot()
    root_hex = layer2_v2_to_state_root_cidv1_hex(snapshot)
    raw = bytes.fromhex(root_hex)

    assert len(root_hex) == 72
    assert root_hex.startswith(DAG_CBOR_SHA2_256_CIDV1_PREFIX_HEX)
    assert len(raw) == 36
    assert cidv1_from_str(snapshot.cidv1) == raw
    assert parse_nodeid_strict(snapshot.cidv1)["codec"] == 0x71


def test_state_root_validation_rejects_wrong_lengths_and_zero_root() -> None:
    with pytest.raises(ValueError, match="epoch_state_root_cidv1_hex_all_zero"):
        validate_state_root_cidv1_hex("0" * 72)
    for value in ("a" * 64, "a" * 71, "a" * 73):
        with pytest.raises(ValueError, match="epoch_state_root_cidv1_hex_invalid"):
            validate_state_root_cidv1_hex(value)


def test_state_root_validation_rejects_non_dag_cbor_codec_prefix() -> None:
    with pytest.raises(ValueError, match="epoch_state_root_cidv1_hex_not_dag_cbor"):
        validate_state_root_cidv1_hex("01551220" + "a" * 64)


def test_epoch_two_requires_previous_state_root_cidv1_hex() -> None:
    with pytest.raises(ValueError, match="missing_previous_state_root"):
        generate_layer2_epoch_snapshot_v2(
            epoch_number=2,
            previous_snapshot_sha256=SHA256_A,
            layer0_sha256=SHA256_A,
            graph_state_digest=graph_state_digest_from_manifest(_graph_manifest()),
            agent_state_digest="sha256:" + SHA256_B,
            active_contract_digest="sha256:" + SHA256_C,
            economic_settlement_root_sha256=SHA256_B,
            previous_epoch_state_root_cidv1_hex="",
            validator_set_root_sha256=validator_set_root_from_manifest(_validator_manifest()),
        )


def test_state_root_bytes_rejects_v1_snapshot() -> None:
    with pytest.raises(ValueError, match="layer2_epoch_snapshot_v2_required"):
        state_root_cidv1_bytes_from_layer2_v2(object())  # type: ignore[arg-type]
