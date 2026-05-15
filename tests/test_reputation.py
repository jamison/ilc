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


def test_apply_atrophy_decay() -> None:
    current_epoch = ATROPHY_HALF_LIFE_EPOCHS + 2000
    agent_state = {
        "last_active_epoch": 2000,
        "trust_vector": {"accuracy": Decimal("1"), "precision": Decimal("1")},
    }

    new_state = apply_atrophy(agent_state, current_epoch)
    assert new_state["trust_vector"]["accuracy"] == Decimal("0.500000000000")
    assert new_state["trust_vector"]["precision"] == Decimal("0.500000000000")


def test_reputation_runtime_tokens_and_default_off_guard() -> None:
    assert REPUTATION_RUNTIME_VERSION == "reputation_runtime_h11_float_kill_1357.v0.1"
    with pytest.raises(ValueError, match=PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN):
        require_production_reputation_scoring_activation()
