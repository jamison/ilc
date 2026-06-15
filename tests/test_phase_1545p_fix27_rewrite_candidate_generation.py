import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_atlas_rewrite_candidate_generation_1545p_fix27.json"
CANDIDATES = ROOT / "out/atlas_research/genesis_atlas_rewrite_candidates_1545p_fix27.jsonl"
FIX22 = ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
RUNNER = ROOT / "tools/evaluators/sim_atlas_rewrite_candidate_generation_1545p_fix27.py"
GENESIS_ROOT = "artifact:genesis_intent_attestation_init_authority_map"


REQUIRED_TOKENS = {
    "atlas_rewrite_candidate_generation_committed_phase_1545p_fix27",
    "atlas_dpo_invariant_checks_recorded_phase_1545p_fix27",
    "atlas_hyperedge_replacement_candidates_recorded_phase_1545p_fix27",
    "atlas_node_merge_split_candidates_recorded_phase_1545p_fix27",
    "atlas_rewrite_candidates_not_promoted_phase_1545p_fix27",
    "public_path_remains_blocked_phase_1545p_fix27",
}


REQUIRED_RECORD_FIELDS = {
    "atom_candidate_refs",
    "deleted_material",
    "expected_objective_delta",
    "fix26_hypothesis_scope",
    "fix26_terminal_resolution",
    "interface_boundary",
    "invariant_checklist",
    "left_pattern",
    "matched_subgraph",
    "negative_application_conditions",
    "passage_validation",
    "preserved_interface",
    "promotion_boundary",
    "proof_class_delta",
    "review_class",
    "rewrite_candidate_id",
    "right_pattern",
    "rule_type",
    "source_evidence",
    "terminal_confidence_class",
    "typed_trace_edge_roles",
}


def _summary():
    _ensure_outputs()
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def _records():
    _ensure_outputs()
    return [
        json.loads(line)
        for line in CANDIDATES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _ensure_outputs():
    if SUMMARY.exists() and CANDIDATES.exists():
        return
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)


def test_fix27_summary_counts_and_tokens():
    summary = _summary()
    records = _records()

    assert summary["phase"] == "1545p-Fix27"
    assert summary["candidate_record_count"] == len(records)
    assert summary["candidate_record_count"] > 30_000
    assert set(summary["output_tokens"]) == REQUIRED_TOKENS
    assert summary["dpo_invariant_summary"]["canonical_graph_mutated"] is False
    assert summary["dpo_invariant_summary"]["endpoint_validity_failures"] == 0
    assert summary["dpo_invariant_summary"]["role_declaration_failures"] == 0


def test_fix27_rule_families_and_review_classes_present():
    summary = _summary()
    rule_counts = summary["rule_type_counts"]
    review_counts = summary["review_class_counts"]

    for rule_type in {
        "edge_refine",
        "hyperedge_replace",
        "node_merge",
        "node_split",
        "projection_simplify",
        "semantic_pre_pass",
    }:
        assert rule_counts[rule_type] > 0

    assert review_counts["candidate_keep_for_fix30"] > 0
    assert review_counts["candidate_defer"] > 0
    assert review_counts["candidate_reject"] > 0
    assert summary["fix26_input_counts"] == {
        "accepted_atom_candidates_for_review": 5482,
        "deferred_low_confidence": 14958,
    }


def test_fix27_records_have_required_dpo_and_proof_fields():
    records = _records()
    rule_counts = Counter()
    for record in records:
        rule_counts[record["rule_type"]] += 1
        assert REQUIRED_RECORD_FIELDS <= set(record)
        assert record["promotion_boundary"]
        assert "research_only" in record["promotion_boundary"] or record["rule_type"] == "projection_simplify"
        assert record["invariant_checklist"]["activation_claim_absent"] is True
        assert record["invariant_checklist"]["signed_artifact_mutation_absent"] is True
        assert record["invariant_checklist"]["endpoint_validity_preserved"] is True
        assert record["invariant_checklist"]["typed_trace_roles_declared_for_all_added_nodes"] is True
        assert record["typed_trace_edge_roles"]
        assert record["proof_class_delta"]
        assert record["matched_subgraph"]
        assert "vertex_ids" in record["matched_subgraph"]

    assert rule_counts["hyperedge_replace"] > 0
    assert rule_counts["node_merge"] > 0
    assert rule_counts["node_split"] > 0


def test_fix27_reclassifies_b10_b12_genesis_fallback_edges():
    records = _records()
    source_tree_member_count = 0
    bad_authority_fallbacks = []
    for record in records:
        for edge in record["right_pattern"].get("add_edges", []):
            provenance = edge.get("provenance", "")
            if edge.get("edge_type") == "SOURCE_TREE_MEMBER":
                source_tree_member_count += 1
            if (
                edge.get("target") == GENESIS_ROOT
                and edge.get("edge_type") == "REFERENCES_AUTHORITY"
                and any(batch in provenance for batch in ("_b10", "_b11", "_b12"))
            ):
                bad_authority_fallbacks.append(edge)

    assert source_tree_member_count > 0
    assert bad_authority_fallbacks == []


def test_fix27_preserves_fix22_baseline_counts_and_no_annotation_flags():
    graph = json.loads(FIX22.read_text(encoding="utf-8"))
    assert len(graph["nodes"]) == 10029
    assert len(graph["edges"]) == 27668
    assert not any(
        node.get("manually_annotated") or node.get("prepass_annotated")
        for node in graph["nodes"]
    )
