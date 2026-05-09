from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1263_werner_flow_governor_cdl_decision_walkthrough.md"
)
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_1262_SPEC_PATH = Path(
    "docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md"
)
FORWARD_PLAN_PATH = Path(
    "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md"
)


REQUIRED_TOKENS = (
    "werner_flow_governor_cdl_opening_prelock_decision_phase_1263.v0.1",
    "werner_flow_governor_cdl_not_opened_without_evidence_phase_1263",
    "direct_werner_ecu_creation_rejected_phase_1263",
    "phase_1263_sensitive_cdl_gate_complete",
)

CARRY_FORWARD_TOKENS = (
    "werner_default_topology_pressure_profile_required_before_runtime_cdl",
    "beta_decomposition_required_before_policy_use",
    "flow_governor_spectral_trust_threshold_required_before_policy_use",
    "flow_governor_cdl_required_before_runtime_policy_deployment",
    "transport_principal_identity_required_before_public_p2p",
    "werner_productive_credit_authorization_cdl_required",
    "ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation",
    "heat_signal_must_not_directly_mint_ecu",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1263_decision_packet_records_no_open_no_prelock_verdict() -> None:
    text = _read(SPEC_PATH)

    for token in REQUIRED_TOKENS:
        assert token in text

    assert "werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock" in text
    assert "does not open or prelock a Werner flow-governor CDL" in text
    assert "not a rejection of the Werner lane" in text


def test_phase_1263_decision_reuses_current_evidence_without_overclaiming() -> None:
    spec = _read(SPEC_PATH)
    phase_1262 = _read(PHASE_1262_SPEC_PATH)
    forward_plan = _read(FORWARD_PLAN_PATH)

    assert (
        "werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup"
        in spec
    )
    assert (
        "werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup"
        in phase_1262
    )
    assert "heat must not directly create ECU" in forward_plan
    assert "Before any heat/topology signal can become a policy input" in forward_plan
    assert "beta_decomposition_required_before_policy_use" in spec
    assert "flow_governor_spectral_trust_threshold_required_before_policy_use" in spec


def test_phase_1263_closing_conditions_keep_policy_non_economic() -> None:
    text = _read(SPEC_PATH)

    for token in CARRY_FORWARD_TOKENS:
        assert token in text

    assert "Allowed flow-control keywords:" in text
    for term in (
        "routing reputation",
        "routing weight",
        "admission budget",
        "cache priority",
        "mirror priority",
    ):
        assert term in text
    assert "direct ECU minting from heat" in text
    assert "ILC settlement from heat" in text
    assert "per-hop ECU micropayments for fetch or relay" in text
    assert "consensus-epoch settled, not wallet-mutated or heat-mutated" in text


def test_phase_1263_cdl_register_is_referenced_but_not_mutated_in_decision() -> None:
    spec = _read(SPEC_PATH)
    register = _read(CDL_REGISTER_PATH)

    assert "| CDL-085 |" in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "ratified_phase: 1278 Fix1" in register
    assert "No new CDL row is added" in spec
    assert "CDL-087 remains open" in spec
    assert "CDL-088 remains unopened" in spec
    assert "direct_werner_ecu_creation_rejected_phase_1263" not in register


def test_phase_1263_status_planning_roadmap_and_walkthrough_are_backfilled() -> None:
    planning = _read(PLANNING_INDEX_PATH)
    status = _read(STATUS_PATH)
    roadmap = _read(ROADMAP_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (planning, status, roadmap, walkthrough):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Phase 1264" in planning
    assert "Phase 1264" in status
    assert "graph_delta=load_bearing_spec_added:docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md -> planning/werner" in status
    assert "CDL register diff disposition" in walkthrough
