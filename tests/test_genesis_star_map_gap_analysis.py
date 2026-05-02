"""Genesis core star-map observed-hypergraph comparison tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_genesis_star_map_to_repo_graph.py"
OBSERVED = ROOT / "out/genesis_observed_repo_hypergraph_v0.1.json"
GAP = ROOT / "out/genesis_core_star_map_gap_analysis_v0.1.json"
REPORT = ROOT / "docs/sims/sim_spectral_02/genesis_core_star_map_gap_analysis_v0.1.md"
_TOOL_RAN = False


def _run_tool() -> None:
    global _TOOL_RAN
    if _TOOL_RAN:
        return
    subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, check=True, text=True, capture_output=True)
    _TOOL_RAN = True


def _json(path: pathlib.Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_gap_analysis_tool_outputs_exist_and_are_valid_json() -> None:
    _run_tool()
    assert OBSERVED.exists()
    assert GAP.exists()
    assert REPORT.exists()
    _json(OBSERVED)
    _json(GAP)


def test_observed_repo_graph_has_explicit_hypergraph_shape() -> None:
    _run_tool()
    observed = _json(OBSERVED)
    assert observed["metadata"]["format_version"] == "genesis_observed_repo_hypergraph.v0.1"
    assert isinstance(observed["vertices"], list)
    assert isinstance(observed["hyperedges"], list)
    assert isinstance(observed["incidence"], list)
    assert observed["vertices"]
    assert observed["hyperedges"]
    assert observed["incidence"]
    first_edge = observed["hyperedges"][0]
    assert "members" in first_edge
    assert all({"role", "vertex"}.issubset(member) for member in first_edge["members"])


def test_observed_repo_graph_includes_key_star_map_vertices_and_symbols() -> None:
    _run_tool()
    observed = _json(OBSERVED)
    vertices = {vertex["vertex_id"]: vertex for vertex in observed["vertices"]}
    for vertex_id in (
        "policy:provenance_decay_alpha_0_45",
        "policy:genesis_theta_hard_0_05",
        "policy:genesis_theta_soft_exp_minus_3",
        "policy:genesis_accrual_governor",
        "ceremony:genesis_agent1_keygen_838a",
        "symbol:GENESIS_THETA_SOFT",
    ):
        assert vertex_id in vertices
    assert observed["observed_counts"]["symbols"]["GENESIS_THETA_SOFT"] > 0
    assert observed["observed_counts"]["symbols"]["PROVENANCE_DECAY_ALPHA"] > 0


def test_gap_analysis_records_review_categories() -> None:
    _run_tool()
    gap = _json(GAP)
    assert gap["metadata"]["format_version"] == "genesis_core_star_map_gap_analysis.v0.1"
    categories = gap["gap_categories"]
    for category in (
        "core_nodes_without_direct_support",
        "low_observed_support_core_nodes",
        "observed_governance_references_not_in_core",
        "proposed_edges_needing_authority",
        "proposed_edges_without_comention",
        "symbol_nodes_without_occurrence",
    ):
        assert category in categories
    assert gap["summary"]["core_node_count"] >= 29
    assert gap["summary"]["proposed_edge_type_count"] > 0


def test_gap_analysis_report_is_human_readable() -> None:
    _run_tool()
    text = REPORT.read_text(encoding="utf-8")
    assert "# Genesis Core Star-Map Gap Analysis v0.1" in text
    assert "Core Nodes Without Direct Support" in text
    assert "Proposed Edges Needing Authority" in text
