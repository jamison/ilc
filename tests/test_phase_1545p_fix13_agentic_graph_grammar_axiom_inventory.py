from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_agentic_graph_grammar_axiom_inventory_1545p_fix13_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix13_agentic_graph_grammar_axiom_inventory_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix13_tokens_and_no_activation_boundary() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix13_agentic_graph_grammar_axiom_inventory_committed",
        "agentic_graph_grammar_axiom_inventory_recorded_phase_1545p_fix13",
        "homoiconic_type_axiom_gap_table_recorded_phase_1545p_fix13",
        "graph_research_governance_routing_rule_recorded_phase_1545p_fix13",
        "graph_research_substrate_not_runtime_activation_phase_1545p_fix13",
        "graph_optimization_not_direct_ecu_minting_phase_1545p_fix13",
        "type_registry_not_activated_phase_1545p_fix13",
        "genesis_manifest_not_mutated_phase_1545p_fix13",
        "public_path_remains_blocked_phase_1545p_fix13",
    ]:
        assert token in text

    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in text
    assert "The type registry is not activated." in text


def test_required_vocabulary_items_are_present() -> None:
    text = read(SPEC)

    for item in [
        "`node_type_definition`",
        "`edge_type_definition`",
        "`hyperedge_arity_definition`",
        "`rewrite_rule_candidate`",
        "`rewrite_interface_boundary`",
        "`negative_application_condition`",
        "`projection_operator`",
        "`hydration_slice_contract`",
        "`maintenance_task_evidence_package`",
        "`optimization_candidate_score_vector`",
    ]:
        assert item in text


def test_research_mechanism_mapping_is_recorded() -> None:
    text = read(SPEC)

    for mechanism in [
        "HRG",
        "DPO/SPO",
        "TPP",
        "E-graph / equality saturation",
        "Morphogenesis",
        "Agent hydration",
    ]:
        assert mechanism in text

    assert "Pushout-style rewrite validity does not imply protocol promotion." in text
    assert "Transitivity-preserving support views are not canonical edges." in text


def test_governance_routing_rule_is_explicit() -> None:
    text = read(SPEC)

    assert "Start with specs and candidate prompts" in text
    assert "ADR is required if a mechanism becomes a protocol architecture rule" in text
    assert "CDL is required only when the mechanism assigns constitutional authority" in text
    assert "No research mechanism may infer ADR/CDL authority" in text


def test_non_claims_and_frontier_docs_record_fix13() -> None:
    text = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    assert "Graph optimization candidates do not directly generate ECU or ILC." in text
    assert "does not implement a rewrite engine" in text
    assert "mutate `out/genesis_core_star_map_v0.3_candidate.json`" in text

    assert "phase_1545p_fix13_agentic_graph_grammar_axiom_inventory_committed" in walkthrough
    assert "Phase 1545p-Fix13" in status
    assert "Phase 1545p-Fix13" in planning
    fix13_line = planning.split("Phase 1545p-Fix13", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix13_line or "Superseded as current frontier" in fix13_line
