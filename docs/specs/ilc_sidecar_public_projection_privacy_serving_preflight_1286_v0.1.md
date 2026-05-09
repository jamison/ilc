# ILC Sidecar Public Projection Privacy Serving Preflight 1286 v0.1

Status: privacy/serving preflight recorded / no public serving
Date: 2026-05-09
Phase: 1286
Owner lane: G8 public-RC sidecar projection boundary

Required tokens:

```text
sidecar_public_projection_privacy_serving_preflight_phase_1286.v0.1
sidecar_public_serving_not_enabled_phase_1286
non_loopback_bind_not_enabled_phase_1286
public_projection_endpoint_not_enabled_phase_1286
transport_principal_activation_required_before_public_projection_phase_1286
```

Additional carry-forward tokens:

```text
sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving
no_new_public_listener_phase_1286
peer_discovery_not_enabled_phase_1286
phase_1287_release_publication_signing_authorization_preflight_next
public_rc_remains_blocked_after_phase_1286
```

Verdict:

```text
sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving
```

Phase 1286 was executed after explicit human authorization:

```text
GO Phase 1285-1288
```

The authorization is interpreted according to the user's stated preflight
stance for Phases 1285-1288. It authorizes this sensitive preflight packet. It
does not authorize public sidecar/projection serving, a public projection
endpoint, non-loopback bind, wildcard bind, public host bind, listener, peer
discovery, public P2P exposure, public fetch serving, public claimability,
wallet withdrawal, wallet transfer, wallet spend, ECU minting, ILC settlement,
source publication, release artifacts, release keys, release envelopes, Genesis
Atlas mutation, v0.2 signing, CDL mutation, CDL-088 opening, public RC, or
public launch.

---

## 0. Discovery Discipline

Phase 1286 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| §0a Known-token audit | Verified the Phase 1286 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1286_g8_sidecar_public_projection_privacy_serving_preflight.md` and carried them into this packet, the walkthrough, STATUS, PLANNING_INDEX, Roadmap v1.1, and Capsule v5.51. |
| §0b Concept-discovery search | Searched sidecar, projection, public projection, non-loopback, listener, bind, privacy, peer discovery, CDL-087, TransportPrincipal, endpoint, serving, loopback, graph leakage, fetch incentive, and hostile-network terms. |
| §0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, no listener, no public, loopback, `PUBLIC_RC_EXCLUDE`, privacy review, hostile-network, public host, wildcard bind, peer discovery, endpoint, and serving denial terms. |
| §0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source granted public sidecar/projection serving authority. The newly carried tokens are `sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving`, `no_new_public_listener_phase_1286`, `peer_discovery_not_enabled_phase_1286`, `phase_1287_release_publication_signing_authorization_preflight_next`, and `public_rc_remains_blocked_after_phase_1286`. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md`
- `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md`
- `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md`
- `docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md`
- `ilc_core/graph/sidecar_public_path_preflight.py`
- `ilc_core/graph/sidecar_query_runtime.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Boundary Decision

Phase 1286 records a sidecar public projection privacy/serving preflight only:

```text
sidecar_public_serving_not_enabled_phase_1286
non_loopback_bind_not_enabled_phase_1286
public_projection_endpoint_not_enabled_phase_1286
transport_principal_activation_required_before_public_projection_phase_1286
no_new_public_listener_phase_1286
peer_discovery_not_enabled_phase_1286
```

The Phase 1278 helper remains the only current sidecar public-path preflight
substrate:

```text
ilc_core/graph/sidecar_public_path_preflight.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

No new runtime helper was introduced in Phase 1286. The existing helper already
records a fail-closed preflight posture with false authorization flags for
sidecar public serving, public projection endpoint, non-loopback bind, new
public listener, peer discovery, public fetch serving, public P2P, CDL-087
public-projection readiness, TransportPrincipal public-path authority, and
release artifact authority.

No public sidecar/projection serving is authorized. No public projection endpoint is authorized.
No non-loopback bind, wildcard bind, public host bind, listener, socket
listener, HTTP route, public endpoint, peer discovery, public fetch serving, or
public P2P exposure is authorized.

Phase 1285 did not activate TransportPrincipal public-path authority. Therefore
Phase 1286 explicitly carries:

```text
transport_principal_activation_required_before_public_projection_phase_1286
```

## 2. Privacy And Abuse Risks Still Open

