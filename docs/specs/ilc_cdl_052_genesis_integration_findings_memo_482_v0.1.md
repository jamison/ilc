# ILC CDL-052 and Genesis Integration Findings Memo 482 v0.1

Status: findings memo
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. CDL-052 epistemic runtime completeness

The CDL-052 runtime surface implemented in Phases 477-478 is complete within the authorized
scope of Window 475-484.

Implemented surface:
- node-submission envelope validation and deterministic mode routing,
- CDL-V7 Popperian admissibility delegation,
- bounded refutation submission handling,
- novelty-check query surface,
- reuse-centrality query stub.

Deferred items already visible at runtime boundary:
- calibrated staking amounts,
- non-stub reuse-centrality backend,
- Mode 3 auditor-review execution,
- downstream simulation calibration.

Staking constants are symbolically deferred pending a future simulation lane.
Reuse-centrality computation backend is a stub pending a future implementation lane.
Mode 3 auditor-review execution is deferred beyond Window 475-484.

## 2. Genesis validator bootstrap completeness

The genesis validator bootstrap runtime implemented in Phases 480-481 is complete within the
authorized scope of Window 475-484.

Implemented surface:
- deterministic enrollment-record generation,
- epoch-zero state materialization,
- deterministic `quorum_record_seed` derivation,
- admission-control bundle construction,
- admission-control bundle verification,
- epoch-zero admission enforcement.

Deferred items already visible at the bootstrap boundary:
- validator network join after epoch zero,
- validator recovery flow,
- private-key handling and ceremony execution tooling,
- post-bootstrap operator lifecycle automation.

Validator network join and recovery flow is deferred beyond Window 475-484.

## 3. Cross-track dependency review

Cross-track review outcome: partial alignment, with one deferred binding gap.

Aligned items:
- Phase 480 derives `validator_id` from CDL-042 using `derive_agent_id`,
- Phase 481 admission-control enforcement operates over canonical `validator_id` values,
- both tracks remain anchored to already-ratified dependencies and do not invent new authority.

Deferred binding gap:
- the CDL-052 node-submission runtime currently validates `agent_id` as a non-empty string only,
- Phase 477 does not yet normalize or prove that `agent_id` equals the CDL-042-derived
  `validator_id` used by the genesis bootstrap runtime,
- there is no Phase 475-484 requirement that epistemic submissions must be admitted genesis
  validators before submission acceptance.

This is an honest integration gap, but it does not invalidate the declared scope of either track.
It is a future integration obligation rather than a defect in the completed Phase 477-481 work.

Phase 476-481 regression bundle results are recorded in this memo.
Regression counts:
- Phase 476: `6 passed`
- Phase 477: `8 passed`
- Phase 478: `8 passed`
- Phase 479: `6 passed`
- Phase 480: `8 passed`
- Phase 481: `8 passed`
- Aggregate recorded result: `44 passed`

## 4. Deferred items and governance-priority list

Governance-priority items:
- `CRITICAL` — bind CDL-052 submission identity to a canonical CDL-042-derived validator identity
  or an explicitly authorized non-validator submission identity model,
- `CRITICAL` — run the future simulation lane needed to replace symbolic staking placeholders with
  evidence-backed staking values,
- `MODERATE` — implement a non-stub reuse-centrality backend and publish its computational contract,
- `MODERATE` — define Mode 3 auditor-review execution semantics and authority boundary,
- `MODERATE` — specify validator network join and recovery flow after genesis bootstrap,
- `LOW` — standardize ceremony-tooling/operator workflow interfaces around the genesis runtime.

The integration gap in Section 3 is recorded here as a governance-priority carry-forward item.
No ilc_core/ implementation occurs in Phase 482.
No decision-log mutation occurs in Phase 482.

## 5. Adversarial hardening relevance review

Phase 473 remains relevant to the combined surface in three ways:
- insufficient-diversity finality handling remains the governing upstream consensus hardening
  context for any future validator bootstrap admission expansion,
- malformed policy and malformed cluster-map handling reinforce the need for strict typed
  envelope and bootstrap record validation,
- bridge realism findings confirm that deterministic semantics outrank transport realism at this
  stage, which is consistent with the current stubbed reuse-centrality and non-live bootstrap lane.

Not directly discharged by Phase 473:
- Mode 3 auditor-review execution,
- validator network join and recovery flow,
- live distributed deployment evidence for epistemic runtime and validator bootstrap.

## 6. Window 475-484 integration verdict

Window 475-484 CDL-052 epistemic runtime and genesis validator bootstrap are complete within the
authorized scope of the Phase 475 sequence lock.

The combined surface is coherent enough to close this window honestly, with deferred follow-on
obligations explicitly recorded in Section 4. No cross-track finding in this memo requires a
retroactive change to Phases 476-481.

Phase 483 is the next authorized phase.
