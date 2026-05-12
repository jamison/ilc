# ILC TransportPrincipal Admission Sidecar Lifecycle 1309 v0.1

**Phase:** 1309
**Date:** 2026-05-11
**Status:** local lifecycle substrate implemented; public path activation remains blocked
**Window lock:** `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md`

```text
transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1
transport_principal_lifecycle_policy_local_substrate_phase_1309
transport_principal_public_path_not_activated_phase_1309
public_p2p_not_activated_phase_1309
phase_1310_revocation_replay_admission_ban_tests_next
public_rc_remains_blocked_after_phase_1309
```

## 1. Verdict

Phase 1309 executes after explicit human authorization:

```text
GO Phase 1309
```

The active 1303-1316 sequence lock controls this phase. Phase 1309 implements a
local graph-native TransportPrincipal admission sidecar lifecycle substrate at:

```text
ilc_core/sidecars/transport_principal_admission.py
```

This substrate consumes the Phase 1267 pre-public TransportPrincipal context
validator and emits a canonical local admission decision packet. It does not
import or promote the stale Phase 1277 `PUBLIC_RC_EXCLUDE` public-path helper.

Phase 1309 does not activate a public path:

```text
transport_principal_public_path_not_activated_phase_1309
public_p2p_not_activated_phase_1309
```

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Required Phase 1309 tokens existed only in the Phase 1309 prompt before execution and are now recorded in code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, and graph-native sidecar architecture. |
| Section 0b Concept-discovery search | Searched TransportPrincipal, credential issuer, lifecycle, revocation, replay cache, admission, ban registry, rate limit, privacy policy, requester_id, client IP, AgentID fallback, public P2P, and public fetch. |
| Section 0c Contradiction and non-claim search | Searched not activated, not authorized, not enabled, local-only, no public, no listener, non-loopback, `PUBLIC_RC_EXCLUDE`, stale helper, and `cdl087_not_ratified`. |
| Section 0d Source expansion | Direct-read the active planning index, Capsule v5.53, STATUS, Window 1303-1316 lock/guidance, Phase 1295/1296 transport preflights, transport/value forward plan, graph-native sidecar architecture, roadmap, CDL register, Phase 1267 identity helper, Phase 1277 stale public-path helper, registry manifest, and current tests. |

Newly carried-forward finding: the Phase 1277 public-path helper remains
`PUBLIC_RC_EXCLUDE` and still carries the stale pre-ratification CDL-087 false
gate. Phase 1309 therefore implements a replacement local sidecar substrate
rather than promoting that helper.

## 3. Implementation Boundary

The Phase 1309 sidecar:

- validates a Phase 1267 `pre_public_path` TransportPrincipal context;
- enforces current epoch validity with non-negative integer epoch inputs;
- accepts only bounded local collections for accepted credential kinds,
  revoked credentials, replay cache entries, and banned transport keys;
- rejects public activation flags including public P2P, public fetch serving,
  public sidecar serving, non-loopback projection, public listener, peer
  discovery, public credential issuer authority, public revocation registry,
  public replay cache, public rate-limit state, and release artifact authority;
- rejects fallback identity flags for requester id, JSON requester id, client
  IP, AgentID, harness identity, OpenClaw identity, and Tailscale identity;
- emits canonical JSON with `sort_keys=True`, `allow_nan=False`, and compact
  separators;
- rejects floats, tuple values, non-string mapping keys, cycles, excessive
  depth, and excessive node count before hashing or export.

The decision packet is:

```text
state=transport_principal_admission_lifecycle_local_only
decision=admitted_local_only_no_public_path_phase_1309
```

The sidecar is local-only. It creates no HTTP route, socket listener, server,
non-loopback bind, public credential issuer, public persistent registry,
network call, wallet action, ECU mint, or ILC settlement surface.

## 4. Registry Delta

