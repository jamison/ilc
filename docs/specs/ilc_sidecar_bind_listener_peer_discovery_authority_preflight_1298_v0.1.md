# ILC Sidecar Bind Listener Peer Discovery Authority Preflight 1298 v0.1

Status: preflight only / no public serving
Date: 2026-05-10
Phase: 1298
Owner lane: G8 public-RC sidecar projection boundary

Required tokens:

```text
sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
public_rc_remains_blocked_after_phase_1298
phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next
```

Verdict:

```text
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
```

Phase 1298 was executed after explicit human authorization:

```text
GO Phase 1298 and any subsequent non-sensitive phases, in order
```

The authorization grants only this bind/listener/peer-discovery authority
preflight. Phase 1299 is sensitive and requires explicit `GO Phase 1299`; it
is not authorized by the "subsequent non-sensitive phases" continuation clause.

Phase 1298 does not authorize non-loopback bind, wildcard bind, public host
bind, public listener, socket listener, HTTP route, peer discovery, public
sidecar/projection serving, public projection endpoint serving, public P2P,
public fetch serving, public claimability, public verifier service, wallet
withdrawal, wallet transfer, wallet spend, ECU minting, ILC settlement, source
allowlist export, public repository publication, public package publication,
release artifact production, release keys, release envelopes, Genesis Atlas
mutation, Genesis Atlas regeneration, Genesis Atlas signing, v0.2 signing, CDL
mutation, CDL-088 opening, public RC, public launch, IP filing, or paper
publication.

---

## 0. Discovery Discipline

