# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-310 D2 schema baseline generator/verifier runtime."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Iterable


SCHEMA_BASELINE_VERSION = "d2_schema_baseline_310.v0.1"
ALLOWED_FIELD_TYPES = ("array", "bool", "int", "object", "string")


CANONICAL_SCHEMA_VECTORS: list[dict[str, Any]] = [
    {
        "schema_id": "d2.claim.v1",
        "fields": [
            {"name": "claim_id", "type": "string", "required": True},
            {"name": "body", "type": "string", "required": True},
            {"name": "epoch", "type": "int", "required": True},
            {"name": "agent_id", "type": "string", "required": False},
        ],
        "metadata": {"domain": "knowledge", "kind": "claim"},
    },
    {
        "schema_id": "d2.edge.v1",
        "fields": [
            {"name": "edge_id", "type": "string", "required": True},
            {"name": "source", "type": "string", "required": True},
            {"name": "target", "type": "string", "required": True},
            {"name": "relation", "type": "string", "required": True},
        ],
        "metadata": {"domain": "graph", "kind": "edge"},
    },
]


class D2SchemaValidationError(ValueError):
    """Typed validation exception with deterministic error token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _sorted_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value, key=lambda item: str(item)):
            if not isinstance(key, str):
                raise D2SchemaValidationError(
                    "d2_schema_metadata_key_not_string",
                    f"metadata_key_not_string:{key!r}",
                )
            if key in normalized:
                raise D2SchemaValidationError(
                    "d2_schema_metadata_key_collision",
                    f"metadata_key_collision:{key}",
                )
            normalized[key] = _sorted_mapping(value[key])
        return normalized
    if isinstance(value, list):
        return [_sorted_mapping(item) for item in value]
    return value


def _coerce_bool(value: Any, token: str, message: str) -> bool:
    if isinstance(value, bool):
        return value
    raise D2SchemaValidationError(token, message)


def _normalize_field(field: Any, *, schema_id: str) -> dict[str, Any]:
    if not isinstance(field, dict):
        raise D2SchemaValidationError(
            "d2_schema_invalid_field",
            f"field_not_object:{schema_id}",
        )

    name = field.get("name")
    if not isinstance(name, str) or not name.strip():
        raise D2SchemaValidationError(
            "d2_schema_missing_field_name",
            f"field_name_missing:{schema_id}",
        )

    field_type = field.get("type")
    if not isinstance(field_type, str) or field_type not in ALLOWED_FIELD_TYPES:
        raise D2SchemaValidationError(
            "d2_schema_invalid_field_type",
            f"field_type_invalid:{schema_id}:{name}",
        )

    required = _coerce_bool(
        field.get("required", False),
        "d2_schema_invalid_required_flag",
        f"required_flag_invalid:{schema_id}:{name}",
    )

    return {"name": name, "required": required, "type": field_type}


def _normalize_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise D2SchemaValidationError("d2_schema_invalid_entry", "entry_not_object")

    schema_id = entry.get("schema_id")
    if not isinstance(schema_id, str) or not schema_id.strip():
        raise D2SchemaValidationError("d2_schema_missing_schema_id", "schema_id_missing")

    raw_fields = entry.get("fields")
    if not isinstance(raw_fields, list):
        raise D2SchemaValidationError("d2_schema_fields_not_list", f"fields_not_list:{schema_id}")
    if not raw_fields:
        raise D2SchemaValidationError("d2_schema_fields_empty", f"fields_empty:{schema_id}")

    normalized_fields = sorted(
        (_normalize_field(field, schema_id=schema_id) for field in raw_fields),
        key=lambda item: (item["name"], item["type"], item["required"]),
    )
    dedupe_key = {item["name"] for item in normalized_fields}
    if len(dedupe_key) != len(normalized_fields):
        raise D2SchemaValidationError(
            "d2_schema_duplicate_field",
            f"duplicate_field_name:{schema_id}",
        )

    normalized: dict[str, Any] = {
        "schema_id": schema_id,
        "field_count": len(normalized_fields),
        "fields": normalized_fields,
    }

    metadata = entry.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            raise D2SchemaValidationError(
                "d2_schema_invalid_metadata",
                f"metadata_not_object:{schema_id}",
            )
        normalized["metadata"] = _sorted_mapping(metadata)

    return normalized


def generate_schema_catalog(entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Generate deterministic baseline schema catalog from raw entries."""

    entry_list = list(entries)
    if not entry_list:
        raise D2SchemaValidationError("d2_schema_entries_empty", "entries_empty")

    normalized_entries = sorted(
        (_normalize_entry(entry) for entry in entry_list),
        key=lambda item: item["schema_id"],
    )
    schema_ids = [entry["schema_id"] for entry in normalized_entries]
    if len(schema_ids) != len(set(schema_ids)):
        raise D2SchemaValidationError("d2_schema_duplicate_schema_id", "duplicate_schema_id")

    catalog_core = {
        "catalog_version": SCHEMA_BASELINE_VERSION,
        "entries": normalized_entries,
    }
    return {
        **catalog_core,
        "catalog_sha256": _stable_sha256(catalog_core),
    }


def verify_schema_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic schema catalog shape and digest."""

    if not isinstance(catalog, dict):
        raise D2SchemaValidationError("d2_schema_catalog_not_object", "catalog_not_object")

    observed_version = catalog.get("catalog_version")
    if observed_version != SCHEMA_BASELINE_VERSION:
        raise D2SchemaValidationError(
            "d2_schema_invalid_catalog_version",
            f"catalog_version_invalid:{observed_version}",
        )

    raw_entries = catalog.get("entries")
    if not isinstance(raw_entries, list):
        raise D2SchemaValidationError("d2_schema_catalog_entries_not_list", "entries_not_list")

    generated = generate_schema_catalog(raw_entries)
    canonical_core = {
        "catalog_version": SCHEMA_BASELINE_VERSION,
        "entries": generated["entries"],
    }
    observed_core = {
        "catalog_version": catalog.get("catalog_version"),
        "entries": catalog.get("entries"),
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(canonical_core)):
        raise D2SchemaValidationError("d2_schema_catalog_not_canonical", "catalog_not_canonical")

    observed_digest = catalog.get("catalog_sha256")
    if not isinstance(observed_digest, str):
        raise D2SchemaValidationError("d2_schema_catalog_digest_missing", "catalog_sha256_missing")
    if observed_digest != generated["catalog_sha256"]:
        raise D2SchemaValidationError("d2_schema_catalog_digest_mismatch", "catalog_sha256_mismatch")

    return {
        "valid": True,
        "catalog_version": SCHEMA_BASELINE_VERSION,
        "entry_count": len(generated["entries"]),
        "catalog_sha256": generated["catalog_sha256"],
        "checks": [
            {"check_type": "catalog_version_supported", "passed": True},
            {"check_type": "catalog_entries_canonical", "passed": True},
            {"check_type": "catalog_digest_matches", "passed": True},
        ],
    }


def canonical_schema_vectors() -> list[dict[str, Any]]:
    """Return a copy of baseline canonical vectors for deterministic tests."""

    return copy.deepcopy(CANONICAL_SCHEMA_VECTORS)
