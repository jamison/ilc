import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/evaluators/sim_atlas_projection_hydration_1545p_fix28.py"
SUMMARY = ROOT / "out/sim_atlas_projection_hydration_1545p_fix28.json"
SLICES = ROOT / "out/atlas_research/genesis_atlas_projection_hydration_slices_1545p_fix28.json"
REPORT = ROOT / "docs/sims/sim_atlas_projection_hydration_1545p_fix28_v0.1.md"
REVIEW = ROOT / "docs/specs/ilc_atlas_projection_hydration_review_1545p_fix28_v0.1.md"


REQUIRED_TOKENS = {
    "atlas_projection_hydration_sim_committed_phase_1545p_fix28",
    "atlas_transitivity_projection_checks_recorded_phase_1545p_fix28",
    "atlas_hydration_slice_budget_checks_recorded_phase_1545p_fix28",
    "atlas_semantic_loss_annotations_recorded_phase_1545p_fix28",
    "atlas_projection_hydration_not_public_serving_phase_1545p_fix28",
    "public_path_remains_blocked_phase_1545p_fix28",
}


REQUIRED_SLICE_FIELDS = {
    "authority_class_filter",
    "authority_reachability",
    "b10_b12_fallback_edge_count",
    "delta_authority_reachability",
    "directed_view_not_yet_contractualized_count",
    "max_bytes",
    "max_edges",
    "max_hops",
    "max_nodes",
    "non_authorization_tokens",
    "path_family_digest",
    "permission_decision",
    "privacy_class_filter",
    "proof_class_distribution",
    "reachability_loss",
    "replay_digest",
    "root_node_ids",
    "semantic_loss_annotations",
    "slice_id",
    "slice_type",
    "source_citations",
    "typed_trace_roles_present",
}


def _ensure_outputs() -> None:
    if SUMMARY.exists() and SLICES.exists() and REPORT.exists() and REVIEW.exists():
        return
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)


def _summary() -> dict:
    _ensure_outputs()
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def _slices() -> dict:
    _ensure_outputs()
    return json.loads(SLICES.read_text(encoding="utf-8"))


def test_fix28_summary_tokens_and_fallback_filter():
    summary = _summary()

    assert summary["phase"] == "1545p-Fix28"
    assert summary["status"] == "pass"
    assert set(summary["output_tokens"]) == REQUIRED_TOKENS
    assert summary["b10_b12_fallback_filter_applied"] is True
    assert summary["b10_b12_fallback_edge_count"] > 0
    assert "source_tree_member_to_node0" in summary["fallback_count_source"]
    assert summary["fix22_node_count"] == 10029
    assert summary["fix22_edge_count"] == 27668
    assert summary["fix27_candidate_record_count"] == 31741


def test_fix28_slices_have_required_projection_and_trace_fields():
    payload = _slices()
    slices = payload["slices"]

    assert payload["phase"] == "1545p-Fix28"
    assert payload["fallback_filter"]["b10_b12_fallback_edge_count"] > 0
    assert len(slices) >= 7
    assert {
        "onboarding_seed_slice",
        "type_definition_slice",
        "sidecar_recipe_slice",
        "maintenance_evidence_slice",
        "public_release_candidate_slice",
        "private_excluded_slice",
        "rejected_budget_exceeded_slice",
    } <= {record["slice_type"] for record in slices}

    for record in slices:
        assert REQUIRED_SLICE_FIELDS <= set(record)
        assert record["path_family_digest"]
        assert record["replay_digest"]
        assert "SOURCE_TREE_MEMBER" not in record["typed_trace_roles_present"]
        assert set(record["proof_class_distribution"]) == {
            "merkle_inclusion_only",
            "merkle_plus_typed_authority_eligibility_path",
            "merkle_plus_typed_non_authority_trace",
        }
        assert "projection_hydration_not_public_serving_phase_1545p_fix28" in record[
            "non_authorization_tokens"
        ]
        assert "projection_hydration_not_live_zkp_phase_1545p_fix28" in record[
            "non_authorization_tokens"
        ]


def test_fix28_private_slice_redacts_roots_edges_and_citations():
    private_slice = next(
        record for record in _slices()["slices"] if record["slice_type"] == "private_excluded_slice"
    )

    assert private_slice["root_node_ids_redacted"] is True
    assert private_slice["root_node_ids"]
    assert all(root.startswith("redacted_node:") for root in private_slice["root_node_ids"])
    assert all(
        edge["source"].startswith("redacted_node:") and edge["target"].startswith("redacted_node:")
        for edge in private_slice["hydrated_edges"]
    )
    assert all(
        citation.startswith("redacted_private_path_sha256:") or citation.startswith("node:")
        for citation in private_slice["source_citations"]
    )
    assert "privacy_redacted_paths" in private_slice["semantic_loss_annotations"]


def test_fix28_rejected_slice_and_reachability_loss_are_explicit():
    slices = _slices()["slices"]
    rejected = next(
        record for record in slices if record["slice_type"] == "rejected_budget_exceeded_slice"
    )

    assert rejected["permission_decision"] == "denied_privacy_budget"
    assert rejected["reachability_loss"] is True
    assert "bounded_context_truncation" in rejected["semantic_loss_annotations"]
    assert any(record["reachability_loss"] for record in slices)
    assert all("delta_authority_reachability" in record for record in slices)


def test_fix28_reports_preserve_research_only_non_claims():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPORT, REVIEW)
    )

    assert "No public serving" in combined
    assert "No public serving, public P2P, live ZKP" in combined
    assert "No Genesis signing" in combined or "Genesis signing" in combined
    assert "No ADR or CDL mutation" not in combined or "No" in combined
    assert "SOURCE_TREE_MEMBER/provisional fallback edges" in SLICES.read_text(encoding="utf-8")
