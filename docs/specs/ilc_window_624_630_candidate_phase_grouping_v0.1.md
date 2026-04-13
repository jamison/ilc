# ILC Window 624-630 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-13
Owner lane: G8 ECU active economic layer runtime strike force
Classification: planning surface — not canonical law until sequence lock is committed

`window_624_630_candidate_grouping_v0_1`

## 1. Window identity and basis

Window 624-630 is the ECU Active Economic Layer runtime strike-force window.
Its purpose is to:
- ratify `CDL-063`,
- implement bounded directed-commission earmark and debit runtime,
- harden that runtime through a dedicated post-implementation gate,
- close the debit-side gap surfaced by Phase 622 without widening the wallet or
  collapsing ECU into ILC.

This window runs in parallel to Window 623+ (MVP touchpoints interface/runtime
closure). Neither window blocks the other, and Window 623+ remains the
highest-priority continuation for the MVP package.

**Authorization basis:**
- Human authorization 2026-04-13: the Phase 622 debit-side gap was identified
  as the next active constitutional/runtime target for agent economic agency.
- Human authorization 2026-04-13: `Disposition B` was rejected for this lane;
  runtime deferral is not an acceptable window outcome.
- `CDL-063` is authorized as the narrow constitutional vehicle for bounded
  directed-commission earmark and debit semantics.
- AG-8 named-vehicle rule remains satisfied and is strengthened here by a
  runtime-hardening requirement before the window may claim live enforcement.
- `CDL-062` remains not opened; `CDL-063` is the next available number.

`window_624_630_requires_window_620_622_complete`
`disposition_b_not_permitted_window_624_630`

**Minimum guaranteed change after this window closes:**
- `CDL-063` is ratified.
- A bounded internal ECU active-layer runtime exists for earmark proposal,
  acceptance, delivery, expiry, debit-at-epoch-commit, and query/history.
- A dedicated hardening gate has passed before closure.

## 2. Pre-window prerequisite

Window 620-622 must be fully closed and its tests must pass before Phase 624
begins. Phase 622 (`bounded_ecu_exchange_model_622_locked`) is the direct
topology predecessor that this window upgrades from spec-form-only coordination
to bounded runtime-enforced internal economic agency.

## 3. Phase map

### Phase 624 — Window 624-630 Sequence Lock (SENSITIVE)

**Type:** SENSITIVE — sequence lock  
**Primary output:** `docs/specs/ilc_phase_624_630_sequence_lock_v0.1.md`

**Mission:** Lock the runtime strike-force window, name `CDL-063` as the
constitutional vehicle, forbid `Disposition B`, and require a dedicated runtime
hardening gate before closure.

---

### Phase 625 — Architecture Scoping + CDL-063 Opening Stub

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md`
- CDL-063 opening stub row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`

**Mission:** Resolve the three architectural questions for bounded earmark and
debit semantics:
1. earmark mechanics and reserved-balance accounting,
2. anti-gaming invariants and enforcement boundary,
3. attribution non-inflation.

---

### Phase 626 — Prelock Hardening + SIM-COMMISSION-01

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md`
- `docs/specs/ilc_sim_commission_01_earmark_expiry_calibration_626_v0.1.md`
- `tests/test_phase_626_cdl_063_ecu_directed_commission_prelock.py`

**Mission:** Harden the scoping answers into constitutional-prelock clauses and
calibrate expiry/volume-cap parameters for the bounded active layer.

---

### Phase 627 — CDL-063 Ratification Evidence

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_cdl_063_ecu_directed_commission_ratification_evidence_627_v0.1.md`
- `tests/test_phase_627_cdl_063_ecu_directed_commission_ratification.py`
- CDL-063 row updated: `status: open` -> `status: ratified`

**Mission:** Ratify bounded directed-commission earmark and debit semantics into
constitutional law without widening into generalized transferability.

---

### Phase 628 — ECU Active Layer Runtime Implementation and Accounting Spec

