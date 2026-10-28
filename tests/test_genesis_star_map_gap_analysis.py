"""Genesis core star-map observed-hypergraph comparison tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_genesis_star_map_to_repo_graph.py"
@pytest.fixture(scope="module")
def analysis_outputs(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    output_dir = tmp_path_factory.mktemp("genesis_star_map_gap")
    observed = output_dir / "observed.json"
    gap = output_dir / "gap.json"
    report = output_dir / "report.md"
    subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--observed-out",
            str(observed),
            "--gap-out",
            str(gap),
            "--report-out",
            str(report),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return observed, gap, report


def _json(path: pathlib.Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_gap_analysis_tool_outputs_exist_and_are_valid_json(
    analysis_outputs: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
) -> None:
    observed, gap, report = analysis_outputs
    assert observed.exists()
    assert gap.exists()
    assert report.exists()
    _json(observed)
    _json(gap)


def test_observed_repo_graph_has_explicit_hypergraph_shape(
    analysis_outputs: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
) -> None:
    observed_path, _, _ = analysis_outputs
    observed = _json(observed_path)
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


def test_observed_repo_graph_includes_key_star_map_vertices_and_symbols(
    analysis_outputs: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
) -> None:
    observed_path, _, _ = analysis_outputs
    observed = _json(observed_path)
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


def test_gap_analysis_records_review_categories(
    analysis_outputs: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
) -> None:
    _, gap_path, _ = analysis_outputs
    gap = _json(gap_path)
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


def test_gap_analysis_report_is_human_readable(
    analysis_outputs: tuple[pathlib.Path, pathlib.Path, pathlib.Path],
) -> None:
    _, _, report = analysis_outputs
    text = report.read_text(encoding="utf-8")
    assert "# Genesis Core Star-Map Gap Analysis v0.1" in text
    assert "Core Nodes Without Direct Support" in text
    assert "Proposed Edges Needing Authority" in text
