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


def test_fix63e_authority_visual_colors_are_distinct() -> None:
    assert graph_viz_export.PREFIX_COLORS["adr"] != graph_viz_export.PREFIX_COLORS["cdl"]
    assert graph_viz_3d.PREFIX_COLORS["adr"] != graph_viz_3d.PREFIX_COLORS["cdl"]
    assert graph_viz_export.PREFIX_COLORS["genesis_authority_root"] == "#ffffff"


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
    assert node_by_id[graph_viz_export.NODE0]["group"] == "genesis_authority_root"
    assert node_by_id[graph_viz_export.NODE0]["prefix"] == "artifact"
    assert node_by_id[graph_viz_export.NODE0]["authority_class"] == "genesis_authority_root"
    assert M012 in node_by_id
    assert node_by_id[M012]["degree_lmdb_total"] == 2
    assert node_by_id[M012]["directed_hop_from_root"] == 1
    assert node_by_id[M012]["projection"] == "support_candidate_graph"
    assert node_by_id[M012]["status"] == "support_trace_not_independent_authority"
    assert any(edge["type"] == "CLASSIFIED_BY" for edge in payload["edges"])
    assert all(edge["type"] != "CONTAINS_FILE" for edge in payload["edges"])


def test_fix63e_visual_taxonomy_separates_node0_from_material_roots() -> None:
    generated_root = "artifact:generated_evidence_material_root_1545p_fix22"
    source_overlay = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
    nodes = [
        {
            "candidate_id": graph_viz_export.NODE0,
            "authority_status": "retrospective_genesis_attestation_phase_1142",
            "graph_projection": "genesis_core_star_map",
            "node_kind": "authority_map",
            "tier": "genesis_core",
        },
        {
            "candidate_id": generated_root,
            "authority_status": "support_only_candidate_not_signed",
            "graph_projection": "support_candidate_graph",
            "node_kind": "repo_material_root",
            "tier": "generated_evidence_root",
        },
        {
            "candidate_id": source_overlay,
            "canonicality_tier": "fix38_candidate_overlay",
            "graph_projection": "support_candidate_graph",
            "node_kind": "",
        },
    ]
    payload = graph_viz_export.build_view(
        view="all-local",
        nodes=nodes,
        edges=[],
        digest_manifest=_fix61_digest_manifest(),
        lmdb_root=LMDB_ROOT,
        omit_export_time=True,
    )
    node_by_id = {node["id"]: node for node in payload["nodes"]}
    assert node_by_id[graph_viz_export.NODE0]["group"] == "genesis_authority_root"
    assert node_by_id[generated_root]["group"] == "material_partition_root"
    assert node_by_id[generated_root]["authority_class"] == "support_only_candidate_not_signed"
    assert node_by_id[source_overlay]["group"] == "source_tree_overlay"
    assert node_by_id[source_overlay]["authority_class"] == "candidate_overlay_not_canonical"


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
            },
            {
                "degree_lmdb_total": 2,
                "directed_hop_from_root": 3,
                "group": "repo",
                "id": "repo:file:abc:ilc_core_runtime_example_py",
                "kind": "repo_material_node",
                "label": "ilc_core/runtime_example.py",
                "projection": "support_candidate_graph",
                "repo_subgroup": "runtime",
                "size": 4,
                "status": "",
                "tier": "public_release_candidate_material",
            },
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
    assert "authority_class" in html
    assert "genesis_authority_root" in html
    assert "Genesis authority root is always visible" in html
    assert 'const hiddenGroups = new Set(["repo"])' in html
    assert "hiddenRepoSubgroups" in html
    assert "data-repo-subgroup" in html
    assert "repo_subgroup" in html
    assert 'id="hop-slider" min="-1"' in html
    assert "let hopDepth            = -1" in html
    assert "hopDepth >= 0" in html


def test_fix63e_renderer_preserves_exported_visual_group_and_color() -> None:
    nodes, links = graph_viz_3d._build_graph_data(
        {
            "nodes": [
                {
                    "color": "#123456",
                    "degree_lmdb_total": 1,
                    "group": "genesis_authority_root",
                    "id": graph_viz_export.NODE0,
                    "kind": "authority_map",
                    "prefix": "artifact",
                    "size": 20,
                    "visual_group": "genesis_authority_root",
                }
            ],
            "edges": [],
        }
    )
    assert links == []
    assert nodes[0]["group"] == "genesis_authority_root"
    assert nodes[0]["prefix"] == "artifact"
    assert nodes[0]["color"] == "#123456"


def test_fix63e_repo_subgroup_is_exported_and_renderer_falls_back() -> None:
    payload = graph_viz_export.build_view(
        view="all-local",
        nodes=[
            {
                "candidate_id": "repo:file:abc123:ilc_core_crypto_cose_sign1_py",
                "source_path": "ilc_core/crypto/cose_sign1.py",
                "node_kind": "repo_material_node",
                "tier": "public_release_candidate_material",
            },
            {
                "candidate_id": "repo:file:def456:tests_test_runtime_py",
                "source_path": "tests/test_runtime.py",
                "node_kind": "repo_material_node",
                "tier": "public_release_candidate_material",
            },
        ],
        edges=[],
        digest_manifest=_fix61_digest_manifest(),
        lmdb_root=LMDB_ROOT,
        omit_export_time=True,
    )
    by_id = {node["id"]: node for node in payload["nodes"]}
    assert by_id["repo:file:abc123:ilc_core_crypto_cose_sign1_py"]["repo_subgroup"] == "security"
    assert by_id["repo:file:def456:tests_test_runtime_py"]["repo_subgroup"] == "test"

    rendered_nodes, _ = graph_viz_3d._build_graph_data(
        {
            "nodes": [
                {
                    "id": "repo:file:ghi789:docs_specs_example_md",
                    "group": "repo",
                    "label": "docs/specs/example.md",
                }
            ],
            "edges": [],
        }
    )
    assert rendered_nodes[0]["repo_subgroup"] == "spec_doc"
