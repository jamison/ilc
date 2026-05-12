# ILC Local Graph Memory Projection Sidecar 1311 v0.1

Status: implemented / local-only / no public serving
Date: 2026-05-11
Phase: 1311
Owner lane: G8 graph-native sidecars / Gap 9 / CCSS prerequisite

Required tokens:

```text
local_graph_memory_projection_sidecar_phase_1311.v0.1
public_safe_projection_implementation_local_only_phase_1311
confidential_coordination_projection_reference_local_only_phase_1311
public_sidecar_projection_serving_not_enabled_phase_1311
phase_1312_projection_privacy_field_filtering_tests_next
public_rc_remains_blocked_after_phase_1311
```

Phase 1311 was executed after explicit human authorization:

```text
GO Phase 1311
```

This phase implements a deterministic local graph/memory projection sidecar at
`ilc_core/sidecars/local_graph_memory_projection.py`. It produces bounded,
canonical, local-only projection envelopes. It does not authorize public
sidecar/projection serving, non-loopback bind, public listener, peer discovery,
public P2P, public fetch serving, public confidential messaging, public
confidential coordination serving, source export, package publication, release
artifacts, signing, wallet withdrawal, ECU minting, or ILC settlement.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The Phase 1311 required tokens were found only in the executable prompt before implementation, then carried into code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, and the graph-native sidecar architecture. |
| Section 0b Concept-discovery search | Direct searches covered sidecar projection, public-safe projection, field classification, privacy filter, private shard, gated shard, encrypted coordination node, sealed payload, membership, route history, public serving, non-loopback, listener, and peer discovery. |
| Section 0c Contradiction and non-claim search | Searches confirmed the standing non-claims: public sidecar/projection serving is not enabled, non-loopback bind is not enabled, public listener is not enabled, peer discovery is not enabled, public confidential messaging is not claimed, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Direct-read sources included PLANNING_INDEX, Capsule v5.53, STATUS tail, the Window 1303-1316 sequence lock and guidance, Phase 1297 projection schema, Phase 1298 bind/listener/peer-discovery preflight, the graph-native sidecar architecture, the CCSS forward plan, and `ilc_core/graph/sidecar_query_runtime.py`. Newly carried implementation tokens are the six Phase 1311 required tokens. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Implementation

The Phase 1311 sidecar exposes local Python functions only:

- `local_graph_memory_projection_sidecar_manifest()`
- `build_aggregate_summary_record_from_query_result()`
- `build_private_gated_shard_header_record()`
- `build_encrypted_coordination_reference_record()`
- `build_public_safe_projection_envelope()`
- `validate_public_safe_projection_envelope()`
- `export_public_safe_projection_envelope_json()`

The sidecar depends on the existing local read-only query runtime version
`sidecar_query_runtime_1237.v0.1` and the Phase 1297 schema token
`sidecar_public_safe_projection_schema_phase_1297.v0.1`.

It is wired into `ilc_core/sidecars/registry_manifest.py` as
`local_graph_memory_projection` with status:

```text
local_projection_substrate_implemented_phase_1311_privacy_tests_routed_phase_1312
```

## 2. Projection Field Table

| Field family | Phase 1311 disposition |
|--------------|------------------------|
| Envelope version, schema dependency, projection epoch, profile, kind, field policy, source artifact root ref, count, byte size, hash, tokens | Allowed only inside the local canonical envelope. |
| Aggregate graph counts | Allowed as non-identifying counts: node count, edge count, hyperedge count, query result count, record count, private shard header count, encrypted coordination ref count. |
| Public proof or artifact references | Allowed only as opaque digest refs such as `artifact:<sha256>`, `manifest:<sha256>`, `proof:<sha256>`, or `root:<sha256>`. |
| Private/gated shard header | Allowed only as opaque digest refs: `private_shard_header:<sha256>`, `shard_commitment:<sha256>`, `capability_policy:<sha256>`, and encrypted coordination refs. |
| Encrypted coordination node reference | Allowed only as opaque digest refs: `encrypted_coordination:<sha256>`, `ciphertext:<sha256>`, and `capability:<sha256>`. |
| Raw graph node ids, edge ids, centrality ranking, path-to-Genesis evidence, convergence trace membership | Not emitted by the Phase 1311 public-safe envelope. Phase 1312 must add broader privacy/filtering tests. |
| Plaintext, membership sets, route history, sealed payloads, AgentID, requester id, client IP, harness identity, OpenClaw identity, Tailscale identity | Denied fail-closed by record/envelope validation. |
| Wallet, stake, reward, ECU, ILC, settlement, withdrawal, transfer, spend, economic position | Denied fail-closed and not modeled by this sidecar. |

## 3. Confidential Coordination Boundary

Phase 1311 gives confidential coordination only a local projection reference
shape. A private/gated shard header can be represented by commitments and
capability-policy refs; an encrypted coordination node can be represented by an
encrypted object ref and ciphertext digest ref. No plaintext, membership, route
history, raw sealed payload, public confidential messaging claim, or public
confidential coordination serving claim is created.

The actual private/gated shard sidecar, capability/membership sidecar, sealed
sender sidecar, gossip/jitter sidecar, and private OpenClaw/NemoClaw dry run
remain routed to later CCSS phases 1324-1329.

## 4. Validation And Canonicalization

The implementation enforces:

- deterministic canonical JSON with `sort_keys=True`, compact separators, and
  `allow_nan=False`;
- no Python `float` values in projection payloads;
- no tuples or non-JSON value types in projection payloads;
- string-only mapping keys;
- bounded payload depth and node count;
- bounded record count and byte size;
- exact record schemas by `record_kind`;
- sorted and unique digest reference lists;
- epoch integers for projection, shard, and coordination epochs;
- all public-serving authorization flags false.

## 5. Non-Claims

Phase 1311 does not authorize:

- public RC claim or public launch claim;
- source export, source publication, package publication, release artifact production, release keys, release envelopes, or signing;
- public claimability/API activation or public verifier service;
- public P2P, public fetch serving, public sidecar/projection serving, non-loopback bind, public listener, or peer discovery;
- helper promotion, marker removal, helper stripping, or public export stripping;
- Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening;
- wallet withdrawal, transfer, spend, wallet signing, ledger-write, ECU minting, ILC settlement, or withdrawal runtime;
- public confidential messaging or public confidential coordination serving.

## 6. Next Gate

Phase 1312 is sensitive and requires explicit `GO Phase 1312`.

```text
phase_1312_projection_privacy_field_filtering_tests_next
```
