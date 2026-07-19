# SPDX-License-Identifier: AGPL-3.0-only
"""Production Atlas slice schema primitives for Window 1576.

This module defines deterministic schema helpers only. It does not write LMDB,
sign manifests, fetch content, materialize slices, or grant authority.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from ilc_core.private_json_guardrails import canonical_json, reject_float


ATLAS_SLICE_SCHEMA_VERSION = "atlas_slice_schema_1576.v0.1"
ATLAS_SLICE_CANONICALIZATION_VERSION = "atlas_slice_canonical_json_sha384_1576.v0.1"
ATLAS_SLICE_NATIVE_TABLE = "__signed_slices__"
ATLAS_SLICE_LEAF_DOMAIN = b"ILC_ATLAS_SLICE_LEAF_V1"
ATLAS_SLICE_NODE_DOMAIN = b"ILC_ATLAS_SLICE_NODE_V1"
ATLAS_SLICE_EMPTY_DOMAIN = b"ILC_ATLAS_SLICE_EMPTY_V1"
ATLAS_SLICE_PREIMAGE_DOMAIN = "ILC_ATLAS_SLICE_SIGNED_PREIMAGE_V1"
ATLAS_SLICE_WITNESS_DOMAIN = "ILC_ATLAS_SLICE_PORTABLE_WITNESS_V1"

ALLOWED_PRIVACY_CLASSES = frozenset(
    {
        "public",
        "private_local",
        "redacted",
        "structure_only",
        "manifest_only",
        "mixed_overlay",
    }
)
ALLOWED_SIGNER_AUTHORITY_CLASSES = frozenset(
    {
        "genesis",
        "sidecar_maintainer",
        "collaborator_group",
        "private_capability_holder",
    }
)
GENESIS_PUBLIC_SIGNABLE_PROJECTIONS = frozenset(
    {
        "genesis_core_star_map",
        "public_protocol_graph",
        "support_candidate_graph",
    }
)
SIGNED_SLICE_PREIMAGE_REQUIRED_FIELDS = (
    "authority_root",
    "canonicalization_version",
    "epoch_or_version",
    "included_tables",
    "merkle_root",
    "privacy_class",
    "projection_parameters",
    "projection_query_id",
    "schema_version",
    "slice_id",
)
PORTABLE_WITNESS_REQUIRED_FIELDS = (
    "authority_proof_path",
    "authority_root",
    "availability",
    "canonicalization_version",
    "content_commitments",
    "derived_from_native_record_sha384",
    "edge_commitments",
    "epoch_or_version",
    "excluded_tables",
    "manifest_domain",
    "merkle_root",
    "node_commitments",
    "permission_policy",
    "privacy_class",
    "projection_parameters",
    "projection_query_id",
    "required_tests",
    "schema_version",
    "semantic_loss_annotations",
    "signer_authority_class",
    "slice_id",
)
_HEX_96 = frozenset("0123456789abcdef")
_FLOAT_TOKEN = "atlas_slice_schema_float_not_allowed"


class AtlasSliceSchemaError(ValueError):
    """Stable Atlas slice schema error."""


def canonical_schema_json(payload: Mapping[str, Any]) -> str:
    """Return deterministic canonical JSON for slice schema records."""

    _reject_float(payload)
    return canonical_json(payload, float_token=_FLOAT_TOKEN)


def sha384_canonical(payload: Mapping[str, Any]) -> str:
    """Return SHA-384 over canonical schema JSON."""

    return hashlib.sha384(canonical_schema_json(payload).encode("utf-8")).hexdigest()


def build_projection_query_definition(
    *,
    projection_query_id: str,
    projection_parameters: Mapping[str, Any],
    included_tables: Sequence[str],
    privacy_class: str,
) -> dict[str, Any]:
    """Build and validate a deterministic named-projection definition."""

    _require_non_empty_str(projection_query_id, "projection_query_id")
    _require_mapping(projection_parameters, "projection_parameters")
    normalized_tables = _normalize_included_tables(included_tables)
    if privacy_class not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSliceSchemaError("atlas_slice_privacy_class_invalid")
    if ATLAS_SLICE_NATIVE_TABLE in normalized_tables:
        raise AtlasSliceSchemaError("atlas_slice_recursive_signed_slices_table_forbidden")
    definition = {
        "canonicalization_version": ATLAS_SLICE_CANONICALIZATION_VERSION,
        "included_tables": normalized_tables,
        "privacy_class": privacy_class,
        "projection_parameters": dict(sorted(projection_parameters.items())),
        "projection_query_id": projection_query_id,
        "schema_version": ATLAS_SLICE_SCHEMA_VERSION,
    }
    _reject_float(definition)
    return definition


def merkle_leaf_hash(*, table: str, key: str, canonical_value: str) -> str:
    """Hash one signed-slice leaf using the ratified SHA-384 leaf recipe."""

    _require_non_empty_str(table, "table")
    _require_non_empty_str(key, "key")
    _require_non_empty_str(canonical_value, "canonical_value")
    return _sha384_bytes(
        b"".join(
            (
                ATLAS_SLICE_LEAF_DOMAIN,
                _len_prefixed(table.encode("utf-8")),
                _len_prefixed(key.encode("utf-8")),
                _len_prefixed(canonical_value.encode("utf-8")),
            )
        )
    )


def merkle_root_from_rows(rows: Sequence[Mapping[str, Any]]) -> str:
    """Return deterministic SHA-384 root for sorted projection rows."""

    leaves = []
    seen_row_keys: set[tuple[str, str]] = set()
    for row in rows:
        table = _required_str(row, "table")
        key = _required_str(row, "key")
        row_key = (table, key)
        if row_key in seen_row_keys:
            raise AtlasSliceSchemaError("atlas_slice_row_key_duplicate")
        seen_row_keys.add(row_key)
        value = row.get("value")
        if not isinstance(value, Mapping):
            raise AtlasSliceSchemaError("atlas_slice_row_value_not_mapping")
        leaves.append(
            (
                table,
                key,
                merkle_leaf_hash(
                    table=table,
                    key=key,
                    canonical_value=canonical_schema_json(value),
                ),
            )
        )
    if not leaves:
        return _sha384_bytes(ATLAS_SLICE_EMPTY_DOMAIN)
    level = [leaf for _, _, leaf in sorted(leaves, key=lambda item: (item[0], item[1], item[2]))]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [
            _sha384_bytes(
                ATLAS_SLICE_NODE_DOMAIN
                + bytes.fromhex(level[index])
                + bytes.fromhex(level[index + 1])
            )
            for index in range(0, len(level), 2)
        ]
    return level[0]


def build_signed_slice_preimage(
    *,
    slice_id: str,
    projection_query_id: str,
    projection_parameters: Mapping[str, Any],
    included_tables: Sequence[str],
    privacy_class: str,
    authority_root: str,
    epoch_or_version: str,
    merkle_root: str,
) -> dict[str, Any]:
    """Build the native signed-slice preimage committed by authority signature."""

    projection = build_projection_query_definition(
        projection_query_id=projection_query_id,
        projection_parameters=projection_parameters,
        included_tables=included_tables,
        privacy_class=privacy_class,
    )
    _require_non_empty_str(slice_id, "slice_id")
    _require_non_empty_str(authority_root, "authority_root")
    _require_non_empty_str(epoch_or_version, "epoch_or_version")
    if not _is_sha384(merkle_root):
        raise AtlasSliceSchemaError("atlas_slice_merkle_root_invalid")
    preimage = {
        "authority_root": authority_root,
        "canonicalization_version": ATLAS_SLICE_CANONICALIZATION_VERSION,
        "epoch_or_version": epoch_or_version,
        "included_tables": projection["included_tables"],
        "merkle_root": merkle_root,
        "preimage_domain": ATLAS_SLICE_PREIMAGE_DOMAIN,
        "privacy_class": privacy_class,
        "projection_parameters": projection["projection_parameters"],
        "projection_query_id": projection_query_id,
        "schema_version": ATLAS_SLICE_SCHEMA_VERSION,
        "slice_id": slice_id,
    }
    _require_exact_field_set(
        preimage,
        set(SIGNED_SLICE_PREIMAGE_REQUIRED_FIELDS) | {"preimage_domain"},
        "atlas_slice_preimage_fields_invalid",
    )
    _reject_float(preimage)
    return preimage


def native_signed_slice_record(
    *,
    preimage: Mapping[str, Any],
    signer_authority_class: str,
    signer_key_ref: str,
    authority_proof_path: Sequence[str],
    signature_status: str = "unsigned_schema_only",
) -> dict[str, Any]:
    """Build an unsigned future `__signed_slices__` table record shape."""

    if signer_authority_class not in ALLOWED_SIGNER_AUTHORITY_CLASSES:
        raise AtlasSliceSchemaError("atlas_slice_signer_authority_class_invalid")
    if signer_authority_class == "genesis":
        projection = _required_str(preimage, "projection_query_id")
        if projection not in GENESIS_PUBLIC_SIGNABLE_PROJECTIONS:
            raise AtlasSliceSchemaError("atlas_slice_genesis_projection_not_signable")
    _require_non_empty_str(signer_key_ref, "signer_key_ref")
    proof = _normalize_str_sequence(authority_proof_path, "authority_proof_path")
    preimage_sha384 = sha384_canonical(preimage)
    record = {
        "authority_proof_path": proof,
        "native_record_kind": "atlas_signed_slice_record",
        "native_table": ATLAS_SLICE_NATIVE_TABLE,
        "preimage": dict(preimage),
        "preimage_sha384": preimage_sha384,
        "schema_version": ATLAS_SLICE_SCHEMA_VERSION,
        "signature": None,
        "signature_status": signature_status,
        "signer_authority_class": signer_authority_class,
        "signer_key_ref": signer_key_ref,
    }
    _reject_float(record)
    return record


def derive_portable_manifest_witness(
    *,
    native_record: Mapping[str, Any],
    node_commitments: Sequence[Mapping[str, Any]] = (),
    edge_commitments: Sequence[Mapping[str, Any]] = (),
    content_commitments: Sequence[Mapping[str, Any]] = (),
    availability: Mapping[str, Any] | None = None,
    permission_policy: Mapping[str, Any] | None = None,
    required_tests: Sequence[str] = (),
    semantic_loss_annotations: Sequence[str] = (),
) -> dict[str, Any]:
    """Derive a portable manifest witness from a native signed-slice record."""

    _reject_float(native_record)
    preimage = native_record.get("preimage")
    if not isinstance(preimage, Mapping):
        raise AtlasSliceSchemaError("atlas_slice_native_record_preimage_missing")
    if sha384_canonical(preimage) != _required_str(native_record, "preimage_sha384"):
        raise AtlasSliceSchemaError("atlas_slice_native_record_preimage_hash_mismatch")
    manifest = {
        "authority_proof_path": _normalize_str_sequence(
            native_record.get("authority_proof_path", ()),
            "authority_proof_path",
        ),
        "authority_root": _required_str(preimage, "authority_root"),
        "availability": dict(availability or {"fetch_source_classes": []}),
        "canonicalization_version": ATLAS_SLICE_CANONICALIZATION_VERSION,
        "content_commitments": _normalize_commitments(content_commitments, "content_commitments"),
        "derived_from_native_record_sha384": sha384_canonical(native_record),
        "edge_commitments": _normalize_commitments(edge_commitments, "edge_commitments"),
        "epoch_or_version": _required_str(preimage, "epoch_or_version"),
        "excluded_tables": [ATLAS_SLICE_NATIVE_TABLE],
        "manifest_domain": ATLAS_SLICE_WITNESS_DOMAIN,
        "merkle_root": _required_str(preimage, "merkle_root"),
        "node_commitments": _normalize_commitments(node_commitments, "node_commitments"),
        "permission_policy": dict(permission_policy or {"privacy_class": preimage["privacy_class"]}),
        "privacy_class": _required_str(preimage, "privacy_class"),
        "projection_parameters": dict(preimage["projection_parameters"]),
        "projection_query_id": _required_str(preimage, "projection_query_id"),
        "required_tests": _normalize_str_sequence(required_tests, "required_tests"),
        "schema_version": ATLAS_SLICE_SCHEMA_VERSION,
        "semantic_loss_annotations": _normalize_str_sequence(
            semantic_loss_annotations,
            "semantic_loss_annotations",
        ),
        "signer_authority_class": _required_str(native_record, "signer_authority_class"),
        "slice_id": _required_str(preimage, "slice_id"),
    }
    _require_exact_field_set(
        manifest,
        set(PORTABLE_WITNESS_REQUIRED_FIELDS),
        "atlas_slice_portable_witness_fields_invalid",
    )
    _reject_float(manifest)
    return {**manifest, "manifest_sha384": sha384_canonical(manifest)}


def _normalize_commitments(
    values: Sequence[Mapping[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    commitments = []
    for value in values:
        if not isinstance(value, Mapping):
            raise AtlasSliceSchemaError(f"atlas_slice_commitment_invalid:{field}")
        _reject_float(value)
        _validate_commitment_shape(value, field)
        commitments.append(dict(sorted(value.items())))
    return sorted(commitments, key=lambda row: canonical_schema_json(row))


def _validate_commitment_shape(value: Mapping[str, Any], field: str) -> None:
    if field == "node_commitments":
        expected = {"node_id", "record_sha384"}
        digest_field = "record_sha384"
    elif field == "edge_commitments":
        expected = {"edge_id", "record_sha384"}
        digest_field = "record_sha384"
    elif field == "content_commitments":
        present_id_fields = [
            candidate for candidate in ("content_id", "content_cid", "table_key") if candidate in value
        ]
        if len(present_id_fields) != 1:
            raise AtlasSliceSchemaError(f"atlas_slice_commitment_id_fields_invalid:{field}")
        expected = {present_id_fields[0], "sha384"}
        digest_field = "sha384"
    else:
        raise AtlasSliceSchemaError(f"atlas_slice_commitment_field_unknown:{field}")
    if set(value) != expected:
        raise AtlasSliceSchemaError(f"atlas_slice_commitment_fields_invalid:{field}")
    for key, raw in value.items():
        if key == digest_field:
            if not _is_sha384(raw):
                raise AtlasSliceSchemaError(f"atlas_slice_commitment_sha384_invalid:{field}:{key}")
            continue
        _require_non_empty_str(raw, f"{field}:{key}")


def _normalize_included_tables(values: Sequence[str]) -> list[str]:
    return _normalize_str_sequence(values, "included_tables")


def _normalize_str_sequence(values: Any, field: str) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise AtlasSliceSchemaError(f"atlas_slice_sequence_invalid:{field}")
    normalized = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise AtlasSliceSchemaError(f"atlas_slice_sequence_value_invalid:{field}")
        normalized.append(value)
    if not normalized and field in {"included_tables", "authority_proof_path"}:
        raise AtlasSliceSchemaError(f"atlas_slice_sequence_empty:{field}")
    return sorted(dict.fromkeys(normalized))


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AtlasSliceSchemaError(f"atlas_slice_required_string_invalid:{key}")
    return value


def _require_non_empty_str(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSliceSchemaError(f"atlas_slice_required_string_invalid:{field}")


def _require_mapping(value: Any, field: str) -> None:
    if not isinstance(value, Mapping):
        raise AtlasSliceSchemaError(f"atlas_slice_mapping_invalid:{field}")
    _reject_float(value)


def _reject_float(value: Any) -> None:
    try:
        reject_float(value, _FLOAT_TOKEN)
    except ValueError as exc:
        raise AtlasSliceSchemaError(_FLOAT_TOKEN) from exc


def _require_exact_field_set(payload: Mapping[str, Any], expected: set[str], error: str) -> None:
    if set(payload) != expected:
        raise AtlasSliceSchemaError(error)


def _len_prefixed(data: bytes) -> bytes:
    return len(data).to_bytes(8, "big") + data


def _sha384_bytes(data: bytes) -> str:
    return hashlib.sha384(data).hexdigest()


def _is_sha384(value: str) -> bool:
    return isinstance(value, str) and len(value) == 96 and all(c in _HEX_96 for c in value)
