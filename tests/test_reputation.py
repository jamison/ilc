from decimal import Decimal

import pytest

from ilc_core.consensus.reputation import (
    ATROPHY_HALF_LIFE_EPOCHS,
    MAX_POTENTIAL_BOOST,
    PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN,
    REPUTATION_RUNTIME_VERSION,
    apply_atrophy,
    calculate_voting_power,
    require_production_reputation_scoring_activation,
)


def test_calculate_voting_power_perfect_score() -> None:
    stake = Decimal("100")
    trust_vector = {
        "accuracy": Decimal("1"),
        "precision": Decimal("1"),
        "potential": Decimal("1"),
    }

    assert MAX_POTENTIAL_BOOST == Decimal("0.5")
    assert calculate_voting_power(stake, trust_vector) == Decimal("150")


def test_calculate_voting_power_zero_score() -> None:
    stake = Decimal("100")
    trust_vector = {
        "accuracy": Decimal("0"),
        "precision": Decimal("0"),
        "potential": Decimal("0"),
    }

    assert calculate_voting_power(stake, trust_vector) == Decimal("0")


def test_calculate_voting_power_mixed_score() -> None:
    stake = Decimal("100")
    trust_vector = {
        "accuracy": Decimal("0.8"),
        "precision": Decimal("0.6"),
        "potential": Decimal("0.5"),
    }

    assert calculate_voting_power(stake, trust_vector) == Decimal("92.500")


def test_calculate_voting_power_rejects_float_input() -> None:
    with pytest.raises(
        ValueError,
        match="reputation_stake_must_be_non_negative_decimal_phase_1357",
    ):
        calculate_voting_power(100.0, {"accuracy": Decimal("1")})


def test_calculate_voting_power_rejects_non_finite_trust_values() -> None:
    for field in ("accuracy", "precision", "potential"):
        trust_vector = {
            "accuracy": Decimal("1"),
            "precision": Decimal("1"),
            "potential": Decimal("0"),
        }
        trust_vector[field] = Decimal("NaN")
        with pytest.raises(ValueError, match="invalid_amount_non_finite"):
            calculate_voting_power(Decimal("100"), trust_vector)


def test_calculate_voting_power_rejects_trust_values_above_one() -> None:
    for field, token in (
        ("accuracy", "reputation_accuracy_must_be_non_negative_decimal_phase_1357"),
        ("precision", "reputation_precision_must_be_non_negative_decimal_phase_1357"),
        ("potential", "reputation_potential_must_be_non_negative_decimal_phase_1357"),
    ):
        trust_vector = {
            "accuracy": Decimal("1"),
            "precision": Decimal("1"),
            "potential": Decimal("0"),
        }
        trust_vector[field] = Decimal("1.000000000001")
        with pytest.raises(ValueError, match=token):
            calculate_voting_power(Decimal("100"), trust_vector)


def test_apply_atrophy_no_decay_returns_copy_without_mutation() -> None:
    current_epoch = 2000
    agent_state = {
        "last_active_epoch": 1000,
        "trust_vector": {"accuracy": Decimal("1"), "precision": Decimal("1")},
    }

    new_state = apply_atrophy(agent_state, current_epoch)
    assert new_state is not agent_state
    assert new_state["trust_vector"] is not agent_state["trust_vector"]
    assert new_state["trust_vector"]["accuracy"] == Decimal("1")
    assert new_state["trust_vector"]["precision"] == Decimal("1")
    assert agent_state["trust_vector"]["accuracy"] == Decimal("1")


def test_apply_atrophy_rejects_last_active_epoch_after_current_epoch() -> None:
    with pytest.raises(
        ValueError,
        match="reputation_current_epoch_precedes_last_active_epoch_phase_1357",
    ):
        apply_atrophy(
            {
                "last_active_epoch": 11,
                "trust_vector": {"accuracy": Decimal("1"), "precision": Decimal("1")},
            },
            10,
        )


def test_apply_atrophy_decay() -> None:
    current_epoch = ATROPHY_HALF_LIFE_EPOCHS + 2000
    agent_state = {
        "last_active_epoch": 2000,
        "trust_vector": {"accuracy": Decimal("1"), "precision": Decimal("1")},
    }

    new_state = apply_atrophy(agent_state, current_epoch)
    assert new_state["trust_vector"]["accuracy"] == Decimal("0.500000000000")
    assert new_state["trust_vector"]["precision"] == Decimal("0.500000000000")


def test_calculate_voting_power_missing_potential_defaults_to_zero() -> None:
    # potential is optional; absent key defaults to ZERO via trust_vector.get("potential", ZERO)
    stake = Decimal("100")
    trust_vector = {"accuracy": Decimal("1"), "precision": Decimal("1")}
    result = calculate_voting_power(stake, trust_vector)
    # efficiency_multiplier = 1 + 0 * 0.5 = 1; epistemic_score = 0.7 + 0.3 = 1
    assert result == Decimal("100")


def test_reputation_runtime_tokens_and_default_off_guard() -> None:
    assert REPUTATION_RUNTIME_VERSION == "reputation_runtime_h11_float_kill_1357.v0.1"
    with pytest.raises(ValueError, match=PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN):
        require_production_reputation_scoring_activation()
