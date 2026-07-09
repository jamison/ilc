# SPDX-License-Identifier: AGPL-3.0-only
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
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION = "layer0_truth_primitive_schemas_1558.v0.1"

TRUTH_PRIMITIVE_SCHEMA_TYPE_NAMES = (
    "truth_primitive.assert.truth",
    "truth_primitive.commit.epoch",
    "truth_primitive.contradict.assert",
    "truth_primitive.link.claim",
    "truth_primitive.refute.claim",
    "truth_primitive.revise.assert",
    "truth_primitive.validate.claim",
    "system.genesis_authority_assertion",
)

_TRUTH_PRIMITIVE_EDGE_TYPES = {
    "assert.truth": ("asserted_by", "extends"),
    "validate.claim": ("validated_by",),
    "contradict.assert": ("contradicts",),
    "refute.claim": ("refuted_by", "supported_by"),
    "revise.assert": ("asserted_by", "revision_of", "revised_by"),
    "link.claim": ("cites", "contrasts", "elaborates", "generalizes", "instantiates"),
    "commit.epoch": ("finalizes",),
}

_TRUTH_PRIMITIVE_PAYLOAD_FIELDS = {
    "assert.truth": (
        "content",
        "epistemic_type",
        "parent_node_ids",
        "primitive_type",
    ),
    "validate.claim": ("confidence", "evidence_summary", "target_node_id"),
    "contradict.assert": (
        "contradiction_scope",
        "node_a_id",
        "node_b_id",
        "rationale",
    ),
    "refute.claim": (
        "evidence_node_ids",
        "refutation_criterion",
        "target_node_id",
    ),
    "revise.assert": (
        "revised_content",
        "revision_rationale",
        "source_node_id",
    ),
    "link.claim": (
        "link_rationale",
        "link_type",
        "source_node_id",
        "target_node_id",
    ),
    "commit.epoch": (
        "epoch_id",
        "participating_agents",
        "previous_epoch_hash",
        "reward_distribution",
        "scoring_results",
    ),
}

_TRUTH_PRIMITIVE_AUTHORITY = {
    "assert.truth": "agent_or_genesis_authority",
    "validate.claim": "agent",
    "contradict.assert": "agent",
    "refute.claim": "agent",
    "revise.assert": "agent",
    "link.claim": "agent",
    "commit.epoch": "consensus_layer_only",
}


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer0_protocol_bundle_float_not_allowed")


def build_truth_primitive_layer0_schemas() -> tuple[Mapping[str, object], ...]:
    """Return Layer 0 schema records for CDL-073 truth primitives and HB-001.

    The source canon is the Phase 855 truth-primitive wire format and Phase 859
    Layer 0 schema-section artifact. This helper embeds compact machine-readable
    records through the existing Layer 0 `schemas=` path; it does not activate
    live graph submission, public P2P, or public RC distribution.
    """

    schema_records: list[dict[str, object]] = []
    for primitive in sorted(_TRUTH_PRIMITIVE_PAYLOAD_FIELDS):
        schema_records.append(
            {
                "authority": _TRUTH_PRIMITIVE_AUTHORITY[primitive],
                "canonical_encoding": "dag-cbor",
                "cdl_dependency": CDL_073_DEPENDENCY,
                "edge_types_produced": list(_TRUTH_PRIMITIVE_EDGE_TYPES[primitive]),
                "required_envelope_fields": [
                    "agent_id",
                    "epoch",
                    "payload",
                    "primitive",
                    "sig",
                    "v",
                ],
                "required_payload_fields": list(_TRUTH_PRIMITIVE_PAYLOAD_FIELDS[primitive]),
                "schema_kind": "truth_primitive_submission",
                "schema_version": LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION,
                "type_name": f"truth_primitive.{primitive}",
            }
        )
    schema_records.append(
        {
            "authority": "genesis_authority",
            "canonical_encoding": "canonical-json-for-ml-dsa-signing",
            "cdl_dependency": CDL_073_DEPENDENCY,
            "required_envelope_fields": [
                "agent_id",
                "epoch",
                "payload",
                "primitive",
                "sig",
                "v",
            ],
            "required_payload_fields": [
                "genesis_authority_key",
                "genesis_epoch",
                "is_testnet",
                "kind",
                "network_id",
                "real_ecu",
                "schema_version",
                "validators",
            ],
            "schema_kind": "system_genesis_assertion",
            "schema_version": LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION,
            "type_name": "system.genesis_authority_assertion",
        }
    )
    normalized = normalize_json_value(schema_records)
    if not isinstance(normalized, list):
        raise ValueError("layer0_truth_primitive_schema_build_failed")
    return freeze_json_value(normalized)  # type: ignore[return-value]


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
    type_names = [str(schema.get("type_name", "")) for schema in normalized_schemas]
    if len(type_names) != len(set(type_names)):
        raise ValueError("layer0_bundle_duplicate_schema_type_name")

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
    include_truth_primitive_schemas: bool = False,
    signing_private_key: ed25519.Ed25519PrivateKey | None = None,
    cose_kid: bytes | None = None,
) -> Layer0ProtocolBundle:
    if bundle_id == "" or version == "":
        raise ValueError("layer0_bundle_missing_identifier")
    merged_schemas = list(schemas)
    if include_truth_primitive_schemas is True:
        merged_schemas.extend(
            thaw_json_value(build_truth_primitive_layer0_schemas())  # type: ignore[arg-type]
        )
    elif include_truth_primitive_schemas is not False:
        raise ValueError("layer0_bundle_include_truth_primitive_schemas_must_be_bool")
    if len(merged_schemas) == 0 or len(merged_schemas) > MAX_SCHEMA_COUNT:
        raise ValueError("layer0_bundle_invalid_schema_count")

    envelope, frozen_schemas, frozen_parameters = _build_layer0_envelope(
        bundle_id=bundle_id,
        version=version,
        schemas=merged_schemas,
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
    "CDL_073_DEPENDENCY",
    "LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION",
    "Layer0ProtocolBundle",
    "MAX_SCHEMA_COUNT",
    "TRUTH_PRIMITIVE_SCHEMA_TYPE_NAMES",
    "build_truth_primitive_layer0_schemas",
    "generate_layer0_protocol_bundle",
    "verify_layer0_protocol_bundle",
]
