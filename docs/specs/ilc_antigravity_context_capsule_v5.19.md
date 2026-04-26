# ILC Antigravity Context Capsule v5.19

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.18.md
Date: 2026-04-26
Owner lane: Human decision log phase — posture correction and HIGH-002 closure

`capsule_v5_19_supersedes_v5_18`
`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`
`option_b_phase_841_gate_resynthesis_confirmed_go`
`high_002_closed_phase_a_3abd63e4_phase_b_53c4000d`
`first_validator_deployment_human_gate_not_yet_pulled`
`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

This capsule is self-contained.

## 1. Current Frontier State

**Window 839–843 — COMPLETE. HIGH-002 — CLOSED.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 839 | Sequence lock | Baseline verified, five-phase budget locked |
| 840 | Row 8 substrate candidate evaluation | ILC Native Minimal L1 passes Phase 673 + 675 criteria |
| 841 | Option B gate re-synthesis | `option_b_gate_synthesis_verdict=go` — gate satisfied |
| 842 | HIGH-002 production hardening planning | Phase A + Phase B path authorized |
| 843 | Coherence report + capsule v5.18 + closure gate | Window closed |
| HIGH-002 Phase A | Rust consensus fix | `quorum_threshold(N)` fix; 86/86 tests pass (commit `3abd63e4`) |
| HIGH-002 Phase B | M-track adversarial validation | 3-of-4 quorum live pass; HIGH-002 CLOSED (commit `53c4000d`) |

**Option B posture:** `adr_0028_posture=option_b`. Option B was selected by
explicit human authorization on 2026-04-23 (Phase 814). The Phase 823-829
sequence lock carried this forward (`option_b_selected_adr_0028_posture_confirmed`).
The Phase 841 gate re-synthesis correctly found gate conditions satisfied (`go`)
but its `option_b_selectable_not_selected` framing was an error of scope — the
gate re-synthesis did not see the Phase 814 selection from the parallel lane.
Capsule v5.18 inherited that error. This capsule corrects it.

**ILC Native Minimal L1** is the named sovereign settlement substrate candidate
(Phase 840). Option D is no longer the active posture.

## 2. Option B Status

**Selection:** recorded Phase 814 (2026-04-23), human-authorized.
`option_b_selected_by_human_authorization_2026_04_23`

**Gate verdict:** `option_b_gate_synthesis_verdict=go` (Phase 841, 2026-04-26).

Both CW-5 blockers discharged:

| Blocker | Resolution |
|---------|------------|
| CDL-017 ratification | ✅ Ratified Phase 765 |
| Row 8 substrate candidate evaluation | ✅ Discharged Phase 840 |

ADR-0028 Phase 812 amendment: Row 5 is a parallel-obligation row — selection
is permitted with Row 5 explicitly acknowledged open and obligation intact.

**Row 5:** `spec_closed_runtime_pending`. Obligation intact. SIM-LEAKAGE-03
live run still required before `runtime_closed`. Blocked on Rust privacy lane
integration gate (human decision, authorized after first-validator gate pull).

## 3. CDL Status (relevant)

| CDL | Status | Phase |
|-----|--------|-------|
| CDL-001 | Open (genesis_blocker, bounded for packaging) | — |
| CDL-017 | **Ratified** | 765 |
| CDL-042 | Ratified | 407 |
| CDL-068 | Ratified | 743 |
| CDL-069 | **Ratified** | 838j |
| CDL-070 | Deferred (PQ migration ceremony; not yet opened) | — |
| CDL-071 | Deferred (temporal tier reconciliation; not yet opened) | — |

CDL-070 and CDL-071 are deferred pending review at each window closure.
CDL-071 is higher user priority than CDL-070 when they are taken up.

## 4. ADR Status (relevant)

| ADR | Status |
|-----|--------|
| ADR-0028 | Accepted; posture = `option_b` (selected Phase 814, gate=go Phase 841) |

Row 7: `runtime_closed` ✅
Row 5: `spec_closed_runtime_pending` (parallel-obligation, carry-forward intact)
Row 8: `evaluation_complete` — ILC Native Minimal L1 candidate named and classified

## 5. HIGH-002 — CLOSED

HIGH-002 (all-N quorum stall in `process_epoch_checkpoint`) is closed.

**Phase A** (commit `3abd63e4`): `quorum_threshold(N) = 2*floor((N-1)/3)+1`
implemented in `validator.rs`. `EpochCheckpoint` and `StoredCheckpoint` gain
`signers: Vec<ValidatorID>`. `process_epoch_checkpoint` verifies: subset ≥
threshold, no duplicates, all signers in active set, BLS verify against subset
only. 86/86 tests pass.

**Phase B** (commit `53c4000d`): Live M-009 loopback run. V4 partitioned.
V1, V2, V3 committed epoch 1 with 3-of-4 quorum. SafetyNoDualCert unaffected.
Harness updated: silent/slow scenario passes 3 quorum keys, not 4.

Gate implication: HIGH-002 liveness caveat is cleared. The Phase 826 §6 gate
form acknowledgement "HIGH-002 remains debt" is superseded — HIGH-002 is closed.

## 6. Identity and Endorsement Surface (unchanged from v5.18)

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

All code-verifiable Phase 826 entry conditions satisfied. HIGH-002 is now closed
(supersedes the HIGH-002 liveness caveat in Phase 826 §6 form).

Human gate not yet pulled. What remains for gate pull:

1. Operator provisions validator keys, TLS material, network ID, rollback plan.
2. Machine identities for the first non-Genesis validator confirmed.
3. Live three-machine smoke proof passes all Phase 825 §5 criteria (Phase 572
   smoke proof satisfies preconditions; a post-rotation smoke proof is required
   per Phase 826 §5 after key provisioning).
4. Human authorization record completed per Phase 826 §6.

Note: three VPSes are currently available. Machine count and key provisioning
to be determined in the gate-pull planning session.

## 8. Row 5 and SIM-LEAKAGE-03

Row 5 remains `spec_closed_runtime_pending`. The live run is still required
before `runtime_closed` can be recorded.

The live run requires: (1) Rust privacy lane integration gate (human decision,
authorized after first-validator gate pull); (2) live `LeakageMetricsCollector`
run against M-009 testbed; (3) `check_bounds()` returning `{"A": True, "B": True, "C": True}`.

`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

