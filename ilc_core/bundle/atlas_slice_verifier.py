# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only Atlas signed-slice verifier for Window 1576.

The verifier treats native signed-slice records and portable witnesses as
untrusted JSON. It replays canonical hashes and validates structure only; it
does not write LMDB, fetch blobs, materialize slices, or sign records.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.bundle.atlas_slice_schema import (
    ALLOWED_PRIVACY_CLASSES,
    ALLOWED_SIGNER_AUTHORITY_CLASSES,
    ATLAS_SLICE_CANONICALIZATION_VERSION,
    ATLAS_SLICE_NATIVE_TABLE,
    ATLAS_SLICE_PREIMAGE_DOMAIN,
    ATLAS_SLICE_SCHEMA_VERSION,
    ATLAS_SLICE_WITNESS_DOMAIN,
    GENESIS_PUBLIC_SIGNABLE_PROJECTIONS,
    PORTABLE_WITNESS_REQUIRED_FIELDS,
    SIGNED_SLICE_PREIMAGE_REQUIRED_FIELDS,
    build_projection_query_definition,
    canonical_schema_json,
    sha384_canonical,
)
from ilc_core.private_json_guardrails import reject_float


ATLAS_SLICE_VERIFIER_SCHEMA_VERSION = "atlas_slice_verifier_1576.v0.1"
ATLAS_SLICE_VERIFIER_PHASE = "1576-slice-verifier"
ATLAS_SLICE_VERIFIER_TOKEN = "atlas_slice_verifier_committed_phase_1576"
ATLAS_SLICE_NATIVE_RECORD_VERIFICATION_TOKEN = (
    "atlas_slice_native_record_verification_committed_phase_1576"
)
ATLAS_SLICE_PORTABLE_WITNESS_VERIFICATION_TOKEN = (
    "atlas_slice_portable_witness_linkage_verification_committed_phase_1576"
)
ATLAS_SLICE_VERIFIER_NEGATIVE_TESTS_TOKEN = (
    "atlas_slice_verifier_negative_tests_committed_phase_1576"
)
ATLAS_SLICE_VERIFIER_NO_MATERIALIZATION_TOKEN = (
    "atlas_slice_verifier_no_lmdb_no_materialization_phase_1576"
)

NATIVE_SIGNED_SLICE_RECORD_REQUIRED_FIELDS = (
    "authority_proof_path",
    "native_record_kind",
    "native_table",
    "preimage",
    "preimage_sha384",
    "schema_version",
    "signature",
    "signature_status",
    "signer_authority_class",
    "signer_key_ref",
)

ALLOWED_SIGNATURE_STATUSES = frozenset(
    {
        "unsigned_schema_only",
        "signature_attached_unverified",
        "signature_verified",
        "signature_verification_deferred",
    }
)

_FLOAT_TOKEN = "atlas_slice_verifier_float_not_allowed"
_HEX_96 = frozenset("0123456789abcdef")
_MAX_JSON_BYTES = 16 * 1024 * 1024
_MAX_COMMITMENTS = 100_000
_MAX_SIGNATURE_HEX_CHARS = 32_768
_RECEIPT_PREFIX = "atlas_slice_verification_receipt:"
_TOKENS = (
    ATLAS_SLICE_VERIFIER_TOKEN,
    ATLAS_SLICE_NATIVE_RECORD_VERIFICATION_TOKEN,
    ATLAS_SLICE_PORTABLE_WITNESS_VERIFICATION_TOKEN,
    ATLAS_SLICE_VERIFIER_NEGATIVE_TESTS_TOKEN,
    ATLAS_SLICE_VERIFIER_NO_MATERIALIZATION_TOKEN,
)


class AtlasSliceVerifierError(ValueError):
    """Stable Atlas slice verifier error."""


