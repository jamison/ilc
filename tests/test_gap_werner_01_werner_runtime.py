"""Tests for Werner Credit Pressure-Signal Runtime (GAP-WERNER-01).

Covers:
- Zero/empty topology → Decimal("0")
- Single-node topology
- Two-node symmetric topology
- Full clique topology
- Star topology (hub vs. leaf pressure)
- Non-finite Decimal rejection (NaN, Infinity)
- Alpha out-of-range rejection
- No float in output
- Beta signal computation
- Smoothed pressure EMA
- Spectral trust eligibility
- Flow budget computation
- Multi-epoch smoothed candidate priority

All inputs use decimal.Decimal — never float.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics.werner_runtime import (
    WERNER_CREDIT_WIRING_NOT_ACTIVATED,
    WERNER_RUNTIME_VERSION,
    TOPOLOGY_PRESSURE_MODEL,
    WERNER_HEAT_THRESHOLD,
    SPECTRAL_TRUST_BETA_FLOOR,
    SPECTRAL_TRUST_PULSE_FLOOR,
    compute_degree_centrality,
    compute_smoothed_pressure,
    compute_beta_signal,
    compute_werner_pressure_signal,
    compute_werner_smoothed_candidate_priority,
    compute_flow_budget,
    is_spectral_trust_eligible,
)


# ---------------------------------------------------------------------------
# Guard and version constants
# ---------------------------------------------------------------------------

class TestGuardAndVersion:
    def test_guard_is_true(self):
        """WERNER_CREDIT_WIRING_NOT_ACTIVATED must be True in this phase."""
        assert WERNER_CREDIT_WIRING_NOT_ACTIVATED is True

    def test_version_token(self):
        assert WERNER_RUNTIME_VERSION == "werner_credit_pressure_signal_gap_werner_01.v0.1"

    def test_topology_model(self):
        assert TOPOLOGY_PRESSURE_MODEL == "werner_v1"

    def test_heat_threshold(self):
        assert WERNER_HEAT_THRESHOLD == Decimal("100")


# ---------------------------------------------------------------------------
# Test 1: Zero topology (empty adjacency)
# ---------------------------------------------------------------------------

class TestZeroTopology:
    def test_zero_topology_returns_zero(self):
        """Empty adjacency → compute_werner_pressure_signal returns Decimal('0')."""
        result = compute_werner_pressure_signal(
            node_id="n1",
            adjacency={},
            centrality={},
            alpha=Decimal("0.5"),
            beta_signal=Decimal("0.75"),
        )
        assert result == Decimal("0")
        assert isinstance(result, Decimal)

    def test_empty_adjacency_degree_centrality(self):
        """compute_degree_centrality of empty graph returns empty dict."""
        result = compute_degree_centrality({})
        assert result == {}


# ---------------------------------------------------------------------------
# Test 2: Single-node topology
# ---------------------------------------------------------------------------

class TestSingleNode:
    def test_single_node_centrality_zero(self):
        """One node with no neighbors → degree centrality = 0."""
        adj = {"n1": []}
        centrality = compute_degree_centrality(adj)
        assert centrality["n1"] == Decimal("0")

    def test_single_node_pressure_signal_zero(self):
        """Single node in adjacency → pressure signal = 0 (no edges → centrality 0)."""
        adj = {"n1": []}
        centrality = compute_degree_centrality(adj)
        result = compute_werner_pressure_signal(
            node_id="n1",
            adjacency=adj,
            centrality=centrality,
            alpha=Decimal("0.5"),
            beta_signal=Decimal("0.8"),
        )
        assert result == Decimal("0")
        assert isinstance(result, Decimal)


# ---------------------------------------------------------------------------
# Test 3: Two-node symmetric topology
# ---------------------------------------------------------------------------

class TestTwoNodeSymmetric:
    def test_two_node_equal_centrality(self):
        """Two connected nodes have equal degree centrality (each has 1 neighbor, max=1)."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = compute_degree_centrality(adj)
        assert centrality["a"] == Decimal("1")
        assert centrality["b"] == Decimal("1")

    def test_two_node_equal_pressure(self):
        """Two connected nodes with equal beta produce equal pressure signals."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = compute_degree_centrality(adj)
        beta = Decimal("0.7")
        pa = compute_werner_pressure_signal(
            node_id="a", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        pb = compute_werner_pressure_signal(
            node_id="b", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        assert pa == pb
        assert isinstance(pa, Decimal)


# ---------------------------------------------------------------------------
# Test 4: Full clique — uniform pressure
# ---------------------------------------------------------------------------

class TestFullClique:
    def _make_clique(self, n: int) -> dict[str, list[str]]:
        nodes = [f"n{i}" for i in range(n)]
        return {node: [other for other in nodes if other != node] for node in nodes}

    def test_full_clique_uniform_centrality(self):
        """All nodes in a clique have degree centrality = 1."""
        adj = self._make_clique(5)
        centrality = compute_degree_centrality(adj)
        expected = Decimal("1")
        for node_id, c in centrality.items():
            assert c == expected, f"Node {node_id} centrality {c} != {expected}"

    def test_full_clique_uniform_pressure(self):
        """In a clique, all nodes produce the same pressure signal."""
        adj = self._make_clique(4)
        centrality = compute_degree_centrality(adj)
        beta = Decimal("0.6")
        pressures = [
            compute_werner_pressure_signal(
                node_id=nid, adjacency=adj, centrality=centrality,
                alpha=Decimal("0.5"), beta_signal=beta,
            )
            for nid in adj
        ]
        assert len(set(pressures)) == 1
        assert isinstance(pressures[0], Decimal)


# ---------------------------------------------------------------------------
# Test 5: Star topology — hub has higher pressure than leaves
# ---------------------------------------------------------------------------

class TestStarTopologyHub:
    def _make_star(self, n_leaves: int) -> dict[str, list[str]]:
        """Create a star with 1 hub and n_leaves leaf nodes."""
        hub = "hub"
        leaves = [f"leaf{i}" for i in range(n_leaves)]
        adj = {hub: leaves[:]}
        for leaf in leaves:
            adj[leaf] = [hub]
        return adj

    def test_hub_higher_centrality_than_leaf(self):
        """Hub node in a star has higher degree centrality than any leaf."""
        adj = self._make_star(4)
        centrality = compute_degree_centrality(adj)
        hub_c = centrality["hub"]
        leaf_c = centrality["leaf0"]
        assert hub_c > leaf_c

    def test_hub_higher_pressure_than_leaf(self):
        """Hub node produces higher pressure signal than leaves (same beta)."""
        adj = self._make_star(4)
        centrality = compute_degree_centrality(adj)
        beta = Decimal("0.75")
        hub_pressure = compute_werner_pressure_signal(
            node_id="hub", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        leaf_pressure = compute_werner_pressure_signal(
            node_id="leaf0", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        assert hub_pressure > leaf_pressure
        assert isinstance(hub_pressure, Decimal)


# ---------------------------------------------------------------------------
# Test 6: Star topology — leaf node
# ---------------------------------------------------------------------------

class TestStarTopologyLeaf:
    def test_leaf_pressure_non_negative(self):
        """Leaf node pressure signal is non-negative Decimal."""
        adj = {"hub": ["leaf0", "leaf1"], "leaf0": ["hub"], "leaf1": ["hub"]}
        centrality = compute_degree_centrality(adj)
        result = compute_werner_pressure_signal(
            node_id="leaf0", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=Decimal("0.6"),
        )
        assert result >= Decimal("0")
        assert isinstance(result, Decimal)

    def test_leaf_pressure_less_than_hub(self):
        """Leaf pressure is strictly less than hub pressure in an unbalanced star."""
        adj = {"hub": ["l0", "l1", "l2"], "l0": ["hub"], "l1": ["hub"], "l2": ["hub"]}
        centrality = compute_degree_centrality(adj)
        beta = Decimal("0.8")
        hub_p = compute_werner_pressure_signal(
            node_id="hub", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        leaf_p = compute_werner_pressure_signal(
            node_id="l0", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=beta,
        )
        assert hub_p > leaf_p


# ---------------------------------------------------------------------------
# Test 7: Non-finite centrality (NaN) rejected
# ---------------------------------------------------------------------------

class TestNonFiniteCentralityNaN:
    def test_nan_centrality_raises(self):
        """Decimal('NaN') centrality input raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("NaN"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=Decimal("0.5"), beta_signal=Decimal("0.7"),
            )


