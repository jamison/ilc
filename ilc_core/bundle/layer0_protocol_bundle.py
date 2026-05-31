"""PUBLIC_RC_EXCLUDE: private_layer0_protocol_bundle
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 0 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from ilc_core.private_json_guardrails import (
    canonical_json,
    freeze_json_value,
    normalize_json_value,
    reject_float,
    thaw_json_value,
)

MAX_SCHEMA_COUNT = 64
ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION = True


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer0_protocol_bundle_float_not_allowed")


@dataclass(frozen=True)
class Layer0ProtocolBundle:
    bundle_id: str
    version: str
    schemas: tuple[Mapping[object, object], ...]
    parameters: Mapping[object, object]
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


def generate_layer0_protocol_bundle(
    *,
    bundle_id: str,
    version: str,
    schemas: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
    parameters: Mapping[str, object],
) -> Layer0ProtocolBundle:
    if bundle_id == "" or version == "":
        raise ValueError("layer0_bundle_missing_identifier")
    if len(schemas) == 0 or len(schemas) > MAX_SCHEMA_COUNT:
        raise ValueError("layer0_bundle_invalid_schema_count")

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

    envelope = {
        "bundle_id": bundle_id,
        "layer": 0,
        "parameters": dict(parameters),
        "public_rc_exclude": True,
        "schemas": normalized_schemas,
        "version": version,
    }
    canonical_json = _canonical_json(envelope)
    return Layer0ProtocolBundle(
        bundle_id=bundle_id,
        version=version,
        schemas=freeze_json_value(normalized_schemas),  # type: ignore[arg-type]
        parameters=freeze_json_value(normalize_json_value(parameters)),  # type: ignore[arg-type]
        canonical_json=canonical_json,
        sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_layer0_protocol_bundle(bundle: Layer0ProtocolBundle) -> bool:
    rebuilt = generate_layer0_protocol_bundle(
        bundle_id=bundle.bundle_id,
        version=bundle.version,
        schemas=thaw_json_value(bundle.schemas),  # type: ignore[arg-type]
        parameters=thaw_json_value(bundle.parameters),  # type: ignore[arg-type]
    )
    return (
        rebuilt.canonical_json == bundle.canonical_json
        and rebuilt.sha256 == bundle.sha256
        and bundle.public_rc_exclude is True
    )
