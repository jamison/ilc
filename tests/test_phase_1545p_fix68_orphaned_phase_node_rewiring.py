from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix68_phase_rewiring_audit_report_v0.1.md"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"


def _graph() -> tuple[list[dict], list[dict]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def _node_id(node: dict) -> str:
    return node.get("candidate_id") or node.get("node_id")


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def test_fix68_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix68_orphaned_phase_node_rewiring_phase_1545p",
        "fix59b_phase_node_connected_phase_1545p_fix68",
        "fix62_series_phase_nodes_connected_phase_1545p_fix68",
        "fix63_series_phase_nodes_connected_phase_1545p_fix68",
        "fix68_complete",
    ):
        assert token in text


def test_no_phase_nodes_have_zero_non_repo_degree() -> None:
    nodes, edges = _graph()
    ids = {_node_id(node) for node in nodes}
    non_repo_degree: dict[str, int] = defaultdict(int)
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source not in ids or target not in ids:
            continue
        if not target.startswith("repo:"):
            non_repo_degree[source] += 1
        if not source.startswith("repo:"):
            non_repo_degree[target] += 1

    orphan_phases = sorted(
        node_id
        for node_id in ids
        if node_id.startswith("phase:") and non_repo_degree[node_id] == 0
    )
    assert orphan_phases == []


def test_fix68_edges_use_only_allowed_types_and_have_evidence() -> None:
    _, edges = _graph()
    fix68_edges = [
        edge for edge in edges if edge.get("annotation_phase") == "phase_1545p_fix68"
    ]
    manual_edges = [
        edge
        for edge in fix68_edges
        if edge.get("annotation_method") == "fix68_manual_batch_read"
    ]
    assert len(fix68_edges) >= 528
    assert len(manual_edges) == 521

    forbidden = {"GOVERNS", "SOURCE_TREE_MEMBER"}
    for edge in fix68_edges:
        assert edge["edge_type"] not in forbidden

    for edge in manual_edges:
        assert edge.get("evidence_path")
        assert edge.get("evidence_summary")
        assert edge.get("edge_id")


def test_no_dangling_or_missing_edge_id_debt() -> None:
    nodes, edges = _graph()
    ids = {_node_id(node) for node in nodes}
    dangling = [
        (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
        for edge in edges
        if _edge_source(edge) not in ids or _edge_target(edge) not in ids
    ]
    missing_edge_id = [
        (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
        for edge in edges
        if not edge.get("edge_id")
    ]
    assert dangling == []
    assert missing_edge_id == []


def test_final_batch_representative_edges_present() -> None:
    _, edges = _graph()
    semantics = {
        (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
        for edge in edges
    }
    assert (
        "phase:launch_roadmap_cdl078_hb002_cdl079_sequence",
        "REFERENCES_AUTHORITY",
        "cdl:079_hb_002_p2p_bootstrap_distribution_bootstrap_bundle_signed",
    ) in semantics
    assert (
        "phase:early_protocol_event_log_epoch_playground",
        "EVIDENCES",
        "invariant:protocol_event_log_append_iter_empty_and_payload_round_trip",
    ) in semantics
    assert (
        "phase:meta_test_integrity_hardening",
        "EVIDENCES",
        "invariant:test_suite_no_silent_head_fallback_no_swallowed_broad_exceptions_no_assert_true_placeholders",
    ) in semantics


def test_fix68_report_records_final_state() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    for expected in (
        "phase_orphans=0",
        "dangling_edges=0",
        "missing_edge_id=0",
        "fix68_edges=528",
        "fix68_manual_batch_read_edges=521",
        "forbidden_fix68_edge_types=0",
    ):
        assert expected in text
