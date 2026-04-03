# ILC Phase 575-584 Sequence Lock v0.1

Status: locked
Date: 2026-04-03
Phase: 575
Owner lane: G8 implementation cluster

## 1. Window summary

Window 575-584 is the RC0.1 testnet economics and agent-loop window. It builds
on the already-passing three-machine substrate and hardens the live economic
path without claiming public-release constitutional closure.

Required lock tokens:
- `rc0_1_testnet_window_575_584_primary_gate`
- `settlement_wallet_boundary_precedes_agent_loop_runtime`
- `persisted_graph_contract_precedes_live_submission_cutover`
- `curated_genesis_lineage_testnet_only`
- `wallet_visibility_accounting_only_in_rc0_1`
- `cdl_v7_reproducibility_disposition_required_before_phase_584`
- `outbound_http_machine_payment_skill_support_lane_only`
- `outbound_http_machine_payment_skill_may_close_as_explicit_defer`
- `public_genesis_and_minting_stabilization_deferred_to_585_plus`
- `no_public_release_claim_before_585_594`

## 2. Hard pass condition

Window 575-584 passes only if all of the following are true:
1. The live agent loop runs across the three-machine substrate with seven agent
   processes and the bounded 7+1 panel path.
2. The minimum persisted graph records are written durably and can be queried
   deterministically from runtime state.
3. ECU attribution claims flow into the durable settlement path and epoch commit
   updates the settled ledger without replay drift.
4. Wallet status, history, and export surfaces read deterministic settled state
   without requiring ledger write authority.
5. Negative-path economic drills cover replay, manifest/store mismatch, and
   missing or corrupted runtime-state conditions with deterministic failure
   tokens.
6. The bounded CDL-V7 reproducibility disposition is explicit before window
   closure.
7. No public genesis-governance stabilization, permissionless public admission,
   or finalized public minting semantics are claimed by this window.
8. The outbound `HTTP machine-payment skill` lane, if landed in this window,
   remains secondary to the economic proof path; if deferred, the defer is
   explicit in the coherence report and handoff.

## 3. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 575 | Window 575-584 sequence lock | `ilc_phase_575_584_sequence_lock_v0.1.md` | No |
| 576 | RC0.1 settlement + wallet boundary lock | `ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` | No |
| 577 | RC0.1 persisted graph contract lock | `ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md` | No |
| 578 | RC0.1 curated genesis/bootstrap lineage lock | `ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md` | No |
| 579 | Agent behavioral loop runtime cutover | `tools/agent_loop_v1.py` | YES |
| 580 | 7+1 panel and live submission integration | panel wiring + submission runtime | YES |
| 581 | ECU attribution, settlement, and wallet query integration | durable economic runtime updates | YES |
| 582 | Reproducibility disposition + outbound HTTP machine-payment skill defer-or-attach | reproducibility artifact + outbound skill attachment or explicit defer | YES |
| 583 | Coherence report + capsule v3.1 | report + capsule | No |
| 584 | Window 575-584 closure gate and handoff | gate script + handoff | YES |

## 4. Locked implementation decisions

The following implementation decisions are locked for the full window:
- Window 575-584 is the RC0.1 testnet economics and agent-loop window, not the
  public-release closure window.
- LMDB-backed public runtime state remains the active durable storage base for
  RC0.1 graph, ledger, and wallet-read surfaces; this window does not reopen
  the storage-engine choice.
- The already-landed bounded implementation baseline for Phases 579-581
  includes `tools/agent_loop_v1.py`, `tools/query_rc0_1_economic_state.py`,
  `tools/run_rc0_1_economic_proof.py`, and the LMDB-backed runtime state;
  Phases 579-581 harden and authorize cutover over this baseline rather than
  reopen greenfield design.
- `settlement_wallet_boundary_precedes_agent_loop_runtime`.
- `persisted_graph_contract_precedes_live_submission_cutover`.
- `curated_genesis_lineage_testnet_only` remains the lineage posture for this
  operator-managed testnet.
- `wallet_visibility_accounting_only_in_rc0_1` remains the wallet boundary.
- `cdl_v7_reproducibility_disposition_required_before_phase_584`.
- `outbound_http_machine_payment_skill_support_lane_only`; it may land in this
  window or close as an explicit defer without invalidating the RC0.1 testnet
  gate.
- Inbound `HTTP machine-payment ingress` remains out of scope.
- `public_genesis_and_minting_stabilization_deferred_to_585_plus`.
- `no_public_release_claim_before_585_594`.

## 5. Carry-forward inputs from Window 565-574

The following carry-forwards are locked into this window:
- Server TLS plus `ILC-Signature` remains the active posture.
- Mutual TLS remains deferred.
- Automatic fallback remains deferred.
- Dynamic discovery, DHT, and multi-hop remain deferred.
- The three-machine substrate remains the active RC0.1 execution base.

## 6. Protected boundaries and anti-pattern exclusions

The following constraints are non-negotiable for Window 575-584:
- No treating RC0.1 testnet closure as equivalent to RC0.1+ public-release closure.
- No reopening D2d transport governance.
- No permissionless public admission.
- No mTLS as a closure criterion.
- No automatic fallback negotiation.
- No public-routing/privacy redesign.
- No silent widening of minting or founder/governance semantics.
- No treating harness-specific integrations as ILC correctness dependencies.
- No blurring wallet visibility/accounting with spend/transfer semantics.

## 7. Sequence integrity rule

Window 575-584 must execute in this order:
1. Phase 575 sequence lock.
2. Phase 576 RC0.1 settlement + wallet boundary lock.
3. Phase 577 RC0.1 persisted graph contract lock.
4. Phase 578 RC0.1 curated genesis/bootstrap lineage lock.
5. Phase 579 agent behavioral loop runtime cutover.
6. Phase 580 7+1 panel and live submission integration.
7. Phase 581 ECU attribution, settlement, and wallet query integration.
8. Phase 582 reproducibility disposition and outbound HTTP machine-payment skill
   defer-or-attach.
9. Phase 583 coherence report and capsule v3.1.
10. Phase 584 closure gate and handoff.

This ordering prevents runtime integration from hardening against ambiguous
economic or graph semantics and preserves a clean handoff into the public
stabilization lane after the RC0.1 testnet gate is complete.
