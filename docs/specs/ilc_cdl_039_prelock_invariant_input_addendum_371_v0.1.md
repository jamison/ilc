# ILC CDL-039 Prelock Invariant Input Addendum 371 v0.1

Status: Non-ratifying prelock input artifact  
Date: 2026-03-06  
Phase context: Phase 371 input to Phase 372/373 drafting  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and boundary

This addendum captures invariant candidates for CDL-039 prelock drafting based on:
- Phase 368 sequence-lock boundaries,
- Phase 369 SIM-004 evidence,
- Phase 370 SIM-005 evidence,
- privacy/routing design feedback.

Boundary:
- non-ratifying,
- no decision-log mutation,
- no runtime mutation,
- no retroactive invalidation of ratified v0.1 runtime tranches.

## 2. Five invariant candidates for CDL-039 prelock

### 2.1 Transport header non-authorship invariant

**Invariant candidate:**
- Transport Envelope routing headers MUST NOT carry `creator_agent_id`; authorship attribution is resolved from Authored Payload and protocol interpretation, not routing headers.

**Implementation note (bounded, one-way):**
- Current v0.1 dissemination runtime (`Phase 362`) includes `creator_agent_id` in transport headers; CDL-039 prelock sets the target invariant, and runtime upgrade is bounded to the authorized D2d/network runtime implementation window (Window 378+).

### 2.2 Partition-state cross-cluster reference rate-limit invariant

**Invariant candidate:**
- When partition-state is asserted by the gossip coordinate system, nodes MUST apply a cross-cluster reference creation rate limit not exceeding `R_partition_cross_ref` per epoch, emit deterministic backpressure signaling, and maintain release hysteresis `H_release` to prevent limit flapping.

**Parameterization boundary:**
- `R_partition_cross_ref` and `H_release` are prelock parameters for Phase 373 adversarial calibration, not fixed constants in this addendum.

### 2.3 Cluster membership non-inferrability invariant

**Invariant candidate:**
- Dissemination headers and gossip messages MUST NOT enable a passive observer to reconstruct the membership set of any cluster.

**Adversarial-test anchor:**
- Phase 373 must include explicit passive-observer reconstruction attempts as a required prelock adversarial check.

### 2.4 Private-visibility expiry invariant (with scope question)

**Invariant candidate:**
- Private-visibility nodes without a valid `promotion_receipt` after `retention_epochs` MUST be treated as expired and ineligible for direct promotion.

**Open scope question (must be resolved in CDL-039 prelock text):**
- Whether post-expiry recovery is fully covered by existing CDL-038 successor-node semantics, or needs an explicit CDL-039 clause, remains open and must be decided explicitly rather than assumed.

**Dependency note:**
- `retention_epochs` constant is blocked on Phase 371 epoch-type interpretation resolution for SIM-003/SIM-005 consistency.

### 2.5 Opaque channel identifier invariant

**Invariant candidate:**
- Transport `channel` routing field MUST be an opaque identifier (CID or uniformly random bytes). Human-readable channel labels are UI-layer concerns and MUST NOT appear in transport headers.

**Implementation note (bounded, one-way):**
- Current v0.1 dissemination runtime (`Phase 362`) uses enum-style channel values; CDL-039 prelock sets the target invariant, and runtime upgrade is bounded to the authorized D2d/network runtime implementation window (Window 378+).

## 3. Phase 371 output contract dependencies

Phase 371 interpretation artifact must provide:

1. **SIM taxonomy table (canonical numbering and scope):**
   - explicit mapping for SIM-003, SIM-004, SIM-005 semantics used by the current window,
   - explicit note of any historical numbering drift and the canonical resolution for Phase 372 inputs.

2. **Epoch-type interpretation table for active sim outputs:**
   - SIM-003 interpretation under declared epoch type,
   - SIM-004 interpretation under declared epoch type,
   - SIM-005 interpretation under declared epoch type,
   - wall-clock conversion for any parameter carried into prelock decisions.

3. **Constant lock/readiness flags:**
   - which constants are interpretation-locked for Phase 372 drafting,
   - which constants remain Phase 373 adversarial calibration inputs.

This addendum does not resolve SIM taxonomy drift; it requires Phase 371 to resolve it.

## 4. Drafting guidance for Phase 372 and Phase 373

### 4.1 Phase 372 (topology/privacy hardening)

Phase 372 prompt should require prelock artifact coverage for:
- the five invariant candidates above,
- explicit distinction between target invariants and current v0.1 runtime state,
- explicit unresolved item list handed to Phase 373 calibration.

### 4.2 Phase 373 (adversarial review and evidence freeze)

Phase 373 prompt should require adversarial checks for:
- partition rate-limit flapping under noisy partition-state detection,
- passive cluster membership reconstruction attempts,
- expiry-path abuse attempts around `promotion_receipt` timing,
- channel identifier leakage tests (semantic inference from routing identifiers).

## 5. Non-goals

This addendum does not:
- ratify CDL-039,
- set final constants for `R_partition_cross_ref`, `H_release`, or `retention_epochs`,
- modify `CDL-036` or `CDL-038` rows,
- authorize any D2d runtime implementation in Window 368-377.
