from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix43_g10_spectral_pagerank_analysis.md"
SPECTRAL = ROOT / "out/genesis_base_graph_spectral_post_fix38.json"
PAGERANK = ROOT / "out/genesis_base_graph_pagerank_post_fix38.json"
QUEUE = ROOT / "out/genesis_base_graph_fix44_target_queue.json"
REPORT = ROOT / "docs/sims/sim_spectral_02/genesis_spectral_delta_fix38_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
EVALUATOR = ROOT / "tools/evaluators/sim_genesis_base_graph_spectral_pagerank_1545p_fix43.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix43_prompt_points_at_fix41a_candidate() -> None:
    text = PROMPT.read_text(encoding="utf-8")
    assert "genesis_atlas_enriched_candidate_fix41a.json" in text
    assert "genesis_atlas_enriched_candidate_fix40.json" not in text
    assert "fix43_complete" in text


def test_fix43_spectral_output_records_crossed_percolation_without_authority_claim() -> None:
    data = _load(SPECTRAL)
    assert data["status"] == "PASS"
    assert data["candidate_source"] == "genesis_atlas_enriched_candidate_fix41a.json"
    assert data["node_count"] == 15676
    assert data["edge_count"] >= 65000
    assert data["bridge_count"] == 6175
    assert data["weakly_connected_components"] == [15676]
    assert data["giant_component_fraction"] == 1.0
    assert data["giant_component_protocol_fraction"] == 1.0
    assert data["percolation_threshold_assessment"] == "crossed"
    assert data["lambda_2"] > 0.03
    assert data["largest_component_lambda_2"] > 0.03
    assert data["baseline"]["bridge_count"] == 4990
    assert data["baseline"]["lambda_2_clique_incidence"] == 0.000223125904
    assert "Spectral, PageRank, bridge, and betweenness metrics are structural diagnostics only, not authority proof." in data["non_claims"]


def test_fix43_pagerank_output_is_bounded_and_complete() -> None:
    data = _load(PAGERANK)
    assert data["status"] == "PASS"
    assert data["node_count"] == 15676
    assert data["betweenness_method"] == "networkx_betweenness_centrality_k64_seed0_deterministic_research_only"
    assert data["pagerank_method"] == "networkx_pagerank_alpha_0_85_tol_1e_10"
    assert len(data["nodes"]) == data["node_count"]
    protocol_rows = [row for row in data["nodes"] if row["is_protocol_relevant"]]
    assert len(protocol_rows) >= 5000
    assert all("pagerank_score" in row for row in data["nodes"])
    assert all("betweenness_centrality" in row for row in data["nodes"])


def test_fix43_target_queue_excludes_generated_material() -> None:
    data = _load(QUEUE)
    assert data["status"] == "PASS"
    assert data["entry_count"] == 500
    assert len(data["entries"]) == 500
    assert data["filter"] == "protocol_relevant_only_lowest_pagerank_bottom_500"
    scores = [entry["pagerank_score"] for entry in data["entries"]]
    assert scores == sorted(scores)
    for entry in data["entries"]:
        assert entry["repo_path"].startswith(("ilc_core/", "docs/specs/", "tests/", "tools/"))
        assert not entry["repo_path"].startswith(("out/", ".git/"))
        assert isinstance(entry["current_edge_types"], list)


def test_fix43_report_and_status_preserve_boundaries() -> None:
    report = REPORT.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "percolation_threshold_assessment: crossed" in report
    assert "Full-graph λ₂" in report
    assert "not authority proof" in report
    assert "No Genesis signing occurred." in report
    assert "fix43_spectral_analysis_complete" in status
    assert "fix43_pagerank_complete" in status
    assert "fix43_fix44_target_queue_produced" in status
    assert "fix43_complete" in status
    assert "public_path_remains_blocked_phase_1545p_fix43" in status


def test_fix43_evaluator_uses_atomic_writes_and_public_rc_exclude() -> None:
    text = EVALUATOR.read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE: genesis_base_graph_spectral_pagerank_fix43_research_only" in text
    assert "tempfile.mkstemp" in text
    assert "os.replace" in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
