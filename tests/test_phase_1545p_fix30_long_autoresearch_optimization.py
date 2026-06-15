import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_atlas_long_autoresearch_optimization_1545p_fix30.json"
ITERATIONS = ROOT / "out/atlas_research/genesis_atlas_autoresearch_iterations_1545p_fix30.jsonl"
OPTIMIZED = ROOT / "out/atlas_research/genesis_atlas_optimized_candidate_1545p_fix30.json"
REPORT = ROOT / "docs/sims/sim_atlas_long_autoresearch_optimization_1545p_fix30_v0.1.md"
REVIEW = ROOT / "docs/specs/ilc_atlas_long_autoresearch_optimization_review_1545p_fix30_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix30_g10_long_autoresearch_optimization_run.md"
CHECKPOINT_DIR = ROOT / "out/atlas_research/fix30_checkpoints"


REQUIRED_TOKENS = {
    "atlas_long_autoresearch_run_committed_phase_1545p_fix30",
    "atlas_iteration_keep_revert_log_committed_phase_1545p_fix30",
    "atlas_objective_vector_improvement_recorded_phase_1545p_fix30",
    "atlas_invariant_preservation_confirmed_phase_1545p_fix30",
    "atlas_optimized_candidate_not_signed_phase_1545p_fix30",
    "public_path_remains_blocked_phase_1545p_fix30",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _iterations():
    return [json.loads(line) for line in ITERATIONS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_fix30_outputs_and_required_tokens_present():
    payload = _json(SUMMARY)
    combined = SUMMARY.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")

    assert payload["status"] == "pass"
    assert payload["phase"] == "1545p-Fix30"
    assert payload["sim_id"] == "SIM-ATLAS-AUTORESEARCH-01"
    assert REQUIRED_TOKENS.issubset(set(payload["output_tokens"]))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_fix30_fixed_budget_iteration_log_and_checkpoints():
    payload = _json(SUMMARY)
    records = _iterations()

    assert payload["iteration_count"] == 200
    assert len(records) == 200
    assert all(budget == 20 for budget in payload["operator_budgets"].values())
    assert records[0]["iteration"] == 1
    assert records[-1]["iteration"] == 200
    assert payload["objective_summary"]["verdict_counts"]["KEEP"] == 46
    assert len(list(CHECKPOINT_DIR.glob("checkpoint_*.json"))) == 46


def test_fix30_invariants_and_fiedler_firewall():
    payload = _json(SUMMARY)
    records = _iterations()
    summary = payload["objective_summary"]
    fiedler = payload["fiedler_carry_forward"]

    assert summary["endpoint_error_count"] == 0
    assert summary["root_reachable_node_count"] == summary["optimized_node_count"]
    assert summary["accepted_edge_count"] == 46
    assert summary["objective_delta"]["spectral_lambda2_claim_delta"] == "not_recomputed_no_spectral_claim"
    assert fiedler["clique_incidence_fiedler_vector_status"] == "available_boundary_hint_only"
    assert fiedler["star_fiedler_vector_status"] == "not_available_budget_fallback"
    assert fiedler["anti_gaming_result"] == "no_keep_based_only_on_lambda2_bridge_or_articulation_improvement"

    keep_records = [record for record in records if record["verdict"] == "KEEP"]
    assert keep_records
    for record in keep_records:
        assert record["objective_delta"]["spectral_gain_claim"] == "not_used_for_keep_decision"
        assert record["hard_invariants"]["spectral_only_keep_absent"] is True
        assert record["proof_class_delta"]["nodes_downgraded"] == 0
        assert record["typed_trace_edge_roles"]


def test_fix30_optimized_candidate_is_research_only_and_no_authority_padding():
    payload = _json(SUMMARY)
    optimized = _json(OPTIMIZED)

    assert optimized["candidate_status"] == "research_only_unsigned_optimized_candidate_phase_1545p_fix30"
    assert optimized["fix30_added_edge_count"] == payload["objective_summary"]["accepted_edge_count"]
    added = [
        edge
        for edge in optimized["edges"]
        if edge.get("feature_hints", {}).get("phase") == "1545p-Fix30"
    ]
    assert len(added) == payload["objective_summary"]["accepted_edge_count"]
    assert all(edge["edge_type"] not in {"GOVERNS", "ATTESTATION"} for edge in added)
    assert all(
        edge["feature_hints"]["promotion_boundary"]
        == "research_only_no_canonical_mutation_no_signing_no_activation"
        for edge in added
    )


def test_fix30_docs_preserve_nonclaims_and_no_placeholder_ellipses():
    combined = (
        PROMPT.read_text(encoding="utf-8")
        + REPORT.read_text(encoding="utf-8")
        + REVIEW.read_text(encoding="utf-8")
    )

    assert "No Genesis v0.4 or v0.5 signing occurred." in combined
    assert "not authority proof" in combined
    assert "not_available_budget_fallback" in combined
    assert "Do not use `...`, `…`, or placeholder text." in combined
    assert "..." not in combined.replace("Do not use `...`, `…`, or placeholder text.", "")
    assert "…" not in combined.replace("Do not use `...`, `…`, or placeholder text.", "")
