"""
Gate test: SIM-SPECTRAL-01 commissioning verification.

Verifies:
1. The results document exists at the canonical path
2. The viability token is present
3. All six topology classes are mentioned
4. All eight requirements (R1-R8) are addressed
5. Rayleigh calibration outputs (N_batch, ε_trigger) are present as quoted values
6. The bootstrap N_bootstrap value is present
7. At least one raw numeric result from the simulation is present (anti-fabrication)

Environment variable: ILC_SIM_SPECTRAL_01_SELFTEST=1 runs selftest (no-op exit).

Governing spec: docs/specs/ilc_sim_spectral_01_commissioning_spec_v0.1.md
"""
import os
import re

SELFTEST_ENV = "ILC_SIM_SPECTRAL_01_SELFTEST"
RESULTS_PATH = "docs/research/ilc_sim_spectral_01_results_v0.1.md"

VIABILITY_TOKEN = "sim_spectral_01_lambda2_signal_viable=true"

TOPOLOGY_CLASSES = [
    "T1_random",
    "T2_panel_heavy",
    "T3_coalition_sparse",
    "T4_adversarial_sybil",
    "T5_bootstrap",
    "T6_new_node_influx",
]

REQUIREMENT_MARKERS = [
    "R1",  # Bootstrap health signal
    "R2",  # Genesis epoch floor / N_bootstrap
    "R3",  # Founding hyperedge weight anchor
    "R4",  # New-node exclusion guard
    "R5",  # Fiedler vector per-node centrality
    "R6",  # Rayleigh quotient validation
    "R7",  # N_batch and ε_trigger calibration
    "R8",  # spectral_gap reporting
]

# Rayleigh calibration carry-forward values
RAYLEIGH_MARKERS = [
    "N_batch",
    "ε_trigger",
    "N_bootstrap",
]

# Raw numeric values from actual simulation execution (anti-fabrication).
# These specific float values only come from running the script.
RAW_NUMBERS = [
    "0.0409",    # T1 λ₂ mean
    "0.0332",    # T2 λ₂ mean
    "0.0041",    # T3 λ₂ mean
    "1.0824",    # T1 CV
    "1.5725",    # T2 CV
    "3.5459",    # T3 CV
    "0.5178",    # T1 Fiedler ρ
    "0.4020",    # T2 Fiedler ρ
    "0.3391",    # ε_trigger
    "0.7500",    # bootstrap λ₂ at genesis
]


def test_selftest_guard():
    """Selftest: when ILC_SIM_SPECTRAL_01_SELFTEST=1, all tests are skipped."""
    if os.environ.get(SELFTEST_ENV) == "1":
        return  # intentional no-op


def test_results_document_exists():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    assert os.path.isfile(RESULTS_PATH), (
        f"Results document not found at {RESULTS_PATH!r}. "
        "Run tools/sim/sim_spectral_01_signal_quality.py and write the research doc."
    )


def _read_results() -> str:
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return f.read()


def test_viability_token_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert VIABILITY_TOKEN in text, (
        f"Viability token {VIABILITY_TOKEN!r} not found in {RESULTS_PATH}. "
        "The document must include the explicit viability verdict token."
    )


def test_all_topology_classes_mentioned():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for topo in TOPOLOGY_CLASSES:
        assert topo in text, (
            f"Topology class {topo!r} not mentioned in {RESULTS_PATH}. "
            "All six topology classes must be covered."
        )


def test_all_requirements_addressed():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in REQUIREMENT_MARKERS:
        assert marker in text, (
            f"Requirement {marker!r} not addressed in {RESULTS_PATH}. "
            "All eight requirements R1-R8 must be covered."
        )


def test_rayleigh_calibration_outputs_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in RAYLEIGH_MARKERS:
        assert marker in text, (
            f"Rayleigh calibration marker {marker!r} not found in {RESULTS_PATH}. "
            "The document must report N_batch, ε_trigger, and N_bootstrap as carry-forward values."
        )


def test_n_bootstrap_value_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    # N_bootstrap must be present as a quoted numeric value
    match = re.search(r"N_bootstrap\s*[=:]\s*(\d+)", text)
    assert match is not None, (
        f"N_bootstrap numeric value not found in {RESULTS_PATH}. "
        "The document must report the bootstrap node count threshold."
    )
    n_bootstrap = int(match.group(1))
    assert n_bootstrap > 0, f"N_bootstrap must be positive, got {n_bootstrap}"


def test_at_least_one_raw_number_present():
    """Anti-fabrication: at least one numeric value must match a known simulation output."""
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    found = [n for n in RAW_NUMBERS if n in text]
    assert found, (
        f"None of the expected raw simulation numbers {RAW_NUMBERS} were found "
        f"in {RESULTS_PATH}. The document must quote actual simulation output, "
        "not fabricated values."
    )


def test_fiedler_centrality_verdict_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert "NON-REDUNDANT" in text, (
        f"Fiedler centrality verdict not found in {RESULTS_PATH}. "
        "The document must include the Spearman rank correlation verdict."
    )


def test_spoofability_verdict_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert "HARD_TO_FAKE" in text or "SPOOFABLE" in text, (
        f"Spoofability verdict not found in {RESULTS_PATH}. "
        "The document must include the explicit spoofability verdict."
    )