def verify_native_signed_slice_record(
    record: Mapping[str, Any],
    *,
    require_signature_status: bool = False,
) -> dict[str, Any]:
    """Verify a native `__signed_slices__` record without mutating state."""

    _reject_float(record)
    _require_exact_field_set(
        record,
        set(NATIVE_SIGNED_SLICE_RECORD_REQUIRED_FIELDS),
        "atlas_slice_native_record_fields_invalid",
    )
    if record.get("native_record_kind") != "atlas_signed_slice_record":
        raise AtlasSliceVerifierError("atlas_slice_native_record_kind_invalid")
    if record.get("native_table") != ATLAS_SLICE_NATIVE_TABLE:
        raise AtlasSliceVerifierError("atlas_slice_native_table_invalid")
    if record.get("schema_version") != ATLAS_SLICE_SCHEMA_VERSION:
        raise AtlasSliceVerifierError("atlas_slice_native_schema_version_invalid")

    preimage = record.get("preimage")
    if not isinstance(preimage, Mapping):
        raise AtlasSliceVerifierError("atlas_slice_native_preimage_invalid")
    preimage_summary = verify_signed_slice_preimage(preimage)
    preimage_sha384 = _required_sha384(record, "preimage_sha384")
    if sha384_canonical(preimage) != preimage_sha384:
        raise AtlasSliceVerifierError("atlas_slice_native_preimage_sha384_mismatch")

    signer_authority_class = _required_str(record, "signer_authority_class")
    if signer_authority_class not in ALLOWED_SIGNER_AUTHORITY_CLASSES:
        raise AtlasSliceVerifierError("atlas_slice_signer_authority_class_invalid")
    if (
        signer_authority_class == "genesis"
        and preimage_summary["projection_query_id"] not in GENESIS_PUBLIC_SIGNABLE_PROJECTIONS
    ):
        raise AtlasSliceVerifierError("atlas_slice_genesis_projection_not_signable")
    _require_non_empty_str(record.get("signer_key_ref"), "signer_key_ref")
    _require_str_sequence(record.get("authority_proof_path"), "authority_proof_path", non_empty=True)

    signature_status = _required_str(record, "signature_status")
    if signature_status not in ALLOWED_SIGNATURE_STATUSES:
        raise AtlasSliceVerifierError("atlas_slice_signature_status_invalid")
    signature = record.get("signature")
    if require_signature_status and signature_status != "signature_verified":
        raise AtlasSliceVerifierError("atlas_slice_signature_status_not_verified")
    if signature_status in {"signature_attached_unverified", "signature_verified"}:
        _require_signature_hex(signature, signature_status)
    if signature_status == "signature_verification_deferred" and signature is not None:
        _require_signature_hex(signature, signature_status)
    if signature_status == "unsigned_schema_only" and signature is not None:
        raise AtlasSliceVerifierError("atlas_slice_unsigned_record_has_signature")

    return {
        "authority_root": preimage_summary["authority_root"],
        "native_record_sha384": sha384_canonical(record),
        "preimage_sha384": preimage_sha384,
        "projection_query_id": preimage_summary["projection_query_id"],
        "signature_status": signature_status,
        "signer_authority_class": signer_authority_class,
        "slice_id": preimage_summary["slice_id"],
        "verified": True,
    }


def verify_signed_slice_preimage(preimage: Mapping[str, Any]) -> dict[str, Any]:
    """Verify a signed-slice preimage field set and projection boundary."""

    _reject_float(preimage)
    _require_exact_field_set(
        preimage,
        set(SIGNED_SLICE_PREIMAGE_REQUIRED_FIELDS) | {"preimage_domain"},
        "atlas_slice_preimage_fields_invalid",
    )
    if preimage.get("preimage_domain") != ATLAS_SLICE_PREIMAGE_DOMAIN:
        raise AtlasSliceVerifierError("atlas_slice_preimage_domain_invalid")
    if preimage.get("schema_version") != ATLAS_SLICE_SCHEMA_VERSION:
        raise AtlasSliceVerifierError("atlas_slice_preimage_schema_version_invalid")
    if preimage.get("canonicalization_version") != ATLAS_SLICE_CANONICALIZATION_VERSION:
        raise AtlasSliceVerifierError("atlas_slice_preimage_canonicalization_invalid")
    privacy_class = _required_str(preimage, "privacy_class")
    if privacy_class not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSliceVerifierError("atlas_slice_privacy_class_invalid")
    projection_parameters = preimage.get("projection_parameters")
    if not isinstance(projection_parameters, Mapping):
        raise AtlasSliceVerifierError("atlas_slice_projection_parameters_invalid")
    raw_included_tables = preimage.get("included_tables")
    if isinstance(raw_included_tables, list) and ATLAS_SLICE_NATIVE_TABLE in raw_included_tables:
        raise AtlasSliceVerifierError("atlas_slice_recursive_signed_slices_table_forbidden")
    included_tables = _require_str_sequence(
        raw_included_tables,
        "included_tables",
        non_empty=True,
    )
    expected_projection = build_projection_query_definition(
        projection_query_id=_required_str(preimage, "projection_query_id"),
        projection_parameters=projection_parameters,
        included_tables=included_tables,
        privacy_class=privacy_class,
    )
    if list(preimage["included_tables"]) != expected_projection["included_tables"]:
        raise AtlasSliceVerifierError("atlas_slice_included_tables_not_canonical")
    if dict(preimage["projection_parameters"]) != expected_projection["projection_parameters"]:
        raise AtlasSliceVerifierError("atlas_slice_projection_parameters_not_canonical")
    return {
        "authority_root": _required_str(preimage, "authority_root"),
        "epoch_or_version": _required_str(preimage, "epoch_or_version"),
        "merkle_root": _required_sha384(preimage, "merkle_root"),
        "privacy_class": privacy_class,
        "projection_parameters": dict(projection_parameters),
        "projection_query_id": _required_str(preimage, "projection_query_id"),
        "slice_id": _required_str(preimage, "slice_id"),
        "verified": True,
    }


