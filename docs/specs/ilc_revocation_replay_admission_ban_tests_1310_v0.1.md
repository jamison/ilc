# ILC Revocation Replay Admission Ban Tests 1310 v0.1

**Phase:** 1310
**Date:** 2026-05-11
**Status:** Hostile-network negative paths hardened; public path remains blocked
**Window lock:** `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md`

```text
revocation_replay_admission_ban_tests_phase_1310.v0.1
transport_principal_revocation_replay_tests_hardened_phase_1310
admission_ban_rate_privacy_tests_hardened_phase_1310
hostile_network_public_path_still_blocked_phase_1310
phase_1311_local_graph_memory_projection_sidecar_next
public_rc_remains_blocked_after_phase_1310
```

## 1. Verdict

Phase 1310 executes after explicit human authorization:

```text
GO Phase 1310
```

The active Window 1303-1316 sequence lock controls this phase. Phase 1310 is a
hostile-network test and local hardening phase for the Phase 1309
TransportPrincipal admission sidecar. It does not activate a public
TransportPrincipal path, public P2P, public fetch serving, public sidecar or
projection serving, public credential issuer authority, public revocation
registry, public replay cache, public rate-limit state, admission service, ban
registry, public confidential messaging, wallet action, ECU mint, or ILC
settlement.

The Phase 1310 verdict is:

```text
revocation_replay_admission_ban_tests_phase_1310.v0.1
hostile_network_public_path_still_blocked_phase_1310
```

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Before implementation, the Phase 1310 required tokens existed only in the Phase 1310 prompt draft. This phase publishes them in code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, and the graph-native sidecar suite architecture. |
| Section 0b Concept-discovery search | Searched revocation, replay, admission, ban, rate-limit, rate_limit, privacy, hostile network, requester_id, client IP, client_ip, AgentID, agent_id, public P2P, public fetch, and Werner overlay across current TransportPrincipal code, specs, architecture, and focused tests. |
| Section 0c Contradiction and non-claim search | Searched not activated, not authorized, not enabled, local-only, no public, no listener, non-loopback, PUBLIC_RC_EXCLUDE, public path blocked, and public fetch serving. No source granted public activation, public serving, publication, signing, helper stripping, wallet economics, ECU minting, or ILC settlement authority. |
| Section 0d Source expansion and newly discovered tokens | Source expansion added the Phase 1310 code-hardening tokens `transport_principal_admission_forbidden_identity_context_key_phase_1310`, `transport_principal_admission_rate_limit_exceeded_phase_1310`, `transport_principal_admission_unexpected_keys_forbidden_phase_1310`, and `transport_principal_admission_payload_type_invalid_phase_1310`. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.53.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1310_g8_revocation_replay_admission_ban_tests.md`
- `docs/specs/ilc_transport_principal_admission_sidecar_lifecycle_1309_v0.1.md`
- `docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md`
- `docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md`
- `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
- `ilc_core/sidecars/transport_principal_admission.py`
- `ilc_core/sidecars/registry_manifest.py`
- `ilc_core/network/d2d/transport_principal_pre_public_path.py`
- `tests/test_phase_1309_transport_principal_admission_sidecar_lifecycle_hardening.py`

## 3. Code Hardening

Phase 1310 hardens `ilc_core/sidecars/transport_principal_admission.py` in four
local-only ways:

- Incoming TransportPrincipal context payloads are checked as bounded canonical
  JSON-compatible trees before the Phase 1267 validator is called.
- Incoming context payloads fail closed if they include fallback or private
  disclosure keys such as `requester_id`, `client_ip`, `AgentID`, `agent_id`,
  harness identity, OpenClaw identity, Tailscale identity, wallet fields, stake
  fields, economic position, or graph position.
- Local caller-supplied rate-limit counters are bounded, keyed only by
  authenticated `tp_rate:<sha256>` material, and rejected when the local counter
  is at or above the local ceiling.
- Admission decision validation now rejects unexpected extra keys and non-JSON
  value types before canonical export or hash acceptance.

The graph-native sidecar registry now records the TransportPrincipal admission
sidecar as:

```text
lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310
```

This is still local/package metadata only. It does not activate any public
registry, public replay cache, public rate-limit state, public ban registry, or
public admission service.

## 4. Negative-Path Matrix

