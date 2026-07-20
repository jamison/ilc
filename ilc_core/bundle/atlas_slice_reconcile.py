# SPDX-License-Identifier: AGPL-3.0-only
"""Atlas slice reconcile registry schema helpers for Window 1576.

This module validates local installed-slice registry metadata. It does not
install manifests, write LMDB, fetch blobs, grant roles, clear guards, sign
records, mint, settle, write wallets, activate sidecars, or transition epochs.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.bundle.atlas_sidecar_profile import ALLOWED_BOUNDED_QUERY_TYPES
from ilc_core.bundle.atlas_slice_schema import (
    ALLOWED_PRIVACY_CLASSES,
    ALLOWED_SIGNER_AUTHORITY_CLASSES,
)


ATLAS_SLICE_RECONCILE_SCHEMA_VERSION = "atlas_slice_reconcile_1576.v0.1"
ATLAS_SLICE_RECONCILE_RECEIPT_SCHEMA_VERSION = (
    "atlas_slice_reconcile_status_receipt_1576.v0.1"
)
ATLAS_SLICE_RECONCILE_PHASE = "1576-atlas-reconcile"
ATLAS_SLICE_RECONCILE_TOKEN = "atlas_slice_reconcile_schema_committed_phase_1576"
ATLAS_SLICE_RECONCILE_OPEN_ITEMS_TOKEN = (
    "atlas_slice_reconcile_open_items_resolved_phase_1576"
)
ATLAS_SLICE_RECONCILE_REGISTRY_LOCATION_TOKEN = (
    "atlas_slice_reconcile_registry_location_decided_phase_1576"
)
ATLAS_SLICE_RECONCILE_MEMBERSHIP_INDEX_TOKEN = (
    "atlas_slice_reconcile_membership_index_schema_committed_phase_1576"
)
ATLAS_SLICE_RECONCILE_CHUNK_FORMAT_TOKEN = (
    "atlas_slice_reconcile_chunk_format_committed_phase_1576"
)
ATLAS_SLICE_RECONCILE_NO_WRITE_TOKEN = (
    "atlas_slice_reconcile_no_lmdb_write_no_install_no_role_phase_1576"
)

NODE_COMMITMENT_DIGEST_FIELD = "record_sha384"
EDGE_COMMITMENT_DIGEST_FIELD = "record_sha384"
CONTENT_COMMITMENT_DIGEST_FIELD = "sha384"
DEFAULT_REGISTRY_PATH = Path("out/installed_slice_registry/registry.json")

ALLOWED_RECONCILE_STATES = frozenset(
    {
        "installed",
        "manifest_only",
        "partial",
        "pending_verification",
        "verification_failed",
    }
)
ALLOWED_AUTHORITY_PRECEDENCE_LEVELS = frozenset(
    {
        "genesis_core",
        "pending_local",
        "private_owner",
        "public_baseline",
        "public_extension",
    }
)
AUTHORITY_PRECEDENCE_ORDER = (
    "genesis_core",
    "public_baseline",
    "public_extension",
    "private_owner",
    "pending_local",
)
RECONCILE_NON_CLAIMS = {
    "no_epoch_transition": True,
    "no_guard_clearance": True,
    "no_lmdb_install": True,
    "no_lmdb_write": True,
    "no_manifest_download": True,
    "no_network_fetch": True,
    "no_production_minting": True,
    "no_production_signing": True,
    "no_public_graph_write": True,
    "no_role_grant": True,
    "no_sidecar_activation": True,
    "no_wallet_write": True,
}
RECONCILE_OUTPUT_TOKENS = (
    ATLAS_SLICE_RECONCILE_TOKEN,
    ATLAS_SLICE_RECONCILE_OPEN_ITEMS_TOKEN,
    ATLAS_SLICE_RECONCILE_REGISTRY_LOCATION_TOKEN,
    ATLAS_SLICE_RECONCILE_MEMBERSHIP_INDEX_TOKEN,
    ATLAS_SLICE_RECONCILE_CHUNK_FORMAT_TOKEN,
    ATLAS_SLICE_RECONCILE_NO_WRITE_TOKEN,
)

MAX_RECORDS_PER_REGISTRY = 1000
MAX_DEPENDENCY_MANIFESTS_PER_RECORD = 50
MAX_CHUNK_DIGESTS_PER_RECORD = 500
MAX_MANIFESTS_PER_MEMBERSHIP_ENTRY = 100
MAX_MEMBERSHIP_INDEX_ENTRIES = 100_000
MAX_STRING_LENGTH = 512
MAX_JSON_DEPTH = 32
MAX_REGISTRY_JSON_BYTES = 16 * 1024 * 1024

_HEX_96 = frozenset("0123456789abcdef")
_INSTALL_RECORD_FIELDS = frozenset(
    {
        "authority_precedence_level",
        "content_commitment_digest_field",
        "declared_chunk_digests",
        "dependency_manifest_sha384s",
        "edge_commitment_digest_field",
        "installed_at_utc",
        "manifest_sha384",
        "native_record_sha384",
        "node_commitment_digest_field",
        "non_claims",
        "privacy_class",
        "projection_query_id",
        "reconcile_state",
        "record_schema_version",
        "signer_authority_class",
        "slice_id",
    }
)
_REGISTRY_FIELDS = frozenset(
    {
        "non_claims",
        "record_count",
        "records",
        "registry_body_sha384",
        "registry_kind",
        "registry_schema_version",
    }
)
_MEMBERSHIP_ENTRY_FIELDS = frozenset({"manifest_sha384s", "stable_id"})
_RECEIPT_FIELDS = frozenset(
    {
        "counts",
        "generated_at_source",
        "generated_at_utc",
        "non_claims",
        "phase",
        "read_only",
        "receipt_body_sha384",
        "receipt_id",
        "registry_sha384",
        "schema_version",
        "tokens",
        "verdict",
    }
)
_RECEIPT_COUNT_FIELDS = frozenset({"records", *ALLOWED_RECONCILE_STATES})
_RECEIPT_PREFIX = "atlas_slice_reconcile_receipt:"


class AtlasSliceReconcileError(ValueError):
    """Stable Atlas slice reconcile error."""


def build_install_record(**fields: Any) -> dict[str, Any]:
    """Build and validate one installed-slice registry record."""

    record = {
        **fields,
        "content_commitment_digest_field": CONTENT_COMMITMENT_DIGEST_FIELD,
        "edge_commitment_digest_field": EDGE_COMMITMENT_DIGEST_FIELD,
        "node_commitment_digest_field": NODE_COMMITMENT_DIGEST_FIELD,
        "non_claims": _normalize_non_claims(fields.get("non_claims")),
        "record_schema_version": ATLAS_SLICE_RECONCILE_SCHEMA_VERSION,
    }
    return validate_install_record(record)


def validate_install_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize one installed-slice registry record."""

    _reject_unsafe_json_tree(record)
    normalized = dict(record)
    _require_exact_fields(normalized, _INSTALL_RECORD_FIELDS, "atlas_slice_install_record_fields_invalid")
    if normalized.get("record_schema_version") != ATLAS_SLICE_RECONCILE_SCHEMA_VERSION:
        raise AtlasSliceReconcileError("atlas_slice_install_record_schema_version_invalid")
    _require_sha384(normalized.get("manifest_sha384"), "atlas_slice_install_record_manifest_sha384_invalid")
    _require_sha384(
        normalized.get("native_record_sha384"),
        "atlas_slice_install_record_native_record_sha384_invalid",
    )
    _validate_categorical_fields(normalized)
    _validate_digest_field_names(normalized)
    _validate_timestamp_or_pending(normalized.get("installed_at_utc"))
    dependencies = _normalize_sha384_sequence(
        normalized.get("dependency_manifest_sha384s"),
        "dependency_manifest_sha384s",
        max_count=MAX_DEPENDENCY_MANIFESTS_PER_RECORD,
    )
    chunks = _normalize_sha384_sequence(
        normalized.get("declared_chunk_digests"),
        "declared_chunk_digests",
        max_count=MAX_CHUNK_DIGESTS_PER_RECORD,
    )
    return {
        **normalized,
        "declared_chunk_digests": chunks,
        "dependency_manifest_sha384s": dependencies,
        "non_claims": _normalize_non_claims(normalized.get("non_claims")),
    }


