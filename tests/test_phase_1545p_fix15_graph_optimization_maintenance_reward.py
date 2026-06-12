from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_graph_optimization_maintenance_reward_spec_1545p_fix15_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix15_g10_graph_optimization_maintenance_reward_spec.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix15_graph_optimization_maintenance_reward_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix15_tokens_and_no_direct_mint_boundary() -> None:
    text = read(SPEC)

    for token in [
        "phase_1545p_fix15_graph_optimization_maintenance_reward_spec_committed",
        "graph_optimization_maintenance_reward_boundary_recorded_phase_1545p_fix15",
        "graph_optimization_evidence_package_requirements_recorded_phase_1545p_fix15",
        "graph_optimization_not_minting_recorded_phase_1545p_fix15",
        "productive_ecu_expansion_guard_retained_phase_1545p_fix15",
        "peer_funded_bounty_runtime_not_activated_phase_1545p_fix15",
        "public_path_remains_blocked_phase_1545p_fix15",
    ]:
        assert token in text

    assert "without directly minting ECU" in text
    assert "does not authorize any payout" in text


def test_task_taxonomy_and_evidence_package_requirements_are_present() -> None:
    text = read(SPEC)

    for task_class in [
        "`missing_canonical_edge_discovery`",
        "`type_definition_gap_discovery`",
        "`graph_grammar_repair_proposal`",
        "`projection_compression_improvement`",
        "`transitivity_preserving_projection_improvement`",
        "`hydration_slice_quality_improvement`",
        "`anti_gaming_or_invariant_break_discovery`",
        "`source_coverage_improvement`",
        "`decomposition_recipe_improvement`",
        "`privacy_preserving_proximity_evidence_improvement`",
    ]:
        assert task_class in text

    for field in [
        "`candidate_id`",
        "`claimed_graph_delta`",
        "`direct_read_sources`",
        "`reproduction_command`",
        "`before_after_score_vector`",
        "`invariant_preservation_checklist`",
        "`anti_gaming_checklist`",
        "`non_activation_tokens`",
    ]:
        assert field in text


def test_review_path_antigaming_and_guard_retention_are_explicit() -> None:
    text = read(SPEC)

    for phrase in [
        "No reward for merely increasing node or edge count.",
        "No reward for making sources harder to audit.",
        "No reward for a claim without repo evidence",
        "No reward for candidates that require unratified authority",
        "`PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED` | Retained.",
        "`PRODUCTION_EMISSION_NOT_ACTIVATED=True` | Preserved.",
        "`TREASURY_DISTRIBUTION_NOT_ACTIVATED=True` | Preserved.",
        "Economic event | A canonical economic event may be emitted only by an already authorized runtime path.",
    ]:
        assert phrase in text


def test_adr0016_current_status_clarification_is_recorded() -> None:
    text = read(SPEC)
    prompt = read(PROMPT)

    assert "ADR-0016 is currently Accepted." in text
    assert "`ADR_0016_STATUS_PROPOSED` because it was created before Fix17 acceptance" in text
    assert "adr_0016_accepted_phase_1545p_fix17" in prompt
    assert "treat `ADR_0016_STATUS_PROPOSED` as a historical activation-gating" in prompt


def test_frontier_docs_record_fix15() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    assert "phase_1545p_fix15_graph_optimization_maintenance_reward_spec_committed" in walkthrough
    assert "Phase 1545p-Fix15" in status
    assert "Phase 1545p-Fix15" in planning
    fix15_line = planning.split("Phase 1545p-Fix15", 1)[1].splitlines()[0]
    assert "⬅ CURRENT" in fix15_line or "Superseded as current frontier by Fix16" in fix15_line
