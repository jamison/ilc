# SPDX-License-Identifier: AGPL-3.0-only
"""Local CDL-087 serving-peer evidence helpers.

Phase 1259 records production-candidate evidence for CDL-087 Conditions 2 and
3 without exposing public fetch serving. The helpers are pure, bounded, and use
canonical JSON for machine-verifiable artifacts.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

CDL087_SERVING_PEER_EVIDENCE_VERSION = (
    "cdl_087_serving_peer_evidence_slice_phase_1259.v0.1"
)
PRODUCTION_CANDIDATE_TIER_CLASSIFICATION_TOKEN = (
    "production_candidate_tier_classification_runtime_evidence_recorded_phase_1259"
)
BOOTSTRAP_SNAPSHOT_EVIDENCE_TOKEN = (
    "bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259"
)
NO_PUBLIC_FETCH_SERVING_TOKEN = "no_public_fetch_serving_enabled_phase_1259"

DEFAULT_MAX_ARTIFACTS = 512
DEFAULT_MAX_JSON_BYTES = 2_000_000

TIER_A = "Tier A"
TIER_B = "Tier B"
TIER_C = "Tier C"
TIERS = frozenset({TIER_A, TIER_B, TIER_C})

TIER_A_ARTIFACT_TYPES = frozenset(
    {
        "accepted_adr",
        "accepted_cdl",
        "adr_0004_truth_primitive",
        "bootstrap_bundle",
        "cdl_086_release_artifact",
        "epoch_checkpoint_root",
        "genesis_root",
        "lineage_receipt",
        "signed_manifest",
        "truth_primitive",
    }
)

TIER_B_ARTIFACT_TYPES = frozenset(
    {
        "agent_bootstrap_index",
        "epoch_delta",
        "graph_projection_snapshot",
        "recent_manifest_delta",
        "route_index",
    }
)

_LOWER_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")


def classify_artifact(artifact: Mapping[str, Any]) -> str:
    """Return the CDL-087 Tier A/B/C class for a local artifact record."""

    artifact_type = _require_text(artifact.get("artifact_type"), "artifact_type_required")
    explicit_tier = artifact.get("tier")
    if explicit_tier is not None:
        if explicit_tier not in TIERS:
            raise ValueError("artifact_tier_unsupported")
        return str(explicit_tier)
    if artifact_type in TIER_A_ARTIFACT_TYPES:
        return TIER_A
    if artifact_type in TIER_B_ARTIFACT_TYPES:
        return TIER_B
    return TIER_C


def build_tier_classification_evidence(
    artifacts: Sequence[Mapping[str, Any]],
    *,
    serving_peer_id: str,
    max_artifacts: int = DEFAULT_MAX_ARTIFACTS,
) -> dict[str, Any]:
    """Build deterministic local Tier A/B/C classification evidence."""

    _require_non_empty_text(serving_peer_id, "serving_peer_id_required")
    _enforce_artifact_count(artifacts, max_artifacts)

    classified = []
    counts = {TIER_A: 0, TIER_B: 0, TIER_C: 0}
    for artifact in artifacts:
        artifact_id = _require_text(artifact.get("artifact_id"), "artifact_id_required")
        artifact_type = _require_text(
            artifact.get("artifact_type"),
            "artifact_type_required",
        )
        tier = classify_artifact(artifact)
        counts[tier] += 1
        classified.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "tier": tier,
            }
        )
    classified.sort(key=lambda item: (item["tier"], item["artifact_id"]))

    return {
        "artifacts": classified,
        "counts_by_tier": counts,
        "non_public_boundary": {
            "network_endpoint_enabled": False,
            "public_fetch_serving_enabled": False,
            "token": NO_PUBLIC_FETCH_SERVING_TOKEN,
        },
        "serving_peer_id": serving_peer_id,
        "tokens": {
            "classification": PRODUCTION_CANDIDATE_TIER_CLASSIFICATION_TOKEN,
            "version": CDL087_SERVING_PEER_EVIDENCE_VERSION,
        },
        "version": CDL087_SERVING_PEER_EVIDENCE_VERSION,
    }


def build_bootstrap_snapshot(
    artifact_records: Sequence[Mapping[str, Any]],
    *,
    genesis_domain_hash: str,
    snapshot_epoch: int,
    epoch_checkpoint_range: Mapping[str, Any],
    authority_refs: Sequence[str],
    snapshot_id: str = "cdl087-bootstrap-snapshot",
    graph_projection_export: Mapping[str, Any] | None = None,
    max_artifacts: int = DEFAULT_MAX_ARTIFACTS,
) -> dict[str, Any]:
    """Build a Genesis-verifiable local bootstrap snapshot."""

    normalized_genesis_hash = _require_lower_hex_64(
        genesis_domain_hash,
        "genesis_domain_hash_invalid",
    )
    _validate_snapshot_epoch(snapshot_epoch)
    normalized_range = _normalize_epoch_checkpoint_range(
        epoch_checkpoint_range,
        snapshot_epoch=snapshot_epoch,
    )
    normalized_authority_refs = _normalize_authority_refs(authority_refs)
    _require_non_empty_text(snapshot_id, "snapshot_id_required")
    _enforce_artifact_count(artifact_records, max_artifacts)

    artifact_list = []
    for artifact in artifact_records:
        artifact_id = _require_text(artifact.get("artifact_id"), "artifact_id_required")
        artifact_type = _require_text(
            artifact.get("artifact_type"),
            "artifact_type_required",
        )
        artifact_payload = artifact.get("artifact_payload")
        if not isinstance(artifact_payload, Mapping):
            raise ValueError("artifact_payload_required")
        artifact_hash = compute_artifact_hash(artifact_payload)
        lineage_chain = _normalize_lineage_chain(
            artifact.get("lineage_proof_chain"),
            genesis_domain_hash=normalized_genesis_hash,
        )
        artifact_list.append(
            {
                "artifact_hash": artifact_hash,
                "artifact_id": artifact_id,
                "artifact_payload": _canonicalize(artifact_payload),
                "artifact_type": artifact_type,
                "lineage_proof_chain": lineage_chain,
                "tier": classify_artifact(artifact),
            }
        )
    artifact_list.sort(key=lambda item: item["artifact_id"])

    snapshot = {
        "artifact_list": artifact_list,
        "authority_refs": normalized_authority_refs,
        "epoch_checkpoint_range": normalized_range,
        "genesis_domain_hash": normalized_genesis_hash,
        "graph_projection_export": (
            None if graph_projection_export is None else _canonicalize(graph_projection_export)
        ),
        "snapshot_epoch": snapshot_epoch,
        "snapshot_manifest": {
            "network_endpoint_enabled": False,
            "public_fetch_serving_enabled": False,
            "snapshot_id": snapshot_id,
            "token": BOOTSTRAP_SNAPSHOT_EVIDENCE_TOKEN,
            "version": CDL087_SERVING_PEER_EVIDENCE_VERSION,
        },
    }
    _enforce_json_size(snapshot)
    return snapshot


def verify_bootstrap_snapshot(
    snapshot: Mapping[str, Any],
    *,
    expected_genesis_domain_hash: str,
) -> dict[str, Any]:
    """Validate a bootstrap snapshot and return a canonicalized copy."""

    expected_hash = _require_lower_hex_64(
        expected_genesis_domain_hash,
        "expected_genesis_domain_hash_invalid",
    )
    if not isinstance(snapshot, Mapping):
        raise ValueError("bootstrap_snapshot_mapping_required")
    if snapshot.get("genesis_domain_hash") != expected_hash:
        raise ValueError("bootstrap_snapshot_genesis_hash_mismatch")

    snapshot_epoch = snapshot.get("snapshot_epoch")
    _validate_snapshot_epoch(snapshot_epoch)
    _normalize_epoch_checkpoint_range(
        _require_mapping(
            snapshot.get("epoch_checkpoint_range"),
            "epoch_checkpoint_range_required",
        ),
        snapshot_epoch=snapshot_epoch,
    )
    _normalize_authority_refs(snapshot.get("authority_refs"))
    manifest = _require_mapping(snapshot.get("snapshot_manifest"), "snapshot_manifest_required")
    if manifest.get("public_fetch_serving_enabled") is not False:
        raise ValueError("bootstrap_snapshot_public_fetch_serving_forbidden")
    if manifest.get("network_endpoint_enabled") is not False:
        raise ValueError("bootstrap_snapshot_network_endpoint_forbidden")

    artifact_list = snapshot.get("artifact_list")
    if not isinstance(artifact_list, Sequence) or isinstance(artifact_list, (str, bytes)):
        raise ValueError("artifact_list_required")
    _enforce_artifact_count(artifact_list, DEFAULT_MAX_ARTIFACTS)
    for artifact in artifact_list:
        artifact_mapping = _require_mapping(artifact, "artifact_entry_mapping_required")
        payload = _require_mapping(artifact_mapping.get("artifact_payload"), "artifact_payload_required")
        expected_artifact_hash = compute_artifact_hash(payload)
        if artifact_mapping.get("artifact_hash") != expected_artifact_hash:
            raise ValueError("artifact_hash_mismatch")
        _normalize_lineage_chain(
            artifact_mapping.get("lineage_proof_chain"),
            genesis_domain_hash=expected_hash,
        )
        if artifact_mapping.get("tier") not in TIERS:
            raise ValueError("artifact_tier_unsupported")

    canonical_snapshot = _canonicalize(snapshot)
    _enforce_json_size(canonical_snapshot)
    return canonical_snapshot


def export_bootstrap_snapshot_json(
    snapshot: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_JSON_BYTES,
) -> str:
    """Export a bootstrap snapshot as canonical JSON."""

    payload = json.dumps(
        _canonicalize(snapshot),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("bootstrap_snapshot_json_size_exceeded")
    return payload


def verify_bootstrap_snapshot_json(
    payload: str,
    *,
    expected_genesis_domain_hash: str,
) -> dict[str, Any]:
    """Parse and verify canonical bootstrap snapshot JSON."""

    if not isinstance(payload, str):
        raise ValueError("bootstrap_snapshot_json_required")
    parsed = json.loads(payload)
    verified = verify_bootstrap_snapshot(
        parsed,
        expected_genesis_domain_hash=expected_genesis_domain_hash,
    )
    if payload != export_bootstrap_snapshot_json(verified):
        raise ValueError("bootstrap_snapshot_json_not_canonical")
    return verified


def compute_artifact_hash(payload: Mapping[str, Any]) -> str:
    """Compute the canonical SHA-256 hash for an artifact payload."""

    canonical = json.dumps(
        _canonicalize(payload),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _canonicalize(value: Any) -> Any:
    if isinstance(value, float):
        raise ValueError("float_values_forbidden")
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    return value


def _require_mapping(value: Any, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_text(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(token)
    return value


def _require_non_empty_text(value: Any, token: str) -> str:
    return _require_text(value, token)


def _require_lower_hex_64(value: Any, token: str) -> str:
    if not isinstance(value, str) or _LOWER_HEX_64_RE.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _validate_snapshot_epoch(value: Any) -> None:
    if type(value) is not int or value < 0:
        raise ValueError("snapshot_epoch_invalid")


def _normalize_epoch_checkpoint_range(
    value: Mapping[str, Any],
    *,
    snapshot_epoch: int,
) -> dict[str, int]:
    start = value.get("start_epoch")
    end = value.get("end_epoch")
    if type(start) is not int or type(end) is not int:
        raise ValueError("epoch_checkpoint_range_invalid")
    if start < 0 or end < start:
        raise ValueError("epoch_checkpoint_range_invalid")
    if snapshot_epoch < start or snapshot_epoch > end:
        raise ValueError("bootstrap_snapshot_epoch_range_stale")
    return {"end_epoch": end, "start_epoch": start}


def _normalize_authority_refs(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("authority_refs_required")
    refs = [_require_lower_hex_64(item, "authority_ref_invalid") for item in value]
    if not refs:
        raise ValueError("authority_refs_required")
    return sorted(refs)


def _normalize_lineage_chain(value: Any, *, genesis_domain_hash: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("lineage_proof_chain_required")
    chain = [_require_lower_hex_64(item, "lineage_ref_invalid") for item in value]
    if genesis_domain_hash not in chain:
        raise ValueError("lineage_proof_chain_missing_genesis")
    return chain


def _enforce_artifact_count(
    artifacts: Sequence[Mapping[str, Any]],
    max_artifacts: int,
) -> None:
    if type(max_artifacts) is not int or max_artifacts < 1:
        raise ValueError("max_artifacts_invalid")
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        raise ValueError("artifacts_sequence_required")
    if len(artifacts) > max_artifacts:
        raise ValueError("artifact_count_exceeded")


def _enforce_json_size(
    snapshot: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_JSON_BYTES,
) -> None:
    export_bootstrap_snapshot_json(snapshot, max_bytes=max_bytes)
