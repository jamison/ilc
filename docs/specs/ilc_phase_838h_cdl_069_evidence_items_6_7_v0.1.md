# Phase 838h — CDL-069 Evidence Items 6 and 7

**Phase:** 838h  
**Date:** 2026-04-26  
**Evidence items satisfied:** 6 (minting proof chain audit), 7 (privacy lane compatibility assertion)  
**Governing spec:** CDL-069 §4 evidence checklist

---

## Item 6 — Minting Proof Chain Compatibility Audit

**Required token:** `minting_proof_chain_compatibility_audit_complete`

### 6.1 Scope

This audit verifies that:

1. The Phase 550 passive ECU attribution runtime
   (`ilc_core/economics/passive_ecu_attribution_runtime.py`) is compatible with
   the CDL-069 epoch-close attestation protocol.
2. The `epoch_nonce` construction (`sha256(domain || identity_seed_commitment || epoch_id)`)
   is compatible with ECU total aggregation in the minting circuit.
3. The deferred-reveal window for `ecu_sent_commitment` / `ecu_received_commitment`
   does not break any CDL-054 timing guarantee.

### 6.2 Passive ECU Attribution Runtime (Phase 550)

The Phase 550 runtime (`PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION =
"passive_ecu_attribution_runtime_550.v0.1"`) computes passive ECU attribution
for one reuse path:

```
passive_ecu = min(
    base_reward × PASSIVE_ATTRIBUTION_RATE × centrality_score × quality_factor(q_i),
    base_reward × ATTRIBUTION_CAP
)
```

Constants: `PASSIVE_ATTRIBUTION_RATE = 0.20`, `DECAY_FLOOR = 0.05`,
`ATTRIBUTION_CAP = 0.15`, `GAMMA = 0.15`.

**Compatibility analysis:**

The passive ECU attribution runtime operates on `base_reward` (a float), which
is the resolved ECU value of a reuse event. This is a *per-event, per-path*
computation — it is independent of any epoch-boundary protocol. It does not
read or write `ecu_sent_commitment`, `ecu_received_commitment`, or any
epoch-close attestation field.

The passive attribution runtime produces an ECU delta per reuse event. These
deltas accumulate within an issuance epoch and are summed at epoch close into
`ecu_received_total` (for the attributed agent). The epoch-close attestation
commits `sha256(ecu_received_total || epoch_nonce)`. This is a two-phase
design: accumulation happens continuously (Phase 550 runtime), commitment
happens once at epoch close (CDL-069 §2b).

**No field conflict found.** The Phase 550 runtime produces floating-point
ECU values; the epoch-close attestation commitment operates on a canonical
string representation of the accumulated total. These operate at different
layers with no shared mutable state.

**Authorship primacy invariant:** The Phase 550 runtime enforces
`PASSIVE_ATTRIBUTION_RATE × (1 + GAMMA) < 1.0` (checked at module load via
`_validate_runtime_contract()`). This invariant is unaffected by the CDL-069
epoch-close commitment construction.

### 6.3 Epoch Nonce Construction Compatibility

CDL-069 §2b specifies:

```
epoch_nonce = sha256("ilc-epoch-nonce-v1:" || identity_seed_commitment || epoch_id.to_bytes(8, 'big'))
ecu_sent_commitment = sha256("ilc-ecu-commit-v1:" || ecu_sent_total || epoch_nonce)
```

The `epoch_nonce` is derived from `identity_seed_commitment` (public, 96-char
SHA-384 hex) and `epoch_id` (u64). Both are available to the agent at epoch
close without additional storage.

**Aggregation compatibility:** ECU totals (`ecu_sent_total`, `ecu_received_total`)
are accumulated across the epoch as floating-point values in the agent runtime,
then canonicalized to string at commitment time. The commitment and aggregation
are strictly sequential: accumulate → canonicalize → commit. No conflict exists.

**Reveal protocol:** At the start of the next epoch, the agent publishes
`ecu_sent_total` (canonical string) and `epoch_nonce` (64-char hex). Validators
verify: `sha256(domain || total || nonce) == ecu_sent_commitment`. This is a
standard hash commitment; verification does not depend on any CDL-054 timing
structure.

