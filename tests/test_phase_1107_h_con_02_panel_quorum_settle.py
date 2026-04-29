"""Phase 1107 — H-CON-02 ratification evidence tests.

Tests CDL-083 panel quorum rules and REFUTATION attribution runtime
implemented in Phases 1105–1106.

CDL-083 ratified Phase 1105. evaluate_ejected_stake_vote(): Phase 1106.
Covers G1–G10 per ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md §5.
"""

import dataclasses
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    CDL_083_DEPENDENCY,
    CDL_HCON_02_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    HCON02_QUORUM_FLOOR,
    HCON02_QUORUM_MINIMUM_VOTERS,
    HCON02_VOTE_THRESHOLD_DENOMINATOR,
    HCON02_VOTE_THRESHOLD_NUMERATOR,
    evaluate_ejected_stake_vote,
    settle_attribution_batch,
)
from ilc_core.types import (
    REUSE_ATTRIBUTION_RATE,
    EdgeType,
    EpochAttributionBatch,
)


def _settle_single_event(event: AttributionEvent) -> list[tuple[str, Decimal]]:
    batch = EpochAttributionBatch(epoch=event.epoch)
    batch.add_event(event)
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


# ---------------------------------------------------------------------------
# G1: Runtime constants (4 tests)
# ---------------------------------------------------------------------------


def test_g1_quorum_floor_is_decimal():
    assert HCON02_QUORUM_FLOOR == Decimal("0.50")
    assert isinstance(HCON02_QUORUM_FLOOR, Decimal)


def test_g1_quorum_minimum_voters_is_int_two():
    assert HCON02_QUORUM_MINIMUM_VOTERS == 2
    assert isinstance(HCON02_QUORUM_MINIMUM_VOTERS, int)


def test_g1_vote_threshold_integer_pair():
    assert HCON02_VOTE_THRESHOLD_NUMERATOR == 2
    assert HCON02_VOTE_THRESHOLD_DENOMINATOR == 3
    assert isinstance(HCON02_VOTE_THRESHOLD_NUMERATOR, int)
    assert isinstance(HCON02_VOTE_THRESHOLD_DENOMINATOR, int)


def test_g1_quorum_floor_not_float():
    assert not isinstance(HCON02_QUORUM_FLOOR, float)
    assert isinstance(HCON02_QUORUM_FLOOR, Decimal)


# ---------------------------------------------------------------------------
# G2: Dependency tokens (2 tests)
# ---------------------------------------------------------------------------


def test_g2_cdl_083_dependency_token():
    assert CDL_083_DEPENDENCY == "cdl_083_h_con_02_ratified_1105.v0.1"


def test_g2_hcon02_historical_marker_retained():
    assert CDL_HCON_02_DEPENDENCY == "h_con_02_cdl_required_before_ejected_stake_treasury_executes"


# ---------------------------------------------------------------------------
# G3: REFUTATION attribution via settle_attribution_batch() (3 tests)
# ---------------------------------------------------------------------------


def test_g3a_refutation_payout_correct_recipient():
    event = AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id="creator_of_refuted_node",
        star_node_id=None,
        epoch=1,
        refuting_agent_id="refuting_agent",
    )
    payouts = _settle_single_event(event)
    assert len(payouts) == 1
    assert payouts[0][0] == "refuting_agent"
    assert payouts[0][1] == REUSE_ATTRIBUTION_RATE
    assert isinstance(payouts[0][1], Decimal)


def test_g3b_refuted_target_creator_not_paid():
    event = AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id="creator_of_refuted_node",
        star_node_id=None,
        epoch=1,
        refuting_agent_id="refuting_agent",
    )
    payouts = _settle_single_event(event)
    payout_recipients = [p[0] for p in payouts]
    assert "creator_of_refuted_node" not in payout_recipients


def test_g3c_missing_refuting_agent_id_raises_value_error():
    bad_event = AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id="someone",
        star_node_id=None,
        epoch=1,
        refuting_agent_id=None,
    )
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(bad_event)
    batch.seal()
    with pytest.raises(ValueError, match="refutation_event_missing_refuting_agent_id"):
        settle_attribution_batch(batch, stake_map={})


# ---------------------------------------------------------------------------
# G4: REFUTATION caller-filter contract (1 test)
# ---------------------------------------------------------------------------


def test_g4_attribution_event_has_no_upheld_field():
    field_names = [f.name for f in dataclasses.fields(AttributionEvent)]
    assert "upheld" not in field_names
    assert "refuting_agent_id" in field_names
    assert field_names == [
        "edge_type",
        "target_creator_id",
        "star_node_id",
        "epoch",
        "refuting_agent_id",
    ]


# ---------------------------------------------------------------------------
# G4b: REFUTATION recipient shape (1 test)
# ---------------------------------------------------------------------------


def test_g4b_refuting_agent_id_is_payout_recipient():
    event = AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id="TARGET_CREATOR",
        star_node_id=None,
        epoch=5,
        refuting_agent_id="REFUTING_AGENT",
    )
    payouts = _settle_single_event(event)
    assert payouts[0][0] == "REFUTING_AGENT"
    assert payouts[0][0] != "TARGET_CREATOR"


