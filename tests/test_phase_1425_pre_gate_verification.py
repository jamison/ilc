"""Phase 1425 — Pre-Gate Verification tests.

Proves:
- All 7 blocking conditions are now GateConditionStatus.MET
- evaluate_jury_activation_gate() returns verdict="PASS" and blocking_not_met=[]
- PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED is False after Phase 1427
- All 7 Phase 1425 evidence tokens are present in the gate source
- Historical NOT_MET tokens are still present in phase_tokens (archived evidence)
- Gate module version token reflects Phase 1425
- No import random in gate source
- gate_authorized is True after Phase 1427
- production_activated remains False until concrete execution surfaces activate
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GATE_MODULE = REPO / "ilc_core/epistemic/jury_activation_gate.py"

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from ilc_core.epistemic.jury_activation_gate import (
    JURY_ACTIVATION_GATE_VERSION,
    JURY_ACTIVATION_GATE_VERSION_1425,
    PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED,
    GateConditionStatus,
    JuryActivationGateReport,
    evaluate_jury_activation_gate,
)

# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_gate_module_exists():
    assert GATE_MODULE.exists(), "jury_activation_gate.py must exist"


# ---------------------------------------------------------------------------
# Phase 1425 required tokens in module source
# ---------------------------------------------------------------------------

_PHASE_1425_TOKENS = [
    "pre_gate_verification_complete_phase_1425",
    "vrf_verifier_implemented_condition_met_verified_phase_1425",
    "capproof_cdl_ratified_condition_met_verified_phase_1425",
    "maintenance_lottery_cdl_ratified_condition_met_verified_phase_1425",
    "jury_incentive_cdl_ratified_condition_met_verified_phase_1425",
    "review_lane_wiring_complete_condition_met_verified_phase_1425",
    "anti_capture_diversity_verified_condition_met_verified_phase_1425",
    "copyright_counsel_disposition_condition_met_verified_phase_1425",
    "all_seven_blocking_conditions_met_verified_phase_1425",
    "j008_gate_verdict_still_incomplete_pending_production_go_phase_1425",
]


@pytest.mark.parametrize("token", _PHASE_1425_TOKENS)
def test_module_contains_phase_1425_token(token):
    src = GATE_MODULE.read_text(encoding="utf-8")
    assert token in src, f"jury_activation_gate.py must contain Phase 1425 token: {token}"


# ---------------------------------------------------------------------------
# Safety flag
# ---------------------------------------------------------------------------


def test_production_not_authorized_constant_flipped_by_phase_1427():
    """PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED was flipped by Phase 1427."""
    assert PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED is False


def test_version_token_reflects_phase_1425():
    assert "jury_activation_gate_phase_1425" in JURY_ACTIVATION_GATE_VERSION_1425


def test_original_version_token_still_present():
    assert "jury_activation_gate_phase_j008" in JURY_ACTIVATION_GATE_VERSION


# ---------------------------------------------------------------------------
# Gate report fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def report() -> JuryActivationGateReport:
    return evaluate_jury_activation_gate()


# ---------------------------------------------------------------------------
# Verdict and blocking_not_met
# ---------------------------------------------------------------------------


def test_verdict_is_pass(report):
    """After Phase 1425 patch: all blocking conditions are MET -> verdict=PASS."""
    assert report.verdict == "PASS"


def test_blocking_not_met_is_empty(report):
    """After Phase 1425 patch: no blocking conditions remain unmet."""
    assert report.blocking_not_met == []


def test_blocking_not_met_length_zero(report):
    assert len(report.blocking_not_met) == 0


def test_gate_authorized_true_but_production_surfaces_default_off_after_phase_1427(report):
    assert report.gate_authorized is True
    assert report.production_activated is False
    assert report.execution_surfaces_activated is False


# ---------------------------------------------------------------------------
# All 7 previously-blocking conditions are now MET
# ---------------------------------------------------------------------------

_SEVEN_BLOCKING_CONDITIONS = [
    "VRF_VERIFIER_IMPLEMENTED",
    "CAPPROOF_CDL_RATIFIED",
    "MAINTENANCE_LOTTERY_CDL_RATIFIED",
    "JURY_INCENTIVE_CDL_RATIFIED",
    "REVIEW_LANE_WIRING_COMPLETE",
    "ANTI_CAPTURE_DIVERSITY_VERIFIED",
    "COPYRIGHT_COUNSEL_DISPOSITION",
]


@pytest.mark.parametrize("condition_id", _SEVEN_BLOCKING_CONDITIONS)
def test_blocking_condition_now_met(condition_id, report):
    """Each of the 7 previously-blocking conditions must now be MET."""
    cond = next(c for c in report.conditions if c.condition_id == condition_id)
    assert cond.status == GateConditionStatus.MET, (
        f"{condition_id} must be MET after Phase 1425 patch"
    )
    assert cond.blocking is True


def test_all_ten_conditions_met(report):
    """All 10 gate conditions must be MET after Phase 1425 patch."""
    not_met = [c.condition_id for c in report.conditions if c.status == GateConditionStatus.NOT_MET]
    assert not_met == [], f"All conditions must be MET; still NOT_MET: {not_met}"


def test_ten_conditions_total(report):
    assert len(report.conditions) == 10


# ---------------------------------------------------------------------------
# Evidence tokens present in phase_tokens
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("token", _PHASE_1425_TOKENS)
def test_phase_1425_token_in_report_phase_tokens(token, report):
    assert token in report.phase_tokens, (
        f"Phase 1425 token must be in report.phase_tokens: {token}"
    )


# ---------------------------------------------------------------------------
# Historical NOT_MET tokens still present in phase_tokens (archived evidence)
# ---------------------------------------------------------------------------

_HISTORICAL_NOT_MET_TOKENS = [
    "vrf_verifier_required_not_implemented_phase_j008",
    "capproof_cdl_not_opened_phase_j008",
    "maintenance_lottery_cdl_not_opened_phase_j008",
    "jury_incentive_cdl_not_ratified_phase_j008",
    "j008_gate_verdict_incomplete",
]


@pytest.mark.parametrize("token", _HISTORICAL_NOT_MET_TOKENS)
def test_historical_not_met_token_still_in_phase_tokens(token, report):
    """Historical NOT_MET tokens must be retained in phase_tokens as archived evidence."""
    assert token in report.phase_tokens, (
        f"historical NOT_MET token must remain in phase_tokens: {token}"
    )


@pytest.mark.parametrize("token", _HISTORICAL_NOT_MET_TOKENS)
def test_historical_not_met_token_still_in_source(token):
    """Historical NOT_MET tokens must remain in module source as archived evidence."""
    src = GATE_MODULE.read_text(encoding="utf-8")
    assert token in src, f"historical NOT_MET token must remain in source: {token}"


# ---------------------------------------------------------------------------
# Evidence refs contain Phase 1425 verification tokens
# ---------------------------------------------------------------------------


def test_vrf_evidence_ref_contains_phase_1411_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "VRF_VERIFIER_IMPLEMENTED")
    assert "vrf_proof_verifier_implemented_phase_1411" in cond.evidence_ref


def test_vrf_evidence_ref_contains_phase_1412_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "VRF_VERIFIER_IMPLEMENTED")
    assert "vrf_verifier_integrated_jury_assignment_phase_1412" in cond.evidence_ref


def test_capproof_evidence_ref_contains_cdl_092_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "CAPPROOF_CDL_RATIFIED")
    assert "cdl_092_ratified_phase_1405" in cond.evidence_ref


def test_maintenance_lottery_evidence_ref_contains_cdl_093_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "MAINTENANCE_LOTTERY_CDL_RATIFIED")
    assert "cdl_093_ratified_phase_1408" in cond.evidence_ref


def test_jury_incentive_evidence_ref_contains_cdl_091_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "JURY_INCENTIVE_CDL_RATIFIED")
    assert "cdl_091_ratified_phase_1400" in cond.evidence_ref


def test_review_lane_evidence_ref_contains_phase_1417_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "REVIEW_LANE_WIRING_COMPLETE")
    assert "review_lane_wiring_complete_phase_1417" in cond.evidence_ref


def test_anti_capture_evidence_ref_contains_phase_1419_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "ANTI_CAPTURE_DIVERSITY_VERIFIED")
    assert "anti_capture_diversity_verified_phase_1419" in cond.evidence_ref


def test_copyright_evidence_ref_contains_phase_1420_token(report):
    cond = next(c for c in report.conditions if c.condition_id == "COPYRIGHT_COUNSEL_DISPOSITION")
    assert "copyright_counsel_disposition_complete_phase_1420" in cond.evidence_ref


# ---------------------------------------------------------------------------
# Routing strings updated
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("condition_id", _SEVEN_BLOCKING_CONDITIONS)
def test_blocking_condition_routing_says_already_met(condition_id, report):
    cond = next(c for c in report.conditions if c.condition_id == condition_id)
    assert "ALREADY MET" in cond.routing, (
        f"{condition_id} routing must say 'ALREADY MET' after Phase 1425 patch"
    )


# ---------------------------------------------------------------------------
# Security / coding standards
# ---------------------------------------------------------------------------


def test_no_random_import():
    src = GATE_MODULE.read_text(encoding="utf-8")
    assert "import random" not in src


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_gate_is_deterministic():
    r1 = evaluate_jury_activation_gate()
    r2 = evaluate_jury_activation_gate()
    assert r1.verdict == r2.verdict
    assert r1.blocking_not_met == r2.blocking_not_met
    assert len(r1.conditions) == len(r2.conditions)
