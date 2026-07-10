# SPDX-License-Identifier: AGPL-3.0-only
"""AtlasSliceManifest runtime for local homoiconic build-pipeline rehearsal.

PUBLIC_RC_EXCLUDE: atlas_slice_manifest_local_pipeline_rehearsal
PUBLIC_RC_EXCLUDE_REASON: Local pre-public-RC manifest builder/verifier. Ed25519 dev/test signing only; no Genesis signing ceremony, public publication, private export, or public RC activation.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes
from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.ledger.exact_numeric import normalize_json_scalars
from ilc_core.private_json_guardrails import (
    canonical_json,
    freeze_json_value,
    normalize_json_value,
    reject_float,
    thaw_json_value,
)
from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


ATLAS_SLICE_MANIFEST_RUNTIME_VERSION = "atlas_slice_manifest_1573ap.v0.1"
VALID_SLICE_VARIANTS = frozenset({"core", "bridge", "full"})
PUBLIC_SIGNABLE_PROJECTIONS = frozenset(
    {
        "genesis_core_star_map",
        "public_protocol_graph",
        "support_candidate_graph",
    }
)
EXCLUDED_PRIVATE_PROJECTION = "excluded_private_material"
EMPTY_MERKLE_ROOT_SHA256 = hashlib.sha256(b"").hexdigest()


@dataclass(frozen=True)
class AtlasSliceManifest:
    """Deterministic executable map for a bounded Atlas projection slice."""

    slice_id: str
    slice_version: str
    section_label: str
    source_lmdb_root_sha256: str
    projection_filter: str
    root_pointers: tuple[str, ...]
    content_entries: tuple[Mapping[object, object], ...]
    included_node_merkle_root: str
    cross_section_ref_count: int
    exclusion_policy: str
    semantic_loss_annotations: tuple[str, ...]
    privacy_budget: str
    installer_profile: str
    receipt_sha256: str | None
    canonical_json: str
    dag_cbor: bytes
    cidv1: str
    sha256: str
    cose_sign1: bytes = b""
    public_rc_exclude: bool = True
    dev_signed: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe manifest representation."""

        return {
            "canonical_json": self.canonical_json,
            "cidv1": self.cidv1,
            "content_entries": thaw_json_value(self.content_entries),
            "cose_sign1_b64": base64.b64encode(self.cose_sign1).decode("ascii"),
            "cross_section_ref_count": self.cross_section_ref_count,
            "dag_cbor_b64": base64.b64encode(self.dag_cbor).decode("ascii"),
            "dev_signed": self.dev_signed,
            "exclusion_policy": self.exclusion_policy,
            "included_node_merkle_root": self.included_node_merkle_root,
            "installer_profile": self.installer_profile,
            "privacy_budget": self.privacy_budget,
            "projection_filter": self.projection_filter,
            "public_rc_exclude": self.public_rc_exclude,
            "receipt_sha256": self.receipt_sha256,
            "root_pointers": list(self.root_pointers),
            "runtime_version": ATLAS_SLICE_MANIFEST_RUNTIME_VERSION,
            "section_label": self.section_label,
            "semantic_loss_annotations": list(self.semantic_loss_annotations),
            "sha256": self.sha256,
            "slice_id": self.slice_id,
            "slice_version": self.slice_version,
            "source_lmdb_root_sha256": self.source_lmdb_root_sha256,
        }


