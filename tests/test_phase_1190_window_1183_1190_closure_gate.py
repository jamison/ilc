import hashlib
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    CDL_085_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
)


ROOT = Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1190_GATE_SELFTEST") == "1"
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_COVERAGE_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1190_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_document_and_token() -> None:
    text = _read("docs/specs/ilc_phase_1183_1190_sequence_lock_v0.1.md")
    assert "window_1183_1190_sequence_lock_committed" in text


def test_cat2_prelock_hardening_test_file_exists() -> None:
    assert (ROOT / "tests/test_phase_1184_cdl_085_prelock_hardening.py").exists()


def test_cat3_cdl_085_ratification_evidence_exists() -> None:
    assert (ROOT / "docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md").exists()


def test_cat4_cdl_085_ratified_in_register() -> None:
    text = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    assert "cdl_085_ratified_phase_1185" in text
    assert "ratified_phase: 1185" in text


def test_cat5_phi_bound_is_decimal_and_active() -> None:
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")


def test_cat6_cdl_085_dependency_token() -> None:
    assert CDL_085_DEPENDENCY == "cdl_085_werner_phi_bound_ratified_1185.v0.1"


def test_cat7_runtime_version_updated() -> None:
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1185.v0.6"


def test_cat8_v02_signing_routed() -> None:
    status = _read("docs/phases/STATUS.md")
    signed = "genesis_atlas_v0_2_signed_phase_1186" in status
    deferred = "v0_2_signing_ceremony_deferred_pending_signing_authorization" in status
    assert signed or deferred
    if not signed:
        assert not (ROOT / "out/genesis_atlas_v0_2_release_envelope_1186.json").exists()


def test_cat9_gossip_slice_routed() -> None:
    text = _read("docs/sims/sim_spectral_05/gossip_slice_disposition_1187_v0.1.md")
    assert "sim_spectral_05_gossip_slice_pass" in text
    assert "sim_spectral_05_gossip_slice_deferred_window_1176_resolved" in text


def test_cat10_public_launch_packaging_blocker_scoping_done() -> None:
    text = _read("docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md")
    assert "cdl_001_genesis_blocker_scoping_committed_phase_1188" in text
    assert "Roadmap Label Drift Correction" in text
    assert "fresh CDL number" in text


def test_cat11_coherence_report_1189_exists() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1189_v0.1.md")
    assert "coherence_report_1189_verdict=pass" in text


def test_cat12_capsule_v544_exists_and_supersedes() -> None:
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.44.md")
    assert "capsule_v5_44_supersedes_v5_43" in text
    assert "cdl_085_ratified_phase_1185" in text


def test_cat13_signed_genesis_v01_hash_in_sequence_lock() -> None:
    text = _read("docs/specs/ilc_phase_1183_1190_sequence_lock_v0.1.md")
    assert ROOT_HASH in text


def test_cat14_compile_coverage_diagnostic_immutable_hash() -> None:
    payload = (ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == COMPILE_COVERAGE_SHA256


def test_cat15_provenance_decay_alpha_unchanged() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


def test_cat16_provenance_max_depth_unchanged() -> None:
    assert PROVENANCE_MAX_DEPTH == 3


def test_cat17_handoff_sections_and_tokens() -> None:
    text = _read("docs/specs/ilc_window_1183_1190_handoff_1190_v0.1.md")
    for heading in [
        "## 1. Window Identity and Closure Basis",
        "## 2. Closure Verdict Summary",
        "## 3. Constitutional and Runtime Frontier",
        "## 4. SIM-SPECTRAL-05 Observer Slice Closure",
        "## 5. Genesis Atlas and Signing Frontier",
        "## 6. Public-Launch Packaging Blocker Routing",
        "## 7. Carry-Forward Items",
    ]:
        assert heading in text
    assert "window_1183_1190_closed_phase_1190" in text
    assert "window_1183_1190_closure_gate_verdict=pass" in text
