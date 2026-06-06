"""PUBLIC_RC_EXCLUDE: private_layer0_protocol_bundle
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 0 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes
from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.private_json_guardrails import (
    canonical_json,
    freeze_json_value,
    normalize_json_value,
    reject_float,
    thaw_json_value,
)

MAX_SCHEMA_COUNT = 64
ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION = False  # guard cleared Phase 1520p - ADR-0009 accepted


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer0_protocol_bundle_float_not_allowed")


@dataclass(frozen=True)
class Layer0ProtocolBundle:
    bundle_id: str
    version: str
    schemas: tuple[Mapping[object, object], ...]
    parameters: Mapping[object, object]
    canonical_json: str
    dag_cbor: bytes
    cidv1: str
    sha256: str
    cose_sign1: bytes = b""
    public_rc_exclude: bool = True


def _build_layer0_envelope(
    *,
    bundle_id: str,
    version: str,
    schemas: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
    parameters: Mapping[str, object],
) -> tuple[dict[str, object], tuple[Mapping[object, object], ...], Mapping[object, object]]:
    reject_float(schemas, "layer0_protocol_bundle_float_not_allowed")
    reject_float(parameters, "layer0_protocol_bundle_float_not_allowed")
    normalized_schemas: list[dict[str, object]] = []
    for schema in schemas:
        normalized = normalize_json_value(schema)
        if not isinstance(normalized, dict):
            raise ValueError("layer0_bundle_invalid_schema")
        normalized_schemas.append(normalized)
    normalized_schemas.sort(key=lambda row: str(row.get("type_name", "")))
    for schema in normalized_schemas:
        if str(schema.get("type_name", "")) == "":
            raise ValueError("layer0_bundle_invalid_schema")

    normalized_parameters = normalize_json_value(parameters)
    if not isinstance(normalized_parameters, dict):
        raise ValueError("layer0_bundle_invalid_parameters")

    envelope = {
        "bundle_id": bundle_id,
        "layer": 0,
        "parameters": normalized_parameters,
        "public_rc_exclude": True,
        "schemas": normalized_schemas,
        "version": version,
    }
    return (
        envelope,
        freeze_json_value(normalized_schemas),  # type: ignore[return-value]
        freeze_json_value(normalized_parameters),  # type: ignore[return-value]
    )


def generate_layer0_protocol_bundle(
    *,
    bundle_id: str,
    version: str,
    schemas: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
    parameters: Mapping[str, object],
    signing_private_key: ed25519.Ed25519PrivateKey | None = None,
    cose_kid: bytes | None = None,
) -> Layer0ProtocolBundle:
    if bundle_id == "" or version == "":
        raise ValueError("layer0_bundle_missing_identifier")
    if len(schemas) == 0 or len(schemas) > MAX_SCHEMA_COUNT:
        raise ValueError("layer0_bundle_invalid_schema_count")

    envelope, frozen_schemas, frozen_parameters = _build_layer0_envelope(
        bundle_id=bundle_id,
        version=version,
        schemas=schemas,
        parameters=parameters,
    )
    canonical_json = _canonical_json(envelope)
    dag_cbor = encode_dag_cbor(envelope)
    cidv1 = node_id_from_bytes(dag_cbor)
    cose_sign1 = (
        cose_sign1_sign(dag_cbor, signing_private_key, kid=cose_kid)
        if signing_private_key is not None
        else b""
    )
    return Layer0ProtocolBundle(
        bundle_id=bundle_id,
        version=version,
        schemas=frozen_schemas,
        parameters=frozen_parameters,
        canonical_json=canonical_json,
        dag_cbor=dag_cbor,
        cidv1=cidv1,
        sha256=hashlib.sha256(dag_cbor).hexdigest(),
        cose_sign1=cose_sign1,
    )


def verify_layer0_protocol_bundle(
    bundle: Layer0ProtocolBundle,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
) -> bool:
    rebuilt = generate_layer0_protocol_bundle(
        bundle_id=bundle.bundle_id,
        version=bundle.version,
        schemas=thaw_json_value(bundle.schemas),  # type: ignore[arg-type]
        parameters=thaw_json_value(bundle.parameters),  # type: ignore[arg-type]
    )
    return (
        rebuilt.canonical_json == bundle.canonical_json
        and rebuilt.dag_cbor == bundle.dag_cbor
        and rebuilt.cidv1 == bundle.cidv1
        and rebuilt.sha256 == bundle.sha256
        and bundle.public_rc_exclude is True
        and _verify_optional_cose(bundle, public_key)
    )


def _verify_optional_cose(
    bundle: Layer0ProtocolBundle,
    public_key: ed25519.Ed25519PublicKey | None,
) -> bool:
    if bundle.cose_sign1 == b"":
        return True
    if public_key is None:
        return False
    try:
        verified = cose_sign1_verify(bundle.cose_sign1, public_key)
    except (InvalidSignature, ValueError):
        return False
    return verified["nodeid"] == bundle.cidv1 and verified["payload"] == bundle.dag_cbor


__all__ = [
    "ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION",
    "Layer0ProtocolBundle",
    "MAX_SCHEMA_COUNT",
    "generate_layer0_protocol_bundle",
    "verify_layer0_protocol_bundle",
]
