import json
from decimal import Decimal
from pathlib import Path


PROGRAM = Path("docs/sims/sim_spectral_05/gossip_slice_program_1187_v0.1.md")
RUN_ARTIFACT = Path("out/sim_spectral_05_gossip_slice_run_1187.json")
DISPOSITION = Path("docs/sims/sim_spectral_05/gossip_slice_disposition_1187_v0.1.md")


def test_gossip_program_spec_exists() -> None:
    assert PROGRAM.exists()


def test_gossip_run_artifact() -> None:
    data = json.loads(RUN_ARTIFACT.read_text(encoding="utf-8"))
    assert data["verdict"] == "sim_spectral_05_gossip_slice_pass"
    assert (
        data["carry_forward_resolved"]
        == "sim_spectral_05_gossip_slice_deferred_window_1176"
    )
    assert data["phi_bound_source"] == "ilc_core.types.EDGE_MINT_PHI_BOUND"
    assert data["three_slice_framework_complete"] is True


def test_gossip_disposition_exists() -> None:
    content = DISPOSITION.read_text(encoding="utf-8")
    assert "sim_spectral_05_gossip_slice_pass" in content
    assert "sim_spectral_05_three_slice_observer_framework_complete" in content
    assert "sim_spectral_05_gossip_slice_deferred_window_1176_resolved" in content


def test_phi_bound_live_constant() -> None:
    from ilc_core.types import EDGE_MINT_PHI_BOUND

    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")


def test_gossip_slice_decisions_match_phi_bound() -> None:
    from ilc_core.types import EDGE_MINT_PHI_BOUND

    data = json.loads(RUN_ARTIFACT.read_text(encoding="utf-8"))
    assert Decimal(data["phi_bound_active"]) == EDGE_MINT_PHI_BOUND
    assert data["test_a_s1_acceptance_rate"] == 1.0
    assert data["test_b_s3_rejection_rate"] == 1.0
    assert data["test_c_cross_contamination_cases"] == 0
