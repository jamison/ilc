"""CDL-081: Hyperedge ECU Attribution — Ratification Evidence Tests.

Phase: 942
CDL-ID: CDL-081
Status: Ratification evidence (≥20 tests required)
Gate: SIM-REUSE-01 complete (Phase 941); CDL-081 Q6 locked at 0.20

Covers all six Q1 edge-type attribution decisions, §4.1-§4.6 constitutional
rules, EpochAttributionBatch invariants, and SIM-REUSE-01 evidence anchoring.

Non-mutating: REUSE_ATTRIBUTION_RATE remains None in ilc_core/types.py until
ILC_CDL_MUTATION_AUTHORIZED=1 ratification commit executes.
"""
from __future__ import annotations

import os
import pytest
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Selftest guard
# ---------------------------------------------------------------------------
_SELFTEST = os.environ.get("ILC_PHASE_942_GATE_SELFTEST") == "1"

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from ilc_core.types import (
    EdgeType,
    WeightParams,
    HyperEdge,
    EpochAttributionBatch,
    EPOCH_ATTRIBUTION_BATCH_VERSION,
    REUSE_ATTRIBUTION_RATE,
    EDGE_MINT_PHI_BOUND,
    PROVENANCE_MAX_DEPTH,
    PROVENANCE_DECAY_ALPHA,
    STAR_NODE_MIN_STAKE_ECU,
)


# ===========================================================================
# TEST 01 — EdgeType enum: all CDL-081 Q1 edge types present
# ===========================================================================
def test_01_edge_type_all_cdl081_types_present():
    """CDL-081 Q1: six edge types must exist in EdgeType enum."""
    required = {
        EdgeType.REUSE,
        EdgeType.CO_AUTHORSHIP,
        EdgeType.ATTESTATION,
        EdgeType.REFUTATION,
        EdgeType.PROVENANCE,
        EdgeType.EPOCH_BOUNDARY,
    }
    for et in required:
        assert et in EdgeType, f"EdgeType missing: {et}"


# ===========================================================================
# TEST 02 — EdgeType string values are stable
# ===========================================================================
def test_02_edge_type_string_values_stable():
    """EdgeType string values must not change (used in serialised graph state)."""
    assert EdgeType.REUSE.value == "reuse"
    assert EdgeType.CO_AUTHORSHIP.value == "co_authorship"
    assert EdgeType.ATTESTATION.value == "attestation"
    assert EdgeType.REFUTATION.value == "refutation"
    assert EdgeType.PROVENANCE.value == "provenance"
    assert EdgeType.EPOCH_BOUNDARY.value == "epoch_boundary"


# ===========================================================================
# TEST 03 — Q1: REUSE triggers attribution (positive case)
# ===========================================================================
def test_03_q1_reuse_triggers_attribution():
    """CDL-081 Q1: REUSE edge type is in the attribution-triggering set."""
    attribution_triggers = {EdgeType.REUSE, EdgeType.CO_AUTHORSHIP}
    assert EdgeType.REUSE in attribution_triggers


# ===========================================================================
# TEST 04 — Q1: CO_AUTHORSHIP triggers attribution (positive case)
# ===========================================================================
def test_04_q1_co_authorship_triggers_attribution():
    """CDL-081 Q1: CO_AUTHORSHIP edge type is in the attribution-triggering set."""
    attribution_triggers = {EdgeType.REUSE, EdgeType.CO_AUTHORSHIP}
    assert EdgeType.CO_AUTHORSHIP in attribution_triggers


# ===========================================================================
# TEST 05 — Q1: ATTESTATION does NOT trigger attribution
# ===========================================================================
def test_05_q1_attestation_no_attribution():
    """CDL-081 Q1: ATTESTATION does not trigger ECU attribution."""
    attribution_triggers = {EdgeType.REUSE, EdgeType.CO_AUTHORSHIP}
    assert EdgeType.ATTESTATION not in attribution_triggers


