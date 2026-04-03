# ILC RC0.1 Persisted Graph Contract Lock 577 v0.1

Status: locked
Date: 2026-04-03
Phase: 577
Owner lane: G8 implementation cluster

## 1. Bounded RC target

Phase 577 locks the minimum durable graph contract for the RC0.1 curated
testnet lane.

This packet authorizes the smallest persisted graph record set required for the
live economic and agent-loop cutover without claiming public linkage taxonomy
or payout-traceability closure.

Required governance tokens:
- `minimum_persisted_graph_contract_rc0_1`
- `claim_support_refute_quorum_attribution_epoch_commit_required_record_set`
- `persisted_graph_contract_precedes_live_submission_cutover`
- `runtime_store_and_manifest_identity_must_align`
- `query_surfaces_must_read_durable_state_not_projection_only`
- `graph_linkage_traceability_public_contract_deferred_post_rc0_1`

## 2. Minimum persisted record set

`minimum_persisted_graph_contract_rc0_1`.

The minimum durable record set for RC0.1 is:
- claim node
- support edge
- refute edge
- quorum record
- attribution record
- epoch-commit record

`claim_support_refute_quorum_attribution_epoch_commit_required_record_set`.

These are distinct durable record roles even when the current runtime uses
bounded adapters or adjacent manifests while converging on the full record set.

## 3. Node and link contract

A claim node is the minimum graph object for bounded RC0.1 claim persistence.

Support and refute edges are graph relations and must not be collapsed into
opaque wallet-only or ledger-only metadata.

Persisted graph queries must be able to distinguish node records from link
records deterministically.

The bounded RC0.1 lane treats claim nodes, support edges, and refute edges as
the minimum graph-facing runtime surface that later query tools may rely on.

## 4. Quorum, attribution, and epoch-commit contract

Quorum record, attribution record, and epoch-commit record are distinct durable
record roles even if the current runtime temporarily derives some of them from
adjacent manifests.

The RC0.1 runtime may use bounded adapters while converging on the full minimum
record set, but it must not erase these role distinctions.

Live submission cutover is not considered authoritative until these record
roles are explicit in the runtime-facing contract.

## 5. Runtime-store integrity rule

`runtime_store_and_manifest_identity_must_align`.

Runtime-store identity and manifest identity must align deterministically.

`query_surfaces_must_read_durable_state_not_projection_only`.

Durable query surfaces must read from runtime state rather than projection-only
exports when runtime state is present.

Stable RC0.1 graph-facing query surfaces must remain machine-legible and
include bounded equivalents for:
- `graph-summary`
- `graph-node`
- `graph-links`
- `quorum-record`
- `store-summary`

Missing, mismatched, or corrupted graph-state identity must fail closed with
deterministic tokens.

## 6. Explicit deferrals to RC0.1+

Deferred beyond RC0.1:
- fuller public graph linkage taxonomy
- public receipt and payout traceability contract
- broader node-schema or executable-descriptor work
- public-release minting and lineage stabilization

`graph_linkage_traceability_public_contract_deferred_post_rc0_1`.
