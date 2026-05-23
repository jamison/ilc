# ILC CDL-094 TransportPrincipal Prelock 1435 v0.1

**Date:** 2026-05-23
**Phase:** 1435
**Status:** prelock scope constants locked for ratification; no runtime activation
**Human authorization:** `GO Phase 1435`
**Opening anchor:** Phase 1434 C1 `b5152c37`

```text
cdl_094_prelock_committed_phase_1435
cdl_094_scope_constants_locked_phase_1435
transport_principal_cdl_ratified_phase_1435
cdl_094_transport_principal_ratified_phase_1435
gap_10_cdl_governance_closed_phase_1435
cdl_094_ratified_governance_only_not_activated_phase_1435
```

## 1. Verdict

CDL-094 prelocks the TransportPrincipal public-path governance scope. The
prelock closes no runtime path by itself. It locks the constitutional rule that
all future non-loopback public fetch, verifier, sidecar/projection, P2P, or
public confidential coordination surfaces require an authenticated
TransportPrincipal before they can bind or serve.

```text
TRANSPORT_PRINCIPAL_CDL_RATIFIED=true
policy_boundary_constant=TRANSPORT_PRINCIPAL_CDL_RATIFIED
runtime_activation_status=not_authorized
public_fetch_serving_status=not_enabled
public_sidecar_projection_status=not_enabled
public_p2p_status=not_enabled
public_confidential_coordination_status=not_enabled
confidential_contact_status=jamison_confidential_sidecar_planned_not_live
```

## 2. Locked Scope Constants

| Constant | Locked value | Meaning |
|---|---|---|
| `TRANSPORT_PRINCIPAL_CDL_RATIFIED` | `true` | Governance authority exists for TransportPrincipal policy after ratification. |
| `AUTHENTICATED_PRINCIPAL_REQUIRED_FOR_NON_LOOPBACK` | `true` | A non-loopback public path must bind to authenticated transport material. |
| `TRANSPORT_PRINCIPAL_REQUIRED_FOR_NON_LOOPBACK` | `true` | The authenticated material must instantiate TransportPrincipal policy. |
| `IP_ONLY_AUTHENTICATION_ALLOWED` | `false` | IP address alone is not an authenticated principal. |
| `JSON_REQUESTER_ID_AUTHENTICATION_ALLOWED` | `false` | JSON/body identity is not an authenticated transport principal. |
| `REQUESTER_ID_FALLBACK_ALLOWED` | `false` | Public-path fallback to requester_id remains forbidden. |
| `RAW_AGENT_ID_DEFAULT_RATE_LIMIT_KEY_ALLOWED` | `false` | Permanent AgentID is not the default public transport rate-limit key. |
| `CLIENT_IP_PRIMARY_RATE_LIMIT_KEY_ALLOWED` | `false` | Client IP may not be the primary hostile-network limiter key. |
| `BAN_REVOCATION_INTERFACE_REQUIRED` | `true` | Runtime activation must expose ban, revocation, replay, and admission checks. |

## 3. Rate-Limit Policy

The ratified policy identifier is:

```text
rate_limit_policy=per_agent_id_bound_transport_principal_epoch_window
rate_limit_identity_source=authenticated_transport_principal
rate_limit_window_basis=epoch_sequence
rate_limit_numeric_limits_status=deferred_to_phase_1436_runtime_config
```

The policy is intentionally keyed by the authenticated TransportPrincipal and
its agent binding. It is not keyed by raw AgentID, requester_id, client IP, host
name, OpenClaw harness identity, or other caller-controlled metadata. Phase
1436 or a later activation phase must provide concrete numeric limits before
any public runtime surface opens.

Required public-path buckets:

```text
rate_limit_surface_bucket=fetch
rate_limit_surface_bucket=verifier
rate_limit_surface_bucket=sidecar_projection
rate_limit_surface_bucket=p2p
```

## 4. Ban, Revocation, Replay, And Admission Interface

The public runtime must fail closed unless all checks below are wired to the
authenticated TransportPrincipal context:

```text
ban_revocation_key_source=authenticated_transport_principal
credential_fingerprint_required=true
principal_id_required=true
agent_binding_required=true
issued_epoch_required=true
expires_epoch_required=true
revocation_registry_check_required=true
ban_registry_check_required=true
replay_cache_check_required=true
admission_throttle_check_required=true
```

The runtime may use separate derived keys for rate-limit, admission, ban, and
replay decisions, consistent with the Phase 1267 helper. Those keys must derive
from authenticated transport material, not from caller-supplied JSON or IP.

## 5. Credential Kinds

The first ratified admissible credential families are:

```text
credential_kind=mtls_certificate_fingerprint
credential_kind=quic_peer_credential
credential_kind=rustls_peer_certificate_chain_hash
credential_kind=signed_transport_handshake
```

Successor credential kinds require later explicit governance authorization.

## 6. README Contact Placeholder Disposition

CDL-094 ratification reviews the README contact placeholder but does not make
Jamison reachable through a live public confidential sidecar.

```text
jamison_confidential_sidecar=planned_not_live
public_confidential_messaging_enabled=false
public_confidential_coordination_enabled=false
live_contact_instruction_added=false
readme_contact_update_required_when_public_sidecar_activation_authorized=true
```

The README may be updated in a later phase only after both public sidecar
activation and public confidential coordination authority are explicitly live.

## 7. Explicit Non-Activation

This prelock does not authorize:

- public fetch serving;
- non-loopback sidecar/projection serving;
- public P2P or OpenClaw gateway activation;
- public confidential messaging or public confidential coordination serving;
- graph writes;
- wallet writes;
- treasury writes;
- ECU minting or distribution;
- ILC settlement;
- public RC publication;
- signing;
- epoch 0-to-1 transition.

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_094_transport_principal_prelock_1435_v0.1.md -> governance/transport-principal
```
