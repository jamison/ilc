"""Phase 1398 / J-008 — Production Jury Activation Gate.

Defines and evaluates the conditions required before production jury
assignment, production reviewer payment, production public ingestion, or
any live ECU distribution via a jury/maintenance lane may be activated.

This is a gate-definition and gate-evaluation module. Phase 1427 authorizes
the production jury activation machinery by flipping the explicit guard, but
this module does NOT execute jury assignment, reviewer payment, ingestion,
ledger writes, wallet writes, treasury writes, or graph writes by itself.

Phase 1398 initial tokens (historical — do NOT remove):
  production_jury_activation_gate_defined_phase_j008
  production_jury_activation_not_authorized_phase_j008
  j008_gate_verdict_incomplete
  vrf_verifier_required_not_implemented_phase_j008
  capproof_cdl_not_opened_phase_j008
  maintenance_lottery_cdl_not_opened_phase_j008
  jury_incentive_cdl_not_ratified_phase_j008
  j007_harness_condition_met_phase_j008
  public_economics_firewall_condition_met_phase_j008

Phase 1425 pre-gate verification tokens (conditions patched to MET):
  pre_gate_verification_complete_phase_1425
  vrf_verifier_implemented_condition_met_verified_phase_1425
  capproof_cdl_ratified_condition_met_verified_phase_1425
  maintenance_lottery_cdl_ratified_condition_met_verified_phase_1425
  jury_incentive_cdl_ratified_condition_met_verified_phase_1425
  review_lane_wiring_complete_condition_met_verified_phase_1425
  anti_capture_diversity_verified_condition_met_verified_phase_1425
  copyright_counsel_disposition_condition_met_verified_phase_1425
  all_seven_blocking_conditions_met_verified_phase_1425
  j008_gate_verdict_still_incomplete_pending_production_go_phase_1425

Phase 1427 gate re-run tokens:
  production_jury_activation_gate_pass_phase_1427
  j008_gate_rerun_phase_1427
  production_jury_activation_authorized_phase_1427
  all_10_conditions_met_phase_1427

SENSITIVE: This module defines the production activation boundary. Phase 1427
has issued the explicit production GO and re-run the gate. Public RC
publication, signing, repository push, and package upload remain separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

JURY_ACTIVATION_GATE_VERSION = "jury_activation_gate_phase_j008.v0.1"
JURY_ACTIVATION_GATE_VERSION_1425 = "jury_activation_gate_phase_1425.v0.1"
JURY_ACTIVATION_GATE_VERSION_1427 = "jury_activation_gate_phase_1427.v0.1"
ADR_0040_DEPENDENCY = "jury_eligibility_assignment_adr_accepted_phase_j002"
J007_DEPENDENCY = "shadow_public_ingestion_harness_phase_j007"

# Phase 1398 tokens — historical, must remain in source
_TOKEN_GATE_DEFINED = "production_jury_activation_gate_defined_phase_j008"
_TOKEN_NOT_AUTHORIZED = "production_jury_activation_not_authorized_phase_j008"
_TOKEN_INCOMPLETE = "j008_gate_verdict_incomplete"
_TOKEN_VRF_NOT_IMPL = "vrf_verifier_required_not_implemented_phase_j008"
_TOKEN_CAPPROOF_NOT_OPENED = "capproof_cdl_not_opened_phase_j008"
_TOKEN_LOTTERY_NOT_OPENED = "maintenance_lottery_cdl_not_opened_phase_j008"
_TOKEN_INCENTIVE_NOT_RATIFIED = "jury_incentive_cdl_not_ratified_phase_j008"
_TOKEN_J007_MET = "j007_harness_condition_met_phase_j008"
_TOKEN_FIREWALL_MET = "public_economics_firewall_condition_met_phase_j008"

# Phase 1425 tokens — all 7 blocking conditions verified MET
_TOKEN_PRE_GATE_COMPLETE = "pre_gate_verification_complete_phase_1425"
_TOKEN_VRF_MET_1425 = "vrf_verifier_implemented_condition_met_verified_phase_1425"
_TOKEN_CAPPROOF_MET_1425 = "capproof_cdl_ratified_condition_met_verified_phase_1425"
_TOKEN_LOTTERY_MET_1425 = "maintenance_lottery_cdl_ratified_condition_met_verified_phase_1425"
_TOKEN_INCENTIVE_MET_1425 = "jury_incentive_cdl_ratified_condition_met_verified_phase_1425"
_TOKEN_REVIEW_LANE_MET_1425 = "review_lane_wiring_complete_condition_met_verified_phase_1425"
_TOKEN_ANTI_CAPTURE_MET_1425 = "anti_capture_diversity_verified_condition_met_verified_phase_1425"
_TOKEN_COPYRIGHT_MET_1425 = "copyright_counsel_disposition_condition_met_verified_phase_1425"
_TOKEN_ALL_SEVEN_MET = "all_seven_blocking_conditions_met_verified_phase_1425"
_TOKEN_GATE_STILL_INCOMPLETE = "j008_gate_verdict_still_incomplete_pending_production_go_phase_1425"

# Phase 1427 tokens - production jury activation boundary authorized
_TOKEN_GATE_PASS_1427 = "production_jury_activation_gate_pass_phase_1427"
_TOKEN_GATE_RERUN_1427 = "j008_gate_rerun_phase_1427"
_TOKEN_PRODUCTION_AUTHORIZED_1427 = "production_jury_activation_authorized_phase_1427"
_TOKEN_ALL_TEN_MET_1427 = "all_10_conditions_met_phase_1427"

# Safety gate: Phase 1427 flips this only after all blocking conditions are MET.
PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED: bool = False


class GateConditionStatus(str, Enum):
    MET = "MET"
    NOT_MET = "NOT_MET"


@dataclass(frozen=True)
class GateCondition:
    """A single condition in the production jury activation gate."""

    condition_id: str
    description: str
    status: GateConditionStatus
    evidence_ref: str          # file, token, or commit that proves/disproves
    blocking: bool             # if True, gate cannot pass without this condition
    routing: str               # what must happen to satisfy this condition


@dataclass(frozen=True)
class JuryActivationGateReport:
    """Point-in-time evaluation of the production jury activation gate."""

    conditions: List[GateCondition]
    verdict: str                           # "PASS" | "INCOMPLETE"
    blocking_not_met: List[str]            # condition_ids of blocking conditions not yet met
    phase_tokens: List[str]
    gate_authorized: bool                  # True after PASS and explicit Phase 1427 GO
    production_activated: bool             # True only after execution surfaces are flipped live
    execution_surfaces_activated: bool     # Assignment/payment/ingestion runtime flags are live
    runtime_version: str


def evaluate_jury_activation_gate() -> JuryActivationGateReport:
    """Evaluate all production jury activation gate conditions.

    Returns a JuryActivationGateReport documenting each condition's current
    status (MET or NOT_MET), the overall verdict, and future routing for
    unmet conditions.

    The verdict is INCOMPLETE as long as any blocking condition is NOT_MET.
    A PASS verdict records all blocking conditions MET. gate_authorized
    additionally requires the explicit Phase 1427 production GO guard flip.
    production_activated remains false until later phases flip the concrete
    assignment, review-lane, payment, ingestion, and value-path runtime flags.
    """
    conditions: List[GateCondition] = [

        # -------------------------------------------------------------------
        # Condition 1: J-007 shadow harness has passed (MET)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="J007_HARNESS_PASS",
            description=(
                "J-007 shadow public-ingestion harness has been implemented and "
                "produces a PASS verdict (≥1 valid T0.5 submission + ≥1 task "
                "reaching audited state)"
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "ilc_core/epistemic/ingestion_shadow_harness.py; "
                "tests/test_phase_1397_j007_shadow_public_ingestion_harness.py "
                "(55 tests passing); token: shadow_public_ingestion_harness_phase_j007"
            ),
            blocking=True,
            routing="ALREADY MET — no further action required",
        ),

        # -------------------------------------------------------------------
        # Condition 2: VRF proof verifier implemented (MET — Phase 1411/1412)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="VRF_VERIFIER_IMPLEMENTED",
            description=(
                "A VRF proof verifier is implemented for production high-value "
                "reviewer assignment. Epoch-hash shadow assignment (J-006) must "
                "NOT be marketed as production privacy or production unpredictability."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "ilc_core/epistemic/vrf_proof_verifier.py; "
                "token: vrf_proof_verifier_implemented_phase_1411; "
                "ADR-0042 accepted: vrf_proof_verifier_adr_accepted_phase_1410; "
                "ilc_core/epistemic/jury_assignment_runtime.py; "
                "token: vrf_verifier_integrated_jury_assignment_phase_1412; "
                "tests/test_phase_1413_vrf_integration.py (14 tests); "
                "Phase 1425 verified: vrf_verifier_implemented_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: vrf_verifier_implemented_phase_1411, "
                "vrf_verifier_integrated_jury_assignment_phase_1412"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 3: CapProof CDL ratified (MET — Phase 1405)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="CAPPROOF_CDL_RATIFIED",
            description=(
                "A CapProof CDL has been opened and ratified, covering: probe "
                "content-addressing (GEMMProbe, InferProbe, GraphProbe, "
                "BandwidthProbe, DeterminismProbe), Capability Vector signing "
                "contract, ±15% ECU-pricing-band enforcement, Genesis baseline "
                "transition rule, and VRF-based spot-recheck mechanism."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "docs/specs/ilc_cdl_092_capproof_ratification_evidence_1405_v0.1.md; "
                "token: cdl_092_ratified_phase_1405; "
                "CDL-092 ratified at Phase 1405: ADR-0001 content address, "
                "ADR-0038 CV signing, Decimal-only +/-15% band, explicit-lane "
                "allowlist, subjective jury exclusion; "
                "Phase 1425 verified: capproof_cdl_ratified_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: cdl_092_ratified_phase_1405"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 4: Maintenance lottery pool CDL ratified (MET — Phase 1408)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="MAINTENANCE_LOTTERY_CDL_RATIFIED",
            description=(
                "A maintenance lottery pool CDL has been ratified, defining how "
                "low-capability agents earn ECU through maintenance tasks and a "
                "lottery/pool lane regardless of full review-lane eligibility."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "docs/specs/ilc_cdl_093_maintenance_lottery_pool_ratification_evidence_1408_v0.1.md; "
                "token: cdl_093_ratified_phase_1408; "
                "ilc_core/epistemic/maintenance_lottery_runtime.py; "
                "MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN='cdl_093_ratified_phase_1408'; "
                "CDL-053 Werner local productive credit ratified Phase 1407-Fix2; "
                "Phase 1425 verified: maintenance_lottery_cdl_ratified_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: cdl_093_ratified_phase_1408"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 5: J-004 jury incentive economics CDL ratified (MET — Phase 1400)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="JURY_INCENTIVE_CDL_RATIFIED",
            description=(
                "J-004 jury incentive economics CDL is ratified, locking: "
                "fixed-base-plus-delayed-accuracy-weighted reviewer compensation, "
                "non-response economics, bond/escrow terms, and anti-approval-volume "
                "bias controls."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md; "
                "token: cdl_091_ratified_phase_1400; "
                "ilc_core/epistemic/jury_incentive_runtime.py; "
                "JURY_INCENTIVE_CDL_RATIFIED_TOKEN='cdl_091_ratified_phase_1400'; "
                "Phase 1425 verified: jury_incentive_cdl_ratified_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: cdl_091_ratified_phase_1400"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 6: Production review lane wiring complete (MET — Phase 1415/1416/1417)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="REVIEW_LANE_WIRING_COMPLETE",
            description=(
                "Production review lane wiring is complete: T0.5 -> T1+ admission path "
                "is implemented (ADR-0041 §1), reviewer-payment settlement stubs are "
                "wired default-off, and public admission evidence satisfies the Phase "
                "1387a public-economics admission firewall."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "ilc_core/epistemic/review_lane_admission_runtime.py; "
                "token: review_lane_admission_runtime_committed_phase_1415; "
                "token: review_lane_dedup_enforcement_stub_phase_1416; "
                "token: review_lane_payment_settlement_stub_phase_1416; "
                "tests/test_phase_1417_review_lane_integration.py; "
                "token: review_lane_wiring_complete_phase_1417; "
                "ADR-0043 accepted: review_lane_wiring_adr_accepted_phase_1414; "
                "Phase 1425 verified: review_lane_wiring_complete_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: review_lane_wiring_complete_phase_1417"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 7: Anti-capture diversity checks verified (MET — Phase 1419)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="ANTI_CAPTURE_DIVERSITY_VERIFIED",
            description=(
                "Anti-capture diversity checks are verified in production mode: "
                "CDL-V3-style cluster diversity enforcement, VRF-backed outsider "
                "selection, and same-operator-domain-not-independent enforcement "
                "are active for high-value production review lanes."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "ilc_core/epistemic/jury_assignment_runtime.py; "
                "token: anti_capture_diversity_verified_phase_1419; "
                "token: cdl_v3_cluster_diversity_wired_jury_assignment_phase_1419; "
                "token: vrf_outsider_selection_verified_phase_1419; "
                "token: same_operator_domain_independence_verified_phase_1419; "
                "ADR-0044 accepted: anti_capture_diversity_adr_accepted_phase_1418; "
                "Phase 1425 verified: anti_capture_diversity_verified_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: anti_capture_diversity_verified_phase_1419"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 8: Copyright/publication legal disposition (MET — Phase 1420)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="COPYRIGHT_COUNSEL_DISPOSITION",
            description=(
                "ADR-0041 §5 copyright/publication boundary is resolved via a "
                "counsel disposition before open public ingestion is activated: "
                "verbatim storage legal character confirmed, D2D distribution "
                "legal character confirmed, fair-use/research-exemption basis "
                "documented per applicable jurisdiction."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "docs/specs/ilc_copyright_counsel_disposition_1420_v0.1.md; "
                "token: copyright_counsel_disposition_complete_phase_1420; "
                "token: self_counsel_verbatim_storage_boundary_phase_1420; "
                "token: self_counsel_d2d_distribution_boundary_phase_1420; "
                "disposition is Genesis-authority self-counsel, not external legal opinion; "
                "Phase 1425 verified: copyright_counsel_disposition_condition_met_verified_phase_1425"
            ),
            blocking=True,
            routing=(
                "ALREADY MET -- evidence: copyright_counsel_disposition_complete_phase_1420"
            ),
        ),

        # -------------------------------------------------------------------
        # Condition 9: Public-economics admission firewall active (MET)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="PUBLIC_ECONOMICS_FIREWALL",
            description=(
                "Phase 1387a public-economics admission firewall is active and "
                "enforces that private, semi-private, or operator-local material "
                "cannot construct protocol ECU, public reputation, public "
                "settlement, or public claimability events."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "ilc_core/ledger/public_economics_admission_firewall.py; "
                "Phase 1387a tokens: public_economics_requires_public_node_admission_verified_phase_1387a, "
                "private_visibility_excluded_from_public_economics_phase_1387a; "
                "token: public_economics_firewall_condition_met_phase_j008"
            ),
            blocking=False,
            routing="ALREADY MET — no further action required",
        ),

        # -------------------------------------------------------------------
        # Condition 10: Epoch-hash not marketed as production privacy (MET)
        # -------------------------------------------------------------------
        GateCondition(
            condition_id="NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM",
            description=(
                "Epoch-hash shadow assignment is documented as transparent and "
                "auditable — NOT private or strategically unpredictable. "
                "No claim of production privacy via epoch-hash is made anywhere "
                "in the J-series artifacts."
            ),
            status=GateConditionStatus.MET,
            evidence_ref=(
                "docs/adr/ADR_0040_Jury_Eligibility_Assignment.md §Assignment Source; "
                "ilc_core/epistemic/jury_assignment_runtime.py: "
                "assignment_mode='epoch_hash_shadow', "
                "token: epoch_hash_shadow_assignment_only_phase_j006"
            ),
            blocking=False,
            routing="ALREADY MET — must remain documented in all future J-series artifacts",
        ),
    ]

    # Compute verdict
    blocking_not_met = [
        c.condition_id for c in conditions
        if c.blocking and c.status == GateConditionStatus.NOT_MET
    ]

    verdict = "PASS" if not blocking_not_met else "INCOMPLETE"

    return JuryActivationGateReport(
        conditions=conditions,
        verdict=verdict,
        blocking_not_met=blocking_not_met,
        phase_tokens=[
            # Phase 1398 historical tokens — must remain present
            _TOKEN_GATE_DEFINED,
            _TOKEN_NOT_AUTHORIZED,
            _TOKEN_INCOMPLETE,           # historical — all conditions are now MET
            _TOKEN_VRF_NOT_IMPL,         # historical — now superseded by Phase 1411/1412
            _TOKEN_CAPPROOF_NOT_OPENED,  # historical — now superseded by CDL-092 Phase 1405
            _TOKEN_LOTTERY_NOT_OPENED,   # historical — now superseded by CDL-093 Phase 1408
            _TOKEN_INCENTIVE_NOT_RATIFIED,  # historical — now superseded by CDL-091 Phase 1400
            _TOKEN_J007_MET,
            _TOKEN_FIREWALL_MET,
            # Phase 1425 tokens — all 7 blocking conditions verified MET
            _TOKEN_PRE_GATE_COMPLETE,
            _TOKEN_VRF_MET_1425,
            _TOKEN_CAPPROOF_MET_1425,
            _TOKEN_LOTTERY_MET_1425,
            _TOKEN_INCENTIVE_MET_1425,
            _TOKEN_REVIEW_LANE_MET_1425,
            _TOKEN_ANTI_CAPTURE_MET_1425,
            _TOKEN_COPYRIGHT_MET_1425,
            _TOKEN_ALL_SEVEN_MET,
            _TOKEN_GATE_STILL_INCOMPLETE,
            # Phase 1427 tokens - production jury activation authorized
            _TOKEN_GATE_PASS_1427,
            _TOKEN_GATE_RERUN_1427,
            _TOKEN_PRODUCTION_AUTHORIZED_1427,
            _TOKEN_ALL_TEN_MET_1427,
        ],
        gate_authorized=(verdict == "PASS" and not PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED),
        production_activated=False,
        execution_surfaces_activated=False,
        runtime_version=JURY_ACTIVATION_GATE_VERSION_1427,
    )
