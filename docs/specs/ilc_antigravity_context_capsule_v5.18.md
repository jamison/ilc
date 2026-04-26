# ILC Antigravity Context Capsule v5.18

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.17.md
Date: 2026-04-26
Owner lane: Window 839–843 — Row 8 substrate candidate evaluation and Option B gate re-synthesis

`capsule_v5_18_supersedes_v5_17`
`option_b_gate_synthesis_verdict_go_recorded_in_capsule_v5_18`
`option_b_selectable_not_selected`
`option_d_remains_active_posture_until_explicit_graduation`
`row8_substrate_candidate_evaluation_complete`
`high_002_production_hardening_planned`
`first_validator_deployment_human_gate_not_yet_pulled`
`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

This capsule is self-contained.

## 1. Current Frontier State

**Window 839–843 — COMPLETE.**

All five phases complete:

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 839 | Sequence lock | Baseline verified, five-phase budget locked |
| 840 | Row 8 substrate candidate evaluation | ILC Native Minimal L1 passes Phase 673 + 675 criteria |
| 841 | Option B gate re-synthesis | `option_b_gate_synthesis_verdict=go` — selectable, not selected |
| 842 | HIGH-002 production hardening planning | Phase A + Phase B path authorized |
| 843 | Coherence report + capsule v5.18 + closure gate | This document |

**Option B gate:** `go`. Option B is now **selectable**. It is not selected.
Option D remains the active architectural posture until an explicit, deliberate,
human-authorized Option B selection act occurs.

**Prior state (v5.17) preserved:** CDL-069 ratified (Phase 838j), all prior
Phase 826 entry conditions satisfied. First-validator human gate not yet pulled.

## 2. Option B Gate Status

**Gate verdict:** `option_b_gate_synthesis_verdict=go` (Phase 841).

Both CW-5 blockers discharged:

| Blocker | Resolution |
|---------|------------|
| CDL-017 ratification | ✅ Ratified Phase 765 |
| Row 8 substrate candidate evaluation | ✅ Discharged Phase 840 |

ADR-0028 Phase 812 amendment: Row 5 is a parallel-obligation row — selection
is permitted with Row 5 explicitly acknowledged open and obligation intact.

**Row 5:** `spec_closed_runtime_pending`. Obligation intact. SIM-LEAKAGE-03
live run still required before `runtime_closed`. Blocked on Rust privacy lane
integration gate (human decision).

**Selecting Option B** is a separate future deliberate act requiring explicit
human authorization. This capsule does not record that act.

## 3. CDL Status (relevant)

| CDL | Status | Phase |
|-----|--------|-------|
| CDL-001 | Open (genesis_blocker, bounded for packaging) | — |
| CDL-017 | **Ratified** | 765 |
| CDL-042 | Ratified | 407 |
| CDL-068 | Ratified | 743 |
| CDL-069 | **Ratified** | 838j |
| CDL-070 | Not yet opened (forward PQ migration ceremony) | — |
| CDL-071 | Not yet opened (temporal tier reconciliation) | — |

## 4. ADR Status (relevant)

| ADR | Status |
|-----|--------|
| ADR-0028 | Accepted (amended Phase 812 — hard-closure / parallel-obligation row distinction) |

Row 7: `runtime_closed` ✅
Row 5: `spec_closed_runtime_pending` (parallel-obligation, carry-forward intact)
Row 8: `evaluation_complete` — ILC Native Minimal L1 candidate named and classified

## 5. HIGH-002 Production Hardening

`process_epoch_checkpoint` requires all-N signatures (all-N quorum). BFT-correct
threshold is `quorum_threshold(N) = 2 * floor((N-1)/3) + 1`.

At N=4: correct threshold is 3. One offline or Byzantine validator must not stall
liveness at production scale.

**Phase A** (Rust consensus fix + tests): authorized as the next
`ilc_consensus/` work. No CDL required. No `ilc_core/` mutation.

**Phase B** (M-track adversarial validation): authorized after Phase A.

**Gate dependency:** Phase A is mandatory before production N≥4, F≥1 deployment.
Not a blocker for controlled testnet deployment (Phase 826 §3 explicit carve-out).
Not a gate item for Option B selectability.

## 6. Identity and Endorsement Surface (unchanged from v5.17)

Three runtime layers govern the CDL-069 identity and endorsement protocol:

1. **Genesis ceremony layer** (`genesis_record_schema.py`): derives blinding
   factor, computes genesis record commitments, validates recovery transactions
   with freeze clamping.
2. **Endorsement packet schema layer** (`endorsement_packet_schema.py`): strict
   field validation, liveness assertion derivation, COSE_Sign1 payload
   construction.
3. **Validator runtime layer** (`epoch_endorsement_runtime.py`): sequence-number
   ordering, valid_epochs window enforcement, supersedes_epoch_id distributed
   atomicity, freeze/revocation, `EndorsementCache` eviction.

213 tests, all pass. Two audit rounds complete (commits c5dc9633, c8fd06a0).

Open item D1 (recovery spec wire format mismatch between Rust `pq_keygen` and
Python `encode_recovery_spec`) is non-blocking; CDL-070 resolution path.

## 7. First-Validator Deployment Readiness

Unchanged from v5.17. All code-verifiable Phase 826 entry conditions satisfied.
Human gate not pulled. CDL-069 ratification and Option B gate `go` verdict are
additive — neither changes the Phase 826 gate-pull conditions.

What remains:
1. Operator provisions validator keys, TLS material, genesis state, network ID,
   rollback plan (Phase 826 §6).
2. Live three-machine smoke proof passes all Phase 825 §5 criteria.
3. Human authorization record completed per Phase 826 §6.

## 8. Row 5 and SIM-LEAKAGE-03

Row 5 remains `spec_closed_runtime_pending`. The live run is still required
before `runtime_closed` can be recorded.

The live run requires: (1) Rust privacy lane integration gate (human decision);
(2) live `LeakageMetricsCollector` run against M-009 testbed; (3)
`check_bounds()` returning `{"A": True, "B": True, "C": True}`.

`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

## 9. Immediate Carry-Forward

**Operator-gated:**
1. Explicit Option B selection act (human-authorized deliberate act — separate from gate verdict).
2. First-validator human gate (Phase 826 §6 checklist).
3. Rust privacy lane integration gate → SIM-LEAKAGE-03 live run on M-009.

**Code-side (next window):**
1. HIGH-002 Phase A — Rust consensus fix: replace all-N quorum with
   `quorum_threshold(N)` in `process_epoch_checkpoint` (`ilc_consensus/src/validator/`).
2. HIGH-002 Phase B — M-track adversarial validation (after Phase A).

**Future CDL lanes:**
1. CDL-070 — PQ migration ceremony (D1 recovery spec wire format resolution path).
2. CDL-071 — temporal tier reconciliation.

## 10. Preserved Boundaries

- Option B not yet selected (gate `go` ≠ selection; Option D remains active posture),
- CDL-017 ratified (Phase 765); first non-Genesis validator deployment human-gated,
- Row 7 `runtime_closed` (Phases 759–760, Mysticeti convergence window),
- Row 5 `spec_closed_runtime_pending`,
- privacy lane not wired into live settlement,
- SIM-LEAKAGE-03 live run not yet executed,
- CDL-070 and CDL-071 not yet opened,
- HIGH-002 Phase A not yet implemented (`ilc_consensus/` fix is post-window).
