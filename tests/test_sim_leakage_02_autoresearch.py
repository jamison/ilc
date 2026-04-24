import unittest

from tools.testbed.sim_leakage_autoresearch import BASELINE_MECHANISM, MECHANISM_FAMILIES, run_simulation


class TestSimLeakage02Autoresearch(unittest.TestCase):
    def test_baseline_produces_full_recall(self) -> None:
        result = run_simulation(BASELINE_MECHANISM, {}, seed=7)
        self.assertEqual(result["recall_a"], 1.0)
        self.assertEqual(result["recall_b"], 1.0)
        self.assertEqual(result["recall_c"], 1.0)

    def test_mixing_large_pool_and_rounds_reduce_variant_a(self) -> None:
        weak = run_simulation(
            "mixing",
            {
                "mix_pool_size": 2,
                "num_rounds": 1,
                "delay_epochs": 0,
                "forward_fraction": 0.5,
                "shuffle_strategy": "uniform",
            },
            seed=13,
        )
        strong = run_simulation(
            "mixing",
            {
                "mix_pool_size": 32,
                "num_rounds": 5,
                "delay_epochs": 2,
                "forward_fraction": 1.0,
                "shuffle_strategy": "uniform",
            },
            seed=13,
        )
        self.assertLess(strong["recall_a"], weak["recall_a"])

    def test_k_anonymity_higher_k_reduces_variant_b(self) -> None:
        low_k = run_simulation(
            "k_anonymity",
            {
                "k_value": 2,
                "partition_strategy": "random",
                "rebatch_interval_epochs": 1,
                "carry_over_policy": "hold",
            },
            seed=17,
        )
        high_k = run_simulation(
            "k_anonymity",
            {
                "k_value": 20,
                "partition_strategy": "random",
                "rebatch_interval_epochs": 1,
                "carry_over_policy": "hold",
            },
            seed=17,
        )
        self.assertLess(high_k["recall_b"], low_k["recall_b"])

    def test_sealed_sender_more_relays_reduce_variant_a(self) -> None:
        direct = run_simulation(
            "sealed_sender",
            {
                "relay_hop_count": 0,
                "routing_entropy": 0.0,
                "relay_selection_strategy": "random",
                "balance_surface_protected": False,
            },
            seed=19,
        )
        relayed = run_simulation(
            "sealed_sender",
            {
                "relay_hop_count": 3,
                "routing_entropy": 1.0,
                "relay_selection_strategy": "random",
                "balance_surface_protected": False,
            },
            seed=19,
        )
        self.assertLess(relayed["recall_a"], direct["recall_a"])

    def test_sealed_sender_without_balance_protection_keeps_variant_b_high(self) -> None:
        result = run_simulation(
            "sealed_sender",
            {
                "relay_hop_count": 3,
                "routing_entropy": 1.0,
                "relay_selection_strategy": "random",
                "balance_surface_protected": False,
            },
            seed=23,
        )
        self.assertGreaterEqual(result["recall_b"], 0.9)

    def test_same_seed_is_deterministic(self) -> None:
        params = {
            "mix_pool_size": 16,
            "num_rounds": 3,
            "delay_epochs": 1,
            "forward_fraction": 0.85,
            "shuffle_strategy": "uniform",
        }
        first = run_simulation("mixing", params, seed=29)
        second = run_simulation("mixing", params, seed=29)
        self.assertEqual(first, second)

    def test_family_smoke_samples_cover_supported_ranges(self) -> None:
        samples = {
            "mixing": {
                "mix_pool_size": 24,
                "num_rounds": 2,
                "delay_epochs": 4,
                "forward_fraction": 0.7,
                "shuffle_strategy": "weighted_by_volume",
            },
            "k_anonymity": {
                "k_value": 15,
                "partition_strategy": "epoch_aligned",
                "rebatch_interval_epochs": 5,
                "carry_over_policy": "drop",
            },
            "sealed_sender": {
                "relay_hop_count": 2,
                "routing_entropy": 0.75,
                "relay_selection_strategy": "contributor_keyed",
                "balance_surface_protected": True,
            },
        }
        for family in MECHANISM_FAMILIES:
            result = run_simulation(family, samples[family], seed=31)
            self.assertIn("recall_a", result)
            self.assertIn("recall_b", result)
            self.assertIn("recall_c", result)

    def test_complexity_scores_remain_bounded(self) -> None:
        cases = [
            (
                "mixing",
                {
                    "mix_pool_size": 32,
                    "num_rounds": 5,
                    "delay_epochs": 4,
                    "forward_fraction": 1.0,
                    "shuffle_strategy": "uniform",
                },
            ),
            (
                "k_anonymity",
                {
                    "k_value": 20,
                    "partition_strategy": "random",
                    "rebatch_interval_epochs": 5,
                    "carry_over_policy": "hold",
                },
            ),
            (
                "sealed_sender",
                {
                    "relay_hop_count": 3,
                    "routing_entropy": 1.0,
                    "relay_selection_strategy": "random",
                    "balance_surface_protected": True,
                },
            ),
        ]
        for family, params in cases:
            result = run_simulation(family, params, seed=37)
            self.assertGreaterEqual(result["complexity_score"], 0.0)
            self.assertLessEqual(result["complexity_score"], 1.0)


    def test_calibration_mixing_weak_pool_not_too_private(self) -> None:
        # pool=2 provides very limited anonymity; recall_a must stay above 0.30
        result = run_simulation(
            "mixing",
            {
                "mix_pool_size": 2,
                "num_rounds": 1,
                "delay_epochs": 0,
                "forward_fraction": 1.0,
                "shuffle_strategy": "uniform",
                "amount_distribution": "uniform",
            },
            seed=42,
        )
        self.assertGreater(result["recall_a"], 0.30)

    def test_calibration_mixing_strong_fixed_amounts_low_recall(self) -> None:
        # pool=32, rounds=5, fixed amounts: attacker has minimal signal
        result = run_simulation(
            "mixing",
            {
                "mix_pool_size": 32,
                "num_rounds": 5,
                "delay_epochs": 4,
                "forward_fraction": 1.0,
                "shuffle_strategy": "uniform",
                "amount_distribution": "fixed",
            },
            seed=42,
        )
        self.assertLess(result["recall_a"], 0.40)

    def test_calibration_sealed_sender_unprotected_keeps_variant_b_very_high(self) -> None:
        # sealed-sender without balance protection: recall_b must be > 0.80
        result = run_simulation(
            "sealed_sender",
            {
                "relay_hop_count": 3,
                "routing_entropy": 1.0,
                "relay_selection_strategy": "random",
                "balance_surface_protected": False,
                "amount_distribution": "uniform",
            },
            seed=42,
        )
        self.assertGreater(result["recall_b"], 0.80)


if __name__ == "__main__":
    unittest.main()
