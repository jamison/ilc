# ILC CDL-094 TransportPrincipal Ratification Evidence 1435 v0.1

**Date:** 2026-05-23
**Phase:** 1435
**Status:** ratification evidence prepared; C2 mutates CDL register
**Human authorization:** `GO Phase 1435`
**Opening anchor:** Phase 1434 C1 `b5152c37`
**Prelock document:** `docs/specs/ilc_cdl_094_transport_principal_prelock_1435_v0.1.md`

```text
transport_principal_cdl_ratified_phase_1435
cdl_094_transport_principal_ratified_phase_1435
gap_10_cdl_governance_closed_phase_1435
cdl_094_ratified_governance_only_not_activated_phase_1435
cdl_094_prelock_committed_phase_1435
cdl_094_scope_constants_locked_phase_1435
```

## 1. Ratification Verdict

CDL-094 is ratified as the TransportPrincipal public-path governance authority.
This closes Gap 10 at the constitutional level only.

Ratification locks the rule that public non-loopback network paths must be
bound to an authenticated TransportPrincipal with rate-limit, ban, revocation,
replay, and admission policy. It does not open any public runtime surface.

```text
cdl_094_status=ratified
ratified_phase=1435
ratification_token=transport_principal_cdl_ratified_phase_1435
gap_10_cdl_governance_status=closed
runtime_activation_status=not_authorized
public_fetch_serving_status=not_enabled
public_sidecar_projection_status=not_enabled
public_p2p_status=not_enabled
public_confidential_coordination_status=not_enabled
confidential_contact_status=jamison_confidential_sidecar_planned_not_live
```

## 2. Pre-Execution Claim Verification

| Claim | File or symbol checked | Result |
|---|---|---|
| Phase 1435 is SENSITIVE and has explicit human GO | user request; `docs/antigravity_tasks/antigravity_prompt__phase_1435_g8_transport_principal_cdl_ratification.md` | confirmed |
| CDL-094 was open before ratification | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed: row status was `open` with Phase 1434 opening token |
| Phase 1434 opening artifact is committed | `docs/specs/ilc_cdl_094_transport_principal_public_path_opening_1434_v0.1.md`; C1 commit `b5152c37` | confirmed |
| CDL-087 did not activate public fetch or public sidecar/projection serving | `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md` | confirmed |
| CDL-079 is curated bootstrap distribution, not permissionless public P2P authority | `docs/specs/ilc_cdl_079_hb_002_bootstrap_distribution_ratification_evidence_918_v0.1.md` | confirmed |
| Phase 1436 is SENSITIVE, not non-sensitive | `docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`; `docs/specs/ilc_window_1429_1458_public_rc_activation_forward_plan_v0.1.md` | confirmed; prompt walkthrough wording patched |
| README contact placeholder is not live | `README.md` | confirmed: `jamison_confidential_sidecar: planned_not_live` and `local_preview_only_no_public_confidential_messaging` |

## 3. Discovery Results

Known-token, concept, contradiction, and non-claim searches covered:

```text
transport_principal_cdl_ratified_phase_1435
cdl_094_transport_principal_ratified_phase_1435
cdl_094_transport_principal_opened_phase_1434
gap_10_cdl_opening_committed_phase_1434
CDL-094
TransportPrincipal
authenticated_principal
non_loopback
loopback_only
rate_limit_policy
ban_revocation
jamison_confidential_sidecar
public_confidential_messaging
public_confidential_coordination_serving
not authorized
not enabled
not ratified
no_public_confidential_messaging
```

Relevant historical sources direct-read:

- `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
- `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md`
- `ilc_core/network/d2d/transport_principal_pre_public_path.py`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
- `ilc_core/sidecars/transport_principal_admission.py`

The searches confirmed that previous TransportPrincipal code is local,
pre-public, or fail-closed scaffolding. No source authorized public fetch
serving, public P2P, non-loopback sidecar/projection, or public confidential
coordination.

## 4. Locked Ratification Constants

| Constant | Value |
|---|---|
| `policy_boundary_constant` | `TRANSPORT_PRINCIPAL_CDL_RATIFIED` |
| `authenticated_principal_required_for_non_loopback` | `true` |
| `transport_principal_required_for_non_loopback` | `true` |
| `ip_only_authentication_allowed` | `false` |
| `json_requester_id_authentication_allowed` | `false` |
| `requester_id_fallback_allowed` | `false` |
| `raw_agent_id_default_rate_limit_key_allowed` | `false` |
| `client_ip_primary_rate_limit_key_allowed` | `false` |
| `rate_limit_policy` | `per_agent_id_bound_transport_principal_epoch_window` |
| `rate_limit_identity_source` | `authenticated_transport_principal` |
| `rate_limit_window_basis` | `epoch_sequence` |
| `ban_revocation_interface` | `required` |

## 5. Ratification Boundary

CDL-094 ratification authorizes governance policy only. Runtime activation
remains in Phase 1436 after Gap 14 completes and requires explicit SENSITIVE
human GO.

```text
public_fetch_serving_enabled=false
public_sidecar_projection_enabled=false
public_p2p_enabled=false
public_confidential_coordination_enabled=false
live_confidential_contact_instruction_added=false
wallet_writes=false
graph_writes=false
ecu_minting=false
ilc_settlement=false
epoch_0_to_1_transition=false
```

## 6. README Placeholder Disposition

The README contact block remains a future-gated placeholder:

```text
jamison_confidential_sidecar=planned_not_live
public_confidential_messaging_enabled=false
public_confidential_coordination_enabled=false
live_contact_instruction_added=false
```

CDL-094 ratification is necessary for a future public confidential sidecar but
is not sufficient. A later phase must explicitly authorize public sidecar
activation, public confidential coordination authority, and the concrete README
contact update.

## 7. C2 Register Mutation Requirements

C2 must update the CDL-094 register row with:

```text
status=ratified
ratified_phase=1435
ratified_date=2026-05-23
ratification_token=transport_principal_cdl_ratified_phase_1435
evidence_document=docs/specs/ilc_cdl_094_transport_principal_ratification_evidence_1435_v0.1.md
runtime_activation_status=not_authorized
```

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_094_transport_principal_ratification_evidence_1435_v0.1.md -> governance/transport-principal
```
