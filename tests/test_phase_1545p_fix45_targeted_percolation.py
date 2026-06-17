from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix45_g10_targeted_percolation_annotation.md"
BASE_CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix45.json"
ANALYSIS = ROOT / "out/genesis_base_graph_fix45_target_queue_analysis.json"
LEDGER = ROOT / "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix45_algorithmic_percolation_report_v0.1.md"
MANUAL_QUEUE = ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix45_targeted_percolation_annotation_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
BUILDER = ROOT / "tools/evaluators/sim_genesis_base_graph_fix45_targeted_percolation.py"

NEW_DOC_PATHS = {
    "docs/specs/ilc_fix45_target_queue_analysis_v0.1.md",
    "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json",
    "docs/specs/ilc_fix45_algorithmic_percolation_report_v0.1.md",
    "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fix45_edges(candidate: dict) -> list[dict]:
    return [edge for edge in candidate["edges"] if edge.get("source_phase") == "1545p-Fix45"]


def test_fix45_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "fix45_target_queue_algorithmic_annotation_complete",
        "fix45_enriched_candidate_produced",
        "fix45_manual_semantic_tranche_deferred",
        "fix45_complete",
        "public_path_remains_blocked_phase_1545p_fix45",
    ):
        assert token in status


def test_fix45_candidate_extends_fix41a_without_authority_promotion() -> None:
    base = _load(BASE_CANDIDATE)
    candidate = _load(CANDIDATE)
    assert len(candidate["nodes"]) >= len(base["nodes"])
    assert len(candidate["edges"]) >= len(base["edges"])
    assert candidate["candidate_status"] == "unsigned_support_only_not_canonical_fix45_percolation_candidate"
    assert candidate["fix45_merge_summary"]["added_candidate_edges"] == 103
    assert candidate["fix45_merge_summary"]["added_candidate_nodes"] == 4
    assert candidate["fix45_merge_summary"]["manual_semantic_queue_count"] > 0
    assert "No Genesis signing occurred." in candidate["non_claims"]


def test_fix45_new_edges_are_candidate_only_and_never_governance_edges() -> None:
    candidate = _load(CANDIDATE)
    edges = _fix45_edges(candidate)
    assert edges
    assert {edge["edge_type"] for edge in edges} == {"REFERENCES_AUTHORITY", "SOURCE_TREE_MEMBER"}
    for edge in edges:
        assert edge.get("candidate_status")
        assert edge["edge_type"] != "GOVERNS"
        assert edge["review_status"] == "candidate_only_not_authority_promotion"
        assert edge["annotation_method"] == "fix45_algorithmic_percolation"


def test_fix45_edges_do_not_target_generated_or_out_material() -> None:
    candidate = _load(CANDIDATE)
    forbidden_fragments = ("repo:group:out", "out/", "out_viz_exports", "out_monitoring", "graph_view_")
    for edge in _fix45_edges(candidate):
        target = edge["target"]
        origin = edge.get("origin_repo_path", "")
        assert not any(fragment in target for fragment in forbidden_fragments)
        assert not origin.startswith("out/")
        assert "monitoring/" not in target


def test_fix45_manual_queue_and_reports_preserve_carry_forward() -> None:
    analysis = _load(ANALYSIS)
    ledger = _load(LEDGER)
    manual_queue = _load(MANUAL_QUEUE)
    report = REPORT.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert analysis["total_queue_count"] == 500
    assert ledger["queue_entry_count"] == 500
    assert ledger["decision_counts"]["added_edge"] == 99
    assert manual_queue["entry_count"] == 382
    assert manual_queue["entry_count"] > 0
    assert "Manual semantic carry-forward entries: `382`" in report
    assert "No Genesis signing occurred." in report
    assert "Manual semantic review carry-forward entries: `382`" in walkthrough
    assert "Fix45 did not add\n`GOVERNS` edges" in walkthrough


def test_fix45_new_docs_have_graph_intake_candidate_nodes() -> None:
    candidate = _load(CANDIDATE)
    by_source_path = {
        node.get("source_path"): node
        for node in candidate["nodes"]
        if node.get("source_phase") == "1545p-Fix45"
    }
    assert NEW_DOC_PATHS <= set(by_source_path)
    for path in NEW_DOC_PATHS:
        node = by_source_path[path]
        assert node["candidate_status"] == "fix45_support_only"
        assert node["node_kind"] == "repo_support_doc_node"
        assert node["signature_status"] == "unsigned_candidate"


def test_fix45_prompt_and_builder_preserve_execution_boundaries() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")
    builder = BUILDER.read_text(encoding="utf-8")
    assert "Do not run\nthe manual semantic review tranche in this phase." in prompt
    assert "target:*` nodes have no deterministic authority rule" in prompt
    assert "PUBLIC_RC_EXCLUDE: genesis_base_graph_fix45_targeted_percolation_research_only" in builder
    assert "tempfile.mkstemp" in builder
    assert "os.replace" in builder
    assert "sort_keys=True" in builder
    assert "allow_nan=False" in builder