def build_atlas_slice_manifest(
    *,
    slice_version: str,
    section_label: str,
    source_lmdb_root_sha256: str,
    projection_filter: str,
    root_pointers: tuple[str, ...],
    content_entries: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
    cross_section_ref_count: int = 0,
    exclusion_policy: str = "no_excluded_private_material",
    semantic_loss_annotations: tuple[str, ...] = (),
    privacy_budget: str = "public",
    installer_profile: str = "installer_profile:local_dev_1573ap",
    receipt_sha256: str | None = None,
) -> AtlasSliceManifest:
    """Build an unsigned deterministic AtlasSliceManifest."""

    _validate_common_inputs(
        slice_version=slice_version,
        section_label=section_label,
        source_lmdb_root_sha256=source_lmdb_root_sha256,
        projection_filter=projection_filter,
        root_pointers=root_pointers,
        content_entries=content_entries,
        cross_section_ref_count=cross_section_ref_count,
        exclusion_policy=exclusion_policy,
        semantic_loss_annotations=semantic_loss_annotations,
        privacy_budget=privacy_budget,
        installer_profile=installer_profile,
        receipt_sha256=receipt_sha256,
    )
    normalized_entries = _normalize_content_entries(content_entries)
    included_node_merkle_root = _content_entries_merkle_root(normalized_entries)
    slice_id = _slice_id(
        {
            "content_entries": normalized_entries,
            "included_node_merkle_root": included_node_merkle_root,
            "projection_filter": projection_filter,
            "root_pointers": list(root_pointers),
            "section_label": section_label,
            "slice_version": slice_version,
            "source_lmdb_root_sha256": source_lmdb_root_sha256,
        }
    )
    envelope = _manifest_envelope(
        slice_id=slice_id,
        slice_version=slice_version,
        section_label=section_label,
        source_lmdb_root_sha256=source_lmdb_root_sha256,
        projection_filter=projection_filter,
        root_pointers=root_pointers,
        content_entries=normalized_entries,
        included_node_merkle_root=included_node_merkle_root,
        cross_section_ref_count=cross_section_ref_count,
        exclusion_policy=exclusion_policy,
        semantic_loss_annotations=semantic_loss_annotations,
        privacy_budget=privacy_budget,
        installer_profile=installer_profile,
        receipt_sha256=receipt_sha256,
    )
    manifest_canonical_json = canonical_json(
        envelope,
        float_token="atlas_slice_manifest_float_not_allowed",
    )
    dag_cbor = encode_dag_cbor(envelope)
    cidv1 = node_id_from_bytes(dag_cbor)
    return AtlasSliceManifest(
        slice_id=slice_id,
        slice_version=slice_version,
        section_label=section_label,
        source_lmdb_root_sha256=source_lmdb_root_sha256,
        projection_filter=projection_filter,
        root_pointers=tuple(root_pointers),
        content_entries=freeze_json_value(normalized_entries),  # type: ignore[arg-type]
        included_node_merkle_root=included_node_merkle_root,
        cross_section_ref_count=cross_section_ref_count,
        exclusion_policy=exclusion_policy,
        semantic_loss_annotations=tuple(semantic_loss_annotations),
        privacy_budget=privacy_budget,
        installer_profile=installer_profile,
        receipt_sha256=receipt_sha256,
        canonical_json=manifest_canonical_json,
        dag_cbor=dag_cbor,
        cidv1=cidv1,
        sha256=hashlib.sha256(dag_cbor).hexdigest(),
    )


def build_atlas_slice_manifest_from_lmdb(
    *,
    lmdb_path: str | Path,
    slice_variant: str,
    projection: str,
    slice_version: str = "0.1",
) -> AtlasSliceManifest:
    """Build an unsigned manifest from nodes matching an Atlas graph projection."""

    if slice_variant not in VALID_SLICE_VARIANTS:
        raise ValueError("atlas_slice_manifest_invalid_slice_variant")
    if projection == EXCLUDED_PRIVATE_PROJECTION:
        raise ValueError("atlas_slice_manifest_private_projection_blocked")
    if not projection:
        raise ValueError("atlas_slice_manifest_projection_missing")

    writer = AtlasLmdbSafeWriter(Path(lmdb_path))
    try:
        payload = writer.store.get_graph_payload() or {}
        nodes = [
            dict(node)
            for node in writer.store.iter_nodes()
            if str(node.get("graph_projection", "")) == projection
        ]
    finally:
        writer.close()
    if not nodes:
        raise ValueError("atlas_slice_manifest_projection_empty")
    nodes.sort(key=lambda node: str(node.get("candidate_id", "")))
    entries = [_content_entry_from_node(node) for node in nodes]
    root_pointers = tuple(str(entry["node_id"]) for entry in entries[:2])
    if not root_pointers:
        raise ValueError("atlas_slice_manifest_root_pointers_missing")
    return build_atlas_slice_manifest(
        slice_version=slice_version,
        section_label=slice_variant,
        source_lmdb_root_sha256=_sha256_json(payload),
        projection_filter=projection,
        root_pointers=root_pointers,
        content_entries=entries,
        cross_section_ref_count=_cross_section_ref_count(payload, projection),
        semantic_loss_annotations=(
            "1573ap_manifest_contains_node_record_hashes_not_materialized_blobs",
        ),
        installer_profile=f"installer_profile:{slice_variant}:{projection}:1573ap",
    )


