# ILC CDL-055 Validator Staking and Liveness Enforcement Opening Stub 492 v0.1

Status: open
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Lane identity

CDL-055 opens in Phase 492.

This lane amends validator-participation consequences and is separate from the content-claim
orphan-policy surface except where CDL-046 is explicitly referenced.

## 2. CDL-046 amendment boundary

CDL-054 is already ratified before CDL-055 opens.
CDL-046 remains the orphan-policy authority outside validator participation.

## 3. Evidence dependencies

Required anchors:
- `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md`
- `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`

## 4. Non-goals

This opening does not:
- ratify validator stake amounts,
- ratify liveness thresholds,
- change `ilc_core/`,
- consume CDL-053.

No `ilc_core/` mutation occurs in Phase 492.
