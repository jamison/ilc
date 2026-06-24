from __future__ import annotations

from collections import Counter
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = (
    REPO_ROOT / "docs/specs/ilc_fix69_policy_target_sim_rewiring_audit_report_v0.1.md"
)
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"


def _graph() -> tuple[list[dict], list[dict]]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def _node_id(node: dict) -> str:
    return node.get("candidate_id") or node.get("node_id") or ""


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src") or ""


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt") or ""


def _non_repo_degree(nodes: list[dict], edges: list[dict]) -> Counter[str]:
    ids = {_node_id(node) for node in nodes}
    degree: Counter[str] = Counter()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source not in ids or target not in ids:
            continue
        if not target.startswith("repo:"):
            degree[source] += 1
        if not source.startswith("repo:"):
            degree[target] += 1
    return degree


def test_fix69_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix69_orphaned_policy_target_sim_rewiring_phase_1545p",
        "policy_nodes_rewired_phase_1545p_fix69",
        "target_nodes_rewired_phase_1545p_fix69",
        "sim_nodes_rewired_phase_1545p_fix69",
        "fix69_complete",
    ):
        assert token in text


def test_fix69_edges_are_safe_bridge_types() -> None:
    _, edges = _graph()
    fix69_edges = [
        edge for edge in edges if edge.get("annotation_phase") == "phase_1545p_fix69"
    ]
    semantic_edges = [
        edge
        for edge in fix69_edges
        if edge.get("annotation_method") == "fix69_orphan_rewiring_direct_read"
    ]
    assert len(semantic_edges) >= 213

    allowed = {"CARRIES_FORWARD", "EVIDENCES", "REFERENCES_AUTHORITY"}
    forbidden = {"GOVERNS", "SOURCE_TREE_MEMBER", "CLASSIFIED_BY"}
    for edge in semantic_edges:
        assert edge.get("edge_type") in allowed
        assert edge.get("edge_type") not in forbidden
        assert edge.get("edge_id")
        assert edge.get("evidence_path")
        assert edge.get("evidence_summary")


def test_no_sim_nodes_have_zero_non_repo_degree_after_fix69() -> None:
    nodes, edges = _graph()
    degree = _non_repo_degree(nodes, edges)
    sim_orphans = sorted(
        _node_id(node)
        for node in nodes
        if _node_id(node).startswith("sim:") and degree[_node_id(node)] == 0
    )
    assert sim_orphans == []


def test_no_phase_nodes_have_zero_non_repo_degree_after_fix69() -> None:
    nodes, edges = _graph()
    degree = _non_repo_degree(nodes, edges)
    phase_orphans = sorted(
        _node_id(node)
        for node in nodes
        if _node_id(node).startswith("phase:") and degree[_node_id(node)] == 0
    )
    assert phase_orphans == []


def test_public_path_policy_has_outgoing_non_repo_edge() -> None:
    _, edges = _graph()
    hub = "policy:public_path_still_blocked_phase_1545p"
    outgoing = [
        edge
        for edge in edges
        if _edge_source(edge) == hub and not _edge_target(edge).startswith("repo:")
    ]
    assert outgoing


def test_no_dangling_edges_or_edge_id_debt() -> None:
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


def test_fix69_report_records_target_classification_not_forced_edges() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    for expected in (
        "Pre-repair orphan counts: policy=267, target=786, sim=39",
        "Post-repair orphan counts: policy=93, target=786, sim=0",
        "Semantic edges accepted: 213",
        "Phase-lineage hygiene edges accepted: 14",
        "tier1_build_critical_review_required",
        "tier2_support_leaf_no_wiring_required",
        "No `GOVERNS` edges added.",
        "No `SOURCE_TREE_MEMBER` edges added.",
    ):
        assert expected in text
