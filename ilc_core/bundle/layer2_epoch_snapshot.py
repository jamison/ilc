# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.private_json_guardrails import canonical_json, reject_float, require_digest_ref, require_sha256_hex

ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION = False  # guard cleared Phase 1520p - ADR-0009 accepted
PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1 = "public_consensus_slices_0_1_plus_epoch_public_deltas_v1"
PUBLIC_CONSENSUS_GRAPH_SNAPSHOT_SCHEMA_V1 = "public_consensus_graph_snapshot_v1"
VALIDATOR_SET_MANIFEST_SCHEMA_V1 = "validator_set_manifest_v1"
MAX_EPOCH_PUBLIC_DELTAS = 4096
MAX_VALIDATOR_SET_MEMBERS = 1024


def _reject_float(value: object, token: str) -> None:
    reject_float(value, token)


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer2_epoch_snapshot_float_not_allowed")


def _require_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)


def _require_sha256(value: str, missing_token: str, invalid_token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(missing_token)
    require_sha256_hex(value, invalid_token)


def _require_sha384(value: object, token: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 96
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(token)
    return value


def _require_digest(value: str, missing_token: str, invalid_token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(missing_token)
    require_digest_ref(value, invalid_token)


def _require_epoch_number(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("layer2_epoch_snapshot_invalid_epoch_number")


def _require_cidv1_if_provided(value: str, token: str) -> None:
    if value == "":
        return
    try:
        parse_nodeid_strict(value)
    except (ValueError, Exception):
        raise ValueError(token)


def _require_cidv1(value: object, token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)
    try:
        parse_nodeid_strict(value)
    except (ValueError, Exception):
        raise ValueError(token)
    return value


def _require_positive_int(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(token)
    return value


def _require_state_root_cidv1_hex_for_epoch(
    *,
    epoch_number: int,
    previous_epoch_state_root_cidv1_hex: str,
) -> None:
    if not isinstance(previous_epoch_state_root_cidv1_hex, str):
        raise ValueError("layer2_epoch_snapshot_v2_invalid_previous_state_root_cidv1_hex")
    if epoch_number == 1 and previous_epoch_state_root_cidv1_hex == "":
        return
    if previous_epoch_state_root_cidv1_hex == "":
        raise ValueError("layer2_epoch_snapshot_v2_missing_previous_state_root_cidv1_hex")
    if (
        len(previous_epoch_state_root_cidv1_hex) != 72
        or any(char not in "0123456789abcdef" for char in previous_epoch_state_root_cidv1_hex)
    ):
        raise ValueError("layer2_epoch_snapshot_v2_invalid_previous_state_root_cidv1_hex")


@dataclass(frozen=True)
class Layer2EpochSnapshot:
    epoch_number: int
    previous_snapshot_sha256: str
    layer0_protocol_bundle_sha256: str
    layer0_protocol_bundle_cidv1: str
    layer1_genesis_bundle_cidv1: str
    graph_state_digest: str
    agent_state_digest: str
    active_contract_digest: str
    canonical_json: str
    dag_cbor: bytes
    cidv1: str
    sha256: str
    cose_sign1: bytes = b""
    public_rc_exclude: bool = True


@dataclass(frozen=True)
class Layer2EpochSnapshotV2:
    epoch_number: int
    previous_snapshot_sha256: str
    layer0_protocol_bundle_sha256: str
    layer0_protocol_bundle_cidv1: str
    layer1_genesis_bundle_cidv1: str
    graph_state_digest: str
    agent_state_digest: str
    active_contract_digest: str
    economic_settlement_root_sha256: str
    previous_epoch_state_root_cidv1_hex: str
    validator_set_root_sha256: str
    graph_state_scope: str
    canonical_json: str
    dag_cbor: bytes
    cidv1: str
    sha256: str
    cose_sign1: bytes = b""
    public_rc_exclude: bool = True


@dataclass(frozen=True)
class Layer2EpochSnapshotV2Params:
    epoch_number: int
    previous_snapshot_sha256: str
    layer0_sha256: str
    graph_state_digest: str
    agent_state_digest: str
    active_contract_digest: str
    economic_settlement_root_sha256: str
    previous_epoch_state_root_cidv1_hex: str
    validator_set_root_sha256: str
    graph_state_scope: str = PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1
    layer0_cidv1: str = ""
    layer1_cidv1: str = ""


def _build_layer2_envelope(
    *,
    epoch_number: int,
    previous_snapshot_sha256: str,
    layer0_sha256: str,
    layer0_cidv1: str,
    layer1_cidv1: str,
    graph_state_digest: str,
    agent_state_digest: str,
    active_contract_digest: str,
) -> dict[str, object]:
    return {
        "active_contract_digest": active_contract_digest,
        "agent_state_digest": agent_state_digest,
        "epoch_number": epoch_number,
        "graph_state_digest": graph_state_digest,
        "layer": 2,
        "layer0_protocol_bundle_cidv1": layer0_cidv1,
        "layer0_protocol_bundle_sha256": layer0_sha256,
        "layer1_genesis_bundle_cidv1": layer1_cidv1,
        "previous_snapshot_sha256": previous_snapshot_sha256,
        "public_rc_exclude": True,
    }


def _build_layer2_v2_envelope(params: Layer2EpochSnapshotV2Params) -> dict[str, object]:
    envelope = _build_layer2_envelope(
        epoch_number=params.epoch_number,
        previous_snapshot_sha256=params.previous_snapshot_sha256,
        layer0_sha256=params.layer0_sha256,
        layer0_cidv1=params.layer0_cidv1,
        layer1_cidv1=params.layer1_cidv1,
        graph_state_digest=params.graph_state_digest,
        agent_state_digest=params.agent_state_digest,
        active_contract_digest=params.active_contract_digest,
    )
    envelope.update(
        {
            "economic_settlement_root_sha256": params.economic_settlement_root_sha256,
            "graph_state_scope": params.graph_state_scope,
            "previous_epoch_state_root_cidv1_hex": params.previous_epoch_state_root_cidv1_hex,
            "validator_set_root_sha256": params.validator_set_root_sha256,
        }
    )
    return envelope


def build_public_consensus_graph_snapshot_manifest(
    *,
    epoch_number: int,
    slice_0_sha384: str,
    slice_1_sha384: str,
    epoch_public_deltas: Sequence[str] = (),
) -> dict[str, object]:
    _require_epoch_number(epoch_number)
    if not isinstance(epoch_public_deltas, Sequence) or isinstance(
        epoch_public_deltas,
        (str, bytes, bytearray),
    ):
        raise ValueError("layer2_epoch_snapshot_v2_epoch_public_deltas_must_be_sequence")
    if len(epoch_public_deltas) > MAX_EPOCH_PUBLIC_DELTAS:
        raise ValueError("layer2_epoch_snapshot_v2_epoch_public_deltas_exceeds_cap")
    normalized_deltas = tuple(
        sorted(
            _require_sha384(
                digest,
                "layer2_epoch_snapshot_v2_invalid_epoch_public_delta_sha384",
            )
            for digest in epoch_public_deltas
        )
    )
    return {
        "epoch": epoch_number,
        "epoch_public_delta_count": len(normalized_deltas),
        "epoch_public_deltas": list(normalized_deltas),
        "schema": PUBLIC_CONSENSUS_GRAPH_SNAPSHOT_SCHEMA_V1,
        "scope": PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1,
        "slice_0_sha384": _require_sha384(
            slice_0_sha384,
            "layer2_epoch_snapshot_v2_invalid_slice_0_sha384",
        ),
        "slice_1_sha384": _require_sha384(
            slice_1_sha384,
            "layer2_epoch_snapshot_v2_invalid_slice_1_sha384",
        ),
    }


def graph_state_digest_from_manifest(manifest: Mapping[str, object]) -> str:
    if manifest.get("schema") != PUBLIC_CONSENSUS_GRAPH_SNAPSHOT_SCHEMA_V1:
        raise ValueError("layer2_epoch_snapshot_v2_graph_manifest_schema_invalid")
    if manifest.get("scope") != PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1:
        raise ValueError("layer2_epoch_snapshot_v2_graph_manifest_scope_invalid")
    _require_epoch_number(manifest.get("epoch"))  # type: ignore[arg-type]
    _require_sha384(
        manifest.get("slice_0_sha384"),
        "layer2_epoch_snapshot_v2_invalid_slice_0_sha384",
    )
    _require_sha384(
        manifest.get("slice_1_sha384"),
        "layer2_epoch_snapshot_v2_invalid_slice_1_sha384",
    )
    deltas = manifest.get("epoch_public_deltas")
    if not isinstance(deltas, list):
        raise ValueError("layer2_epoch_snapshot_v2_epoch_public_deltas_invalid")
    if len(deltas) > MAX_EPOCH_PUBLIC_DELTAS:
        raise ValueError("layer2_epoch_snapshot_v2_epoch_public_deltas_exceeds_cap")
    for digest in deltas:
        _require_sha384(digest, "layer2_epoch_snapshot_v2_invalid_epoch_public_delta_sha384")
    if manifest.get("epoch_public_delta_count") != len(deltas):
        raise ValueError("layer2_epoch_snapshot_v2_epoch_public_delta_count_invalid")
    canonical = _canonical_json(manifest)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_validator_set_manifest(
    *,
    validators: Sequence[Mapping[str, object]],
    quorum_threshold: int,
) -> dict[str, object]:
    threshold = _require_positive_int(
        quorum_threshold,
        "layer2_epoch_snapshot_v2_invalid_validator_quorum_threshold",
    )
    if not isinstance(validators, Sequence) or isinstance(validators, (str, bytes, bytearray)):
        raise ValueError("layer2_epoch_snapshot_v2_validator_set_must_be_sequence")
    if len(validators) > MAX_VALIDATOR_SET_MEMBERS:
        raise ValueError("layer2_epoch_snapshot_v2_validator_set_exceeds_cap")
    normalized_records = []
    seen_ids: set[int] = set()
    for record in validators:
        if not isinstance(record, Mapping):
            raise ValueError("layer2_epoch_snapshot_v2_validator_record_invalid")
        validator_id = _require_positive_int(
            record.get("validator_id"),
            "layer2_epoch_snapshot_v2_validator_id_invalid",
        )
        if validator_id in seen_ids:
            raise ValueError("layer2_epoch_snapshot_v2_duplicate_validator_id")
        seen_ids.add(validator_id)
        bls_public_key_sha256 = record.get("bls_public_key_sha256")
        if not isinstance(bls_public_key_sha256, str):
            raise ValueError("layer2_epoch_snapshot_v2_validator_key_sha256_invalid")
        require_sha256_hex(
            bls_public_key_sha256,
            "layer2_epoch_snapshot_v2_validator_key_sha256_invalid",
        )
        normalized_records.append(
            {
                "bls_public_key_sha256": bls_public_key_sha256,
                "validator_agent_cidv1": _require_cidv1(
                    record.get("validator_agent_cidv1"),
                    "layer2_epoch_snapshot_v2_validator_agent_cidv1_invalid",
                ),
                "validator_id": validator_id,
            }
        )
    if not normalized_records:
        raise ValueError("layer2_epoch_snapshot_v2_validator_set_empty")
    if threshold > len(normalized_records):
        raise ValueError("layer2_epoch_snapshot_v2_validator_quorum_threshold_exceeds_set")
    normalized_records.sort(key=lambda item: item["validator_id"])
    return {
        "quorum_threshold": threshold,
        "schema": VALIDATOR_SET_MANIFEST_SCHEMA_V1,
        "validator_count": len(normalized_records),
        "validators": normalized_records,
    }


def validator_set_root_from_manifest(manifest: Mapping[str, object]) -> str:
    if manifest.get("schema") != VALIDATOR_SET_MANIFEST_SCHEMA_V1:
        raise ValueError("layer2_epoch_snapshot_v2_validator_manifest_schema_invalid")
    validators = manifest.get("validators")
    if not isinstance(validators, list):
        raise ValueError("layer2_epoch_snapshot_v2_validator_manifest_validators_invalid")
    rebuilt = build_validator_set_manifest(
        validators=validators,  # type: ignore[arg-type]
        quorum_threshold=_require_positive_int(
            manifest.get("quorum_threshold"),
            "layer2_epoch_snapshot_v2_invalid_validator_quorum_threshold",
        ),
    )
    if rebuilt != dict(manifest):
        raise ValueError("layer2_epoch_snapshot_v2_validator_manifest_not_canonical")
    canonical = _canonical_json(manifest)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def generate_layer2_epoch_snapshot(
    *,
    epoch_number: int,
    previous_snapshot_sha256: str,
    layer0_sha256: str,
    graph_state_digest: str,
    agent_state_digest: str,
    active_contract_digest: str,
    layer0_cidv1: str = "",
    layer1_cidv1: str = "",
    signing_private_key: ed25519.Ed25519PrivateKey | None = None,
    cose_kid: bytes | None = None,
) -> Layer2EpochSnapshot:
    _require_epoch_number(epoch_number)
    _require_sha256(
        layer0_sha256,
        "layer2_epoch_snapshot_missing_layer0_sha256",
        "layer2_epoch_snapshot_invalid_layer0_sha256",
    )
    _require_digest(
        graph_state_digest,
        "layer2_epoch_snapshot_missing_graph_state_digest",
        "layer2_epoch_snapshot_invalid_graph_state_digest",
    )
    _require_digest(
        agent_state_digest,
        "layer2_epoch_snapshot_missing_agent_state_digest",
        "layer2_epoch_snapshot_invalid_agent_state_digest",
    )
    _require_digest(
        active_contract_digest,
        "layer2_epoch_snapshot_missing_active_contract_digest",
        "layer2_epoch_snapshot_invalid_active_contract_digest",
    )
    _require_cidv1_if_provided(layer0_cidv1, "layer2_epoch_snapshot_invalid_layer0_cidv1")
    _require_cidv1_if_provided(layer1_cidv1, "layer2_epoch_snapshot_invalid_layer1_cidv1")
    if epoch_number > 1 and previous_snapshot_sha256 == "":
        raise ValueError("layer2_epoch_snapshot_missing_previous_sha256")
    if previous_snapshot_sha256 != "":
        _require_sha256(
            previous_snapshot_sha256,
            "layer2_epoch_snapshot_missing_previous_sha256",
            "layer2_epoch_snapshot_invalid_previous_sha256",
        )

    envelope = _build_layer2_envelope(
        epoch_number=epoch_number,
        previous_snapshot_sha256=previous_snapshot_sha256,
        layer0_sha256=layer0_sha256,
        layer0_cidv1=layer0_cidv1,
        layer1_cidv1=layer1_cidv1,
        graph_state_digest=graph_state_digest,
        agent_state_digest=agent_state_digest,
        active_contract_digest=active_contract_digest,
    )
    canonical_json = _canonical_json(envelope)
    dag_cbor = encode_dag_cbor(envelope)
    cidv1 = node_id_from_bytes(dag_cbor)
    cose_sign1 = (
        cose_sign1_sign(dag_cbor, signing_private_key, kid=cose_kid)
        if signing_private_key is not None
        else b""
    )
    return Layer2EpochSnapshot(
        epoch_number=epoch_number,
        previous_snapshot_sha256=previous_snapshot_sha256,
        layer0_protocol_bundle_sha256=layer0_sha256,
        layer0_protocol_bundle_cidv1=layer0_cidv1,
        layer1_genesis_bundle_cidv1=layer1_cidv1,
        graph_state_digest=graph_state_digest,
        agent_state_digest=agent_state_digest,
        active_contract_digest=active_contract_digest,
        canonical_json=canonical_json,
        dag_cbor=dag_cbor,
        cidv1=cidv1,
        sha256=hashlib.sha256(dag_cbor).hexdigest(),
        cose_sign1=cose_sign1,
    )


def generate_layer2_epoch_snapshot_v2(
    params: Layer2EpochSnapshotV2Params,
    *,
    signing_private_key: ed25519.Ed25519PrivateKey | None = None,
    cose_kid: bytes | None = None,
) -> Layer2EpochSnapshotV2:
    if not isinstance(params, Layer2EpochSnapshotV2Params):
        raise ValueError("layer2_epoch_snapshot_v2_params_required")
    _require_epoch_number(params.epoch_number)
    _require_sha256(
        params.layer0_sha256,
        "layer2_epoch_snapshot_missing_layer0_sha256",
        "layer2_epoch_snapshot_invalid_layer0_sha256",
    )
    _require_digest(
        params.graph_state_digest,
        "layer2_epoch_snapshot_missing_graph_state_digest",
        "layer2_epoch_snapshot_invalid_graph_state_digest",
    )
    _require_digest(
        params.agent_state_digest,
        "layer2_epoch_snapshot_missing_agent_state_digest",
        "layer2_epoch_snapshot_invalid_agent_state_digest",
    )
    _require_digest(
        params.active_contract_digest,
        "layer2_epoch_snapshot_missing_active_contract_digest",
        "layer2_epoch_snapshot_invalid_active_contract_digest",
    )
    _require_sha256(
        params.economic_settlement_root_sha256,
        "layer2_epoch_snapshot_v2_missing_economic_settlement_root_sha256",
        "layer2_epoch_snapshot_v2_invalid_economic_settlement_root_sha256",
    )
    _require_sha256(
        params.validator_set_root_sha256,
        "layer2_epoch_snapshot_v2_missing_validator_set_root_sha256",
        "layer2_epoch_snapshot_v2_invalid_validator_set_root_sha256",
    )
    if params.graph_state_scope != PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1:
        raise ValueError("layer2_epoch_snapshot_v2_invalid_graph_state_scope")
    _require_state_root_cidv1_hex_for_epoch(
        epoch_number=params.epoch_number,
        previous_epoch_state_root_cidv1_hex=params.previous_epoch_state_root_cidv1_hex,
    )
    _require_cidv1_if_provided(params.layer0_cidv1, "layer2_epoch_snapshot_invalid_layer0_cidv1")
    _require_cidv1_if_provided(params.layer1_cidv1, "layer2_epoch_snapshot_invalid_layer1_cidv1")
    if params.epoch_number > 1 and params.previous_snapshot_sha256 == "":
        raise ValueError("layer2_epoch_snapshot_missing_previous_sha256")
    if params.previous_snapshot_sha256 != "":
        _require_sha256(
            params.previous_snapshot_sha256,
            "layer2_epoch_snapshot_missing_previous_sha256",
            "layer2_epoch_snapshot_invalid_previous_sha256",
        )

    envelope = _build_layer2_v2_envelope(params)
    canonical_json = _canonical_json(envelope)
    dag_cbor = encode_dag_cbor(envelope)
    cidv1 = node_id_from_bytes(dag_cbor)
    cose_sign1 = (
        cose_sign1_sign(dag_cbor, signing_private_key, kid=cose_kid)
        if signing_private_key is not None
        else b""
    )
    return Layer2EpochSnapshotV2(
        epoch_number=params.epoch_number,
        previous_snapshot_sha256=params.previous_snapshot_sha256,
        layer0_protocol_bundle_sha256=params.layer0_sha256,
        layer0_protocol_bundle_cidv1=params.layer0_cidv1,
        layer1_genesis_bundle_cidv1=params.layer1_cidv1,
        graph_state_digest=params.graph_state_digest,
        agent_state_digest=params.agent_state_digest,
        active_contract_digest=params.active_contract_digest,
        economic_settlement_root_sha256=params.economic_settlement_root_sha256,
        previous_epoch_state_root_cidv1_hex=params.previous_epoch_state_root_cidv1_hex,
        validator_set_root_sha256=params.validator_set_root_sha256,
        graph_state_scope=params.graph_state_scope,
        canonical_json=canonical_json,
        dag_cbor=dag_cbor,
        cidv1=cidv1,
        sha256=hashlib.sha256(dag_cbor).hexdigest(),
        cose_sign1=cose_sign1,
    )


def verify_layer2_epoch_snapshot(
    snapshot: Layer2EpochSnapshot,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
) -> bool:
    rebuilt = generate_layer2_epoch_snapshot(
        epoch_number=snapshot.epoch_number,
        previous_snapshot_sha256=snapshot.previous_snapshot_sha256,
        layer0_sha256=snapshot.layer0_protocol_bundle_sha256,
        layer0_cidv1=snapshot.layer0_protocol_bundle_cidv1,
        layer1_cidv1=snapshot.layer1_genesis_bundle_cidv1,
        graph_state_digest=snapshot.graph_state_digest,
        agent_state_digest=snapshot.agent_state_digest,
        active_contract_digest=snapshot.active_contract_digest,
    )
    return (
        rebuilt.canonical_json == snapshot.canonical_json
        and rebuilt.dag_cbor == snapshot.dag_cbor
        and rebuilt.cidv1 == snapshot.cidv1
        and rebuilt.sha256 == snapshot.sha256
        and snapshot.public_rc_exclude is True
        and _verify_optional_cose(snapshot, public_key)
    )


def verify_layer2_epoch_snapshot_v2(
    snapshot: Layer2EpochSnapshotV2,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
) -> bool:
    rebuilt = generate_layer2_epoch_snapshot_v2(
        Layer2EpochSnapshotV2Params(
            epoch_number=snapshot.epoch_number,
            previous_snapshot_sha256=snapshot.previous_snapshot_sha256,
            layer0_sha256=snapshot.layer0_protocol_bundle_sha256,
            layer0_cidv1=snapshot.layer0_protocol_bundle_cidv1,
            layer1_cidv1=snapshot.layer1_genesis_bundle_cidv1,
            graph_state_digest=snapshot.graph_state_digest,
            agent_state_digest=snapshot.agent_state_digest,
            active_contract_digest=snapshot.active_contract_digest,
            economic_settlement_root_sha256=snapshot.economic_settlement_root_sha256,
            previous_epoch_state_root_cidv1_hex=snapshot.previous_epoch_state_root_cidv1_hex,
            validator_set_root_sha256=snapshot.validator_set_root_sha256,
            graph_state_scope=snapshot.graph_state_scope,
        )
    )
    return (
        rebuilt.canonical_json == snapshot.canonical_json
        and rebuilt.dag_cbor == snapshot.dag_cbor
        and rebuilt.cidv1 == snapshot.cidv1
        and rebuilt.sha256 == snapshot.sha256
        and snapshot.public_rc_exclude is True
        and _verify_optional_cose(snapshot, public_key)
    )


def _verify_optional_cose(
    snapshot: Layer2EpochSnapshot | Layer2EpochSnapshotV2,
    public_key: ed25519.Ed25519PublicKey | None,
) -> bool:
    if snapshot.cose_sign1 == b"":
        return True
    if public_key is None:
        return False
    try:
        verified = cose_sign1_verify(snapshot.cose_sign1, public_key)
    except (InvalidSignature, ValueError):
        return False
    return verified["nodeid"] == snapshot.cidv1 and verified["payload"] == snapshot.dag_cbor


__all__ = [
    "ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION",
    "Layer2EpochSnapshot",
    "Layer2EpochSnapshotV2",
    "Layer2EpochSnapshotV2Params",
    "MAX_EPOCH_PUBLIC_DELTAS",
    "MAX_VALIDATOR_SET_MEMBERS",
    "PUBLIC_CONSENSUS_GRAPH_STATE_SCOPE_V1",
    "PUBLIC_CONSENSUS_GRAPH_SNAPSHOT_SCHEMA_V1",
    "VALIDATOR_SET_MANIFEST_SCHEMA_V1",
    "build_public_consensus_graph_snapshot_manifest",
    "build_validator_set_manifest",
    "generate_layer2_epoch_snapshot",
    "generate_layer2_epoch_snapshot_v2",
    "graph_state_digest_from_manifest",
    "validator_set_root_from_manifest",
    "verify_layer2_epoch_snapshot",
    "verify_layer2_epoch_snapshot_v2",
]
