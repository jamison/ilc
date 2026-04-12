# ILC Window 607-612 Handoff 612 v0.1

Status: handoff artifact
Date: 2026-04-12
Classification: closure and carry-forward handoff

---

## 1. Window identity and closure basis

Window 607-612 is the G8 settlement-substrate reconciliation lane. It is closed
by Phase 612, on the basis of the Phase 611 memo-plus-ADR governance vehicle
selection and `ADR-0028`.

The closure phase is Phase 612. The verdict source is the Phase 612 closure memo
at `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`.

The authoritative closure inputs used are:
- Phase 611 governance memo (`docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`)
- `ADR-0028` (`docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`)
- Phase 612 closure memo (the six-section bespoke phase memo defined by the Phase 612 prompt)

The window closed without decision-log mutation. No `CDL-062` opening occurred.
No `ilc_core/` changes were made.

## 2. Inputs and closure inheritance

**Sequence lock:** `docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md`

**Phase closure artifacts:**
- Phase 607: `docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md`
- Phase 608: `docs/specs/ilc_settlement_substrate_historical_lineage_audit_608_v0.1.md`,
  `docs/specs/ilc_settlement_substrate_authority_tier_classification_608_v0.1.md`
- Phase 609: `docs/specs/ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md`
- Phase 610: `docs/specs/ilc_public_ledger_substrate_options_and_rejection_matrix_610_v0.1.md`
- Phase 611: `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`,
  `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- Phase 612: `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`

**Governing ADR:** `ADR-0028` — Settlement Substrate Graduation and Governance Route

**Active capsule reference:** Capsule v3.2 (Phase 604) carries the bounded RC0.1
posture that this window refined and bounded further.

**Prior closure artifact:** `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
(predecessor window closure)

## 3. Closure verdict summary

**What closed:**
- The settlement-substrate historical lineage was audited and authority tiers were
  classified (Phase 608).
- ECU, ILC, and the current RC/runtime posture were separated and bounded without
  selecting a final substrate (Phase 609).
- Four substrate paths were evaluated; `Option D` was kept as the near-term
  posture; `Option B` and `Option C` were deferred as later viable paths; `Option A`
  was rejected (Phase 610).
- The memo-plus-ADR governance vehicle was selected as the lowest-authority
  sufficient route; `ADR-0028` was accepted; the `Option B` graduation checklist
  and blocker matrix were published (Phase 611).
- The minimum participant-touch package was defined; downstream lane sequencing
  was locked; the MVP gate was established as a strict precondition before
  sovereign substrate execution (Phase 612).

**What remained deferred:**
- Final public settlement substrate ratification: not selected and not
  ratified. `Option D` remains the active bounded bridge.
- `CDL-062` opening: not authorized by `ADR-0028` or Phase 612.
- Privacy-preserving public legitimacy mechanism: rule locked, mechanism
  unresolved.
- Sovereign substrate selection: deferred until the `Option B` graduation
  checklist is satisfied.
- Coupling invariants final governance lock: carried forward as a partial-state
  item.

**Scope explicitly blocked throughout:**
- No wallet widening authorized.
- No payment runtime authorized.
- No chain implementation authorized.
- No decision-log mutation in this window.

## 4. Carry-forward items and residual blockers

**Closed and not carried forward:**
- The ECU/ILC conflation in prior wallet-handoff language (Phase 609 resolution).
- The ambiguity between bounded current runtime posture and final-substrate
  closure (Phase 607/609 resolution).
- The gap in the governance routing contract for `Option D` → `Option B`
  graduation (Phase 611/ADR-0028 resolution).

**Carried-forward items:**
- Minimum participant-touch package: five touchpoints (init/admission, receipt
  issuance/query, ECU visibility, delayed ILC visibility, wallet/query) must be
  closed in spec and interface/runtime form before broader public RC claims.
- `Option B` graduation checklist (Phase 611 Section 5): nine criteria at various
  partial/not-started states. Graduation requires all criteria satisfied plus
  explicit human authorization.
- Blocker matrix (Phase 611 Section 6): eight blockers across class A, B, and C.
  Class A blockers are closable with governance/spec work in the first post-612
  windows. Class B and C blockers follow from those.
- ADR-0028 governing rules: carry forward as the durable routing contract for any
  later `Option B` selection.

**Blocked items requiring future routing:**
- Public init/admission flow contract: blocker class A, owner lane
  public-legitimacy spec lane, earliest phase is the first post-612 spec window.
- Machine-legible public receipt runtime: blocker class B, owner lane
  receipt/runtime lane, depends on first post-612 spec lane outputs.
- Public wallet surface beyond read-only accounting: blocker class B, depends on
  governance-selected routing.
- Privacy-preserving public legitimacy mechanism: blocker class C, depends on
  Phase 611 route and later substrate decision.
- Sovereign substrate selection: blocker class C, depends on graduation checklist
  completion.

## 5. Next-window entry criteria and routing

**What the next window may assume:**
- `Option D` is the active near-term posture.
- `Option B` is not selected.
- `CDL-062` is not open.
- No wallet widening has been authorized.
- No payment runtime has been authorized.
- No chain implementation is in scope.
- The RC0.1 work from Window 575-584 (Phase 581 forward) was deferred for this
  window and must be resumed.
- The `ADR-0028` graduation rules are the controlling carry-forward contract.

**What still requires explicit confirmation:**
- Any departure from `Option D` requires explicit satisfaction of the Phase 611
  graduation checklist plus human authorization with GO-token handling.
- Any `CDL-062` opening requires demonstration of `ADR-0028` Section 4
  conditions plus explicit human authorization.
- Any wallet widening, payment runtime, or chain implementation requires explicit
  new authorization, not inherited from this window.

**Lane routing for unresolved items:**
- RC lane: resume at Phase 581 (in-flight, execution priority).
- First post-612 spec lane: public init/admission contract and visible ECU-to-ILC
  lifecycle contract (authorized now, independent of RC lane completion).
- First post-612 interface/runtime lane: receipt, wallet, and transport work
  (follows first post-612 spec lane outputs).
- Later public-legitimacy mechanism lane and later sovereign substrate selection
  lane: blocked on blocker-class B/C prerequisites, not openable until the MVP
  gate is satisfied.

## 6. MemPalace refresh disposition

Disposition: required
Active working set impacted: yes
Basis: Window 607-612 added seven new spec artifacts (Phase 607-612 memos plus
ADR-0028) covering the settlement substrate reconciliation lane. The active
working set did not previously include these artifacts. The planning surface
changed substantially enough that retrieval briefing for Phase 581 and the first
post-612 spec lane work should draw from the updated frontier.

Working-set descriptor: `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
Manifest: `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
Rebuild command: `bash tools/mempalace/build_active_working_set.sh`
