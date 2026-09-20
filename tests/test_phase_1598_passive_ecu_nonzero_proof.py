from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ilc_core.economics import epoch_attribution_settle_runtime as settle_runtime
from ilc_core.economics import passive_ecu_attribution_runtime as passive_runtime
from ilc_core.economics.epoch_attribution_settle_runtime import AttributionEvent
from ilc_core.types import EdgeType, EpochAttributionBatch, REUSE_ATTRIBUTION_RATE
from tools.ecu import passive_ecu_nonzero_proof as proof


def _event(star_node_id: str | None = proof.SEEDED_NODE_ID) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.REUSE,
        target_creator_id=proof.PHASE1598_TARGET_CREATOR_ID,
        star_node_id=star_node_id,
        epoch=proof.SEEDED_EPOCH,
    )


def _walk_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise AssertionError("float_value_found")
    if isinstance(value, dict):
        for item in value.values():
            _walk_no_float(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _walk_no_float(item)


def test_direct_nonzero_formula_result_exact() -> None:
    result = passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("0.10"),
        Decimal("0.5"),
    )

    assert result == Decimal("0.004000000000")
    assert result > Decimal("0")


@pytest.mark.parametrize(
    ("centrality", "expected"),
    [
        (Decimal("0.04"), Decimal("0")),
        (Decimal("0.05"), Decimal("0.002000000000")),
    ],
)
def test_decay_floor_boundary(centrality: Decimal, expected: Decimal) -> None:
    assert (
        passive_runtime.compute_passive_ecu(
            Decimal("0.20"),
            centrality,
            Decimal("0.5"),
        )
        == expected
    )


def test_formula_output_cap_is_independent_from_epoch_centrality_cap() -> None:
    # Direct formula calls can reach ATTRIBUTION_CAP; normal settlement first
    # applies PASSIVE_ECU_EPOCH_CENTRALITY_CAP and cannot reach this ceiling
    # with the current constants.
    result = passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("1.0"),
        Decimal("0.5"),
    )

    assert result == Decimal("0.030000000000")


def test_normal_settlement_path_stays_below_formula_output_cap() -> None:
    result = settle_runtime._compute_passive_ecu_for_event(
        _event(),
        {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "1.0"}}},
        quality_scores={proof.SEEDED_NODE_ID: Decimal("1.0")},
    )

    assert result == Decimal("0.004600000000")
    assert result < REUSE_ATTRIBUTION_RATE * passive_runtime.ATTRIBUTION_CAP


def test_decimal_like_int_and_string_inputs_are_intentionally_accepted() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        "0.10",
        Decimal("0.5"),
    ) == Decimal("0.004000000000")
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        1,
        Decimal("0.5"),
    ) == Decimal("0.030000000000")
    assert passive_runtime.quality_factor("0.5") == Decimal("1.000000000000")


def test_upper_boundary_centrality_one_is_accepted() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("1.0"),
        Decimal("0.5"),
    ) == Decimal("0.030000000000")


@pytest.mark.parametrize(
    ("q_i", "expected_quality", "expected_passive"),
    [
        (Decimal("0.0"), Decimal("0.850000000000"), Decimal("0.003400000000")),
        (Decimal("0.5"), Decimal("1.000000000000"), Decimal("0.004000000000")),
        (Decimal("1.0"), Decimal("1.150000000000"), Decimal("0.004600000000")),
    ],
)
def test_quality_factor_exact_decimal_results(
    q_i: Decimal,
    expected_quality: Decimal,
    expected_passive: Decimal,
) -> None:
    quality = passive_runtime.quality_factor(q_i)

    assert isinstance(quality, Decimal)
    assert quality == expected_quality
    assert str(quality) == str(expected_quality)
    assert passive_runtime.compute_passive_ecu(
        Decimal("0.20"),
        Decimal("0.10"),
        q_i,
    ) == expected_passive


def test_base_reward_zero_short_circuits_to_zero() -> None:
    assert passive_runtime.compute_passive_ecu(
        Decimal("0"),
        Decimal("0.10"),
        Decimal("0.5"),
    ) == Decimal("0")


@pytest.mark.parametrize(
    ("callable_factory", "token"),
    [
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), 0.10, Decimal("0.5")
            ),
            "centrality_score_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                0.20, Decimal("0.10"), Decimal("0.5")
            ),
            "base_reward_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.quality_factor(0.5),
            "q_i_must_be_decimal_in_unit_interval",
        ),
    ],
)
def test_float_inputs_rejected_with_specific_tokens(
    callable_factory: Any,
    token: str,
) -> None:
    with pytest.raises(ValueError, match=token):
        callable_factory()


@pytest.mark.parametrize(
    ("callable_factory", "token"),
    [
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("NaN"), Decimal("0.5")
            ),
            "centrality_score_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("Infinity"), Decimal("0.5")
            ),
            "centrality_score_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("NaN"), Decimal("0.10"), Decimal("0.5")
            ),
            "base_reward_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.quality_factor(Decimal("NaN")),
            "q_i_must_be_decimal_in_unit_interval",
        ),
        (
            lambda: passive_runtime.quality_factor(Decimal("Infinity")),
            "q_i_must_be_decimal_in_unit_interval",
        ),
    ],
)
def test_non_finite_inputs_rejected_with_specific_tokens(
    callable_factory: Any,
    token: str,
) -> None:
    with pytest.raises(ValueError, match=token):
        callable_factory()


