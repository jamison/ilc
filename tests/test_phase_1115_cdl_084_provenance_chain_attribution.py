"""Phase 1115 — CDL-084 PROVENANCE chain attribution evidence tests.

Tests CDL-084 PROVENANCE settlement runtime implemented in Phase 1114.

CDL-084 ratified Phase 1113. PROVENANCE settlement path activated Phase 1114.
Covers G1–G14 per
ilc_cdl_084_provenance_chain_attribution_ratification_evidence_1112_v0.1.md §4.
"""

import dataclasses
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    CDL_084_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.types import (
    CDL_084_TYPES_DEPENDENCY,
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)


def _settle_event(event: AttributionEvent) -> list[tuple[str, Decimal]]:
    batch = EpochAttributionBatch(epoch=event.epoch)
    batch.add_event(event)
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


def _provenance_event(
    chain: tuple[tuple[str, str], ...] | None,
    *,
    epoch: int = 1,
) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id="unused_target_creator",
        star_node_id=None,
        epoch=epoch,
        provenance_chain=chain,
    )


# ---------------------------------------------------------------------------
# G1: Runtime constants (4 tests)
# ---------------------------------------------------------------------------


def test_g1_provenance_max_depth_is_three_int():
    assert PROVENANCE_MAX_DEPTH == 3
    assert isinstance(PROVENANCE_MAX_DEPTH, int)


def test_g1_provenance_decay_alpha_is_decimal_half():
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)


def test_g1_provenance_decay_alpha_is_not_float():
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_g1_reuse_attribution_rate_is_decimal_point_two_zero():
    assert REUSE_ATTRIBUTION_RATE == Decimal("0.20")
    assert isinstance(REUSE_ATTRIBUTION_RATE, Decimal)


# ---------------------------------------------------------------------------
# G2: Dependency tokens (3 tests)
# ---------------------------------------------------------------------------


def test_g2_runtime_dependency_token():
    assert CDL_084_DEPENDENCY == "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"


def test_g2_types_dependency_token():
    assert (
        CDL_084_TYPES_DEPENDENCY
        == "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
    )


def test_g2_runtime_version_token():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1114.v0.3"


# ---------------------------------------------------------------------------
# G3: AttributionEvent shape (2 tests)
# ---------------------------------------------------------------------------


def test_g3_attribution_event_has_provenance_chain_field():
    field_names = [f.name for f in dataclasses.fields(AttributionEvent)]
    assert "provenance_chain" in field_names


def test_g3_attribution_event_field_order_matches_ratified_shape():
    field_names = [f.name for f in dataclasses.fields(AttributionEvent)]
    assert field_names == [
        "edge_type",
        "target_creator_id",
        "star_node_id",
        "epoch",
        "refuting_agent_id",
        "provenance_chain",
    ]


# ---------------------------------------------------------------------------
# G4: Q10 missing/empty validation (2 tests)
# ---------------------------------------------------------------------------


def test_g4_missing_provenance_chain_raises_stable_error():
    event = _provenance_event(None)
    with pytest.raises(ValueError, match="provenance_event_missing_chain"):
        _settle_event(event)


def test_g4_empty_provenance_chain_raises_stable_error():
    event = _provenance_event(())
    with pytest.raises(ValueError, match="provenance_event_empty_chain"):
        _settle_event(event)


# ---------------------------------------------------------------------------
# G5: Q7 duplicate node ID validation (1 test)
# ---------------------------------------------------------------------------


def test_g5_duplicate_node_id_raises_stable_error():
    event = _provenance_event((
        ("node_1", "creator_A"),
        ("node_1", "creator_B"),
    ))
    with pytest.raises(ValueError, match="provenance_chain_contains_duplicate_node_id"):
        _settle_event(event)


# ---------------------------------------------------------------------------
# G6: Single-hop payout (3 tests)
# ---------------------------------------------------------------------------


def test_g6_single_hop_payout_amount_uses_alpha_power_one():
    payouts = _settle_event(_provenance_event((("node_1", "creator_A"),)))
    expected = REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA
    assert payouts == [("creator_A", expected)]


def test_g6_single_hop_payout_amount_is_decimal():
    payouts = _settle_event(_provenance_event((("node_1", "creator_A"),)))
    assert isinstance(payouts[0][1], Decimal)