# ---------------------------------------------------------------------------
# G5: Version token (1 test)
# ---------------------------------------------------------------------------


def test_g5_version_token_phase_1106():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1106.v0.2"


# ---------------------------------------------------------------------------
# G6: CDL-083 spec state (2 tests)
# ---------------------------------------------------------------------------


def test_g6_cdl_083_spec_file_exists():
    spec = Path("docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md")
    assert spec.exists()


def test_g6_cdl_083_spec_ratified_tokens_present():
    spec = Path("docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md")
    content = spec.read_text()
    assert "**Status:** RATIFIED" in content
    assert "cdl_083_ratified_phase_1105" in content


# ---------------------------------------------------------------------------
# G7: CDL log state (1 test)
# ---------------------------------------------------------------------------


def test_g7_cdl_log_row_is_ratified():
    result = subprocess.run(
        ["grep", "CDL-083", "docs/specs/ilc_constitutional_decision_log_v0.1.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "ratified" in result.stdout.lower()
    assert "ratified_phase: 1105" in result.stdout


# ---------------------------------------------------------------------------
# G8: Quorum floor and 2/3 threshold correctness (6 tests)
# ---------------------------------------------------------------------------


def test_g8a_exact_2_of_3_passes_threshold():
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=2,
        participating_voters=3,
    )
    assert ok
    assert len(payouts) == 2


def test_g8b_exact_4_of_6_passes_threshold():
    ok, _ = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=4,
        participating_voters=6,
    )
    assert ok


def test_g8c_exact_6_of_9_passes_threshold():
    ok, _ = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=6,
        participating_voters=9,
    )
    assert ok


def test_g8d_quorum_floor_failure_one_of_four():
    ok, _ = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("25"), "b": Decimal("25"), "c": Decimal("25"), "d": Decimal("25")},
        approve_votes=1,
        participating_voters=1,
    )
    assert not ok


def test_g8e_hard_minimum_two_voters_blocks_one_voter():
    ok, _ = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=1,
        participating_voters=1,
    )
    assert not ok


def test_g8f_threshold_failure_one_of_three():
    ok, _ = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=1,
        participating_voters=3,
    )
    assert not ok


# ---------------------------------------------------------------------------
# G9: No float leakage (2 tests)
# ---------------------------------------------------------------------------


def test_g9_quorum_floor_constant_no_float_leakage():
    assert isinstance(HCON02_QUORUM_FLOOR, Decimal)
    assert not isinstance(HCON02_QUORUM_FLOOR, float)


def test_g9_ejected_stake_vote_payouts_are_decimal():
    _, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=2,
        participating_voters=2,
    )
    for _, amount in payouts:
        assert isinstance(amount, Decimal)
        assert not isinstance(amount, float)


# ---------------------------------------------------------------------------
# G10: Prelock historical assertion (1 test)
# ---------------------------------------------------------------------------


def test_g10_cdl_083_was_open_at_phase_1103_introducing_commit():
    result = subprocess.run(
        [
            "git",
            "show",
            "da10991f:docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "**Status:** OPEN" in result.stdout


# ---------------------------------------------------------------------------
# G11: Distribution formula (3 tests)
# ---------------------------------------------------------------------------


def test_g11_distribution_50_50_exact():
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("200"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=2,
        participating_voters=2,
    )
    assert ok
    payout_map = dict(payouts)
    assert payout_map["a"] == Decimal("100")
    assert payout_map["b"] == Decimal("100")


def test_g11_distribution_25_75_exact():
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("25"), "b": Decimal("75")},
        approve_votes=2,
        participating_voters=2,
    )
    assert ok
    payout_map = dict(payouts)
    assert payout_map["a"] == Decimal("25")
    assert payout_map["b"] == Decimal("75")


def test_g11_distribution_all_zero_stake_edge_case_returns_empty_payouts():
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {},
        approve_votes=2,
        participating_voters=2,
    )
    assert ok
    assert payouts == []


# ---------------------------------------------------------------------------
# G12: Input validation (3 tests)
# ---------------------------------------------------------------------------


def test_g12_negative_ejected_stake_rejected():
    with pytest.raises(ValueError, match="ejected_stake_must_be_positive_finite_decimal"):
        evaluate_ejected_stake_vote(
            Decimal("-1"),
            {"a": Decimal("50")},
            approve_votes=1,
            participating_voters=1,
        )


def test_g12_approve_votes_must_not_exceed_participating_voters():
    with pytest.raises(ValueError, match="approve_votes_must_not_exceed_participating_voters"):
        evaluate_ejected_stake_vote(
            Decimal("100"),
            {"a": Decimal("50")},
            approve_votes=3,
            participating_voters=2,
        )


def test_g12_non_decimal_member_stake_rejected():
    with pytest.raises(ValueError, match="stake_map_member_stake_must_be_decimal"):
        evaluate_ejected_stake_vote(
            Decimal("100"),
            {"a": 0.5},
            approve_votes=1,
            participating_voters=1,
        )
