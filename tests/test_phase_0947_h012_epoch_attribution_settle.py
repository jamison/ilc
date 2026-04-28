"""Phase 947 — H-012 ratification evidence tests (30 tests).

Tests CDL-081 §§4.1–4.6 attribution settlement runtime implemented in
Phase 946. All 30 tests must pass for H-012 ratification evidence.

CDL-081 ratified Phase 943. Runtime: Phase 946.
"""

import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    CDL_081_DEPENDENCY,
    CDL_HCON_02_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.types import (
    EPOCH_ATTRIBUTION_BATCH_VERSION,
    REUSE_ATTRIBUTION_RATE,
    EdgeType,
    EpochAttributionBatch,
)


# ---------------------------------------------------------------------------
# Group 1: REUSE attribution — single creator (5 tests)
# ---------------------------------------------------------------------------


def test_g1_reuse_single_creator_payout_amount():
    """§4.1 REUSE: single traversal yields REUSE_ATTRIBUTION_RATE to creator."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_alice", None, 1))
    batch.seal()
    payouts = batch.settle({})
    assert len(payouts) == 1
    agent_id, amount = payouts[0]
    assert agent_id == "creator_alice"
    assert amount == Decimal("0.20")


def test_g1_reuse_payout_type_is_decimal():
    """§4.1 REUSE: returned amount is Decimal, not float."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_bob", None, 2))
    batch.seal()
    payouts = batch.settle({})
    _, amount = payouts[0]
    assert isinstance(amount, Decimal), f"Expected Decimal, got {type(amount)}"


def test_g1_reuse_payout_matches_reuse_attribution_rate():
    """§4.1 REUSE: payout equals REUSE_ATTRIBUTION_RATE constant exactly."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_carol", None, 5))
    batch.seal()
    payouts = batch.settle({})
    assert payouts[0][1] == REUSE_ATTRIBUTION_RATE


def test_g1_reuse_returns_creator_id():
    """§4.1 REUSE: target_creator_id is the payout recipient, not any other agent."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_dave", None, 1))
    batch.seal()
    payouts = batch.settle({})
    assert payouts[0][0] == "creator_dave"


def test_g1_reuse_stake_map_not_accessed():
    """§4.1 REUSE: stake_map content irrelevant for REUSE events — empty map works."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_eve", None, 1))
    batch.seal()
    # Passing completely empty stake_map must not raise
    payouts = batch.settle({})
    assert payouts[0][0] == "creator_eve"


# ---------------------------------------------------------------------------
# Group 2: REUSE attribution — multiple events per epoch (3 tests)
# ---------------------------------------------------------------------------


def test_g2_reuse_two_events_accumulate():
    """§4.1 REUSE: two distinct traversal events each produce one payout."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_a", None, 1))
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_b", None, 1))
    batch.seal()
    payouts = batch.settle({})
    assert len(payouts) == 2
    agents = {p[0] for p in payouts}
    assert "creator_a" in agents
    assert "creator_b" in agents


def test_g2_reuse_same_creator_two_events():
    """§4.1 REUSE: same creator in two separate events each receives one payout.

    visited_set is fresh per event — cross-event deduplication does not apply.
    The same creator may receive in both events.
    """
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_shared", None, 1))
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_shared", None, 2))
    batch.seal()
    payouts = batch.settle({})
    # Two events → two payouts (fresh visited_set per event allows same creator twice)
    assert len(payouts) == 2
    total = sum(p[1] for p in payouts)
    assert total == Decimal("0.40")


def test_g2_reuse_batch_returns_list():
    """§4.1 REUSE: batch with multiple events returns a list (not None or tuple)."""
    batch = EpochAttributionBatch(epoch=1)
    for i in range(3):
        batch.add_event(AttributionEvent(EdgeType.REUSE, f"creator_{i}", None, 1))
    batch.seal()
    result = batch.settle({})
    assert isinstance(result, list)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# Group 3: CO_AUTHORSHIP proportional split (5 tests)
# ---------------------------------------------------------------------------


def test_g3_co_authorship_two_member_equal_split():
    """§4.2 CO_AUTHORSHIP: two equal-stake members split rate 50/50."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    stake_map = {"star_1": {"alice": Decimal("1"), "bob": Decimal("1")}}
    payouts = batch.settle(stake_map)
    total = sum(p[1] for p in payouts)
    assert total == Decimal("0.20")
    amounts = {p[0]: p[1] for p in payouts}
    assert amounts["alice"] == amounts["bob"] == Decimal("0.10")


def test_g3_co_authorship_unequal_stake():
    """§4.2 CO_AUTHORSHIP: proportional split by stake — 3:1 ratio."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    stake_map = {"star_1": {"alice": Decimal("3"), "bob": Decimal("1")}}
    payouts = batch.settle(stake_map)
    amounts = {p[0]: p[1] for p in payouts}
    assert amounts["alice"] == Decimal("0.15")
    assert amounts["bob"] == Decimal("0.05")


