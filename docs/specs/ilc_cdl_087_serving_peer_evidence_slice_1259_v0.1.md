# ILC CDL-087 Serving-Peer Evidence Slice 1259 v0.1

**Date:** 2026-05-08
**Phase:** 1259
**Status:** local production-candidate evidence slice
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
cdl_087_serving_peer_evidence_slice_phase_1259.v0.1
production_candidate_tier_classification_runtime_evidence_recorded_phase_1259
bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259
no_public_fetch_serving_enabled_phase_1259
```

## 1. Scope and Verdict

Phase 1259 records local production-candidate evidence for CDL-087 Conditions 2
and 3:

- Tier A/B/C classification evidence for artifact records.
- Genesis-verifiable bootstrap snapshot builder/verifier evidence.

Implementation:

```text
ilc_core/network/d2d/cdl087_serving_peer_evidence.py
```

Focused tests:

```text
tests/test_phase_1259_cdl087_serving_peer_evidence_slice.py
```

Verdict:

```text
cdl_087_conditions_2_and_3_local_evidence_recorded_phase_1259
```

This is a local evidence slice. It does not expose public fetch serving,
public sidecar/projection serving, public P2P, or any non-loopback endpoint.

## 2. Evidence Surface

The helper exports:

| Surface | Purpose |
|---------|---------|
| `classify_artifact()` | Classifies artifact records as `Tier A`, `Tier B`, or `Tier C` from explicit tier or artifact type. |
| `build_tier_classification_evidence()` | Builds deterministic local serving-peer evidence with counts by tier and explicit non-public boundary fields. |
| `build_bootstrap_snapshot()` | Builds a Genesis-verifiable bootstrap snapshot with required CDL-087 fields. |
| `verify_bootstrap_snapshot()` | Recomputes artifact hashes, checks Genesis lineage, validates authority refs, and rejects public-serving flags. |
| `export_bootstrap_snapshot_json()` | Emits canonical JSON with `sort_keys=True`, compact separators, and `allow_nan=False`. |
| `verify_bootstrap_snapshot_json()` | Requires canonical JSON and rejects non-canonical encodings. |

The implementation performs no filesystem I/O, network I/O, socket binding, HTTP
serving, peer discovery, CDL mutation, or release operation.

## 3. Tier Classification Evidence

Tier A includes the required high-authority artifact classes from the Phase 1246
readiness route, including:

- Genesis root artifacts.
- ADR-0004 truth primitives.
- Accepted CDLs and ADRs.
- Signed manifests.
- Lineage receipts.
- CDL-086 release artifacts.
- Bootstrap bundles.
- Epoch/checkpoint roots.

Tier B includes hot operational content such as recent epoch deltas, graph
projection snapshots, route indexes, agent bootstrap indexes, and recent
manifest deltas.

Tier C is the fallback advisory class for artifacts outside the Tier A/B
production-candidate rules.

## 4. Bootstrap Snapshot Evidence

The builder/verifier covers the CDL-087 prelock snapshot fields:

```text
snapshot_manifest
genesis_domain_hash
snapshot_epoch
artifact_list
lineage_proof_chain
epoch_checkpoint_range
authority_refs
graph_projection_export
```

Verification rejects:

- malformed Genesis hashes;
- wrong expected Genesis hash;
- missing authority refs;
- stale snapshot epoch ranges;
- artifact hash mismatch;
- missing Genesis lineage;
- non-canonical JSON;
- float values in machine payloads;
- public fetch serving or network endpoint flags.

## 5. Condition Routing

| CDL-087 condition | Phase 1259 status |
|-------------------|-------------------|
| Condition 2 - Tier A/B/C classification in a production-candidate serving peer | Local evidence surface recorded. Later sensitive ratification must decide whether this evidence is sufficient for ratification. |
| Condition 3 - Bootstrap snapshot format implemented and Genesis-verifiable | Local builder/verifier evidence recorded. Later sensitive ratification must decide whether this evidence is sufficient for ratification. |
| Condition 4 - Production-candidate observability collection | Still routed to Phase 1260. |
| Condition 5 - CDL-077 final limiter regression | Still routed to Phase 1260. |

## 6. Non-Authorization Boundary

Phase 1259 does not authorize:

- public fetch serving;
- public sidecar/projection serving;
- public P2P exposure;
- non-loopback endpoint exposure;
- TransportPrincipal runtime implementation;
- CDL register mutation;
- CDL-087 ratification;
- CDL-088 opening;
- public RC claim;
- public repository publication;
- public claimability activation;
- ECU minting;
- ILC settlement activation;
- release-key generation;
- release envelope production;
- v0.2 signing.

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/network/d2d/cdl087_serving_peer_evidence.py -> transport/cdl087
graph_delta=support_tests_added:tests/test_phase_1259_cdl087_serving_peer_evidence_slice.py -> validation
graph_delta=support_only:docs/specs/ilc_cdl_087_serving_peer_evidence_slice_1259_v0.1.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1259_cdl087_serving_peer_evidence_slice_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 8. Next Phase

Phase 1260 remains the next locked phase:

```text
cdl_087_observability_collection_window_phase_1260.v0.1
```