def verify_portable_manifest_witness(
    witness: Mapping[str, Any],
    *,
    native_record: Mapping[str, Any] | None = None,
    require_signature_status: bool = False,
) -> dict[str, Any]:
    """Verify a portable manifest witness and optional native-record linkage."""

    _reject_float(witness)
    _require_exact_field_set(
        witness,
        set(PORTABLE_WITNESS_REQUIRED_FIELDS) | {"manifest_sha384"},
        "atlas_slice_portable_witness_fields_invalid",
    )
    if witness.get("schema_version") != ATLAS_SLICE_SCHEMA_VERSION:
        raise AtlasSliceVerifierError("atlas_slice_witness_schema_version_invalid")
    if witness.get("canonicalization_version") != ATLAS_SLICE_CANONICALIZATION_VERSION:
        raise AtlasSliceVerifierError("atlas_slice_witness_canonicalization_invalid")
    if witness.get("manifest_domain") != ATLAS_SLICE_WITNESS_DOMAIN:
        raise AtlasSliceVerifierError("atlas_slice_witness_domain_invalid")
    if witness.get("excluded_tables") != [ATLAS_SLICE_NATIVE_TABLE]:
        raise AtlasSliceVerifierError("atlas_slice_witness_excluded_tables_invalid")

    manifest_sha384 = _required_sha384(witness, "manifest_sha384")
    witness_body = {key: value for key, value in witness.items() if key != "manifest_sha384"}
    if sha384_canonical(witness_body) != manifest_sha384:
        raise AtlasSliceVerifierError("atlas_slice_witness_manifest_sha384_mismatch")

    _required_sha384(witness, "derived_from_native_record_sha384")
    _required_sha384(witness, "merkle_root")
    privacy_class = _required_str(witness, "privacy_class")
    if privacy_class not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSliceVerifierError("atlas_slice_witness_privacy_class_invalid")
    signer_authority_class = _required_str(witness, "signer_authority_class")
    if signer_authority_class not in ALLOWED_SIGNER_AUTHORITY_CLASSES:
        raise AtlasSliceVerifierError("atlas_slice_witness_signer_authority_class_invalid")
    if (
        signer_authority_class == "genesis"
        and _required_str(witness, "projection_query_id") not in GENESIS_PUBLIC_SIGNABLE_PROJECTIONS
    ):
        raise AtlasSliceVerifierError("atlas_slice_witness_genesis_projection_not_signable")
    if not isinstance(witness.get("projection_parameters"), Mapping):
        raise AtlasSliceVerifierError("atlas_slice_witness_projection_parameters_invalid")
    if not isinstance(witness.get("availability"), Mapping):
        raise AtlasSliceVerifierError("atlas_slice_witness_availability_invalid")
    if not isinstance(witness.get("permission_policy"), Mapping):
        raise AtlasSliceVerifierError("atlas_slice_witness_permission_policy_invalid")
    if witness["permission_policy"].get("privacy_class") != privacy_class:  # type: ignore[index]
        raise AtlasSliceVerifierError("atlas_slice_witness_permission_privacy_mismatch")
    _require_str_sequence(witness.get("authority_proof_path"), "authority_proof_path")
    _require_str_sequence(witness.get("required_tests"), "required_tests")
    _require_str_sequence(witness.get("semantic_loss_annotations"), "semantic_loss_annotations")
    _require_commitment_list(
        witness.get("node_commitments"),
        "node_commitments",
        id_fields=("node_id",),
        digest_field="record_sha384",
    )
    _require_commitment_list(
        witness.get("edge_commitments"),
        "edge_commitments",
        id_fields=("edge_id",),
        digest_field="record_sha384",
    )
    _require_commitment_list(
        witness.get("content_commitments"),
        "content_commitments",
        id_fields=("content_id", "content_cid", "table_key"),
        digest_field="sha384",
    )

    native_summary: dict[str, Any] | None = None
    if native_record is not None:
        native_summary = verify_native_signed_slice_record(
            native_record,
            require_signature_status=require_signature_status,
        )
        if witness["derived_from_native_record_sha384"] != native_summary["native_record_sha384"]:
            raise AtlasSliceVerifierError("atlas_slice_witness_native_record_sha384_mismatch")
        native_preimage = native_record["preimage"]  # type: ignore[index]
        for field in (
            "authority_root",
            "epoch_or_version",
            "merkle_root",
            "privacy_class",
            "projection_parameters",
            "projection_query_id",
            "slice_id",
        ):
            if witness.get(field) != native_preimage.get(field):  # type: ignore[union-attr]
                raise AtlasSliceVerifierError(f"atlas_slice_witness_native_field_mismatch:{field}")
        if signer_authority_class != native_record.get("signer_authority_class"):
            raise AtlasSliceVerifierError(
                "atlas_slice_witness_native_field_mismatch:signer_authority_class"
            )
        if witness.get("authority_proof_path") != native_record.get("authority_proof_path"):
            raise AtlasSliceVerifierError(
                "atlas_slice_witness_native_field_mismatch:authority_proof_path"
            )

    return {
        "derived_from_native_record_sha384": str(witness["derived_from_native_record_sha384"]),
        "manifest_sha384": manifest_sha384,
        "native_record_verified": native_summary is not None,
        "projection_query_id": _required_str(witness, "projection_query_id"),
        "slice_id": _required_str(witness, "slice_id"),
        "verified": True,
    }