def sign_atlas_slice_manifest(
    manifest: AtlasSliceManifest,
    *,
    private_key: ed25519.Ed25519PrivateKey,
    cose_kid: bytes | None = b"atlas-slice-dev-1573ap",
) -> AtlasSliceManifest:
    """Return a dev/test-signed manifest using the current Ed25519 COSE path."""

    cose_sign1 = cose_sign1_sign(manifest.dag_cbor, private_key, kid=cose_kid)
    return AtlasSliceManifest(
        **{
            **manifest.__dict__,
            "cose_sign1": cose_sign1,
            "dev_signed": True,
        }
    )


def verify_atlas_slice_manifest(
    manifest: AtlasSliceManifest,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
    require_signature: bool = True,
) -> bool:
    """Verify deterministic manifest commitments and optional dev/test signature."""

    rebuilt = build_atlas_slice_manifest(
        slice_version=manifest.slice_version,
        section_label=manifest.section_label,
        source_lmdb_root_sha256=manifest.source_lmdb_root_sha256,
        projection_filter=manifest.projection_filter,
        root_pointers=manifest.root_pointers,
        content_entries=thaw_json_value(manifest.content_entries),  # type: ignore[arg-type]
        cross_section_ref_count=manifest.cross_section_ref_count,
        exclusion_policy=manifest.exclusion_policy,
        semantic_loss_annotations=manifest.semantic_loss_annotations,
        privacy_budget=manifest.privacy_budget,
        installer_profile=manifest.installer_profile,
        receipt_sha256=manifest.receipt_sha256,
    )
    deterministic_fields_match = (
        rebuilt.slice_id == manifest.slice_id
        and rebuilt.canonical_json == manifest.canonical_json
        and rebuilt.dag_cbor == manifest.dag_cbor
        and rebuilt.cidv1 == manifest.cidv1
        and rebuilt.sha256 == manifest.sha256
        and manifest.public_rc_exclude is True
    )
    if not deterministic_fields_match:
        raise ValueError("atlas_slice_manifest_commitment_mismatch")
    if manifest.cose_sign1 == b"":
        if require_signature:
            raise ValueError("atlas_slice_manifest_signature_missing")
        return True
    if public_key is None:
        raise ValueError("atlas_slice_manifest_public_key_missing")
    try:
        verified = cose_sign1_verify(manifest.cose_sign1, public_key)
    except (InvalidSignature, ValueError) as exc:
        raise ValueError("atlas_slice_manifest_signature_invalid") from exc
    if verified["nodeid"] != manifest.cidv1 or verified["payload"] != manifest.dag_cbor:
        raise ValueError("atlas_slice_manifest_signature_payload_mismatch")
    return True


def manifest_from_json_dict(payload: Mapping[str, object]) -> AtlasSliceManifest:
    """Parse and verify a JSON-safe manifest representation."""

    reject_float(payload, "atlas_slice_manifest_float_not_allowed")
    content_entries = payload.get("content_entries")
    root_pointers = payload.get("root_pointers")
    semantic_loss_annotations = payload.get("semantic_loss_annotations", ())
    if not isinstance(content_entries, list):
        raise ValueError("atlas_slice_manifest_content_entries_invalid")
    if not isinstance(root_pointers, list) or not all(
        isinstance(item, str) for item in root_pointers
    ):
        raise ValueError("atlas_slice_manifest_root_pointers_invalid")
    if not isinstance(semantic_loss_annotations, list) or not all(
        isinstance(item, str) for item in semantic_loss_annotations
    ):
        raise ValueError("atlas_slice_manifest_semantic_loss_invalid")
    rebuilt = build_atlas_slice_manifest(
        slice_version=_require_str(payload, "slice_version"),
        section_label=_require_str(payload, "section_label"),
        source_lmdb_root_sha256=_require_str(payload, "source_lmdb_root_sha256"),
        projection_filter=_require_str(payload, "projection_filter"),
        root_pointers=tuple(root_pointers),
        content_entries=content_entries,
        cross_section_ref_count=_require_int(payload, "cross_section_ref_count"),
        exclusion_policy=_require_str(payload, "exclusion_policy"),
        semantic_loss_annotations=tuple(semantic_loss_annotations),
        privacy_budget=_require_str(payload, "privacy_budget"),
        installer_profile=_require_str(payload, "installer_profile"),
        receipt_sha256=_optional_str(payload, "receipt_sha256"),
    )
    cose_value = payload.get("cose_sign1_b64", "")
    if not isinstance(cose_value, str):
        raise ValueError("atlas_slice_manifest_cose_invalid")
    try:
        cose_sign1 = base64.b64decode(cose_value.encode("ascii"), validate=True)
    except Exception as exc:
        raise ValueError("atlas_slice_manifest_cose_invalid") from exc
    manifest = AtlasSliceManifest(
        **{
            **rebuilt.__dict__,
            "cose_sign1": cose_sign1,
            "dev_signed": bool(payload.get("dev_signed", False)),
        }
    )
    if manifest.to_json_dict()["canonical_json"] != payload.get("canonical_json"):
        raise ValueError("atlas_slice_manifest_canonical_json_mismatch")
    if manifest.to_json_dict()["dag_cbor_b64"] != payload.get("dag_cbor_b64"):
        raise ValueError("atlas_slice_manifest_dag_cbor_mismatch")
    if manifest.cidv1 != payload.get("cidv1"):
        raise ValueError("atlas_slice_manifest_cid_mismatch")
    if manifest.sha256 != payload.get("sha256"):
        raise ValueError("atlas_slice_manifest_sha_mismatch")
    return manifest


