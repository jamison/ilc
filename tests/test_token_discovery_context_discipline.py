from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_exact_token_search_is_completion_check_only_in_agent_memory_and_schema():
    required_paths = [
        "AGENTS.md",
        "docs/antigravity_tasks/README.md",
    ]

    for path in required_paths:
        text = read_repo(path)
        assert "schema/completion check" in text
        assert "token components" in text
        assert "synonyms" in text
        assert "neighboring" in text


def test_exact_token_search_rule_is_in_active_planning_and_next_prompt():
    required_paths = [
        "docs/PLANNING_INDEX.md",
        "docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md",
        "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md",
        "docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md",
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
        "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md",
        "docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md",
        "docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1256_g8_window_1249_1256_closure_gate.md",
    ]

    for path in required_paths:
        text = read_repo(path)
        assert "schema/completion check" in text
        assert "token components" in text


def test_next_phase_prompt_still_validates_after_rule_hardening():
    from tools.validate_phase_prompt import validate

    prompt = (
        ROOT
        / "docs/antigravity_tasks/"
        "antigravity_prompt__phase_1256_g8_window_1249_1256_closure_gate.md"
    )
    assert validate(prompt) == []
