# ILC Sidecar Projection Endpoint Boundary 1261 v0.1

**Date:** 2026-05-08
**Phase:** 1261
**Status:** non-public endpoint boundary recorded
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
sidecar_projection_endpoint_boundary_phase_1261.v0.1
sidecar_projection_endpoint_not_publicly_exposed_phase_1261
sidecar_public_path_requires_cdl087_and_transport_principal_phase_1261
transport_principal_policy_gate_rechecked_phase_1261
```

## 1. Scope and Verdict

Phase 1261 records the sidecar projection endpoint boundary after the Phase
1258-1260 CDL-087 evidence passes and the Phase 1253 TransportPrincipal spec.

Verdict:

```text
sidecar_projection_endpoint_authorization_verdict_phase_1261=blocked_public_path
```

No sidecar projection endpoint is publicly exposed in this phase.
No HTTP server, socket listener, non-loopback bind, peer-discovery surface,
public P2P surface, or runtime TransportPrincipal implementation is added.

## 2. CDL-087 Gate Recheck

The Phase 1258-1260 evidence chain records local evidence for CDL-087
Conditions 2, 3, 4, and 5:

```text
cdl_087_serving_peer_evidence_slice_phase_1259.v0.1
production_candidate_tier_classification_runtime_evidence_recorded_phase_1259
bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259
cdl_087_observability_collection_window_phase_1260.v0.1
cdl_077_rate_limiter_final_regression_recorded_phase_1260
```

Phase 1260 also records:

```text
cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review
no_cdl_087_ratification_phase_1260
```

That is readiness for a later sensitive review, not ratification. The CDL
register still records CDL-087 as `open`, and no CDL mutation has occurred in
this window.
Therefore the CDL-087 prerequisite for public sidecar/projection serving is not
satisfied.
For machine readback: the CDL-087 prerequisite for public sidecar/projection serving is not satisfied.
The CDL-087 prerequisite for public sidecar/projection serving is not satisfied.

## 3. TransportPrincipal Gate Recheck

Phase 1253 recorded TransportPrincipal as a required public-path identity
contract and ADR input, not as runtime implementation:

```text
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
json_requester_id_rate_limit_fallback_forbidden_public_p2p
transport_principal_cdl_required_before_runtime_implementation
transport_principal_lifecycle_and_revocation_spec_required
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

The TransportPrincipal public-path gate remains open because the repo does not
yet have:

- TransportPrincipal runtime implementation;
- lifecycle, issuance, rotation, revocation, local-ban, and replay-prevention
  rules accepted by ADR/CDL authority;
- public-path rate limiting keyed by authenticated TransportPrincipal;
- Rust public-P2P / non-loopback substrate hardening for public serving claims;
- privacy review for projection-serving leakage.

JSON/body `requester_id`, permanent AgentID, BLS economic keys, and OpenClaw or
NemoClaw harness identity must not become the public sidecar rate-limit,
admission, ban, revocation, or reputation key.
OpenClaw or NemoClaw harness identity must not become the public sidecar
rate-limit, admission, ban, revocation, or reputation key.
`client_ip` remains a devnet or local abuse-damping fallback only.

## 4. Current Sidecar Runtime Boundary

Current sidecar and graph projection surfaces remain local, read-only, and
bounded:

```text
ilc_core/graph/agent_graph_projection_runtime.py
ilc_core/graph/sidecar_query_runtime.py
ilc_core/rc/package_profiles.py
```

The runtime boundary confirmed in this phase:

- `agent_graph_projection_runtime.py` builds bounded projections and canonical
  JSON/NDJSON exports.
- `sidecar_query_runtime.py` performs in-process read-only projection queries,
  rejects float payload values, enforces export byte/result bounds, and exports
  canonical JSON with `sort_keys=True` and `allow_nan=False`.
- `PROFILE_LOCAL_SIDECAR_DAEMON` is loopback/local only and records no public
  sidecar endpoint claim.

This phase does not add a loopback HTTP prototype. Future loopback-only
endpoint prototyping may be considered only if a later phase explicitly opens
that scope and keeps binding to loopback, Unix socket, or subprocess-only
harness transport.

## 5. Public Path Preconditions

Any future non-loopback sidecar/projection endpoint must satisfy all of these
preconditions before implementation or exposure:

1. CDL-087 is ratified or a later explicit governance artifact authorizes the
   relevant public fetch/projection-serving policy.
2. TransportPrincipal runtime exists with issuance, rotation, revocation,
   replay prevention, local-ban persistence, and privacy-preserving admission
   semantics.
3. Public-path rate limits, admission controls, bans, and abuse circuit
   breakers are keyed by authenticated TransportPrincipal.
4. Public-path exports enforce byte limits, result-count limits, finite
   numeric constraints, canonical JSON, and no unbounded remote accumulation.
5. Projection privacy is reviewed for graph-membership leakage, serving-peer
   leakage, and stable cross-epoch correlation.
6. A future sequence lock explicitly authorizes the endpoint scope and records
   whether the phase is sensitive.

## 6. Non-Authorization Boundary

Phase 1261 does not authorize:

- public sidecar/projection serving;
- public fetch serving;
- public P2P exposure;
- non-loopback endpoint exposure;
- loopback HTTP endpoint implementation;
- TransportPrincipal runtime implementation;
- CDL register mutation;
- CDL-087 ratification;
- CDL-088 opening;
- public RC claim;
- public repository publication;
- public claimability activation;
- ECU minting;
- ILC settlement activation;
- release-key generation;
- release envelope production;
- v0.2 signing.

## 7. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md -> transport/public_rc
graph_delta=support_tests_added:tests/test_phase_1261_sidecar_projection_endpoint_boundary.py -> validation
graph_delta=support_only:docs/phases/phase_1261_sidecar_projection_endpoint_boundary_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 8. Next Phase

Phase 1262 remains the next locked non-sensitive phase:

```text
werner_flow_governor_overlay_validation_phase_1262.v0.1
```
