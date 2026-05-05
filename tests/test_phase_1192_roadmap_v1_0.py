from pathlib import Path


ROADMAP = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
GUIDANCE = Path("docs/specs/ilc_window_1191_1199_candidate_phase_grouping_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1192_roadmap_v1_0_rc2_status_walkthrough.md")


def test_roadmap_v1_0_exists_and_supersedes_v0_9() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "**Version:** v1.0" in content
    assert "ilc_launch_roadmap_three_machines_seven_agents_v0.9.md" in content
    assert "launch_roadmap_v1_0_published_phase_1192" in content


def test_roadmap_records_cdl_085_ratified_runtime_frontier() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content
    assert "epoch_attribution_settle_runtime_1185.v0.6" in content


def test_roadmap_records_three_slice_framework_complete() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "sim_spectral_05_runtime_binding_slice_pass" in content
    assert "sim_spectral_05_economic_flow_slice_pass" in content
    assert "sim_spectral_05_gossip_slice_pass" in content
    assert "sim_spectral_05_three_slice_observer_framework_complete" in content


def test_roadmap_routes_packaging_blocker_to_fresh_cdl() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "likely CDL-086" in content
    assert "CDL-001 is ratified signer-lineage canon" in content
    assert "CDL-001 genesis_blocker / packaging track" not in content


def test_roadmap_records_phase_1192_window_policy_defaults() -> None:
    content = ROADMAP.read_text(encoding="utf-8")
    assert "Not issued as of Phase 1192" in content
    assert "Scope-first" in content
    assert "firm-if-reached" in content


def test_planning_index_points_to_roadmap_v1_0() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "ilc_launch_roadmap_three_machines_seven_agents_v1.0.md" in content
    assert "Window 1191-1199 is IN PROGRESS through Phase 1192" in content


def test_guidance_augmented_with_open_decision_defaults() -> None:
    content = GUIDANCE.read_text(encoding="utf-8")
    assert "Phase 1192 default decisions" in content
    assert "Phase 1197 should be treated as firm-if-reached" in content


def test_walkthrough_marked_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "launch_roadmap_v1_0_published_phase_1192" in content