def load_atlas_slice_manifest(path: str | Path) -> AtlasSliceManifest:
    """Load a manifest from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("atlas_slice_manifest_json_not_object")
    return manifest_from_json_dict(data)


def write_atlas_slice_manifest(path: str | Path, manifest: AtlasSliceManifest) -> None:
    """Atomically write a manifest JSON file."""

    write_json_atomic(Path(path), manifest.to_json_dict())


def write_json_atomic(path: Path, payload: Mapping[str, object]) -> None:
    """Atomically write deterministic JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        normalize_json_scalars(thaw_json_value(payload)),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _manifest_envelope(
    *,
    slice_id: str,
    slice_version: str,
    section_label: str,
    source_lmdb_root_sha256: str,
    projection_filter: str,
    root_pointers: tuple[str, ...],
    content_entries: list[dict[str, object]],
    included_node_merkle_root: str,
    cross_section_ref_count: int,
    exclusion_policy: str,
    semantic_loss_annotations: tuple[str, ...],
    privacy_budget: str,
    installer_profile: str,
    receipt_sha256: str | None,
) -> dict[str, object]:
    return {
        "content_entries": content_entries,
        "cross_section_ref_count": cross_section_ref_count,
        "exclusion_policy": exclusion_policy,
        "included_node_merkle_root": included_node_merkle_root,
        "installer_profile": installer_profile,
        "privacy_budget": privacy_budget,
        "projection_filter": projection_filter,
        "public_rc_exclude": True,
        "receipt_sha256": receipt_sha256,
        "root_pointers": list(root_pointers),
        "runtime_version": ATLAS_SLICE_MANIFEST_RUNTIME_VERSION,
        "section_label": section_label,
        "semantic_loss_annotations": list(semantic_loss_annotations),
        "slice_id": slice_id,
        "slice_version": slice_version,
        "source_lmdb_root_sha256": source_lmdb_root_sha256,
    }


def _validate_common_inputs(
    *,
    slice_version: str,
    section_label: str,
    source_lmdb_root_sha256: str,
    projection_filter: str,
    root_pointers: tuple[str, ...],
    content_entries: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
    cross_section_ref_count: int,
    exclusion_policy: str,
    semantic_loss_annotations: tuple[str, ...],
    privacy_budget: str,
    installer_profile: str,
    receipt_sha256: str | None,
) -> None:
    reject_float(
        {
            "content_entries": content_entries,
            "cross_section_ref_count": cross_section_ref_count,
            "receipt_sha256": receipt_sha256,
            "root_pointers": root_pointers,
            "semantic_loss_annotations": semantic_loss_annotations,
        },
        "atlas_slice_manifest_float_not_allowed",
    )
    for value, token in (
        (slice_version, "atlas_slice_manifest_version_missing"),
        (section_label, "atlas_slice_manifest_section_label_missing"),
        (source_lmdb_root_sha256, "atlas_slice_manifest_source_root_missing"),
        (projection_filter, "atlas_slice_manifest_projection_missing"),
        (exclusion_policy, "atlas_slice_manifest_exclusion_policy_missing"),
        (privacy_budget, "atlas_slice_manifest_privacy_budget_missing"),
        (installer_profile, "atlas_slice_manifest_installer_profile_missing"),
    ):
        if not isinstance(value, str) or not value:
            raise ValueError(token)
    _require_sha256_hex(source_lmdb_root_sha256, "atlas_slice_manifest_source_root_invalid")
    if receipt_sha256 is not None:
        _require_sha256_hex(receipt_sha256, "atlas_slice_manifest_receipt_sha_invalid")
    if (
        isinstance(cross_section_ref_count, bool)
        or not isinstance(cross_section_ref_count, int)
        or cross_section_ref_count < 0
    ):
        raise ValueError("atlas_slice_manifest_cross_section_ref_count_invalid")
    if not root_pointers or not all(isinstance(item, str) and item for item in root_pointers):
        raise ValueError("atlas_slice_manifest_root_pointers_invalid")
    if not isinstance(semantic_loss_annotations, tuple) or not all(
        isinstance(item, str) for item in semantic_loss_annotations
    ):
        raise ValueError("atlas_slice_manifest_semantic_loss_invalid")
    if not content_entries:
        raise ValueError("atlas_slice_manifest_content_entries_empty")