## 9. Human Decision Log (2026-04-26)

The following operator decisions were recorded in the human decision log phase
(post-HIGH-002 closure, 2026-04-26):

| # | Decision | Outcome |
|---|----------|---------|
| D1 | Option B selection (Phase 814 vs. 841 discrepancy) | Phase 814 is operative. Option B selected 2026-04-23. Phase 841 gate re-synthesis confirmed `go`; its `not_selected` token was a scoping error now corrected. |
| D2 | First-validator human gate (Phase 826 §6) | Option A — pull. Requires joint key-provisioning session. Three VPSes available; machine count TBD. |
| D3 | Rust privacy lane / B-Impl / SIM-LEAKAGE-03 | Authorized after first-validator gate is pulled. |
| D4 | CDL-070 (PQ migration ceremony) | Deferred. Revisit at each window closure. |
| D5 | CDL-071 (temporal tier reconciliation) | Deferred. Higher priority than CDL-070 when taken up. Revisit at each window closure. |
| D6 | Capsule v5.19 patch | Done. This document. |

## 10. Immediate Carry-Forward

**Active next session (joint planning required):**
1. First-validator human gate pull — key provisioning session with operator.

**Next implementation window (after gate pull):**
1. Row 5 B-Impl — Rust privacy lane integration (6 obligations, `node.rs` entry point).
2. SIM-LEAKAGE-03 live run on M-009.

**Deferred (revisit each window closure):**
1. CDL-070 — PQ migration ceremony (D1 wire format mismatch path).
2. CDL-071 — temporal tier reconciliation (higher priority than CDL-070 when taken up).

## 11. Preserved Boundaries

- Option B selected (Phase 814, 2026-04-23); `adr_0028_posture=option_b`,
- CDL-017 ratified (Phase 765); first non-Genesis validator deployment human-gated,
- Row 7 `runtime_closed` (Phases 759–760, Mysticeti convergence window),
- Row 5 `spec_closed_runtime_pending`,
- privacy lane not wired into live settlement,
- SIM-LEAKAGE-03 live run not yet executed,
- CDL-070 and CDL-071 not yet opened,
- HIGH-002 CLOSED (Phase A `3abd63e4` + Phase B `53c4000d`),
- first-validator human gate not yet pulled.
