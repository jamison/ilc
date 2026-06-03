# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 651 bounded public receipt runtime."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ilc_core.protocol.harness_interfaces import PublicReceiptStore


PUBLIC_RECEIPT_RUNTIME_VERSION = "public_receipt_runtime_651.v0.1"
PUBLIC_RECEIPT_SCHEMA_VERSION = "v0.1"

RECEIPT_CLASS_FIELDS: dict[str, tuple[str, ...]] = {
    "public_identity_activation_receipt": (
        "activated_agent_id",
        "admission_authority_scope",
        "stake_binding_ref_or_null",
    ),
    "public_namespace_authority_receipt": (
        "namespace_label",
        "bound_agent_id",
        "activation_receipt_ref",
    ),
    "public_quorum_eligibility_receipt": (
        "eligibility_subject_agent_id",
        "snapshot_or_epoch_root_ref",
        "proof_material_ref",
    ),
    "settlement_linked_public_legitimacy_receipt": (
        "settled_public_action_ref",
        "quorum_receipt_ref",
        "settlement_receipt_ref",
        "payout_or_attribution_ref",
    ),
}
RECEIPTS_WITH_REQUIRED_LINEAGE = {
    "public_identity_activation_receipt",
    "public_namespace_authority_receipt",
    "settlement_linked_public_legitimacy_receipt",
}
VALID_VERIFICATION_STATUSES = {"valid", "failed", "pending"}


class PublicReceiptRuntimeError(ValueError):
    """Fail-closed error with machine token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def issue_public_receipt(
    *,
    payload: dict[str, Any],
    store: PublicReceiptStore,
) -> dict[str, Any]:
    normalized = _normalize_payload(payload)
    receipt_id = _canonical_receipt_id(normalized)
    receipt = {"receipt_id": receipt_id, **normalized}
    store.put_receipt(receipt_id, receipt)
    return {
        "ok": True,
        "token": "receipt_issued",
        "receipt": receipt,
    }


def query_public_receipts(
    *,
    store: PublicReceiptStore,
    receipt_id: str | None = None,
    signer_agent_id: str | None = None,
    artifact_kind: str | None = None,
    epoch_id: str | None = None,
) -> dict[str, Any]:
    provided = sum(
        value is not None
        for value in (receipt_id, signer_agent_id, artifact_kind)
    )
    if provided != 1:
        raise PublicReceiptRuntimeError(
            "invalid_query_mode",
            "query must specify exactly one mode",
        )

    if receipt_id is not None:
        receipt = store.get_receipt(_require_non_empty_string(receipt_id, token="receipt_not_found"))
        if receipt is None:
            raise PublicReceiptRuntimeError("receipt_not_found", "receipt not found")
        return {
            "ok": True,
            "token": "receipt_query_result",
            "receipts": [_normalize_payload(receipt, verify_receipt_id=True)],
        }

    if signer_agent_id is not None:
        signer = _require_non_empty_string(signer_agent_id, token="signer_agent_id_required")
        return {
            "ok": True,
            "token": "receipt_query_result",
            "receipts": [
                _normalize_payload(receipt, verify_receipt_id=True)
                for receipt in store.get_receipts_by_signer(signer)
            ],
        }

    kind = _require_non_empty_string(artifact_kind, token="artifact_kind_required")
    if epoch_id is None:
        raise PublicReceiptRuntimeError("epoch_id_required", "epoch_id is required for artifact_kind queries")
    epoch = _require_non_empty_string(epoch_id, token="epoch_id_required")
    return {
        "ok": True,
        "token": "receipt_query_result",
        "receipts": [
            _normalize_payload(receipt, verify_receipt_id=True)
            for receipt in store.get_receipts_by_artifact_epoch(kind, epoch)
        ],
    }


def _normalize_payload(payload: dict[str, Any], *, verify_receipt_id: bool = False) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PublicReceiptRuntimeError("schema_mismatch", "receipt payload must be an object")

    artifact_kind = _require_non_empty_string(payload.get("artifact_kind"), token="schema_mismatch")
    if artifact_kind not in RECEIPT_CLASS_FIELDS:
        raise PublicReceiptRuntimeError("unsupported_receipt_class", "unsupported receipt class")

    schema_version = _require_non_empty_string(payload.get("schema_version"), token="version_mismatch")
    if schema_version != PUBLIC_RECEIPT_SCHEMA_VERSION:
        raise PublicReceiptRuntimeError("version_mismatch", "schema_version must be v0.1")

    signer_agent_id = _require_non_empty_string(payload.get("signer_agent_id"), token="schema_mismatch")
    authority_scope = _require_non_empty_string(payload.get("authority_scope"), token="missing_scope")
    epoch_id = _require_non_empty_string(payload.get("epoch_id"), token="schema_mismatch")
    verification_material_ref = _require_optional_string(
        payload.get("verification_material_ref"),
        token="missing_attestation",
    )
    if verification_material_ref is None:
        raise PublicReceiptRuntimeError("missing_attestation", "verification_material_ref is required")
    verification_status = _require_non_empty_string(payload.get("verification_status"), token="schema_mismatch")
    if verification_status not in VALID_VERIFICATION_STATUSES:
        raise PublicReceiptRuntimeError("schema_mismatch", "invalid verification_status")

    issued_at = payload.get("issued_at")
    if isinstance(issued_at, bool) or not isinstance(issued_at, int) or issued_at < 0:
        raise PublicReceiptRuntimeError("schema_mismatch", "issued_at must be a non-negative integer")

    lineage_ref = _require_optional_string(payload.get("lineage_ref"), token="missing_lineage")
    if artifact_kind in RECEIPTS_WITH_REQUIRED_LINEAGE and lineage_ref is None:
        raise PublicReceiptRuntimeError("missing_lineage", "lineage_ref is required for this receipt class")

    normalized: dict[str, Any] = {
        "artifact_kind": artifact_kind,
        "schema_version": schema_version,
        "signer_agent_id": signer_agent_id,
        "authority_scope": authority_scope,
        "lineage_ref": lineage_ref,
        "epoch_id": epoch_id,
        "issued_at": issued_at,
        "verification_material_ref": verification_material_ref,
        "verification_status": verification_status,
    }
    for field_name in RECEIPT_CLASS_FIELDS[artifact_kind]:
        if field_name.endswith("_or_null"):
            normalized[field_name] = _require_optional_string(payload.get(field_name), token="schema_mismatch")
        else:
            normalized[field_name] = _require_non_empty_string(payload.get(field_name), token="schema_mismatch")

    if verify_receipt_id:
        expected_receipt_id = _canonical_receipt_id(normalized)
        receipt_id = _require_non_empty_string(payload.get("receipt_id"), token="schema_mismatch")
        if receipt_id != expected_receipt_id:
            raise PublicReceiptRuntimeError("schema_mismatch", "receipt_id does not match canonical payload")
        return {"receipt_id": receipt_id, **normalized}

    return normalized


def _require_non_empty_string(value: Any, *, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicReceiptRuntimeError(token, f"{token}: required non-empty string")
    return value.strip()


def _require_optional_string(value: Any, *, token: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise PublicReceiptRuntimeError(token, f"{token}: expected string or null")
    return value.strip() or None


def _canonical_receipt_id(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


__all__ = [
    "PUBLIC_RECEIPT_RUNTIME_VERSION",
    "PublicReceiptRuntimeError",
    "RECEIPT_CLASS_FIELDS",
    "issue_public_receipt",
    "query_public_receipts",
]
