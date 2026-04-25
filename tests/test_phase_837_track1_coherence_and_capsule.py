"""Phase 837 — Track 1 pre-deployment lane coherence report and capsule v5.16 tests."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COHERENCE = REPO_ROOT / "docs" / "specs" / "ilc_integration_coherence_report_837_v0.1.md"
CAPSULE = REPO_ROOT / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.16.md"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Coherence report
# ---------------------------------------------------------------------------

def test_coherence_report_exists() -> None:
    assert COHERENCE.exists()


def test_coherence_publication_token() -> None:
    assert "track1_pre_deployment_lane_837_coherence_published" in _read(COHERENCE)


def test_coherence_records_prerequisites_satisfied() -> None:
    assert "entry_conditions_human_gate_code_prerequisites_satisfied" in _read(COHERENCE)


def test_coherence_lists_all_four_track1_phases() -> None:
    text = _read(COHERENCE)
    for phase in ("830", "835", "836"):
        assert phase in text


def test_coherence_records_human_gate_not_pulled() -> None:
    assert "first_validator_deployment_human_gate_not_yet_pulled" in _read(COHERENCE)


def test_coherence_records_row5_deferred() -> None:
    assert "row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate" in _read(COHERENCE)


def test_coherence_names_operator_only_items() -> None:
    text = _read(COHERENCE)
    for item in ("TLS material", "genesis state", "rollback plan", "Human authorization"):
        assert item in text


def test_coherence_hard_constraint_compliance() -> None:
    text = _read(COHERENCE)
    for constraint in (
        "did **not** pull the first-validator human gate",
        "did **not** wire live settlement submission ingress",
        "did **not** mutate any CDL row",
        "did **not** claim Row-5 runtime closure",
    ):
        assert constraint in text


# ---------------------------------------------------------------------------
# Capsule v5.16
# ---------------------------------------------------------------------------

def test_capsule_exists() -> None:
    assert CAPSULE.exists()


def test_capsule_supersedes_v5_15() -> None:
    assert "capsule_v5_16_supersedes_v5_15" in _read(CAPSULE)


def test_capsule_records_prerequisites_satisfied() -> None:
    assert "entry_conditions_human_gate_code_prerequisites_satisfied" in _read(CAPSULE)


def test_capsule_records_human_gate_not_pulled() -> None:
    assert "first_validator_deployment_human_gate_not_yet_pulled" in _read(CAPSULE)


def test_capsule_preserves_row5_spec_closed() -> None:
    text = _read(CAPSULE)
    assert "row5_spec_closed_runtime_pending_preserved" in text
    assert "row5_runtime_closed" not in text


def test_capsule_no_cdl_mutation_token() -> None:
    assert "no_cdl_mutation_in_track1_lane_830_837" in _read(CAPSULE)


def test_capsule_records_sim_leakage_deferred() -> None:
    assert "row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate" in _read(CAPSULE)


def test_capsule_names_carry_forward_operator_actions() -> None:
    text = _read(CAPSULE)
    assert "Pull the first-validator human gate" in text
    assert "live three-machine smoke proof" in text
    assert "Authorize Rust privacy lane integration gate" in text
