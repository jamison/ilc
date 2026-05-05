import hashlib
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    CDL_085_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import EDGE_MINT_PHI_BOUND, PROVENANCE_DECAY_ALPHA


ROOT = Path(__file__).resolve().parents[1]
SELFTEST_MODE = os.environ.get("ILC_PHASE_1199_GATE_SELFTEST") == "1"
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_COVERAGE_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1199_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_token() -> None:
    text = _read("docs/specs/ilc_phase_1191_1199_sequence_lock_v0.1.md")
    assert "window_1191_1199_sequence_lock_committed" in text


def test_cat2_roadmap_v1_0_token() -> None:
    text = _read("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
    assert "launch_roadmap_v1_0_published_phase_1192" in text
    assert "Window 1191-1199" in text


def test_cat3_v02_signing_deferred_without_release_envelope() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in status
    assert not (ROOT / "out/genesis_atlas_v0_2_release_envelope_1193.json").exists()


def test_cat4_cdl_086_opening_recorded_and_not_ratified() -> None:
    register = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    opening = _read("docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md")
    assert "CDL-086" in register
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in register
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in opening
    cdl_086_line = next(line for line in register.splitlines() if line.startswith("| CDL-086 |"))
    assert "| open |" in cdl_086_line
    assert "ratified_phase:" not in cdl_086_line


def test_cat5_tier3_runtime_linkage_scope_token() -> None:
    text = _read("docs/specs/ilc_tier3_runtime_linkage_implementation_plan_1195_v0.1.md")
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in text


def test_cat6_persistent_rate_limiter_scope_token() -> None:
    text = _read("docs/specs/ilc_persistent_rate_limiter_scope_1196_v0.1.md")
    assert "persistent_rate_limiter_scope_committed_phase_1196" in text


def test_cat7_canon_bundle_repair_token_and_testing_snapshot() -> None:
    text = _read("docs/specs/ilc_canon_bundle_signing_repair_1197_v0.1.md")
    assert "canon_bundle_signing_repair_pass_phase_1197" in text
    assert "tests/fixtures/canon_bundle_valid_export_v0_1_snapshot.json" in text
    assert "USE_TESTING_CANON_EXPORT_SNAPSHOT = True" in text


def test_cat8_canon_bundle_production_validation_path_unchanged() -> None:
    validator = _read("ilc_core/ledger/canon_export_bundle_validate.py")
    assert "validate_canon_export_v0_1(export_doc)" in validator
    assert "USE_TESTING_CANON_EXPORT_SNAPSHOT" not in validator
    for path in ROOT.joinpath("ilc_core").rglob("*.py"):
        assert "USE_TESTING_CANON_EXPORT_SNAPSHOT" not in path.read_text(encoding="utf-8")


def test_cat9_capsule_v545_exists_and_supersedes() -> None:
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.45.md")
    assert "capsule_v5_45_supersedes_v5_44" in text
    assert "canon_bundle_signing_repair_pass_phase_1197" in text


def test_cat10_coherence_report_1198_exists() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1198_v0.1.md")
    assert "coherence_report_1198_verdict=pass" in text


def test_cat11_signed_genesis_v01_hash_recorded() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1191_1199_sequence_lock_v0.1.md")
    capsule = _read("docs/specs/ilc_antigravity_context_capsule_v5.45.md")
    assert ROOT_HASH in sequence_lock
    assert ROOT_HASH in capsule


def test_cat12_compile_coverage_diagnostic_immutable_hash() -> None:
    payload = (ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == COMPILE_COVERAGE_SHA256


def test_cat13_phi_bound_runtime_still_decimal_active() -> None:
    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")
    assert CDL_085_DEPENDENCY == "cdl_085_werner_phi_bound_ratified_1185.v0.1"
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1185.v0.6"


def test_cat14_provenance_decay_alpha_unchanged() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


def test_cat15_no_public_launch_claim_in_closure_handoff() -> None:
    text = _read("docs/specs/ilc_window_1191_1199_handoff_1199_v0.1.md")
    assert "No public launch claim" in text
    assert "Public launch claim remains forbidden" in text


def test_cat16_no_unauthorized_signing_or_release_key() -> None:
    text = _read("docs/specs/ilc_window_1191_1199_handoff_1199_v0.1.md")
    assert "No release envelope was produced" in text
    assert "no release-key action" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_cat17_handoff_sections_and_tokens() -> None:
    text = _read("docs/specs/ilc_window_1191_1199_handoff_1199_v0.1.md")
    for heading in [
        "## 1. Window Identity and Closure Basis",
        "## 2. Closure Verdict Summary",
        "## 3. Constitutional and Runtime Frontier",
        "## 4. RC2 Gate Status",
        "## 5. Genesis Atlas and Signing Frontier",
        "## 6. Canon Bundle Signing Repair Boundary",
        "## 7. Carry-Forward Items",
        "## 8. Recommended Window 1200+ Entry Order",
    ]:
        assert heading in text
    assert "window_1191_1199_closed_phase_1199" in text
    assert "window_1191_1199_closure_gate_verdict=pass" in text


def test_cat18_planning_index_closure_state() -> None:
    text = _read("docs/PLANNING_INDEX.md")
    assert "Window 1191-1199 is CLOSED" in text
    assert "ilc_window_1191_1199_handoff_1199_v0.1.md" in text


def test_cat19_status_records_phase_1199() -> None:
    text = _read("docs/phases/STATUS.md")
    assert "## Phase 1199" in text
    assert "window_1191_1199_closed_phase_1199" in text
    assert "window_1191_1199_closure_gate_verdict=pass" in text
