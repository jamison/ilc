#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build a local release-slice AtlasSliceManifest from release assertion JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

from ilc_core.bundle.atlas_slice_manifest import (
    build_atlas_slice_manifest,
    manifest_from_json_dict,
    verify_atlas_slice_manifest,
    write_atlas_slice_manifest,
)
from ilc_core.encoding.cidv1 import node_id_from_obj


DEFAULT_RELEASE_ASSERTION_PATH = Path(
    "out/gap_release_assertion_publish_ceremony_00/release_assertion_core.json"
)
DEFAULT_PHASE = "GAP-RELEASE-SLICE-MANIFEST-PUBLISH-00"
HEX_32_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")


class ReleaseSliceManifestError(ValueError):
    """Stable-token exception for the release slice manifest tool."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _require_object(value: Any, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReleaseSliceManifestError(token)
    return value


def _require_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReleaseSliceManifestError(token)
    return value


def _require_sha256(value: Any, token: str) -> str:
    text = _require_string(value, token)
    if HEX_32_RE.fullmatch(text) is None:
        raise ReleaseSliceManifestError(token)
    return text


def _content_entry(
    *,
    node_id: str,
    node_kind: str,
    record: Mapping[str, Any],
    source_path: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "graph_projection": "public_protocol_graph",
        "node_id": node_id,
        "node_kind": node_kind,
        "record_sha256": _sha256_json(record),
        "source_path": source_path,
    }
    if extra:
        row.update(dict(extra))
    return row


def _load_release_assertion(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReleaseSliceManifestError("release_assertion_core_missing") from exc
    except json.JSONDecodeError as exc:
        raise ReleaseSliceManifestError("release_assertion_core_invalid_json") from exc
    return _require_object(payload, "release_assertion_core_not_object")


def build_release_slice_manifest(
    *,
    release_assertion_path: Path = DEFAULT_RELEASE_ASSERTION_PATH,
    version: str,
    source_commit: str,
    channel: str = "public_rc",
) -> dict[str, Any]:
    """Return the unsigned release-slice manifest JSON payload."""

    if VERSION_RE.fullmatch(version) is None:
        raise ReleaseSliceManifestError("release_slice_manifest_version_invalid")
    if GIT_SHA_RE.fullmatch(source_commit) is None:
        raise ReleaseSliceManifestError("release_slice_manifest_source_commit_invalid")
    assertion = _load_release_assertion(release_assertion_path)
    release_node = _require_object(
        assertion.get("software_release_node"),
        "software_release_node_missing",
    )
    if release_node.get("version") != version:
        raise ReleaseSliceManifestError("release_slice_manifest_version_mismatch")
    if release_node.get("source_commit") != source_commit:
        raise ReleaseSliceManifestError("release_slice_manifest_source_commit_mismatch")
    release_node_cid = _require_string(release_node.get("cid"), "software_release_node_cid_missing")
    assertion_cid = _require_string(assertion.get("assertion_cid"), "assertion_cid_missing")
    artifact_nodes_raw = assertion.get("artifact_nodes")
    if not isinstance(artifact_nodes_raw, list) or not artifact_nodes_raw:
        raise ReleaseSliceManifestError("artifact_nodes_missing")
    build_recipe_nodes_raw = assertion.get("build_recipe_nodes")
    if not isinstance(build_recipe_nodes_raw, list) or not build_recipe_nodes_raw:
        raise ReleaseSliceManifestError("build_recipe_nodes_missing")

    content_entries: list[dict[str, Any]] = []
    root_pointers = [assertion_cid, release_node_cid]
    for index, raw_node in enumerate(artifact_nodes_raw):
        node = _require_object(raw_node, "artifact_node_invalid")
        node_id = _require_string(node.get("cid"), "artifact_node_cid_missing")
        content_entries.append(
            _content_entry(
                node_id=node_id,
                node_kind="ArtifactNode",
                record=node,
                source_path=f"{release_assertion_path}#artifact_nodes[{index}]",
                extra={
                    "artifact_id": _require_string(node.get("artifact_id"), "artifact_id_missing"),
                    "artifact_type": _require_string(
                        node.get("artifact_type"),
                        "artifact_type_missing",
                    ),
                    "artifact_sha256": _require_sha256(
                        node.get("sha256"),
                        "artifact_sha256_invalid",
                    ),
                    "size_bytes": node.get("size_bytes"),
                },
            )
        )
    for index, raw_node in enumerate(build_recipe_nodes_raw):
        node = _require_object(raw_node, "build_recipe_node_invalid")
        node_id = _require_string(
            node.get("cid") or node_id_from_obj(dict(node)),
            "build_recipe_node_cid_missing",
        )
        content_entries.append(
            _content_entry(
                node_id=node_id,
                node_kind="BuildRecipeNode",
                record=node,
                source_path=f"{release_assertion_path}#build_recipe_nodes[{index}]",
            )
        )
    content_entries.append(
        _content_entry(
            node_id=release_node_cid,
            node_kind="SoftwareReleaseNode",
            record=release_node,
            source_path=f"{release_assertion_path}#software_release_node",
            extra={"version": version, "release_channel": channel},
        )
    )
    content_entries.append(
        _content_entry(
            node_id=assertion_cid,
            node_kind="software_release_assertion",
            record=assertion,
            source_path=str(release_assertion_path),
            extra={"assertion_cid": assertion_cid},
        )
    )

    source_root = _sha256_json(
        {
            "assertion_cid": assertion_cid,
            "release_assertion_path": str(release_assertion_path),
            "source_commit": source_commit,
            "version": version,
        }
    )
    receipt_sha256 = _sha256_json(assertion)
    manifest = build_atlas_slice_manifest(
        slice_version=version,
        section_label="release",
        source_lmdb_root_sha256=source_root,
        projection_filter="public_protocol_graph",
        root_pointers=tuple(root_pointers),
        content_entries=content_entries,
        cross_section_ref_count=0,
        exclusion_policy="no_excluded_private_material",
        semantic_loss_annotations=(
            "release_slice_manifest_derives_from_existing_release_assertion_without_retroactive_mutation",
            "source_urls_are_retrieval_hints_not_release_authority",
        ),
        privacy_budget="public",
        installer_profile=f"installer_profile:release:ilc-core:{version}:{DEFAULT_PHASE}",
        receipt_sha256=receipt_sha256,
    )
    verify_atlas_slice_manifest(manifest, require_signature=False)
    parsed = manifest_from_json_dict(manifest.to_json_dict())
    verify_atlas_slice_manifest(parsed, require_signature=False)
    return manifest.to_json_dict()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--channel", default="public_rc")
    parser.add_argument("--release-assertion", type=Path, default=DEFAULT_RELEASE_ASSERTION_PATH)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print manifest JSON without writing the output path.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = build_release_slice_manifest(
            release_assertion_path=args.release_assertion,
            version=args.version,
            source_commit=args.source_commit,
            channel=args.channel,
        )
        if not args.dry_run:
            write_atlas_slice_manifest(args.output, manifest_from_json_dict(payload))
        sys.stdout.write(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False))
        sys.stdout.write("\n")
        return 0
    except ReleaseSliceManifestError as exc:
        print(exc.token, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
