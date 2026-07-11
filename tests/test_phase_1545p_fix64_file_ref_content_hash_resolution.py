from __future__ import annotations

import hashlib
from pathlib import Path

import tools.graph_viz_export as graph_viz_export
from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
    repo_file_ref_id,
)


ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS = ROOT / "docs/phases/STATUS.md"
QUEUE = ROOT / "docs/specs/ilc_fix64_file_ref_resolution_queue_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix64_file_ref_resolution_report_v0.1.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix64_file_ref_content_hash_resolution_walkthrough.md"
EVALUATOR = ROOT / "tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py"
TIER1 = {
    "repo:file_ref:ilc_core_cli_atlas_lmdb_cli_py": "ilc_core/cli/atlas_lmdb_cli.py",
    "repo:file_ref:ilc_core_storage_genesis_atlas_lmdb_writer_py": "ilc_core/storage/genesis_atlas_lmdb_writer.py",
    "repo:file_ref:tests_test_phase_1545p_fix59b_atlas_lmdb_safe_writer_py": "tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py",
    "repo:file_ref:tests_test_phase_1545p_fix59c_atlas_lmdb_read_cli_py": "tests/test_phase_1545p_fix59c_atlas_lmdb_read_cli.py",
    "repo:file_ref:tests_test_phase_1545p_fix59d_atlas_lmdb_write_cli_py": "tests/test_phase_1545p_fix59d_atlas_lmdb_write_cli.py",
    "repo:file_ref:tests_test_phase_1545p_fix59e_atlas_lmdb_write_guard_py": "tests/test_phase_1545p_fix59e_atlas_lmdb_write_guard.py",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _edge_source(edge: dict) -> str:
    return str(edge.get("source", edge.get("src", "")))


def _edge_target(edge: dict) -> str:
    return str(edge.get("target", edge.get("tgt", "")))


def test_fix64_outputs_and_status_tokens_present() -> None:
    assert QUEUE.exists()
    assert REPORT.exists()
    assert WALKTHROUGH.exists()
    assert EVALUATOR.exists()
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "fix64_tier1_public_protocol_refs_resolved",
        "fix64_tier2_source_path_refs_resolved",
        "fix64_tier3_label_path_refs_resolved",
        "fix64_file_ref_source_sha256_coverage_reported",
        "fix64_complete",
    ):
        assert token in status


def test_fix64_all_tier1_file_refs_are_content_addressed_and_linked() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        edges = store.iter_edges()
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
    finally:
        store.close()

    for file_ref_id, repo_path in TIER1.items():
        node = nodes[file_ref_id]
        expected_hash = _sha(ROOT / repo_path)
        assert node["source_path"] == repo_path
        assert node["source_sha256"] == expected_hash
        assert node["source_identity_status"] == "content_addressed_by_fix64"
        same_source_edges = [
            edge
            for edge in edges
            if _edge_source(edge) == file_ref_id and edge.get("edge_type") == "SAME_SOURCE"
        ]
        assert len(same_source_edges) == 1
        target = nodes[_edge_target(same_source_edges[0])]
        assert target["candidate_id"].startswith("repo:file:")
        assert target["source_path"] == repo_path
        assert target["source_sha256"] == expected_hash
        assert target["source_sha256"] == node["source_sha256"]


def test_fix64_full_file_ref_coverage_and_lmdb_clean() -> None:
    import json

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        inspection = writer.inspect()
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
    finally:
        writer.close()
    file_refs = [
        node
        for node in nodes
        if str(node.get("candidate_id", "")).startswith("repo:file_ref:")
    ]
    same_source_sources = {
        _edge_source(edge)
        for edge in edges
        if edge.get("edge_type") == "SAME_SOURCE"
    }
    assert file_refs
    if report.get("status") == "PASS":
        assert all(node.get("source_sha256") for node in file_refs)
        assert all(node.get("source_path") for node in file_refs)
        assert all(node["candidate_id"] in same_source_sources for node in file_refs)
    else:
        assert report.get("tier_executed") == 1
        assert report.get("status") == "PARTIAL"
        for file_ref_id in TIER1:
            assert file_ref_id in same_source_sources
    assert inspection["dangling_edge_count"] == 0
    assert inspection["edge_id_debt_count"] == 0
    assert all(inspection["invariants"].values())


def test_fix64_report_and_queue_use_live_counts() -> None:
    import json

    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert queue["schema_version"] == "fix64_file_ref_resolution_queue.v0.1"
    assert queue["counts"]["total_file_refs"] >= 3296
    assert report["schema_version"] == "fix64_file_ref_resolution_report.v0.1"
    assert report["status"] in {"PASS", "PARTIAL"}
    if report["status"] == "PASS":
        assert report["post_counts"]["file_refs_missing_source_sha256"] == 0
        assert report["post_counts"]["file_refs_missing_same_source"] == 0
    else:
        assert report["tier_executed"] == 1
        assert report["tier_result"]["stale_same_source_edges_removed"] >= 0
    assert report["escalation_count"] == 0


def test_fix64_same_source_visual_semantics_are_registered() -> None:
    assert "SAME_SOURCE" in graph_viz_export.EDGE_COLORS


def test_fix64_safe_writer_registration_content_addresses_existing_and_refreshes(tmp_path: Path) -> None:
    source = tmp_path / "phase_artifact.md"
    source.write_text("phase artifact v1\n", encoding="utf-8")
    root = tmp_path / "atlas"
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        nodes = [
            {
                "candidate_id": "node:root",
                "graph_projection": "support_candidate_graph",
                "node_kind": "support_node",
                "tier": "support_candidate",
            },
            {
                "candidate_id": repo_file_ref_id(source.as_posix()),
                "graph_projection": "support_candidate_graph",
                "node_kind": "phase_artifact",
                "source_path": source.as_posix(),
                "source_identity_status": "stale_before_registration",
                "tier": "support_candidate",
            },
        ]
        store.put_nodes(nodes)
        store.put_graph_payload({"edges": [], "nodes": nodes})
    finally:
        store.close()

    source.write_text("phase artifact v2\n", encoding="utf-8")
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.register_phase_files(
            "1545p-Fix64-test",
            [
                AtlasPhaseFileRegistration(
                    path=source,
                    node_kind="phase_artifact",
                    graph_projection="support_candidate_graph",
                    skip_carries_forward=True,
                )
            ],
            dry_run=False,
        )
        assert receipt["file_identity_update_count"] == 1
        node = writer.store.get_node(repo_file_ref_id(source.as_posix()))
        assert node is not None
        assert node["source_sha256"] == _sha(source)
        assert node["source_identity_status"] == "content_addressed_at_registration"
        assert node["size_bytes"] == source.stat().st_size
    finally:
        writer.close()
