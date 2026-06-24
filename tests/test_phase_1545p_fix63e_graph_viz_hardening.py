from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.graph_viz_3d as graph_viz_3d
import tools.graph_viz_export as graph_viz_export


STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")
DIGEST_MANIFEST = Path("out/genesis_base_graph_v0.4_unified_lmdb_digest_fix61.json")
M012 = "policy:phase_m012_full_bft_transfer_binary_complete"


def _fix61_digest_manifest() -> dict[str, str]:
    return {
        "edge_digest": "1" * 64,
        "lmdb_path": "out/genesis_base_graph_v0.4_unified.lmdb",
        "node_digest": "0" * 64,
        "phase": "1545p-Fix61",
        "preimage_digest": "2" * 64,
    }


def test_fix63e_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix63e_viz_governance_edge_types_expanded" in text
    assert "fix63e_popup_diagnostics_added" in text
    assert "fix63e_lmdb_source_header_added" in text
    assert "fix63e_complete" in text


def test_fix63e_governance_edge_type_contract() -> None:
    assert "CLASSIFIED_BY" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "SAME_AUTHORITY" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "OPENED_FOR" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "RESOLVED_BY" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "DERIVED_FROM" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "CARRIES_FORWARD" in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "CONTAINS_FILE" not in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "CONTAINS_GROUP" not in graph_viz_export.GOVERNANCE_EDGE_TYPES
    assert "CONTAINS_PARTITION" not in graph_viz_export.GOVERNANCE_EDGE_TYPES


def test_fix63e_build_view_exports_degree_and_hop_diagnostics() -> None:
    nodes = [
        {
            "candidate_id": graph_viz_export.NODE0,
            "graph_projection": "genesis_core_star_map",
            "node_kind": "artifact",
            "tier": "genesis_core",
        },
        {
            "candidate_id": "cdl:example",
            "graph_projection": "genesis_core_star_map",
            "node_kind": "ratified_cdl",
            "tier": "genesis_core",
        },
        {
            "candidate_id": M012,
            "candidate_status": "support_trace_not_independent_authority",
            "graph_projection": "support_candidate_graph",
            "node_kind": "policy_support_trace_node",
            "tier": "support_candidate",
        },
    ]
    edges = [
        {"edge_type": "GOVERNS", "source": graph_viz_export.NODE0, "target": "cdl:example"},
        {"edge_type": "CLASSIFIED_BY", "source": M012, "target": "cdl:example"},
        {"edge_type": "CONTAINS_FILE", "source": graph_viz_export.NODE0, "target": M012},
    ]
    payload = graph_viz_export.build_view(
        view="governance",
        nodes=nodes,
        edges=edges,
        digest_manifest=_fix61_digest_manifest(),
        lmdb_root=LMDB_ROOT,
        omit_export_time=True,
    )
    node_by_id = {node["id"]: node for node in payload["nodes"]}
    assert M012 in node_by_id
    assert node_by_id[M012]["degree_lmdb_total"] == 2
    assert node_by_id[M012]["directed_hop_from_root"] == 1
    assert node_by_id[M012]["projection"] == "support_candidate_graph"
    assert node_by_id[M012]["status"] == "support_trace_not_independent_authority"
    assert any(edge["type"] == "CLASSIFIED_BY" for edge in payload["edges"])
    assert all(edge["type"] != "CONTAINS_FILE" for edge in payload["edges"])


def test_fix63e_governance_export_contains_m012_classified_edge(tmp_path: Path) -> None:
    if not LMDB_ROOT.exists() or not DIGEST_MANIFEST.exists():
        pytest.skip("local unified LMDB or digest manifest not available")
    exported = graph_viz_export.export_views(
        lmdb_root=LMDB_ROOT,
        digest_manifest_path=DIGEST_MANIFEST,
        output_dir=tmp_path,
        view="governance",
        omit_export_time=True,
    )
    graph = json.loads(exported["governance"].read_text(encoding="utf-8"))
    m012_edges = [
        edge
        for edge in graph["edges"]
        if edge["source"] == M012 or edge["target"] == M012
    ]
    assert m012_edges
    assert all(edge["type"] == "CLASSIFIED_BY" for edge in m012_edges)
    assert graph["metadata"]["lmdb_root"].endswith("out/genesis_base_graph_v0.4_unified.lmdb")
    assert "lmdb_digest_sha256" in graph["metadata"]
    assert all(isinstance(node["degree_lmdb_total"], int) for node in graph["nodes"])
    assert all("directed_hop_from_root" in node for node in graph["nodes"])


def test_fix63e_carries_forward_in_governance_export(tmp_path: Path) -> None:
    if not LMDB_ROOT.exists() or not DIGEST_MANIFEST.exists():
        pytest.skip("local unified LMDB or digest manifest not available")
    exported = graph_viz_export.export_views(
        lmdb_root=LMDB_ROOT,
        digest_manifest_path=DIGEST_MANIFEST,
        output_dir=tmp_path,
        view="governance",
        omit_export_time=True,
    )
    graph = json.loads(exported["governance"].read_text(encoding="utf-8"))
    carries_forward_edges = [edge for edge in graph["edges"] if edge["type"] == "CARRIES_FORWARD"]
    assert carries_forward_edges, "governance export must contain at least one CARRIES_FORWARD edge"


def test_fix63e_html_contains_source_bar_and_popup_diagnostics() -> None:
    html = graph_viz_3d._html(
        [
            {
                "degree_lmdb_total": 4,
                "directed_hop_from_root": 2,
                "group": "policy",
                "id": M012,
                "kind": "policy_support_trace_node",
                "label": M012,
                "projection": "support_candidate_graph",
                "size": 4,
                "status": "support_trace_not_independent_authority",
                "tier": "support_candidate",
            }
        ],
        [],
        "test",
        metadata={
            "export_time_utc": "omitted_for_test",
            "lmdb_digest_sha256": "a" * 64,
            "lmdb_root": "out/genesis_base_graph_v0.4_unified.lmdb",
        },
    )
    assert "lmdb-source-bar" in html
    assert "lmdb_degree" in html
    assert "visible_degree" in html
    assert "hidden_edges" in html
    assert "directed_hop" in html
