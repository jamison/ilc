# ILC Post-586 Strike Force Runtime Hardening Packet v0.1

Status: planning packet
Date: 2026-04-04
Owner lane: post-586 runtime hardening / economic proof lane

## 1. Purpose

This packet restates the implementation-heavy Strike Force tranche after the
public-boundary clarifications landed through Phases 585-586.

The goal is to keep forward momentum on the live runtime and economic proof
lane without inventing public-authority semantics ahead of the remaining
Phase 587-594 constitutional closure work.

## 2. Dependency stack

This packet depends on the following already-locked surfaces:
- `docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md`
- `docs/specs/ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`

## 3. Operating rule

The Strike Force lane may continue hardening the runtime, proof, and gate
surfaces, but it must not silently close public-release law by implementation.

That means:
- no ad hoc public identity activation semantics ahead of Phase 587,
- no ad hoc public namespace authority semantics ahead of Phase 587,
- no ad hoc public quorum eligibility semantics ahead of Phase 588,
- no ad hoc public settlement legitimacy or payout traceability semantics ahead
  of Phase 589,
- no ad hoc Genesis authority, sunset, or fork-legitimacy closure ahead of
  Phase 590,
- no public-release honesty or final public-runtime claim ahead of Phases
  591-594.

If the runtime needs new receipts or manifests before those phases close, they
must be described as bounded internal or RC proof artifacts rather than as
canonical public-authority receipts.

## 4. Strike Force tranche in scope

The resumed tranche remains:

### 4.1 Wallet semantics and history hardening

Target:
- tighten `wallet-status`, `wallet-history`, and `wallet-export`,
- preserve the Phase 576 read-only/accounting boundary,
- harden stable machine-auditable history and receipt output.

### 4.2 Live settlement idempotency tightening

Target:
- push replay rejection and no-drift semantics deeper into the live settlement
  path,
- prove deterministic repeated execution behavior,
- preserve bounded RC settlement status values.

### 4.3 Runtime-store integrity checks

Target:
- strengthen LMDB root, manifest, schema/version, and identity-alignment
  checks,
- fail closed on runtime-store mismatches,
- keep durable state authoritative when present.

### 4.4 Durable graph query closure

Target:
- harden the bounded query surface over durable state,
- keep `graph-summary`, `graph-node`, `graph-links`, `quorum-record`, and
  related summaries stable for proof and agent use,
- avoid widening into public graph-legitimacy claims.

### 4.5 Multi-cycle economic proof

Target:
- move from single-cycle proof confidence toward repeated multi-epoch behavior,
- prove stable balances, wallet history, and graph/runtime continuity across
  repeated cycles.

### 4.6 Economic negative-path expansion

Target:
- corrupted state,
- partial state,
- stale manifest/store mismatch,
- duplicate settlement attempts,
- deterministic recovery or fail-closed behavior.

### 4.7 RC gate and release-claim promotion

Target:
- require stronger economic proof evidence at the RC gate,
- reduce operator interpretation in favor of machine-legible proof outputs,
- promote only bounded RC/testnet claims until the public lane closes.

## 5. Explicit exclusions

This Strike Force packet does not authorize:
- QuotaMiner, onboarding UX, dashboards, or other harness/product features,
- wallet spend, transfer, withdrawal, or public claimability semantics,
- public identity or quorum authority closure,
- public minting or founder/genesis payout stabilization,
- protocol-law mutation by runtime shortcut.

## 6. Expected outputs

This tranche should leave behind:
- fresh committed-head economic proof artifacts,
- stronger replay and idempotency evidence,
- stronger runtime-store and graph-state integrity checks,
- multi-cycle proof coverage,
- expanded negative-path drills,
- tighter RC gate consumption of economic proof results.

## 7. Relationship to Phase 587+

This packet is parallel to, not a substitute for, the remaining public-release
constitutional lane.

The intended sequencing is:
1. keep Phase 587-590 queued as the public-boundary closure lane,
2. continue runtime/economic hardening against the already-locked boundaries,
3. feed cleaner runtime and proof surfaces into the later public-runtime and
   public-release claim phases.

## 8. Related references

- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_post_582_harness_sdk_lane_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
