# SPDX-License-Identifier: AGPL-3.0-only
"""Local-only Atlas signed-slice materializer for Window 1576.

This module consumes verifier-passing native signed-slice records and portable
witnesses, verifies local blob bytes against witness commitments, and emits a
status-only receipt. It does not write LMDB, fetch over a network, grant roles,
clear guards, sign records, or activate runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.bundle.atlas_slice_schema import sha384_canonical
from ilc_core.bundle.atlas_slice_verifier import (
    AtlasSliceVerifierError,
    verify_native_signed_slice_record,
    verify_portable_manifest_witness,
)


ATLAS_SLICE_MATERIALIZER_SCHEMA_VERSION = "atlas_slice_materializer_1576.v0.1"
ATLAS_SLICE_MATERIALIZER_PHASE = "1576-slice-materializer"
ATLAS_SLICE_MATERIALIZER_TOKEN = "atlas_slice_materializer_committed_phase_1576"
ATLAS_SLICE_MATERIALIZER_LOCAL_ONLY_TOKEN = (
    "atlas_slice_materializer_local_sources_only_phase_1576"
)
ATLAS_SLICE_MATERIALIZER_DIGEST_TOKEN = (
    "atlas_slice_materializer_blob_digest_verification_committed_phase_1576"
)
MATERIALIZED_BASELINE_VERIFIED_TOKEN = "materialized_baseline_verified_phase_1576"
VERIFIER_ELIGIBILITY_EVIDENCE_TOKEN = "verifier_eligibility_evidence_committed_phase_1576"
ATLAS_SLICE_MATERIALIZER_NO_ROLE_TOKEN = (
    "atlas_slice_materializer_no_role_grant_no_guard_clearance_phase_1576"
)

MAX_BLOB_BYTES = 128 * 1024 * 1024
MAX_TOTAL_MATERIALIZED_BYTES = 1024 * 1024 * 1024
MAX_RECEIPT_JSON_DEPTH = 256
_RECEIPT_PREFIX = "atlas_slice_materialization_receipt:"
_TOKENS = (
    ATLAS_SLICE_MATERIALIZER_TOKEN,
    ATLAS_SLICE_MATERIALIZER_LOCAL_ONLY_TOKEN,
    ATLAS_SLICE_MATERIALIZER_DIGEST_TOKEN,
    MATERIALIZED_BASELINE_VERIFIED_TOKEN,
    VERIFIER_ELIGIBILITY_EVIDENCE_TOKEN,
    ATLAS_SLICE_MATERIALIZER_NO_ROLE_TOKEN,
)


class AtlasSliceMaterializerError(ValueError):
    """Stable Atlas slice materializer error."""


def build_slice_materialization_receipt(
    *,
    native_record: Mapping[str, Any],
    portable_witness: Mapping[str, Any] | None,
    local_source_root: str | Path,
    generated_at_utc: str | None = None,
    allow_missing_blobs: bool = False,
    require_baseline: bool = False,
) -> dict[str, Any]:
    """Verify local blobs and build a deterministic materialization receipt."""

    try:
        native_summary = verify_native_signed_slice_record(native_record)
        witness_summary = (
            verify_portable_manifest_witness(portable_witness, native_record=native_record)
            if portable_witness is not None
            else None
        )
    except AtlasSliceVerifierError as exc:
        raise AtlasSliceMaterializerError(f"atlas_slice_materializer_verifier_failed:{exc}") from exc

    generated_at_source = "caller_supplied"
    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        generated_at_source = "wall_clock_utc"
    _validate_timestamp(generated_at_utc)

    root = Path(local_source_root).resolve()
    if not root.is_dir():
        raise AtlasSliceMaterializerError("atlas_slice_materializer_source_root_missing")

    commitments = _commitments_from_witness(portable_witness)
    verified, missing, total_bytes = _verify_commitments(
        commitments,
        local_source_root=root,
        allow_missing_blobs=allow_missing_blobs,
    )
    verifier_eligibility = bool(commitments) and not missing and len(verified) == len(commitments)
    baseline_verified, baseline_reason = _baseline_status(verified)
    if require_baseline and not baseline_verified:
        raise AtlasSliceMaterializerError(f"atlas_slice_materializer_baseline_not_verified:{baseline_reason}")

    body: dict[str, Any] = {
        "blobs_missing": len(missing),
        "blobs_verified": len(verified),
        "generated_at_source": generated_at_source,
        "generated_at_utc": generated_at_utc,
        "local_source_root": str(root),
        "materialized_baseline_verified": baseline_verified,
        "materialized_baseline_verified_reason": baseline_reason,
        "missing_blobs": missing,
        "native_record": native_summary,
        "non_claims": _non_claims(),
        "phase": ATLAS_SLICE_MATERIALIZER_PHASE,
        "projection_query_id": native_summary["projection_query_id"],
        "schema_version": ATLAS_SLICE_MATERIALIZER_SCHEMA_VERSION,
        "slice_id": native_summary["slice_id"],
        "tokens": list(_TOKENS),
        "total_bytes_materialized": total_bytes,
        "verified_blobs": verified,
        "verifier_eligibility_evidence": verifier_eligibility,
        "witness": witness_summary,
    }
    _reject_float(body)
    body_sha384 = sha384_canonical(body)
    return {
        **body,
        "receipt_body_sha384": body_sha384,
        "receipt_id": f"{_RECEIPT_PREFIX}{body_sha384}",
    }


def write_slice_materialization_receipt(
    path: str | Path,
    receipt: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write a materialization receipt."""

    _reject_float(receipt)
    target = Path(path)
    if allowed_root is not None:
        root = Path(allowed_root).resolve()
        target_resolved = target.resolve()
        if target_resolved != root and root not in target_resolved.parents:
            raise AtlasSliceMaterializerError("atlas_slice_materializer_output_path_outside_allowed_root")
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


