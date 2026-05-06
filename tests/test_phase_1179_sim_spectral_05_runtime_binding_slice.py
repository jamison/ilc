import json
from pathlib import Path

from ilc_core.types import EDGE_MINT_PHI_BOUND


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "docs/sims/sim_spectral_05/runtime_binding_slice_program_1179_v0.1.md"
RUN = ROOT / "out/sim_spectral_05_runtime_binding_slice_run_1179.json"
DISPOSITION = ROOT / "docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md"


def test_phase_1179_runtime_binding_program_spec_exists():
    assert PROGRAM.exists()


def test_phase_1179_runtime_binding_run_artifact_passes():
    data = json.loads(RUN.read_text(encoding="utf-8"))
    assert data["verdict"] == "sim_spectral_05_runtime_binding_slice_pass"
    assert data["carry_forward_resolved"] == "sim_spectral_05_runtime_binding_slice_deferred_window_1176"
    assert data["phi_bound_candidate"] == "0.60"
    assert data["s1_acceptance_rate"] == 1.0
    assert data["s3_rejection_rate"] == 1.0


def test_phase_1179_runtime_binding_disposition_contains_tokens():
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "sim_spectral_05_runtime_binding_slice_pass" in text
    assert "sim_spectral_05_runtime_binding_slice_deferred_window_1176_resolved" in text


def test_phase_1179_cdl_085_prelock_prerequisite():
    text = PRELOCK.read_text(encoding="utf-8")
    assert "cdl_085_prelock_committed_phase_1177" in text
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in text


def test_phase_1179_runtime_phi_bound_not_activated():
    # Originally asserted None (pre-CDL-085). CDL-085 ratified at Phase 1185
    # set EDGE_MINT_PHI_BOUND = Decimal("0.60"). Updated to match current runtime.
    from decimal import Decimal
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")
