from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    CDL_083_DEPENDENCY,
    CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN,
    EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_NOT_IMPLEMENTED_CLOSED_PHASE_1350_TOKEN,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    HCON02_QUORUM_FLOOR,
    HCON02_QUORUM_MINIMUM_VOTERS,
    HCON02_VOTE_THRESHOLD_DENOMINATOR,
    HCON02_VOTE_THRESHOLD_NUMERATOR,
    H_CON_02_QUORUM_GUARD_PHASE_1350_TOKEN,
    PRODUCTION_EJECTED_STAKE_DISTRIBUTION_ACTIVATION_TOKEN,
    build_ejected_stake_treasury_distribution_quote,
    evaluate_ejected_stake_vote,
    require_h_con_02_quorum_guard,
    require_production_ejected_stake_distribution_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/economics/epoch_attribution_settle_runtime.py"
TYPES = ROOT / "ilc_core/types.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1350_g8_cdl_083_ejected_stake_treasury_distribution.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1350_cdl_083_ejected_stake_treasury_distribution_walkthrough.md"
)
CDL_083_EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md"
)
CDL_083_SPEC = (
    ROOT / "docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md"
)
SCOPING = ROOT / "docs/specs/ilc_issuance_stack_scoping_window_1343_1368_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1350_constants_bind_cdl_083_and_default_off_state() -> None:
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == (
        "epoch_attribution_settle_runtime_1210.v0.7"
    )
    assert CDL_083_DEPENDENCY == "cdl_083_h_con_02_ratified_1105.v0.1"
    assert CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN == (
        "cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1"
    )
    assert H_CON_02_QUORUM_GUARD_PHASE_1350_TOKEN == "h_con_02_quorum_guard_phase_1350"
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_NOT_IMPLEMENTED_CLOSED_PHASE_1350_TOKEN == (
        "epoch_attribution_settle_runtime_not_implemented_closed_phase_1350"
    )
    assert EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN == (
        "ejected_stake_distribution_not_activated_phase_1350"
    )
    assert PRODUCTION_EJECTED_STAKE_DISTRIBUTION_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert HCON02_QUORUM_FLOOR == Decimal("0.50")
    assert HCON02_QUORUM_MINIMUM_VOTERS == 2
    assert HCON02_VOTE_THRESHOLD_NUMERATOR == 2
    assert HCON02_VOTE_THRESHOLD_DENOMINATOR == 3


def test_ejected_stake_distribution_quote_routes_after_h_con_02_guard() -> None:
    quote = build_ejected_stake_treasury_distribution_quote(
        distribution_epoch=1350,
        ejected_stake_ilc="100",
        remaining_member_stakes={"agent-a": "1", "agent-b": "3"},
        approve_votes=2,
        participating_voters=2,
    )

    assert quote.distribution_epoch == 1350
    assert quote.ejected_stake_ilc == Decimal("100.000000000")
    assert quote.remaining_member_stake_total_ilc == Decimal("4")
    assert quote.remaining_member_count == 2
    assert quote.participating_voters == 2
    assert quote.approve_votes == 2
    assert quote.quorum_floor == Decimal("0.50")
    assert quote.quorum_minimum_voters == 2
    assert quote.vote_threshold_numerator == 2
    assert quote.vote_threshold_denominator == 3
    assert quote.payouts == (
        ("agent-a", Decimal("25.000000000")),
        ("agent-b", Decimal("75.000000000")),
    )
    assert quote.production_ejected_stake_distribution_activated is False
    assert quote.decision_token == EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN


def test_ejected_stake_distribution_quote_quantizes_down_and_preserves_total() -> None:
    quote = build_ejected_stake_treasury_distribution_quote(
        distribution_epoch=0,
        ejected_stake_ilc="1.0000000009",
        remaining_member_stakes={"agent-a": "1", "agent-b": "1", "agent-c": "1"},
        approve_votes=3,
        participating_voters=3,
    )

    assert quote.ejected_stake_ilc == Decimal("1.000000000")
    assert quote.payouts == (
        ("agent-a", Decimal("0.333333333")),
        ("agent-b", Decimal("0.333333333")),
        ("agent-c", Decimal("0.333333334")),
    )
    assert sum((amount for _, amount in quote.payouts), Decimal("0")) == Decimal(
        "1.000000000"
    )