def _normalize_content_entries(
    content_entries: list[Mapping[str, object]] | tuple[Mapping[str, object], ...],
) -> list[dict[str, object]]:
    normalized_entries: list[dict[str, object]] = []
    seen: set[str] = set()
    for entry in content_entries:
        normalized = normalize_json_value(entry)
        if not isinstance(normalized, dict):
            raise ValueError("atlas_slice_manifest_content_entry_invalid")
        node_id = str(normalized.get("node_id", "") or normalized.get("candidate_id", ""))
        if not node_id:
            raise ValueError("atlas_slice_manifest_content_entry_node_id_missing")
        if node_id in seen:
            raise ValueError("atlas_slice_manifest_duplicate_content_entry")
        seen.add(node_id)
        record_sha256 = str(normalized.get("record_sha256", ""))
        _require_sha256_hex(record_sha256, "atlas_slice_manifest_content_entry_sha_invalid")
        normalized["node_id"] = node_id
        normalized_entries.append(normalized)
    normalized_entries.sort(key=lambda row: str(row["node_id"]))
    return normalized_entries


def _content_entry_from_node(node: Mapping[str, object]) -> dict[str, object]:
    node_id = str(node.get("candidate_id", ""))
    if not node_id:
        raise ValueError("atlas_slice_manifest_node_missing_candidate_id")
    return {
        "graph_projection": str(node.get("graph_projection", "")),
        "node_id": node_id,
        "node_kind": str(node.get("node_kind", "")),
        "record_sha256": _sha256_json(node),
        "source_path": str(node.get("source_path", "")),
    }


def _content_entries_merkle_root(entries: list[dict[str, object]]) -> str:
    if not entries:
        return EMPTY_MERKLE_ROOT_SHA256
    leaves = [str(entry["record_sha256"]) for entry in entries]
    payload = "\n".join(sorted(leaves)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _slice_id(payload: Mapping[str, object]) -> str:
    return node_id_from_bytes(encode_dag_cbor(normalize_json_value(payload)))


def _sha256_json(payload: Mapping[object, object]) -> str:
    encoded = json.dumps(
        normalize_json_scalars(thaw_json_value(normalize_json_value(payload))),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _cross_section_ref_count(payload: Mapping[str, object], projection: str) -> int:
    edges = payload.get("edges", [])
    if not isinstance(edges, list):
        return 0
    count = 0
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        if str(edge.get("edge_type", "")) != "CROSS_SECTION_REF":
            continue
        if str(edge.get("graph_projection", "")) == projection:
            count += 1
    return count


def _require_sha256_hex(value: str, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(token)


def _require_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or (key != "receipt_sha256" and value == ""):
        raise ValueError(f"atlas_slice_manifest_{key}_invalid")
    return value


def _optional_str(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"atlas_slice_manifest_{key}_invalid")
    return value


def _require_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"atlas_slice_manifest_{key}_invalid")
    return value


__all__ = [
    "ATLAS_SLICE_MANIFEST_RUNTIME_VERSION",
    "AtlasSliceManifest",
    "build_atlas_slice_manifest",
    "build_atlas_slice_manifest_from_lmdb",
    "load_atlas_slice_manifest",
    "manifest_from_json_dict",
    "sign_atlas_slice_manifest",
    "verify_atlas_slice_manifest",
    "write_atlas_slice_manifest",
]