**CDL-054 timing:** CDL-054 governs validator reward pool routing. It specifies
that validator rewards are computed from the issuance-epoch minting batch. The
deferred ECU reveal window is sub-epoch (reveal at next validation epoch start,
not next issuance epoch). The CDL-054 minting batch reads aggregated ECU totals
after all reveals are confirmed, which occurs within the same issuance epoch.
No CDL-054 timing guarantee is broken: the reveal window is bounded to one
validation epoch (~1 minute), far shorter than the issuance epoch (~1 month)
over which minting is computed.

### 6.4 Floating-Point Note

The Phase 550 passive attribution runtime uses Python `float` for ECU values.
This is consistent with the design constraint that ECU values are advisory
(not monetary precision) until they reach the minting layer. The CDL-069
commitment operates on the canonical string representation of the accumulated
total (e.g. a decimal string or fixed-point encoding — encoding is a
ratification decision). The commitment layer is hash-based and representation-
agnostic; no floating-point arithmetic occurs in the commitment computation.

### 6.5 Audit Verdict

No conflicts found between the Phase 550 passive ECU attribution runtime and
the CDL-069 epoch-close attestation protocol. All three compatibility
requirements are satisfied:

- (a) No field conflicts between epoch-close attestation and Phase 550 runtime.
- (b) `epoch_nonce = sha256(domain || identity_seed_commitment || epoch_id)` is
  compatible with ECU total aggregation: accumulation and commitment are
  strictly sequential layers.
- (c) The deferred-reveal window (one validation epoch) does not break any
  CDL-054 timing guarantee. The issuance-epoch minting batch reads post-reveal
  totals, which are confirmed within the same issuance epoch.

**Token satisfied:** `minting_proof_chain_compatibility_audit_complete`

---

## Item 7 — Privacy Lane Compatibility Assertion

**Required token:** `row5_epoch_endorsement_compatibility_asserted`

### 7.1 Scope

This section verifies that the CDL-069 epoch endorsement protocol does not
violate SIM-LEAKAGE-03 bounds or Row 5 anonymity constraints, per CDL-069
§2f and prelock criterion 10.

**SIM-LEAKAGE-03 bounds (from CDL-069 §2f, coherence report 834):**
- A ≤ 0.15 — direct identity correlation bound
- B ≤ 0.15 — flow correlation bound  
- C ≤ 0.05 — membership inference bound

**Hard constraint (CDL-069 §2f, prelock criterion 10):** The ML-DSA
endorsement packet must not reveal Row 5 group membership, routing assignment,
or privacy lane participation.

### 7.2 Endorsement Packet Field Analysis

The 8 required fields of the endorsement packet are analyzed against each
SIM-LEAKAGE bound:

| Field | Content | Leaks group membership? | Leaks routing? | Leaks privacy lane? |
|-------|---------|------------------------|----------------|---------------------|
| `protocol_version` | u32 = 1 | No | No | No |
| `agent_id` | 96-char SHA-384 of identity_seed | No — stable identifier, no group info | No | No |
| `epoch_id` | u64 | No | No | No |
| `sequence_number` | u64 monotonic | No | No | No |
| `ephemeral_signing_pk` | BLS G1 pk hex | No | No | No |
| `valid_epochs` | u32 ∈ [1, 1440] | No — reveals signing frequency preference only | No | No |
| `liveness_assertion` | sha256(domain \|\| agent_id \|\| epoch_id) | No — deterministic from public fields | No | No |
| `agent_state_root` | CID of prior epoch-close attestation | No — opaque CID, no content | No | No |

**Analysis:** None of the 8 required fields carries group membership,
routing assignment, or privacy lane participation. The fields are either
cryptographic identifiers derived from the agent's permanent seed (agent_id),
or protocol-level metadata with no Row 5 structural information embedded.

**Optional fields** (`capability_declaration`, `stake_position`,
`next_epoch_intent`, `canonical_root_pk`, `supersedes_epoch_id`) are by
definition optional. If an agent includes `capability_declaration`, it is
self-disclosed and does not reveal Row 5 assignment. Row 5 routing assignment
is not a field that can be included — it is not defined in the packet schema.

### 7.3 ECU Commitment Construction and Bound A

SIM-LEAKAGE-03 bound A bounds direct identity correlation. The epoch-close
attestation uses:

```
ecu_sent_commitment   = sha256(domain || ecu_sent_total || epoch_nonce)
ecu_received_commitment = sha256(domain || ecu_received_total || epoch_nonce)
```

