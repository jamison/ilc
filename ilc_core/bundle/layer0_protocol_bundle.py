"""PUBLIC_RC_EXCLUDE: private_layer0_protocol_bundle
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 0 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

MAX_SCHEMA_COUNT = 64
ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION = True


def _canonical_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class Layer0ProtocolBundle:
    bundle_id: str
    version: str
    schemas: list[dict[str, object]]
    parameters: dict[str, object]
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


def generate_layer0_protocol_bundle(
    *,
    bundle_id: str,
    version: str,
    schemas: list[Mapping[str, object]],
    parameters: Mapping[str, object],
) -> Layer0ProtocolBundle:
    if bundle_id == "" or version == "":
        raise ValueError("layer0_bundle_missing_identifier")
    if len(schemas) == 0 or len(schemas) > MAX_SCHEMA_COUNT:
        raise ValueError("layer0_bundle_invalid_schema_count")

    normalized_schemas = [dict(schema) for schema in schemas]
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
        schemas=normalized_schemas,
        parameters=dict(parameters),
        canonical_json=canonical_json,
        sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_layer0_protocol_bundle(bundle: Layer0ProtocolBundle) -> bool:
    rebuilt = generate_layer0_protocol_bundle(
        bundle_id=bundle.bundle_id,
        version=bundle.version,
        schemas=bundle.schemas,
        parameters=bundle.parameters,
    )
    return (
        rebuilt.canonical_json == bundle.canonical_json
        and rebuilt.sha256 == bundle.sha256
        and bundle.public_rc_exclude is True
    )
