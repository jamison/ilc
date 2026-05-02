"""
Phase 1137: Coherence report + capsule v5.38 evidence tests
"""

import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
CAPSULE = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.38.md"
COHERENCE = REPO_ROOT / "docs/specs/ilc_integration_coherence_report_1137_v0.1.md"
DISPOSITION = REPO_ROOT / "docs/sims/sim_spectral_02/run02_disposition_1136_v0.1.md"
STAR_MAP = REPO_ROOT / "out/genesis_core_star_map_v0.1.json"
RUNTIME = REPO_ROOT / "ilc_core/economics/epoch_attribution_settle_runtime.py"
TYPES = REPO_ROOT / "ilc_core/types.py"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# C01 — capsule exists and carries required opening tokens
def test_c01_capsule_v5_38_exists_with_opening_tokens():
    text = _read(CAPSULE)
    for token in (
        "capsule_v5_38_supersedes_v5_37",
        "window_1130_1138_sim_spectral_02_complete",
        "sim_spectral_02_disposition_phase_1136",
    ):
        assert token in text, f"Missing capsule token: {token}"


# C02 — capsule supersedes v5.37 (exact supersedes line)
def test_c02_capsule_supersedes_v5_37():
    text = _read(CAPSULE)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.37.md" in text


# C03 — coherence report exists and verdict token present
def test_c03_coherence_report_exists_with_verdict_token():
    text = _read(COHERENCE)
    assert "coherence_report_1137_verdict=pass" in text


# C04 — CDL-084 constants are unchanged: alpha in types.py, version in runtime
def test_c04_cdl_084_constants_unchanged():
    types_text = _read(TYPES)
    assert 'Decimal("0.45")' in types_text, "PROVENANCE_DECAY_ALPHA must be Decimal('0.45') in types.py"
    runtime_text = _read(RUNTIME)
    assert "epoch_attribution_settle_runtime_1129_fix1.v0.5" in runtime_text, (
        "Runtime version must remain epoch_attribution_settle_runtime_1129_fix1.v0.5"
    )


# C05 — SIM-SPECTRAL-02 Run 02 disposition file exists
def test_c05_run02_disposition_file_exists():
    assert DISPOSITION.exists(), f"Missing: {DISPOSITION}"


# C06 — capsule §5 records SIM-SPECTRAL-02 as COMPLETE with Scenario B advisory
def test_c06_capsule_records_sim_spectral_02_outcome():
    text = _read(CAPSULE)
    assert "Scenario B advisory" in text or "sim_spectral_02_scenario_b_advisory" in text, (
        "Capsule §5 must record SIM-SPECTRAL-02 Scenario B advisory outcome"
    )


# C07 — capsule §6 new test count matches window additions (87 new tests)
def test_c07_capsule_records_window_test_additions():
    text = _read(CAPSULE)
    assert "87 tests" in text, "Capsule §6 must record 87 new tests added in Window 1130-1138"


# C08 — capsule records genesis atlas obligations (Tier-1, GENESIS-COMPILE-01)
def test_c08_capsule_records_genesis_atlas_obligations():
    text = _read(CAPSULE)
    assert "Genesis Atlas Tier-1" in text, "Capsule §5 must record Atlas Tier-1 obligation"
    assert "GENESIS-COMPILE-01" in text, "Capsule must reference GENESIS-COMPILE-01"