def _commitments_from_witness(witness: Mapping[str, Any] | None) -> list[dict[str, str]]:
    if witness is None:
        return []
    commitments: list[dict[str, str]] = []
    for field, digest_field, id_fields in (
        ("node_commitments", "record_sha384", ("node_id",)),
        ("edge_commitments", "record_sha384", ("edge_id",)),
        ("content_commitments", "sha384", ("content_id", "content_cid", "table_key")),
    ):
        values = witness.get(field)
        if not isinstance(values, list):
            raise AtlasSliceMaterializerError(f"atlas_slice_materializer_commitments_invalid:{field}")
        for raw in values:
            if not isinstance(raw, Mapping):
                raise AtlasSliceMaterializerError(f"atlas_slice_materializer_commitment_not_object:{field}")
            stable_id = _stable_id(raw, id_fields, field)
            digest = _required_str(raw, digest_field)
            commitments.append(
                {
                    "commitment_table": field,
                    "digest_field": digest_field,
                    "sha384": digest,
                    "stable_id": stable_id,
                }
            )
    return commitments


def _verify_commitments(
    commitments: Sequence[Mapping[str, str]],
    *,
    local_source_root: Path,
    allow_missing_blobs: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], int]:
    verified: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    total_bytes = 0
    for commitment in commitments:
        blob_path = _resolve_blob_path(commitment, local_source_root)
        if blob_path is None:
            missing_entry = {
                "commitment_table": commitment["commitment_table"],
                "sha384": commitment["sha384"],
                "stable_id": commitment["stable_id"],
            }
            if not allow_missing_blobs:
                raise AtlasSliceMaterializerError(
                    f"atlas_slice_materializer_blob_missing:{commitment['stable_id']}"
                )
            missing.append(missing_entry)
            continue
        size = blob_path.stat().st_size
        if size > MAX_BLOB_BYTES:
            raise AtlasSliceMaterializerError("atlas_slice_materializer_blob_too_large")
        if total_bytes + size > MAX_TOTAL_MATERIALIZED_BYTES:
            raise AtlasSliceMaterializerError("atlas_slice_materializer_total_bytes_too_large")
        digest = _sha384_file(blob_path)
        if digest != commitment["sha384"]:
            raise AtlasSliceMaterializerError(
                f"atlas_slice_materializer_blob_digest_mismatch:{commitment['stable_id']}"
            )
        total_bytes += size
        verified.append(
            {
                "bytes": size,
                "commitment_table": commitment["commitment_table"],
                "path": str(blob_path.relative_to(local_source_root)),
                "sha384": digest,
                "stable_id": commitment["stable_id"],
            }
        )
    return verified, missing, total_bytes