def test_h_con_02_guard_fails_closed_before_distribution() -> None:
    with pytest.raises(
        ValueError,
        match="h_con_02_quorum_guard_minimum_voters_not_met_phase_1350",
    ):
        require_h_con_02_quorum_guard(
            {"a": Decimal("1"), "b": Decimal("1")},
            approve_votes=1,
            participating_voters=1,
        )
    with pytest.raises(ValueError, match="h_con_02_quorum_guard_floor_not_met_phase_1350"):
        require_h_con_02_quorum_guard(
            {letter: Decimal("1") for letter in "abcde"},
            approve_votes=2,
            participating_voters=2,
        )
    with pytest.raises(
        ValueError,
        match="h_con_02_quorum_guard_threshold_not_met_phase_1350",
    ):
        require_h_con_02_quorum_guard(
            {"a": Decimal("1"), "b": Decimal("1"), "c": Decimal("1")},
            approve_votes=1,
            participating_voters=3,
        )


def test_production_ejected_stake_distribution_guard_remains_closed() -> None:
    with pytest.raises(ValueError, match=EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN):
        require_production_ejected_stake_distribution_activation(None)
    with pytest.raises(
        ValueError,
        match="production_ejected_stake_distribution_activation_not_implemented_phase_1350",
    ):
        require_production_ejected_stake_distribution_activation(
            PRODUCTION_EJECTED_STAKE_DISTRIBUTION_ACTIVATION_TOKEN
        )


def test_exact_numeric_and_vote_guards_reject_invalid_inputs() -> None:
    with pytest.raises(
        ValueError,
        match="ejected_stake_distribution_epoch_must_be_non_negative_integer",
    ):
        build_ejected_stake_treasury_distribution_quote(True, "1", {"a": "1"}, 1, 1)
    with pytest.raises(ValueError, match="ejected_stake_ilc_must_be_exact_decimal"):
        build_ejected_stake_treasury_distribution_quote(0, 0.1, {"a": "1"}, 1, 1)
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        build_ejected_stake_treasury_distribution_quote(
            0,
            Decimal("NaN"),
            {"a": "1", "b": "1"},
            2,
            2,
        )
    with pytest.raises(ValueError, match="ejected_stake_ilc_must_be_positive"):
        build_ejected_stake_treasury_distribution_quote(0, "-1", {"a": "1"}, 1, 1)
    with pytest.raises(ValueError, match="ejected_stake_member_stake_must_be_exact_decimal"):
        build_ejected_stake_treasury_distribution_quote(
            0,
            "1",
            {"a": 0.1, "b": "1"},
            2,
            2,
        )
    with pytest.raises(
        ValueError,
        match="ejected_stake_distribution_requires_positive_remaining_stake_phase_1350",
    ):
        build_ejected_stake_treasury_distribution_quote(
            0,
            "1",
            {"a": "0", "b": "0"},
            2,
            2,
        )


def test_phase_1350_wrapper_does_not_break_existing_phase_1107_evaluator() -> None:
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"agent-a": Decimal("1"), "agent-b": Decimal("3")},
        approve_votes=2,
        participating_voters=2,
    )

    assert ok is True
    assert payouts == [
        ("agent-a", Decimal("25.000000000")),
        ("agent-b", Decimal("75.000000000")),
    ]


def test_canonical_record_uses_strings_for_decimal_amounts() -> None:
    record = build_ejected_stake_treasury_distribution_quote(
        distribution_epoch=7,
        ejected_stake_ilc="100",
        remaining_member_stakes={"agent-a": "1", "agent-b": "3"},
        approve_votes=2,
        participating_voters=2,
    ).to_canonical_record()

    assert record["runtime_version"] == EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
    assert record["distribution_token"] == CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN
    assert record["h_con_02_guard_token"] == H_CON_02_QUORUM_GUARD_PHASE_1350_TOKEN
    assert record["ejected_stake_ilc"] == "100"
    assert record["remaining_member_stake_total_ilc"] == "4"
    assert record["quorum_floor"] == "0.5"
    assert record["payouts"] == (
        {"agent_id": "agent-a", "amount_ilc": "25"},
        {"agent_id": "agent-b", "amount_ilc": "75"},
    )
    assert record["production_ejected_stake_distribution_activated"] is False
    assert record["decision_token"] == EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_083_EVIDENCE)
    spec = _read(CDL_083_SPEC)
    scoping = _read(SCOPING)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)
    types = _read(TYPES)

    assert "CDL-083 constitutionalises" in evidence
    assert "HCON02_QUORUM_FLOOR` (= 0.50)" in spec
    assert "No `NotImplementedError` stubs exist" in scoping
    assert "NotImplementedError(CDL_HCON_02_DEPENDENCY)" not in runtime
    assert "ejected stake treasury path raises NotImplementedError" not in types
    for token in (
        "cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1",
        "h_con_02_quorum_guard_phase_1350",
        "epoch_attribution_settle_runtime_not_implemented_closed_phase_1350",
        "ejected_stake_distribution_not_activated_phase_1350",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
    ):
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
