# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic Genesis package membership manifest helpers.

PUBLIC_RC_EXCLUDE: fix65_genesis_package_membership_manifest_local
PUBLIC_RC_EXCLUDE_REASON: Pre-RC manifest construction helper. It computes an
unsigned package-membership root for local Atlas verification only; it does not
sign Genesis material, authorize public distribution, activate public RC, or
clear export gates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


GENESIS_PACKAGE_MANIFEST_VERSION = "genesis_package_membership_manifest_1545p_fix65.v0.1"
GENESIS_PACKAGE_ARTIFACT_ID = "artifact:genesis_package_merkle_root_v0.4"
GENESIS_PACKAGE_PROFILE_ID = "genesis_public_protocol_graph_v0.4"
PUBLIC_PROTOCOL_GRAPH_PROJECTION = "public_protocol_graph"
PUBLIC_RC_EXCLUDE_MARKER = b"PUBLIC_RC_EXCLUDE"


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def file_sha256(path: Path, *, chunk_size: int = 65_536) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def file_contains_public_rc_exclude(path: Path, *, chunk_size: int = 65_536) -> bool:
    """Return True if marker bytes are present without loading unbounded files."""

    overlap = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                return False
            window = overlap + chunk
            if PUBLIC_RC_EXCLUDE_MARKER in window:
                return True
            overlap = window[-len(PUBLIC_RC_EXCLUDE_MARKER) + 1 :]


def package_role_for_path(source_path: str) -> str:
    path = Path(source_path)
    if source_path.startswith("ilc_core/bundle/"):
        return "adr_0009_bundle_runtime"
    if source_path.startswith("ilc_core/cli/"):
        return "cli_runtime"
    if source_path.startswith("ilc_core/storage/"):
        return "storage_runtime"
    if source_path.startswith("ilc_core/"):
        return "core_runtime"
    if source_path.startswith("docs/adr/"):
        return "adr_document"
    if source_path.startswith("docs/specs/"):
        return "spec_document"
    if path.name == "sidecars.md":
        return "sidecar_document"
    return "package_material"


def _candidate_id(node: Mapping[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("genesis_package_manifest_node_missing_candidate_id")
    return value


def _source_path(node: Mapping[str, Any]) -> str:
    value = node.get("source_path")
    if not isinstance(value, str) or not value:
        raise ValueError(f"genesis_package_manifest_missing_source_path:{_candidate_id(node)}")
    return value


def _source_sha256(node: Mapping[str, Any]) -> str:
    value = node.get("source_sha256")
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"genesis_package_manifest_invalid_source_sha256:{_candidate_id(node)}")
    return value


def build_package_members(
    nodes: Iterable[Mapping[str, Any]],
    *,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """Select content-addressed public-protocol repo files for the M0 manifest."""

    members: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for node in nodes:
        candidate_id = _candidate_id(node)
        if not candidate_id.startswith("repo:file:"):
            continue
        if node.get("graph_projection") != PUBLIC_PROTOCOL_GRAPH_PROJECTION:
            continue
        source_path = _source_path(node)
        if source_path.startswith("out/"):
            raise ValueError(f"genesis_package_manifest_out_path_forbidden:{candidate_id}")
        if source_path in seen_paths:
            raise ValueError(f"genesis_package_manifest_duplicate_source_path:{source_path}")
        seen_paths.add(source_path)
        source_sha256 = _source_sha256(node)
        absolute_path = repo_root / source_path
        if not absolute_path.is_file():
            raise ValueError(f"genesis_package_manifest_source_missing:{source_path}")
        actual_sha256 = file_sha256(absolute_path)
        if actual_sha256 != source_sha256:
            raise ValueError(f"genesis_package_manifest_source_sha256_mismatch:{source_path}")
        size_bytes = absolute_path.stat().st_size
        base_row = {
            "candidate_id": candidate_id,
            "graph_projection": PUBLIC_PROTOCOL_GRAPH_PROJECTION,
            "node_kind": str(node.get("node_kind", "")),
            "package_role": package_role_for_path(source_path),
            "public_rc_exclude_marker_present": file_contains_public_rc_exclude(absolute_path),
            "size_bytes": size_bytes,
            "source_path": source_path,
            "source_sha256": source_sha256,
        }
        members.append({**base_row, "member_digest_sha256": canonical_sha256(base_row)})
    return sorted(members, key=lambda item: (item["source_path"], item["candidate_id"]))


def merkle_root_from_member_digests(member_digests: Sequence[str]) -> str:
    if not member_digests:
        return hashlib.sha256(b"").hexdigest()
    level = sorted(member_digests)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        next_level: list[str] = []
        for index in range(0, len(level), 2):
            left = bytes.fromhex(level[index])
            right = bytes.fromhex(level[index + 1])
            next_level.append(hashlib.sha256(left + right).hexdigest())
        level = next_level
    return level[0]


def build_genesis_package_manifest(
    nodes: Iterable[Mapping[str, Any]],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    members = build_package_members(nodes, repo_root=repo_root)
    marker_count = sum(1 for member in members if member["public_rc_exclude_marker_present"])
    manifest: dict[str, Any] = {
        "artifact_id": GENESIS_PACKAGE_ARTIFACT_ID,
        "graph_projection": PUBLIC_PROTOCOL_GRAPH_PROJECTION,
        "manifest_status": "unsigned_pre_rc_candidate",
        "member_count": len(members),
        "members": members,
        "merkle_algorithm": "sha256_binary_tree_duplicate_last_sorted_member_digests",
        "merkle_root_m0": merkle_root_from_member_digests(
            [member["member_digest_sha256"] for member in members]
        ),
        "non_claims": [
            "no_genesis_signing",
            "no_public_rc_activation",
            "no_public_distribution_authority",
            "public_rc_exclude_marker_count_blocks_public_clean_claim",
        ],
        "package_profile_id": GENESIS_PACKAGE_PROFILE_ID,
        "public_rc_exclude_marker_count": marker_count,
        "schema_version": GENESIS_PACKAGE_MANIFEST_VERSION,
        "selection_rule": (
            "repo:file nodes in the unified Genesis Atlas LMDB with "
            "graph_projection == public_protocol_graph, source_path present, "
            "source_sha256 present, source path not under out/, and source hash "
            "matching current repo bytes"
        ),
        "signed": False,
        "source_lmdb": "out/genesis_base_graph_v0.4_unified.lmdb",
    }
    manifest["manifest_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    return manifest
