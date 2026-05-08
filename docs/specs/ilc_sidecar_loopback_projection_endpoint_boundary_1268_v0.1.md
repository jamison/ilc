# ILC Sidecar Loopback Projection Endpoint Boundary - Phase 1268

**Status:** Phase 1268 complete; local-only boundary recorded
**Scope:** Sidecar loopback/subprocess/Unix-socket boundary and public-path block
**Date:** 2026-05-08

```text
sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1
sidecar_loopback_only_no_non_loopback_serving_phase_1268
sidecar_public_path_still_blocked_phase_1268
transport_principal_required_before_non_loopback_projection_phase_1268
```

## 1. Verdict

Phase 1268 records the sidecar endpoint decision:

```text
sidecar_loopback_endpoint_decision_phase_1268=record_boundary_no_new_listener
```

No HTTP server, socket listener, Unix-socket server, peer-discovery surface,
non-loopback bind, public sidecar/projection serving, or public P2P exposure is
implemented in this phase.

The allowed current surface remains local in-process import, harness-owned
subprocess/transport seams, or future explicitly authorized loopback-only or
Unix-socket-only prototypes. Binding beyond loopback remains blocked.

## 2. Discovery Discipline

Exact-token search was used as a schema/completion check for:

- `sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1`
- `sidecar_loopback_only_no_non_loopback_serving_phase_1268`
- `sidecar_public_path_still_blocked_phase_1268`
- `transport_principal_required_before_non_loopback_projection_phase_1268`

Concept discovery searched `sidecar`, `projection endpoint`, `loopback`, `Unix
socket`, `subprocess`, `HTTP`, `non-loopback`, `TransportPrincipal`, `bounds`,
`canonical JSON`, `NDJSON`, `privacy`, and `graph leakage`.

Contradiction and non-claim search checked `blocked`, `not authorized`, `no
public`, `local-only`, `test-only`, `devnet`, `non-loopback`, `unbounded`,
`privacy`, `must not`, and `public sidecar`.

Source expansion confirmed these controlling inputs:

- `docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md`
- `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
- `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`
- `ilc_core/graph/sidecar_query_runtime.py`
- `ilc_core/graph/agent_graph_projection_runtime.py`
- `ilc_core/rc/local_skill_preview.py`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/atlas_graph_discipline.py`

Graph Node context: this phase preserves existing Graph Node projection
semantics. It does not make Graph Node membership, serving evidence, or
fetch-incentive projection data publicly queryable.

## 3. Current Local Sidecar Surfaces

The existing local sidecar surfaces are sufficient for this phase:

- `ilc_core/graph/sidecar_query_runtime.py` provides in-process read-only query
  execution and canonical JSON/NDJSON exports.
- `ilc_core/rc/local_skill_preview.py` records `loopback_or_subprocess_only =
  True`, `public_p2p_enabled = False`, `public_claimability_enabled = False`,
  and `transport_principal_required_for_non_loopback = True`.
- `ilc_core/rc/package_profiles.py` records `PROFILE_LOCAL_SIDECAR_DAEMON` as
  loopback/local only with no public sidecar endpoint claim.

The Phase 1268 decision is to keep endpoint work at the boundary level because
a new listener is not needed to prove bounded export behavior and could create a
stale public-readiness signal.

## 4. Loopback-Only Allowed Shape

If a later explicit phase authorizes a loopback prototype, it must satisfy all
of these constraints:

- Bind only to loopback (`127.0.0.1` or equivalent local-only interface) or use
  a local Unix socket or harness-owned subprocess pipe.
- Fail closed on any non-loopback bind, wildcard bind, public host, or peer
  discovery configuration.
- Use bounded request and response sizes.
- Use mandatory network/socket timeouts if a socket exists.
- Route all projection output through existing canonical export helpers with
  `sort_keys=True`, `allow_nan=False`, finite Decimal handling, no float export,
  max-byte bounds, and max-result bounds.
- Expose no write, submit, gossip, fetch-serving, claimability, settlement, or
  protocol mutation operations.
- Carry explicit non-claims in manifest/status output.

## 5. Non-Loopback/Public Path Preconditions

Non-loopback sidecar/projection serving remains blocked until a later explicit
authorization closes all of these:

- CDL-087 ratification or equivalent explicit governance authorization for
  public fetch/projection-serving policy.
- Full TransportPrincipal public-path integration, not only the Phase 1267
  pre-public helper.
- Public-path rate limit, admission, ban, revocation, replay, and privacy
  controls keyed by authenticated TransportPrincipal.
- Graph leakage/privacy review for stable cross-epoch correlation, membership
  leakage, serving-peer leakage, and projection-query abuse.
- Rust/public-P2P substrate hardening and ATLAS-G public-RC graph gate closure.

Machine-readable boundary:

```text
transport_principal_required_before_non_loopback_projection_phase_1268
sidecar_public_path_still_blocked_phase_1268
```

## 6. Non-Claims

Phase 1268 does not authorize:

- Public sidecar/projection serving.
- Non-loopback sidecar/projection serving.
- Loopback HTTP endpoint implementation.
- Unix-socket endpoint implementation.
- Public P2P exposure.
- Public fetch serving.
- CDL-087 ratification.
- CDL register mutation.
- CDL-088 opening.
- Public RC claim.
- Public repository or package publication.
- Public claimability activation.
- Wallet withdrawal, transfer, or spend semantics.
- ECU mint authorization.
- Werner ECU creation.
- ILC settlement or withdrawal runtime activation.
- Release-key generation.
- Release envelope production.
- v0.2 signing.
- Signed Genesis v0.1 mutation.
- Genesis Atlas mutation/regeneration/signing.
- Immutable diagnostic mutation.
- Production `commit.epoch` emission authorization.

## 7. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md -> sidecar/public_path
graph_delta=support_tests_added:tests/test_phase_1268_sidecar_loopback_projection_endpoint_boundary.py -> validation
graph_delta=support_only:docs/phases/phase_1268_sidecar_loopback_projection_endpoint_boundary_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 8. Verification

Expected verification:

```bash
.venv/bin/python -m pytest tests/test_phase_1268_sidecar_loopback_projection_endpoint_boundary.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/specs ilc_core tests docs/phases/STATUS.md docs/phases/phase_1268_sidecar_loopback_projection_endpoint_boundary_walkthrough.md docs/PLANNING_INDEX.md
```
