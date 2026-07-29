#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the Phase 1142s Genesis node attestation manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
STAR_MAP = REPO_ROOT / "out" / "genesis_core_star_map_v0.1.json"
OUT = REPO_ROOT / "out" / "genesis_node_attestation_manifest_v0.1.json"
CEREMONY_DATE = "2026-05-03"
SIGNABLE_NODE_EXCLUDED_FIELDS = (
    "signature_status",
    "signature_envelope_ref",
    "signature_file_ref",
    "star_map_version",
)


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(obj) + b"\n")


def _signable_node_payload(node: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in node.items()
        if key not in SIGNABLE_NODE_EXCLUDED_FIELDS
    }


def build_manifest(star_map_path: Path = STAR_MAP) -> dict[str, Any]:
    star_map = _load_json(star_map_path)
    nodes = [
        node for node in star_map["nodes"]
        if node.get("genesis_attested") is True
    ]
    if len(nodes) != 32:
        raise ValueError(f"genesis_attested_node_count_must_be_32:{len(nodes)}")

    entries = []
    for node in sorted(nodes, key=lambda item: item["candidate_id"]):
        payload = _signable_node_payload(node)
        entries.append(
            {
                "candidate_id": node["candidate_id"],
                "canonical_hash": _sha256_bytes(_canonical_bytes(payload)),
            }
        )

    manifest = {
        "attestation_scope": "genesis_intent_attestation_and_init_authority_map_v0.1",
        "attestation_source": "docs/specs/ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md",
        "canonicalization": "json.dumps(sort_keys=True,separators=(',', ':'),allow_nan=False)",
        "issuer": "genesis_agent:01",
        "manifest_created": CEREMONY_DATE,
        "manifest_hash": None,
        "manifest_type": "genesis_node_attestation_manifest",
        "manifest_version": "v0.1",
        "node_hash_algorithm": "sha256_canonical_json",
        "node_hash_excluded_fields": list(SIGNABLE_NODE_EXCLUDED_FIELDS),
        "nodes": entries,
        "public_key_ref": "artifact:genesis_agent1_pubkey_record_838a",
    }
    manifest["manifest_hash"] = _sha256_bytes(_canonical_bytes(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--star-map", type=Path, default=STAR_MAP)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    manifest = build_manifest(args.star_map)
    _write_json(args.out, manifest)
    print(manifest["manifest_hash"])


if __name__ == "__main__":
    main()
