# ILC TransportPrincipal Lifecycle Revocation Replay Preflight 1295 v0.1

**Phase:** 1295
**Date:** 2026-05-10
**Status:** lifecycle/revocation/replay preflight recorded; public path activation remains blocked
**Window lock:** `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

```text
transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295
transport_principal_public_path_helper_not_promoted_phase_1295
transport_principal_lifecycle_policy_not_activated_phase_1295
transport_principal_revocation_registry_not_activated_phase_1295
transport_principal_replay_cache_not_activated_phase_1295
requester_id_fallback_still_forbidden_phase_1295
public_p2p_not_activated_phase_1295
public_fetch_serving_not_enabled_phase_1295
public_rc_remains_blocked_after_phase_1295
phase_1296_hostile_network_admission_ban_rate_privacy_plan_next
```

## 1. Verdict

Phase 1295 executes after explicit human authorization:

```text
GO Phase 1295
```

The active 1289-1302 sequence lock controls this phase. Phase 1295 is a
TransportPrincipal lifecycle, revocation, and replay preflight only. It does not
activate a public path.

```text
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
```

The current Phase 1277 helper remains useful as an internal fail-closed
preflight substrate, but it is not promotable as-is. The material finding is
that CDL-087 is now ratified by Phase 1278 Fix1 while the Phase 1277 helper
still carries a pre-ratification false gate:

```text
cdl087_not_ratified_by_phase_1277
authorization_flags.cdl087_ratified == False
```

That mismatch is safe while the helper remains `PUBLIC_RC_EXCLUDE`, but it means
the helper cannot be promoted directly into a public RC/public-path runtime. A
future public-path contract must replace or supersede that old gate with a
post-ratification authority contract before public activation.

Phase 1295 does not modify runtime code. It records the blocker and keeps the
helper internal:

```text
transport_principal_public_path_helper_not_promoted_phase_1295
```

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Verified the active Phase 1295 authority against `docs/PLANNING_INDEX.md`, Capsule v5.52, STATUS, the 1289-1302 lock/guidance, Phase 1267 TransportPrincipal runtime identity, Phase 1277 public-path helper, Phase 1285 activation preflight, Phase 1293 helper register, Phase 1294 allowlist rehearsal, and the CDL register. |
| Section 0b Concept-discovery search | Searched TransportPrincipal, principal, credential, lifecycle, issue, expiry, rotation, renewal, revocation, replay, replay cache, admission key, ban key, rate-limit key, requester_id, client_ip, AgentID, harness identity, public P2P, public fetch, public path, CDL-087, CDL-088, and `PUBLIC_RC_EXCLUDE`. |
| Section 0c Contradiction and non-claim search | Searched blocked, not authorized, not activated, not enabled, not executed, no public, no listener, no bind, no public P2P, no public fetch, no helper promotion, no marker removal, no wallet spend, no ECU minting, no ILC settlement, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Source expansion found the post-Phase 1278 Fix1 CDL-087 ratification state and the older Phase 1277 false `cdl087_ratified` helper gate. This is carried as an explicit Phase 1295 blocker token and future replacement requirement. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md`
- `docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md`
- `docs/specs/ilc_claimability_package_allowlist_rehearsal_1294_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_core/network/d2d/transport_principal_pre_public_path.py`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
- `tests/test_phase_1267_transport_principal_runtime_identity_pre_public_path.py`
- `tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py`

## 3. Current Runtime Readback

The Phase 1267 helper currently provides deterministic pre-public identity
material:

| Control | Existing behavior | Phase 1295 disposition |
|---------|-------------------|------------------------|
| Credential kind | Accepts bounded authenticated transport-credential kinds and rejects requester/client/AgentID fallback kinds. | Keep as internal substrate. Future public issuer authority still required. |
| Epoch lifecycle | Requires non-negative integer `issued_epoch`, `current_epoch`, and `expires_epoch`; rejects current epochs outside the credential window. | Local check is useful, but production issue/rotation/renewal policy is not activated. |
| Revocation | Rejects credential fingerprint or principal id present in caller-supplied revocation input. | No authoritative revocation registry, update cadence, propagation, or fail-closed replication is activated. |
| Replay | Rejects replay keys present in caller-supplied replay input. | No persistent replay cache, retention policy, cross-instance consistency, or eviction policy is activated. |
| Fallback identity | Refuses `requester_id`, `json_body_requester_id`, `client_ip`, `AgentID`, `agent_id`, and harness identity fallback material. | Requirement remains locked. |
| Canonical export | Uses deterministic JSON with `sort_keys=True`, `allow_nan=False`, and compact separators. | Keep as internal deterministic substrate. |

The Phase 1277 public-path helper adds a public-path preflight envelope:

