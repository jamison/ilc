from __future__ import annotations

import json
from pathlib import Path

from tools.evaluators.genesis_optimization_harness import (
    AUTHORITY_STATUS,
    ARTIFACT_STATUS,
    HarnessInputs,
    build_genesis_optimization_evaluation,
    default_inputs,
    export_genesis_optimization_evaluation_json,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_genesis_optimization_autoresearch_harness_1545p_fix9_v0.1.md"
OUTPUT = ROOT / "out/genesis_optimization_candidate_scores_1545p_fix9.json"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.3_candidate.json"
DIAGNOSTIC = ROOT / "out/genesis_compile_coverage_diagnostic_v0.3_candidate.json"
QUEUE = ROOT / "out/genesis_common_registry_node_candidates_1545p_fix7.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix9_genesis_optimization_autoresearch_harness_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix9_tokens_and_objective_boundary_are_recorded() -> None:
    text = read(SPEC)
    for token in (
        "phase_1545p_fix9_genesis_optimization_autoresearch_harness_committed",
        "genesis_optimization_harness_support_only_phase_1545p_fix9",
        "human_objective_selection_boundary_recorded_phase_1545p_fix9",
        "candidate_scoring_not_authority_recorded_phase_1545p_fix9",
        "genesis_manifest_not_mutated_phase_1545p_fix9",
        "public_path_remains_blocked_phase_1545p_fix9",
    ):
        assert token in text
    assert "Candidate scoring is not authority." in text
    assert "Humans select goals and scoring rubrics" in text


def test_default_evaluation_is_support_only_and_canonical() -> None:
    exported_once = export_genesis_optimization_evaluation_json(default_inputs())
    exported_twice = export_genesis_optimization_evaluation_json(default_inputs())
    committed = read(OUTPUT)

    assert exported_once == exported_twice
    assert exported_once == committed

    data = json.loads(committed)
    assert data["artifact_status"] == ARTIFACT_STATUS
    assert data["authority_status"] == AUTHORITY_STATUS
    assert data["rejected"] is False
    assert data["reject_reasons"] == []
    assert data["public_path"] == "blocked"
    assert data["human_objective_selection_required"] is True
    assert data["source_coverage_baseline_ratio"] == "0.311384"


def test_objective_vector_uses_string_scores_not_float() -> None:
    data = json.loads(read(OUTPUT))
    vector = data["objective_vector"]
    expected_fields = {
        "authority_traceability_preservation",
        "basis_reachability_preservation",
        "source_coverage_improvement",
        "decomposition_recipe_coverage",
        "edge_endpoint_validity",
        "minimality",
        "semantic_justification_strength",
        "registry_namespace_hygiene",
        "visualization_projection_clarity",
        "non_gaming_penalty",
    }
    assert set(vector) == expected_fields
    assert all(isinstance(value, str) for value in vector.values())
    assert all(value.count(".") == 1 and len(value.rsplit(".", 1)[1]) == 6 for value in vector.values())


def test_mutated_candidate_is_rejected_with_stable_reasons(tmp_path: Path) -> None:
    candidate = json.loads(read(STAR_MAP))
    candidate["nodes"] = [
        node
        for node in candidate["nodes"]
        if node.get("candidate_id")
        not in {"truth_primitive:commit.epoch", "genesis_agent:01"}
    ]
    candidate["metadata"]["transition_basis"] = ["truth_primitive:assert.truth"]
    candidate["edges"].append(
        {
            "edge_id": "edge:bad_optimization_candidate",
            "edge_type": "LINKS",
            "source": "truth_primitive:assert.truth",
            "target": "missing:node",
            "rationale": "activate public rc and mint ecu",
        }
    )
    bad_path = tmp_path / "bad_candidate.json"
    bad_path.write_text(
        json.dumps(candidate, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = build_genesis_optimization_evaluation(
        HarnessInputs(
            candidate_path=bad_path,
            baseline_path=STAR_MAP,
            diagnostic_path=DIAGNOSTIC,
            registry_queue_path=QUEUE,
        )
    )

    assert result["rejected"] is True
    reasons = set(result["reject_reasons"])
    assert "basis_reachability_required_nodes_missing" in reasons
    assert "authority_traceability_required_nodes_missing" in reasons
    assert "transition_basis_mismatch" in reasons
    assert "edge_endpoint_invalid:edge:bad_optimization_candidate" in reasons
    assert "decomposition_recipe_missing:edge:bad_optimization_candidate" in reasons
    assert "activation_claim_detected" in reasons
    assert result["objective_vector"]["non_gaming_penalty"] == "1.000000"


def test_frontier_docs_record_fix9() -> None:
    for path in (WALKTHROUGH, STATUS, PLANNING_INDEX):
        text = read(path)
        assert "phase_1545p_fix9_genesis_optimization_autoresearch_harness_committed" in text
        assert "genesis_optimization_harness_support_only_phase_1545p_fix9" in text
        assert "public_path_remains_blocked_phase_1545p_fix9" in text
    assert "the harness does not promote candidates to Genesis authority" in read(WALKTHROUGH)
