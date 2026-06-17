from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix46_g10_manual_semantic_annotation.md"
BASE_CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix45.json"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix46.json"
LEDGER = ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_ledger_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_report_v0.1.md"
RESIDUAL_QUEUE = ROOT / "docs/specs/ilc_fix47_residual_semantic_annotation_queue_v0.1.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix46_manual_semantic_annotation_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
BUILDER = ROOT / "tools/evaluators/sim_genesis_base_graph_fix46_manual_semantic_annotation.py"

NEW_DOC_PATHS = {
    "docs/specs/ilc_fix46_manual_semantic_annotation_ledger_v0.1.json",
    "docs/specs/ilc_fix46_manual_semantic_annotation_report_v0.1.md",
    "docs/specs/ilc_fix47_residual_semantic_annotation_queue_v0.1.json",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fix46_edges(candidate: dict) -> list[dict]:
    return [edge for edge in candidate["edges"] if edge.get("source_phase") == "1545p-Fix46"]


def test_fix46_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "fix46_manual_semantic_annotation_complete",
        "fix46_enriched_candidate_produced",
        "fix46_residual_queue_produced",
        "fix46_complete",
        "public_path_remains_blocked_phase_1545p_fix46",
    ):
        assert token in status


def test_fix46_candidate_extends_fix45_and_preserves_unsigned_boundary() -> None:
    base = _load(BASE_CANDIDATE)
    candidate = _load(CANDIDATE)
    assert len(candidate["nodes"]) >= len(base["nodes"])
    assert len(candidate["edges"]) >= len(base["edges"])
    assert candidate["candidate_status"] == "unsigned_support_only_not_canonical_fix46_manual_semantic_candidate"
    assert candidate["fix46_merge_summary"]["queue_entry_count"] == 382
    assert candidate["fix46_merge_summary"]["added_candidate_edges"] == 963
    assert candidate["fix46_merge_summary"]["residual_queue_count"] == 101
    assert "No Genesis signing occurred." in candidate["non_claims"]


def test_fix46_ledger_records_batches_of_ten_with_tail() -> None:
    ledger = _load(LEDGER)
    assert ledger["queue_entry_count"] == 382
    assert ledger["batch_count"] == 39
    assert len(ledger["rows"]) == 382
    assert all(row.get("batch_id") for row in ledger["rows"])
    assert all(row.get("batch_index") for row in ledger["rows"])
    for batch_id, count in ledger["batch_counts"].items():
        if batch_id != "fix46_batch_039":
            assert count == 10
    assert ledger["batch_counts"]["fix46_batch_039"] == 2
    assert ledger["source_read_disposition_counts"]["read_text"] == 375


def test_fix46_edges_are_evidence_backed_candidate_edges() -> None:
    candidate = _load(CANDIDATE)
    edges = _fix46_edges(candidate)
    assert len(edges) == 963
    assert {edge["edge_type"] for edge in edges} == {
        "IMPLEMENTS",
        "IMPORTS_MODULE",
        "REFERENCES_AUTHORITY",
        "SOURCE_TREE_MEMBER",
        "TESTS",
    }
    assert any(edge["edge_type"] != "REFERENCES_AUTHORITY" for edge in edges)
    for edge in edges:
        assert edge.get("candidate_status")
        assert edge.get("annotation_method") == "fix46_manual_semantic_batch_read"
        assert edge.get("origin_repo_path")
        assert edge.get("review_status") == "candidate_only_not_authority_promotion"
        assert edge.get("evidence")
        assert edge["edge_type"] != "GOVERNS"


def test_fix46_edges_do_not_target_generated_or_out_material() -> None:
    candidate = _load(CANDIDATE)
    forbidden_fragments = ("repo:group:out", "out/", "out_viz_exports", "out_monitoring", "graph_view_")
    for edge in _fix46_edges(candidate):
        assert not any(fragment in edge["target"] for fragment in forbidden_fragments)
        assert not edge.get("origin_repo_path", "").startswith("out/")


def test_fix46_residual_queue_report_and_walkthrough_are_consistent() -> None:
    ledger = _load(LEDGER)
    residual = _load(RESIDUAL_QUEUE)
    report = REPORT.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert residual["entry_count"] == 101
    assert residual["status"] == "PASS"
    assert ledger["edge_type_counts_added"] == {
        "IMPLEMENTS": 34,
        "IMPORTS_MODULE": 140,
        "REFERENCES_AUTHORITY": 663,
        "SOURCE_TREE_MEMBER": 19,
        "TESTS": 107,
    }
    assert "Candidate edges added: `963`" in report
    assert "Residual Fix47 entries: `101`" in report
    assert "Fix46 consumed the Fix45 manual semantic queue in deterministic batches of ten" in walkthrough
    assert "No Genesis signing occurred." in walkthrough


def test_fix46_new_docs_have_graph_intake_candidate_nodes() -> None:
    candidate = _load(CANDIDATE)
    by_source_path = {
        node.get("source_path"): node
        for node in candidate["nodes"]
        if node.get("source_phase") == "1545p-Fix46"
    }
    assert NEW_DOC_PATHS <= set(by_source_path)
    for path in NEW_DOC_PATHS:
        node = by_source_path[path]
        assert node["candidate_status"] == "fix46_support_only"
        assert node["node_kind"] == "repo_support_doc_node"
        assert node["signature_status"] == "unsigned_candidate"


def test_fix46_prompt_and_builder_preserve_manual_batch_contract() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")
    builder = BUILDER.read_text(encoding="utf-8")
    assert "batches of `10` files" in prompt
    assert "Do not restrict the pass to governance references." in prompt
    assert "PUBLIC_RC_EXCLUDE: genesis_base_graph_fix46_manual_semantic_annotation_research_only" in builder
    assert "tempfile.mkstemp" in builder
    assert "os.replace" in builder
    assert "sort_keys=True" in builder
    assert "allow_nan=False" in builder