**Type:** Runtime strike-force implementation  
**Primary outputs:**
- `docs/specs/ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md`
- `tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py`
- `tests/test_ecu_active_layer_runtime.py`
- runtime module(s) under `ilc_core/ledger/` for bounded ECU active-layer semantics

**Mission:** Implement the bounded runtime. This phase must land complete,
passing runtime behavior for:
- earmark propose,
- accept,
- deliver,
- commit-bound debit,
- expiry release,
- status/history queries.

`Disposition B` is not permitted in this window.

---

### Phase 629 — ECU Active Layer Runtime Hardening Gate

**Type:** Runtime hardening / strike-force closure gate  
**Primary outputs:**
- `docs/specs/ilc_ecu_active_layer_runtime_hardening_gate_629_v0.1.md`
- `tests/test_phase_629_ecu_active_layer_runtime_hardening_gate.py`
- `tests/test_ecu_active_layer_runtime_hardening.py`
- `tools/run_window_624_630_runtime_hardening_gate_phase_629.sh`

**Mission:** Run the dedicated hardening gate for the Phase 628 runtime, apply
Fix-1..N if required within the phase, and refuse closure unless the runtime is
stable and the bounded invariants hold under the hardening suite.

---

### Phase 630 — Coherence Report + Capsule Update + Window Closure

**Type:** Non-sensitive  
**Primary outputs:**
- `docs/specs/ilc_window_624_630_coherence_report_630_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.4.md`
- `docs/specs/ilc_window_624_630_handoff_630_v0.1.md`

**Mission:** Close the strike-force window after ratification, runtime
implementation, and runtime hardening are all complete. Update capsule and
handoff without changing Option-D posture, wallet boundary, or sovereign
substrate status.

## 4. Window-level constraints

All phases share:
- No decision-log mutation except the `CDL-063` row (opening in Phase 625,
  ratification update in Phase 627 only)
- No `CDL-062` opening
- No Option-B selection claim
- No ILC transferability
- No generalized ECU transfer between arbitrary parties
- No external purchasing power claim
- No wallet-write widening or participant-visible wallet expansion beyond the
  read-only Phase 576/581 boundary
- Window 623+ remains independent and highest-priority for the MVP runtime lane
- Phase 629 hardening gate is mandatory before Phase 630 closure

## 5. CDL-063 constitutional scope boundary

**In scope for CDL-063:**
- bounded directed commission,
- bounded earmark reservation against accrued ECU,
- debit at epoch commit following valid delivery,
- expiry release,
- same-key self-commission prohibition and bounded anti-gaming invariants,
- attribution non-inflation,
- machine-legible internal runtime interfaces for the bounded loop.

**Explicitly out of scope for CDL-063:**
- ILC transferability,
- generalized ECU transfer,
- public claimability,
- wallet write authority,
- external purchases,
- sovereign substrate execution,
- Option-B graduation.

## 6. AG-gate preview

| Gate | Preview | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Agents gain bounded internal economic agency with live runtime, not topology only |
| AG-2 W_e increase | advance | Directed commission can route effort toward higher-value graph work |
| AG-3 Epistemic integrity | pass | Popperian validation remains mandatory; commissions do not bypass graph admission |
| AG-4 ECU-ILC separation | pass (critical) | ECU debit remains internal measurement-layer semantics; no ILC payment path |
| AG-5 Harness-agnostic | neutral | Runtime is protocol-level and machine-legible, not harness-owned |
| AG-6 Near-infinite scale | pass | Reserved-balance and expiry rules bound state growth without central approvals |
| AG-7 Machine-legible first | advance | Earmark interfaces, state machine, and gate outputs are machine-legible |
| AG-8 Outbound economic loop | advance | Named vehicle, runtime implementation, and hardening gate all required in-window |

## 7. Relationship to Window 623+

Window 624-630 and Window 623+ are independent parallel lanes.

Window 623+ remains the highest-priority continuation for the MVP touchpoints
runtime. Window 624-630 does not prescribe or block that sequence. Once the
active-layer runtime and hardening gate close, Window 623+ or a later bounded
runtime-only phase may consume `CDL-063` and the Phase 628 runtime surface where
that integration is useful.
