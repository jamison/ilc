from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES
from tools.evaluators.sim_genesis_atlas_fix56_projection_aware_fiedler_rebaseline import (
    _edge_target,
)


REPORT_PATH = Path("out/genesis_atlas_fix59a_deferred_repair_reconciliation_report_v0.1.json")
STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def _store() -> GenesisAtlasCandidateStore:
    return GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )


def test_fix59a_complete_token_in_status() -> None:
    assert "fix59a_complete" in STATUS_PATH.read_text(encoding="utf-8")


def test_fix59a_report_exists_and_valid() -> None:
    report = _report()
    assert report["status"] == "PASS"
    assert report["node_count_delta"] >= 0
    assert report["edge_count_delta"] >= 0
    assert report["graph_payload_rebuilt_from_row_stores"] is True
    assert report["index_rebuild_performed"] is True
    assert report["phase_file_nodes_registered"]
    assert report["phase_file_candidate_edges"]


def test_fix59a_payload_counts_match_lmdb_rows() -> None:
    report = _report()
    store = _store()
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
        payload = store.get_graph_payload()
    finally:
        store.close()
    assert isinstance(payload, dict)
    assert len(nodes) == report["post_node_count"]
    assert len(edges) == report["post_edge_count"]
    assert len(payload["nodes"]) == len(nodes)
    assert len(payload["edges"]) == len(edges)


def test_fix59a_tier_indexes_match_lmdb_rows() -> None:
    store = _store()
    try:
        nodes = store.iter_nodes()
        tiers = sorted({str(node.get("tier", "unknown")) for node in nodes})
        for tier in tiers:
            actual = sorted(
                str(node["candidate_id"])
                for node in nodes
                if str(node.get("tier", "unknown")) == tier
            )
            assert store.node_ids_by_tier(tier) == actual
    finally:
        store.close()


def test_fix59a_non_ratified_cdl_targets_are_support_stubs() -> None:
    store = _store()
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
    finally:
        store.close()
    for node_id in ("cdl:021", "cdl:085_prelock_spec"):
        node = nodes[node_id]
        assert node["annotation_method"] == "stub_materialized"
        assert node["graph_projection"] == "support_candidate_graph"
        assert node["node_kind"] == "authority_stub"
        assert node["tier"] == "support_candidate"


def test_fix59a_required_targets_present_and_no_dangling_edges() -> None:
    required = {
        "cdl:020",
        "cdl:021",
        "cdl:024",
        "cdl:032",
        "cdl:033",
        "cdl:082",
        "cdl:085_prelock_spec",
        "policy:genesis_optimization_harness_support_only_phase_1545p_fix9",
        "policy:human_objective_selection_boundary_phase_1545p_fix9",
        "policy:launch_roadmap_three_machines_seven_agents_v0_8_testbed_not_public_claim",
        "policy:public_path_still_blocked_phase_1487p",
    }
    store = _store()
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
    finally:
        store.close()
    node_ids = {node["candidate_id"] for node in nodes}
    assert required <= node_ids
    assert all(_edge_target(edge) in node_ids for edge in edges)


def test_fix59a_phase_files_registered_with_typed_edges() -> None:
    report = _report()
    store = _store()
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edges = store.iter_edges()
    finally:
        store.close()
    registered_node_ids = {node["candidate_id"] for node in report["phase_file_nodes_registered"]}
    assert {
        "phase:1545p_fix59_missing_target_materialization",
        "phase:1545p_fix59a_deferred_repair_reconciliation",
        "repo:file_ref:tools_evaluators_sim_genesis_atlas_fix59_missing_target_materialization_py",
        "repo:file_ref:tests_test_phase_1545p_fix59_missing_target_materialization_py",
        "repo:file_ref:docs_phases_phase_1545p_fix59a_deferred_repair_reconciliation_walkthrough_md",
    } <= registered_node_ids
    for node_id in registered_node_ids:
        assert nodes[node_id]["graph_projection"] == "support_candidate_graph"
        assert nodes[node_id]["graph_delta"] == "support_only"
    edge_semantics = {(edge["source"], edge["edge_type"], edge["target"]) for edge in edges}
    for edge in report["phase_file_candidate_edges"]:
        assert (edge["source"], edge["edge_type"], edge["target"]) in edge_semantics
        assert edge["edge_type"] in {"CARRIES_FORWARD", "IMPLEMENTS", "TESTS", "EVIDENCES", "CLASSIFIED_BY"}
