# ILC TransportPrincipal Public-Path ADR Runtime Preflight 1277 v0.1

**Date:** 2026-05-09
**Phase:** 1277
**Status:** public-path ADR/runtime preflight; no public activation
**Human authorization:** `GO Phase 1277`
**Window lock:** `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md`

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
requester_id_fallback_still_forbidden_phase_1277
non_loopback_projection_still_blocked_phase_1277
```

Additional Phase 1277 carry-forward tokens:

```text
public_fetch_serving_not_enabled_phase_1277
cdl087_not_ratified_by_phase_1277
sidecar_public_path_not_authorized_phase_1277
rust_public_p2p_hardening_still_open_phase_1277
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1277
genesis_atlas_v0_2_signing_deferred_until_atlas_g_tail_phase_1277
```

## 1. Decision Verdict

Phase 1277 records a fail-closed TransportPrincipal public-path preflight:

```text
transport_principal_public_path_preflight_verdict_phase_1277=pass_preflight_only_public_path_blocked
transport_principal_public_path_runtime_surface_phase_1277=internal_helper_only_public_rc_excluded
transport_principal_public_path_authority_phase_1277=authenticated_transport_principal_only
```

The phase moves the Phase 1267 pre-public helper closer to public-path ADR and
runtime integration by adding a separate preflight helper:

```text
ilc_core/network/d2d/transport_principal_public_path_preflight.py
```

The helper is explicitly marked internal-only:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

This phase does not expose a listener, does not enable public P2P, does not
enable public fetch serving, does not enable non-loopback sidecar/projection
serving, and does not authorize a public claimability API.

## 2. Canon And Discovery Audit

| Check | Phase 1277 result |
|-------|-------------------|
| Exact-token audit | Exact-token `rg` was used only as a schema/completion check for the four required Phase 1277 tokens and newly recorded carry-forward tokens. |
| Concept discovery | Concept discovery searched TransportPrincipal, principal, credential, lifecycle, revocation, replay, privacy, ban, rate limit, requester_id, client_ip, AgentID, public P2P, public fetch serving, sidecar, projection, and public path. |
| Contradiction search | Contradiction search covered blocked, not authorized, no public, non-loopback, local-only, fallback, forbidden, Rust M-5, hostile network, replay, revocation, and public path required. |
| Source expansion | Source expansion direct-read Phase 1253 identity policy, Phase 1267 helper/spec/tests, Phase 1261 and 1268 sidecar boundaries, Phase 1276 CDL-087 preflight, the current window lock, prompt package, planning index, and current runtime/test surfaces. |

Direct-read sources:

```text
docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md
docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md
ilc_core/network/d2d/transport_principal_pre_public_path.py
tests/test_phase_1267_transport_principal_runtime_identity_pre_public_path.py
docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md
docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md
docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md
docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md
docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md
```

## 3. Public-Path Identity Boundary

Public-path admission, rate limiting, bans, and replay controls must be keyed by
an authenticated TransportPrincipal. Phase 1277 preserves the Phase 1253 and
Phase 1267 rule that the following are not public-path authority:

```text
requester_id
json_body_requester_id
client_ip
AgentID
agent_id
harness_identity
OpenClaw/NemoClaw harness identity
```

The new helper validates a Phase 1267 TransportPrincipal context, carries the
credential fingerprint, principal id, admission key, rate-limit key, ban key,
replay key, issued epoch, current epoch, and expiry epoch, and then binds the
public-path preflight to a canonical `preflight_sha256`.

The only accepted rate-limit identity source is:

```text
authenticated_transport_principal
```

Fallback relaxation fails closed with:

```text
requester_id_fallback_still_forbidden_phase_1277
client_ip_rate_limit_key_still_devnet_only_phase_1277
agent_id_rate_limit_key_still_forbidden_phase_1277
harness_identity_rate_limit_key_still_forbidden_phase_1277
```

## 4. Lifecycle, Revocation, Replay, And Privacy Controls

| Control | Phase 1277 status |
|---------|-------------------|
| Credential lifecycle | The preflight carries `issued_epoch`, `current_epoch`, and `expires_epoch`; validation rejects current epochs outside the credential window. |
| Revocation | The preflight rejects credential fingerprint or principal id entries present in a revocation set. |
| Replay | The preflight rejects replay keys already present in the replay cache. |
| Privacy | The preflight allows only explicit pseudonymous/ephemeral privacy modes and keeps AgentID out of the public-path default. |
| Canonical binding | Preflight JSON uses deterministic key ordering, compact separators, `allow_nan=False`, full SHA-256 digests, and recursive float rejection. |
| Runtime surface | The helper has no socket, HTTP server, network fetch, wall-clock protocol time, or predictable PRNG dependency. |

Phase 1288 Fix1 hardens preflight payload traversal:

```text
phase_1288_fix1_runtime_deep_audit_hardening
untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1
public_path_preflight_key_shape_hardened_phase_1288_fix1
public_rc_remains_blocked_after_phase_1288_fix1
```

Validation now rejects finite floats, non-string JSON keys, recursive cycles,
excessive traversal depth, and excessive traversal node count before canonical
preflight hashing/export. This is internal preflight hardening only and does not
activate a public TransportPrincipal path.

Phase 1277 does not select the final public credential authority. Any future
phase that tries to choose that authority, enable a listener, relax fallback
rules, or expose public P2P/fetch/sidecar surfaces must stop for human review.

## 5. Public Exposure Boundary

The following flags must remain false in Phase 1277:

```text
public_p2p_enabled
public_fetch_serving_enabled
non_loopback_projection_enabled
sidecar_public_path_authorized
cdl087_ratified
rust_public_p2p_hardening_complete
release_artifact_authorized
```

Violation tokens:

```text
transport_principal_public_p2p_not_activated_phase_1277
public_fetch_serving_not_enabled_phase_1277
non_loopback_projection_still_blocked_phase_1277
sidecar_public_path_not_authorized_phase_1277
cdl087_not_ratified_by_phase_1277
rust_public_p2p_hardening_still_open_phase_1277
release_artifact_not_authorized_phase_1277
```

The Phase 1277 helper is a preflight record generator/validator only. It is not
a public API, not a public-path listener, not public fetch serving, and not
non-loopback projection serving.

## 6. User-Decision Carry-Forward

The human reviewer aligned on this sequencing during Phase 1277:

```text
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1277
genesis_atlas_v0_2_signing_deferred_until_atlas_g_tail_phase_1277
```

Practical meaning:

- If Phase 1277 and Phase 1278 both pass, plan a CDL-087 ratification Fix phase
  inside the current window.
- That future Fix phase still needs explicit human authorization for CDL-087
  ratification and CDL register mutation, plus a fresh six-condition proof.
- Genesis Atlas v0.2 signing is deferred until the end of the planned Atlas-G
  phases, not triggered by Phase 1277.

## 7. Phase 1278 Handoff

Phase 1278 remains the next locked sensitive phase:

```text
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
transport_principal_and_cdl087_required_before_public_projection_phase_1278
no_new_public_listener_phase_1278
```

Phase 1277 gives Phase 1278 a stricter TransportPrincipal preflight artifact to
cite, but it does not remove CDL-087, public sidecar/projection, or Rust M-5
hardening blockers.

## 8. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/network/d2d/transport_principal_public_path_preflight.py -> transport/identity
graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md -> transport/identity
graph_delta=support_tests_added:tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py -> validation
graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/phases/phase_1277_transport_principal_public_path_adr_runtime_integration_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 9. Verification

Required verification:

```bash
.venv/bin/python -m pytest tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py
.venv/bin/python -m pytest tests/test_window_1273_1280_prompt_drafts.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1277_transport_principal_public_path_adr_runtime_integration_walkthrough.md tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py
```

Expected CDL register diff: empty.

## 10. Non-Claims

Phase 1277 does not authorize:

- public P2P exposure;
- public fetch serving;
- non-loopback sidecar/projection serving;
- public sidecar/projection serving;
- a new public listener;
- public claimability activation;
- public claimability API activation;
- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- CDL mutation;
- CDL-087 ratification;
- CDL-088 opening;
- wallet withdrawal, transfer, or spend semantics;
- ECU mint authorization;
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- public release artifact production;
- Genesis Atlas v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.
