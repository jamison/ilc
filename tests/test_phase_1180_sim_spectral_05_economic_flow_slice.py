import json
from pathlib import Path

from ilc_core.types import EDGE_MINT_PHI_BOUND


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "docs/sims/sim_spectral_05/economic_flow_slice_program_1180_v0.1.md"
RUN = ROOT / "out/sim_spectral_05_economic_flow_slice_run_1180.json"
DISPOSITION = ROOT / "docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md"
RUNTIME_BINDING = ROOT / "docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md"


def test_phase_1180_economic_flow_program_spec_exists():
    assert PROGRAM.exists()


def test_phase_1180_economic_flow_run_artifact_passes():
    data = json.loads(RUN.read_text(encoding="utf-8"))
    assert data["verdict"] == "sim_spectral_05_economic_flow_slice_pass"
    assert data["runtime_binding_slice_prerequisite"] == "sim_spectral_05_runtime_binding_slice_pass"
    assert data["carry_forward_resolved"] == "sim_spectral_05_economic_flow_slice_deferred_window_1176"
    assert data["test_a_sybil_suppression_rate"] == 1.0
    assert data["test_b_legitimate_preservation_rate"] == 1.0
    assert data["test_c_over_suppression_cases"] == 0


def test_phase_1180_economic_flow_disposition_contains_tokens():
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "sim_spectral_05_economic_flow_slice_pass" in text
    assert "sim_spectral_05_economic_flow_slice_deferred_window_1176_resolved" in text


def test_phase_1180_runtime_binding_prerequisite():
    text = RUNTIME_BINDING.read_text(encoding="utf-8")
    assert "sim_spectral_05_runtime_binding_slice_pass" in text


def test_phase_1180_runtime_phi_bound_not_activated():
    assert EDGE_MINT_PHI_BOUND is None
