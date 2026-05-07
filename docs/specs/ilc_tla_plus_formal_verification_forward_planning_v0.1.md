# TLA+/TLC Formal Verification — Forward Planning

**Recorded:** Phase 1233-1240 era (2026-05-07)
**Status:** Pre-planning. No phase assigned or authorized yet.
**Earliest implementation:** Window 1241+ for pre-RC item; post-launch for remainder.

```text
tla_formal_verification_forward_planning_recorded_phase_1233_1240
```

---

## 1. Current Verified Baseline (as of Phase 1236)

All three gate specs pass cleanly under `tools/run_tlc_m_series_gate.sh`:

| Spec | File | Properties checked | TLC result | Evidence |
|------|------|--------------------|------------|---------|
| Spec A — DAG Liveness | `ilc_dag_censorship_bounds.tla` | Liveness, TypeOK | PASS (MaxRound=12, N=4, F=1) | `ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md` |
| Spec B — ECU Transfer Safety | `ilc_ecu_fast_path_bcast.tla` | SafetyNoDualCert, TypeOK, AcksSubsetValidators, CertifiedSubsetProposed | PASS (N=4, F=1) | Phase 698 gate run |
| Spec C — Partition/Heal | `ilc_partition_heal.tla` | NoFork, NoNewGlobalCommitDuringPartition, EventualCommit, TypeOK | PASS (N=4, F=1, 2\|2 split) | `ilc_partition_heal_tlc_evidence_818_v0.1.md` |

`SafetyNoDualCert` is formally verified in Spec B — the M-019 deferred TODO
and the Phase 1175 TLA+ gap analysis were both written before Spec B's
`SafetyNoDualCert` invariant was confirmed clean. No open gap on equivocation
safety. The M-019 deferred todo item 1 is **resolved**.

---

## 2. Remaining Pre-RC Item

### TLA-PRE-1 — Refinement Notes: TLA+ Variables → Rust Implementation

**Token:** `tla_refinement_notes_pre_rc`
**Status:** NOT DONE. No artifact exists.
**Effort:** Low (hours — documentation only, no new TLA+ spec)
**Value:** High — external BFT auditors will ask how the abstract model maps to
the Rust implementation. Without this, TLA+ and Rust are independent artifacts
that can drift invisibly between sessions.

**What it produces:**

A short document (`docs/research/ilc_tla_plus_rust_refinement_notes_v0.1.md`)
mapping each TLA+ variable and action to the corresponding Rust type/function
in `ilc_consensus/`:

| TLA+ (Spec A/B/C) | Rust location | Notes |
|--------------------|---------------|-------|
| `dag` (vertex receipt set) | `NodeRunner` gossip message buffer | Spec A |
| `committed` (committed epoch set) | `EpochStore::commit_epoch_record` / LMDB | Specs A, C |
| `HonestBroadcast(v)` | `NodeRunner::dispatch` → `GossipMessage::EpochSettlementTx` | Spec A |
| `acks[t]` (ack accumulation) | `FastPathProtocol` ack state | Spec B |
| `ByzantineAck` (equivocation action) | equivocation detection in `node.rs` | Spec B |
| `quorum` threshold | CDL-051 `required_quorum_fraction`; `EpochStore` threshold check | Specs A, B, C |
| `partitioned` (network split state) | QUIC transport topology; no direct Rust analog — modelled abstractly | Spec C |
| `EpochSettlementTx` submission | `NodeRunner` → `GossipMessage::EpochSettlementTx` | Spec C |

**Suggested phase scope:**

```
Phase NNNNa (NON-SENSITIVE, 1 phase)
Topic: TLA+ refinement notes — formal model to Rust bridge
Owner lane: G8
Deliverables:
  - docs/research/ilc_tla_plus_rust_refinement_notes_v0.1.md
  - Token: tla_refinement_notes_pre_rc
No runtime changes. No CDL mutation. No TLC rerun required.
```

**Suggested window:** Any quiet tail slot in Window 1241+ or the pre-RC
hardening window. Can be Strike Forced (NON-SENSITIVE, doc-only).

