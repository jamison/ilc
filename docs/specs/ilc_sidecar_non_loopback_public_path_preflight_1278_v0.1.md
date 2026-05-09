# ILC Sidecar Non-Loopback Public-Path Preflight 1278 v0.1

**Date:** 2026-05-09
**Phase:** 1278
**Status:** authorization preflight; fail-closed; no public serving
**Human authorization:** `GO Phase 1278`
**Window lock:** `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md`

```text
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
transport_principal_and_cdl087_required_before_public_projection_phase_1278
no_new_public_listener_phase_1278
```

Additional carry-forward tokens:

```text
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
sidecar_projection_privacy_review_required_phase_1278
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1278
```

## 1. Decision Verdict

Phase 1278 records a fail-closed sidecar public-path authorization preflight:

```text
sidecar_public_path_preflight_verdict_phase_1278=blocked_no_public_serving
sidecar_public_path_runtime_surface_phase_1278=internal_helper_only_public_rc_excluded
sidecar_public_projection_gate_phase_1278=requires_transport_principal_and_cdl087
```

The phase adds a machine-checkable helper:

```text
ilc_core/graph/sidecar_public_path_preflight.py
```

The helper is explicitly marked internal-only:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

No public sidecar/projection serving, non-loopback bind, new listener, peer
discovery surface, public fetch serving, public P2P exposure, public
claimability API, CDL mutation, or CDL-087 ratification is authorized.

## 2. Canon And Discovery Audit

| Check | Phase 1278 result |
|-------|-------------------|
| Exact-token audit | Exact-token `rg` was used only as a schema/completion check for the required Phase 1278 tokens and carry-forward tokens. |
| Concept discovery | Concept discovery searched sidecar, projection endpoint, loopback, non-loopback, public serving, listener, bind, Unix socket, HTTP, TransportPrincipal, CDL-087, rate limit, privacy, public path, and sidecar query runtime. |
| Contradiction search | Contradiction search covered blocked, not authorized, no public, local-only, loopback only, no listener, non-loopback, public path, replay, revocation, privacy, abuse, and fail closed. |
| Source expansion | Source expansion direct-read Phase 1261 sidecar public-path boundary, Phase 1268 loopback boundary, Phase 1267 TransportPrincipal helper/spec, Phase 1277 TransportPrincipal public-path preflight, current sidecar runtime, local preview manifest, package profiles, ATLAS-G graph discipline, planning index, status, roadmap, and current window lock. |

Direct-read sources:

```text
docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md
docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md
docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md
docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md
ilc_core/network/d2d/transport_principal_public_path_preflight.py
ilc_core/graph/sidecar_query_runtime.py
ilc_core/rc/local_skill_preview.py
ilc_core/rc/package_profiles.py
ilc_core/rc/atlas_graph_discipline.py
```

## 3. Public-Serving Gate Matrix

| Gate | Phase 1278 disposition |
|------|------------------------|
| CDL-087 ratification | Not satisfied. CDL-087 remains open/prelocked/not ratified; no CDL register mutation occurs in Phase 1278. |
| TransportPrincipal public-path authority | Not satisfied for activation. Phase 1277 provides an internal preflight helper, not public-path serving authorization. |
| Sidecar public serving | Disabled and rejected by `sidecar_public_serving_not_enabled_phase_1278`. |
| Public projection endpoint | Disabled and rejected by `public_projection_endpoint_not_enabled_phase_1278`. |
| Non-loopback bind | Disabled and rejected by `non_loopback_bind_not_enabled_phase_1278`. |
| New listener or peer discovery | Disabled and rejected by `no_new_public_listener_phase_1278`. |
| Privacy review | Still required before any public projection because graph-membership leakage, serving-peer leakage, query abuse, and cross-epoch correlation remain public-path concerns. |
| Rust/non-loopback substrate | Still a blocker for any public serving claim. |

The combined public projection gate remains:

```text
transport_principal_and_cdl087_required_before_public_projection_phase_1278
```

## 4. Current Local Sidecar Boundary

The current sidecar runtime remains local/read-only:

```text
ilc_core/graph/sidecar_query_runtime.py
ilc_core/rc/local_skill_preview.py
ilc_core/rc/package_profiles.py
```

