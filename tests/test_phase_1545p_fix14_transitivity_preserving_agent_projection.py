from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_transitivity_preserving_agent_projection_spec_1545p_fix14_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix14_transitivity_preserving_agent_projection_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix14_tokens_and_support_only_boundary() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix14_transitivity_preserving_agent_projection_spec_committed",
        "tpp_agent_projection_support_only_phase_1545p_fix14",
        "projection_uniqueness_idempotence_minimality_recorded_phase_1545p_fix14",
        "agent_projection_semantic_loss_annotations_recorded_phase_1545p_fix14",
        "projection_not_canonical_graph_mutation_phase_1545p_fix14",
        "public_sidecar_serving_not_activated_phase_1545p_fix14",
        "public_path_remains_blocked_phase_1545p_fix14",
    ]:
        assert token in text

    assert "support-only, local agent-facing projection contract" in text
    assert "This recipe is not registered or activated by Fix14." in text


def test_request_response_schema_and_operator_classes_are_recorded() -> None:
    text = read(SPEC)

    for field in [
        "`projection_request_id`",
        "`operator_id`",
        "`source_bundle_refs`",
        "`root_node_ids`",
        "`target_relation_types`",
        "`semantic_loss_policy`",
        "`projection_id`",
        "`dominant_metapaths`",
        "`irreducible_path_families`",
        "`omitted_path_families`",
        "`non_authorization_tokens`",
    ]:
        assert field in text

    for operator in [
        "`incidence_support_projection`",
        "`dominant_metapath_projection`",
        "`irreducible_transitive_projection`",
        "`bounded_hydration_slice_projection`",
        "`agent_memory_summary_projection`",
    ]:
        assert operator in text


def test_uniqueness_idempotence_minimality_and_canonical_json_are_explicit() -> None:
    text = read(SPEC)

    for phrase in [
        "Equivalent canonical inputs produce the same projection id.",
        "must not create new facts",
        "A retained metapath is minimal only if removing it changes declared reachability",
        "Sort path-family rows by",
        "deterministic key ordering",
        "allow_nan=False",
        "no wall-clock protocol fields",
    ]:
        assert phrase in text


def test_semantic_loss_privacy_serving_and_non_claims_are_explicit() -> None:
    text = read(SPEC)

    for phrase in [
        "`lossless_incidence`",
        "`collapsed_hyperedge_identity`",
        "`omitted_parallel_paths`",
        "`inferred_transitive_support`",
        "`privacy_redacted_paths`",
        "`bounded_context_truncation`",
        "Projection output is not a graph write",
        "No public sidecar serving",
        "raw agent IDs must not be exposed",
        "does not mint ECU",
    ]:
        assert phrase in text


def test_frontier_docs_record_fix14() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    assert "phase_1545p_fix14_transitivity_preserving_agent_projection_spec_committed" in walkthrough
    assert "Phase 1545p-Fix14" in status
    assert "Phase 1545p-Fix14" in planning
    fix14_line = planning.split("Phase 1545p-Fix14", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix14_line
