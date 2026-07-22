# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cbor_canonical import MAX_CANONICAL_CBOR_INPUT_BYTES
from ilc_core.crypto.cose_sign1 import cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import decode_dag_cbor_strict, validate_canonical_ilc_dag_cbor

_MAX_HEX_INPUT_CHARS = MAX_CANONICAL_CBOR_INPUT_BYTES * 2
_LOWER_HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True)
class VerifiedAdr0009Layer:
    layer: int
    cidv1: str
    dag_cbor: bytes
    payload: Mapping[str, object]
    cose_sign1: bytes


@dataclass(frozen=True)
class VerifiedAdr0009Bundle:
    layer0: VerifiedAdr0009Layer
    layer1: VerifiedAdr0009Layer
    layer2: VerifiedAdr0009Layer
    layer3: VerifiedAdr0009Layer

    @property
    def layers(self) -> tuple[VerifiedAdr0009Layer, VerifiedAdr0009Layer, VerifiedAdr0009Layer, VerifiedAdr0009Layer]:
        return (self.layer0, self.layer1, self.layer2, self.layer3)


def verify_adr_0009_layer(
    layer: int,
    record: Mapping[str, object],
    *,
    public_key: ed25519.Ed25519PublicKey,
) -> VerifiedAdr0009Layer:
    """Verify one raw ADR-0009 layer record without importing builder modules."""
    if layer not in {0, 1, 2, 3}:
        raise ValueError("adr_0009_bundle_invalid_layer_index")
    cidv1 = _require_string(record, "cidv1", "adr_0009_bundle_missing_cidv1")
    parse_nodeid_strict(cidv1)
    dag_cbor = _bytes_from_hex(
        _require_string(record, "dag_cbor_hex", "adr_0009_bundle_missing_dag_cbor_hex"),
        "adr_0009_bundle_invalid_dag_cbor_hex",
    )
    _enforce_cbor_preload_cap(dag_cbor)
    validate_canonical_ilc_dag_cbor(dag_cbor)
    computed_cidv1 = node_id_from_bytes(dag_cbor)
    if computed_cidv1 != cidv1:
        raise ValueError("adr_0009_bundle_cid_mismatch")

    payload = decode_dag_cbor_strict(dag_cbor)
    if not isinstance(payload, dict):
        raise ValueError("adr_0009_bundle_payload_not_map")
    if payload.get("layer") != layer:
        raise ValueError("adr_0009_bundle_layer_index_mismatch")
    if payload.get("public_rc_exclude") is not True:
        raise ValueError("adr_0009_bundle_missing_private_guard")

    cose_sign1 = _bytes_from_hex(
        _require_string(record, "cose_sign1_hex", "adr_0009_bundle_missing_cose_sign1"),
        "adr_0009_bundle_invalid_cose_sign1_hex",
    )
    _enforce_cbor_preload_cap(cose_sign1)
    try:
        verified = cose_sign1_verify(cose_sign1, public_key)
    except InvalidSignature as exc:
        raise ValueError("adr_0009_bundle_cose_signature_invalid") from exc
    except ValueError as exc:
        raise ValueError("adr_0009_bundle_cose_invalid") from exc
    if verified["payload"] != dag_cbor:
        raise ValueError("adr_0009_bundle_cose_payload_mismatch")
    if verified["nodeid"] != cidv1:
        raise ValueError("adr_0009_bundle_cose_cid_mismatch")

    return VerifiedAdr0009Layer(
        layer=layer,
        cidv1=cidv1,
        dag_cbor=dag_cbor,
        payload=payload,
        cose_sign1=cose_sign1,
    )


def verify_adr_0009_bundle(
    bundle: Mapping[str, object],
    *,
    public_keys_by_layer: Mapping[int, ed25519.Ed25519PublicKey],
) -> VerifiedAdr0009Bundle:
    """Verify a four-layer ADR-0009 bundle and its cross-layer CID chain."""
    layers_obj = bundle.get("layers")
    if not isinstance(layers_obj, Mapping):
        raise ValueError("adr_0009_bundle_missing_layers")

    verified_layers = []
    for layer in range(4):
        record = _layer_record(layers_obj, layer)
        public_key = public_keys_by_layer.get(layer)
        if public_key is None:
            raise ValueError("adr_0009_bundle_missing_public_key")
        verified_layers.append(verify_adr_0009_layer(layer, record, public_key=public_key))

    layer0, layer1, layer2, layer3 = verified_layers
    _require_payload_link(
        layer1.payload,
        "layer0_protocol_bundle_cidv1",
        layer0.cidv1,
        "adr_0009_bundle_layer1_layer0_cid_mismatch",
    )
    _require_payload_link(
        layer2.payload,
        "layer0_protocol_bundle_cidv1",
        layer0.cidv1,
        "adr_0009_bundle_layer2_layer0_cid_mismatch",
    )
    _require_payload_link(
        layer2.payload,
        "layer1_genesis_bundle_cidv1",
        layer1.cidv1,
        "adr_0009_bundle_layer2_layer1_cid_mismatch",
    )
    _require_payload_link(
        layer3.payload,
        "layer2_epoch_snapshot_cidv1",
        layer2.cidv1,
        "adr_0009_bundle_layer3_layer2_cid_mismatch",
    )
    return VerifiedAdr0009Bundle(layer0=layer0, layer1=layer1, layer2=layer2, layer3=layer3)


def _layer_record(layers: Mapping[object, object], layer: int) -> Mapping[str, object]:
    record = layers.get(str(layer), layers.get(layer))
    if not isinstance(record, Mapping):
        raise ValueError("adr_0009_bundle_missing_layer_record")
    return record  # type: ignore[return-value]


def _require_string(record: Mapping[str, object], key: str, token: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(token)
    return value


def _bytes_from_hex(value: str, token: str) -> bytes:
    if len(value) > _MAX_HEX_INPUT_CHARS:
        raise ValueError("adr_0009_bundle_hex_input_exceeds_max_chars")
    if len(value) % 2 != 0 or any(char not in _LOWER_HEX for char in value):
        raise ValueError(token)
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(token) from exc


def _enforce_cbor_preload_cap(data: bytes) -> None:
    if len(data) > MAX_CANONICAL_CBOR_INPUT_BYTES:
        raise ValueError("adr_0009_bundle_cbor_input_exceeds_max_bytes")


def _require_payload_link(payload: Mapping[str, object], key: str, expected: str, token: str) -> None:
    if payload.get(key) != expected:
        raise ValueError(token)


__all__ = [
    "VerifiedAdr0009Bundle",
    "VerifiedAdr0009Layer",
    "verify_adr_0009_bundle",
    "verify_adr_0009_layer",
]
