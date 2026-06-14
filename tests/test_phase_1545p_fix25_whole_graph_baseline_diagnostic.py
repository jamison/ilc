import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_JSON = ROOT / "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json"
REPORT = ROOT / "docs/sims/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25_v0.1.md"
REVIEW = ROOT / "docs/specs/ilc_atlas_whole_graph_baseline_diagnostic_review_1545p_fix25_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix25_whole_graph_baseline_diagnostic_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


REQUIRED_TOKENS = {
    "whole_graph_atlas_baseline_diagnostic_committed_phase_1545p_fix25",
    "atlas_authority_trace_baseline_recorded_phase_1545p_fix25",
    "atlas_backwards_read_baseline_recorded_phase_1545p_fix25",
    "atlas_duplicate_merge_pressure_baseline_recorded_phase_1545p_fix25",
    "atlas_privacy_tier_baseline_recorded_phase_1545p_fix25",
    "public_path_remains_blocked_phase_1545p_fix25",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _diagnostic() -> dict:
    return json.loads(_read(DIAGNOSTIC_JSON))


def test_fix25_outputs_and_tokens_present():
    surfaces = [_read(REPORT), _read(REVIEW), _read(WALKTHROUGH), _read(STATUS), _read(PLANNING)]
    payload = _diagnostic()

    for token in REQUIRED_TOKENS:
        assert token in payload["tokens"]
        assert any(token in surface for surface in surfaces)


def test_five_coverage_dimensions_are_separate_and_transition_view_not_measured():
    payload = _diagnostic()

    assert payload["node_count"] == 10029
    assert payload["edge_count"] == 27668
    assert payload["merkle_source_tree_membership_coverage"] == 1.0
    assert payload["undirected_laplacian_connectedness"] == 1.0
    assert payload["authority_forward_trace_coverage"] < payload["undirected_laplacian_connectedness"]
    assert payload["verification_backtrace_coverage"] < payload["undirected_laplacian_connectedness"]
    assert payload["classification_rule_trace_coverage"] == 0.0
    assert payload["genesis_bound_transition_envelope_view_status"] == "not_yet_implemented_not_measured"


def test_directed_view_gap_is_recorded_without_merkle_or_lambda2_overclaim():
    payload = _diagnostic()
    gap_by_prefix = payload["directed_view_not_yet_contractualized_by_prefix"]

    assert payload["directed_view_not_yet_contractualized_count"] == 9974
    assert gap_by_prefix["repo"] == 9971
    assert gap_by_prefix["artifact"] == 3
    assert gap_by_prefix["adr"] == 0
    assert gap_by_prefix["cdl"] == 0
    assert gap_by_prefix["policy"] == 0
    assert gap_by_prefix["truth_primitive"] == 0
    assert payload["genesis_rootedness_standard"]["merkle_and_lambda2_authority_scope"] == (
        "not_sufficient_for_authority_eligibility_claimability_or_governance_effect"
    )


def test_lmdb_cross_check_and_review_queue_shape():
    payload = _diagnostic()
    cross_check = payload["fix23_lmdb_cross_check"]

    assert cross_check["node_count_match"] is True
    assert cross_check["edge_count_match"] is True
    assert cross_check["preimage_count_match"] is True
    assert payload["review_queue"]

    for row in payload["review_queue"]:
        assert set(row) == {
            "evidence",
            "issue_class",
            "recommended_next_fix",
            "review_id",
            "severity",
            "source_node_id",
        }
        assert row["review_id"].startswith("atlas-review:")
        assert row["issue_class"] in {
            "authority_trace_gap",
            "backwards_read_gap",
            "duplicate_pressure",
            "privacy_tier_gap",
            "orphan_support_leaf",
            "decomposition_gap",
        }


def test_docs_preserve_non_claims_and_no_placeholder_ellipses():
    combined = "\n".join([_read(REPORT), _read(REVIEW), _read(WALKTHROUGH)])
    normalized = " ".join(combined.split())

    assert "Merkle inclusion and undirected connectedness are not treated as authority proof." in combined
    assert "No Genesis signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No canonical Genesis graph mutation occurred." in combined
    assert "not Genesis Atlas signing-batch-ready" in normalized
    assert "..." not in combined
    assert "…" not in combined
