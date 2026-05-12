# ILC Projection Privacy Field Filtering Tests 1312 v0.1

Status: implemented / local-only / no public serving
Date: 2026-05-11
Phase: 1312
Owner lane: G8 graph-native sidecars / Gap 9 / CCSS prerequisite

Required tokens:

```text
projection_privacy_field_filtering_tests_phase_1312.v0.1
projection_privacy_filters_hardened_phase_1312
confidential_coordination_projection_non_leakage_tests_phase_1312
public_sidecar_projection_serving_not_enabled_phase_1312
phase_1313_public_fetch_p2p_activation_candidate_default_off_next
public_rc_remains_blocked_after_phase_1312
```

Phase 1312 was executed after explicit human authorization:

```text
GO Phase 1312
```

This phase hardens tests and local validation around
`ilc_core/sidecars/local_graph_memory_projection.py`. It does not authorize
public sidecar/projection serving, non-loopback bind, public listener, peer
discovery, public P2P, public fetch serving, public confidential messaging,
public confidential coordination serving, source export, package publication,
release artifacts, signing, wallet withdrawal, ECU minting, or ILC settlement.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The six Phase 1312 required tokens were found in the executable prompt before implementation and then carried into code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, and graph-native sidecar architecture docs. |
| Section 0b Concept-discovery search | Direct searches covered privacy filter, field filtering, public-safe projection, identifier leakage, membership, sealed payload, route history, private shard, encrypted coordination, bounded serving, projection serving, and historical Signal/gossip/jitter context through MemPalace and direct repo reads. |
| Section 0c Contradiction and non-claim search | Searches confirmed public sidecar/projection serving, non-loopback bind, public listener, peer discovery, public confidential messaging, public confidential coordination serving, public P2P/fetch, wallet economics, release, and signing remain not authorized. |
| Section 0d Source expansion and newly discovered tokens | Direct-read sources included PLANNING_INDEX, Capsule v5.53, STATUS tail, the Window 1303-1316 sequence lock/guidance, Phase 1297 public-safe projection schema, Phase 1311 projection implementation/spec/tests, graph-native sidecar architecture, CCSS forward plan, ADR-0025, ADR-0034, private shard proposal 791, and leakage/jitter research. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Hardened Privacy Contract

Phase 1312 keeps the Phase 1311 envelope shape, but adds an explicit
export-level leak guard for raw identifier fragments embedded inside otherwise
valid string values. This is separate from the Phase 1311 forbidden-key guard.
The intent is simple: a public-safe projection cannot smuggle a private node id,
requester id, route trace, membership marker, wallet field, stake field, or
plaintext payload inside a field that has an allowed name.

The hardening is local and deterministic:

- `projection_privacy_field_filtering_required_tokens()` records the Phase 1312
  hardening tokens.
- `projection_privacy_forbidden_fragments()` records the export-fragment deny
  vocabulary used by the tests.
- `validate_projection_privacy_filtering_payload()` rejects unsafe JSON,
  forbidden private keys, and forbidden raw export fragments before canonical
  serialization.
- `canonical_local_graph_memory_projection_json()` now uses the Phase 1312
  privacy guard before `json.dumps(..., sort_keys=True, allow_nan=False)`.
- `local_graph_memory_projection_sidecar_manifest()` now records that privacy
  filtering, confidential-coordination non-leakage tests, and bounded-serving
  blocker tests are hardened.

## 2. Filtering Matrix

| Field or fragment family | Phase 1312 disposition |
|--------------------------|------------------------|
| Exact Phase 1311 record keys and envelope keys | Allowed only when the whole record/envelope matches the exact schema. Unknown fields are rejected. |
| Aggregate counts | Allowed as non-identifying counts only. Raw graph records are not passed through. |
| Opaque artifact/proof/root refs | Allowed only as prefixed sha256 digest refs. |
| Opaque private/gated shard refs | Allowed only as `private_shard_header`, `shard_commitment`, `capability_policy`, and `encrypted_coordination` digest refs. |
| Opaque encrypted coordination refs | Allowed only as `encrypted_coordination`, `ciphertext`, and `capability` digest refs. |
| Raw `node:` and `edge:` handles | Denied at export-fragment level. |
| `AgentID`, `agent_id`, requester id, client IP, harness/OpenClaw/Tailscale identity | Denied at key and export-fragment level. |
| Membership, route history, sealed payload, plaintext payload | Denied at key and export-fragment level. |
| Wallet, stake, economic position, graph position | Denied at key and export-fragment level. |
| Public serving flags | Must remain false. Any true flag fails validation. |

## 3. Confidential Coordination Non-Leakage

Phase 1312 confirms that confidential-coordination projection remains an opaque
reference projection, not a messaging product claim. The local preview envelope
can reference private/gated shard headers and encrypted coordination objects by
digest, but it does not disclose plaintext, membership, route history, raw
sealed payloads, sender/requester identity, or public serving state.

This is still only a prerequisite for later CCSS work. Private/gated shard,
capability/membership, sealed sender, gossip/jitter, and OpenClaw/NemoClaw
private droplet dry-run slices remain routed to Phases 1324-1329.

## 4. Registry Impact

The sidecar registry now records `local_graph_memory_projection` as:

```text
local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312
```

Its authority gate is:

```text
phase_1311_1312_local_projection_substrate_privacy_hardened_public_serving_blocked
```

This is still local/package metadata only. It does not create a server,
listener, socket, HTTP route, public endpoint, non-loopback bind, peer discovery
path, public P2P/fetch surface, public confidential messaging surface, wallet
action, ECU mint, or ILC settlement surface.

## 5. Non-Claims

Phase 1312 does not authorize:

- public RC claim or public launch claim;
- source export, source publication, package publication, release artifact production, release keys, release envelopes, or signing;
- public claimability/API activation or public verifier service;
- public P2P, public fetch serving, public sidecar/projection serving, non-loopback bind, public listener, or peer discovery;
- helper promotion, marker removal, helper stripping, or public export stripping;
- Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening;
- wallet withdrawal, transfer, spend, wallet signing, ledger-write, ECU minting, ILC settlement, or withdrawal runtime;
- public confidential messaging or public confidential coordination serving.

## 6. Next Gate

Phase 1313 is sensitive and requires explicit `GO Phase 1313`.

```text
phase_1313_public_fetch_p2p_activation_candidate_default_off_next
```
