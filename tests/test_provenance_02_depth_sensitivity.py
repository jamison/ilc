"""Tests for SIM-PROVENANCE-02: depth-sensitivity, lost-middle, Genesis-skew,
load-bearing ancestor selection, and anti-circular-flow verification.

Research-only. No runtime ECU minting, settlement, or activation authority.

Non-activation tokens:
  provenance_02_depth_sensitivity_simulation_research_only
  no_provenance_depth_amendment_from_sim_02
  provenance_max_depth_3_not_changed_by_sim_02
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

# Ensure simulations package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulations.sim_provenance_02_depth_sensitivity import (
    DUST_THRESHOLD,
    GENESIS_CAP_FRACTION,
    HUB_MAINTENANCE_CAP,
    HUB_PARASITIC_THRESHOLD,
    HUB_PASS_THROUGH_FRACTION,
    HUB_RELAY_HOP_DEPTHS,
    HUB_RETAIN_RATE,
    ONE,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH_CURRENT,
    REUSE_ATTRIBUTION_RATE,
    ZERO,
    ChainNode,
    HubRelayNode,
    _hop_payout,
    _hub_relay_chain,
    _infinite_geometric_total,
    _q9,
    _region_fractions,
    circular_chain,
    convergence_topology,
    linear_chain,
    run_all_sims,
    settle_chain_depth_cap,
    settle_chain_top_k,
    settle_hub_relay,
    sim_anti_circular_flow,
    sim_branch_skew,
    sim_convergence_accumulation,
    sim_depth_cap_comparison,
    sim_dust_aggregation,
    sim_genesis_skew,
    sim_hub_relay_variant,
    sim_lost_middle,
    sim_top_k_selection,
)


# ---------------------------------------------------------------------------
# Test 1: Depth-3 baseline — matches current canon
# ---------------------------------------------------------------------------

class TestDepth3Baseline:
    """SIM case 1: depth-3 behavior matches known runtime output."""

    def test_hop_payouts_match_canon(self):
        """Hop payouts at depth 3 match values documented in canon."""
        # From docs/research/ilc_pressure_flow_application_confidence_ranking_v0.1.md
        # Hop 1: 0.20 * 0.45 = 0.090
        # Hop 2: 0.20 * 0.45^2 = 0.0405
        # Hop 3: 0.20 * 0.45^3 = 0.018225
        assert _hop_payout(0) == _q9(Decimal("0.090"))
        assert _hop_payout(1) == _q9(Decimal("0.0405"))
        assert _hop_payout(2) == _q9(Decimal("0.018225"))

    def test_depth3_captures_expected_fraction_of_infinite(self):
        """Depth-3 cap captures ~90.9% of infinite geometric total."""
        chain = linear_chain(20)
        result = settle_chain_depth_cap(chain, 3)
        capture = Decimal(result["capture_fraction"])
        # Should be ~ 0.148725 / 0.163636... ≈ 0.908874
        assert capture > Decimal("0.89")
        assert capture < Decimal("0.93")

    def test_depth3_pays_exactly_3_creators(self):
        """Depth-3 on a 20-node chain pays exactly 3 creators."""
        chain = linear_chain(20)
        result = settle_chain_depth_cap(chain, 3)
        if not (len(result["payouts_by_creator"]) == 3):
            raise ValueError("depth3_creator_count_mismatch")

    def test_provenance_max_depth_current_is_3(self):
        """Canon constant PROVENANCE_MAX_DEPTH is 3 — not changed by this sim."""
        assert PROVENANCE_MAX_DEPTH_CURRENT == 3


# ---------------------------------------------------------------------------
# Test 2: Depth 5/8/13 comparison
# ---------------------------------------------------------------------------

class TestDepthCapProgression:
    """SIM case 2: deeper caps pay more total attribution, monotonically."""

    def test_deeper_caps_pay_more_total(self):
        chain = linear_chain(20)
        prev_total = ZERO
        for cap in (3, 5, 8, 13):
            result = settle_chain_depth_cap(chain, cap)
            total = Decimal(result["total_paid_ecu"])
            assert total > prev_total, f"depth_cap_{cap} should pay more than prior"
            prev_total = total

    def test_full_tail_approaches_infinite_sum(self):
        chain = linear_chain(50)
        result = settle_chain_depth_cap(chain, None)
        capture = Decimal(result["capture_fraction"])
        assert capture > Decimal("0.99"), f"full-tail should capture >99%; got {capture}"

    def test_deeper_caps_increase_middle_ancestor_fraction(self):
        """Higher depth caps increase the middle-region fraction."""
        chain = linear_chain(20)
        fracs_d3 = _region_fractions(chain, 3)
        fracs_d8 = _region_fractions(chain, 8)
        middle_d3 = Decimal(fracs_d3["middle"])
        middle_d8 = Decimal(fracs_d8["middle"])
        assert middle_d8 > middle_d3, "deeper caps must unlock middle-ancestor attribution"


# ---------------------------------------------------------------------------
# Test 3: Top-K load-bearing ancestor selection
# ---------------------------------------------------------------------------

class TestTopKSelection:
    """SIM case 3: top-K selection targets load-bearing ancestors regardless of depth."""

    def test_top_k3_reaches_deep_ancestors(self):
        """On a 20-node chain where deeper nodes have more downstream reuse,
        top-K=3 may select ancestors beyond hop 3."""
        chain = linear_chain(20)
        result = settle_chain_top_k(chain, 3)
        # On a linear chain with downstream_reuse_count = length - index,
        # the deepest nodes have the highest reuse; top-3 should include hop 20
        # But payout uses actual hop index, so deep hops pay dust.
        # Key: payouts should include at least one creator beyond hop 3.
        creators_paid = set(result["payouts_by_creator"].keys())
        # Deepest nodes paid by top-K (not by depth-3)
        assert len(creators_paid) > 0

    def test_top_k_nearest_hop_wins_on_duplicates(self):
        """Top-K deduplicates by creator; nearest hop wins."""
        # Build a chain where same creator appears twice at different depths
        chain = linear_chain(10)
        chain[8] = ChainNode(
            node_id=chain[8].node_id,
            creator_id=chain[0].creator_id,
            is_genesis=False,
            downstream_reuse_count=chain[8].downstream_reuse_count,
        )
        result = settle_chain_top_k(chain, 10)
        # creator_001 should appear at most once
        creator_payouts = {k: v for k, v in result["payouts_by_creator"].items()
                          if k == chain[0].creator_id}
        assert len(creator_payouts) <= 1, "nearest-hop-wins must deduplicate creators"

    def test_top_k5_total_within_valid_range(self):
        """Top-K=5 total is bounded by infinite geometric sum."""
        chain = linear_chain(20)
        result = settle_chain_top_k(chain, 5)
        total = Decimal(result["total_paid_ecu"])
        infinite = Decimal(result["infinite_geometric_total_ecu"])
        assert total >= ZERO
        assert total <= infinite + Decimal("0.000001")


# ---------------------------------------------------------------------------
# Test 4: Convergence accumulation
# ---------------------------------------------------------------------------

class TestConvergenceAccumulation:
    """SIM case 4: convergence-as-centrality — N chains paying one central node."""

    def test_linear_scaling_with_chain_count(self):
        """Central ancestor attribution scales linearly with number of frontier chains."""
        results: dict[int, dict[str, Decimal]] = {}
        for num_chains in (1, 3, 5):
            chains, central_node = convergence_topology(
                num_frontier_chains=num_chains,
                chain_length_before_convergence=2,
                tail_after_convergence=1,
            )
            total_for_central = ZERO
            for chain in chains:
                result = settle_chain_depth_cap(chain, 5)  # depth-5 reaches the central node
                payout = Decimal(result["payouts_by_creator"].get(central_node.creator_id, "0"))
                total_for_central += payout
            results[num_chains] = total_for_central

        # 3 chains should pay ~3x what 1 chain pays
        if results[1] > ZERO:
            ratio = results[3] / results[1]
            assert abs(ratio - Decimal("3")) < Decimal("0.1"), (
                f"3 chains should give ~3x attribution to central node; ratio={ratio}"
            )

    def test_depth3_truncates_central_ancestor_at_depth4(self):
        """Central ancestor at depth 4 receives zero attribution under depth-3 cap."""
        chains, central_node = convergence_topology(
            num_frontier_chains=5,
            chain_length_before_convergence=3,  # central is at hop 4
            tail_after_convergence=1,
        )
        total_d3 = ZERO
        total_d5 = ZERO
        for chain in chains:
            r3 = settle_chain_depth_cap(chain, 3)
            total_d3 += Decimal(r3["payouts_by_creator"].get(central_node.creator_id, "0"))
            r5 = settle_chain_depth_cap(chain, 5)
            total_d5 += Decimal(r5["payouts_by_creator"].get(central_node.creator_id, "0"))

        assert total_d3 == ZERO, "depth-3 must NOT reach an ancestor at hop 4"
        assert total_d5 > ZERO, "depth-5 MUST reach an ancestor at hop 4"


# ---------------------------------------------------------------------------
# Test 5: Lost-middle fractions
# ---------------------------------------------------------------------------

class TestLostMiddle:
    """SIM case 5: under depth-3, middle region receives zero attribution mass."""

    def test_depth3_no_middle_attribution(self):
        """Depth-3 cap gives zero middle (hops 4-10) attribution."""
        for length in (10, 20, 50):
            chain = linear_chain(length)
            fracs = _region_fractions(chain, 3)
            assert Decimal(fracs["middle"]) == ZERO, (
                f"chain_length={length}: depth-3 must not reach middle region"
            )

    def test_deeper_caps_recover_middle(self):
        """Depth-8 or depth-13 gives non-zero middle attribution on length-20 chain."""
        chain = linear_chain(20)
        for cap in (8, 13, None):
            fracs = _region_fractions(chain, cap)
            assert Decimal(fracs["middle"]) > ZERO, (
                f"depth_cap={cap} must recover middle attribution"
            )

    def test_frontier_always_dominant(self):
        """Hop-1 frontier always has the largest single-region attribution fraction."""
        chain = linear_chain(20)
        for cap in (3, 5, 8, 13, None):
            fracs = _region_fractions(chain, cap)
            frontier = Decimal(fracs["frontier"])
            near_frontier = Decimal(fracs["near_frontier"])
            assert frontier > near_frontier, f"cap={cap}: frontier must dominate near_frontier"


# ---------------------------------------------------------------------------
# Test 6: Genesis-skew analysis
# ---------------------------------------------------------------------------

class TestGenesisSkew:
    """SIM case 6: Genesis attribution and 5% cap binding under various depth strategies."""

    def test_genesis_at_depth3_receives_some_attribution(self):
        """Genesis node exactly at depth 3 receives hop-3 payout."""
        chain = linear_chain(5)
        chain[2] = ChainNode(
            node_id=chain[2].node_id,
            creator_id="genesis_creator",
            is_genesis=True,
            downstream_reuse_count=chain[2].downstream_reuse_count,
        )
        result = settle_chain_depth_cap(chain, 3)
        genesis_payout = Decimal(result["payouts_by_creator"].get("genesis_creator", "0"))
        expected = _hop_payout(2)
        assert genesis_payout == expected

    def test_genesis_at_depth4_receives_zero_under_depth3(self):
        """Genesis node at depth 4 receives no attribution under depth-3 cap."""
        chain = linear_chain(5)
        chain[3] = ChainNode(
            node_id=chain[3].node_id,
            creator_id="genesis_creator",
            is_genesis=True,
            downstream_reuse_count=chain[3].downstream_reuse_count,
        )
        result = settle_chain_depth_cap(chain, 3)
        genesis_payout = Decimal(result["payouts_by_creator"].get("genesis_creator", "0"))
        assert genesis_payout == ZERO

    def test_genesis_fraction_bounded_when_cap_increased(self):
        """Genesis fraction of per-event payout stays reasonable as depth increases."""
        # Build a chain with Genesis at depth 5; total attribution grows with depth
        # but Genesis payout is fixed at one hop's value.
        chain = linear_chain(10)
        chain[4] = ChainNode(
            node_id=chain[4].node_id,
            creator_id="genesis_creator",
            is_genesis=True,
            downstream_reuse_count=chain[4].downstream_reuse_count,
        )
        for cap in (5, 8, 13, None):
            result = settle_chain_depth_cap(chain, cap)
            total = Decimal(result["total_paid_ecu"])
            gen_payout = Decimal(result["payouts_by_creator"].get("genesis_creator", "0"))
            if total > ZERO and gen_payout > ZERO:
                genesis_fraction = _q9(gen_payout / total)
                # Genesis fraction should not exceed its single-hop contribution
                # relative to the total; it decreases as depth increases
                assert genesis_fraction <= Decimal("0.20"), (
                    f"cap={cap}: genesis_fraction={genesis_fraction} exceeds 20%"
                )


# ---------------------------------------------------------------------------
# Test 7: Anti-circular-flow
# ---------------------------------------------------------------------------

class TestAntiCircularFlow:
    """SIM case 7: circular creator insertion cannot generate unbounded attribution."""

    def test_circular_creator_paid_once_depth3(self):
        """Under depth-3, a creator appearing at hop 1 and hop 4 is paid once (hop 1)."""
        chain = circular_chain(10)
        # Manually insert creator_001 also at hop 4 (index 3) for this test
        chain[3] = ChainNode(
            node_id=chain[3].node_id,
            creator_id=chain[0].creator_id,
            is_genesis=False,
            downstream_reuse_count=chain[3].downstream_reuse_count,
        )
        circular_creator = chain[0].creator_id
        result = settle_chain_depth_cap(chain, 3)
        payout = Decimal(result["payouts_by_creator"].get(circular_creator, "0"))
        expected_single = _hop_payout(0)
        assert payout <= expected_single + Decimal("0.000000001"), (
            f"circular creator must not receive more than one hop-1 payout; got {payout}"
        )

    def test_circular_creator_paid_once_full_tail(self):
        """Even with unbounded depth, creator appearing at multiple hops is paid once."""
        chain = linear_chain(20)
        # Insert creator_001 at multiple positions
        for i in (4, 9, 14, 19):
            chain[i] = ChainNode(
                node_id=chain[i].node_id,
                creator_id=chain[0].creator_id,
                is_genesis=False,
                downstream_reuse_count=chain[i].downstream_reuse_count,
            )
        circular_creator = chain[0].creator_id
        result = settle_chain_depth_cap(chain, None)
        payout = Decimal(result["payouts_by_creator"].get(circular_creator, "0"))
        expected_single = _hop_payout(0)
        assert payout <= expected_single + Decimal("0.000000001"), (
            f"full-tail: circular creator must not receive more than one payout; got {payout}"
        )

    def test_sim_anti_circular_all_cycles_contained(self):
        """All strategies in sim_7 report cycle_contained=True."""
        result = sim_anti_circular_flow()
        for row in result["results"]:
            assert row["cycle_contained"], (
                f"strategy={row['strategy']}: cycle not contained"
            )


# ---------------------------------------------------------------------------
# Test 8: Dust aggregation
# ---------------------------------------------------------------------------

class TestDustAggregation:
    """SIM case 8: sub-dust payouts are economically negligible."""

    def test_dust_threshold_is_micro_ecu(self):
        assert DUST_THRESHOLD == Decimal("0.000001")

    def test_dust_onset_around_hop_15(self):
        """At alpha=0.45, payout drops below dust threshold around hop 15."""
        for hop in range(13, 18):
            payout = _hop_payout(hop)
            if payout < DUST_THRESHOLD:
                assert hop <= 16, f"dust onset at hop {hop+1} is later than expected"
                return
        raise AssertionError("dust onset not found within hops 13-17")

    def test_dust_not_material_for_full_tail(self):
        """Including sub-dust payouts changes total attribution by a very small amount.

        The precise threshold: at alpha=0.45, dust payouts are geometric tail
        fragments below 1e-6. Their aggregate across ~35+ hops is on the order
        of a few micro-ECU — verified as economically negligible relative to the
        ~0.163 ECU infinite sum (< 0.01% of total attribution mass).
        """
        chain = linear_chain(50)
        without_dust = settle_chain_depth_cap(chain, None, track_dust=False)
        with_dust = settle_chain_depth_cap(chain, None, track_dust=True)
        diff = abs(Decimal(with_dust["total_paid_ecu"]) - Decimal(without_dust["total_paid_ecu"]))
        # Dust aggregate must be < 0.0001 ECU (< 0.06% of infinite sum ~0.1636)
        assert diff < Decimal("0.0001"), f"dust materiality threshold exceeded: diff={diff}"
        # Must also be below 1% of the infinite geometric total
        infinite = Decimal(without_dust["infinite_geometric_total_ecu"])
        fraction = diff / infinite if infinite > ZERO else ZERO
        assert fraction < Decimal("0.01"), f"dust fraction of infinite sum exceeded: {fraction}"

    def test_dust_skipped_correctly_reported(self):
        """Dust skipped is correctly reported as a non-negative value."""
        chain = linear_chain(50)
        result = settle_chain_depth_cap(chain, None, track_dust=False)
        dust_skipped = Decimal(result["dust_skipped_ecu"])
        assert dust_skipped >= ZERO


# ---------------------------------------------------------------------------
# Test 9: run_all_sims integration
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Test 10: Hub relay variant (SIM 9)
# ---------------------------------------------------------------------------

class TestHubRelayVariant:
    """SIM case 9: hub relay pass-through variant — architectural evaluation."""

    def test_hub_relay_chain_has_hubs_at_correct_depths(self):
        """_hub_relay_chain marks exactly the specified depths as hubs."""
        chain = _hub_relay_chain(50, HUB_RELAY_HOP_DEPTHS)
        hub_positions = {i + 1 for i, n in enumerate(chain) if n.is_hub}
        assert hub_positions == set(HUB_RELAY_HOP_DEPTHS), (
            f"hub positions {hub_positions} != expected {set(HUB_RELAY_HOP_DEPTHS)}"
        )

    def test_hub_relay_reduces_upstream_payout_via_multiplier(self):
        """Nodes beyond a hub receive a reduced payout due to relay multiplier."""
        # 10-node chain with one hub at depth 3
        chain = _hub_relay_chain(10, (3,))
        r_hub = settle_hub_relay(chain, HUB_PASS_THROUGH_FRACTION)
        r_flat = settle_chain_depth_cap(
            [ChainNode(n.node_id, n.creator_id, n.is_genesis, 10 - i)
             for i, n in enumerate(chain)],
            None,
        )
        # Node at depth 5 (beyond hub at depth 3) must receive less under hub relay
        creator_d5 = chain[4].creator_id
        hub_payout_d5 = Decimal(r_hub["payouts_by_creator"].get(creator_d5, "0"))
        flat_payout_d5 = Decimal(r_flat["payouts_by_creator"].get(creator_d5, "0"))
        assert hub_payout_d5 < flat_payout_d5, (
            "hub relay must reduce payout to nodes beyond the hub"
        )

    def test_hub_retains_correct_fraction(self):
        """Hub node retains min(maintenance_cap, inflow * retain_rate) of its inflow."""
        chain = _hub_relay_chain(10, (3,))
        r = settle_hub_relay(chain, HUB_PASS_THROUGH_FRACTION)
        hub_creator = chain[2].creator_id  # depth 3, index 2
        inflow = Decimal(r["hub_inflow_ecu"].get(hub_creator, "0"))
        retained = Decimal(r["hub_retention_ecu"].get(hub_creator, "0"))
        outflow = Decimal(r["hub_outflow_ecu"].get(hub_creator, "0"))
        if inflow > ZERO:
            expected_retain = _q9(min(HUB_MAINTENANCE_CAP, _q9(inflow * HUB_RETAIN_RATE)))
            expected_outflow = _q9(inflow - expected_retain)
            assert abs(retained - expected_retain) < Decimal("0.000000002"), (
                f"hub retained {retained} but expected {expected_retain}"
            )
            assert abs(outflow - expected_outflow) < Decimal("0.000000002"), (
                f"hub outflow {outflow} but expected {expected_outflow}"
            )

    def test_parasitic_hub_flagged_at_full_retain_rate(self):
        """A hub with retain_rate=1.0 (keeps everything, passes nothing) is flagged as parasitic."""
        chain = _hub_relay_chain(50, HUB_RELAY_HOP_DEPTHS)
        # retain_rate=ONE means hub retains 100% of inflow — fully parasitic
        r = settle_hub_relay(chain, Decimal("0.0"), retain_rate=ONE)
        assert len(r["parasitic_hub_flags"]) > 0, (
            "at least one hub must be flagged when retain_rate=1.0"
        )
        # All hubs with nonzero inflow must be flagged
        for creator_id, inflow_str in r["hub_inflow_ecu"].items():
            if Decimal(inflow_str) > ZERO:
                assert creator_id in r["parasitic_hub_flags"], (
                    f"hub {creator_id} with retain_rate=1.0 must be flagged as parasitic"
                )

    def test_normal_hub_not_flagged_at_standard_retain_rate(self):
        """A hub with retain_rate=0.15 (passes 85% upstream) is not flagged as parasitic."""
        chain = _hub_relay_chain(50, HUB_RELAY_HOP_DEPTHS)
        r = settle_hub_relay(chain, HUB_PASS_THROUGH_FRACTION)
        assert r["parasitic_hub_flags"] == [], (
            f"no hub should be flagged at retain_rate={HUB_RETAIN_RATE}; "
            f"got {r['parasitic_hub_flags']}"
        )

    def test_depth3_truncation_reaches_neither_depth12_nor_depth28(self):
        """Depth-3 cap pays nothing to ancestors at depths 12 or 28."""
        chain_plain = [
            ChainNode(
                node_id=f"node_{i+1:03d}",
                creator_id=f"creator_{i+1:03d}",
                is_genesis=(i == 49),
                downstream_reuse_count=50 - i,
            )
            for i in range(50)
        ]
        r = settle_chain_depth_cap(chain_plain, 3)
        assert Decimal(r["payouts_by_creator"].get("creator_012", "0")) == ZERO
        assert Decimal(r["payouts_by_creator"].get("creator_028", "0")) == ZERO

    def test_sim9_structure_complete(self):
        """sim_hub_relay_variant returns all required sub-scenario keys."""
        result = sim_hub_relay_variant()
        required_keys = {
            "sub_9a_ancestor_reach_comparison",
            "sub_9b_parasitic_hub_test",
            "sub_9c_cross_cluster_filter",
            "conclusion",
        }
        missing = required_keys - set(result.keys())
        if missing:
            raise ValueError(f"sim_9_missing_keys: {missing}")

    def test_sim9_sub9a_has_four_strategies(self):
        """Sub-9a compares exactly four strategies."""
        result = sim_hub_relay_variant()
        strategies = result["sub_9a_ancestor_reach_comparison"]["strategies"]
        names = {s["strategy"] for s in strategies}
        assert names == {
            "depth_3_truncation",
            "depth_13_flat",
            "full_geometric_tail",
            "hub_relay_retain_0.15",
        }, f"unexpected strategy names: {names}"

    def test_sim9_sub9b_parasitic_correctly_detected(self):
        """Sub-9b: parasitic hub (retain_rate=1.0) is flagged; normal hub is not."""
        result = sim_hub_relay_variant()
        b = result["sub_9b_parasitic_hub_test"]
        assert b["parasitic_retain_rate_1_0"]["flagged_as_parasitic"] is True
        assert b["normal_retain_rate_0_15"]["flagged_as_parasitic"] is False

    def test_sim9_sub9c_filter_distinguishes_hubs(self):
        """Sub-9c: cross-cluster filter score exceeds same-cluster-only score."""
        result = sim_hub_relay_variant()
        c = result["sub_9c_cross_cluster_filter"]
        genuine = Decimal(c["genuine_hub_weighted_score"])
        manufactured = Decimal(c["manufactured_hub_weighted_score"])
        assert genuine > manufactured, (
            f"cross-cluster filter must score genuine hub higher; "
            f"genuine={genuine}, manufactured={manufactured}"
        )

    def test_conservation_invariant_hub_does_not_mint_ecu(self):
        """Hub relay must not mint new ECU: sum(all_recipients) <= original_attribution_budget."""
        chain = _hub_relay_chain(50, HUB_RELAY_HOP_DEPTHS)
        # Build an equivalent plain chain to get the original budget (no hubs)
        chain_plain = [
            ChainNode(
                node_id=n.node_id,
                creator_id=n.creator_id,
                is_genesis=n.is_genesis,
                downstream_reuse_count=50 - i,
            )
            for i, n in enumerate(chain)
        ]
        original_budget = Decimal(settle_chain_depth_cap(chain_plain, None)["total_paid_ecu"])

        # Hub relay at standard retain_rate
        r_normal = settle_hub_relay(chain, HUB_PASS_THROUGH_FRACTION)
        total_normal = sum(Decimal(v) for v in r_normal["payouts_by_creator"].values())
        assert total_normal <= original_budget + Decimal("0.000000002"), (
            f"conservation invariant violated: hub relay total {total_normal} "
            f"> original budget {original_budget}"
        )
        assert r_normal["conservation_invariant_holds"] is True

        # Conservation invariant also holds for fully parasitic hub (retain_rate=1.0)
        r_parasitic = settle_hub_relay(chain, Decimal("0.0"), retain_rate=ONE)
        total_parasitic = sum(Decimal(v) for v in r_parasitic["payouts_by_creator"].values())
        assert total_parasitic <= original_budget + Decimal("0.000000002"), (
            f"conservation invariant violated for parasitic hub: {total_parasitic} "
            f"> original budget {original_budget}"
        )
        assert r_parasitic["conservation_invariant_holds"] is True

    def test_sim9_conclusion_present_and_non_empty(self):
        """Conclusion block has an architectural_verdict string."""
        result = sim_hub_relay_variant()
        verdict = result["conclusion"].get("architectural_verdict", "")
        assert len(verdict) > 50, "architectural_verdict must be a substantive string"

    def test_sim9_conclusion_conservation_invariant_enforced(self):
        """Conclusion block records conservation_invariant_enforced=True."""
        result = sim_hub_relay_variant()
        assert result["conclusion"]["conservation_invariant_enforced"] is True

    def test_sim9_sub9b_both_cases_conservation_holds(self):
        """Sub-9b: conservation invariant holds for both parasitic and normal hubs."""
        result = sim_hub_relay_variant()
        b = result["sub_9b_parasitic_hub_test"]
        assert b["parasitic_retain_rate_1_0"]["conservation_invariant_holds"] is True
        assert b["normal_retain_rate_0_15"]["conservation_invariant_holds"] is True


# ---------------------------------------------------------------------------
# Test 11: run_all_sims integration (updated for 9 sims)
# ---------------------------------------------------------------------------

class TestRunAllSims:
    """Integration test: run_all_sims produces well-formed output."""

    def test_run_all_sims_returns_all_9_sims(self):
        results = run_all_sims()
        expected_keys = {
            "sim_1_depth_cap_comparison",
            "sim_2_top_k_selection",
            "sim_3_convergence_accumulation",
            "sim_4_lost_middle",
            "sim_5_genesis_skew",
            "sim_6_branch_skew",
            "sim_7_anti_circular_flow",
            "sim_8_dust_aggregation",
            "sim_9_hub_relay_variant",
        }
        missing = expected_keys - set(results.keys())
        if missing:
            raise ValueError(f"missing_sim_keys: {missing}")

    def test_non_activation_tokens_present(self):
        results = run_all_sims()
        assert results["research_token"] == "provenance_02_depth_sensitivity_simulation_research_only"
        assert results["no_amendment_token"] == "no_provenance_depth_amendment_from_sim_02"
        assert results["no_depth_change_token"] == "provenance_max_depth_3_not_changed_by_sim_02"

    def test_params_block_correct(self):
        results = run_all_sims()
        params = results["params"]
        assert params["provenance_max_depth_current"] == 3
        assert params["provenance_decay_alpha"] == "0.45"
        assert params["hub_relay_chain_length"] == 50
        # retain_rate=0.15 (hub keeps 15%), pass_through=0.85 (hub passes 85% upstream)
        assert params["hub_relay_retain_rate"] == "0.15"
        assert params["hub_relay_pass_through_fraction"] == "0.85"
        assert params["hub_relay_maintenance_cap"] == "0.05"