def build_reconcile_registry(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build a deterministic registry from validated install records."""

    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_records_invalid")
    if len(records) > MAX_RECORDS_PER_REGISTRY:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_too_many_records")
    validated = [validate_install_record(record) for record in records]
    manifests = [record["manifest_sha384"] for record in validated]
    if len(set(manifests)) != len(manifests):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_manifest_duplicate")
    body = {
        "non_claims": _standard_non_claims(),
        "record_count": len(validated),
        "records": sorted(validated, key=lambda record: record["manifest_sha384"]),
        "registry_kind": "installed_slice_registry",
        "registry_schema_version": ATLAS_SLICE_RECONCILE_SCHEMA_VERSION,
    }
    body_sha384 = _sha384_canonical(body)
    return {**body, "registry_body_sha384": body_sha384}


def validate_reconcile_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize an installed-slice registry."""

    _reject_unsafe_json_tree(registry)
    normalized = dict(registry)
    _require_exact_fields(normalized, _REGISTRY_FIELDS, "atlas_slice_reconcile_registry_fields_invalid")
    if normalized.get("registry_schema_version") != ATLAS_SLICE_RECONCILE_SCHEMA_VERSION:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_schema_version_invalid")
    if normalized.get("registry_kind") != "installed_slice_registry":
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_kind_invalid")
    records_raw = normalized.get("records")
    if not isinstance(records_raw, list):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_records_invalid")
    expected = build_reconcile_registry(records_raw)
    if normalized.get("record_count") != expected["record_count"]:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_count_mismatch")
    if normalized.get("registry_body_sha384") != expected["registry_body_sha384"]:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_sha384_mismatch")
    _normalize_non_claims(normalized.get("non_claims"))
    return expected


def write_reconcile_registry(
    path: str | Path,
    registry: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write an installed-slice registry JSON file."""

    validated = validate_reconcile_registry(registry)
    return _write_json_atomic(
        path,
        validated,
        allowed_root=allowed_root,
        token_prefix="atlas_slice_reconcile_registry",
    )


def load_reconcile_registry(path: str | Path) -> dict[str, Any]:
    """Load and validate a bounded installed-slice registry JSON file."""

    source = Path(path)
    if not source.exists():
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_missing")
    if source.stat().st_size > MAX_REGISTRY_JSON_BYTES:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_json_too_large")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_json_invalid") from exc
    if not isinstance(payload, Mapping):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_registry_not_object")
    return validate_reconcile_registry(payload)


def build_reconcile_receipt(
    registry: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build a read-only reconcile-status receipt for a validated registry."""

    generated_at_source = "caller_supplied"
    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        generated_at_source = "wall_clock_utc"
    _validate_timestamp(generated_at_utc)
    validated = validate_reconcile_registry(registry)
    body = {
        "counts": _registry_counts(validated),
        "generated_at_source": generated_at_source,
        "generated_at_utc": generated_at_utc,
        "non_claims": _standard_non_claims(),
        "phase": ATLAS_SLICE_RECONCILE_PHASE,
        "read_only": True,
        "registry_sha384": validated["registry_body_sha384"],
        "schema_version": ATLAS_SLICE_RECONCILE_RECEIPT_SCHEMA_VERSION,
        "tokens": list(RECONCILE_OUTPUT_TOKENS),
        "verdict": "pass",
    }
    body_sha384 = _sha384_canonical(body)
    return {
        **body,
        "receipt_body_sha384": body_sha384,
        "receipt_id": f"{_RECEIPT_PREFIX}{body_sha384}",
    }


def validate_reconcile_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a reconcile-status receipt."""

    _reject_unsafe_json_tree(receipt)
    normalized = dict(receipt)
    _require_exact_fields(normalized, _RECEIPT_FIELDS, "atlas_slice_reconcile_receipt_fields_invalid")
    _validate_receipt_semantics(normalized)
    body = {key: normalized[key] for key in sorted(_RECEIPT_FIELDS - {"receipt_body_sha384", "receipt_id"})}
    expected_sha384 = _sha384_canonical(body)
    if normalized.get("receipt_body_sha384") != expected_sha384:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_sha384_mismatch")
    if normalized.get("receipt_id") != f"{_RECEIPT_PREFIX}{expected_sha384}":
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_id_mismatch")
    return normalized


def write_reconcile_receipt(
    path: str | Path,
    receipt: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write a reconcile-status receipt JSON file."""

    validated = validate_reconcile_receipt(receipt)
    return _write_json_atomic(
        path,
        validated,
        allowed_root=allowed_root,
        token_prefix="atlas_slice_reconcile_receipt",
    )


def build_membership_index_entry(
    *,
    stable_id: str,
    manifest_sha384s: Sequence[str],
) -> dict[str, Any]:
    """Build one membership index entry."""

    entry = {
        "manifest_sha384s": _normalize_sha384_sequence(
            manifest_sha384s,
            "manifest_sha384s",
            max_count=MAX_MANIFESTS_PER_MEMBERSHIP_ENTRY,
        ),
        "stable_id": _required_str_value(stable_id, "stable_id"),
    }
    return validate_membership_index_entry(entry)


def validate_membership_index_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one membership index entry."""

    _reject_unsafe_json_tree(entry)
    normalized = dict(entry)
    _require_exact_fields(normalized, _MEMBERSHIP_ENTRY_FIELDS, "atlas_slice_membership_entry_fields_invalid")
    stable_id = _required_str(normalized, "stable_id")
    manifests = _normalize_sha384_sequence(
        normalized.get("manifest_sha384s"),
        "manifest_sha384s",
        max_count=MAX_MANIFESTS_PER_MEMBERSHIP_ENTRY,
    )
    return {"manifest_sha384s": manifests, "stable_id": stable_id}


def validate_membership_index(index: Mapping[str, Any]) -> dict[str, list[str]]:
    """Validate a membership index mapping stable_id to manifest digests."""

    _reject_unsafe_json_tree(index)
    if len(index) > MAX_MEMBERSHIP_INDEX_ENTRIES:
        raise AtlasSliceReconcileError("atlas_slice_membership_index_too_many_entries")
    normalized: dict[str, list[str]] = {}
    for stable_id, manifests in index.items():
        entry = validate_membership_index_entry(
            {"manifest_sha384s": manifests, "stable_id": stable_id}
        )
        normalized[entry["stable_id"]] = entry["manifest_sha384s"]
    return dict(sorted(normalized.items()))


def build_chunk_digest(entries: Sequence[Mapping[str, Any]]) -> str:
    """Return SHA-384 of a sorted chunk entry list."""

    normalized = _normalize_chunk_entries(entries)
    return _sha384_json_array(normalized)


def _validate_categorical_fields(record: Mapping[str, Any]) -> None:
    if record.get("privacy_class") not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSliceReconcileError("atlas_slice_install_record_privacy_class_invalid")
    if record.get("signer_authority_class") not in ALLOWED_SIGNER_AUTHORITY_CLASSES:
        raise AtlasSliceReconcileError("atlas_slice_install_record_signer_authority_class_invalid")
    if record.get("reconcile_state") not in ALLOWED_RECONCILE_STATES:
        raise AtlasSliceReconcileError("atlas_slice_install_record_reconcile_state_invalid")
    if record.get("authority_precedence_level") not in ALLOWED_AUTHORITY_PRECEDENCE_LEVELS:
        raise AtlasSliceReconcileError("atlas_slice_install_record_authority_precedence_invalid")
    _required_str(record, "slice_id")
    _required_str(record, "projection_query_id")


def _validate_digest_field_names(record: Mapping[str, Any]) -> None:
    if record.get("node_commitment_digest_field") != NODE_COMMITMENT_DIGEST_FIELD:
        raise AtlasSliceReconcileError("atlas_slice_install_record_node_digest_field_invalid")
    if record.get("edge_commitment_digest_field") != EDGE_COMMITMENT_DIGEST_FIELD:
        raise AtlasSliceReconcileError("atlas_slice_install_record_edge_digest_field_invalid")
    if record.get("content_commitment_digest_field") != CONTENT_COMMITMENT_DIGEST_FIELD:
        raise AtlasSliceReconcileError("atlas_slice_install_record_content_digest_field_invalid")


def _normalize_non_claims(value: Any) -> dict[str, bool]:
    if value is None:
        claims = dict(RECONCILE_NON_CLAIMS)
    elif isinstance(value, Mapping):
        claims = dict(value)
    else:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_non_claims_invalid")
    _require_exact_fields(claims, frozenset(RECONCILE_NON_CLAIMS), "atlas_slice_reconcile_non_claims_fields_invalid")
    if any(claims[key] is not True for key in RECONCILE_NON_CLAIMS):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_non_claims_not_true")
    return dict(RECONCILE_NON_CLAIMS)


def _standard_non_claims() -> dict[str, bool]:
    return dict(RECONCILE_NON_CLAIMS)


def _normalize_sha384_sequence(value: Any, label: str, *, max_count: int) -> list[str]:
    values = _normalize_str_sequence(value, label, max_count=max_count)
    for item in values:
        _require_sha384(item, f"atlas_slice_reconcile_{label}_sha384_invalid")
    return values


def _normalize_str_sequence(value: Any, label: str, *, max_count: int) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise AtlasSliceReconcileError(f"atlas_slice_reconcile_{label}_invalid")
    if len(value) > max_count:
        raise AtlasSliceReconcileError(f"atlas_slice_reconcile_{label}_too_many")
    normalized = []
    for item in value:
        normalized.append(_required_str_value(item, f"{label}_item"))
    if len(set(normalized)) != len(normalized):
        raise AtlasSliceReconcileError(f"atlas_slice_reconcile_{label}_duplicate")
    return sorted(dict.fromkeys(normalized))


def _validate_receipt_semantics(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema_version") != ATLAS_SLICE_RECONCILE_RECEIPT_SCHEMA_VERSION:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_schema_version_invalid")
    if receipt.get("phase") != ATLAS_SLICE_RECONCILE_PHASE:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_phase_invalid")
    if receipt.get("read_only") is not True:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_read_only_invalid")
    if receipt.get("verdict") != "pass":
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_verdict_invalid")
    if receipt.get("tokens") != list(RECONCILE_OUTPUT_TOKENS):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_tokens_invalid")
    _normalize_non_claims(receipt.get("non_claims"))
    _validate_timestamp(receipt.get("generated_at_utc"))
    if receipt.get("generated_at_source") not in {"caller_supplied", "wall_clock_utc"}:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_generated_at_source_invalid")
    _require_sha384(receipt.get("registry_sha384"), "atlas_slice_reconcile_receipt_registry_sha384_invalid")
    counts = receipt.get("counts")
    if not isinstance(counts, Mapping):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_counts_invalid")
    _require_exact_fields(counts, _RECEIPT_COUNT_FIELDS, "atlas_slice_reconcile_receipt_counts_fields_invalid")
    total_states = 0
    for key in sorted(_RECEIPT_COUNT_FIELDS):
        value = counts[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_count_invalid")
        if key != "records":
            total_states += value
    if counts["records"] != total_states:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_receipt_counts_mismatch")


def _normalize_chunk_entries(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise AtlasSliceReconcileError("atlas_slice_chunk_entries_invalid")
    normalized = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise AtlasSliceReconcileError("atlas_slice_chunk_entry_not_object")
        _require_exact_fields(dict(entry), frozenset({"content_id", "sha384", "size_bytes"}), "atlas_slice_chunk_entry_fields_invalid")
        content_id = _required_str(entry, "content_id")
        _require_sha384(entry.get("sha384"), "atlas_slice_chunk_entry_sha384_invalid")
        size = entry.get("size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise AtlasSliceReconcileError("atlas_slice_chunk_entry_size_invalid")
        normalized.append({"content_id": content_id, "sha384": entry["sha384"], "size_bytes": size})
    return sorted(normalized, key=lambda row: (row["content_id"], row["sha384"], row["size_bytes"]))


def _registry_counts(registry: Mapping[str, Any]) -> dict[str, int]:
    records = registry.get("records", [])
    states = {state: 0 for state in sorted(ALLOWED_RECONCILE_STATES)}
    for record in records:
        states[str(record["reconcile_state"])] += 1
    return {"records": len(records), **states}


def _write_json_atomic(
    path: str | Path,
    payload: Mapping[str, Any],
    *,
    allowed_root: str | Path | None,
    token_prefix: str,
) -> Path:
    _reject_unsafe_json_tree(payload)
    target = Path(path)
    if allowed_root is not None:
        root = Path(allowed_root).resolve()
        target_resolved = target.resolve()
        if target_resolved != root and root not in target_resolved.parents:
            raise AtlasSliceReconcileError(f"{token_prefix}_path_outside_allowed_root")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    text = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            os.chmod(tmp, 0o600)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def _reject_unsafe_json_tree(value: Any, *, _depth: int = 0) -> None:
    if _depth > MAX_JSON_DEPTH:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_json_depth_exceeded")
    if isinstance(value, float):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise AtlasSliceReconcileError("atlas_slice_reconcile_string_too_long")
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise AtlasSliceReconcileError("atlas_slice_reconcile_key_not_string")
            _reject_unsafe_json_tree(key, _depth=_depth + 1)
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)
        return
    if value is None or isinstance(value, (bool, int)):
        return
    raise AtlasSliceReconcileError("atlas_slice_reconcile_json_scalar_invalid")


def _validate_timestamp_or_pending(value: Any) -> None:
    if value == "pending":
        return
    _validate_timestamp(value)


def _validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_timestamp_invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_timestamp_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise AtlasSliceReconcileError("atlas_slice_reconcile_timestamp_not_utc")


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    return _required_str_value(payload.get(key), key)


def _required_str_value(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AtlasSliceReconcileError(f"atlas_slice_reconcile_required_string_invalid:{label}")
    if len(value) > MAX_STRING_LENGTH:
        raise AtlasSliceReconcileError(f"atlas_slice_reconcile_string_too_long:{label}")
    return value


def _require_sha384(value: Any, token: str) -> None:
    if not isinstance(value, str) or len(value) != 96 or any(char not in _HEX_96 for char in value):
        raise AtlasSliceReconcileError(token)


def _require_exact_fields(payload: Mapping[str, Any], fields: frozenset[str], token: str) -> None:
    if set(payload) != set(fields):
        raise AtlasSliceReconcileError(token)


def _sha384_canonical(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(canonical.encode("utf-8")) > MAX_REGISTRY_JSON_BYTES:
        raise AtlasSliceReconcileError("atlas_slice_reconcile_json_too_large")
    return hashlib.sha384(canonical.encode("utf-8")).hexdigest()


def _sha384_json_array(payload: Sequence[Mapping[str, Any]]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha384(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "ALLOWED_AUTHORITY_PRECEDENCE_LEVELS",
    "ALLOWED_BOUNDED_QUERY_TYPES",
    "ALLOWED_RECONCILE_STATES",
    "ATLAS_SLICE_RECONCILE_CHUNK_FORMAT_TOKEN",
    "ATLAS_SLICE_RECONCILE_MEMBERSHIP_INDEX_TOKEN",
    "ATLAS_SLICE_RECONCILE_NO_WRITE_TOKEN",
    "ATLAS_SLICE_RECONCILE_OPEN_ITEMS_TOKEN",
    "ATLAS_SLICE_RECONCILE_PHASE",
    "ATLAS_SLICE_RECONCILE_RECEIPT_SCHEMA_VERSION",
    "ATLAS_SLICE_RECONCILE_REGISTRY_LOCATION_TOKEN",
    "ATLAS_SLICE_RECONCILE_SCHEMA_VERSION",
    "ATLAS_SLICE_RECONCILE_TOKEN",
    "AUTHORITY_PRECEDENCE_ORDER",
    "CONTENT_COMMITMENT_DIGEST_FIELD",
    "DEFAULT_REGISTRY_PATH",
    "EDGE_COMMITMENT_DIGEST_FIELD",
    "MAX_CHUNK_DIGESTS_PER_RECORD",
    "MAX_DEPENDENCY_MANIFESTS_PER_RECORD",
    "MAX_JSON_DEPTH",
    "MAX_MANIFESTS_PER_MEMBERSHIP_ENTRY",
    "MAX_MEMBERSHIP_INDEX_ENTRIES",
    "MAX_RECORDS_PER_REGISTRY",
    "MAX_REGISTRY_JSON_BYTES",
    "MAX_STRING_LENGTH",
    "NODE_COMMITMENT_DIGEST_FIELD",
    "RECONCILE_NON_CLAIMS",
    "RECONCILE_OUTPUT_TOKENS",
    "AtlasSliceReconcileError",
    "build_chunk_digest",
    "build_install_record",
    "build_membership_index_entry",
    "build_reconcile_receipt",
    "build_reconcile_registry",
    "load_reconcile_registry",
    "validate_install_record",
    "validate_membership_index",
    "validate_membership_index_entry",
    "validate_reconcile_receipt",
    "validate_reconcile_registry",
    "write_reconcile_receipt",
    "write_reconcile_registry",
]
