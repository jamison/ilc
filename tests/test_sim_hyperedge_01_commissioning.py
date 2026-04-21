"""
Gate test: SIM-HYPEREDGE-01 commissioning verification.

Verifies:
1. The results document exists at the canonical path
2. The recommended W(e) token is present
3. All four topology class names are mentioned
4. The incremental update validation result is present
5. At least one raw numeric result from the simulation is present (anti-fabrication)

Environment variable: ILC_SIM_HYPEREDGE_01_SELFTEST=1 runs selftest (no-op exit).

Governing spec: docs/specs/ilc_sim_hyperedge_01_commissioning_spec_v0.1.md
"""
import os
import re

SELFTEST_ENV = "ILC_SIM_HYPEREDGE_01_SELFTEST"
RESULTS_PATH = "docs/research/ilc_sim_hyperedge_01_results_v0.1.md"

EXPECTED_TOKEN = "sim_hyperedge_01_recommended_w_e=stake_harmonic_mean"

TOPOLOGY_CLASSES = [
    "T1_random",
    "T2_panel_heavy",
    "T3_coalition_sparse",
    "T4_adversarial_sybil",
]

# At least one raw numeric result quoted from the actual simulation run.
# These are specific float values that only come from executing the script.
RAW_NUMBERS = [
    "2.5683",   # harmonic mean_CV from verdict table
    "2.6819",   # sum mean_CV
    "4.4983",   # product mean_CV
    "3.84e-17", # max Frobenius error
    "38.25",    # incremental speedup
]

INCREMENTAL_MARKERS = [
    "Frobenius",
    "exact",
    "speedup",
]


def test_selftest_guard():
    """Selftest: when ILC_SIM_HYPEREDGE_01_SELFTEST=1, all tests are skipped."""
    if os.environ.get(SELFTEST_ENV) == "1":
        return  # intentional no-op


def test_results_document_exists():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    assert os.path.isfile(RESULTS_PATH), (
        f"Results document not found at {RESULTS_PATH!r}. "
        "Run tools/sim/sim_hyperedge_01_w_e_calibration.py and write the research doc."
    )


def _read_results() -> str:
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return f.read()


def test_recommended_w_e_token_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert EXPECTED_TOKEN in text, (
        f"Commissioning token {EXPECTED_TOKEN!r} not found in {RESULTS_PATH}. "
        "The document must include the explicit recommendation token."
    )


def test_all_topology_classes_mentioned():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for topo in TOPOLOGY_CLASSES:
        assert topo in text, (
            f"Topology class {topo!r} not mentioned in {RESULTS_PATH}. "
            "All four topology classes must be covered."
        )


def test_incremental_update_validation_present():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in INCREMENTAL_MARKERS:
        assert marker in text, (
            f"Incremental update validation marker {marker!r} not found "
            f"in {RESULTS_PATH}. The document must report Frobenius error, "
            "exactness, and speedup."
        )


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


def test_stake_harmonic_mean_identified_as_recommended():
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    # Must explicitly call out stake_harmonic_mean as the recommendation.
    assert "stake_harmonic_mean" in text, (
        f"'stake_harmonic_mean' not found in {RESULTS_PATH}."
    )
    # Must not recommend stake_product (disqualified candidate).
    assert "stake_product" not in re.search(
        r"sim_hyperedge_01_recommended_w_e=(\S+)", text
    ).group(0).replace("sim_hyperedge_01_recommended_w_e=", ""), (
        "Token must not recommend stake_product."
    )
