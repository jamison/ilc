import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import EDGE_MINT_PHI_BOUND, PROVENANCE_DECAY_ALPHA


ROOT = Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1182_GATE_SELFTEST") == "1"
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_COVERAGE_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _load_json(path: str) -> dict:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_cat0_selftest_env_required():
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1182_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_document_exists():
    assert (ROOT / "docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md").exists()


def test_cat2_sequence_lock_token_present():
    text = _read("docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md")
    assert "window_1176_1182_sequence_lock_committed" in text


def test_cat3_cdl_085_prelock_spec_exists():
    assert (ROOT / "docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md").exists()


def test_cat4_cdl_085_prelock_token_present():
    text = _read("docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md")
    assert "cdl_085_prelock_committed_phase_1177" in text


def test_cat5_cdl_085_prelock_contains_all_q_resolutions():
    text = _read("docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md")
    for q in ["Q1 Resolution", "Q2 Resolution", "Q3 Resolution", "Q4 Resolution", "Q5 Resolution"]:
        assert q in text


def test_cat6_phi_bound_candidate_not_activated_in_runtime():
    runtime_types = _read("ilc_core/types.py")
    assert EDGE_MINT_PHI_BOUND is None
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' not in runtime_types
    assert 'EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")' not in runtime_types


def test_cat7_v02_signing_routed():
    status = _read("docs/phases/STATUS.md")
    signed = "genesis_atlas_v0_2_signed_phase_1178" in status
    deferred = "v0_2_signing_ceremony_deferred_pending_signing_authorization" in status
    assert signed or deferred
    if not signed:
        assert not (ROOT / "out/genesis_atlas_v0_2_release_envelope_1178.json").exists()


def test_cat8_runtime_binding_slice_routed():
    disposition = _read("docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md")
    assert "sim_spectral_05_runtime_binding_slice_pass" in disposition
    assert "sim_spectral_05_runtime_binding_slice_deferred_window_1176_resolved" in disposition


def test_cat9_economic_flow_slice_routed():
    disposition = _read("docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md")
    assert "sim_spectral_05_economic_flow_slice_pass" in disposition
    assert "sim_spectral_05_economic_flow_slice_deferred_window_1176_resolved" in disposition


def test_cat10_coherence_report_1181_exists():
    text = _read("docs/specs/ilc_integration_coherence_report_1181_v0.1.md")
    assert "coherence_report_1181_verdict=pass" in text


def test_cat11_capsule_v543_exists_and_supersedes():
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.43.md")
    assert "capsule_v5_43_supersedes_v5_42" in text
    assert "Phase 1182 closure gate pending" in text


def test_cat12_signed_genesis_v01_unchanged():
    star_map = _load_json("out/genesis_core_star_map_v0.1.json")
    sequence_lock = _read("docs/specs/ilc_phase_1176_1182_sequence_lock_v0.1.md")
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert ROOT_HASH in sequence_lock


def test_cat13_compile_coverage_diagnostic_immutable_hash():
    payload = (ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == COMPILE_COVERAGE_SHA256


def test_cat14_runtime_chain_unchanged():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)


def test_cat15_handoff_sections_and_tokens():
    text = _read("docs/specs/ilc_window_1176_1182_handoff_1182_v0.1.md")
    for heading in [
        "## 1. Window Identity and Closure Basis",
        "## 2. Inputs and Closure Inheritance",
        "## 3. Closure Verdict Summary",
        "## 4. Carry-Forward Items and Residual Blockers",
        "## 5. Next-Window Entry Criteria and Routing",
        "## 6. MemPalace Refresh Disposition",
    ]:
        assert heading in text
    assert "window_1176_1182_closed_phase_1182" in text
    assert "window_1176_1182_closure_gate_verdict=pass" in text
