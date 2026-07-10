# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573y Fix65b section-level integrity audit for Atlas LMDB.

PUBLIC_RC_EXCLUDE: block6_lmdb_integrity_audit_tool
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance/audit tool. No
public graph publication, Genesis signing, public RC activation, or release
authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from ilc_core.distribution.genesis_package_manifest import file_sha256
from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


DEFAULT_LMDB = Path("out/genesis_base_graph_v0.4_unified.lmdb")
DEFAULT_RECEIPT = Path("out/phase_1573y/fix65b_section_integrity_audit.json")
SCRIPT_VERSION = "fix65b_section_integrity_audit_1573y.v0.1"


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def merkle_root_from_digests(digests: Iterable[str]) -> str:
    level = sorted(digests)
    if not level:
        return hashlib.sha256(b"").hexdigest()
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha256(bytes.fromhex(level[index]) + bytes.fromhex(level[index + 1])).hexdigest()
            for index in range(0, len(level), 2)
        ]
    return level[0]


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def build_receipt(lmdb: Path, repo_root: Path) -> dict[str, Any]:
    store = GenesisAtlasCandidateStore(lmdb, allow_synthetic_edge_keys=True)
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
        section_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
        mismatch_rows: list[dict[str, str]] = []
        missing_file_rows: list[dict[str, str]] = []
        missing_sha_rows: list[dict[str, str]] = []
        duplicate_paths: Counter[str] = Counter()
        cross_section_refs = 0
        unresolved_cross_section_refs = 0
        node_sections = {
            str(node.get("candidate_id", "")): str(node.get("graph_projection", ""))
            for node in nodes
        }

        for node in nodes:
            projection = str(node.get("graph_projection", "") or "UNSET")
            source_path = node.get("source_path")
            source_sha256 = node.get("source_sha256")
            if isinstance(source_path, str) and source_path:
                duplicate_paths[source_path] += 1
            if (
                isinstance(source_path, str)
                and source_path
                and isinstance(source_sha256, str)
                and len(source_sha256) == 64
            ):
                path = repo_root / source_path
                if not path.is_file():
                    missing_file_rows.append(
                        {
                            "candidate_id": str(node.get("candidate_id", "")),
                            "source_path": source_path,
                        }
                    )
                    continue
                actual = file_sha256(path)
                if actual != source_sha256:
                    mismatch_rows.append(
                        {
                            "actual_sha256": actual,
                            "candidate_id": str(node.get("candidate_id", "")),
                            "recorded_sha256": source_sha256,
                            "source_path": source_path,
                        }
                    )
                    continue
                member = {
                    "candidate_id": str(node.get("candidate_id", "")),
                    "source_path": source_path,
                    "source_sha256": source_sha256,
                }
                member["member_digest_sha256"] = canonical_sha256(member)
                section_members[projection].append(member)
            elif isinstance(source_path, str) and source_path:
                missing_sha_rows.append(
                    {
                        "candidate_id": str(node.get("candidate_id", "")),
                        "source_path": source_path,
                    }
                )

        for edge in edges:
            edge_type = str(edge.get("edge_type", ""))
            source = str(edge.get("source_candidate_id", edge.get("source", edge.get("from", ""))))
            target = str(edge.get("target_candidate_id", edge.get("target", edge.get("to", ""))))
            if edge_type == "CROSS_SECTION_REF" or (
                source in node_sections
                and target in node_sections
                and node_sections[source] != node_sections[target]
            ):
                cross_section_refs += 1
                if source not in node_sections or target not in node_sections:
                    unresolved_cross_section_refs += 1

        sections = []
        for projection, members in sorted(section_members.items()):
            member_digests = [member["member_digest_sha256"] for member in members]
            sections.append(
                {
                    "included_member_count": len(members),
                    "included_node_merkle_root": merkle_root_from_digests(member_digests),
                    "section_label": projection,
                }
            )

        duplicate_source_paths = [
            {"count": count, "source_path": path}
            for path, count in sorted(duplicate_paths.items())
            if count > 1
        ]
        # Missing or drifted historical source hashes are evidence for later
        # identity-refresh work, not safe automatic mutation targets here.
        status = "PASS" if unresolved_cross_section_refs == 0 else "FAIL"
        receipt = {
            "automatic_source_sha256_rewrite": "not_performed_historical_identity_preserved",
            "carry_forward_identity_refresh_note": (
                "missing or mismatched source_sha256 rows are reported but not "
                "rewritten because many rows are historical content-addressed "
                "identities whose source files have intentionally changed"
            ),
            "cross_section_ref_count": cross_section_refs,
            "duplicate_source_path_count": len(duplicate_source_paths),
            "duplicate_source_path_sample": duplicate_source_paths[:20],
            "lmdb_path": str(lmdb),
            "missing_file_count": len(missing_file_rows),
            "missing_file_sample": missing_file_rows[:20],
            "missing_source_sha256_count": len(missing_sha_rows),
            "mismatched_source_sha256_count": len(mismatch_rows),
            "mismatched_source_sha256_sample": mismatch_rows[:20],
            "node_count": len(nodes),
            "script_version": SCRIPT_VERSION,
            "section_count": len(sections),
            "section_manifests": sections,
            "section_manifest_merkle_root": merkle_root_from_digests(
                [canonical_sha256(section) for section in sections]
            ),
            "sequential_write_discipline": True,
            "status": status,
            "unresolved_cross_section_ref_count": unresolved_cross_section_refs,
        }
        return receipt
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lmdb", type=Path, default=DEFAULT_LMDB)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    receipt = build_receipt(args.lmdb, args.repo_root)
    write_json_atomic(args.receipt, receipt)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False))
    if receipt["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
