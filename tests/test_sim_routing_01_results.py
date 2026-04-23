"""
Gate test: SIM-ROUTING-01 research artifact verification.
"""

from pathlib import Path


RESULTS_PATH = Path("docs/research/ilc_sim_routing_01_results_v0.1.md")
SCRIPT_PATH = Path("tools/sim/sim_routing_01_spectral_convergence.py")


def _read() -> str:
    return RESULTS_PATH.read_text(encoding="utf-8")


def test_results_and_script_exist() -> None:
    assert RESULTS_PATH.is_file()
    assert SCRIPT_PATH.is_file()


def test_required_verdict_token_present() -> None:
    assert "`run_h014_sim_routing_01_verdict=pass`" in _read()


def test_thresholds_are_declared_before_results() -> None:
    text = _read()
    assert text.index("## 2. Up-Front Pass Criteria") < text.index("## 5. Results by Topology")
    assert "Healthy greedy convergence floor" in text
    assert "`0.85`" in text
    assert "Partition-near greedy convergence floor" in text
    assert "`0.60`" in text
    assert "Two-phase convergence floor" in text
    assert "`0.80`" in text


def test_four_h005_topology_classes_are_present() -> None:
    text = _read()
    for token in (
        "`T1_random`",
        "`T2_panel_heavy`",
        "`T3_coalition_sparse`",
        "`T4_partition_near`",
    ):
        assert token in text
    assert "partition-risk floor" in text
    assert "`theta_floor = 0.001`" in text


def test_hop_distribution_percentiles_present() -> None:
    text = _read()
    assert "P5" in text
    assert "P50" in text
    assert "P95" in text
    assert "`1.54`" in text
    assert "`4.49`" in text


def test_comparison_algorithms_present() -> None:
    text = _read()
    for token in ("`spectral_greedy`", "`spectral_two_phase`", "`random_walk`", "`dht_naive`"):
        assert token in text


def test_failure_mode_taxonomy_present() -> None:
    text = _read()
    assert "## 6. Failure Mode Taxonomy" in text
    assert "`cycle`" in text
    assert "`max_hops`" in text
    assert "`no_peers`" in text
    assert "eliminated by the two-phase fallback" in text


def test_h015_unblock_assessment_is_bounded() -> None:
    text = _read()
    assert "H-015 is unblocked" in text
    assert "immediate random-walk fallback" in text
    assert "may not activate spectral beacon gossip" in text
    assert "may not mutate any CDL row" in text


def test_script_locks_topology_count_and_seed() -> None:
    script = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "TOPOLOGIES" in script
    assert "T4_partition_near" in script
    assert "SEED: int = 42" in script
    assert "json.dumps(output, indent=2, sort_keys=True)" in script
