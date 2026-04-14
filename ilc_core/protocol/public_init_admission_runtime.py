"""Phase 650 public init/admission runtime."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ilc_core.identity.agent_id_runtime import AgentIdentityError, verify_agent_id
from ilc_core.storage.lmdb_public_runtime import LmdbAdmissionStore


PUBLIC_INIT_ADMISSION_RUNTIME_VERSION = "public_init_admission_runtime_650.v0.1"
PUBLIC_INIT_ADMISSION_SCHEMA_VERSION = "v0.1"
PUBLIC_IDENTITY_ACTIVATION_RECEIPT_KIND = "public_identity_activation_receipt"
PUBLIC_INIT_ADMISSION_SCOPE = "public_init_admission"


class PublicInitAdmissionRuntimeError(ValueError):
    """Fail-closed runtime error with machine token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def issue_public_init_admission_receipt(
    *,
    payload: dict[str, Any],
    epoch_id: str,
    store: LmdbAdmissionStore,
) -> dict[str, Any]:
    agent_id = _require_non_empty_string(payload.get("agent_id"), token="missing_agent_id")
    canonical_root_key_hex = _require_non_empty_string(
        payload.get("canonical_root_key_hex"),
        token="missing_canonical_root_key",
    )
    authority_scope = _require_non_empty_string(payload.get("authority_scope"), token="missing_scope")
    lineage_ref = _require_non_empty_string(payload.get("lineage_ref"), token="missing_lineage")
    verification_material_ref = _require_non_empty_string(
        payload.get("verification_material_ref"),
        token="missing_attestation",
    )
    stake_binding_ref_or_null = _require_optional_string(payload.get("stake_binding_ref_or_null"))

    if authority_scope != PUBLIC_INIT_ADMISSION_SCOPE:
        raise PublicInitAdmissionRuntimeError(
            "authority_scope_forbidden",
            "authority_scope must remain the bounded public init/admission scope",
        )

    canonical_root_key_bytes = _parse_root_key_hex(canonical_root_key_hex)
    try:
        if not verify_agent_id(agent_id, canonical_root_key_bytes):
            raise PublicInitAdmissionRuntimeError(
                "canonical_agent_id_mismatch",
                "agent_id does not match canonical root key derivation",
            )
    except AgentIdentityError as exc:
        raise PublicInitAdmissionRuntimeError(exc.token, str(exc)) from exc

    issued_at = _deterministic_issued_at(epoch_id)
    receipt_payload = {
        "artifact_kind": PUBLIC_IDENTITY_ACTIVATION_RECEIPT_KIND,
        "schema_version": PUBLIC_INIT_ADMISSION_SCHEMA_VERSION,
        "signer_agent_id": agent_id,
        "authority_scope": authority_scope,
        "lineage_ref": lineage_ref,
        "epoch_id": epoch_id,
        "issued_at": issued_at,
        "verification_material_ref": verification_material_ref,
        "verification_status": "valid",
        "activated_agent_id": agent_id,
        "admission_authority_scope": authority_scope,
        "stake_binding_ref_or_null": stake_binding_ref_or_null,
    }
    receipt_id = _canonical_receipt_id(receipt_payload)
    receipt = {"receipt_id": receipt_id, **receipt_payload}
    store.put_admission_receipt(receipt_id, receipt)

    return {
        "ok": True,
        "token": "admission_receipt_issued",
        "persisted": True,
        "receipt": receipt,
    }


def _parse_root_key_hex(value: str) -> bytes:
    try:
        root_key = bytes.fromhex(value)
    except ValueError as exc:
        raise PublicInitAdmissionRuntimeError(
            "canonical_root_key_invalid_hex",
            "canonical_root_key_hex must be valid hexadecimal bytes",
        ) from exc
    if len(root_key) == 0:
        raise PublicInitAdmissionRuntimeError(
            "canonical_root_key_empty",
            "canonical_root_key_hex must not decode to empty bytes",
        )
    return root_key


def _require_non_empty_string(value: Any, *, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicInitAdmissionRuntimeError(token, f"{token}: required non-empty string")
    return value.strip()


def _require_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise PublicInitAdmissionRuntimeError(
            "stake_binding_ref_invalid_type",
            "stake_binding_ref_or_null must be a string or null",
        )
    return value.strip() or None


def _canonical_receipt_id(payload: dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _deterministic_issued_at(epoch_id: str) -> int:
    suffix = epoch_id.rsplit("::", 1)[-1]
    if suffix.isdigit():
        return int(suffix)
    digest = hashlib.sha256(epoch_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


__all__ = [
    "PUBLIC_IDENTITY_ACTIVATION_RECEIPT_KIND",
    "PUBLIC_INIT_ADMISSION_RUNTIME_VERSION",
    "PUBLIC_INIT_ADMISSION_SCOPE",
    "PublicInitAdmissionRuntimeError",
    "issue_public_init_admission_receipt",
]