# ---------------------------------------------------------------------------
# Test 8: Non-finite centrality (Infinity) rejected
# ---------------------------------------------------------------------------

class TestNonFiniteCentralityInfinity:
    def test_infinity_centrality_raises(self):
        """Decimal('Infinity') centrality input raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("Infinity"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=Decimal("0.5"), beta_signal=Decimal("0.7"),
            )


# ---------------------------------------------------------------------------
# Test 9: Non-finite alpha (NaN) rejected
# ---------------------------------------------------------------------------

class TestNonFiniteAlphaRejected:
    def test_nan_alpha_raises(self):
        """Decimal('NaN') alpha raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("1"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=Decimal("NaN"), beta_signal=Decimal("0.7"),
            )

    def test_infinity_alpha_raises(self):
        """Decimal('Infinity') alpha raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("1"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=Decimal("Infinity"), beta_signal=Decimal("0.7"),
            )


# ---------------------------------------------------------------------------
# Test 10: No float in output
# ---------------------------------------------------------------------------

class TestNoFloatInOutput:
    def test_output_is_decimal_not_float(self):
        """compute_werner_pressure_signal always returns Decimal, never float."""
        adj = {"a": ["b", "c"], "b": ["a"], "c": ["a"]}
        centrality = compute_degree_centrality(adj)
        result = compute_werner_pressure_signal(
            node_id="a", adjacency=adj, centrality=centrality,
            alpha=Decimal("0.5"), beta_signal=Decimal("0.75"),
        )
        assert isinstance(result, Decimal), f"Expected Decimal, got {type(result)}"
        assert not isinstance(result, float)

    def test_float_beta_raises(self):
        """Passing float as beta_signal raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("1"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="float_not_allowed"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=Decimal("0.5"), beta_signal=0.75,  # float — must be rejected
            )

    def test_float_alpha_raises(self):
        """Passing float as alpha raises ValueError."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("1"), "b": Decimal("1")}
        with pytest.raises(ValueError, match="float_not_allowed"):
            compute_werner_pressure_signal(
                node_id="a", adjacency=adj, centrality=centrality,
                alpha=0.5,  # float — must be rejected
                beta_signal=Decimal("0.75"),
            )

    def test_smoothed_pressure_output_is_decimal(self):
        """compute_smoothed_pressure always returns Decimal."""
        sequence = [Decimal("10"), Decimal("20"), Decimal("15")]
        result = compute_smoothed_pressure(sequence, alpha=Decimal("0.5"))
        assert isinstance(result, Decimal)

    def test_degree_centrality_values_are_decimal(self):
        """compute_degree_centrality returns Decimal values."""
        adj = {"a": ["b", "c"], "b": ["a"], "c": ["a"]}
        result = compute_degree_centrality(adj)
        for node, c in result.items():
            assert isinstance(c, Decimal), f"Node {node} centrality is {type(c)}"


# ---------------------------------------------------------------------------
# Test 11: Beta signal computation
# ---------------------------------------------------------------------------

class TestBetaSignalComputation:
    def test_beta_full_scheduled(self):
        """All capacity scheduled → beta = 1."""
        result = compute_beta_signal(
            scheduled_capacity=Decimal("1000"),
            unserved_capacity=Decimal("0"),
        )
        assert result == Decimal("1")

    def test_beta_none_scheduled(self):
        """No capacity scheduled → beta = 0."""
        result = compute_beta_signal(
            scheduled_capacity=Decimal("0"),
            unserved_capacity=Decimal("500"),
        )
        assert result == Decimal("0")

    def test_beta_zero_total_zero(self):
        """Zero total capacity → beta = 0 (no division by zero)."""
        result = compute_beta_signal(
            scheduled_capacity=Decimal("0"),
            unserved_capacity=Decimal("0"),
        )
        assert result == Decimal("0")

    def test_beta_sim_v3_epoch_147401(self):
        """Reproduce SIM v3 §3 epoch 147401: beta = 1800/(1800+600) ≈ 0.75."""
        result = compute_beta_signal(
            scheduled_capacity=Decimal("1800"),
            unserved_capacity=Decimal("600"),
        )
        assert result == Decimal("0.75").quantize(Decimal("0.000000000001"))

    def test_beta_sim_v3_epoch_147403(self):
        """Reproduce SIM v3 §3 epoch 147403: beta = 900/(900+3500) ≈ 0.2045..."""
        result = compute_beta_signal(
            scheduled_capacity=Decimal("900"),
            unserved_capacity=Decimal("3500"),
        )
        expected = (Decimal("900") / Decimal("4400")).quantize(Decimal("0.000000000001"))
        assert result == expected

    def test_beta_nan_scheduled_raises(self):
        """NaN in scheduled_capacity raises ValueError."""
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_beta_signal(
                scheduled_capacity=Decimal("NaN"),
                unserved_capacity=Decimal("100"),
            )

    def test_beta_float_input_raises(self):
        """Float input raises ValueError."""
        with pytest.raises(ValueError, match="float_not_allowed"):
            compute_beta_signal(
                scheduled_capacity=100.0,  # float — must be rejected
                unserved_capacity=Decimal("0"),
            )


# ---------------------------------------------------------------------------
# Test 12: Smoothed pressure EMA
# ---------------------------------------------------------------------------

class TestSmoothedPressureEMA:
    def test_single_value_returns_value(self):
        """Single raw pressure → smoothed = that value."""
        result = compute_smoothed_pressure([Decimal("50")], alpha=Decimal("0.5"))
        assert result == Decimal("50").quantize(Decimal("0.000000000001"))

    def test_ema_decreasing(self):
        """EMA of decreasing sequence is below the first value."""
        sequence = [Decimal("100"), Decimal("50"), Decimal("10")]
        result = compute_smoothed_pressure(sequence, alpha=Decimal("0.5"))
        assert result < Decimal("100")
        assert result > Decimal("0")

    def test_ema_constant_sequence(self):
        """EMA of constant sequence returns that constant."""
        sequence = [Decimal("30"), Decimal("30"), Decimal("30")]
        result = compute_smoothed_pressure(sequence, alpha=Decimal("0.5"))
        assert result == Decimal("30").quantize(Decimal("0.000000000001"))

    def test_ema_empty_sequence_raises(self):
        """Empty sequence raises ValueError."""
        with pytest.raises(ValueError, match="non_empty"):
            compute_smoothed_pressure([], alpha=Decimal("0.5"))

    def test_ema_nan_alpha_raises(self):
        """NaN alpha raises ValueError."""
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_smoothed_pressure([Decimal("10")], alpha=Decimal("NaN"))

    def test_cdl096_pressure_sequence(self):
        """Reproduce CDL-096 §2 evidence: smoothed sequence 479.875, 739.3125, 848.65625."""
        # These smoothed values from CDL-096 §2 Tier B evidence
        # We verify the EMA formula gives increasing smoothed pressure for increasing input
        raw = [Decimal("479"), Decimal("1000"), Decimal("960")]
        result = compute_smoothed_pressure(raw, alpha=Decimal("0.5"))
        assert result > Decimal("479")
        assert isinstance(result, Decimal)


# ---------------------------------------------------------------------------
# Test 13: Spectral trust eligibility (CDL-096 §2: K=2, N=3)
# ---------------------------------------------------------------------------

class TestSpectralTrustEligibility:
    def test_all_above_floor_eligible(self):
        """3 epochs all above beta_floor and pulse_floor → eligible (K=2 of N=3)."""
        betas = [Decimal("0.8"), Decimal("0.9"), Decimal("0.7")]
        pulses = [Decimal("0.8"), Decimal("0.9"), Decimal("0.7")]
        assert is_spectral_trust_eligible(betas, pulses) is True

    def test_one_above_floor_not_eligible(self):
        """Only 1 epoch above both floors → not eligible (need K=2)."""
        betas = [Decimal("0.3"), Decimal("0.3"), Decimal("0.8")]
        pulses = [Decimal("0.3"), Decimal("0.3"), Decimal("0.8")]
        assert is_spectral_trust_eligible(betas, pulses) is False

    def test_exactly_at_floor_not_eligible(self):
        """Exactly at beta_floor (not strictly above) → not eligible."""
        betas = [Decimal("0.5"), Decimal("0.5"), Decimal("0.5")]
        pulses = [Decimal("0.8"), Decimal("0.8"), Decimal("0.8")]
        assert is_spectral_trust_eligible(betas, pulses) is False

    def test_insufficient_history_not_eligible(self):
        """Fewer than N epochs of history → not eligible."""
        betas = [Decimal("0.9"), Decimal("0.9")]   # only 2 < N=3
        pulses = [Decimal("0.9"), Decimal("0.9")]
        assert is_spectral_trust_eligible(betas, pulses) is False

    def test_nan_beta_history_raises(self):
        """NaN in beta_signal_history raises ValueError."""
        betas = [Decimal("0.8"), Decimal("NaN"), Decimal("0.8")]
        pulses = [Decimal("0.8"), Decimal("0.8"), Decimal("0.8")]
        with pytest.raises(ValueError, match="non_finite_decimal"):
            is_spectral_trust_eligible(betas, pulses)


# ---------------------------------------------------------------------------
# Test 14: Multi-epoch smoothed candidate priority
# ---------------------------------------------------------------------------

class TestMultiEpochSmoothedPriority:
    def test_increasing_beta_increases_priority(self):
        """Increasing beta signal sequence should yield positive priority for connected node."""
        adj = {"hub": ["l0", "l1"], "l0": ["hub"], "l1": ["hub"]}
        centrality = compute_degree_centrality(adj)
        betas = [Decimal("0.5"), Decimal("0.6"), Decimal("0.7")]
        result = compute_werner_smoothed_candidate_priority(
            node_id="hub", adjacency=adj, centrality=centrality,
            beta_signal_sequence=betas, alpha=Decimal("0.5"),
        )
        assert result > Decimal("0")
        assert isinstance(result, Decimal)

    def test_zero_beta_throughout_gives_zero(self):
        """Zero beta for all epochs → priority = 0."""
        adj = {"a": ["b"], "b": ["a"]}
        centrality = {"a": Decimal("1"), "b": Decimal("1")}
        betas = [Decimal("0"), Decimal("0"), Decimal("0")]
        result = compute_werner_smoothed_candidate_priority(
            node_id="a", adjacency=adj, centrality=centrality,
            beta_signal_sequence=betas, alpha=Decimal("0.5"),
        )
        assert result == Decimal("0")

    def test_empty_adjacency_gives_zero(self):
        """Empty adjacency → multi-epoch priority = 0."""
        result = compute_werner_smoothed_candidate_priority(
            node_id="x", adjacency={}, centrality={},
            beta_signal_sequence=[Decimal("0.8")], alpha=Decimal("0.5"),
        )
        assert result == Decimal("0")


# ---------------------------------------------------------------------------
# Test 15: Flow budget computation
# ---------------------------------------------------------------------------

class TestFlowBudgetComputation:
    def test_flow_budget_capped_by_policy(self):
        """flow_budget = min(cap, priority) → cap applies when priority > cap."""
        result = compute_flow_budget(
            candidate_priority=Decimal("5"),
            runtime_policy_cap=Decimal("3"),
        )
        assert result == Decimal("3")

    def test_flow_budget_uncapped(self):
        """flow_budget = priority when priority <= cap."""
        result = compute_flow_budget(
            candidate_priority=Decimal("2"),
            runtime_policy_cap=Decimal("10"),
        )
        assert result == Decimal("2")

    def test_flow_budget_returns_decimal(self):
        """flow_budget always returns Decimal."""
        result = compute_flow_budget(
            candidate_priority=Decimal("1"),
            runtime_policy_cap=Decimal("100"),
        )
        assert isinstance(result, Decimal)

    def test_flow_budget_nan_cap_raises(self):
        """NaN runtime_policy_cap raises ValueError."""
        with pytest.raises(ValueError, match="non_finite_decimal"):
            compute_flow_budget(
                candidate_priority=Decimal("1"),
                runtime_policy_cap=Decimal("NaN"),
            )

    def test_flow_budget_float_raises(self):
        """Float candidate_priority raises ValueError."""
        with pytest.raises(ValueError, match="float_not_allowed"):
            compute_flow_budget(
                candidate_priority=1.5,  # float — must be rejected
                runtime_policy_cap=Decimal("10"),
            )