def build_slice_verification_receipt(
    *,
    native_record: Mapping[str, Any],
    portable_witness: Mapping[str, Any] | None = None,
    generated_at_utc: str | None = None,
    source_label: str = "local",
    require_signature_status: bool = False,
) -> dict[str, Any]:
    """Build a deterministic local verification receipt for supplied objects."""

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(generated_at_utc)
    _require_non_empty_str(source_label, "source_label")
    native_summary = verify_native_signed_slice_record(
        native_record,
        require_signature_status=require_signature_status,
    )
    witness_summary = None
    if portable_witness is not None:
        witness_summary = verify_portable_manifest_witness(
            portable_witness,
            native_record=native_record,
            require_signature_status=require_signature_status,
        )
    body: dict[str, Any] = {
        "generated_at_utc": generated_at_utc,
        "native_record": native_summary,
        "non_claims": _non_claims(),
        "phase": ATLAS_SLICE_VERIFIER_PHASE,
        "schema_version": ATLAS_SLICE_VERIFIER_SCHEMA_VERSION,
        "source_label": source_label,
        "tokens": list(_TOKENS),
        "witness": witness_summary,
    }
    body_sha384 = sha384_canonical(body)
    receipt = {
        **body,
        "receipt_body_sha384": body_sha384,
        "receipt_id": f"{_RECEIPT_PREFIX}{body_sha384}",
    }
    _reject_float(receipt)
    return receipt


def load_json_object(path: str | Path) -> dict[str, Any]:
    """Load a bounded JSON object from disk."""

    source = Path(path)
    try:
        if source.stat().st_size > _MAX_JSON_BYTES:
            raise AtlasSliceVerifierError("atlas_slice_verifier_json_too_large")
        payload = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AtlasSliceVerifierError(f"atlas_slice_verifier_json_read_failed:{source}") from exc
    except json.JSONDecodeError as exc:
        raise AtlasSliceVerifierError(f"atlas_slice_verifier_json_invalid:{source}") from exc
    if not isinstance(payload, dict):
        raise AtlasSliceVerifierError(f"atlas_slice_verifier_json_not_object:{source}")
    try:
        _reject_float(payload)
    except RecursionError as exc:
        raise AtlasSliceVerifierError("atlas_slice_verifier_json_too_deep") from exc
    return payload


def write_slice_verification_receipt(path: str | Path, receipt: Mapping[str, Any]) -> Path:
    """Atomically write a deterministic local verification receipt."""

    _reject_float(receipt)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    payload = json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def _require_commitment_list(
    values: Any,
    field: str,
    *,
    id_fields: Sequence[str],
    digest_field: str,
) -> None:
    if not isinstance(values, list):
        raise AtlasSliceVerifierError(f"atlas_slice_witness_commitments_invalid:{field}")
    if len(values) > _MAX_COMMITMENTS:
        raise AtlasSliceVerifierError(f"atlas_slice_witness_commitments_too_many:{field}")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in values:
        if not isinstance(raw, Mapping):
            raise AtlasSliceVerifierError(f"atlas_slice_witness_commitment_not_object:{field}")
        _reject_float(raw)
        present_id_fields = [candidate_id for candidate_id in id_fields if candidate_id in raw]
        if len(present_id_fields) != 1:
            raise AtlasSliceVerifierError(f"atlas_slice_witness_commitment_id_fields_invalid:{field}")
        expected_fields = {present_id_fields[0], digest_field}
        if set(raw) != expected_fields:
            raise AtlasSliceVerifierError(f"atlas_slice_witness_commitment_fields_invalid:{field}")
        stable_id = _required_str(raw, present_id_fields[0])
        if stable_id in seen_ids:
            raise AtlasSliceVerifierError(f"atlas_slice_witness_commitment_duplicate:{field}")
        seen_ids.add(stable_id)
        _require_sha384_value(raw[digest_field], f"{field}:{digest_field}")
        normalized.append(dict(sorted(raw.items())))
    if list(values) != sorted(normalized, key=lambda row: canonical_schema_json(row)):
        raise AtlasSliceVerifierError(f"atlas_slice_witness_commitments_not_canonical:{field}")


