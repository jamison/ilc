# ILC Antigravity Context Capsule v1.1

Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.0.md

This capsule is self-contained.

## 1. Project identity

ILC remains a ratification-first constitutional protocol project for autonomous agents coordinating in an epistemic graph through claims, refutations, and challenge-driven reuse.

## 2. Core architectural invariants

- The three-envelope model remains the anchor invariant.
- Canonical encoding remains DAG-CBOR + CIDv1 + COSE Sign1 + NDJSON.
- The graph remains the computer.
- Constitutional mutations remain controlled by CDL process authority, not runtime shortcuts.
- 7+1 panel architecture remains locked for task-level epistemic evaluation (`panel_size=8`, `independence_k=3`, `outsider_seat=true`, `k=5 of m=7`).

Canonical carried-forward panel and governance tokens:
- `Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat`
- `VRF-selected outsider seat is the anti-capture mechanism`
- `trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2`
- `CDL-V3 cluster diversity floor operationalizes independence_k=3`
- `CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism`
- `The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.`
- `The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.`
- `Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention.`

## 3. Project state (as of Phase 366 completion)

Phase 366 complete.

Phase 367 next.

Window 358-367 is in closure-prep state with runtime tranche complete (360-364) and simulation commissioning complete (365).

## 4. Window 358-367 constitutional and runtime state

- `CDL-034` through `CDL-038` are ratified and implemented in this window.
- `CDL-039` is open (opened in Phase 359) with prelock finalization deferred to later evidence windows.
- No V-series runtime implementation is authorized in Window 358-367.
- ADM-003 7+1 behavioral role resolution remains in force from Phase 354.

## 5. Implemented node-schema runtime surfaces

CDL-034 through CDL-038 runtime implementation tranches are complete in phases 360-364.

Implemented modules:
- `ilc_core/node/node_schema_core_runtime_360.py`
- `ilc_core/node/validation_lifecycle_runtime_361.py`
- `ilc_core/node/node_dissemination_runtime_362.py`
- `ilc_core/node/executable_descriptor_runtime_363.py`
- `ilc_core/node/promotion_continuity_runtime_364.py`

## 6. Simulation evidence now available

Phase 365 published deterministic simulation outputs and manifests for:
- `SIM-001` bootstrap threshold analysis,
- `SIM-002` micro-agent cost-floor model,
- `SIM-003` graph growth and storage pressure.

Current modeled signals:
- SIM-001 launch-threshold signal indicates high minimum network-size requirements,
- SIM-002 signals a low tolerated write-fee multiplier bound in tested ranges,
- SIM-003 signals aggressive pruning pressure under high claim-rate lanes.

These are modeled evidence inputs and remain non-ratifying.

## 7. Runtime authorization and implementation boundary

- Runtime authorization in this window remains bounded to `CDL-034` through `CDL-038` surfaces.
- CDL-039 remains open and implementation-barred in this window.
- Unratified surfaces remain implementation-barred.
- ILC co-opts existing wallet trust rather than building competing wallet infrastructure.

## 8. Phase 367 closure preconditions

Phase 367 must prove:
- closure-gate recursion integrity,
- bounded-runtime mutation scope for Window 358-367,
- non-sensitive phase boundaries held for 365 and 366,
- handoff readiness for Window 368 sequence-lock drafting.

## 9. Change log from v1.0

Changed relative to v1.0:
- project state advanced from pre-runtime authorization framing to completed runtime tranche framing,
- SIM-001/002/003 evidence availability added,
- explicit closure-prep boundary for Phase 367 added,
- wallet-agnostic strategic principle added explicitly.

## 10. Key canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v1.0.md`
- `docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.4.md`
- `docs/specs/ilc_integration_coherence_report_366_v0.1.md`
- `docs/specs/ilc_sim_001_002_003_commissioning_results_365_v0.1.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`
- `docs/specs/ilc_signing_provider_interface_262_v0.1.md`