def test_g3_co_authorship_three_member_split():
    """§4.2 CO_AUTHORSHIP: three-member star node splits proportionally."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    stake_map = {"star_1": {"a": Decimal("1"), "b": Decimal("1"), "c": Decimal("2")}}
    payouts = batch.settle(stake_map)
    total = sum(p[1] for p in payouts)
    # Total must equal REUSE_ATTRIBUTION_RATE
    assert total == REUSE_ATTRIBUTION_RATE
    amounts = {p[0]: p[1] for p in payouts}
    # a and b each get 1/4, c gets 1/2
    assert amounts["a"] == amounts["b"]
    assert amounts["c"] == amounts["a"] * 2


def test_g3_co_authorship_returns_decimal_amounts():
    """§4.2 CO_AUTHORSHIP: all payout amounts are Decimal (no float leakage)."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    stake_map = {"star_1": {"alice": Decimal("2"), "bob": Decimal("3")}}
    payouts = batch.settle(stake_map)
    for _, amount in payouts:
        assert isinstance(amount, Decimal), f"Float leak in CO_AUTHORSHIP: {type(amount)}"


def test_g3_co_authorship_missing_star_node_is_zero_member():
    """§4.6 Zero-member commons: missing star_node_id in stake_map → no payouts."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_unknown", 1))
    batch.seal()
    payouts = batch.settle({})  # star_unknown not in map → empty inner dict
    assert payouts == []


# ---------------------------------------------------------------------------
# Group 4: CO_AUTHORSHIP zero-member commons (3 tests)
# ---------------------------------------------------------------------------


def test_g4_zero_member_commons_no_payouts():
    """§4.6: Empty member dict → attribution suspended, no ECU payouts."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_empty", 1))
    batch.seal()
    payouts = batch.settle({"star_empty": {}})
    assert payouts == []


def test_g4_zero_member_commons_emits_token():
    """§4.6: Empty member dict → cdl_081_zero_member_commons_transition token emitted."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_empty", 1))
    batch.seal()
    tokens: list[str] = []
    batch.settle({"star_empty": {}}, tokens)
    assert "cdl_081_zero_member_commons_transition" in tokens


def test_g4_zero_member_commons_token_not_emitted_when_no_list():
    """§4.6: emitted_tokens is optional — no crash when not provided."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_empty", 1))
    batch.seal()
    # Must not raise even if emitted_tokens is not passed
    payouts = batch.settle({"star_empty": {}})
    assert payouts == []


# ---------------------------------------------------------------------------
# Group 5: CDL-V1 temporal decay integration (3 tests)
# ---------------------------------------------------------------------------


def test_g5_late_buy_in_lower_stake_gets_less():
    """§4.4 CDL-V1 decay: stake_map values are decay-adjusted by caller.

    When a member has lower (decay-reduced) stake, their proportional share
    is smaller. The settle runtime uses whatever stake values are provided.
    """
    batch = EpochAttributionBatch(epoch=10)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 10))
    batch.seal()
    # alice has full stake; bob has decay-reduced stake (late buy-in)
    stake_map = {"star_1": {"alice": Decimal("1"), "bob": Decimal("0.5")}}
    payouts = batch.settle(stake_map)
    amounts = {p[0]: p[1] for p in payouts}
    # alice should get more than bob
    assert amounts["alice"] > amounts["bob"]


def test_g5_full_stake_equal_to_rate_total():
    """§4.4 CDL-V1 decay: full-stake (no decay) members get exactly REUSE_ATTRIBUTION_RATE total."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    # Both at full stake (no decay applied)
    stake_map = {"star_1": {"alice": Decimal("10"), "bob": Decimal("10")}}
    payouts = batch.settle(stake_map)
    total = sum(p[1] for p in payouts)
    assert total == REUSE_ATTRIBUTION_RATE


def test_g5_stake_map_with_high_precision_decimals():
    """§4.4 CDL-V1 decay: high-precision Decimal stakes work without float conversion."""
    batch = EpochAttributionBatch(epoch=5)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 5))
    batch.seal()
    stake_map = {"star_1": {"alice": Decimal("0.333333"), "bob": Decimal("0.666667")}}
    payouts = batch.settle(stake_map)
    for _, amount in payouts:
        assert isinstance(amount, Decimal)
    # Total must be exactly REUSE_ATTRIBUTION_RATE (Decimal arithmetic — no float loss)
    total = sum(p[1] for p in payouts)
    assert total == REUSE_ATTRIBUTION_RATE


# ---------------------------------------------------------------------------
# Group 6: Ejected stake treasury guard (2 tests)
# ---------------------------------------------------------------------------


def test_g6_refutation_raises_not_implemented():
    """§4.5 Ejected stake: REFUTATION event raises NotImplementedError."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REFUTATION, "", None, 1))
    batch.seal()
    with pytest.raises(NotImplementedError):
        batch.settle({})