| Control | Existing behavior | Phase 1295 disposition |
|---------|-------------------|------------------------|
| Helper marker | File starts with `PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface`. | Marker remains. No promotion or marker removal. |
| Public exposure flags | Requires `public_p2p_enabled=False`, `public_fetch_serving_enabled=False`, `non_loopback_projection_enabled=False`, `sidecar_public_path_authorized=False`, and `release_artifact_authorized=False`. | No public P2P, public fetch, sidecar serving, listener, bind, or public endpoint is activated. |
| CDL-087 gate | Requires `cdl087_ratified=False` with the old `cdl087_not_ratified_by_phase_1277` token. | Stale after Phase 1278 Fix1 ratification; direct promotion is blocked. |
| Traversal hardening | Phase 1288 Fix1 hardening rejects finite floats, non-string JSON keys, recursive cycles, excessive depth, and excessive node count before canonical hashing/export. | Keep internal safety property. |
| Network surface | No socket, HTTP server, outbound network, wall-clock protocol time, or predictable PRNG dependency in the helper. | No public path activation. |

## 4. Public-Path Preconditions

Future TransportPrincipal public-path activation still requires all of the
following to be defined, reviewed, and explicitly authorized:

| Gate | Phase 1295 disposition |
|------|------------------------|
| Public credential issuer authority | Not selected or activated. |
| Accepted public credential kinds | Not ratified for public serving. |
| Credential lifecycle | Issue, expiry, renewal, rotation, replacement, and recovery policy not activated. |
| Revocation registry | Registry authority, signed update format, update cadence, propagation, replication, and fail-closed behavior not activated. |
| Replay cache | Persistence, retention, cross-instance consistency, eviction, replay window, and abuse handling not activated. |
| Admission state | Routed to Phase 1296 hostile-network admission/ban/rate/privacy planning. |
| Ban state | Routed to Phase 1296 hostile-network admission/ban/rate/privacy planning. |
| Rate-limit state | Routed to Phase 1296 hostile-network admission/ban/rate/privacy planning. |
| Privacy mode | Public correlation, rotation, and AgentID disclosure rules not activated. |
| CDL-087 post-ratification contract | Required before replacing the Phase 1277 pre-ratification gate. |
| Helper export eligibility | Blocked by `PUBLIC_RC_EXCLUDE` and Phase 1293 keep-internal register. |

## 5. Future Public-Path Contract Requirements

A future replacement or promotion candidate must prove at least:

- CDL-087 post-ratification authority is represented without the old
  `cdl087_not_ratified_by_phase_1277` false gate.
- Public credential issuer and accepted credential kinds are explicit.
- Credential lifecycle events use epoch/sequence protocol time, not wall-clock
  time.
- Revocation input is authenticated, bounded, replay-safe, and fail-closed
  across instances.
- Replay cache semantics are persistent or otherwise proven safe for the chosen
  deployment topology.
- Admission, ban, and rate-limit state are keyed only by authenticated
  TransportPrincipal material.
- `requester_id`, JSON body identity, client IP, AgentID, agent id, and harness
  identity fallback remain forbidden.
- Canonical machine-verifiable JSON uses deterministic serialization:

```text
json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))
```

## 6. Carry-Forward

Public RC remains blocked after Phase 1295 by:

- final public claimability verifier/API authority and public endpoint
  authorization;
- public-safe helper replacement or later explicit helper promotion
  prerequisites;
- public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry;
- TransportPrincipal public-path activation authority, including the
  post-ratification CDL-087 helper replacement, lifecycle policy, revocation
  registry, replay cache, admission, ban, rate-limit, and privacy controls;
- actual public sidecar/projection serving authority, including public-safe
  field schema, filtering, bind/listener policy, and peer-discovery policy;
- counsel/license/CLA/trademark/IP/publication clearance;
- source allowlist export execution and public source/package publication;
- release artifact production, release-key generation, release envelope
  production, and release manifest instance production;
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization;
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy;
- wallet withdrawal/transfer/spend semantics, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.

The next locked phase remains sensitive:

```text
phase_1296_hostile_network_admission_ban_rate_privacy_plan_next
```

## 7. Non-Claims

```text
transport_principal_lifecycle_policy_not_activated_phase_1295
transport_principal_revocation_registry_not_activated_phase_1295
transport_principal_replay_cache_not_activated_phase_1295
requester_id_fallback_still_forbidden_phase_1295
public_p2p_not_activated_phase_1295
public_fetch_serving_not_enabled_phase_1295
public_rc_remains_blocked_after_phase_1295
```

Phase 1295 does not authorize:

- TransportPrincipal public-path activation;
- public credential issuer authority;
- credential lifecycle policy activation;
- public revocation registry activation;
- public replay cache activation;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback bind, wildcard bind, public host bind, listener, or peer discovery;
- helper promotion;
- `PUBLIC_RC_EXCLUDE` marker removal;
- materialized export manifest production;
- source allowlist export execution;
- public repository publication;
- public package publication;
- public release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
- public claimability runtime activation;
- public claimability API activation;
- public verifier service;
- public claim endpoint;
- wallet withdrawal, wallet transfer, or wallet spend;
- wallet signing authority or wallet ledger-write authority;
- ECU minting;
- ILC settlement or withdrawal runtime activation;
- CDL mutation;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- IP filing or paper publication.

## 8. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md -> transport/identity
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1295_g8_release_allowlist_artifact_genesis_readiness_preflight.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1295_transport_principal_lifecycle_revocation_replay_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1295_transport_principal_lifecycle_revocation_replay_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
