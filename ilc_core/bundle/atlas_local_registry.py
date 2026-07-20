# SPDX-License-Identifier: AGPL-3.0-only
"""Local Atlas installed-slice registry helpers for Window 1576.

This module tracks local slice state above the reconcile registry. It does not
write LMDB, fetch from the network, install manifests, grant roles, clear
guards, mint, settle, write wallets, activate sidecars, or transition epochs.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.bundle.atlas_slice_reconcile import (
    DEFAULT_REGISTRY_PATH,
    AtlasSliceReconcileError,
    MAX_JSON_DEPTH,
    MAX_MEMBERSHIP_INDEX_ENTRIES,
    MAX_RECORDS_PER_REGISTRY,
    MAX_REGISTRY_JSON_BYTES,
    MAX_STRING_LENGTH,
    RECONCILE_NON_CLAIMS,
    validate_install_record,
    validate_reconcile_registry,
)
from ilc_core.bundle.atlas_slice_schema import ALLOWED_PRIVACY_CLASSES


ATLAS_LOCAL_REGISTRY_SCHEMA_VERSION = "atlas_local_registry_1576_fix9.v0.1"
ATLAS_LOCAL_REGISTRY_RECEIPT_SCHEMA_VERSION = (
    "atlas_local_registry_status_receipt_1576_fix9.v0.1"
)
ATLAS_LOCAL_REGISTRY_PHASE = "1576-fix9"
ATLAS_LOCAL_REGISTRY_KIND = "atlas_local_registry"
DEFAULT_LOCAL_REGISTRY_PATH = Path("out/installed_slice_registry/local_registry.json")
DEFAULT_LOCAL_CONTENT_ROOT = Path("out/installed_slice_registry/content")

ATLAS_LOCAL_REGISTRY_MODULE_TOKEN = "atlas_local_registry_module_committed_phase_1576_fix9"
ATLAS_LOCAL_REGISTRY_CLI_TOKEN = "atlas_local_registry_cli_committed_phase_1576_fix9"
ATLAS_LOCAL_REGISTRY_TESTS_TOKEN = "atlas_local_registry_tests_committed_phase_1576_fix9"
ATLAS_LOCAL_REGISTRY_NO_WRITE_TOKEN = (
    "atlas_local_registry_no_lmdb_no_network_no_role_phase_1576_fix9"
)
ATLAS_LOCAL_REGISTRY_OUTPUT_TOKENS = (
    ATLAS_LOCAL_REGISTRY_MODULE_TOKEN,
    ATLAS_LOCAL_REGISTRY_CLI_TOKEN,
    ATLAS_LOCAL_REGISTRY_TESTS_TOKEN,
    ATLAS_LOCAL_REGISTRY_NO_WRITE_TOKEN,
)

LOCAL_REGISTRY_NON_CLAIMS = {
    **RECONCILE_NON_CLAIMS,
    "no_manifest_install": True,
    "no_manifest_publication": True,
    "no_network_discovery": True,
}

ALLOWED_CONTENT_AVAILABILITY_STATUS = frozenset(
    {
        "all_present",
        "none_checked",
        "partial",
    }
)
ALLOWED_COVERAGE_STATES = frozenset({"covered", "partial", "unresolved"})
ALLOWED_CONTENT_VERIFICATION_STATUS = frozenset({"failed", "not_checked", "verified"})
ALLOWED_PENDING_RECORD_KINDS = frozenset({"content", "edge", "hyperedge", "node"})

MAX_CONTENT_AVAILABILITY_ENTRIES = 10_000
MAX_PENDING_OVERLAY_ENTRIES = 500
MAX_OVERLAY_FIELDS = 32
MAX_LOCAL_CONTENT_BYTES = 128 * 1024 * 1024
MAX_TOTAL_CONTENT_CHECK_BYTES = 1024 * 1024 * 1024

_HEX_96 = frozenset("0123456789abcdef")
_INSTALLED_SLICE_RECORD_FIELDS = frozenset({"install_record", "local_metadata"})
_LOCAL_METADATA_FIELDS = frozenset(
    {
        "content_availability_status",
        "local_content_root",
        "local_path",
        "local_path_verified",
    }
)
_MEMBERSHIP_COVERAGE_FIELDS = frozenset(
    {"coverage_state", "manifest_sha384s", "stable_id"}
)
_CONTENT_AVAILABILITY_FIELDS = frozenset(
    {
        "available",
        "content_id",
        "local_content_root",
        "local_path",
        "sha384",
        "verification_status",
        "verified_at_utc",
    }
)
_PENDING_OVERLAY_FIELDS = frozenset(
    {
        "fields",
        "overlay_id",
        "privacy_class",
        "record_kind",
        "slice_id",
        "staged_at_epoch",
    }
)
_LOCAL_REGISTRY_FIELDS = frozenset(
    {
        "content_availability",
        "counts",
        "installed_slices",
        "local_registry_body_sha384",
        "local_registry_kind",
        "local_registry_schema_version",
        "membership_coverage",
        "non_claims",
        "pending_local_overlay",
    }
)
_RECEIPT_FIELDS = frozenset(
    {
        "check_availability",
        "counts",
        "generated_at_source",
        "generated_at_utc",
        "local_registry_sha384",
        "non_claims",
        "phase",
        "read_only",
        "receipt_body_sha384",
        "receipt_id",
        "schema_version",
        "tokens",
        "verdict",
    }
)
_RECEIPT_COUNT_FIELDS = frozenset(
    {
        "available_content",
        "content_availability",
        "installed_slices",
        "membership_coverage",
        "pending_local_overlay",
        "unavailable_content",
    }
)
_RECEIPT_PREFIX = "atlas_local_registry_receipt:"


class AtlasLocalRegistryError(ValueError):
    """Stable local registry error."""


def build_installed_slice_record(
    *,
    install_record: Mapping[str, Any],
    local_content_root: str | Path = DEFAULT_LOCAL_CONTENT_ROOT,
    local_path: str = "",
    local_path_verified: bool = False,
    content_availability_status: str = "none_checked",
) -> dict[str, Any]:
    """Build one installed-slice local record without mutating reconcile fields."""

    metadata = {
        "content_availability_status": content_availability_status,
        "local_content_root": _normalize_root(local_content_root),
        "local_path": local_path,
        "local_path_verified": local_path_verified,
    }
    return validate_installed_slice_record(
        {"install_record": dict(install_record), "local_metadata": metadata}
    )


def validate_installed_slice_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an installed-slice local record."""

    _reject_unsafe_json_tree(record)
    normalized = dict(record)
    _require_exact_fields(
        normalized,
        _INSTALLED_SLICE_RECORD_FIELDS,
        "atlas_local_registry_installed_slice_fields_invalid",
    )
    try:
        install_record = validate_install_record(normalized["install_record"])
    except AtlasSliceReconcileError as exc:
        raise AtlasLocalRegistryError(str(exc)) from exc
    metadata = _validate_local_metadata(normalized["local_metadata"])
    return {"install_record": install_record, "local_metadata": metadata}