| Attack or edge case | Phase 1310 expected behavior |
|---------------------|------------------------------|
| Credential fingerprint appears in local revocation input | Rejects before admission with `transport_principal_revoked`. |
| Principal id appears in local revocation input | Rejects before admission with `transport_principal_revoked`. |
| Replay key appears in local replay input | Rejects before admission with `transport_principal_replay_detected`. |
| Ban key appears in local ban input | Rejects with `transport_principal_admission_banned_phase_1309`. |
| Credential fingerprint appears in local ban input | Rejects with `transport_principal_admission_banned_phase_1309`. |
| Principal id appears in local ban input | Rejects with `transport_principal_admission_banned_phase_1309`. |
| Credential kind is outside the local accepted-kind set | Rejects with `transport_principal_admission_credential_kind_rejected_phase_1309`. |
| Local rate-limit count is below ceiling | Admits locally and records `rate_limit_state_source=caller_supplied_local_collection`. |
| Local rate-limit count is at or above ceiling | Rejects with `transport_principal_admission_rate_limit_exceeded_phase_1310`. |
| Context includes `requester_id`, `client_ip`, `AgentID`, harness identity, OpenClaw identity, Tailscale identity, wallet, stake, economic position, or graph position | Rejects with `transport_principal_admission_forbidden_identity_context_key_phase_1310`. |
| Decision includes an unexpected extra key | Rejects with `transport_principal_admission_unexpected_keys_forbidden_phase_1310`. |
| Decision includes a non-JSON value type | Rejects with `transport_principal_admission_payload_type_invalid_phase_1310`. |
| Public P2P, public fetch, public listener, peer discovery, or public state activation flags are enabled | Rejects through the existing Phase 1309 public-authority fail-closed path. |

## 5. Carry-Forward

Phase 1310 narrows the hostile-network local-test blocker but does not close the
public-path blocker. Public RC remains blocked by:

- public TransportPrincipal activation authority;
- public credential issuer authority;
- public revocation registry activation and signed registry propagation;
- public replay cache activation, retention, and cross-instance consistency;
- public admission policy activation;
- public ban registry activation and appeal/sunset policy;
- public rate-limit state activation and cross-instance abuse handling;
- public privacy policy activation for public transport paths;
- Rust public P2P substrate ADR/integration and hostile-network transport
  hardening;
- public sidecar/projection serving authority and projection privacy filters;
- public claimability API/verifier serving authority;
- `PUBLIC_RC_EXCLUDE` helper replacement and clean materialized public tree
  proof;
- source publication, package publication, release artifacts, release keys,
  release envelopes, Genesis Atlas mutation/signing, v0.2 signing,
  wallet withdrawal/transfer/spend, ECU minting, and ILC settlement.

The next phase remains sensitive:

```text
phase_1311_local_graph_memory_projection_sidecar_next
```

## 6. Non-Claims

Phase 1310 does not authorize:

- public RC claim;
- public launch claim;
- source allowlist export;
- source publication;
- public package publication;
- release artifact production;
- release-key generation;
- release envelope production;
- public claimability activation;
- public claimability API activation;
- public verifier service;
- public claim endpoint;
- public P2P;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback bind;
- wildcard bind;
- public host bind;
- listener;
- socket listener;
- HTTP route activation;
- peer discovery;
- TransportPrincipal public-path activation;
- public credential issuer authority;
- credential lifecycle policy activation for a public path;
- public revocation registry activation;
- public replay cache activation;
- public rate-limit state activation;
- admission policy activation for a public path;
- ban registry activation for a public path;
- privacy policy activation for a public path;
- helper promotion;
- marker removal;
- helper stripping;
- CDL mutation;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- public confidential messaging;
- public confidential coordination serving;
- wallet withdrawal;
- wallet transfer;
- wallet spend;
- ECU minting;
- ILC settlement.

## 7. Graph Delta

```text
graph_delta=load_bearing_code_changed:ilc_core/sidecars/transport_principal_admission.py -> graph-native-sidecars/transport-principal/hostile-network-negative-paths
graph_delta=load_bearing_code_changed:ilc_core/sidecars/registry_manifest.py -> graph-native-sidecars/registry/transport-principal
graph_delta=support_tests_added:tests/test_phase_1310_revocation_replay_admission_ban_tests.py -> validation
graph_delta=load_bearing_spec_added:docs/specs/ilc_revocation_replay_admission_ban_tests_1310_v0.1.md -> graph-native-sidecars/transport-principal/hostile-network-negative-paths
graph_delta=support_only:docs/phases/phase_1310_revocation_replay_admission_ban_tests_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.53.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md -> graph-native-sidecars
```

## 8. Verification

Phase-close verification:

```text
.venv/bin/python -m pytest tests/test_phase_1310_revocation_replay_admission_ban_tests.py tests/test_window_1303_1316_prompt_drafts.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1310_revocation_replay_admission_ban_tests_walkthrough.md tests/test_phase_1310_revocation_replay_admission_ban_tests.py
```
