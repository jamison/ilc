# ILC TransportPrincipal Public-Path Activation Preflight 1285 v0.1

Status: activation preflight recorded / no public path activation
Date: 2026-05-09
Phase: 1285
Owner lane: G8 public-RC transport identity boundary

Required tokens:

```text
transport_principal_public_path_activation_preflight_phase_1285.v0.1
transport_principal_public_p2p_not_activated_phase_1285
public_fetch_serving_not_enabled_phase_1285
requester_id_fallback_still_forbidden_phase_1285
transport_principal_lifecycle_revocation_replay_required_phase_1285
```

Additional carry-forward tokens:

```text
transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation
transport_principal_public_path_authority_not_activated_phase_1285
phase_1286_sidecar_public_projection_privacy_serving_preflight_next
public_rc_remains_blocked_after_phase_1285
```

Verdict:

```text
transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation
```

Phase 1285 was executed after explicit human authorization:

```text
GO Phase 1285-1288
```

The authorization is interpreted according to the user's stated preflight
stance for Phases 1285-1288. It authorizes this sensitive preflight packet. It
does not authorize public P2P exposure, public fetch serving, non-loopback
sidecar/projection serving, a listener, a public host bind, wildcard bind, peer
discovery, public claimability, wallet withdrawal, wallet transfer, wallet
spend, ECU minting, ILC settlement, source publication, release artifacts,
release keys, release envelopes, Genesis Atlas mutation, v0.2 signing, CDL
mutation, CDL-088 opening, public RC, or public launch.

---

## 0. Discovery Discipline

Phase 1285 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| §0a Known-token audit | Verified the Phase 1285 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1285_g8_transport_principal_public_path_activation_preflight.md` and carried them into this packet, the walkthrough, STATUS, PLANNING_INDEX, Roadmap v1.1, and Capsule v5.51. |
| §0b Concept-discovery search | Searched TransportPrincipal, public path, public P2P, public fetch, rate limit, admission, ban, revocation, replay, credential, requester_id, client_ip, AgentID fallback, and hostile-network. |
| §0c Contradiction and non-claim search | Searched blocked, not authorized, not activated, fallback forbidden, no public, no P2P, no fetch, `PUBLIC_RC_EXCLUDE`, listener, bind, and hostile-network terms. |
| §0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source granted public-path activation authority. The newly carried tokens are `transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation`, `transport_principal_public_path_authority_not_activated_phase_1285`, `phase_1286_sidecar_public_projection_privacy_serving_preflight_next`, and `public_rc_remains_blocked_after_phase_1285`. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md`
- `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`
- `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Boundary Decision

Phase 1285 records a TransportPrincipal public-path activation preflight only:

```text
transport_principal_public_path_authority_not_activated_phase_1285
transport_principal_public_p2p_not_activated_phase_1285
public_fetch_serving_not_enabled_phase_1285
```

The Phase 1277 helper remains the only current local TransportPrincipal
public-path preflight substrate:

```text
ilc_core/network/d2d/transport_principal_public_path_preflight.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

No new runtime helper was introduced in Phase 1285. The existing helper already
binds the necessary preflight evidence without exposing a public path.

No public P2P exposure is authorized. No public fetch serving is authorized. No
non-loopback sidecar/projection serving, public listener, socket listener, HTTP
route, public host bind, wildcard bind, peer discovery, or public admission
service is authorized.

No public P2P exposure, public fetch serving, non-loopback sidecar/projection
serving, public listener, public endpoint, public host bind, wildcard bind, or
peer discovery is authorized.

No public P2P exposure, public fetch serving, non-loopback sidecar/projection serving, public listener, public endpoint, public host bind, wildcard bind, or peer discovery is authorized.

## 2. Lifecycle, Revocation, Replay, Admission, Ban, And Privacy Requirements

A future public-path activation still requires a closed lifecycle/revocation/
replay policy:

```text
transport_principal_lifecycle_revocation_replay_required_phase_1285
```

The Phase 1277 preflight proves the shape of the controls but not production
activation. A future activation phase must still define or ratify:

- credential issuer and accepted credential kinds for public serving;
- credential issue, expiry, rotation, and renewal rules;
- revocation-set authority, update cadence, and fail-closed propagation;
- replay-cache scope, retention, and cross-instance consistency;
- admission-key derivation and admission policy;
- ban-key derivation, ban propagation, and appeal/removal policy;
- rate-limit-key derivation and limiter state storage;
- privacy mode selection, AgentID non-default posture, and correlation limits;
- hostile-network validation against public inputs and timing/adversarial
  retry behavior.

The following fallbacks remain forbidden:

```text
requester_id_fallback_still_forbidden_phase_1285
```

Forbidden fallback identity sources remain:

- `requester_id`
- `json_body_requester_id`
- `client_ip`
- `AgentID`
- `agent_id`
- `harness_identity`
- OpenClaw/NemoClaw harness identity

The only acceptable public-path identity direction remains authenticated
TransportPrincipal material.

## 3. Current Permitted Surface

The current permitted surface is internal/offline preflight verification only.
It can cite:

- Phase 1267 pre-public TransportPrincipal context construction and validation.
- Phase 1277 internal public-path preflight helper.
- Phase 1278 sidecar public-path preflight dependency on TransportPrincipal.
- Phase 1284 claimability verifier/API boundary, which requires
  TransportPrincipal before any non-loopback claimability API.

Phase 1285 does not promote the Phase 1277 helper into a public RC package and
does not remove its `PUBLIC_RC_EXCLUDE` marker.

## 4. Activation Preconditions Carried Forward

Future public-path activation still requires:

| Gate | Current Phase 1285 disposition |
|------|--------------------------------|
| Explicit public-path activation authority | Not activated by Phase 1285. |
| Public P2P exposure | Not activated by Phase 1285. |
| Public fetch serving | Not enabled by Phase 1285. |
| Lifecycle/revocation/replay production policy | Required before activation. |
| Admission/ban/rate-limit state and persistence | Required before activation. |
| Fallback identity relaxation | Still forbidden. |
| Sidecar public projection authorization | Routed to Phase 1286 preflight. |
| Release publication/signing authority | Still blocked. |

The next locked phase is:

```text
phase_1286_sidecar_public_projection_privacy_serving_preflight_next
```

Phase 1286 is sensitive and authorized in the same human `GO Phase 1285-1288`
only as a preflight under the stated no-activation stance.

## 5. Non-Claims

Phase 1285 does not authorize or perform:

- public P2P exposure
- public fetch serving
- non-loopback sidecar/projection serving
- public sidecar/projection serving
- public listener
- socket listener
- HTTP route or public endpoint
- non-loopback bind, wildcard bind, or public host bind
- peer discovery
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

Public RC remains blocked after Phase 1285:

```text
public_rc_remains_blocked_after_phase_1285
```

Remaining blocker classes include sidecar public projection privacy/serving
preflight, release publication and v0.2 signing authorization, counsel/IP/
publication authorization, source publication/release artifact authorization,
final public claimability API/verifier authority, wallet
withdrawal/transfer/spend semantics, ECU minting, ILC settlement, and actual
TransportPrincipal public-path activation authority.

---

## 6. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md -> transport/identity
graph_delta=support_tests_added:tests/test_phase_1285_transport_principal_public_path_activation_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1285_transport_principal_public_path_activation_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
```