where `epoch_nonce = sha256(domain || identity_seed_commitment || epoch_id)`.

The nonce is derived from `identity_seed_commitment` (public, known to all
validators) and `epoch_id` (public). The nonce does not introduce new identity
correlation because `identity_seed_commitment` is already the agent's permanent
public identifier. The SHA-256 preimage resistance of the commitment ensures
that the ECU total cannot be recovered by enumeration during the deferred-reveal
window. This directly addresses bound A: an adversary cannot correlate ECU
flows to specific agents within the epoch without knowing the committed total
in advance.

**Bound A assessment:** The epoch_nonce adds full SHA-256 preimage resistance
(2^128 quantum preimage) to any ECU amount regardless of magnitude. Low-entropy
amounts (e.g. 50 ECU) that would be trivially brute-forced without the nonce
are protected for the duration of the reveal window (one validation epoch).
Bound A ≤ 0.15 remains satisfiable.

### 7.4 Participation Threshold and Bound C

SIM-LEAKAGE-03 bound C bounds membership inference. CDL-069 §2f notes:

> The participation threshold (§2c) interacts with Row 5 group construction:
> below-threshold agents may not appear in rolling groups at all, which affects
> anonymity set sizing.

**Analysis of the interaction:**

The participation threshold creates a binary observable: agents above it
publish mandatory epoch-close attestations; agents below it do not. This is
an existing observable — it is not introduced by CDL-069. The endorsement
packet publication pattern (mandatory above threshold, absent below) mirrors
the existing participation-threshold structure.

The critical question for bound C is whether the endorsement packet publication
pattern narrows the anonymity set more than the pre-existing participation
threshold already does. It does not: the set of agents publishing endorsement
packets is exactly the set of agents above the participation threshold — no new
information is disclosed beyond what was already observable from participation
threshold crossing.

Row 5 group assignment operates on the set of above-threshold agents. Since
the endorsement packet does not reveal which rolling group an agent belongs to,
the group assignment privacy property is preserved. Bound C ≤ 0.05 remains
satisfiable given the existing anonymity set construction — the endorsement
protocol does not worsen it.

### 7.5 Bound B — Flow Correlation

SIM-LEAKAGE-03 bound B bounds flow correlation. The endorsement packet contains
no ECU flow information (that is deferred to the epoch-close attestation, which
uses hash commitments). The `valid_epochs` field reveals how often the agent
re-signs (every N epochs), but does not reveal the direction or magnitude of
any ECU flow. Bound B ≤ 0.15 remains satisfiable.

### 7.6 SIM-LEAKAGE-03 Status Note

As of Phase 837, `SIM-LEAKAGE-03` has not yet been executed live against the
M-009 testbed (deferred pending Rust privacy lane integration gate,
`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`). This
assertion is therefore a structural analysis, not an empirical measurement.
It establishes that the CDL-069 endorsement protocol does not introduce any
new mechanism that would prevent SIM-LEAKAGE-03 bounds from being satisfied
when the live run does occur. The live run is not required for CDL-069
ratification; it is a Row 5 runtime closure gate (separate track).

### 7.7 Compatibility Verdict

All three SIM-LEAKAGE-03 bounds remain satisfiable under the CDL-069 epoch
endorsement protocol. The hard constraint (no Row 5 group/routing/privacy lane
information in endorsement packets) is satisfied by design: no such field is
defined or permitted in the packet schema.

Specific findings:
- Bound A: epoch_nonce provides full SHA-256 preimage resistance during reveal window.
- Bound B: no ECU flow information in endorsement packets.
- Bound C: participation threshold interaction does not widen membership inference
  beyond the pre-existing threshold observable.
- Hard constraint: 8 required fields contain no Row 5 structural information.
  Optional fields are self-disclosed and contain no group assignment.

**Token satisfied:** `row5_epoch_endorsement_compatibility_asserted`

---

## Summary

Both evidence items are satisfied by this document:

| Token | Status |
|-------|--------|
| `minting_proof_chain_compatibility_audit_complete` | **SATISFIED** — Phase 838h |
| `row5_epoch_endorsement_compatibility_asserted` | **SATISFIED** — Phase 838h |

Updated checklist: **11 of 14 tokens satisfied**. Remaining open: items 8, 12, 14 (Phase 838i).
