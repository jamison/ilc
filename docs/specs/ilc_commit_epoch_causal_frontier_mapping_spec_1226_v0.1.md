# ILC `commit.epoch` Causal Frontier Mapping Spec 1226 v0.1

**Phase:** 1226
**Window:** 1225-1232
**Date:** 2026-05-06
**Status:** Spec committed — no runtime activation
**Token:** `commit_epoch_causal_frontier_mapping_spec_committed_phase_1226`
**Consumes:** `commit_epoch_causal_frontier_mapping_spec_required`

---

## 1. Purpose

This specification maps the ADR-0004 `commit.epoch` truth primitive to the
current consensus/finality substrate without changing runtime code. It resolves
the Phase 1219 carry-forward obligation by defining how:

- Genesis epoch-zero bootstrap anchors into `commit.epoch`;
- post-Genesis CDL-051 epoch-state/quorum records map to `commit.epoch`;
- the Rust consensus epoch structures expose enough data for a future
  production emission runtime; and
- the non-agent-issuable boundary remains intact.

This phase is spec-only. It does not mutate the CDL register, does not mutate
`ilc_core/`, does not mutate `ilc_consensus/`, does not sign v0.2, and does not
authorize public launch, public repository publication, public release artifact
distribution, external contributor onboarding, release-key generation, or a
production `commit.epoch` emission runtime.

---

## 2. Authority Order

Authoritative sources for this mapping:

| Source | Role |
|--------|------|
| `docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md` | Defines `commit.epoch` as one of the ADR-0004 New Seven and demotes `star.map` |
| `docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md` | Ratifies epoch-state / quorum-record / finality vocabulary and CDL-051 consensus authority |
| `docs/specs/ilc_cdl_074_truth_primitive_runtime_opening_864_v0.1.md` and Phase 863-872 closure artifacts | Preserve `commit_epoch_agent_submission_rejected`; agent submission is permanently excluded |
| `docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md` | Genesis-attests primitive permanence and records this mapping obligation |
| `ilc_consensus/src/types.rs` | Defines `EpochSeq`, `CIDv1Root`, `EpochSettlementRecord`, `EpochCheckpoint`, `AggSig`, `ValidatorID`, and `AgentID` |
| `ilc_consensus/src/epoch_settlement.rs` | Defines `StoredCheckpoint`, `EpochStore`, and `EpochSettlementProtocol::process_epoch_checkpoint` |
| `ilc_consensus/src/app_interface.rs` | Defines the read-only gRPC surface (`GetEpoch`, `GetEpochRecord`, `GetEpochChain`) |
| `AGENTS.md` | Current repo-local coding guardrails: no wall-clock protocol time, no float economics, canonical JSON for machine surfaces |

### Historical Draft Files — Subordinated

The older G4/G5 `commit_epoch_*` draft files are useful historical context only.
They are not governing sources for Phase 1226:

| File | Superseded / prohibited element |
|------|---------------------------------|
| `docs/specs/commit_epoch_event_schema_v0.1.md` | Uses wall-clock `created_at`; permits issuer/namespace assumptions not aligned to the consensus-only boundary |
| `docs/specs/commit_epoch_economics_v0.1.md` | Uses JSON numeric reward/stake examples and pre-CDL-051 economics framing |
| `docs/specs/commit_epoch_event_schema_v0.1.json` | Encodes the same stale wall-clock event shape |

Historical concepts that remain usable only after remapping: epoch sequence,
state-root/checksum anchoring, and the general idea that `commit.epoch` marks
finalization. Historical wall-clock timestamps, float/JSON-number economics,
timestamp-based conflict resolution, agent/namespace issuer fields, and direct
event-log emission assumptions are superseded.

---

## 3. Canonical `commit.epoch` Envelope

The first canonical wire object is a deterministic JSON object. It is a
consensus-layer projection of finalized epoch state, not an agent submission.

Required serialization policy:

- JSON object only;
- `json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))`
  for any Python-side canonical export;
- deterministic key ordering;
- no floats or JSON non-finite values;
- no wall-clock timestamps;
- no local machine paths;
- no random identifiers;
- no `AgentID` in the issuer field.

### 3.1 Fields