def _non_claims() -> dict[str, bool]:
    return {
        "no_ccss_delivery_activation": True,
        "no_content_fetch": True,
        "no_ecu_credit": True,
        "no_epoch_transition": True,
        "no_lmdb_write": True,
        "no_live_settlement": True,
        "no_manifest_publication": True,
        "no_materialization": True,
        "no_production_minting": True,
        "no_production_signing": True,
        "no_public_graph_write": True,
        "no_public_p2p_activation": True,
        "no_verifier_role_grant": True,
        "no_wallet_write": True,
    }


def _require_str_sequence(values: Any, field: str, *, non_empty: bool = False) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, list):
        raise AtlasSliceVerifierError(f"atlas_slice_sequence_invalid:{field}")
    if non_empty and not values:
        raise AtlasSliceVerifierError(f"atlas_slice_sequence_empty:{field}")
    normalized = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise AtlasSliceVerifierError(f"atlas_slice_sequence_value_invalid:{field}")
        normalized.append(value)
    if len(set(normalized)) != len(normalized):
        raise AtlasSliceVerifierError(f"atlas_slice_sequence_duplicate:{field}")
    if normalized != sorted(normalized):
        raise AtlasSliceVerifierError(f"atlas_slice_sequence_not_canonical:{field}")
    return normalized


def _required_sha384(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    _require_sha384_value(value, key)
    return str(value)


def _require_sha384_value(value: Any, field: str) -> None:
    if not isinstance(value, str) or len(value) != 96 or any(char not in _HEX_96 for char in value):
        raise AtlasSliceVerifierError(f"atlas_slice_sha384_invalid:{field}")


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AtlasSliceVerifierError(f"atlas_slice_required_string_invalid:{key}")
    return value


def _require_non_empty_str(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSliceVerifierError(f"atlas_slice_required_string_invalid:{field}")


def _require_signature_hex(value: Any, status: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > _MAX_SIGNATURE_HEX_CHARS
        or len(value) % 2 != 0
        or any(char not in _HEX_96 for char in value)
    ):
        raise AtlasSliceVerifierError(f"atlas_slice_signature_hex_invalid:{status}")


def _require_exact_field_set(payload: Mapping[str, Any], expected: set[str], error: str) -> None:
    if set(payload) != expected:
        raise AtlasSliceVerifierError(error)


def _reject_float(value: Any) -> None:
    try:
        reject_float(value, _FLOAT_TOKEN)
    except ValueError as exc:
        raise AtlasSliceVerifierError(_FLOAT_TOKEN) from exc


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSliceVerifierError("atlas_slice_verifier_timestamp_invalid")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasSliceVerifierError("atlas_slice_verifier_timestamp_invalid") from exc


__all__ = [
    "ALLOWED_SIGNATURE_STATUSES",
    "ATLAS_SLICE_NATIVE_RECORD_VERIFICATION_TOKEN",
    "ATLAS_SLICE_PORTABLE_WITNESS_VERIFICATION_TOKEN",
    "ATLAS_SLICE_VERIFIER_NEGATIVE_TESTS_TOKEN",
    "ATLAS_SLICE_VERIFIER_NO_MATERIALIZATION_TOKEN",
    "ATLAS_SLICE_VERIFIER_PHASE",
    "ATLAS_SLICE_VERIFIER_SCHEMA_VERSION",
    "ATLAS_SLICE_VERIFIER_TOKEN",
    "AtlasSliceVerifierError",
    "NATIVE_SIGNED_SLICE_RECORD_REQUIRED_FIELDS",
    "build_slice_verification_receipt",
    "load_json_object",
    "verify_native_signed_slice_record",
    "verify_portable_manifest_witness",
    "verify_signed_slice_preimage",
    "write_slice_verification_receipt",
]