def _resolve_blob_path(commitment: Mapping[str, str], local_source_root: Path) -> Path | None:
    digest = commitment["sha384"]
    stable_id = commitment["stable_id"]
    candidates = [
        Path("sha384") / digest,
        Path("blobs") / "sha384" / digest,
        Path("blobs") / digest,
        Path(digest),
        Path(stable_id),
    ]
    for relative in candidates:
        candidate = (local_source_root / relative).resolve()
        if candidate != local_source_root and local_source_root not in candidate.parents:
            raise AtlasSliceMaterializerError("atlas_slice_materializer_path_traversal")
        if candidate.is_file():
            return candidate
    return None


def _baseline_status(verified: Sequence[Mapping[str, Any]]) -> tuple[bool, str]:
    verified_ids = {str(blob["stable_id"]) for blob in verified}
    has_core = any(
        _matches_baseline_id(stable_id, "genesis_core_slice_0_authority_package.json")
        or stable_id == "genesis_core_slice_0_authority_package"
        for stable_id in verified_ids
    )
    has_baseline = any(
        _matches_baseline_id(stable_id, "genesis_v05_public_rc_baseline_slice_1.json")
        or stable_id == "genesis_v05_public_rc_baseline_slice_1"
        for stable_id in verified_ids
    )
    if has_core and has_baseline:
        return True, "core_slice_0_and_public_rc_baseline_slice_1_verified"
    if not verified and not verified_ids:
        return False, "no_real_blobs_in_schema_examples"
    return False, "baseline_pair_not_fully_verified"


def _matches_baseline_id(stable_id: str, filename: str) -> bool:
    return stable_id == filename or stable_id.endswith(f"/{filename}")


def _stable_id(raw: Mapping[str, Any], id_fields: Sequence[str], field: str) -> str:
    present = [candidate for candidate in id_fields if candidate in raw]
    if len(present) != 1:
        raise AtlasSliceMaterializerError(f"atlas_slice_materializer_commitment_id_invalid:{field}")
    return _required_str(raw, present[0])


def _sha384_file(path: Path) -> str:
    digest = hashlib.sha384()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _non_claims() -> dict[str, bool]:
    return {
        "no_ccss_delivery_activation": True,
        "no_ecu_credit": True,
        "no_epoch_transition": True,
        "no_guard_clearance": True,
        "no_lmdb_write": True,
        "no_live_settlement": True,
        "no_manifest_publication": True,
        "no_production_minting": True,
        "no_production_network_fetch": True,
        "no_production_signing": True,
        "no_public_graph_write": True,
        "no_public_p2p_activation": True,
        "no_verifier_role_grant": True,
        "no_wallet_write": True,
    }


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AtlasSliceMaterializerError(f"atlas_slice_materializer_required_string_invalid:{key}")
    return value


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSliceMaterializerError("atlas_slice_materializer_timestamp_invalid")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasSliceMaterializerError("atlas_slice_materializer_timestamp_invalid") from exc


def _reject_float(value: Any, *, _depth: int = 0) -> None:
    if _depth > MAX_RECEIPT_JSON_DEPTH:
        raise AtlasSliceMaterializerError("atlas_slice_materializer_json_depth_exceeded")
    if isinstance(value, float):
        raise AtlasSliceMaterializerError("atlas_slice_materializer_float_not_allowed")
    if isinstance(value, Mapping):
        for key, nested in value.items():
            _reject_float(key, _depth=_depth + 1)
            _reject_float(nested, _depth=_depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_float(nested, _depth=_depth + 1)


__all__ = [
    "ATLAS_SLICE_MATERIALIZER_DIGEST_TOKEN",
    "ATLAS_SLICE_MATERIALIZER_LOCAL_ONLY_TOKEN",
    "ATLAS_SLICE_MATERIALIZER_NO_ROLE_TOKEN",
    "ATLAS_SLICE_MATERIALIZER_PHASE",
    "ATLAS_SLICE_MATERIALIZER_SCHEMA_VERSION",
    "ATLAS_SLICE_MATERIALIZER_TOKEN",
    "AtlasSliceMaterializerError",
    "MATERIALIZED_BASELINE_VERIFIED_TOKEN",
    "MAX_BLOB_BYTES",
    "MAX_RECEIPT_JSON_DEPTH",
    "MAX_TOTAL_MATERIALIZED_BYTES",
    "VERIFIER_ELIGIBILITY_EVIDENCE_TOKEN",
    "build_slice_materialization_receipt",
    "write_slice_materialization_receipt",
]
