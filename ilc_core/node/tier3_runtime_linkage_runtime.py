# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


TIER3_RUNTIME_LINKAGE_VERSION = "tier3_runtime_linkage_runtime_1201.v0.1"

SCHEMA_NODE_REQUIRED_FIELDS = (
    "schema_id",
    "schema_version",
    "schema_digest",
    "schema_artifact_ref",
    "authority_ref",
    "lineage_ref",
    "status",
)
RUNTIME_NODE_REQUIRED_FIELDS = (
    "runtime_id",
    "runtime_version",
    "implementation_ref",
    "schema_refs",
    "cdl_dependency_refs",
    "adr_dependency_refs",
    "test_evidence_refs",
    "lineage_ref",
    "status",
)
SCHEMA_NODE_STATUSES = frozenset({"draft", "accepted", "ratified", "superseded"})
RUNTIME_NODE_STATUSES = frozenset({"planned", "active", "superseded"})
RUNTIME_NODE_LIST_FIELDS = frozenset(
    {"schema_refs", "cdl_dependency_refs", "adr_dependency_refs", "test_evidence_refs"}
)


@dataclass(frozen=True)
class SchemaNodeRecord:
    schema_id: str
    schema_version: str
    schema_digest: str
    schema_artifact_ref: str
    authority_ref: str
    lineage_ref: str
    status: str


@dataclass(frozen=True)
class RuntimeNodeRecord:
    runtime_id: str
    runtime_version: str
    implementation_ref: str
    schema_refs: tuple[str, ...]
    cdl_dependency_refs: tuple[str, ...]
    adr_dependency_refs: tuple[str, ...]
    test_evidence_refs: tuple[str, ...]
    lineage_ref: str
    status: str


def _require_mapping(record: object, *, token: str) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(token)
    return dict(record)


def _reject_float_values(value: object, *, context: str) -> None:
    if isinstance(value, float):
        raise ValueError(f"tier3_float_not_allowed:{context}")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_values(item, context=f"{context}.{key}")
    if isinstance(value, list):
        for idx, item in enumerate(value):
            _reject_float_values(item, context=f"{context}[{idx}]")


def _validate_required_fields(
    record: dict[str, Any], *, required_fields: tuple[str, ...], prefix: str
) -> None:
    for field in required_fields:
        if field not in record:
            raise ValueError(f"{prefix}_missing_field:{field}")
        if record[field] in ("", None):
            raise ValueError(f"{prefix}_invalid_field:{field}")


def _validate_status(value: object, *, allowed: frozenset[str], prefix: str) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{prefix}_invalid_status")


def _validate_string_field(record: dict[str, Any], *, field: str, prefix: str) -> None:
    if not isinstance(record[field], str):
        raise ValueError(f"{prefix}_invalid_field:{field}")


def _validate_string_list(record: dict[str, Any], *, field: str, prefix: str) -> list[str]:
    value = record[field]
    if not isinstance(value, list):
        raise ValueError(f"{prefix}_invalid_field:{field}")
    if field == "schema_refs" and not value:
        raise ValueError("tier3_runtime_node_schema_refs_empty")
    for item in value:
        if not isinstance(item, str) or item == "":
            raise ValueError(f"{prefix}_invalid_field:{field}")
    return list(value)


def validate_schema_node(record: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(record, token="tier3_schema_node_not_mapping")
    _reject_float_values(candidate, context="schema_node")
    _validate_required_fields(
        candidate,
        required_fields=SCHEMA_NODE_REQUIRED_FIELDS,
        prefix="tier3_schema_node",
    )
    for field in SCHEMA_NODE_REQUIRED_FIELDS:
        _validate_string_field(candidate, field=field, prefix="tier3_schema_node")
    _validate_status(
        candidate["status"],
        allowed=SCHEMA_NODE_STATUSES,
        prefix="tier3_schema_node",
    )
    return candidate


def validate_runtime_node(record: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(record, token="tier3_runtime_node_not_mapping")
    _reject_float_values(candidate, context="runtime_node")
    _validate_required_fields(
        candidate,
        required_fields=RUNTIME_NODE_REQUIRED_FIELDS,
        prefix="tier3_runtime_node",
    )
    for field in RUNTIME_NODE_REQUIRED_FIELDS:
        if field in RUNTIME_NODE_LIST_FIELDS:
            _validate_string_list(candidate, field=field, prefix="tier3_runtime_node")
        else:
            _validate_string_field(candidate, field=field, prefix="tier3_runtime_node")
    _validate_status(
        candidate["status"],
        allowed=RUNTIME_NODE_STATUSES,
        prefix="tier3_runtime_node",
    )
    return candidate


def serialize_tier3_record(record: dict[str, Any]) -> str:
    _reject_float_values(record, context="tier3_record")
    return json.dumps(
        record,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
