# ILC Window 575-584 Candidate Phase Grouping v0.1

Status: candidate phase grouping - pre-sequence-lock
Date: 2026-04-03
Owner lane: G8 implementation cluster

This document translates the completed three-machine substrate into the next
bounded window. Window 575-584 is the RC0.1 testnet-economics and agent-loop
window. It must not silently widen into the public-release constitutional lane.

---

## 1. Window purpose

Window 575-584 operationalizes the live agent and economic path on top of the
already-passing three-machine substrate.

This window has two maturity tiers:

- RC0.1 testnet lane: settle the wallet/settlement boundary, persist the minimum
  graph contract, lock curated genesis/bootstrap lineage for the testnet, and
  then wire the live agent loop, 7+1 panel, ECU attribution, and durable wallet
  query surface.
- RC0.1+ public-release lane: public genesis governance stabilization, minting
  economics stabilization, receipt/payout traceability, and other public-facing
  constitutional closure are explicitly deferred beyond this window.

These tiers are related but not equal. Window 575-584 closes only the RC0.1
testnet lane. It may prepare the public-release lane, but it must not claim to
finish it.

---

## 2. Decisions locked before Phase 575

### 2.1 Carry-forward infrastructure posture

- The three-machine substrate from Window 565-574 remains the execution base.
- Server TLS plus `ILC-Signature` remains the active posture.
- Mutual TLS remains deferred.
- `kind=http` remains the proven testbed transport path; no new transport
  governance is reopened in this window.
- LMDB-backed public runtime state remains the durable storage base for the
  curated testnet ledger, graph, and wallet-read surfaces.
- The bounded implementation baseline already includes `tools/agent_loop_v1.py`,
  `tools/query_rc0_1_economic_state.py`, `tools/run_rc0_1_economic_proof.py`,
  and LMDB-backed runtime state; Phases 579-581 convert this baseline into the
  authoritative live path rather than reopening greenfield design.

### 2.2 RC maturity split

- RC0.1 in this window means bounded public code release for a curated,
  operator-controlled testnet.
- RC0.1 in this window does not imply permissionless public admission,
  hostile-network privacy guarantees, or finalized public minting governance.
- RC0.1+ public-release closure is a separate lane and must remain explicitly
  marked as such in all forward planning.

### 2.3 Boundary decisions

- Settlement/wallet semantics must be locked before agent-loop runtime work is
  considered complete.
- The minimum persisted graph contract must be locked before live submission
  cutover is treated as authoritative.
- Curated genesis/bootstrap lineage for the testnet must be locked before
  public-release lineage or minting questions are opened.
- The outbound `HTTP machine-payment skill` remains a support lane in this
  window, not the primary pass condition.
- Inbound `HTTP machine-payment ingress` remains out of scope.
- The bounded CDL-V7 reproducibility disposition remains required before window
  closure; the outbound support lane may land in this window or close as an
  explicit defer without invalidating the RC0.1 testnet gate.

---

## 3. Hard pass condition for Window 575-584

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
6. The window does not claim public genesis-governance stabilization, open
   public admission, or finalized public minting semantics.
7. The bounded CDL-V7 reproducibility disposition is explicit and does not leave
   the agent loop falsely described as protocol-complete by silence.
8. The outbound `HTTP machine-payment skill` lane, if landed in this window,
   remains clearly secondary to the agent/economic proof path; if deferred, the
   defer is explicit in the coherence report and handoff.

---

## 4. Deliverables and test gates

### 4.1 Constitutional pre-runtime lock deliverables

Deliverables:
- Settlement + wallet boundary lock
- Persisted graph contract lock
- Curated genesis/bootstrap lineage lock

Test gates:
- Each lock artifact has explicit scope, non-goals, and exact carry-forward
  boundary to later windows.
- No lock artifact silently mutates CDL status or reopens transport governance.

### 4.2 Runtime and economic proof deliverables

Deliverables:
- Agent loop runtime cutover over the live three-machine substrate
- 7+1 panel submission wiring
- ECU attribution flow integrated with durable settlement
- Wallet query surface over live runtime state
- Multi-cycle economic proof artifacts

