"""Phase 1398 / J-008 — Production Jury Activation Gate tests.

Proves:
- module and gate spec document exist
- required phase tokens present in module source
- required tokens present in gate spec document
- evaluate_jury_activation_gate() returns a report
- gate verdict is INCOMPLETE (multiple blocking conditions NOT_MET)
- all expected condition IDs are present
- J007_HARNESS_PASS and firewall conditions are MET
- all other blocking conditions are NOT_MET
- blocking_not_met list names exactly the unmet blocking conditions
- production_activated is False in all reports
- PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED is True
- no import random in source
- gate spec records non-authorizations
- package exports
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GATE_MODULE = REPO / "ilc_core/epistemic/jury_activation_gate.py"
GATE_SPEC = REPO / "docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md"

# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_gate_module_exists():
    assert GATE_MODULE.exists(), "jury_activation_gate.py must exist"


def test_gate_spec_exists():
    assert GATE_SPEC.exists(), "ilc_production_jury_activation_gate_j008_v0.1.md must exist"


# ---------------------------------------------------------------------------
# Required tokens in module source
# ---------------------------------------------------------------------------

_MODULE_TOKENS = [
    "production_jury_activation_gate_defined_phase_j008",
    "production_jury_activation_not_authorized_phase_j008",
    "j008_gate_verdict_incomplete",
    "vrf_verifier_required_not_implemented_phase_j008",
    "capproof_cdl_not_opened_phase_j008",
    "maintenance_lottery_cdl_not_opened_phase_j008",
    "jury_incentive_cdl_not_ratified_phase_j008",
    "j007_harness_condition_met_phase_j008",
    "public_economics_firewall_condition_met_phase_j008",
]


@pytest.mark.parametrize("token", _MODULE_TOKENS)
def test_module_contains_token(token):
    src = GATE_MODULE.read_text(encoding="utf-8")
    assert token in src, f"jury_activation_gate.py must contain token: {token}"


# ---------------------------------------------------------------------------
# Required tokens in gate spec document
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("token", _MODULE_TOKENS)
def test_spec_contains_token(token):
    text = GATE_SPEC.read_text(encoding="utf-8")
    assert token in text, f"gate spec must contain token: {token}"


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from ilc_core.epistemic.jury_activation_gate import (
    JURY_ACTIVATION_GATE_VERSION,
    PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED,
    GateCondition,
    GateConditionStatus,
    JuryActivationGateReport,
    evaluate_jury_activation_gate,
)


def test_production_not_authorized_constant():
    assert PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED is True


def test_version_token_present():
    assert "jury_activation_gate_phase_j008" in JURY_ACTIVATION_GATE_VERSION


# ---------------------------------------------------------------------------
# Gate report structure
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def report() -> JuryActivationGateReport:
    return evaluate_jury_activation_gate()


def test_report_is_gate_report(report):
    assert isinstance(report, JuryActivationGateReport)


def test_verdict_is_incomplete(report):
    """Gate must be INCOMPLETE — multiple blocking conditions are NOT_MET."""
    assert report.verdict == "INCOMPLETE"


def test_production_activated_false(report):
    assert report.production_activated is False


def test_phase_tokens_in_report(report):
    for token in _MODULE_TOKENS:
        assert token in report.phase_tokens, (
            f"gate report must carry token: {token}"
        )


# ---------------------------------------------------------------------------
# Condition IDs
# ---------------------------------------------------------------------------

_EXPECTED_CONDITION_IDS = {
    "J007_HARNESS_PASS",
    "VRF_VERIFIER_IMPLEMENTED",
    "CAPPROOF_CDL_RATIFIED",
    "MAINTENANCE_LOTTERY_CDL_RATIFIED",
    "JURY_INCENTIVE_CDL_RATIFIED",
    "REVIEW_LANE_WIRING_COMPLETE",
    "ANTI_CAPTURE_DIVERSITY_VERIFIED",
    "COPYRIGHT_COUNSEL_DISPOSITION",
    "PUBLIC_ECONOMICS_FIREWALL",
    "NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM",
}


def test_all_condition_ids_present(report):
    actual = {c.condition_id for c in report.conditions}
    assert actual == _EXPECTED_CONDITION_IDS


def test_ten_conditions(report):
    assert len(report.conditions) == 10


# ---------------------------------------------------------------------------
# MET conditions
# ---------------------------------------------------------------------------

_EXPECTED_MET = {
    "J007_HARNESS_PASS",
    "PUBLIC_ECONOMICS_FIREWALL",
    "NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM",
}


def test_met_conditions(report):
    actual_met = {c.condition_id for c in report.conditions if c.status == GateConditionStatus.MET}
    assert actual_met == _EXPECTED_MET


# ---------------------------------------------------------------------------
# NOT_MET / blocking conditions
# ---------------------------------------------------------------------------

_EXPECTED_BLOCKING_NOT_MET = {
    "VRF_VERIFIER_IMPLEMENTED",
    "CAPPROOF_CDL_RATIFIED",
    "MAINTENANCE_LOTTERY_CDL_RATIFIED",
    "JURY_INCENTIVE_CDL_RATIFIED",
    "REVIEW_LANE_WIRING_COMPLETE",
    "ANTI_CAPTURE_DIVERSITY_VERIFIED",
    "COPYRIGHT_COUNSEL_DISPOSITION",
}


def test_blocking_not_met_set(report):
    assert set(report.blocking_not_met) == _EXPECTED_BLOCKING_NOT_MET


def test_seven_blocking_not_met(report):
    assert len(report.blocking_not_met) == 7


def test_non_blocking_conditions_not_in_blocking_not_met(report):
    """PUBLIC_ECONOMICS_FIREWALL and NO_EPOCH_HASH are non-blocking; must not appear."""
    assert "PUBLIC_ECONOMICS_FIREWALL" not in report.blocking_not_met
    assert "NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM" not in report.blocking_not_met


def test_vrf_condition_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "VRF_VERIFIER_IMPLEMENTED")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_capproof_condition_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "CAPPROOF_CDL_RATIFIED")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_maintenance_lottery_condition_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "MAINTENANCE_LOTTERY_CDL_RATIFIED")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_jury_incentive_condition_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "JURY_INCENTIVE_CDL_RATIFIED")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_review_lane_wiring_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "REVIEW_LANE_WIRING_COMPLETE")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_anti_capture_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "ANTI_CAPTURE_DIVERSITY_VERIFIED")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


def test_copyright_counsel_not_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "COPYRIGHT_COUNSEL_DISPOSITION")
    assert cond.status == GateConditionStatus.NOT_MET
    assert cond.blocking is True


# ---------------------------------------------------------------------------
# Non-blocking conditions are MET
# ---------------------------------------------------------------------------

def test_public_economics_firewall_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "PUBLIC_ECONOMICS_FIREWALL")
    assert cond.status == GateConditionStatus.MET
    assert cond.blocking is False


def test_no_epoch_hash_claim_met(report):
    cond = next(c for c in report.conditions if c.condition_id == "NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM")
    assert cond.status == GateConditionStatus.MET
    assert cond.blocking is False


# ---------------------------------------------------------------------------
# All conditions have non-empty evidence_ref and routing
# ---------------------------------------------------------------------------

def test_all_conditions_have_evidence_ref(report):
    for cond in report.conditions:
        assert cond.evidence_ref, f"condition {cond.condition_id} must have evidence_ref"


def test_all_conditions_have_routing(report):
    for cond in report.conditions:
        assert cond.routing, f"condition {cond.condition_id} must have routing"


# ---------------------------------------------------------------------------
# Gate spec records non-authorizations
# ---------------------------------------------------------------------------

def test_spec_records_non_authorizations():
    text = GATE_SPEC.read_text(encoding="utf-8")
    assert "Non-Authorizations" in text or "no production jury assignment" in text.lower()


def test_spec_records_incomplete_verdict():
    text = GATE_SPEC.read_text(encoding="utf-8")
    assert "INCOMPLETE" in text


def test_spec_references_vrf_not_implemented():
    text = GATE_SPEC.read_text(encoding="utf-8")
    assert "vrf_proof_verifier_not_implemented" in text


# ---------------------------------------------------------------------------
# Determinism — same result on repeated calls
# ---------------------------------------------------------------------------

def test_gate_is_deterministic():
    r1 = evaluate_jury_activation_gate()
    r2 = evaluate_jury_activation_gate()
    assert r1.verdict == r2.verdict
    assert set(r1.blocking_not_met) == set(r2.blocking_not_met)
    assert len(r1.conditions) == len(r2.conditions)


# ---------------------------------------------------------------------------
# Security / coding standards
# ---------------------------------------------------------------------------

def test_no_random_import():
    src = GATE_MODULE.read_text(encoding="utf-8")
    assert "import random" not in src


# ---------------------------------------------------------------------------
# Package exports
# ---------------------------------------------------------------------------

def test_package_exports_evaluate_function():
    from ilc_core.epistemic import evaluate_jury_activation_gate as fn
    assert callable(fn)


def test_package_exports_gate_condition_status():
    from ilc_core.epistemic import GateConditionStatus as GCS
    assert GCS.MET is not None
    assert GCS.NOT_MET is not None


def test_package_exports_production_flag():
    from ilc_core.epistemic import PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED as flag
    assert flag is True