---

## 3. Post-Launch Items

These are formally out of scope for the current RC track. Do not schedule
before public RC.

### TLA-POST-1 — Spec D: EpochSettlementTx Shared-Object Path

**Token:** `tla_spec_d_epoch_settlement_post_launch`
**Effort:** Medium (days — new TLA+ spec)

Models the shared-object `EpochSettlementTx` settlement path: multiple
validators submitting for the same epoch; the commit rule must be
idempotent and exactly-once. Byzantine validators submit conflicting
epoch records. This is the path exercised in M-013/M-014.

**Suggested phase scope (post-launch):**

```
Phase NNNNb (SENSITIVE, 2 phases: spec + TLC run)
Topic: Spec D — EpochSettlementTx shared-object formal model
Owner lane: G8 / Rust consensus lane
Deliverables:
  - docs/specs/tla/ilc_epoch_settlement_tx.tla + .cfg
  - TLC evidence artifact
  - Gate script addition
  - Token: tla_spec_d_epoch_settlement_complete
```

### TLA-POST-2 — TLAPS Unbounded Liveness Proof (Spec A)

**Token:** `tla_tlaps_unbounded_liveness_post_launch`
**Effort:** High (weeks — requires TLA+ Proof System expertise)

Ports the Spec A `Liveness` temporal property from bounded TLC
(MaxRound=12, N=4, F=1) to TLAPS — a machine-checked proof valid for
all N, F satisfying N > 3F. This is mathematically rigorous post-launch
audit hardening, not a pre-RC blocker.

### TLA-POST-3 — Economic Protocol Specs

**Token:** `tla_economic_protocol_specs_post_launch`
**Effort:** High (multiple weeks — several new specs)

TLA+ specs for CDL-047 treasury, CDL-050 ECU governor, CDL-054 validator
rewards, and the ADR-0015 node-transfer economics family. Supply-conservation
invariants are well-suited for TLC verification. Deferred because the economic
layer is not fully wired to production yet.

---

## 4. Suggested Phase Sequence (Window 1241+)

| Phase slot | Topic | Sensitivity | Effort | Token produced |
|-----------|-------|-------------|--------|----------------|
| 1241+a | TLA+ refinement notes (TLA+ vars → Rust types/functions) | NON-SENSITIVE | Hours | `tla_refinement_notes_pre_rc` |
| Post-launch | Spec D: EpochSettlementTx shared-object model | SENSITIVE | Days | `tla_spec_d_epoch_settlement_complete` |
| Post-launch | TLAPS unbounded Liveness proof for Spec A | SENSITIVE | Weeks | `tla_tlaps_unbounded_liveness_post_launch` |
| Post-launch | Economic protocol specs (treasury, ECU governor, node-transfer) | SENSITIVE | Weeks | `tla_economic_protocol_specs_post_launch` |

The refinement notes phase is a single NON-SENSITIVE doc-only phase. It can
sit in any window with tail capacity. The post-launch items each require a
dedicated window with proper guidance doc and phase prompts.

---

## 5. What NOT to Do

- Do not re-run TLC for Spec A with MaxRound > 12 before RC — it is already
  MaxRound=12 and the evidence is recorded. Wider model-checking has
  diminishing returns before TLAPS.
- Do not write a new equivocation spec — `SafetyNoDualCert` is already
  formally verified in Spec B (M-019 deferred item 1 is resolved).
- Do not write Spec C — it already exists and has Phase 818 TLC evidence.
- Do not schedule Spec D or TLAPS before public RC — empirical M-series
  workloads are the primary evidence mechanism at this stage.

---

## 6. Relationship to Existing Gate Infrastructure

The canonical gate script `tools/run_tlc_m_series_gate.sh` already runs
Specs A, B, and C. Any new spec (Spec D) should be added to this script
following the same `run_spec "spec_name"` pattern.

TLC output artifacts live in `docs/specs/tla/states/`. Evidence documents
live in `docs/specs/`.

---

`tla_formal_verification_forward_planning_recorded_phase_1233_1240`
