"""
Gate test: SIM-BEACON-01 research artifact verification.
"""

from pathlib import Path


RESULTS_PATH = Path("docs/research/ilc_sim_beacon_01_results_v0.1.md")
SCRIPT_PATH = Path("tools/sim/sim_beacon_01_privacy_calibration.py")


def _read() -> str:
    return RESULTS_PATH.read_text(encoding="utf-8")


def test_results_and_script_exist() -> None:
    assert RESULTS_PATH.is_file()
    assert SCRIPT_PATH.is_file()


def test_required_tokens_present() -> None:
    text = _read()
    assert "`sim_beacon_01_noise_sigma_recommended=0.005`" in text
    assert "`sim_beacon_01_detection_threshold_theta=0.010`" in text
    assert "`sim_beacon_01_beacon_frequency_recommended_epochs=4`" in text
    assert "`run_h009_sim_beacon_01_verdict=pass`" in text


def test_results_cover_both_scales_and_raw_risk() -> None:
    text = _read()
    assert "`N=500`" in text
    assert "`N=10000`" in text
    assert "0.970" in text
    assert "0.999" in text


def test_selected_candidate_metrics_are_present() -> None:
    text = _read()
    for marker in ("0.792", "0.822", "0.196", "0.194"):
        assert marker in text


def test_rejected_candidates_and_residual_risk_are_explicit() -> None:
    text = _read()
    assert "`sigma = 0.006`, `theta = 0.010`" in text
    assert "`sigma = 0.006`, `theta = 0.012`" in text
    assert "`sigma = 0.007`, `theta = 0.012`" in text
    assert "DP noise alone" in text
    assert "sealed sender" in text
