from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.dynamic_ranking_multiplier_runtime import (
    CDL_031_AUTHORITY_TOKEN,
    CDL_031_DEFERRED_TOKEN_RETAINED,
    CDL_031_DYNAMIC_RANKING_RUNTIME_TOKEN,
    CDL_031_DYNAMIC_RANKING_RUNTIME_VERSION,
    DYNAMIC_RANKING_ANTI_DOMINANCE_MAX_SHARE,
    DYNAMIC_RANKING_F_MAX,
    DYNAMIC_RANKING_F_MIN,
    DYNAMIC_RANKING_FUNCTION,
    DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED,
    DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED_GUARD_TOKEN,
    check_anti_dominance,
    compute_dynamic_ranking_multiplier,
    compute_dynamic_ranking_multiplier_from_node_score,
)


def test_phase_1502p_guard_remains_not_activated() -> None:
    assert DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED is True
    assert (
        DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED_GUARD_TOKEN
        == "DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED_guard_set_phase_1502p"
    )


def test_phase_1502p_version_and_authority_tokens() -> None:
    assert (
        CDL_031_DYNAMIC_RANKING_RUNTIME_VERSION
        == "cdl_031_dynamic_ranking_multiplier_runtime_1502p.v0.1"
    )
    assert (
        CDL_031_DYNAMIC_RANKING_RUNTIME_TOKEN
        == "cdl_031_dynamic_ranking_multiplier_runtime_phase_1502p"
    )
    assert CDL_031_AUTHORITY_TOKEN == "cdl_019_amendment_ratified_phase_1501p"
    assert DYNAMIC_RANKING_FUNCTION == "log"


def test_phase_1502p_floor_at_zero_weight() -> None:
    assert compute_dynamic_ranking_multiplier(Decimal("0")) == DYNAMIC_RANKING_F_MIN


def test_phase_1502p_ceiling_at_unit_weight() -> None:
    assert compute_dynamic_ranking_multiplier(Decimal("1")) <= DYNAMIC_RANKING_F_MAX
    assert compute_dynamic_ranking_multiplier(Decimal("1")) == DYNAMIC_RANKING_F_MAX


def test_phase_1502p_multiplier_is_monotonic() -> None:
    weights = [Decimal("0"), Decimal("0.1"), Decimal("0.25"), Decimal("0.5"), Decimal("1")]
    outputs = [compute_dynamic_ranking_multiplier(weight) for weight in weights]
    assert outputs == sorted(outputs)


def test_phase_1502p_rejects_non_finite_inputs() -> None:
    with pytest.raises(ValueError, match="dynamic_ranking_multiplier_invalid_input"):
        compute_dynamic_ranking_multiplier(Decimal("NaN"))


def test_phase_1502p_rejects_infinite_inputs() -> None:
    with pytest.raises(ValueError, match="dynamic_ranking_multiplier_invalid_input"):
        compute_dynamic_ranking_multiplier(Decimal("Infinity"))


def test_phase_1502p_rejects_out_of_range_inputs() -> None:
    with pytest.raises(ValueError, match="dynamic_ranking_multiplier_out_of_range_input"):
        compute_dynamic_ranking_multiplier(Decimal("-0.0001"))
    with pytest.raises(ValueError, match="dynamic_ranking_multiplier_out_of_range_input"):
        compute_dynamic_ranking_multiplier(Decimal("1.0001"))


def test_phase_1502p_rejects_non_decimal_input() -> None:
    with pytest.raises(ValueError, match="dynamic_ranking_multiplier_invalid_input"):
        compute_dynamic_ranking_multiplier(0.5)  # type: ignore[arg-type]


def test_phase_1502p_reads_node_score_vector_epistemic_weight() -> None:
    score = {"node_id": "node-a", "epistemic_weight": Decimal("0.5")}
    assert compute_dynamic_ranking_multiplier_from_node_score(
        score
    ) == compute_dynamic_ranking_multiplier(Decimal("0.5"))


def test_phase_1502p_uniform_population_satisfies_anti_dominance() -> None:
    population = [compute_dynamic_ranking_multiplier(Decimal("0.5")) for _ in range(101)]
    assert check_anti_dominance(population) is True


def test_phase_1502p_dominant_agent_violates_anti_dominance() -> None:
    population = [compute_dynamic_ranking_multiplier(Decimal("1"))]
    population.extend(compute_dynamic_ranking_multiplier(Decimal("0")) for _ in range(99))
    assert check_anti_dominance(population, DYNAMIC_RANKING_ANTI_DOMINANCE_MAX_SHARE) is False


def test_phase_1502p_decay_coupling_preserves_floor() -> None:
    decayed_weight = Decimal("1")
    for _ in range(5):
        decayed_weight *= Decimal("0.95")
    assert compute_dynamic_ranking_multiplier(decayed_weight) >= DYNAMIC_RANKING_F_MIN


def test_phase_1502p_deferred_token_remains_in_issuance_gate() -> None:
    gate_text = Path("ilc_core/epoch/issuance_economics_integration_gate.py").read_text()
    assert CDL_031_DEFERRED_TOKEN_RETAINED in gate_text