The public projection privacy/serving gate remains open because a public
sidecar can leak graph and network information even if the underlying query
runtime is read-only.

Open risks that must be closed before any public projection serving phase:

- graph-membership leakage from node and edge presence;
- serving-peer leakage from observable projection availability;
- fetch-incentive and projection-slice leakage;
- stable node or principal correlation across requests;
- cross-epoch correlation from repeated public queries;
- query abuse, scraping, and enumeration;
- result-size amplification and response-byte exhaustion;
- public-safe field filtering and redaction;
- public query schema versioning and deprecation policy;
- abuse-rate limiting, ban propagation, and replay controls bound to
  authenticated TransportPrincipal material;
- hostile-network validation for timing, retry, partial-response, and malformed
  query behavior.

These are not solved by CDL-087 ratification alone. CDL-087 is ratified, but
Phase 1278 Fix1 explicitly kept public fetch serving and public sidecar
projection blocked.

## 3. Current Permitted Surface

The current permitted surface remains internal, local, offline, or in-process
read-only sidecar query evaluation with bounded canonical exports.

Permitted evidence surfaces:

- `ilc_core/graph/sidecar_query_runtime.py` read-only in-process query runtime.
- `ilc_core/graph/sidecar_public_path_preflight.py` internal
  `PUBLIC_RC_EXCLUDE` fail-closed preflight helper.
- Phase 1268 loopback boundary as historical boundary context, not current
  authority to create a listener.
- Phase 1278 sidecar public-path preflight as prior fail-closed public-path
  evidence.
- Phase 1285 TransportPrincipal activation preflight as evidence that
  TransportPrincipal remains preflight-only and not publicly activated.

Phase 1286 does not promote the Phase 1278 helper into a public RC package and
does not remove its `PUBLIC_RC_EXCLUDE` marker.

## 4. Activation Preconditions Carried Forward

Future public projection serving still requires:

| Gate | Current Phase 1286 disposition |
|------|--------------------------------|
| Explicit public sidecar/projection serving authority | Not activated by Phase 1286. |
| TransportPrincipal public-path activation | Required before public projection. |
| Public projection endpoint | Not enabled by Phase 1286. |
| Non-loopback or wildcard bind | Not enabled by Phase 1286. |
| New listener or socket listener | Not enabled by Phase 1286. |
| Peer discovery | Not enabled by Phase 1286. |
| Privacy filtering and public-safe field schema | Required before activation. |
| Query abuse, rate-limit, ban, replay, and result-size controls | Required before activation. |
| Release allowlist review | Required before public RC package inclusion. |

The next locked phase is:

```text
phase_1287_release_publication_signing_authorization_preflight_next
```

Phase 1287 is sensitive and authorized in the same human `GO Phase 1285-1288`
only as a preflight under the stated no-publication/no-signing stance.

## 5. Non-Claims

Phase 1286 does not authorize or perform:

- public sidecar/projection serving
- public projection endpoint serving
- non-loopback sidecar/projection serving
- non-loopback bind
- wildcard bind
- public host bind
- public listener
- socket listener
- HTTP route or public endpoint
- peer discovery
- public fetch serving
- public P2P exposure
- TransportPrincipal public-path activation
- public claimability activation
- public claimability API activation
- public verifier service
- wallet withdrawal, transfer, or spend
- wallet signing authority or wallet ledger-write authority
- ECU minting
- ILC settlement or withdrawal runtime activation
- source allowlist export execution
- public repository publication
- public package publication
- release-key generation
- release envelope production
- public release artifact production
- Genesis Atlas mutation, regeneration, or signing
- v0.2 signing
- CDL mutation
- CDL-088 opening
- public RC claim
- public launch claim
- IP filing
- paper publication
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1286:

```text
public_rc_remains_blocked_after_phase_1286
```

Remaining blocker classes include release publication and v0.2 signing
authorization, counsel/IP/publication authorization, source publication/release
artifact authorization, final public claimability API/verifier authority,
actual TransportPrincipal public-path activation authority, actual sidecar
public projection serving authority, privacy filtering, public-safe projection
schema, wallet withdrawal/transfer/spend semantics, ECU minting, and ILC
settlement.

---

## 6. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md -> sidecar/public_path
graph_delta=support_tests_added:tests/test_phase_1286_sidecar_public_projection_privacy_serving_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1286_sidecar_public_projection_privacy_serving_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
```
