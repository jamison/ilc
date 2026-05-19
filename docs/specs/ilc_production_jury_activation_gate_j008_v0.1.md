# ILC Production Jury Activation Gate v0.1

**Phase:** 1398 / J-008
**Date:** 2026-05-19
**Status:** gate defined; verdict INCOMPLETE
**Scope:** gate definition and evaluation only; no production activation

## Required Tokens

```text
production_jury_activation_gate_defined_phase_j008
production_jury_activation_not_authorized_phase_j008
j008_gate_verdict_incomplete
vrf_verifier_required_not_implemented_phase_j008
capproof_cdl_not_opened_phase_j008
maintenance_lottery_cdl_not_opened_phase_j008
jury_incentive_cdl_not_ratified_phase_j008
j007_harness_condition_met_phase_j008
public_economics_firewall_condition_met_phase_j008
```

## 1. Purpose

This document defines the production jury activation gate — the complete set of
conditions that must be satisfied before production jury assignment, production
reviewer payment, production public ingestion, or live ECU distribution via a
jury or maintenance lane may be activated.

This is a gate-definition artifact. It does not activate production jury
assignment. The overall gate verdict at this phase is **INCOMPLETE**: seven of
ten conditions are NOT_MET (six are blocking). No production activation may
proceed until all blocking conditions are MET and a production GO is issued.

Relationship to J-005 activation ladder:

| J-005 Stage | Criteria | Status |
|-------------|----------|--------|
| Shadow / spec-only | Spec complete; no runtime required | ✓ COMPLETE (J-005) |
| Bounded testnet | CapProof runtime; probe content-addressed; CV signing; deterministic probe variation | NOT_MET — CapProof CDL not opened |
| Public RC shadow | J-007 harness passes; no live ECU distribution | ✓ COMPLETE (J-007) |
| Production candidate | J-008 gate passes; VRF confirmed; maintenance lottery pool CDL ratified; review lane wiring complete | NOT_MET — this gate |

## 2. Gate Condition Table

| # | Condition ID | Description | Status | Blocking |
|---|---|---|---|---|
| 1 | `J007_HARNESS_PASS` | J-007 shadow harness passes | **MET** | yes |
| 2 | `VRF_VERIFIER_IMPLEMENTED` | VRF proof verifier implemented for high-value assignment | **NOT_MET** | yes |
| 3 | `CAPPROOF_CDL_RATIFIED` | CapProof CDL ratified (probe content-addressing, CV signing, ±15% band, baseline transition) | **NOT_MET** | yes |
| 4 | `MAINTENANCE_LOTTERY_CDL_RATIFIED` | Maintenance lottery pool CDL ratified | **NOT_MET** | yes |
| 5 | `JURY_INCENTIVE_CDL_RATIFIED` | J-004 jury incentive economics CDL ratified (fixed+accuracy-weighted, bonds, non-response economics) | **NOT_MET** | yes |
| 6 | `REVIEW_LANE_WIRING_COMPLETE` | Production review lane wiring complete (T0.5→T1+ admission runtime, reviewer-payment settlement) | **NOT_MET** | yes |
| 7 | `ANTI_CAPTURE_DIVERSITY_VERIFIED` | Anti-capture diversity checks verified in production mode (CDL-V3 + VRF outsider selection) | **NOT_MET** | yes |
| 8 | `COPYRIGHT_COUNSEL_DISPOSITION` | ADR-0041 §5 copyright/publication counsel disposition complete | **NOT_MET** | yes |
| 9 | `PUBLIC_ECONOMICS_FIREWALL` | Phase 1387a public-economics admission firewall active | **MET** | no |
| 10 | `NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM` | Epoch-hash shadow assignment NOT claimed as production privacy | **MET** | no |

**Gate verdict: INCOMPLETE** (7/10 NOT_MET; 6 blocking conditions unmet)

## 3. Blocking Condition Detail

### 3.1 VRF_VERIFIER_IMPLEMENTED

ADR-0040 §Assignment Source records:
```text
vrf_required_for_production_high_value_assignment
vrf_proof_verifier_not_implemented
```

`ilc_core/validator/topology_shuffle_runtime.py` triggers a VRF upgrade at 10
validators but contains no VRF proof verifier. `ilc_core/epistemic/jury_assignment_runtime.py`
uses `epoch_hash_shadow` assignment mode only.

**Routing:** Future CDL or ADR specifying VRF library selection, proof format,
and integration with `jury_assignment_runtime.py`. Must be implemented before
any production-privacy claim about reviewer assignment.

### 3.2 CAPPROOF_CDL_RATIFIED

CapProof adjusts ECU pricing ±15% only; it never mints ILC directly. The five
probes (GEMMProbe, InferProbe, GraphProbe, BandwidthProbe, DeterminismProbe)
produce a signed Capability Vector. No CapProof CDL exists in the constitutional
decision log.

**Routing:** Open a dedicated CapProof CDL. Must cover:
- Content-addressed probe binary supply chain
- Capability Vector signing contract
- ±15% band enforcement
- Genesis-baseline (score=1.0) transition rule → rolling median post-taper
- VRF-based spot-recheck mechanism

### 3.3 MAINTENANCE_LOTTERY_CDL_RATIFIED

Maintenance tasks are reward-eligible after passing the applicable review lane
(J-005 §6). Low-capability agents may participate through a lottery/pool lane.
No maintenance lottery pool CDL exists.

