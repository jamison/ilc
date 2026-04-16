# ILC Settlement-State Enumeration and Submission Model 687 v0.1

Status: prerequisite spec — required before Phase 690 benchmarks are authoritative
Date: 2026-04-16
Phase: 687
Owner lane: G8 sovereign-substrate research

`settlement_state_enumeration_published_phase_687`
`phase_690_691_benchmark_target_is_defined`

---

## 1. Purpose

This artifact answers: what exactly does ILC need a settlement substrate to
record, order, anchor, and make replayable?

Without this, benchmark harnesses (Phase 690) and comparison analysis (Phase
691) are testing substrate candidates against an undefined target.

This enumeration is grounded in:
- CDL-065 coupling invariants (backend carries already-legitimate state, does
  not author it)
- Phase 609 ECU/ILC/runtime separation
- October 2025 on-chain/off-chain architectural split
- Whitepaper §2 epistemic graph structure

---

## 2. What ILC settlement state is

Settlement state is the set of already-legitimate protocol outputs that require
durable, replayable, publicly auditable anchoring outside the runtime node.

ILC settlement is not:
- gas-paid transaction ordering
- rollup batching
- clearing-house fee collection
- user-facing transaction records

ILC settlement is:
- deterministic finalization of epoch-boundary protocol state
- durable public anchoring of that state
- replayability without privileged operator consent
- exitability — any participant can reconstruct canonical state from the
  anchored record without relying on the original operators

---

## 3. On-chain state: what goes to the settlement substrate

The following categories of state are designated for settlement-substrate
anchoring. Each entry states what is anchored, what is NOT anchored, and why.

### 3.1 Epoch-boundary commit records

**What is anchored:**
- epoch sequence number
- epoch start and close timestamps (validation-epoch granularity, ~1 minute)
- epoch state root — a single content-addressed hash (CIDv1, dag-cbor) that
  commits to the full canonical epoch graph snapshot
- total ECU issued in the epoch
- total ILC converted in the epoch (B_e, I_e, F_e, X_e summary)
- P_e conversion price for the epoch

**What is NOT anchored:**
- raw node payloads
- individual claim texts or evidence
- per-agent ECU balances (these are derivable from the epoch state root)

**Why:** The epoch state root is the single commitment that allows full
replayability. Everything downstream is derivable from it and the genesis
lineage. Anchoring per-agent balances would both bloat the settlement record
and expose linkage information incompatible with the row-5 partial packet.

### 3.2 Node linkage graph anchors

**What is anchored:**
- CIDv1 identifiers of new public nodes submitted in the epoch
- edge-type records: supports, refutes, revises, links — expressed as
  (source CID, target CID, edge-type, epoch) tuples
- authorship attribution is via the authored-payload envelope (CDL-034) —
  the CID commits to it, the settlement layer does not store it separately

**What is NOT anchored:**
- raw authored payloads
- COSE Sign1 signature bytes (verifiable from the CID off-chain)
- private or gated shard content

**Why:** The linkage graph structure is the epistemic graph the settlement
layer is making durable. Raw payloads are off-chain by the October 2025
decision. CIDv1 anchoring is sufficient for replayability.

### 3.3 Namespace and schema registry events

**What is anchored:**
- new namespace registrations: namespace handle, owner CID, epoch of
  registration
- schema updates: schema CIDv1, namespace, epoch

**What is NOT anchored:**
- namespace content or description text (derivable from the CID)

**Why:** Namespace authority is a public legitimacy surface (CDL-065 §2).
Its registration record must be durable and replayable.

### 3.4 Economic events

**What is anchored:**
- validator stake locks: validator agent CID, staked ILC amount, epoch
- validator slash events: validator agent CID, slash reason token, amount,
  epoch
- bounty postings: bounty CID, posted ILC escrow amount, epoch
- bounty fulfillments: bounty CID, fulfilling node CID, epoch, outcome
- protocol-level CDL governance decisions: CDL identifier, decision token,
  epoch, ratified option

**What is NOT anchored:**
- agent internal balance ledger (derivable from epoch state root)
- off-chain escrow custody details

**Why:** Economic events are the on-chain record that makes the ILC economy
auditable. They are sparse relative to raw knowledge work volume. CDL
governance decisions on-chain is the practical enforcement surface for the
governance-as-protocol-law principle.

### 3.5 Genesis lineage anchor

