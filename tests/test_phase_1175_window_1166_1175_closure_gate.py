import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1175_GATE_SELFTEST") == "1"
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_COVERAGE_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _load_json(path: str) -> dict:
    with (ROOT / path).open(encoding="utf-8") as f:
        return json.load(f)


def test_cat0_selftest_env_required():
    if not SELFTEST_MODE:
        pytest.skip("closure gate selftest requires ILC_PHASE_1175_GATE_SELFTEST=1")


def test_cat1_sequence_lock_document_exists():
    assert (ROOT / "docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md").exists()


def test_cat2_sequence_lock_token_present():
    text = _read("docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md")
    assert "window_1166_1175_sequence_lock_committed" in text


def test_cat3_adr_0037_draft_exists():
    assert (ROOT / "docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md").exists()


def test_cat4_adr_0037_draft_token_present():
    text = _read("docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md")
    assert "adr_0037_lineage_contract_draft_committed_phase_1167" in text


def test_cat5_sim_spectral_05_program_exists():
    assert (ROOT / "docs/sims/sim_spectral_05/program.md").exists()


def test_cat6_sim_spectral_05_program_token_present():
    text = _read("docs/sims/sim_spectral_05/program.md")
    assert "sim_spectral_05_program_spec_committed_phase_1168" in text


def test_cat7_track_a_summary_and_sybil_topology():
    data = _load_json("out/sim_spectral_05_track_a_calibration_summary.json")
    assert data["s3_topology"] == "synthetic_sybil_cluster"
    assert data["track_a_verdict"] == "track_a_pass"


def test_cat8_track_a_token_present():
    data = _load_json("out/sim_spectral_05_track_a_calibration_summary.json")
    assert data["gate_token"] == "sim_spectral_05_track_a_completed_phase_1169"


def test_cat9_branchial_projection_tool_exists():
    assert (ROOT / "tools/build_genesis_branchial_claim_projection.py").exists()


def test_cat10_branchial_projection_artifact_valid():
    data = _load_json("out/genesis_branchial_claim_projection_v0.1.json")
    assert data["projection_type"] == "branchial_claim_state"
    assert data["vertex_schema"] == "(claim_id, version, status)"
    assert data["vertex_count"] == 88
    assert data["edge_count"] == 248


def test_cat11_branchial_projection_token_present():
    data = _load_json("out/genesis_branchial_claim_projection_v0.1.json")
    assert data["token"] == "sim_spectral_05_track_b_projection_built_phase_1170"


def test_cat12_track_b_summary_gate_pass():
    data = _load_json("out/sim_spectral_05_track_b_run_summary.json")
    assert data["track_b_verdict"] == "track_b_pass"
    assert data["gate_verdict"] == "sim_spectral_05_gate_pass"
    assert data["s1_convergence_rate"]["mean"] == 0.85
    assert data["s3_convergence_rate"]["mean"] == 0.25
    assert data["separation"]["mean_delta"] == 0.6
    assert data["separation"]["verdict"] == "separated"


def test_cat13_combined_disposition_gate_tokens_present():
    text = _read("docs/sims/sim_spectral_05/disposition_1171_v0.1.md")
    assert "sim_spectral_05_gate_pass" in text
    assert "track_a_pass" in text
    assert "track_b_pass" in text


def test_cat14_cdl_085_opened_not_ratified():
    opening = _read("docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md")
    register = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    assert "**Status:** OPEN" in opening
    assert "cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass" in opening
    assert "| CDL-085 |" in register
    assert "| open |" in register
    assert "opened_phase: 1172" in register


def test_cat15_adr_0037_acceptance_record():
    review = _read("docs/adr/adr_0037_acceptance_review_1173_v0.1.md")
    adr = _read("docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md")
    assert "**Verdict:** **ACCEPTED**" in review
    assert "adr_0037_accepted_phase_1173" in review
    assert "**Status:** Accepted" in adr


def test_cat16_adr_0036_acceptance_record():
    review = _read("docs/adr/adr_0036_acceptance_review_1173_v0.1.md")
    adr = _read("docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md")
    assert "**Verdict:** **ACCEPTED**" in review
    assert "adr_0036_accepted_phase_1173" in review
    assert "**Status:** Accepted" in adr


def test_cat17_signed_v0_1_star_map_unchanged():
    data = _load_json("out/genesis_core_star_map_v0.1.json")
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.42.md")
    assert len(data["nodes"]) == 32
    assert len(data["edges"]) == 55
    assert ROOT_HASH in capsule


def test_cat18_compile_coverage_diagnostic_immutable_hash():
    payload = (ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == COMPILE_COVERAGE_SHA256


def test_cat19_runtime_chain_unchanged():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)


def test_cat20_capsule_v5_42_present():
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.42.md")
    assert "capsule_v5_42_supersedes_v5_41" in text
    assert "Phase 1175 closure gate remains pending" in text


def test_cat21_handoff_sections_and_tokens():
    text = _read("docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md")
    for heading in [
        "## 1. Window Identity and Closure Basis",
        "## 2. Inputs and Closure Inheritance",
        "## 3. Closure Verdict Summary",
        "## 4. Carry-Forward Items and Residual Blockers",
        "## 5. Next-Window Entry Criteria and Routing",
        "## 6. MemPalace Refresh Disposition",
    ]:
        assert heading in text
    assert "window_1166_1175_closed_phase_1175" in text
    assert "window_1166_1175_closure_gate_verdict=pass" in text