**Routing:** Open a maintenance lottery pool CDL defining: pool budget source,
task eligibility, lottery mechanics, ECU distribution path, anti-gaming controls.
Must route through J-008 production activation gate re-run after ratification.

### 3.4 JURY_INCENTIVE_CDL_RATIFIED

J-004 opened the jury incentive economics lane (`jury_incentive_economics_cdl_opened_phase_j004`)
and records `reviewer_payment_not_activated_phase_j004`. The CDL is opened but
not deliberated or ratified. The recommended structure is fixed-base-plus-delayed-
accuracy-weighted compensation to avoid approval-volume bias.

**Routing:** Complete CDL deliberation. Confirm: reviewer fee amounts, bond/escrow
terms, non-response decay mechanics, anti-rubber-stamp controls, funding source
(petition-bond or fixed pool). Ratify before any live reviewer payment.

### 3.5 REVIEW_LANE_WIRING_COMPLETE

The J-007 shadow harness exercises T0.5 quarantine and task lifecycle in shadow
mode only. No production T0.5 → T1+ admission runtime exists. No reviewer-payment-
to-ledger settlement path exists. ADR-0041 §2 dedup enforcement is not implemented
as a protocol-enforced check.

**Routing:** Implement T0.5→T1+ admission runtime (ADR-0041 §1–§4), dedup
enforcement engine, and reviewer-payment settlement (after J-004 CDL ratification).
Wire Phase 1387a public-economics firewall to admission gate.

### 3.6 ANTI_CAPTURE_DIVERSITY_VERIFIED

`jury_assignment_runtime.py` enforces `independence_k=3` and
`same_operator_domain_not_independent` in quote mode. CDL-V3 diversity floor
runtime (`ilc_core/consensus/diversity_floor_runtime.py`) exists but is not
wired to jury assignment. VRF is not implemented, so production outsider
selection cannot claim unpredictability.

**Routing:** Wire CDL-V3 diversity floor into production jury assignment path.
Integrate VRF verifier with outsider-seat selection. Run a production-mode
diversity verification pass and record results.

### 3.7 COPYRIGHT_COUNSEL_DISPOSITION

ADR-0041 §5 records:
```text
verbatim_distribution_via_d2d_requires_counsel_review_before_public_activation
```

Storing hash+metadata+extracted claims is presumptively permissible under
fair-use/research-exemption norms, but verbatim full-text storage and D2D
distribution of verbatim copyrighted content requires explicit legal disposition
before open public ingestion is activated.

**Routing:** Counsel track. Obtain a legal disposition memo (or equivalent
Genesis-authority internal decision under the self-counsel framework) covering
the applicable jurisdictions before open public ingestion is turned on.

## 4. Met Conditions (Evidence)

### 4.1 J007_HARNESS_PASS
`ilc_core/epistemic/ingestion_shadow_harness.py` produces a PASS verdict
(≥1 valid T0.5 submission + ≥1 task reaching audited state).
Token: `shadow_public_ingestion_harness_phase_j007`. 55 tests passing.

### 4.2 PUBLIC_ECONOMICS_FIREWALL
`ilc_core/ledger/public_economics_admission_firewall.py` (Phase 1387a)
enforces the private/public economics separation. Tokens:
`public_economics_requires_public_node_admission_verified_phase_1387a`,
`private_visibility_excluded_from_public_economics_phase_1387a`.

### 4.3 NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM
`ilc_core/epistemic/jury_assignment_runtime.py` uses
`assignment_mode="epoch_hash_shadow"` and records
`epoch_hash_shadow_assignment_only_phase_j006`. ADR-0040 explicitly documents
that J-008 must not market epoch-hash shadow assignment as production privacy.
This constraint is satisfied in the current J-006 runtime.

## 5. Non-Authorizations

This phase authorizes no production jury assignment, no VRF implementation, no
CapProof CDL opening, no maintenance lottery pool CDL opening, no J-004 CDL
ratification, no production review lane wiring, no anti-capture production
verification, no copyright counsel disposition, no live ECU distribution, no
reviewer payment activation, no public graph admission activation, no public
claimability activation, no production ingestion, no CDL mutation, no runtime
mutation beyond the gate module, no public RC publication, no source publication,
no release signing, no wallet/ECU/ILC value-path production activation, no Genesis
intervention execution, and no legal conclusion.

## 6. Future Phase Routing

| Future phase | Required action before gate can re-run |
|---|---|
| CapProof CDL | Open + ratify; must precede CapProof deployment and VRF spot-recheck |
| Maintenance lottery pool CDL | Open + ratify; must precede live ECU distribution from maintenance lane |
| J-004 CDL ratification | Complete deliberation; must precede live reviewer payment |
| VRF implementation | CDL or ADR specifying verifier; must precede high-value production assignment |
| Review lane wiring | T0.5→T1+ admission runtime; ADR-0041 §2 dedup enforcement; reviewer-payment settlement |
| Anti-capture production verification | CDL-V3 + VRF wiring to jury_assignment_runtime.py; diversity verification pass |
| Copyright counsel disposition | Counsel track or Genesis-authority self-counsel memo |
| J-008 gate re-run | After all blocking conditions are MET; requires production GO |

## 7. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md -> jury_epoch_work_canon
```