Test gates:
- Live cycle emits deterministic graph, ledger, and wallet artifacts.
- Replay/idempotency checks prove no balance drift on repeated settlement.
- Runtime-store negative paths fail closed with deterministic tokens.
- RC gate and release claim consume the economic proof outputs directly.

### 4.3 Support-lane deliverables

Deliverables:
- Required bounded CDL-V7 reproducibility disposition for the agent loop
- Optional outbound `HTTP machine-payment skill` attachment through the existing
  CLI/MCP boundary
- Coherence report and handoff

Test gates:
- Reproducibility disposition is present before closure and does not silently
  widen into a broader governance reopening.
- Outbound support-lane work does not become a correctness dependency for the
  economic path.
- Harness-specific work remains harness-agnostic at the ILC core boundary.

---

## 5. Candidate phase map

### Phase 575 - Window 575-584 sequence lock

Purpose:
- Freeze the RC0.1 testnet scope, hard pass condition, and 10-phase execution
  order.

### Phase 576 - RC0.1 settlement + wallet boundary lock

Purpose:
- Lock what settlement means in RC0.1 and what the wallet is allowed to claim
  in this window.

### Phase 577 - RC0.1 persisted graph contract lock

Purpose:
- Lock the minimum durable graph record set required for runtime and proof work.

### Phase 578 - RC0.1 curated genesis/bootstrap lineage lock

Purpose:
- Lock canonical lineage, curated bootstrap rules, and key-compromise posture
  for the testnet fleet only.

### Phase 579 - Agent behavioral loop runtime cutover

Purpose:
- convert the already-landed bounded agent-loop runtime into the authoritative
  live cutover path over the three-machine substrate.

### Phase 580 - 7+1 panel and live submission integration

Purpose:
- harden the existing panel and submission scaffolding into the authoritative
  live panel/quorum submission path and persist the resulting runtime artifacts.

### Phase 581 - ECU attribution, settlement, and wallet query integration

Purpose:
- harden the existing durable economic and wallet-query surfaces into the
  authoritative live settlement path over runtime state.

### Phase 582 - Reproducibility disposition + outbound HTTP machine-payment skill

Purpose:
- Close the bounded reproducibility/governance posture for the agent loop and
  attach the outbound support lane if it lands in this window, without widening
  the correctness boundary.
- Any later harness/operator product work (for example onboarding helpers or
  budget-aware mining modes) remains a separate post-582 lane over stable
  protocol surfaces and is not part of this window's correctness gate.

### Phase 583 - Coherence report and capsule v3.1

Purpose:
- Record the full post-integration state of the testnet RC lane.

### Phase 584 - Window 575-584 closure gate and handoff

Purpose:
- Close the window only if the economic agent-loop gate has passed and the
  public-release carry-forward set is explicit.

---

## 6. Protected boundaries and anti-pattern exclusions

This window must not:

- treat RC0.1 testnet closure as equivalent to RC0.1+ public-release closure
- reopen D2d transport governance
- introduce permissionless public admission
- introduce mTLS, automatic fallback negotiation, or public-routing/privacy
  redesign as closure criteria
- treat harness-specific integrations as ILC correctness dependencies
- blur wallet visibility/accounting with spend/transfer semantics
- silently widen founder/genesis or minting-governance semantics without an
  explicit public-release packet

---

## 7. Relationship to existing artifacts

- `docs/specs/ilc_window_565_574_handoff_574_v0.1.md` - completed carry-forward
  from the infrastructure window
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md` -
  historical roadmap anchor for the agent-loop lane
- `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md` - current RC readiness
  surface
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` - accepted
  protocol-vs-harness boundary for post-582 work
- `docs/specs/ilc_post_582_harness_sdk_lane_v0.1.md` - post-582 harness/operator
  planning lane
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md` - forward
  public-release constitutional closure guidance window
- `docs/specs/ilc_agent_native_rc0_1_guidance_synthesis_v0.1.md` - agent-native
  RC framing
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md` - normalized
  constitutional packet map used to derive this candidate grouping

---

## 8. Bottom line

Window 575-584 is the RC0.1 testnet economics and agent-loop window.

It should leave behind:
- a live, durable, queryable economic path on the three-machine substrate,
- a clear RC0.1 wallet and graph contract,
- and an explicit handoff into RC0.1+ public-release constitutional closure.
