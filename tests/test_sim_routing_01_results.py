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


def test_hop_efficiency_finding_is_explicit() -> None:
    text = _read()
    # The primary advantage of spectral routing over random walk.
    assert "58" in text  # ~58-60% hop reduction
    assert "median" in text
    assert "1 hop" in text


def test_cycle_failure_mode_is_documented() -> None:
    text = _read()
    assert "cycle" in text.lower()
    assert "0.019" in text   # cluster center spacing that causes overlap
    assert "adjacent clusters" in text


def test_noise_penalty_values_are_present() -> None:
    text = _read()
    # N=500 noise penalty: -2.05%
    assert "2.05" in text
    # N=10000 noise penalty: -0.45%
    assert "0.45" in text


def test_key_convergence_rates_are_present() -> None:
    text = _read()
    assert "0.9775" in text   # spectral noisy N=500
    assert "0.9955" in text   # spectral noisy N=10000
    assert "0.9985" in text   # random walk N=500
    assert "0.9195" in text   # DHT naive N=500


def test_key_hop_counts_are_present() -> None:
    text = _read()
    assert "1.55" in text    # spectral noisy mean hops N=500
    assert "1.69" in text    # spectral noisy mean hops N=10000
    assert "3.93" in text    # random walk mean hops N=500


def test_h015_implementation_pattern_is_explicit() -> None:
    text = _read()
    assert "fallback" in text.lower()
    assert "random walk" in text.lower()
    assert "cycle" in text.lower()


def test_dht_finding_is_documented() -> None:
    text = _read()
    assert "DHT" in text
    assert "161" in text   # DHT cycles at N=500


def test_operational_boundaries_present() -> None:
    text = _read()
    assert "H-015" in text
    assert "H-013" in text   # sealed-sender ADR still required


def test_1d_fingerprint_scope_is_documented() -> None:
    # The simulation uses 1D fingerprints (λ₂ scalar only), not the full k-dimensional
    # spectral embedding from H-006b.  This is a conservative lower bound on performance
    # and must be documented so H-015 implementers know to use the full fingerprint.
    text = _read()
    assert "1-dimensional" in text or "1D" in text
    assert "lower bound" in text
    assert "k-dimensional" in text or "k=4" in text