Phase 1309 updates `ilc_core/sidecars/registry_manifest.py` so the
`transport_principal_admission` sidecar is no longer merely planned:

```text
authority_gate=phase_1309_local_lifecycle_substrate_public_path_blocked
implementation_status=lifecycle_substrate_recorded_phase_1309_tests_routed_phase_1310
```

The registry package-profile integrity block now embeds
`transport_principal_admission_sidecar_manifest()`. The sidecar still has
`public_serving_enabled=False` and remains private/local package metadata.

The stale helper disposition from Phase 1308 is unchanged:

```text
ilc_core/network/d2d/transport_principal_public_path_preflight.py -> replace_before_export
```

Phase 1309 does not remove that helper, remove its marker, or execute public
source materialization.

## 5. Guardrail Delta

`tools/check_sensitive_runtime_coding_taboos.py` now scans:

```text
ilc_core/sidecars/transport_principal_admission.py
```

The static guardrail covers canonical JSON arguments, assert usage, wall-clock
usage, predictable PRNG usage, and bounded untrusted payload contracts for the
new sidecar.

## 6. Carry-Forward

Phase 1309 narrows the local TransportPrincipal lifecycle substrate blocker. It
does not close public TransportPrincipal activation.

Public RC remains blocked after Phase 1309 by:

- Phase 1310 revocation, replay, admission, and ban negative-path tests;
- actual public TransportPrincipal public-path activation authority;
- public credential issuer authority;
- public revocation registry activation;
- public replay cache activation;
- public rate-limit state activation;
- privacy policy activation for public transport;
- Rust public P2P substrate ADR/integration gate before any Phase 1313-style
  activation candidate;
- source allowlist export execution and clean public tree materialization;
- public claimability API/verifier serving authority;
- sidecar public projection serving authority;
- release artifacts, release keys, release envelopes, Genesis/v0.2 signing,
  wallet withdrawal/transfer/spend semantics, ECU minting, and ILC settlement.

The next phase remains sensitive:

```text
phase_1310_revocation_replay_admission_ban_tests_next
```

Phase 1310 is sensitive and requires explicit `GO Phase 1310`.

## 7. Non-Claims

Phase 1309 does not authorize:

- public RC claim;
- public launch claim;
- public P2P;
- public fetch serving;
- public sidecar/projection serving;
- public credential issuer authority;
- credential lifecycle policy activation for a public path;
- public revocation registry activation;
- public replay cache activation;
- admission policy activation for a public path;
- ban registry activation for a public path;
- public rate-limit state activation;
- privacy policy activation for a public path;
- non-loopback bind;
- wildcard bind;
- public host bind;
- listener;
- socket listener;
- HTTP route activation;
- peer discovery;
- helper promotion;
- marker removal;
- helper stripping;
- source allowlist export;
- public repository publication;
- public package publication;
- release artifacts;
- release keys;
- release envelopes;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- CDL mutation;
- CDL-088 opening;
- public confidential messaging;
- public confidential coordination serving;
- wallet withdrawal;
- wallet transfer;
- wallet spend;
- ECU minting;
- ILC settlement.

## 8. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/sidecars/transport_principal_admission.py -> graph-native-sidecars/transport-principal/local-admission
graph_delta=load_bearing_code_changed:ilc_core/sidecars/registry_manifest.py -> graph-native-sidecars/registry/transport-principal
graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security
graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_admission_sidecar_lifecycle_1309_v0.1.md -> graph-native-sidecars/transport-principal/local-admission
graph_delta=support_tests_added:tests/test_phase_1309_transport_principal_admission_sidecar_lifecycle_hardening.py -> validation
graph_delta=support_only:docs/phases/phase_1309_transport_principal_admission_sidecar_lifecycle_hardening_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.53.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md -> graph-native-sidecars
graph_delta=support_only:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json -> package/public_rc/profile-audit
graph_delta=support_only:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md -> package/public_rc/profile-audit
```