Phase 1298 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Verified the Phase 1298 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1298_g8_sidecar_bind_listener_peer_discovery_authority_preflight.md` and carried them into this packet, tests, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.52, and Roadmap v1.1. |
| Section 0b Concept-discovery search | Searched sidecar bind, non-loopback, wildcard bind, public host, listener, socket, HTTP route, peer discovery, public projection, public sidecar, public fetch, public P2P, TransportPrincipal, serving peer, and endpoint terms. |
| Section 0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, no listener, no bind, loopback-only, local-only, no public, no peer discovery, no serving, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source grants public sidecar/projection serving authority, listener creation authority, non-loopback bind authority, wildcard bind authority, public host bind authority, or peer-discovery authority. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md`
- `docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md`
- `docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md`
- `docs/specs/ilc_sidecar_public_safe_projection_schema_1297_v0.1.md`
- `ilc_core/graph/sidecar_public_path_preflight.py`
- `ilc_core/graph/sidecar_query_runtime.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Runtime Readback

The current runtime sidecar surfaces remain local, bounded, and non-serving:

- `ilc_core/graph/sidecar_query_runtime.py` is a read-only in-process query
  runtime. It exports canonical JSON with `sort_keys=True`, `allow_nan=False`,
  and compact separators; rejects Python `float`; rejects non-finite
  `Decimal`; and enforces byte/result bounds.
- `ilc_core/graph/sidecar_public_path_preflight.py` is marked
  `PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface`.
  Its file header records no listener, bind, or serving surface.
- `sidecar_public_path_preflight.py` deliberately does not open a listener,
  bind a socket, serve projection data, or enable peer discovery.
- The Phase 1278 helper still records `sidecar_public_serving_not_enabled_phase_1278`,
  `no_new_public_listener_phase_1278`, `non_loopback_bind_not_enabled_phase_1278`,
  `public_projection_endpoint_not_enabled_phase_1278`, and
  `sidecar_projection_privacy_review_required_phase_1278`.

Phase 1298 does not change runtime code. It records the authority boundary a
future explicitly authorized public-serving phase must satisfy before any
sidecar public projection can listen, bind, discover peers, or serve data.

---

## 2. Bind Listener Peer Discovery Authority Table

| Surface | Phase 1298 authority decision | Required later authority |
|---------|-------------------------------|--------------------------|
| Local in-process sidecar query runtime | Preserved as local/read-only only. | None for existing local reads; any public exposure remains separately gated. |
| Harness-owned subprocess or transport seam | Preserved as local test infrastructure only. | Explicit harness scope and no public serving claim. |
| Loopback-only historical boundary | Preserved as historical allowance only; Phase 1298 adds no new listener. | A later exact `GO` would need to authorize a concrete loopback listener implementation. |
| Unix-socket historical boundary | Preserved as historical allowance only; Phase 1298 adds no socket server. | A later exact `GO` would need to authorize a concrete Unix-socket listener implementation. |
| Non-loopback bind | Not enabled. Token: `non_loopback_bind_not_enabled_phase_1298`. | Explicit public sidecar serving authority, bind policy, TransportPrincipal public-path activation, privacy filter implementation, and release/publication clearance. |
| Wildcard bind | Not enabled. | Explicit public bind authority plus host allowlist and operator deployment policy. |
| Public host bind | Not enabled. | Explicit public bind authority plus host allowlist, release authority, and abuse-control policy. |
| Public listener | Not enabled. Token: `public_listener_not_enabled_phase_1298`. | Explicit listener implementation authorization, no `PUBLIC_RC_EXCLUDE` helper dependence, hard timeout and bounded payload contracts, and operator deployment policy. |
| Socket listener | Not enabled. | Same as public listener; no socket is opened by Phase 1298. |
| HTTP route | Not enabled. | Explicit API contract, timeout policy, privacy review, rate limits, and TransportPrincipal-bound admission. |
| Peer discovery | Not enabled. Token: `peer_discovery_not_enabled_phase_1298`. | Explicit peer-discovery protocol, authenticated TransportPrincipal identity, replay/nullifier policy, ban/rate/privacy controls, and public P2P/fetch authority. |
| Public sidecar/projection serving | Not enabled. Token: `public_sidecar_projection_serving_not_enabled_phase_1298`. | Explicit serving authority, Phase 1297 privacy filter implementation/review, bind/listener authority, source/release authorization, and post-ratification helper replacement or explicit promotion prerequisites. |
| Public P2P | Not activated. | Separate public P2P sequence authorization and TransportPrincipal public-path activation. |
| Public fetch serving | Not enabled. | Separate public fetch serving authorization after CDL-087 and public transport controls. |

Authority summary:

```text
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
```

Public P2P, public fetch serving, and public sidecar/projection serving remain
not activated by Phase 1298.

---

## 3. Activation Preconditions Carried Forward

Future public sidecar projection serving still requires:

| Gate | Phase 1298 disposition |
|------|------------------------|
| Explicit public sidecar/projection serving authority | Not activated by Phase 1298. |
| Public-safe field schema | Recorded by Phase 1297, but not served. |
| Privacy filter implementation and review | Required before activation. |
| Bind/listener policy | Preflighted only; no bind or listener authority granted. |
| Peer-discovery policy | Preflighted only; no peer discovery authority granted. |
| TransportPrincipal public-path activation | Required before public projection serving. |
| Post-ratification CDL-087 TransportPrincipal helper replacement or explicit promotion prerequisites | Still open. |
| Admission, ban, rate-limit, replay, and privacy controls | Still future contracts only after Phase 1296. |
| Replay/nullifier and duplicate-claim registry policy | Still open. |
| Source allowlist export execution | Not executed by Phase 1298. |
| Release allowlist/artifact/key/envelope readiness | Still open; routed to Phase 1299. |
| Counsel, IP, and publication clearance | Still open. |

The next locked phase is:

```text
phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next
```

Phase 1299 is sensitive and requires explicit `GO Phase 1299`.

---

## 4. Non-Claims

Phase 1298 does not authorize or perform:

- public sidecar/projection serving
- public projection endpoint serving
- non-loopback sidecar/projection serving
- non-loopback bind
- wildcard bind
- public host bind
- public listener
- socket listener
- HTTP route
- public endpoint
- peer discovery
- public fetch serving
- public P2P exposure
- TransportPrincipal public-path activation
- public credential issuer authority
- credential lifecycle policy activation
- public revocation registry activation
- public replay cache activation
- admission policy activation
- ban registry activation
- public rate-limit state activation
- privacy policy activation
- Werner overlay activation
- helper promotion
- marker removal
- materialized export manifest production
- source allowlist export execution
- public repository publication
- public package publication
- release artifact production
- release-key generation
- release envelope production
- release manifest instance production
- public claimability activation
- public claimability API activation
- public verifier service
- public claim endpoint
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement
- withdrawal runtime activation
- CDL mutation
- CDL-088 opening
- Genesis Atlas mutation
- Genesis Atlas regeneration
- Genesis Atlas signing
- v0.2 signing
- public RC claim
- public launch claim
- IP filing
- paper publication
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1298:

```text
public_rc_remains_blocked_after_phase_1298
```

Remaining blocker classes include final public claimability API/verifier
authority, privacy filter implementation and review, replay/nullifier and
duplicate-claim registry policy, actual TransportPrincipal public-path
activation authority, post-ratification helper replacement or explicit
promotion prerequisites, actual public sidecar/projection serving authority,
sidecar bind/listener/peer-discovery authority, release publication and v0.2
signing authority, counsel/IP/publication authorization, source publication and
release artifact authorization, wallet withdrawal/transfer/spend semantics,
ECU minting, and ILC settlement.

---

## 5. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_sidecar_bind_listener_peer_discovery_authority_preflight_1298_v0.1.md -> sidecar/public_path
graph_delta=support_tests_added:tests/test_phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