Current allowed local surfaces:

- in-process imports;
- harness-owned subprocess or transport/storage seams;
- no current HTTP endpoint;
- no current Unix-socket endpoint;
- no current loopback listener;
- future loopback-only or Unix-socket-only prototypes only after explicit
  authorization.

Current export controls remain:

- canonical JSON with deterministic key ordering and `allow_nan=False`;
- bounded response bytes;
- bounded result count;
- float export rejection;
- finite Decimal conversion;
- read-only query semantics.

## 5. Runtime Helper Boundary

The Phase 1278 helper validates a Phase 1277 TransportPrincipal public-path
preflight and produces a sidecar preflight bound to:

- sidecar query runtime version;
- TransportPrincipal preflight ref;
- TransportPrincipal principal id;
- TransportPrincipal rate-limit key;
- TransportPrincipal admission key;
- TransportPrincipal ban key;
- TransportPrincipal replay key;
- public-serving false flags;
- listener/bind false flags;
- explicit requirements before public projection;
- canonical `sidecar_preflight_sha256`.

It rejects:

```text
sidecar_public_serving_enabled
public_projection_endpoint_enabled
non_loopback_bind_enabled
new_public_listener_enabled
peer_discovery_enabled
public_fetch_serving_enabled
public_p2p_enabled
cdl087_ratified
transport_principal_public_path_authorized
release_artifact_authorized
```

The helper uses canonical JSON with `sort_keys=True`, compact separators,
`allow_nan=False`, full SHA-256 hashes, and recursive float rejection.

Phase 1288 Fix1 hardens sidecar preflight payload traversal:

```text
phase_1288_fix1_runtime_deep_audit_hardening
untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1
public_path_preflight_key_shape_hardened_phase_1288_fix1
public_rc_remains_blocked_after_phase_1288_fix1
```

Validation now rejects finite floats, non-string JSON keys, recursive cycles,
excessive traversal depth, and excessive traversal node count before canonical
preflight hashing/export. This is internal preflight hardening only and does not
activate public sidecar/projection serving.

## 6. Post-1278 Fix-Phase Planning

Phase 1277 and Phase 1278 now both pass as preflight gates without public
activation. The agreed carry-forward is:

```text
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1278
```

The practical next-step interpretation is:

- A CDL-087 ratification Fix phase is planned next inside the current window if
  the human reviewer explicitly authorizes it.
- That Fix phase must explicitly authorize CDL-087 ratification and CDL register
  mutation, then reprove all six CDL-087 conditions against current canon.
- If that explicit authorization is not given, the locked Phase 1279
  release-manifest/source-allowlist prepublication inventory remains the next
  non-sensitive sequence-lock phase.

Genesis Atlas v0.2 signing remains deferred until the Atlas-G tail and is not
authorized by Phase 1278.

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/graph/sidecar_public_path_preflight.py -> sidecar/public_path
graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md -> sidecar/public_path
graph_delta=support_tests_added:tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py -> validation
graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/phases/phase_1278_sidecar_non_loopback_public_path_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 8. Verification

Required verification:

```bash
.venv/bin/python -m pytest tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py
.venv/bin/python -m pytest tests/test_window_1273_1280_prompt_drafts.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1278_sidecar_non_loopback_public_path_preflight_walkthrough.md tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py
```

Expected CDL register diff: empty.

## 9. Non-Claims

Phase 1278 does not authorize:

- public sidecar/projection serving;
- public projection endpoint serving;
- non-loopback sidecar/projection serving;
- non-loopback bind;
- wildcard bind;
- public host bind;
- new listener;
- peer discovery;
- loopback HTTP endpoint implementation;
- Unix-socket endpoint implementation;
- public P2P exposure;
- public fetch serving;
- public claimability API activation;
- public claimability activation;
- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- public release artifact production;
- release-key generation;
- release envelope production;
- CDL mutation;
- CDL-087 ratification;
- CDL-088 opening;
- wallet withdrawal, transfer, or spend semantics;
- ECU mint authorization;
- ILC settlement or withdrawal runtime activation;
- Genesis Atlas v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.
