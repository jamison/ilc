# Phase 1236 Fix1 — Full `commit.epoch` Emission Connector Specification

**Phase:** 1236 Fix1
**Window:** 1233-1240
**Date:** 2026-05-07
**Status:** Spec committed — no runtime expansion
**Token:** `phase_1236_fix1_commit_epoch_full_connector_spec_committed`

---

## 1. Purpose

Phase 1236 added the conservative pure connector:

```text
commit_epoch_emission_runtime_1236.v0.1
```

That connector is intentionally narrow. It builds a Phase 1235 canonical
`commit.epoch` `ProtocolEvent` from caller-supplied epoch/finality inputs, but
it does not compute the causal frontier, project quorum proofs from finalized
consensus records, or write to any production consensus surface.

This Fix1 document specifies the complete expansion path so subsequent Fix2+
work can add richer functionality without scope drift. It is specification only:
no runtime code, CDL row, signing artifact, release artifact, Rust consensus
surface, or production emission authorization changes in Fix1.

The carry-forward remains open:

```text
commit_epoch_projection_runtime_required_before_production_emission
```

---

## 2. Governing Sources

| Source | Governing role |
|--------|----------------|
| `docs/specs/ilc_commit_epoch_causal_frontier_mapping_spec_1226_v0.1.md` | Defines the canonical causal-frontier envelope, no-wall-clock policy, Genesis epoch-zero mapping, and Rust consensus mapping |
| `ilc_core/protocol/event_log.py` | Owns Phase 1235 canonical `commit.epoch` constructor and validator |
| `ilc_core/protocol/commit_epoch_emission_runtime.py` | Owns Phase 1236 pure connector stub |
| `ilc_core/consensus/epoch_state_runtime.py` | Python quorum-record normalization surface |
| `ilc_core/consensus/finality_evaluator.py` | Python exact-weight finality evaluation surface |
| `ilc_consensus/src/types.rs` | Rust `EpochSettlementRecord`, `EpochCheckpoint`, `CIDv1Root`, and validator identity types |
| `ilc_consensus/src/epoch_settlement.rs` | Rust `StoredCheckpoint`, `EpochStore`, and aggregate-signature verification/write path |
| `ilc_consensus/src/app_interface.rs` | Read-only gRPC bridge for epoch-state reads; not a Python write authority |
| `AGENTS.md` | Local implementation guardrails: no protocol wall-clock, no float economics, canonical JSON, no unbounded input |

Historical `commit_epoch_*` drafts remain subordinated where they contain
wall-clock `created_at`, float/JSON-number economics, or direct agent emission
assumptions.

---

## 3. Architectural Boundary

`commit.epoch` has three distinct layers that must not be conflated:

| Layer | Purpose | Current status |
|-------|---------|----------------|
| Canonical event constructor | Builds the canonical Python `ProtocolEvent` shape with no `created_at` | Implemented in Phase 1235 |
| Pure emission connector | Builds a canonical event from caller-supplied epoch/finality inputs | Implemented in Phase 1236 |
| Production projection/emission runtime | Projects finalized consensus state into causal-frontier refs and emits only after consensus authorization | Not implemented; explicitly gated |

The Phase 1236 connector is useful for tests and integration shape, but it is
not proof that production emission exists. Production emission requires the
projection runtime defined below and an explicit later authorization phase.

---

## 4. Complete Connector Stack

### Layer A — Canonical Event Builder

**Status:** implemented.

Consumes explicit caller inputs and returns a canonical `ProtocolEvent`.

Primary function:

```python
build_commit_epoch_event(...)
```

Layer A must remain pure: no filesystem I/O, no network I/O, no wall-clock, no
random, no live consensus write.

### Layer B — Quorum-Proof Projection Builder

**Status:** required next implementation candidate.

Builds the canonical quorum-proof projection from finalized consensus evidence.
The initial Python shape should be:

```python
build_quorum_proof_projection(
    *,
    epoch_sequence: int,
    state_root_cidv1_hex: str,
    signers: Sequence[int],
    agg_sig_bytes_hex: str,
    source_record_digest: str | None = None,
) -> dict[str, object]
```

Required output fields:

```json
{
  "agg_sig_bytes_hex": "<lowercase hex>",
  "epoch_sequence": 12,
  "signers": [0, 1, 2],
  "state_root_cidv1_hex": "<lowercase hex>",
  "source_record_digest": "sha256:<optional canonical source digest>"
}
```

`source_record_digest` may be omitted or `null` in the first implementation if
there is no canonical Rust serialization exposed to Python. It must not be
invented from wall-clock, local paths, or non-canonical object representations.

Hashing rule:

```text
quorum_proof_ref = sha256(canonical_json(quorum_proof_projection))
```

Canonical JSON means:

```python
json.dumps(payload, sort_keys=True, allow_nan=False, separators=(",", ":"))
```

### Layer C — Causal-Frontier Projection Builder

**Status:** required after Layer B.

Builds the Phase 1226 causal-frontier projection object. The initial shape
should be:

```python
build_commit_epoch_causal_frontier_projection(
    *,
    epoch_sequence: int,
    state_root_cidv1_hex: str | None,
    causal_predecessor_ref: str | None,
    quorum_proof_ref: str | None,
    causal_frontier_refs: Sequence[str],
    genesis_domain_hash: str,
) -> dict[str, object]
```

Required output fields follow Phase 1226:

```json
{
  "causal_frontier_refs": ["sha256:<...>"],
  "causal_predecessor_ref": "sha256:<...>",
  "epoch_sequence": 12,
  "event_kind": "commit.epoch",
  "genesis_domain_hash": "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c",
  "issuer": "consensus_layer",
  "quorum_proof_ref": "sha256:<...>",
  "schema_version": "commit_epoch_causal_frontier_mapping_1226.v0.1",
  "state_root_cidv1_hex": "<...>",
  "timestamp_policy": "epoch_sequence_only_no_wall_clock"
}
```