def test_g6_refutation_raises_hcon02_dependency_message():
    """§4.5 Ejected stake: NotImplementedError carries CDL_HCON_02_DEPENDENCY token."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REFUTATION, "", None, 1))
    batch.seal()
    with pytest.raises(NotImplementedError) as exc_info:
        batch.settle({})
    assert CDL_HCON_02_DEPENDENCY in str(exc_info.value)


# ---------------------------------------------------------------------------
# Group 7: Decimal precision invariants (4 tests)
# ---------------------------------------------------------------------------


def test_g7_reuse_rate_is_decimal_type():
    """REUSE_ATTRIBUTION_RATE must be Decimal, not float (ILC coding standard)."""
    assert isinstance(REUSE_ATTRIBUTION_RATE, Decimal)
    assert not isinstance(REUSE_ATTRIBUTION_RATE, float)


def test_g7_passive_attribution_rate_is_decimal():
    """M1 fix: PASSIVE_ATTRIBUTION_RATE is now Decimal (was float before Phase 946)."""
    from ilc_core.economics.passive_ecu_attribution_runtime import PASSIVE_ATTRIBUTION_RATE as PAR
    assert isinstance(PAR, Decimal), f"Expected Decimal, got {type(PAR)}"
    assert PAR == Decimal("0.20")


def test_g7_no_float_in_reuse_payouts():
    """All payout amounts from REUSE events are Decimal (no float leakage)."""
    batch = EpochAttributionBatch(epoch=1)
    for i in range(5):
        batch.add_event(AttributionEvent(EdgeType.REUSE, f"creator_{i}", None, 1))
    batch.seal()
    payouts = batch.settle({})
    for _, amount in payouts:
        assert isinstance(amount, Decimal), f"Float leak: {type(amount)}"


def test_g7_no_float_in_co_authorship_payouts():
    """All payout amounts from CO_AUTHORSHIP events are Decimal (no float leakage)."""
    batch = EpochAttributionBatch(epoch=1)
    for i in range(3):
        batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", f"star_{i}", 1))
    batch.seal()
    stake_map = {f"star_{i}": {"agent": Decimal("1")} for i in range(3)}
    payouts = batch.settle(stake_map)
    for _, amount in payouts:
        assert isinstance(amount, Decimal), f"Float leak: {type(amount)}"


# ---------------------------------------------------------------------------
# Group 8: visited_set epoch isolation (3 tests)
# ---------------------------------------------------------------------------


def test_g8_visited_set_fresh_per_event():
    """§4.1 visited_set is fresh per event — same creator can appear in two events."""
    batch = EpochAttributionBatch(epoch=1)
    # Same creator in two separate events must produce two payouts
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_shared", None, 1))
    batch.add_event(AttributionEvent(EdgeType.REUSE, "creator_shared", None, 1))
    batch.seal()
    payouts = batch.settle({})
    assert len(payouts) == 2, (
        "visited_set must be fresh per event; same creator may receive in each event"
    )


def test_g8_mixed_event_types_no_state_bleed():
    """No state bleeds between REUSE and CO_AUTHORSHIP events in the same batch."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "alice", None, 1))
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    stake_map = {"star_1": {"bob": Decimal("1"), "carol": Decimal("1")}}
    payouts = batch.settle(stake_map)
    agents = [p[0] for p in payouts]
    # alice from REUSE, bob and carol from CO_AUTHORSHIP
    assert "alice" in agents
    assert "bob" in agents
    assert "carol" in agents
    assert len(payouts) == 3


def test_g8_ignored_edge_types_produce_no_payouts():
    """§4.3 ATTESTATION, PROVENANCE, EPOCH_BOUNDARY are silently ignored."""
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.ATTESTATION, "agent_x", None, 1))
    batch.add_event(AttributionEvent(EdgeType.PROVENANCE, "agent_y", None, 1))
    batch.add_event(AttributionEvent(EdgeType.EPOCH_BOUNDARY, "agent_z", None, 1))
    batch.seal()
    payouts = batch.settle({})
    assert payouts == [], f"Ignored edge types must produce no payouts, got: {payouts}"


# ---------------------------------------------------------------------------
# Group 9: Version token present (1 test)
# ---------------------------------------------------------------------------


def test_g9_version_token():
    """Runtime version token is correct and present."""
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_946.v0.1"
    assert EPOCH_ATTRIBUTION_BATCH_VERSION == "epoch_attribution_batch.v0.2"
    assert "stub" not in EPOCH_ATTRIBUTION_BATCH_VERSION


# ---------------------------------------------------------------------------
# Group 10: Dependency token present (1 test)
# ---------------------------------------------------------------------------


def test_g10_dependency_token():
    """CDL_081_DEPENDENCY token is correct and present in the runtime module."""
    assert CDL_081_DEPENDENCY == "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"


# ---------------------------------------------------------------------------
# Phantom edit guard (inline assertion — tested in this file)
# ---------------------------------------------------------------------------


def test_phantom_edit_guard_cdl_hcon01_gone():
    """CDL_HCON_01_DEPENDENCY must not appear in ilc_core/types.py (phantom edit guard)."""
    result = subprocess.run(
        ["grep", "-n", "CDL_HCON_01_DEPENDENCY", "ilc_core/types.py"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "", (
        f"CDL_HCON_01_DEPENDENCY still present in ilc_core/types.py:\n{result.stdout}"
    )
