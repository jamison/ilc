# ILC TransportPrincipal Runtime Identity Pre-Public Path - Phase 1267

**Status:** Phase 1267 complete; pre-public runtime identity slice only
**Scope:** Local deterministic TransportPrincipal context construction and validation
**Date:** 2026-05-08

```text
transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1
transport_principal_runtime_not_public_p2p_activation_phase_1267
requester_id_rate_limit_fallback_still_forbidden_phase_1267
non_loopback_projection_still_blocked_phase_1267
```

## 1. Verdict

Phase 1267 adds a bounded pre-public TransportPrincipal runtime identity helper:

```text
ilc_core/network/d2d/transport_principal_pre_public_path.py
```

This is a safe identity/key-derivation slice for future public-path work. It is
not public P2P activation, not public fetch serving, not `non-loopback projection`
serving, not non-loopback sidecar/projection serving, and not CDL-087
ratification.

The helper builds and validates a `pre_public_path` context from already
authenticated transport credential material. It derives full SHA-256
TransportPrincipal fingerprints and separate rate-limit, admission, ban, and
replay keys. It refuses JSON/body `requester_id`, `client_ip`, AgentID, and
harness identity fallbacks.

## 2. Discovery Discipline

Phase 1267 used exact-token search only as a schema/completion check.

Exact-token audit:

- `transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1`
- `transport_principal_runtime_not_public_p2p_activation_phase_1267`
- `requester_id_rate_limit_fallback_still_forbidden_phase_1267`
- `non_loopback_projection_still_blocked_phase_1267`

Concept discovery searched broad and neighboring ideas: `TransportPrincipal`,
`requester_id`, `AgentID`, `client_ip`, `rate limit`, `admission`, `ban`,
`revocation`, `replay`, `credential`, `handshake`, `public P2P`, `sidecar`, and
`non-loopback`.

Contradiction search checked denial and drift terms: `not implemented`,
`devnet`, `test-only`, `local-only`, `blocked`, `not authorized`, `no public`,
`fallback`, `must not`, `privacy`, and `replay`.

Source expansion confirmed these controlling inputs:

- `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
- `docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md`
- `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md`
- `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`
- `ilc_core/network/d2d/persistent_fetch_rate_limiter_runtime.py`

Graph Node context: this phase changes transport identity support only. It does
not redefine Graph Node identity, Graph Node serving evidence, or fetch-incentive
projection semantics.

## 3. Runtime Contract

The Phase 1267 module is intentionally narrow:

- It accepts only authenticated transport credential kinds such as
  `transport_credential`, `signed_transport_handshake`, QUIC peer credentials,
  rustls peer certificate-chain hashes, or mTLS certificate fingerprints.
- It rejects fallback identity kinds: `requester_id`, `json_body_requester_id`,
  `client_ip`, `ip_address`, `agent_id`, `agentid`, and `harness_identity`.
- It also rejects disguised fallback material with prefixes such as
  `requester_id:`, `client_ip:`, `agent_id:`, and `harness_identity:`.
- It enforces bounded credential material and bounded handshake nonces.
- It validates integer epoch windows and rejects bools or negative values.
- It validates revocation and replay sets without wall-clock protocol time.
- It exports canonical JSON with `sort_keys=True`, `allow_nan=False`, and compact
  separators.

The derived public-path keys are separated by purpose:

- `principal_id`
- `rate_limit_key`
- `admission_key`
- `ban_key`
- `replay_key`

All are full SHA-256 digest bindings, not truncated display tags.

## 4. Carry-Forward from Phase 1253

Phase 1253 remains controlling policy for public-path identity:

```text
json_requester_id_rate_limit_fallback_forbidden_public_p2p_phase_1253
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

Phase 1267 partially discharges the runtime-identity part of that blocker by
adding a deterministic local helper, but it does not claim full public transport
activation. The existing Python HTTP fetch/gossip runtimes remain devnet/test or
local harness surfaces until a later authorized public-path integration replaces
their fallback identity behavior.

## 5. Non-Claims

Phase 1267 does not perform or authorize:

- Public P2P exposure.
- Public fetch serving.
- Public or non-loopback sidecar/projection serving.
- CDL-087 ratification.
- CDL register mutation.
- CDL-088 opening.
- Public RC claim.
- Public repository or package publication.
- Public claimability activation.
- Wallet withdrawal, transfer, or spend semantics.
- ECU mint authorization.
- ILC settlement or withdrawal runtime activation.
- Werner ECU creation.
- Release-key generation.
- Release envelope production.
- v0.2 signing.
- Signed Genesis v0.1 mutation.
- Genesis Atlas mutation/regeneration/signing.
- Immutable diagnostic mutation.
- Production `commit.epoch` emission authorization.

## 6. Boundary for Phase 1268

Phase 1268 may proceed only as a local loopback/subprocess/Unix-socket boundary
or prototype. Non-loopback sidecar/projection remains blocked by:

```text
non_loopback_projection_still_blocked_phase_1267
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/network/d2d/transport_principal_pre_public_path.py -> transport/identity
graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md -> transport/identity
graph_delta=support_tests_added:tests/test_phase_1267_transport_principal_runtime_identity_pre_public_path.py -> validation
graph_delta=support_only:docs/phases/phase_1267_transport_principal_runtime_identity_pre_public_path_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 8. Verification

Expected verification for Phase 1267:

```bash
.venv/bin/python -m pytest tests/test_phase_1267_transport_principal_runtime_identity_pre_public_path.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/specs ilc_core tests docs/phases/STATUS.md docs/phases/phase_1267_transport_principal_runtime_identity_pre_public_path_walkthrough.md docs/PLANNING_INDEX.md
```