**What is anchored:**
- genesis epoch state root CIDv1
- genesis validator set CIDv1 (the canonical bootstrap roster)
- genesis timestamp

**What is NOT anchored:**
- genesis raw content (off-chain, anchored by the CIDv1)

**Why:** The genesis anchor is the root of replayability. Without it, no
downstream state is verifiable.

---

## 4. Off-chain state: what does NOT go to the settlement substrate

The following categories remain off-chain, anchored by hash/CIDv1 only:

| Category | Why off-chain |
|---|---|
| Raw claim and evidence payloads | Too large; privacy-sensitive; CIDv1 anchor is sufficient for replayability |
| COSE Sign1 signature bytes for individual nodes | Verifiable from the CID and the authored payload off-chain |
| Private or gated shard content | Privacy requirement; capability tokens govern access |
| Per-agent ECU balance details | Derivable from epoch state root; direct exposure creates linkage surface |
| Agent identity and profile data | Wallet-agnostic by design; no mandatory on-chain identity |
| Raw panel deliberation records | Deliberation is off-chain; outcomes are anchored via epoch state root |

---

## 5. Submission model

### 5.1 Submission unit

The canonical settlement-state submission unit per epoch is:

```
ILC Epoch Settlement Record:
  epoch_seq:         uint64
  epoch_close_time:  unix timestamp (seconds)
  state_root:        CIDv1 (dag-cbor, sha2-256)
  ecu_issued:        decimal (unratified planning: ECU quantity, not gas)
  ilc_converted:     decimal (ILC quantity)
  p_e:               decimal (conversion price, clamped 0.75-1.30 per CDL-030)
  new_node_cids:     list[CIDv1]
  new_edges:         list[(source CIDv1, target CIDv1, edge_type, epoch_seq)]
  namespace_events:  list[namespace_event]
  economic_events:   list[economic_event]
  governance_events: list[governance_event]
  prior_epoch_root:  CIDv1 (links to previous epoch — creates chain)
```

### 5.2 Submission frequency

One settlement record per validation epoch (~1 minute per
`ilc_epoch_boundary_commit_semantics_decision_546_v0.1.md`).

Substrates that cannot finalize at 1-minute cadence must state their actual
finality latency explicitly in the Phase 691 comparison analysis. A substrate
that requires 10-minute finality windows operates at a different cadence and
must declare the protocol-level implications.

### 5.3 Size estimate (planning input — unvalidated)

At 10,000 active agents, 1-minute epochs, with moderate claim submission rate:
- new node CIDs: ~100-500 per epoch
- new edges: ~200-1000 per epoch
- namespace events: ~0-5 per epoch
- economic events: ~10-50 per epoch
- governance events: ~0-2 per epoch

Estimated per-epoch settlement record size: ~10-50 KB uncompressed.

This is a planning estimate only. Real calibration requires live RC data and
belongs in the Phase 690 benchmark harness definitions.

---

## 6. What this enumeration gates

`phase_690_harnesses_must_be_anchored_to_this_model`
`phase_691_comparison_must_reference_this_model`

Phase 690 benchmark harnesses must define workloads in terms of the submission
model above — specifically epoch-record finalization latency, state-root
anchoring reliability, and economic-event throughput.

Phase 691 comparison analysis must evaluate each surviving candidate family
against this submission model's requirements, not against generic blockchain
throughput metrics.

Any benchmark or comparison artifact that does not anchor to this enumeration
is testing an undefined target.

---

## 7. Relationship to row-5 partial packet

The submission model deliberately excludes per-agent ECU detail and raw
node payloads from the settlement record. This is compatible with all three
near-term tractable mechanism families from Phase 680:

- timing smoothing / batching: the epoch record batches state naturally
- relay / submission indirection: the settlement layer records epoch state
  roots, not individual submission paths
- commitment / selective-disclosure envelope: the CIDv1 state root commits
  to the full state without exposing per-contributor linkage on-chain

Substrate families that would require per-agent identity disclosure on-chain
as a structural necessity fail the row-5 compatibility filter regardless of
other properties.

---

## 8. What this model does not decide

This enumeration does not decide:
- which BFT protocol family finalizes the submission records
- what the validator set composition is
- how the economic events are ordered if two nodes submit conflicting records
- the final cryptographic format for economic or governance events (planning
  level only)
- whether additional shard-specific state categories are needed (deferred to
  KU-2 / shard lifecycle lane)
