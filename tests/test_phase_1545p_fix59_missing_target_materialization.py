from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES


REPORT_PATH = Path("out/genesis_atlas_fix59_missing_target_materialization_report_v0.1.json")
STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def _edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _store_rows() -> tuple[list[dict], list[dict]]:
    store = GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def test_fix59_complete_token_in_status() -> None:
    assert "fix59_complete" in STATUS_PATH.read_text(encoding="utf-8")


def test_fix59_report_exists_and_valid() -> None:
    report = _report()
    assert report["status"] == "PASS"
    assert "edge_id_debt" in report
    assert "missing_target_resolution" in report
    assert "rejection_report_sources" in report


def test_fix59_edge_id_debt_carried_to_fix60() -> None:
    report = _report()
    assert report["edge_id_debt"]["global_repair_performed"] is False
    assert report["edge_id_debt"]["carried_forward_to_fix60"] is True
    assert report["edge_id_debt"]["edges_missing_edge_id_after"] >= 0


def test_fix59_new_or_remapped_edges_have_edge_id() -> None:
    report = _report()
    _, edges = _store_rows()
    by_id = {
        edge["edge_id"]: edge
        for edge in edges
        if edge.get("annotation_phase") == "phase_1545p_fix59"
    }
    assert set(edge["edge_id"] for edge in report["new_edges"]) <= set(by_id)
    for edge in by_id.values():
        assert edge["edge_id"]
        assert edge["edge_id"] == _edge_id(edge["source"], edge["edge_type"], edge["target"])
        assert edge["edge_type"] != "GOVERNS"


def test_fix59_stub_nodes_have_graph_projection() -> None:
    report = _report()
    nodes, _ = _store_rows()
    by_id = {node["candidate_id"]: node for node in nodes}
    for row in report["created_nodes"]:
        node = by_id[row["candidate_id"]]
        assert node["annotation_phase"] == "phase_1545p_fix59"
        assert node["annotation_method"] == "stub_materialized"
        assert node["graph_projection"]


def test_fix59_no_high_authority_blind_stubs() -> None:
    nodes, _ = _store_rows()
    high_prefixes = ("cdl:", "policy:", "artifact:")
    for node in nodes:
        if not str(node.get("candidate_id", "")).startswith(high_prefixes):
            continue
        if node.get("annotation_method") != "stub_materialized":
            continue
        assert node.get("canonical_materialize_evidence")


def test_fix59_lmdb_node_count_nondecreasing() -> None:
    report = _report()
    assert report["node_count_nondecreasing"] is True
    assert report["edge_count_nondecreasing"] is True
    assert report["post_materialization_node_count"] >= report["pre_materialization_node_count"]
    assert report["post_materialization_edge_count"] >= report["pre_materialization_edge_count"]


def test_fix59_report_records_deferred_targets() -> None:
    report = _report()
    deferred = report["missing_target_resolution"]["deferred_targets"]
    assert isinstance(deferred, list)
    for row in deferred:
        assert row["target_id"]
        assert row["prefix"]
        assert row["reason"]
