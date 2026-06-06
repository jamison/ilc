"""PUBLIC_RC_EXCLUDE: adr_0009_layer2_private_implementation
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 2 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.private_json_guardrails import canonical_json, reject_float, require_digest_ref, require_sha256_hex

ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION = False  # guard cleared Phase 1520p - ADR-0009 accepted


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


def _verify_optional_cose(
    snapshot: Layer2EpochSnapshot,
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
    "generate_layer2_epoch_snapshot",
    "verify_layer2_epoch_snapshot",
]
