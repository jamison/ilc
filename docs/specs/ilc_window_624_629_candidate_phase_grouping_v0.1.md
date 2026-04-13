# ILC Window 624-629 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-13
Owner lane: G8 ECU active economic layer
Classification: planning surface — not canonical law until sequence lock is committed

`window_624_629_candidate_grouping_v0_1`

## 1. Window identity and basis

Window 624-629 is the ECU Active Economic Layer strike-force window. Its purpose
is to ratify CDL-063, give agents genuine bounded debit authority over their own
accrued ECU, and deliver a runtime/accounting spec for the directed-commission
loop that Phase 622 described in topology form only.

This window runs in parallel to Window 623+ (MVP touchpoints interface/runtime
closure). Neither window blocks the other.

**Authorization basis:**
- Human authorization 2026-04-13: the debit-side gap in Phase 622 was explicitly
  identified and approved as the next active constitutional design target; CDL-063
  was authorized as the vehicle; Window 624-629 was authorized as the strike-force
  lane
- AG-8 named-vehicle rule (prospective, from Window 624 forward): Phase 624 must
  name CDL-063 as the vehicle for the debit side and commit to ratification within
  this window
- CDL-062 remains not opened; CDL-063 is the next available number

**What changes for agents after this window:**
Minimum guaranteed change: agents gain ratified, machine-legible earmark and
bounded-debit semantics in constitutional/spec form rather than topology-only
description. If Phase 628 uses a runtime-implementation disposition, a
commissioning agent can hold a bounded spendable ECU balance, earmark a declared
portion toward a named commission, and have that earmark debited upon delivery
confirmation at epoch commit. If Phase 628 uses a deferred-runtime disposition,
those semantics are authorized and specified but not yet live in runtime.

## 2. Pre-window prerequisite

Window 620-622 must be fully closed and its tests must pass before Phase 624
begins. Phase 622 (`bounded_ecu_exchange_model_622_locked`) is the direct
predecessor that established the commission topology this window enforces.

`window_624_629_requires_window_620_622_complete`

## 3. Phase map

### Phase 624 — Window 624-629 Sequence Lock (SENSITIVE)

**Type:** SENSITIVE — sequence lock
**Primary output:** `docs/specs/ilc_phase_624_629_sequence_lock_v0.1.md`

**Mission:** Lock Window 624-629 as the ECU active economic layer lane. Name
CDL-063 as the constitutional vehicle. Confirm that Window 623+ is independent
and not blocked. Record AG-gate design basis with AG-8 named-vehicle rule
satisfied.

---

### Phase 625 — Architecture Scoping + CDL-063 Opening Stub

