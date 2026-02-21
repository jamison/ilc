# ILC D2 Minimal Schema Specification 255 v0.1

Status: Non-ratified specification artifact
Date: 2026-02-21
Window: Phase 255
Primary anchors:
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_d2e_pipeline_scaffolding_spec_v0.1.md`

## 1. Purpose and scope

This document specifies the minimum D2 schema subset required to unblock D2e-03 readiness planning:
- D2-01 Node schema specification,
- D2-02 Edge schema specification,
- D2-08 Epoch Record schema specification.

This document does not define implementation code and does not cover the full D2 schema catalog.

## 2. Node schema specification (D2-01)

Required fields for canonical Node objects:
1. `node_id` (CIDv1)
2. `payload`
3. `primitive_type` (enum constrained to New Seven primitives)
4. `creator_agent_id` (CIDv1)
5. `epoch_created`
6. `parent_edges` (list of edge CIDs)
7. `signature` (COSE Sign1 envelope)

Canonical ordering requirement:
- Node fields must be encoded in deterministic canonical order.

Round-trip invariant:
- encode -> decode -> re-encode must produce identical canonical bytes.

## 3. Edge schema specification (D2-02)

Required fields for canonical Edge objects:
1. `edge_id` (CIDv1)
2. `source_node_id`
3. `target_node_id`
4. `edge_type` (enum mapped to protocol operation semantics)
5. `weight`
6. `epoch_created`
7. `creator_agent_id`

Canonical ordering requirement:
- Edge fields must be encoded in deterministic canonical order.

Protocol mapping requirement:
- `edge_type` values map to the New Seven operational semantics.

## 4. Epoch Record schema specification (D2-08)

Required fields for canonical Epoch Record objects:
1. `epoch_id`
2. `participating_agents`
3. `scoring_results`
4. `reward_distribution`
5. `finalization_hash`
6. `previous_epoch_hash`
7. `timestamp`

Hash-chain invariant:
- `finalization_hash` for epoch N is derived from canonical bytes of epoch-N record.
- `previous_epoch_hash` references epoch N-1 and establishes chain linkage.

## 5. Canonical encoding rules

Canonical encoding subset for this minimum D2 specification:
- DAG-CBOR canonical form for schema objects,
- CIDv1 derivation from canonical bytes,
- deterministic field ordering across schema objects.

Encoding boundary rule:
- NDJSON is for logs only and is not used as schema object encoding.

## 6. Deferred schemas

The following D2 schemas are deferred and out of scope in this minimum specification:
- Shard
- Agent Profile
- Star Map Entry
- Subscription
- Inter-Agent Contract
- CapProof Bundle
- Governance Proposal
- Quorum Record

## 7. Non-goal boundaries

This phase does not:
- implement DAG-CBOR schema encoding code,
- provide test-vector byte fixtures,
- implement COSE signing logic,
- change `ilc_core/` runtime behavior,
- mutate any CDL status.