| Field | Type | Genesis epoch-zero value | Post-Genesis value |
|-------|------|--------------------------|--------------------|
| `event_kind` | literal string | `"commit.epoch"` | `"commit.epoch"` |
| `schema_version` | literal string | `"commit_epoch_causal_frontier_mapping_1226.v0.1"` | same |
| `epoch_sequence` | unsigned integer | `0` | `EpochSettlementRecord.epoch.0` |
| `state_root_cidv1_hex` | 72 lowercase hex chars or `null` | Genesis v0.1 root envelope hash domain anchor; no Rust `CIDv1Root` exists before first consensus checkpoint | concatenation of `CIDv1Root.p1 || CIDv1Root.p2` from `EpochSettlementRecord.state_root` |
| `causal_predecessor_ref` | `sha256:<64 lowercase hex>` or `null` | `null` | SHA-256 reference of immediately preceding canonical `commit.epoch` envelope |
| `quorum_proof_ref` | `sha256:<64 lowercase hex>` or `null` | `null` | SHA-256 reference of the canonical quorum-proof projection defined in §5.2 |
| `genesis_domain_hash` | 64 lowercase hex chars | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` | same immutable Genesis domain hash |
| `issuer` | literal string | `"consensus_layer"` | `"consensus_layer"` |
| `timestamp_policy` | literal string | `"epoch_sequence_only_no_wall_clock"` | `"epoch_sequence_only_no_wall_clock"` |
| `causal_frontier_refs` | array of hash refs | `["genesis_root:ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"]` | array containing `quorum_proof_ref` for the finalized epoch and any explicitly modeled predecessor frontier references required by future CDL-051 extensions |

`causal_predecessor_ref`, `quorum_proof_ref`, and `state_root_cidv1_hex` are
required-present fields. They are nullable only for the Genesis epoch-zero case
where the corresponding consensus object does not yet exist.

---

## 4. Genesis Epoch-Zero Mapping

Genesis epoch-zero is a singleton causal frontier:

| Mapping item | Value |
|--------------|-------|
| `epoch_sequence` | `0` |
| `causal_predecessor_ref` | `null` |
| `quorum_proof_ref` | `null` |
| `issuer` | `"consensus_layer"` |
| `timestamp_policy` | `"epoch_sequence_only_no_wall_clock"` |
| Causal frontier | Genesis v0.1 root envelope hash |

The Genesis bootstrap case does not create an agent-issued exception. Genesis
authority is represented here as the singleton consensus frontier. The
`commit.epoch` issuer field remains `"consensus_layer"` and must not contain an
agent identifier, validator identifier, signer roster, model name, or human
name.

The runtime truth primitive submission boundary remains:

```text
commit_epoch_agent_submission_rejected
```

This token applies unconditionally. Agents may not submit, modify, or supersede
`commit.epoch` envelopes.

---

## 5. Post-Genesis Mapping

### 5.1 Rust Consensus Structures

Post-Genesis `commit.epoch` is a projection of finalized Rust consensus state:

| Rust source | File | Mapping |
|-------------|------|---------|
| `EpochSettlementRecord` | `ilc_consensus/src/types.rs` | `epoch.0` → `epoch_sequence`; `state_root` → `state_root_cidv1_hex` |
| `EpochCheckpoint` | `ilc_consensus/src/types.rs` | `record` + `sigs` + `signers` provide quorum certificate material |
| `StoredCheckpoint` | `ilc_consensus/src/epoch_settlement.rs` | Serialized LMDB recovery form: `record`, `agg_sig_bytes`, `signers` |
| `EpochStore` | `ilc_consensus/src/epoch_settlement.rs` | Definitive epoch boundary store; `get_current_epoch`, `get_checkpoint`, `get_epochs_after` |
| `EpochSettlementProtocol::process_epoch_checkpoint` | `ilc_consensus/src/epoch_settlement.rs` | Production path that verifies aggregate signatures before writing to `EpochStore` |
| `ApplicationInterface` / `ILCAppReadService` | `ilc_consensus/src/app_interface.rs` | Read-only bridge to Python: `GetEpoch`, `GetEpochRecord`, `GetEpochChain` |

### 5.2 Quorum Proof Reference

For a post-Genesis epoch, `quorum_proof_ref` is the SHA-256 reference of the
canonical quorum-proof projection:

```json
{
  "agg_sig_bytes_hex": "<lowercase hex of StoredCheckpoint.agg_sig_bytes>",
  "epoch_sequence": <StoredCheckpoint.record.epoch.0>,
  "signers": [<ValidatorID.0 sorted ascending>],
  "state_root_cidv1_hex": "<lowercase hex of StoredCheckpoint.record.state_root.p1 || p2>"
}
```

Serialization policy for this quorum-proof projection is the same canonical JSON
policy as §3. The hash is expressed as:

```text
sha256:<64 lowercase hex>
```

This projection is a wire/spec layer above Rust. It does not require changing
the Rust LMDB serialization in Phase 1226.

### 5.3 Epoch Chain Reference

For epoch `N > 0`, `causal_predecessor_ref` is the SHA-256 reference of the
canonical `commit.epoch` envelope for epoch `N - 1`. `EpochStore` already
provides the monotonic epoch sequence and `GetEpochChain` already exposes a
read-only epoch-chain surface to Python. A future runtime may materialize the
hash chain without adding a write path from Python to Rust.

### 5.4 No Python Write Path

Python reads consensus state via the gRPC read API. It does not submit
`commit.epoch` records to Rust consensus. Existing testnet-only or
fault-simulation paths that call `commit_epoch_record` without BLS material are
not production emission authority.

---

## 6. Causal Frontier Definition

The causal frontier of epoch `N` is the **canonical minimal cut of the finalized
epoch-N consensus DAG/hypergraph**: the smallest set of quorum-proof references
`Q` such that every protocol state element accepted into epoch `N` is causally
covered by at least one `q ∈ Q` through validator block edges and
quorum-certificate hyperedges.

> **Fix1 note:** Earlier draft language said "transitively reachable through the
> committed epoch chain." That phrasing underclaims the substrate: ILC consensus
> is DAG/BFT-oriented (Mysticeti-inspired), not a simple linear chain.
> "Causally covered by `q`" is the correct formulation under the finalized DAG
> orientation; "transitively reachable from `q`" is avoided because it implies a
> specific edge direction that is not universally defined at this layer.

**Required properties of `Q`:**

- **Minimality**: no proper subset of `Q` causally covers all protocol state elements
  accepted into epoch `N`
- **Completeness**: every accepted state element has a causal path to some `q ∈ Q`
  under the finalized DAG orientation
- **No wall-clock**: frontier membership is determined by the protocol DAG structure
  and validator quorum certificates, not by any timestamp or wall-clock interval
- **Hyperedge coverage**: each `q ∈ Q` is a `StoredCheckpoint` containing an
  aggregate BLS signature (`agg_sig_bytes`) and signer bitset (`signers`) spanning a
  Byzantine-threshold subset of the validator set — a hyperedge in the consensus DAG

**Causal ordering preservation** (structure-preserving projection property):

The `commit.epoch` projection must preserve causal order: if state element `A`
causally precedes state element `B` in the finalized consensus DAG/hypergraph,
then the canonical `commit.epoch` references for `A` and `B` must preserve that
ordering through `causal_predecessor_ref` and the committed epoch sequence.

**Genesis epoch-zero special case:**

`Q` is a singleton containing only the Genesis root envelope domain anchor. No
validator quorum certificate exists. No DAG edges exist prior to it. The causal
frontier is the domain anchor alone; causal coverage is trivially satisfied.

**Hard prohibition:**

```text
No wall-clock time: no datetime.now(), no time.time(), no ISO-8601 created_at
as protocol truth, no local clock ordering in commit.epoch.
```

Protocol order is derived from epoch sequence numbers and quorum/finality
records only.

---

## 7. Non-Agent-Issuable Boundary

`commit.epoch` is permanently non-agent-issuable:

```text
commit_epoch_agent_submission_rejected
```

Consequences:

- No agent may submit a `commit.epoch` envelope.
- No agent may modify or supersede a `commit.epoch` envelope.
- `AgentID` must not appear in the canonical `issuer` field.
- Validator identities may appear only inside the quorum-proof projection
  (`signers`), not as the issuer.
- Genesis epoch-zero does not create an agent-issuer exception.
- Python-side tools may render or verify the projection but must not be treated
  as consensus emission authority.

---

## 8. Numeric and Economic Boundary

This mapping does not define reward distribution, decay, consolidation, or
stake economics. It only defines the finality/time primitive projection.

Hard prohibition:

```text
No float economics: no Python float, no IEEE-754 field, no JSON Number for ECU
or stake accounting in any commit.epoch economic field.
```

If a future `commit.epoch` economics envelope is added, it must use
`Decimal`-string or ratified fixed-point integer encoding, consistent with
`ECUBalance.amount_micro_ecu: u64` in the Rust consensus layer and current
Python economic-runtime rules.

---

## 9. Constitutional Routing

CDL-051 is sufficient to govern the consensus/finality interpretation of
`commit.epoch` as a projection over already-finalized epoch records. This Phase
1226 spec therefore records:

```text
commit_epoch_mapping_governed_by_cdl_051_no_new_cdl_required
```

However, production emission tooling is still not implemented. A later runtime
phase is required before public or production `commit.epoch` emission is claimed:

```text
commit_epoch_projection_runtime_required_before_production_emission
```

This is not a request for a new constitutional act by default. It is a runtime
implementation carry-forward. If a later implementation discovers that CDL-051
does not cover a required production behavior, that later phase must open a
fresh CDL or ADR rather than expanding this spec by implication.

---

## 10. Required Invariants

1. **No wall-clock time** — no `datetime.now()`, no `time.time()`, no wall-clock
   seconds anywhere in the `commit.epoch` wire format or causal frontier
   definition.
2. **No float economics** — no Python `float`, no IEEE-754 arithmetic, and no
   JSON Number for ECU/stake economic state in any future `commit.epoch`
   economic extension.
3. **`commit_epoch_agent_submission_rejected`** — preserved; no softening;
   agents may not submit or modify `commit.epoch` envelopes.
4. **Genesis epoch-zero is a singleton frontier** — causal predecessor is
   `null`; quorum proof reference is `null`; Genesis authority is represented
   as the singleton consensus frontier.

---

## 11. Non-Claims

This spec does not:

- implement runtime emission;
- mutate Rust consensus code;
- mutate Python runtime code;
- amend CDL-051 or CDL-074;
- create an agent submission path;
- authorize public launch or public repository publication;
- authorize v0.2 signing;
- authorize a release envelope;
- define or ratify new economic formulas.
