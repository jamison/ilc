from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_hypergraph_visualization_projection_sidecar_spec_1545p_fix12_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix12_hypergraph_visualization_projection_sidecar_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix12_tokens_and_local_only_boundary() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix12_hypergraph_visualization_projection_sidecar_spec_committed",
        "hypergraph_visualization_sidecar_local_only_phase_1545p_fix12",
        "transitivity_preserving_projection_visualization_boundary_recorded_phase_1545p_fix12",
        "zackarydev_depgraph_visual_affordance_analysis_integrated_phase_1545p_fix12",
        "human_visual_impact_rubric_recorded_phase_1545p_fix12",
        "layout_hub_policy_recorded_phase_1545p_fix12",
        "projection_semantics_not_canonical_graph_mutation_phase_1545p_fix12",
        "public_sidecar_serving_not_activated_phase_1545p_fix12",
        "genesis_manifest_not_mutated_phase_1545p_fix12",
        "public_path_remains_blocked_phase_1545p_fix12",
    ]:
        assert token in text

    assert "local-only visualization sidecar" in text
    assert "No DepGraph or HCSN code is vendored, imported, copied, or made a dependency." in text


def test_projection_modes_and_semantic_loss_warnings() -> None:
    text = read(SPEC)

    for phrase in [
        "Incidence bipartite projection",
        "Split-clique projection",
        "Split-path projection",
        "Aggregate-collapse projection",
        "Transitivity-preserving projection",
        "Structure-aware simplification",
        "Semantic-loss warning",
        "UI state, not graph mutation",
    ]:
        assert phrase in text


def test_depgraph_affordances_and_visual_impact_rubric() -> None:
    text = read(SPEC)

    for phrase in [
        "Trace waves",
        "Gather",
        "Rewind and time travel",
        "Semantic zoom",
        "Cluster hulls",
        "Meta-edges",
        "First-glance orientation",
        "Path-following clarity",
        "Recovery from disorientation",
        "Accessibility",
    ]:
        assert phrase in text


def test_adopt_adapt_reject_and_hub_policy_are_explicit() -> None:
    text = read(SPEC)

    for phrase in [
        "`adopt_concept`",
        "`adapt_with_constraints`",
        "`reject_for_protocol`",
        "Nondeterministic layout as canonical evidence",
        "High-degree nodes",
        "Genesis / root",
        "Namespace and common nodes",
        "ADR/CDL nodes",
    ]:
        assert phrase in text


def test_privacy_public_serving_and_canonical_mutation_non_claims() -> None:
    text = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    for phrase in [
        "Do not display raw upstream path sets",
        "No public sidecar serving",
        "public projection endpoint",
        "non-loopback bind",
        "UI layout, hulls, colors, animation, and local history are not canonical graph mutation.",
        "This recipe is not registered and not activated by Fix12.",
    ]:
        assert phrase in text

    assert "phase_1545p_fix12_hypergraph_visualization_projection_sidecar_spec_committed" in walkthrough
    assert "Phase 1545p-Fix12" in status
    assert "Phase 1545p-Fix12" in planning
    fix12_line = planning.split("Phase 1545p-Fix12", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix12_line or "Superseded as current frontier" in fix12_line