def build_membership_coverage_entry(
    *,
    stable_id: str,
    manifest_sha384s: Sequence[str],
    coverage_state: str,
) -> dict[str, Any]:
    """Build one membership coverage row."""

    return validate_membership_coverage_entry(
        {
            "coverage_state": coverage_state,
            "manifest_sha384s": list(manifest_sha384s),
            "stable_id": stable_id,
        }
    )


def validate_membership_coverage_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one membership coverage row."""

    _reject_unsafe_json_tree(entry)
    normalized = dict(entry)
    _require_exact_fields(
        normalized,
        _MEMBERSHIP_COVERAGE_FIELDS,
        "atlas_local_registry_membership_coverage_fields_invalid",
    )
    stable_id = _required_str(normalized, "stable_id")
    coverage_state = _required_str(normalized, "coverage_state")
    if coverage_state not in ALLOWED_COVERAGE_STATES:
        raise AtlasLocalRegistryError("atlas_local_registry_coverage_state_invalid")
    return {
        "coverage_state": coverage_state,
        "manifest_sha384s": _normalize_sha384s(
            normalized.get("manifest_sha384s"),
            "membership_manifest_sha384s",
            max_count=MAX_RECORDS_PER_REGISTRY,
        ),
        "stable_id": stable_id,
    }


def build_content_availability_record(
    *,
    content_id: str,
    sha384: str,
    local_content_root: str | Path = DEFAULT_LOCAL_CONTENT_ROOT,
    local_path: str = "",
    available: bool = False,
    verification_status: str = "not_checked",
    verified_at_utc: str = "never",
) -> dict[str, Any]:
    """Build one content availability row."""

    return validate_content_availability_record(
        {
            "available": available,
            "content_id": content_id,
            "local_content_root": _normalize_root(local_content_root),
            "local_path": local_path,
            "sha384": sha384,
            "verification_status": verification_status,
            "verified_at_utc": verified_at_utc,
        }
    )


def validate_content_availability_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one content availability row."""

    _reject_unsafe_json_tree(record)
    normalized = dict(record)
    _require_exact_fields(
        normalized,
        _CONTENT_AVAILABILITY_FIELDS,
        "atlas_local_registry_content_availability_fields_invalid",
    )
    root = _normalize_root(normalized["local_content_root"])
    local_path = _normalize_relative_path(
        normalized.get("local_path"),
        root=root,
        token_prefix="atlas_local_registry_content_path",
        allow_empty=True,
    )
    if type(normalized.get("available")) is not bool:
        raise AtlasLocalRegistryError("atlas_local_registry_content_available_invalid")
    verification_status = _required_str(normalized, "verification_status")
    if verification_status not in ALLOWED_CONTENT_VERIFICATION_STATUS:
        raise AtlasLocalRegistryError("atlas_local_registry_content_verification_status_invalid")
    available = normalized["available"]
    verified_at = normalized.get("verified_at_utc")
    if verified_at != "never":
        _validate_timestamp(verified_at)
    if verification_status == "verified":
        if available is not True or verified_at == "never":
            raise AtlasLocalRegistryError("atlas_local_registry_content_state_inconsistent")
    elif verification_status == "not_checked":
        if available is not False or verified_at != "never":
            raise AtlasLocalRegistryError("atlas_local_registry_content_state_inconsistent")
    elif available is not False or verified_at == "never":
        raise AtlasLocalRegistryError("atlas_local_registry_content_state_inconsistent")
    _require_sha384(normalized.get("sha384"), "atlas_local_registry_content_sha384_invalid")
    return {
        "available": available,
        "content_id": _required_str(normalized, "content_id"),
        "local_content_root": root,
        "local_path": local_path,
        "sha384": normalized["sha384"],
        "verification_status": verification_status,
        "verified_at_utc": verified_at,
    }


