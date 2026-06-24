# SPDX-License-Identifier: AGPL-3.0-only
"""Regression checks for Phase 1545p-Fix72 measurement outputs."""

from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
FIEDLER_PATH = REPO_ROOT / "out/genesis_atlas_fix72_fiedler_all_local_v0.1.json"
WHOLE_GRAPH_PATH = (
    REPO_ROOT / "docs/specs/ilc_fix72_whole_graph_baseline_diagnostic_v0.1.json"
)
SPECTRAL_PATH = REPO_ROOT / "out/genesis_base_graph_spectral_post_fix69.json"
PERCOLATION_PATH = REPO_ROOT / "docs/specs/ilc_fix72_percolation_analysis_v0.1.json"
AUTHORITY_SIM_PATH = REPO_ROOT / "docs/specs/ilc_fix72_authority_sim_battery_v0.1.json"
MANIFEST_PATH = REPO_ROOT / "docs/specs/ilc_fix72_measurement_suite_manifest_v0.1.json"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix72_status_tokens_present() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in [
        "fix72_fiedler_rebaseline_complete",
        "fix72_whole_graph_baseline_complete",
        "fix72_spectral_pagerank_complete",
        "fix72_percolation_analysis_complete",
        "fix72_authority_sim_battery_complete",
        "fix72_complete",
    ]:
        assert token in status


def test_fix72_fiedler_and_spectral_counts_match_snapshot() -> None:
    fiedler = _load(FIEDLER_PATH)
    whole = _load(WHOLE_GRAPH_PATH)
    spectral = _load(SPECTRAL_PATH)

    assert fiedler["execution_lmdb_counts"]["nodes"] == whole["node_count"]
    assert fiedler["execution_lmdb_counts"]["edges"] == whole["edge_count"]
    assert spectral["node_count"] == whole["node_count"]
    assert spectral["edge_count"] == whole["edge_count"]
    assert spectral["lambda2"] == fiedler["projections"]["all_local"]["lambda2"]
    assert fiedler["projections"]["all_local"]["lambda2_method"] == (
        "networkx_tracemin_pcg_tol_1e-4"
    )
    assert fiedler["projections"]["authority_only"]["lambda2"] == 0.0


def test_fix72_percolation_reports_prompt_metric_and_connectivity_metric() -> None:
    payload = _load(PERCOLATION_PATH)
    total = (
        payload["resolved_count"]
        + payload["still_unresolved_count"]
        + payload["missing_node_count"]
    )
    assert total == 382
    assert payload["resolved_count"] == payload["resolved_by_any_semantic_degree_count"]
    assert payload["resolved_by_prompt_indegree_count"] <= payload["resolved_count"]
    assert payload["write_policy"] == "no_edges_written_analysis_only"


def test_fix72_authority_sim_schema_records_dark_cdls_and_cycles() -> None:
    payload = _load(AUTHORITY_SIM_PATH)
    assert payload["suite_b_governs_cycles"]["cycle_count"] == 0
    suite_d = payload["suite_d_runtime_binding_coverage"]
    assert suite_d["ratified_cdl_node_count"] >= suite_d["implementation_dark_cdl_count"]
    assert isinstance(suite_d["implementation_dark_cdls"], list)


def test_fix72_manifest_tracks_committed_and_out_artifacts() -> None:
    payload = _load(MANIFEST_PATH)
    paths = {row["path"] for row in payload["artifacts"]}
    assert "docs/specs/ilc_fix72_whole_graph_baseline_diagnostic_v0.1.json" in paths
    assert "out/genesis_base_graph_spectral_post_fix69.json" in paths
    assert payload["manifest_self_hash_policy"] == (
        "self_hash_excluded_to_avoid_fixed_point_manifest_loop"
    )
    for row in payload["artifacts"]:
        assert row["bytes"] > 0
        assert len(row["sha256"]) == 64


def test_fix72_lmdb_registration_integrity_and_lineage() -> None:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        info = writer.inspect()
        edges = writer.store.iter_edges()
    finally:
        writer.close()

    assert info["dangling_edge_count"] == 0
    assert info["edge_id_debt_count"] == 0
    assert all(info["invariants"].values())
    assert any(
        (edge.get("source") or edge.get("src")) == "phase:phase_1545p_fix72"
        and (edge.get("target") or edge.get("tgt")) == "phase:1545p"
        and edge.get("edge_type") == "CARRIES_FORWARD"
        for edge in edges
    )