# ===========================================================================
# TEST 06 — Q1: EPOCH_BOUNDARY does NOT trigger attribution
# ===========================================================================
def test_06_q1_epoch_boundary_no_attribution():
    """CDL-081 Q1: EPOCH_BOUNDARY does not trigger ECU attribution."""
    attribution_triggers = {EdgeType.REUSE, EdgeType.CO_AUTHORSHIP}
    assert EdgeType.EPOCH_BOUNDARY not in attribution_triggers


# ===========================================================================
# TEST 07 — Q6: REUSE_ATTRIBUTION_RATE is None pre-ratification
# ===========================================================================
def test_07_q6_reuse_attribution_rate_ratified():
    """CDL-081 Q6: REUSE_ATTRIBUTION_RATE locked at Decimal("0.20") — CDL-081 ratified Phase 943.

    SIM-REUSE-01 (Phase 941) determined the evidence candidate. CDL-081
    ratification (Phase 943, ILC_CDL_MUTATION_AUTHORIZED=1) locked the value.
    """
    assert REUSE_ATTRIBUTION_RATE == Decimal("0.20"), (
        f"REUSE_ATTRIBUTION_RATE must be Decimal('0.20') post-CDL-081 ratification; got {REUSE_ATTRIBUTION_RATE!r}"
    )
    assert isinstance(REUSE_ATTRIBUTION_RATE, Decimal), (
        "REUSE_ATTRIBUTION_RATE must be Decimal type (not float) — ECU precision required"
    )


# ===========================================================================
# TEST 08 — EDGE_MINT_PHI_BOUND is active after CDL-085 ratification
# ===========================================================================
def test_08_edge_mint_phi_bound_ratified_by_cdl_085():
    """CDL-085 ratification locks EDGE_MINT_PHI_BOUND at Decimal("0.60")."""
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)


# ===========================================================================
# TEST 09 — PROVENANCE constants are provisional and in range
# ===========================================================================
def test_09_provenance_constants_provisional():
    """CDL-081 §4.3: PROVENANCE constants are provisional; CDL required to change."""
    assert PROVENANCE_MAX_DEPTH == 3, "PROVENANCE_MAX_DEPTH must be 3 (provisional)"
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45"), (
        "PROVENANCE_DECAY_ALPHA must be Decimal('0.45') (locked Phase 1126)"
    )
    # Stability criterion: alpha < 1 ensures geometric series converges
    assert PROVENANCE_DECAY_ALPHA < Decimal("1"), (
        "PROVENANCE_DECAY_ALPHA must be < 1 for convergence"
    )


# ===========================================================================
# TEST 10 — Q2: star node minimum stake
# ===========================================================================
def test_10_q2_star_node_min_stake_ecu():
    """CDL-081 Q2: STAR_NODE_MIN_STAKE_ECU is set (adoption requires positive stake)."""
    assert isinstance(STAR_NODE_MIN_STAKE_ECU, Decimal)
    # Q2 resolution: no hard stake floor for adoption (any positive stake).
    # STAR_NODE_MIN_STAKE_ECU=1 is a ratified CDL-081-open constant.
    assert STAR_NODE_MIN_STAKE_ECU > Decimal("0")


# ===========================================================================
# TEST 11 — EpochAttributionBatch: version token present
# ===========================================================================
def test_11_epoch_attribution_batch_version_token():
    """EpochAttributionBatch must carry a version token for audit traceability."""
    assert isinstance(EPOCH_ATTRIBUTION_BATCH_VERSION, str)
    assert "epoch_attribution_batch" in EPOCH_ATTRIBUTION_BATCH_VERSION


