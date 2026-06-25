from __future__ import annotations

import json
from pathlib import Path

from ilc_core.distribution.genesis_package_manifest import (
    GENESIS_PACKAGE_ARTIFACT_ID,
    GENESIS_PACKAGE_MANIFEST_VERSION,
    build_genesis_package_manifest,
    canonical_sha256,
    merkle_root_from_member_digests,
)
from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
MANIFEST_PATH = ROOT / "docs/specs/ilc_fix65_package_membership_manifest_v0.1.json"
REPORT_PATH = ROOT / "docs/specs/ilc_fix65_package_membership_report_v0.1.md"
FIX82_REPORT_PATH = ROOT / "docs/specs/ilc_fix82_build_package_closure_v0.1.json"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_1545p_fix65_package_membership_manifest_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
EVALUATOR_PATH = ROOT / "tools/evaluators/sim_genesis_atlas_fix65_package_membership_manifest.py"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _lmdb() -> tuple[list[dict], list[dict]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def test_fix65_manifest_exists_and_is_canonical_json() -> None:
    manifest = _manifest()
    assert manifest["schema_version"] == GENESIS_PACKAGE_MANIFEST_VERSION
    assert manifest["signed"] is False
    assert MANIFEST_PATH.read_text(encoding="utf-8") == (
        json.dumps(manifest, allow_nan=False, separators=(",", ":"), sort_keys=True) + "\n"
    )


def test_fix65_merkle_root_recomputes_from_members() -> None:
    manifest = _manifest()
    member_digests = [member["member_digest_sha256"] for member in manifest["members"]]
    assert manifest["merkle_root_m0"] == merkle_root_from_member_digests(member_digests)
    without_manifest_hash = {
        key: value for key, value in manifest.items() if key != "manifest_sha256"
    }
    assert manifest["manifest_sha256"] == canonical_sha256(without_manifest_hash)


def test_fix65_manifest_member_set_matches_live_public_protocol_repo_files() -> None:
    nodes, _edges = _lmdb()
    expected = build_genesis_package_manifest(nodes, repo_root=ROOT)
    manifest = _manifest()
    assert manifest["member_count"] == expected["member_count"]
    assert manifest["merkle_root_m0"] == expected["merkle_root_m0"]
    assert manifest["manifest_sha256"] == expected["manifest_sha256"]
    assert manifest["public_rc_exclude_marker_count"] == expected["public_rc_exclude_marker_count"]
    assert manifest["member_count"] >= 400
    assert manifest["public_rc_exclude_marker_count"] > 0
    assert all(not member["source_path"].startswith("out/") for member in manifest["members"])


def test_fix65_lmdb_artifact_node_and_contains_edges_present() -> None:
    nodes, edges = _lmdb()
    manifest = _manifest()
    artifact = next(node for node in nodes if node.get("candidate_id") == GENESIS_PACKAGE_ARTIFACT_ID)
    assert artifact["merkle_root_m0"] == manifest["merkle_root_m0"]
    assert artifact["package_member_count"] == manifest["member_count"]
    contains_targets = {
        edge.get("target")
        for edge in edges
        if edge.get("source") == GENESIS_PACKAGE_ARTIFACT_ID
        and edge.get("edge_type") == "CONTAINS_FILE"
    }
    assert contains_targets == {member["candidate_id"] for member in manifest["members"]}


def test_fix65_report_walkthrough_and_status_tokens_present() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")
    status = STATUS_PATH.read_text(encoding="utf-8")
    manifest = _manifest()
    if manifest["merkle_root_m0"] not in report:
        fix82 = json.loads(FIX82_REPORT_PATH.read_text(encoding="utf-8"))
        refreshed = fix82["fix65_manifest_refresh"]
        assert refreshed["merkle_root_m0"] == manifest["merkle_root_m0"]
        assert refreshed["manifest_sha256"] == manifest["manifest_sha256"]
    else:
        assert manifest["manifest_sha256"] in report
    assert "No ellipses in walkthrough." in walkthrough
    for token in (
        "fix65_package_membership_manifest_committed",
        "fix65_m0_merkle_root_recorded",
        "fix65_public_rc_exclude_marker_count_reported",
        "fix65_complete",
    ):
        assert token in status


def test_fix65_evaluator_uses_safe_writer_for_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert ".store.put_nodes(" not in source
    assert ".store.put_edges(" not in source
    assert ".store.replace_edges(" not in source
    assert ".store.put_graph_payload(" not in source