@pytest.mark.parametrize(
    ("callable_factory", "token"),
    [
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("1.01"), Decimal("0.5")
            ),
            "centrality_score_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("-0.01"), Decimal("0.5")
            ),
            "centrality_score_must_be_non_negative_decimal",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("0.10"), Decimal("1.01")
            ),
            "q_i_must_be_decimal_in_unit_interval",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("0.20"), Decimal("0.10"), Decimal("-0.01")
            ),
            "q_i_must_be_decimal_in_unit_interval",
        ),
        (
            lambda: passive_runtime.compute_passive_ecu(
                Decimal("-0.01"), Decimal("0.10"), Decimal("0.5")
            ),
            "base_reward_must_be_non_negative_decimal",
        ),
    ],
)
def test_range_guards_reject_invalid_values(callable_factory: Any, token: str) -> None:
    with pytest.raises(ValueError, match=token):
        callable_factory()


def test_centrality_lookup_caps_int_epoch_key() -> None:
    state = {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}}

    score = settle_runtime._get_centrality_score(
        proof.SEEDED_NODE_ID,
        proof.SEEDED_EPOCH,
        state,
    )

    assert score == settle_runtime.PASSIVE_ECU_EPOCH_CENTRALITY_CAP
    assert score == Decimal("0.100000000000")


def test_centrality_lookup_caps_string_epoch_key_after_json_roundtrip() -> None:
    state = {"_pending": {str(proof.SEEDED_EPOCH): {proof.SEEDED_NODE_ID: "0.15"}}}

    score = settle_runtime._get_centrality_score(
        proof.SEEDED_NODE_ID,
        proof.SEEDED_EPOCH,
        state,
    )

    assert score == Decimal("0.100000000000")


def test_centrality_lookup_fallback_none_and_missing_node() -> None:
    assert settle_runtime._get_centrality_score(
        proof.SEEDED_NODE_ID,
        proof.SEEDED_EPOCH,
        {proof.SEEDED_NODE_ID: "0.08"},
    ) == Decimal("0.080000000000")
    assert settle_runtime._get_centrality_score(
        proof.SEEDED_NODE_ID,
        proof.SEEDED_EPOCH,
        None,
    ) == Decimal("0")
    assert settle_runtime._get_centrality_score(
        proof.MISSING_NODE_ID,
        proof.SEEDED_EPOCH,
        {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}},
    ) == Decimal("0")


def test_compute_passive_ecu_for_event_nonzero_with_seeded_state() -> None:
    # Phase 1598 intentionally couples to the private passive ECU helper to
    # prove the seeded sub-path directly; a sealed-batch wrapper test below
    # protects the public settlement integration surface.
    result = settle_runtime._compute_passive_ecu_for_event(
        _event(),
        {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}},
        quality_scores=None,
    )

    assert REUSE_ATTRIBUTION_RATE == Decimal("0.20")
    assert result == Decimal("0.004000000000")


def test_settle_attribution_batch_routes_direct_and_passive_ecu_to_reuse_recipient() -> None:
    batch = EpochAttributionBatch(epoch=proof.SEEDED_EPOCH)
    batch.add_event(_event())
    batch.seal()

    payouts = settle_runtime.settle_attribution_batch(
        batch,
        stake_map={},
        passive_ecu_centrality_state={
            "_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}
        },
        passive_ecu_quality_scores=None,
    )

    assert payouts == [
        (proof.PHASE1598_TARGET_CREATOR_ID, Decimal("0.20")),
        (proof.PHASE1598_TARGET_CREATOR_ID, Decimal("0.004000000000")),
    ]


def test_compute_passive_ecu_for_event_star_node_none_is_zero() -> None:
    result = settle_runtime._compute_passive_ecu_for_event(
        _event(star_node_id=None),
        {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}},
        quality_scores=None,
    )

    assert result == Decimal("0")


def test_passive_ecu_wiring_guard_forces_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settle_runtime, "PASSIVE_ECU_WIRING_NOT_ACTIVATED", True)

    result = settle_runtime._compute_passive_ecu_for_event(
        _event(),
        {"_pending": {proof.SEEDED_EPOCH: {proof.SEEDED_NODE_ID: "0.15"}}},
        quality_scores=None,
    )

    assert result == Decimal("0")


def test_contract_validation_detects_cdl_060_version_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert hasattr(passive_runtime, "_CDL_060_GOSSIP_RUNTIME_CHECK")
    monkeypatch.setattr(
        passive_runtime,
        "_CDL_060_GOSSIP_RUNTIME_CHECK",
        "wrong-version",
    )

    with pytest.raises(
        passive_runtime.PassiveECUAttributionContractError,
        match="passive_ecu_dependency_mismatch",
    ):
        passive_runtime._validate_runtime_contract()


def test_member_id_whitespace_rejected_in_stake_paths() -> None:
    with pytest.raises(ValueError, match="stake_map_member_id_must_be_non_empty_string"):
        settle_runtime._normalize_member_stakes({"   ": Decimal("1")})
    with pytest.raises(ValueError, match="ejected_stake_member_id_must_be_non_empty_string"):
        settle_runtime._normalize_distribution_member_stakes({" member ": Decimal("1")})


def test_runner_builds_complete_evidence_without_float_values(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"

    evidence = proof.run_proof(evidence_path)
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert evidence["output_token"] == proof.OUTPUT_TOKEN
    assert payload["nonzero_proof_result"] == "0.004000000000"
    assert payload["settle_attribution_batch_passive_result"] == "0.004000000000"
    assert payload["settle_attribution_batch_payouts"] == [
        {"agent_id": proof.PHASE1598_TARGET_CREATOR_ID, "amount_ecu": "0.20"},
        {"agent_id": proof.PHASE1598_TARGET_CREATOR_ID, "amount_ecu": "0.004000000000"},
    ]
    assert payload["float_rejection_confirmed"] is True
    assert payload["nan_rejection_confirmed"] is True
    assert payload["epoch_centrality_cap_enforcement_confirmed"] is True
    _walk_no_float(payload)