Genesis epoch-zero is the only case where `causal_predecessor_ref`,
`quorum_proof_ref`, and `state_root_cidv1_hex` may be `null`. For epoch `N > 0`,
all three are required.

### Layer D — Consensus-State Adapter

**Status:** required before any production claim.

Maps finalized consensus records into Layers B and C. It must read from either:

- Python consensus/finality fixtures already normalized by
  `epoch_state_runtime.py` / `finality_evaluator.py`; or
- a read-only Rust consensus export such as `EpochStore` / `ILCAppReadService`.

It must not create a Python write path into Rust consensus. Python can render or
verify projections, but it is not the authority that finalizes epochs.

### Layer E — Test/Devnet Emission Harness

**Status:** optional after Layers B-D.

Provides deterministic fixture/devnet tests that show:

- a finalized epoch record can produce a quorum-proof projection;
- the projection hashes to `quorum_proof_ref`;
- the causal-frontier projection hashes deterministically;
- the canonical `ProtocolEvent` can include refs derived from those inputs; and
- no wall-clock or float economics enter the path.

This layer may be used for integration testing. It still must not claim public
or production emission.

### Layer F — Production Consensus Emission

**Status:** explicitly out of scope.

Production emission requires a later sensitive phase and must close or replace
the carry-forward only after the runtime proves:

- finalized consensus records are the source of truth;
- aggregate BLS signature material is verified before projection;
- causal predecessor refs are computed from canonical prior envelopes;
- epoch sequence is monotonic;
- Genesis epoch-zero special case is handled exactly once;
- the agent-submission boundary remains closed; and
- no wall-clock timestamp is a protocol input.

---

## 5. Edge Cases To Specify Before Runtime Expansion

Future Fix2+ work must handle these cases explicitly:

| Case | Required behavior |
|------|-------------------|
| Empty quorum records, epoch `0` | Allowed only for Genesis epoch-zero projection |
| Empty quorum records, epoch `N > 0` | Fail closed |
| Missing predecessor for epoch `N > 0` | Fail closed; do not synthesize from wall-clock or local state |
| Duplicate signer IDs | Fail closed unless a future Rust export proves canonical deduplication before this layer |
| Unsorted signer IDs | Normalize to sorted ascending order before hashing, or fail closed; the chosen rule must be tested |
| Non-hex aggregate signature bytes | Fail closed |
| Non-canonical `state_root_cidv1_hex` | Fail closed |
| Mismatched epoch number between record and projection | Fail closed |
| Conflicting finalization states | No production emission; test/devnet harness may emit `rolled_back` or `superseded` only from explicit caller input |
| Decimal economic totals | Must remain finite non-negative `Decimal`; no float compatibility path |
| Rust record unavailable over gRPC | Connector may not invent proof material; emit a deterministic unavailable token instead |

---

## 6. FixN Strike-Force Sequence

This sequence is intentionally narrow. Each runtime expansion after Fix1 touches
the finality surface and should be treated as sensitive unless a prompt says it
is spec/test-only.

| Step | Scope | Output |
|------|-------|--------|
| Fix1 | Full connector specification | This document and doc-lock tests |
| Fix2 | Implement Layer B quorum-proof projection builder | Runtime helper + deterministic tests |
| Fix3 | Implement Layer C causal-frontier projection builder | Runtime helper + Genesis/N>0 tests |
| Fix4 | Implement Layer D fixture adapter from Python epoch/finality records | Adapter + fail-closed tests |
| Fix5 | Add Rust fixture mapping tests using committed sample `StoredCheckpoint`/`EpochSettlementRecord` shape | Cross-layer fixture tests; no Rust mutation by default |
| Fix6 | Add devnet/test harness that exercises Layers A-E end-to-end | Integration tests only; no production emission |
| Future phase | Production consensus emission authorization | Requires explicit sensitive GO and carry-forward closure criteria |

Do not collapse Fix2-Fix6 into one large runtime mutation unless the prompt
explicitly authorizes a larger sensitive strike-force phase.

Sensitivity rule for the remaining strike-force work: Fix2 and Fix3 are
sensitive because they mutate the `commit.epoch` finality-surface connector.
Fix4 is also sensitive if it adds adapter code to `ilc_core/protocol/` or any
consensus/finality runtime surface; it is non-sensitive only if scoped to tests,
fixtures, or documentation. Fix5 is non-sensitive only while it remains test-only
and read-only against Rust source/fixture shapes. Fix6 is non-sensitive only if
confined to devnet/test harnesses with no runtime production path and no
carry-forward closure claim.

---

## 7. Non-Goals

Fix1 and the subsequent Fix2-Fix6 strike-force plan do not authorize:

- live consensus writing;
- public or production `commit.epoch` emission;
- Python write access to Rust consensus;
- new CDL openings or CDL register mutation;
- CDL-087 ratification;
- v0.2 signing;
- public repository publication;
- release-key generation;
- replacing signed Genesis v0.1 artifacts;
- modifying immutable diagnostic anchors; or
- closing `commit_epoch_projection_runtime_required_before_production_emission`.

---

## 8. Ratification / Carry-Forward State

Produced by this Fix1:

```text
phase_1236_fix1_commit_epoch_full_connector_spec_committed
```

Still open after this Fix1:

```text
commit_epoch_projection_runtime_required_before_production_emission
commit_epoch_production_emission_not_yet_authorized
```

Recommended next action:

```text
GO Phase 1236 Fix2
```

only if the human reviewer wants to begin implementing Layer B quorum-proof
projection builder functionality before moving to Phase 1237.