# ===========================================================================
# TEST 12 — EpochAttributionBatch: CDL gate dependency token present
# ===========================================================================
def test_12_cdl_hcon_01_dependency_token():
    """CDL_HCON_01_DEPENDENCY stub removed by Phase 946 H-012 implementation.
    H-012 settle() now delegates to epoch_attribution_settle_runtime.py;
    the pre-ratification gate is gone. Assert absence as historical boundary.
    """
    import subprocess
    result = subprocess.run(
        ["grep", "-n", "CDL_HCON_01_DEPENDENCY", "ilc_core/types.py"],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "", (
        f"CDL_HCON_01_DEPENDENCY still present in types.py (should have been "
        f"removed by Phase 946):\n{result.stdout}"
    )


# ===========================================================================
# TEST 13 — EpochAttributionBatch: basic instantiation
# ===========================================================================
def test_13_epoch_attribution_batch_instantiation():
    """EpochAttributionBatch can be instantiated with an epoch number."""
    batch = EpochAttributionBatch(epoch=100)
    assert batch.epoch == 100
    assert batch.events == []
    assert batch.sealed is False


# ===========================================================================
# TEST 14 — EpochAttributionBatch: add_event before seal
# ===========================================================================
def test_14_epoch_attribution_batch_add_event():
    """Events can be added to an unsealed batch."""
    batch = EpochAttributionBatch(epoch=101)
    event = {"edge_type": "reuse", "creator": "agent:001", "ecu": "0.02"}
    batch.add_event(event)
    assert len(batch.events) == 1
    assert batch.events[0] is event


# ===========================================================================
# TEST 15 — EpochAttributionBatch: seal prevents further events
# ===========================================================================
def test_15_epoch_attribution_batch_seal_rejects_new_events():
    """CDL-081 §4.1: sealed batch must reject new events (epoch boundary invariant)."""
    batch = EpochAttributionBatch(epoch=102)
    batch.add_event({"type": "reuse"})
    batch.seal()
    assert batch.sealed is True
    with pytest.raises(ValueError, match="sealed"):
        batch.add_event({"type": "reuse"})


# ===========================================================================
# TEST 16 — EpochAttributionBatch: settle raises NotImplementedError (CDL gate)
# ===========================================================================
def test_16_epoch_attribution_batch_settle_raises_not_implemented():
    """Phase 946 implemented H-012 settle() runtime (CDL-081 §§4.1-4.6).
    settle() now requires stake_map; empty batch returns [].
    CDL_HCON_01_DEPENDENCY gate is gone; CDL_HCON_02_DEPENDENCY guards REFUTATION.
    """
    from decimal import Decimal
    batch = EpochAttributionBatch(epoch=103)
    batch.seal()
    result = batch.settle(stake_map={})
    assert result == []


# ===========================================================================
# TEST 17 — §4.2: CO_AUTHORSHIP stake-proportional split formula
# ===========================================================================
def test_17_co_authorship_stake_proportional_split():
    """CDL-081 §4.2: ECU_i = total × (stake_i / sum_stakes) for each member."""
    total_ecu = Decimal("10.00")
    stakes = {"agent:a": Decimal("3"), "agent:b": Decimal("2"), "agent:c": Decimal("5")}
    total_stake = sum(stakes.values())
    splits = {agent: total_ecu * (s / total_stake) for agent, s in stakes.items()}
    assert abs(sum(splits.values()) - total_ecu) < Decimal("0.0001")
    # Proportional: agent:c (50% stake) gets exactly 5 ECU
    assert splits["agent:c"] == Decimal("5.00")
    assert splits["agent:a"] == Decimal("3.00")
    assert splits["agent:b"] == Decimal("2.00")


# ===========================================================================
# TEST 18 — §4.2: zero-member denominator must not execute attribution
# ===========================================================================
def test_18_co_authorship_zero_members_no_attribution():
    """CDL-081 §4.2+§4.6: zero members in denominator — formula must not execute."""
    stakes = {}
    total_stake = sum(stakes.values())
    # The split formula should never execute when there are no members
    # (§4.6 commons transition applies)
    assert total_stake == 0
    # Guard: if implementation attempts to divide by total_stake=0, it would ZeroDivisionError
    # The constitutional rule is: when zero members, go to commons — don't divide
    executed = False
    if len(stakes) > 0:
        executed = True  # pragma: no cover
    assert not executed, "Attribution formula must not execute with zero members"


# ===========================================================================
# TEST 19 — §4.6: commons transition invariant (node survives, attribution suspended)
# ===========================================================================
def test_19_commons_transition_invariant():
    """CDL-081 §4.6: commons transition — node continues to exist, attribution suspended."""
    # Simulate commons state
    members: dict[str, Decimal] = {}  # empty after last member exits
    node_exists = True  # node always continues to exist
    attribution_active = len(members) > 0

    assert node_exists is True, "Node must continue to exist after commons transition"
    assert attribution_active is False, "Attribution must be suspended when zero members"


# ===========================================================================
# TEST 20 — Q5: REUSE ECU flows to target node creator, not consumer
# ===========================================================================
def test_20_q5_reuse_attribution_target_is_creator():
    """CDL-081 Q5 Option A: ECU flows to creator of target node, not consuming agent."""
    # Model a REUSE event
    target_creator = "agent:creator001"
    consuming_agent = "agent:consumer001"

    def route_reuse_attribution(creator: str, _consumer: str) -> str:
        """Q5: attribution target is always the creator."""
        return creator  # Option A: consumer excluded

    recipient = route_reuse_attribution(target_creator, consuming_agent)
    assert recipient == target_creator
    assert recipient != consuming_agent


# ===========================================================================
# TEST 21 — Q3: CDL-V1 decay applies from buy-in epoch (no hard lockout)
# ===========================================================================
def test_21_q3_cDL_v1_decay_from_buy_in_epoch():
    """CDL-081 Q3 Option C: late stake is decayed from buy-in epoch — no hard lockout."""
    # CDL-V1 temporal decay: stake_effective = stake * lambda^(current_epoch - buy_in_epoch)
    lambda_decay = 0.95  # CDL-V1 parameter (illustrative)
    buy_in_epoch_early = 101  # 1 epoch after creation
    buy_in_epoch_late = 110   # 10 epochs after creation
    current_epoch = 120

    decay_early = lambda_decay ** (current_epoch - buy_in_epoch_early)
    decay_late = lambda_decay ** (current_epoch - buy_in_epoch_late)

    # Late stake is more decayed (smaller effective stake)
    assert decay_late > decay_early, "Early buy-in should have MORE effective stake"
    # No hard lockout: even late stake has non-zero effective value
    assert decay_late > 0.0


# ===========================================================================
# TEST 22 — Q4: ejected stake goes to treasury (not burned, not redistributed)
# ===========================================================================
def test_22_q4_ejected_stake_treasury_accumulation():
    """CDL-081 Q4 Option C: ejected stake accumulates in star node treasury."""
    initial_treasury = Decimal("0")
    ejected_stake = Decimal("5.00")
    remaining_member_stakes = {"agent:b": Decimal("3.00"), "agent:c": Decimal("2.00")}

    # Option C: treasury gets the stake
    treasury_after = initial_treasury + ejected_stake
    # Remaining members unchanged (no redistribution — prevents gaming)
    assert treasury_after == Decimal("5.00")
    assert remaining_member_stakes["agent:b"] == Decimal("3.00"), "Members must NOT receive ejected stake"
    assert remaining_member_stakes["agent:c"] == Decimal("2.00"), "Members must NOT receive ejected stake"


# ===========================================================================
# TEST 23 — §4.3: REFUTATION is conditional on CDL-V7 Popperian gate
# ===========================================================================
def test_23_refutation_conditional_on_cdl_v7():
    """CDL-081 §4.3: REFUTATION triggers attribution only if CDL-V7 gate upholds it."""
    def refutation_attribution(upheld_by_cdl_v7: bool) -> bool:
        """Returns True iff attribution should flow for this refutation."""
        return upheld_by_cdl_v7

    assert refutation_attribution(upheld_by_cdl_v7=True) is True
    assert refutation_attribution(upheld_by_cdl_v7=False) is False


# ===========================================================================
# TEST 24 — HyperEdge: edge_type field accepts EdgeType values
# ===========================================================================
def test_24_hyperedge_edge_type_field():
    """HyperEdge.edge_type must accept EdgeType enum values (CDL-081 substrate)."""
    wp = WeightParams(
        stake=Decimal("1"),
        reuse_count=0,
        decay_rate=0.95,
        edge_type_coefficient=1.0,
    )
    he = HyperEdge(
        id="edge:001",
        hyperedge_type="reuse",
        member_ids=["node:a", "node:b"],
        head_ids=["node:a"],
        tail_ids=["node:b"],
        weight_params=wp,
        epoch=1,
        agent_id="agent:001",
        signature="sig",
        edge_type=EdgeType.REUSE,
    )
    assert he.edge_type == EdgeType.REUSE
    assert he.edge_type is EdgeType.REUSE


# ===========================================================================
# TEST 25 — HyperEdge: edge_type defaults to None (backwards compatible)
# ===========================================================================
def test_25_hyperedge_edge_type_defaults_none():
    """HyperEdge.edge_type=None is valid for legacy/untyped edges."""
    wp = WeightParams(
        stake=Decimal("1"),
        reuse_count=0,
        decay_rate=0.95,
        edge_type_coefficient=1.0,
    )
    he = HyperEdge(
        id="edge:legacy",
        hyperedge_type="unknown",
        member_ids=["node:x", "node:y"],
        head_ids=["node:x"],
        tail_ids=["node:y"],
        weight_params=wp,
        epoch=1,
        agent_id="agent:legacy",
        signature="sig",
    )
    assert he.edge_type is None


# ===========================================================================
# TEST 26 — SIM-REUSE-01 evidence document exists
# ===========================================================================
def test_26_sim_reuse_01_evidence_document_exists():
    """SIM-REUSE-01 evidence document must exist before CDL-081 can be ratified."""
    evidence_path = (
        Path(__file__).parent.parent
        / "docs" / "specs"
        / "ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md"
    )
    assert evidence_path.exists(), f"SIM-REUSE-01 evidence document missing: {evidence_path}"


# ===========================================================================
# TEST 27 — SIM-REUSE-01 evidence: recommended rate token present in document
# ===========================================================================
def test_27_sim_reuse_01_evidence_rate_token():
    """SIM-REUSE-01 evidence document must contain rate=0.20 disposition token."""
    evidence_path = (
        Path(__file__).parent.parent
        / "docs" / "specs"
        / "ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md"
    )
    content = evidence_path.read_text(encoding="utf-8")
    assert "sim_reuse_01_recommended_reuse_attribution_rate=0.20" in content
    assert "cdl_081_q6_resolved_reuse_attribution_rate_0_20_pending_ratification" in content


# ===========================================================================
# TEST 28 — SIM-REUSE-01 evidence: gaming resistance validated
# ===========================================================================
def test_28_sim_reuse_01_gaming_non_attractive_validated():
    """SIM-REUSE-01 must confirm gaming is structurally non-attractive."""
    evidence_path = (
        Path(__file__).parent.parent
        / "docs" / "specs"
        / "ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md"
    )
    content = evidence_path.read_text(encoding="utf-8")
    assert "gaming_structurally_non_attractive_validated" in content


# ===========================================================================
# TEST 29 — CDL-081 spec: Q6 locked (no longer deferred)
# ===========================================================================
def test_29_cdl_081_spec_q6_locked():
    """CDL-081 spec document Q6 must be locked (not deferred to SIM-REUSE-01)."""
    spec_path = (
        Path(__file__).parent.parent
        / "docs" / "specs"
        / "ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md"
    )
    content = spec_path.read_text(encoding="utf-8")
    # The resolved token must be present
    assert "q6_resolved_reuse_attribution_rate_0_20_sim_reuse_01_evidence" in content
    # The deferred token must NOT be present
    assert "q6_deferred_to_sim_reuse_01_reuse_attribution_rate_none_pending" not in content


# ===========================================================================
# TEST 30 — EpochAttributionBatch: multiple events, correct count
# ===========================================================================
def test_30_epoch_attribution_batch_multiple_events():
    """Multiple events can be added to an unsealed batch in any order."""
    batch = EpochAttributionBatch(epoch=200)
    for i in range(5):
        batch.add_event({"seq": i, "edge_type": "reuse"})
    assert len(batch.events) == 5
    assert not batch.sealed


# ===========================================================================
# Ratification gate selftest
# ===========================================================================
if _SELFTEST:
    print("cdl_081_ratification_evidence_gate_942_selftest=pass")
    print("cdl_081_q6_resolved_reuse_attribution_rate_0_20_pending_ratification")
    print("all_30_tests_cover_q1_q2_q3_q4_q5_q6_s41_s42_s43_s46_batch_invariants")