**Type:** Non-sensitive
**Primary outputs:**
- `docs/specs/ilc_ecu_active_economic_layer_architecture_scoping_625_v0.1.md`
- CDL-063 opening stub row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`

**Mission:** Answer the three architectural questions that must be resolved before
CDL-063 can be ratified:
1. Earmark mechanics and balance accounting model
2. Anti-gaming constraints (arm's-length, Popperian bypass prevention, expiry)
3. Attribution non-inflation proof

CDL-063 row title: *ECU Directed-Commission Earmark and Bounded Debit Semantics*
CDL-063 dependency chain: CDL-027 (issuance epoch cadence), CDL-044 (retention
epochs), Phase 622 (`bounded_ecu_exchange_model_622_locked`), Phase 550 passive
ECU attribution values

---

### Phase 626 — Prelock Hardening + SIM-COMMISSION-01

**Type:** Non-sensitive
**Primary outputs:**
- `docs/specs/ilc_cdl_063_ecu_directed_commission_prelock_626_v0.1.md`
- `docs/specs/ilc_sim_commission_01_earmark_expiry_calibration_626_v0.1.md`
- `tests/test_phase_626_cdl_063_ecu_directed_commission_prelock.py`

**Mission:** Harden the three scoping answers into prelock-form constitutional
clauses. Run SIM-COMMISSION-01 to calibrate the earmark expiry horizon.

**SIM-COMMISSION-01 question:** What is the right earmark expiry horizon in
validation epochs? Too short and legitimate long-horizon commissions expire. Too
long and earmarks function as locked reserves that reduce effective network
liquidity. The simulation should produce a recommended range (minimum, nominal,
maximum) expressed in validation epochs.

---

### Phase 627 — CDL-063 Ratification Evidence

**Type:** Non-sensitive
**Primary outputs:**
- `docs/specs/ilc_cdl_063_ecu_directed_commission_ratification_evidence_627_v0.1.md`
- `tests/test_phase_627_cdl_063_ecu_directed_commission_ratification.py`
- CDL-063 row updated: `status: open` → `status: ratified`

**Mission:** Produce the ratification evidence artifact that closes CDL-063. The
ratification evidence must document all three scoping answers in final form,
consume the SIM-COMMISSION-01 calibration for the expiry parameter, and close
the two-commit ratification pattern (runtime artifacts deferred to Phase 628).

---

### Phase 628 — ECU Active Layer Runtime and Accounting Spec

**Type:** Non-sensitive
**Primary outputs:**
- `docs/specs/ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md`
- `tests/test_phase_628_ecu_active_layer_runtime_and_accounting_spec.py`

**Mission:** Produce the runtime and accounting spec for the CDL-063-ratified
semantics. Define the earmark state machine, the epoch-settled accounting model,
and the machine-legible interfaces for the full loop. This is spec-form; runtime
implementation wires into the existing epoch commit machinery (Window 623+ runtime
or a subsequent runtime-only phase).

---

### Phase 629 — Coherence Report + Capsule Update + Window Closure

**Type:** Non-sensitive
**Primary outputs:**
- `docs/specs/ilc_window_624_629_coherence_report_629_v0.1.md`
- Updated context capsule (v3.4 or next version)
- `docs/specs/ilc_window_624_629_handoff_629_v0.1.md`

**Mission:** Synthesize the window. Confirm CDL-063 ratified, record whether
AG-8 loop enforcement is live in runtime or remains deferred by Phase 628
disposition, and record what remains deferred (ILC transferability, external
purchasing power, Window 623+ runtime). Update capsule. Produce handoff for the
next window.

## 4. Window-level constraints

All phases share:
- No decision-log mutation except the CDL-063 row (opening in Phase 625,
  ratification update in Phase 627)
- No ilc_core/ mutation until Phase 628 runtime spec; Phase 628 may produce
  ilc_core/ changes if the runtime spec requires them, but only for the earmark
  accounting model — no wallet widening
- No CDL-062 opening
- No Option B selection claim
- No ILC transferability or wallet-write widening
- No external purchasing power claim
- Window 623+ runtime is not blocked, sequenced, or prescribed by this window

## 5. CDL-063 constitutional scope boundary

**In scope for CDL-063:**
- Bounded earmark: Agent A may reserve up to their unearmarked accrued ECU as a
  directed commission toward a named Agent B task
- Debit authority: upon delivery confirmation at epoch commit, Agent A's accrued
  ECU is debited by the earmarked amount
- Expiry: an unconfirmed earmark expires after SIM-COMMISSION-01 calibrated
  horizon; expired earmark returns to Agent A's unearmarked balance
- Anti-gaming: arm's-length requirement; Popperian validation still required;
  self-commission prohibited
- Attribution non-inflation: Agent B's W_e attribution comes from the validated
  contribution alone; the commission earmark does not inflate B's credit above
  what the contribution merits

**Explicitly out of scope for CDL-063:**
- ILC transferability (CDL-062 domain, not authorized)
- Generalized ECU transfer between arbitrary parties (only directed commission)
- External purchasing power
- Wallet write widening
- Settlement substrate selection (ADR-0028 / Option B graduation checklist)

## 6. AG-gate window preview

| Gate | Preview | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Genuine agent economic agency, not just topology |
| AG-2 W_e increase | advance | Directed commission incentivizes specialized contribution to higher-W_e tasks |
| AG-3 Epistemic integrity | pass | Popperian validation still required for all commissioned contributions |
| AG-4 ECU-ILC separation | pass (critical) | ECU debit is internal measurement-layer operation; CDL-063 explicitly not ILC payment |
| AG-5 Harness-agnostic | neutral | Protocol-level accounting; no harness dependency |
| AG-6 Near-infinite scale | pass | Bounded by individual accrual authority; no central approval bottleneck |
| AG-7 Machine-legible first | advance | Earmark state machine and epoch-settled accounting are protocol messages |
| AG-8 Outbound economic loop | advance | Named-vehicle rule satisfied: CDL-063 is the vehicle, this window is the target |

## 7. Relationship to Window 623+

Window 624-629 and Window 623+ are independent parallel lanes.

Once CDL-063 is ratified (Phase 627), Window 623+ runtime work can consume
CDL-063 semantics when wiring the ECU accrual surfaces in the MVP touchpoints
runtime. This is an additive dependency — Window 623+ does not need to wait for
CDL-063, but if CDL-063 is ratified first, the runtime work can wire earmark
accounting in the same pass.