def build_pending_overlay_record(
    *,
    overlay_id: str,
    slice_id: str,
    record_kind: str,
    privacy_class: str,
    staged_at_epoch: int,
    fields: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one pending local overlay row."""

    return validate_pending_overlay_record(
        {
            "fields": dict(fields),
            "overlay_id": overlay_id,
            "privacy_class": privacy_class,
            "record_kind": record_kind,
            "slice_id": slice_id,
            "staged_at_epoch": staged_at_epoch,
        }
    )


def validate_pending_overlay_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one pending local overlay row."""

    _reject_unsafe_json_tree(record)
    normalized = dict(record)
    _require_exact_fields(
        normalized,
        _PENDING_OVERLAY_FIELDS,
        "atlas_local_registry_pending_overlay_fields_invalid",
    )
    record_kind = _required_str(normalized, "record_kind")
    if record_kind not in ALLOWED_PENDING_RECORD_KINDS:
        raise AtlasLocalRegistryError("atlas_local_registry_pending_record_kind_invalid")
    privacy_class = _required_str(normalized, "privacy_class")
    if privacy_class not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasLocalRegistryError("atlas_local_registry_pending_privacy_class_invalid")
    staged_at_epoch = normalized.get("staged_at_epoch")
    if type(staged_at_epoch) is not int or staged_at_epoch < 0:
        raise AtlasLocalRegistryError("atlas_local_registry_pending_epoch_invalid")
    fields = normalized.get("fields")
    if not isinstance(fields, Mapping):
        raise AtlasLocalRegistryError("atlas_local_registry_pending_fields_invalid")
    if len(fields) > MAX_OVERLAY_FIELDS:
        raise AtlasLocalRegistryError("atlas_local_registry_pending_fields_too_many")
    return {
        "fields": dict(sorted(fields.items())),
        "overlay_id": _required_str(normalized, "overlay_id"),
        "privacy_class": privacy_class,
        "record_kind": record_kind,
        "slice_id": _required_str(normalized, "slice_id"),
        "staged_at_epoch": staged_at_epoch,
    }


def build_local_registry(
    *,
    installed_slices: Sequence[Mapping[str, Any]],
    membership_coverage: Sequence[Mapping[str, Any]],
    content_availability: Sequence[Mapping[str, Any]],
    pending_local_overlay: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic local registry."""

    slices = _normalize_installed_slices(installed_slices)
    membership = _normalize_membership_coverage(membership_coverage)
    availability = _normalize_content_availability(content_availability)
    overlays = _normalize_pending_overlay(pending_local_overlay)
    body = {
        "content_availability": availability,
        "counts": _counts(slices, membership, availability, overlays),
        "installed_slices": slices,
        "local_registry_kind": ATLAS_LOCAL_REGISTRY_KIND,
        "local_registry_schema_version": ATLAS_LOCAL_REGISTRY_SCHEMA_VERSION,
        "membership_coverage": membership,
        "non_claims": _standard_non_claims(),
        "pending_local_overlay": overlays,
    }
    return {**body, "local_registry_body_sha384": _sha384_canonical(body)}


def validate_local_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize a local registry."""

    _reject_unsafe_json_tree(registry)
    normalized = dict(registry)
    _require_exact_fields(
        normalized,
        _LOCAL_REGISTRY_FIELDS,
        "atlas_local_registry_fields_invalid",
    )
    if normalized.get("local_registry_schema_version") != ATLAS_LOCAL_REGISTRY_SCHEMA_VERSION:
        raise AtlasLocalRegistryError("atlas_local_registry_schema_version_invalid")
    if normalized.get("local_registry_kind") != ATLAS_LOCAL_REGISTRY_KIND:
        raise AtlasLocalRegistryError("atlas_local_registry_kind_invalid")
    expected = build_local_registry(
        installed_slices=normalized["installed_slices"],
        membership_coverage=normalized["membership_coverage"],
        content_availability=normalized["content_availability"],
        pending_local_overlay=normalized["pending_local_overlay"],
    )
    if normalized.get("counts") != expected["counts"]:
        raise AtlasLocalRegistryError("atlas_local_registry_counts_mismatch")
    if normalized.get("local_registry_body_sha384") != expected["local_registry_body_sha384"]:
        raise AtlasLocalRegistryError("atlas_local_registry_sha384_mismatch")
    _normalize_non_claims(normalized.get("non_claims"))
    return expected


def load_local_registry(path: str | Path) -> dict[str, Any]:
    """Load a bounded local registry JSON file."""

    source = Path(path)
    if not source.exists():
        raise AtlasLocalRegistryError("atlas_local_registry_missing")
    if source.stat().st_size > MAX_REGISTRY_JSON_BYTES:
        raise AtlasLocalRegistryError("atlas_local_registry_json_too_large")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AtlasLocalRegistryError("atlas_local_registry_json_invalid") from exc
    if not isinstance(payload, Mapping):
        raise AtlasLocalRegistryError("atlas_local_registry_not_object")
    return validate_local_registry(payload)


def write_local_registry(
    path: str | Path,
    registry: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write a local registry JSON file."""

    return _write_json_atomic(
        path,
        validate_local_registry(registry),
        allowed_root=allowed_root,
        token_prefix="atlas_local_registry",
    )


def check_content_availability(
    record: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Verify one local content record by SHA-384 when the file is present."""

    checked = validate_content_availability_record(record)
    if checked["local_path"] == "":
        return {
            **checked,
            "available": False,
            "verification_status": "not_checked",
            "verified_at_utc": "never",
        }
    path = _resolve_within_root(
        root=checked["local_content_root"],
        local_path=checked["local_path"],
        token_prefix="atlas_local_registry_content_path",
    )
    if not path.exists() or not path.is_file():
        return {
            **checked,
            "available": False,
            "verification_status": "failed",
            "verified_at_utc": _timestamp_or_now(generated_at_utc),
        }
    if path.stat().st_size > MAX_LOCAL_CONTENT_BYTES:
        raise AtlasLocalRegistryError("atlas_local_registry_content_file_too_large")
    actual = hashlib.sha384(path.read_bytes()).hexdigest()
    status = "verified" if actual == checked["sha384"] else "failed"
    return {
        **checked,
        "available": actual == checked["sha384"],
        "verification_status": status,
        "verified_at_utc": _timestamp_or_now(generated_at_utc),
    }


def check_content_availability_records(
    records: Sequence[Mapping[str, Any]],
    *,
    generated_at_utc: str | None = None,
) -> list[dict[str, Any]]:
    """Verify content rows while enforcing a total local-read byte budget."""

    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_invalid")
    if len(records) > MAX_CONTENT_AVAILABILITY_ENTRIES:
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_too_many")
    checked_records = []
    total_bytes = 0
    for record in records:
        checked = validate_content_availability_record(record)
        if checked["local_path"]:
            path = _resolve_within_root(
                root=checked["local_content_root"],
                local_path=checked["local_path"],
                token_prefix="atlas_local_registry_content_path",
            )
            if path.exists() and path.is_file():
                size_bytes = path.stat().st_size
                if size_bytes > MAX_LOCAL_CONTENT_BYTES:
                    raise AtlasLocalRegistryError("atlas_local_registry_content_file_too_large")
                total_bytes += size_bytes
                if total_bytes > MAX_TOTAL_CONTENT_CHECK_BYTES:
                    raise AtlasLocalRegistryError("atlas_local_registry_content_check_bytes_exceeded")
        checked_records.append(
            check_content_availability(record, generated_at_utc=generated_at_utc)
        )
    return checked_records


def build_local_registry_status_receipt(
    registry: Mapping[str, Any],
    *,
    generated_at_utc: str | None = None,
    check_availability: bool = False,
) -> dict[str, Any]:
    """Build a deterministic local-registry status receipt."""

    generated_at_source = "caller_supplied"
    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        generated_at_source = "wall_clock_utc"
    _validate_timestamp(generated_at_utc)
    validated = validate_local_registry(registry)
    body = {
        "check_availability": check_availability,
        "counts": validated["counts"],
        "generated_at_source": generated_at_source,
        "generated_at_utc": generated_at_utc,
        "local_registry_sha384": validated["local_registry_body_sha384"],
        "non_claims": _standard_non_claims(),
        "phase": ATLAS_LOCAL_REGISTRY_PHASE,
        "read_only": True,
        "schema_version": ATLAS_LOCAL_REGISTRY_RECEIPT_SCHEMA_VERSION,
        "tokens": list(ATLAS_LOCAL_REGISTRY_OUTPUT_TOKENS),
        "verdict": "pass",
    }
    body_sha384 = _sha384_canonical(body)
    return {
        **body,
        "receipt_body_sha384": body_sha384,
        "receipt_id": f"{_RECEIPT_PREFIX}{body_sha384}",
    }


def validate_local_registry_status_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a local-registry status receipt."""

    _reject_unsafe_json_tree(receipt)
    normalized = dict(receipt)
    _require_exact_fields(
        normalized,
        _RECEIPT_FIELDS,
        "atlas_local_registry_receipt_fields_invalid",
    )
    _validate_receipt_semantics(normalized)
    body = {
        key: normalized[key]
        for key in sorted(_RECEIPT_FIELDS - {"receipt_body_sha384", "receipt_id"})
    }
    expected_sha384 = _sha384_canonical(body)
    if normalized.get("receipt_body_sha384") != expected_sha384:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_sha384_mismatch")
    if normalized.get("receipt_id") != f"{_RECEIPT_PREFIX}{expected_sha384}":
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_id_mismatch")
    return normalized


def write_local_registry_status_receipt(
    path: str | Path,
    receipt: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write a local-registry status receipt JSON file."""

    return _write_json_atomic(
        path,
        validate_local_registry_status_receipt(receipt),
        allowed_root=allowed_root,
        token_prefix="atlas_local_registry_receipt",
    )


def _validate_local_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, Mapping):
        raise AtlasLocalRegistryError("atlas_local_registry_local_metadata_invalid")
    normalized = dict(metadata)
    _require_exact_fields(
        normalized,
        _LOCAL_METADATA_FIELDS,
        "atlas_local_registry_local_metadata_fields_invalid",
    )
    root = _normalize_root(normalized["local_content_root"])
    local_path = _normalize_relative_path(
        normalized.get("local_path"),
        root=root,
        token_prefix="atlas_local_registry_installed_slice_path",
        allow_empty=True,
    )
    if type(normalized.get("local_path_verified")) is not bool:
        raise AtlasLocalRegistryError("atlas_local_registry_local_path_verified_invalid")
    status = _required_str(normalized, "content_availability_status")
    if status not in ALLOWED_CONTENT_AVAILABILITY_STATUS:
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_status_invalid")
    return {
        "content_availability_status": status,
        "local_content_root": root,
        "local_path": local_path,
        "local_path_verified": normalized["local_path_verified"],
    }


def _normalize_installed_slices(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasLocalRegistryError("atlas_local_registry_installed_slices_invalid")
    if len(records) > MAX_RECORDS_PER_REGISTRY:
        raise AtlasLocalRegistryError("atlas_local_registry_installed_slices_too_many")
    normalized = [validate_installed_slice_record(record) for record in records]
    manifest_ids = [record["install_record"]["manifest_sha384"] for record in normalized]
    if len(set(manifest_ids)) != len(manifest_ids):
        raise AtlasLocalRegistryError("atlas_local_registry_installed_slice_duplicate")
    return sorted(normalized, key=lambda record: record["install_record"]["manifest_sha384"])


def _normalize_membership_coverage(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasLocalRegistryError("atlas_local_registry_membership_coverage_invalid")
    if len(records) > MAX_MEMBERSHIP_INDEX_ENTRIES:
        raise AtlasLocalRegistryError("atlas_local_registry_membership_coverage_too_many")
    normalized = [validate_membership_coverage_entry(record) for record in records]
    stable_ids = [record["stable_id"] for record in normalized]
    if len(set(stable_ids)) != len(stable_ids):
        raise AtlasLocalRegistryError("atlas_local_registry_membership_coverage_duplicate")
    return sorted(normalized, key=lambda record: record["stable_id"])


def _normalize_content_availability(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_invalid")
    if len(records) > MAX_CONTENT_AVAILABILITY_ENTRIES:
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_too_many")
    normalized = [validate_content_availability_record(record) for record in records]
    content_ids = [record["content_id"] for record in normalized]
    if len(set(content_ids)) != len(content_ids):
        raise AtlasLocalRegistryError("atlas_local_registry_content_availability_duplicate")
    return sorted(normalized, key=lambda record: record["content_id"])


def _normalize_pending_overlay(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise AtlasLocalRegistryError("atlas_local_registry_pending_overlay_invalid")
    if len(records) > MAX_PENDING_OVERLAY_ENTRIES:
        raise AtlasLocalRegistryError("atlas_local_registry_pending_overlay_too_many")
    normalized = [validate_pending_overlay_record(record) for record in records]
    overlay_ids = [record["overlay_id"] for record in normalized]
    if len(set(overlay_ids)) != len(overlay_ids):
        raise AtlasLocalRegistryError("atlas_local_registry_pending_overlay_duplicate")
    return sorted(normalized, key=lambda record: record["overlay_id"])


def _counts(
    installed_slices: Sequence[Mapping[str, Any]],
    membership_coverage: Sequence[Mapping[str, Any]],
    content_availability: Sequence[Mapping[str, Any]],
    pending_local_overlay: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    available = sum(1 for record in content_availability if record["available"] is True)
    return {
        "available_content": available,
        "content_availability": len(content_availability),
        "installed_slices": len(installed_slices),
        "membership_coverage": len(membership_coverage),
        "pending_local_overlay": len(pending_local_overlay),
        "unavailable_content": len(content_availability) - available,
    }


def _normalize_non_claims(value: Any) -> dict[str, bool]:
    if value is None:
        claims = dict(LOCAL_REGISTRY_NON_CLAIMS)
    elif isinstance(value, Mapping):
        claims = dict(value)
    else:
        raise AtlasLocalRegistryError("atlas_local_registry_non_claims_invalid")
    _require_exact_fields(
        claims,
        frozenset(LOCAL_REGISTRY_NON_CLAIMS),
        "atlas_local_registry_non_claims_fields_invalid",
    )
    if any(claims[key] is not True for key in LOCAL_REGISTRY_NON_CLAIMS):
        raise AtlasLocalRegistryError("atlas_local_registry_non_claims_not_true")
    return dict(LOCAL_REGISTRY_NON_CLAIMS)


def _standard_non_claims() -> dict[str, bool]:
    return dict(LOCAL_REGISTRY_NON_CLAIMS)


def _normalize_root(root: str | Path) -> str:
    if isinstance(root, Path):
        root_value = str(root)
    else:
        root_value = _required_str_value(root, "local_content_root")
    if len(root_value) > MAX_STRING_LENGTH:
        raise AtlasLocalRegistryError("atlas_local_registry_root_too_long")
    return root_value


def _normalize_relative_path(
    value: Any,
    *,
    root: str,
    token_prefix: str,
    allow_empty: bool,
) -> str:
    if value == "" and allow_empty:
        return ""
    local_path = _required_str_value(value, "local_path")
    _resolve_within_root(root=root, local_path=local_path, token_prefix=token_prefix)
    return local_path


def _resolve_within_root(*, root: str | Path, local_path: str, token_prefix: str) -> Path:
    root_resolved = Path(root).resolve()
    candidate = Path(local_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root_resolved / candidate).resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise AtlasLocalRegistryError(f"{token_prefix}_outside_root")
    return resolved


def _normalize_sha384s(value: Any, label: str, *, max_count: int) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise AtlasLocalRegistryError(f"atlas_local_registry_{label}_invalid")
    if len(value) > max_count:
        raise AtlasLocalRegistryError(f"atlas_local_registry_{label}_too_many")
    normalized = []
    for item in value:
        _require_sha384(item, f"atlas_local_registry_{label}_sha384_invalid")
        normalized.append(item)
    if len(set(normalized)) != len(normalized):
        raise AtlasLocalRegistryError(f"atlas_local_registry_{label}_duplicate")
    return sorted(dict.fromkeys(normalized))


def _validate_receipt_semantics(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema_version") != ATLAS_LOCAL_REGISTRY_RECEIPT_SCHEMA_VERSION:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_schema_version_invalid")
    if receipt.get("phase") != ATLAS_LOCAL_REGISTRY_PHASE:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_phase_invalid")
    if receipt.get("read_only") is not True:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_read_only_invalid")
    if receipt.get("verdict") != "pass":
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_verdict_invalid")
    if type(receipt.get("check_availability")) is not bool:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_check_availability_invalid")
    if receipt.get("tokens") != list(ATLAS_LOCAL_REGISTRY_OUTPUT_TOKENS):
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_tokens_invalid")
    _normalize_non_claims(receipt.get("non_claims"))
    _validate_timestamp(receipt.get("generated_at_utc"))
    if receipt.get("generated_at_source") not in {"caller_supplied", "wall_clock_utc"}:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_generated_at_source_invalid")
    _require_sha384(receipt.get("local_registry_sha384"), "atlas_local_registry_receipt_registry_sha384_invalid")
    counts = receipt.get("counts")
    if not isinstance(counts, Mapping):
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_counts_invalid")
    _require_exact_fields(counts, _RECEIPT_COUNT_FIELDS, "atlas_local_registry_receipt_counts_fields_invalid")
    for key in sorted(_RECEIPT_COUNT_FIELDS):
        value = counts[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AtlasLocalRegistryError("atlas_local_registry_receipt_count_invalid")
    if counts["content_availability"] != counts["available_content"] + counts["unavailable_content"]:
        raise AtlasLocalRegistryError("atlas_local_registry_receipt_counts_mismatch")


def _validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasLocalRegistryError("atlas_local_registry_timestamp_invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasLocalRegistryError("atlas_local_registry_timestamp_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise AtlasLocalRegistryError("atlas_local_registry_timestamp_not_utc")


def _timestamp_or_now(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(value)
    return value


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    return _required_str_value(payload.get(key), key)


def _required_str_value(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AtlasLocalRegistryError(f"atlas_local_registry_required_string_invalid:{label}")
    if len(value) > MAX_STRING_LENGTH:
        raise AtlasLocalRegistryError(f"atlas_local_registry_string_too_long:{label}")
    return value


def _require_sha384(value: Any, token: str) -> None:
    if not isinstance(value, str) or len(value) != 96 or any(char not in _HEX_96 for char in value):
        raise AtlasLocalRegistryError(token)


def _require_exact_fields(payload: Mapping[str, Any], fields: frozenset[str], token: str) -> None:
    if set(payload) != set(fields):
        raise AtlasLocalRegistryError(token)


def _reject_unsafe_json_tree(value: Any, *, _depth: int = 0) -> None:
    if _depth > MAX_JSON_DEPTH:
        raise AtlasLocalRegistryError("atlas_local_registry_json_depth_exceeded")
    if isinstance(value, float):
        raise AtlasLocalRegistryError("atlas_local_registry_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise AtlasLocalRegistryError("atlas_local_registry_string_too_long")
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise AtlasLocalRegistryError("atlas_local_registry_key_not_string")
            _reject_unsafe_json_tree(key, _depth=_depth + 1)
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)
        return
    if value is None or isinstance(value, (bool, int)):
        return
    raise AtlasLocalRegistryError("atlas_local_registry_json_scalar_invalid")


def _sha384_canonical(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(canonical.encode("utf-8")) > MAX_REGISTRY_JSON_BYTES:
        raise AtlasLocalRegistryError("atlas_local_registry_json_too_large")
    return hashlib.sha384(canonical.encode("utf-8")).hexdigest()


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
            raise AtlasLocalRegistryError(f"{token_prefix}_path_outside_allowed_root")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    text = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


__all__ = [
    "ALLOWED_CONTENT_AVAILABILITY_STATUS",
    "ALLOWED_CONTENT_VERIFICATION_STATUS",
    "ALLOWED_COVERAGE_STATES",
    "ALLOWED_PENDING_RECORD_KINDS",
    "ATLAS_LOCAL_REGISTRY_OUTPUT_TOKENS",
    "ATLAS_LOCAL_REGISTRY_PHASE",
    "ATLAS_LOCAL_REGISTRY_RECEIPT_SCHEMA_VERSION",
    "ATLAS_LOCAL_REGISTRY_SCHEMA_VERSION",
    "DEFAULT_LOCAL_CONTENT_ROOT",
    "DEFAULT_LOCAL_REGISTRY_PATH",
    "DEFAULT_REGISTRY_PATH",
    "LOCAL_REGISTRY_NON_CLAIMS",
    "MAX_CONTENT_AVAILABILITY_ENTRIES",
    "MAX_LOCAL_CONTENT_BYTES",
    "MAX_PENDING_OVERLAY_ENTRIES",
    "MAX_TOTAL_CONTENT_CHECK_BYTES",
    "AtlasLocalRegistryError",
    "build_content_availability_record",
    "build_installed_slice_record",
    "build_local_registry",
    "build_local_registry_status_receipt",
    "build_membership_coverage_entry",
    "build_pending_overlay_record",
    "check_content_availability",
    "check_content_availability_records",
    "load_local_registry",
    "validate_content_availability_record",
    "validate_installed_slice_record",
    "validate_local_registry",
    "validate_local_registry_status_receipt",
    "validate_membership_coverage_entry",
    "validate_pending_overlay_record",
    "validate_reconcile_registry",
    "write_local_registry",
    "write_local_registry_status_receipt",
]
