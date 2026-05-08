from pathlib import Path


ROADMAP_V1_1 = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
ROADMAP_V1_0 = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_roadmap_v1_1_exists_and_is_controlling() -> None:
    text = _read(ROADMAP_V1_1)
    assert "**Version:** v1.1" in text
    assert "roadmap_v1_1_controlling_public_rc_roadmap_phase_1242" in text
    assert "Supersedes" in text


def test_roadmap_v1_0_has_supersession_tombstone() -> None:
    text = _read(ROADMAP_V1_0)
    assert "**SUPERSEDED:** Roadmap v1.0 is superseded" in text
    assert "ilc_launch_roadmap_three_machines_seven_agents_v1.1.md" in text


def test_current_canon_corrections_are_recorded() -> None:
    text = _read(ROADMAP_V1_1)
    assert "cdl_086_ratified_phase_1220" in text
    assert "tier3_runtime_linkage_runtime_1201.v0.1" in text
    assert "persistent_fetch_rate_limiter_runtime_1202.v0.1" in text
    assert "persistent_rate_limiter_transport_wiring_committed_phase_1212" in text


def test_public_rc_branch_decision_is_recorded() -> None:
    text = _read(ROADMAP_V1_1)
    assert "public_rc_default_path=openclaw_skill_first_public_claimability_no_public_p2p_claim" in text
    assert "openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim" in text
    assert "public_claimability_required_for_final_public_rc_profile" in text
    assert "gap_14_package_modularity_executes_before_gap_10_public_p2p" in text


def test_public_rc_blocker_classes_are_defined() -> None:
    text = _read(ROADMAP_V1_1)
    for blocker in (
        "Public repository publication",
        "Public RC claim",
        "Public P2P exposure",
        "Public sidecar/projection serving",
        "Public economic claimability",
        "OpenClaw/NemoClaw local skill preview",
        "OpenClaw/NemoClaw claimable public RC",
    ):
        assert blocker in text


def test_gap14_and_gap10_are_sequenced_correctly() -> None:
    text = _read(ROADMAP_V1_1)
    assert "Gap 14 - OpenClaw/NemoClaw Package Modularity" in text
    assert "Gap 10 - TransportPrincipal Identity Layer" in text
    assert "gap_14_package_modularity_first_slice_before_gap_10_transport_principal" in text
    assert "transport_principal_identity_required_before_public_p2p" in text


def test_atlas_g_public_rc_graph_gate_is_carried() -> None:
    text = _read(ROADMAP_V1_1)
    assert "Gap 15 - Atlas Graph Reachability" in text
    assert "atlas_g_001_graph_delta_schema_required" in text
    assert "atlas_g_006_public_rc_graph_reachability_gate_required" in text
    assert "public_rc_release_artifact_must_include_profile_graph_manifest" in text


def test_cdl_087_and_public_claimability_remain_unclaimed() -> None:
    text = _read(ROADMAP_V1_1)
    assert "CDL-087 | OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "CDL-087 ratified" in text
    assert "public claimability implemented" in text
    assert "public P2P exposure authorized" in text


def test_planning_index_points_to_v1_1_as_current() -> None:
    text = _read(PLANNING_INDEX)
    assert "Launch Roadmap v1.1" in text
    assert "ilc_launch_roadmap_three_machines_seven_agents_v1.1.md" in text