def test_g6_single_hop_pays_creator_from_chain_payload():
    payouts = _settle_event(_provenance_event((("node_1", "creator_A"),)))
    assert payouts[0][0] == "creator_A"


# ---------------------------------------------------------------------------
# G7: Multi-hop payout (3 tests)
# ---------------------------------------------------------------------------


def test_g7_three_hop_payouts_use_alpha_powers_one_two_three():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
    )))
    assert payouts == [
        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
        ("creator_C", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 3)),
    ]


def test_g7_over_depth_chain_truncates_at_max_depth():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
        ("node_4", "creator_D"),
    )))
    assert len(payouts) == PROVENANCE_MAX_DEPTH
    assert [agent_id for agent_id, _ in payouts] == ["creator_A", "creator_B", "creator_C"]


def test_g7_multi_hop_payout_amounts_are_decimal():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
    )))
    assert all(isinstance(amount, Decimal) for _, amount in payouts)


# ---------------------------------------------------------------------------
# G8: Duplicate creator handling (2 tests)
# ---------------------------------------------------------------------------


def test_g8_duplicate_creator_nearest_hop_wins():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_A"),
    )))
    assert payouts == [
        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
    ]
    assert [agent_id for agent_id, _ in payouts].count("creator_A") == 1


def test_g8_distinct_creators_are_paid_independently():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
    )))
    assert [agent_id for agent_id, _ in payouts] == ["creator_A", "creator_B", "creator_C"]


# ---------------------------------------------------------------------------
# G9: Caller-only contract (1 test)
# ---------------------------------------------------------------------------


def test_g9_provenance_event_has_no_upheld_field():
    field_names = [f.name for f in dataclasses.fields(AttributionEvent)]
    assert "upheld" not in field_names


# ---------------------------------------------------------------------------
# G10: CDL-084 spec and log state (2 tests)
# ---------------------------------------------------------------------------


def test_g10_cdl_084_spec_is_ratified():
    content = Path(
        "docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md"
    ).read_text()
    assert "**Status:** RATIFIED" in content


def test_g10_cdl_084_log_row_has_ratified_phase_1113():
    content = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md").read_text()
    assert "CDL-084" in content
    assert "ratified_phase: 1113" in content


# ---------------------------------------------------------------------------
# G11: Historical prelock assertion (1 test)
# ---------------------------------------------------------------------------


def test_g11_phase_1111_introducing_commit_was_open():
    result = subprocess.run(
        [
            "git",
            "show",
            "2066f75d:docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "**Status:** OPEN" in result.stdout


# ---------------------------------------------------------------------------
# G12: No float leakage (2 tests)
# ---------------------------------------------------------------------------


def test_g12_alpha_is_decimal_not_float():
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_g12_settlement_payout_is_decimal_not_float():
    payouts = _settle_event(_provenance_event((("node_1", "creator_A"),)))
    assert isinstance(payouts[0][1], Decimal)
    assert not isinstance(payouts[0][1], float)


# ---------------------------------------------------------------------------
# G13: Distribution and truncation edge cases (3 tests)
# ---------------------------------------------------------------------------


def test_g13_chain_length_exactly_three_produces_three_payouts():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
    )))
    assert len(payouts) == 3


def test_g13_chain_length_four_produces_three_payouts():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
        ("node_4", "creator_D"),
    )))
    assert len(payouts) == 3


def test_g13_chain_length_one_produces_one_payout():
    payouts = _settle_event(_provenance_event((("node_1", "creator_A"),)))
    assert len(payouts) == 1


# ---------------------------------------------------------------------------
# G14: Mandatory Option B — mixed batch and tuple shape (2 tests)
# ---------------------------------------------------------------------------


def test_g14_mixed_reuse_and_provenance_batch_computes_both_payouts():
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.REUSE, "reuse_creator", None, 1))
    batch.add_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
    )))
    batch.seal()
    payouts = settle_attribution_batch(batch, stake_map={})
    assert payouts == [
        ("reuse_creator", REUSE_ATTRIBUTION_RATE),
        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
    ]


def test_g14_max_depth_batch_returns_str_decimal_tuples():
    payouts = _settle_event(_provenance_event((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
    )))
    assert len(payouts) == 3
    assert all(isinstance(agent_id, str) for agent_id, _ in payouts)
    assert all(isinstance(amount, Decimal) for _, amount in payouts)

