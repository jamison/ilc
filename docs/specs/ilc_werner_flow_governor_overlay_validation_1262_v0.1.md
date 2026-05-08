# ILC Werner Flow Governor Overlay Validation 1262 v0.1

**Date:** 2026-05-08
**Phase:** 1262
**Status:** Werner overlay validated for simulation evidence promotion
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
werner_flow_governor_overlay_validation_phase_1262.v0.1
werner_overlay_promote_or_retire_verdict_recorded_phase_1262
heat_signal_must_not_directly_mint_ecu_phase_1262
no_werner_ecu_minting_or_ilc_settlement_phase_1262
```

## 1. Scope and Verdict

Phase 1262 validates the SIM-FETCH-01 Werner topology-pressure overlay as a
flow-control evidence signal. The phase does not change runtime economic policy
and does not change SIM-FETCH default behavior in code.

Verdict:

```text
werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup
```

Meaning:

- Promote the overlay as the preferred SIM-FETCH topology-pressure evidence
  profile in a future non-runtime follow-up.
- Replace the boolean opt-in shape with an explicit profile name such as
  `topology_pressure_model=werner_v1` only in a later scoped implementation.
- Preserve a `"none"` or null comparison profile for legacy/research controls.
- Do not deploy Werner heat as runtime economic policy without a future
  sensitive CDL/ADR path.

## 2. Evidence Rechecked

| Source | Phase 1262 conclusion |
|--------|-----------------------|
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | Records Werner as a topology-aware flow governor, not a rate limiter or direct ECU toll. Heat should shift routing, reputation, admission, and cache/mirror priority before any value path. |
| `tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py` | Locks overlay metrics, deterministic traces, unsafe-input rejection, disabled-by-default behavior, and non-authorizing ECU/ILC flags. |
| `docs/sims/sim_fetch_01/sim_fetch_01_werner_overlay_results_1238h_v0.1.json` | Records the overlay authorization note: topology pressure signals only; no ECU mint, no ILC settlement, no CDL-087 authorization, and no production runtime mutation. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md` and `.json` | Records 48-row sweep with 38 pass, 2 needs-review, 8 fail; every row keeps Werner ECU mint and ILC settlement unauthorized. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md` and `.json` | Records robustness verdict pass and repeats that Werner does not authorize ECU minting or ILC settlement. |
| `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py` | Emits `sim_fetch_topology_pressure_only`, deterministic Decimal pressure smoothing, recommendation fields, and hard false authorization flags. |

## 3. Allowed and Forbidden Use

Allowed uses after Phase 1262:

- reputation evidence;
- routing-weight evidence;
- admission-budget evidence;
- cache and mirror priority evidence;
- future CDL evidence for a Werner flow-governor policy.

Forbidden uses after Phase 1262:

- direct ECU minting from heat;
- ILC settlement from heat;
- public claimability activation;
- wallet withdrawal, transfer, spend, or productive-credit signing authority;
- runtime economic policy deployment;
- public RC or public launch claim;
- CDL mutation without a later sensitive phase.

The governing boundary is:

```text
heat_signal_must_not_directly_mint_ecu_phase_1262
no_werner_ecu_minting_or_ilc_settlement_phase_1262
flow_governor_cdl_required_before_runtime_policy_deployment
flow_governor_spectral_trust_threshold_required_before_policy_use
werner_overlay_opt_in_must_be_promoted_or_retired_after_validation
werner_default_topology_pressure_profile_required_before_runtime_cdl
werner_heat_prefers_reputation_routing_admission_before_ecu_creation
```

## 4. Promotion Conditions

The promotion is limited to the simulation/evidence lane. A later follow-up may
implement the default SIM-FETCH topology-pressure profile only if it preserves:

- deterministic Decimal or fixed-point pressure arithmetic;
- explicit profile selection instead of ambiguous booleans;
- canonical JSON exports with stable sorting and `allow_nan=False`;
- legacy `"none"` comparison profile for research controls;
- non-authorizing flags for ECU mint, ILC settlement, public claimability, and
  CDL-087 ratification;
- no runtime policy activation.

Runtime policy deployment remains blocked until a future sensitive governance
phase decides whether to open or prelock a Werner flow-governor CDL.

## 5. Non-Authorization Boundary

Phase 1262 does not authorize:

- runtime economic policy activation;
- ECU minting;
- ILC settlement;
- wallet withdrawal, transfer, or spend semantics;
- public claimability activation;
- CDL opening, prelock, ratification, or register mutation;
- public RC claim;
- public repository publication;
- public P2P exposure;
- public sidecar/projection serving;
- public fetch serving;
- release-key generation;
- release envelope production;
- v0.2 signing.

## 6. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md -> planning/werner
graph_delta=support_tests_added:tests/test_phase_1262_werner_flow_governor_overlay_validation.py -> validation
graph_delta=support_only:docs/phases/phase_1262_werner_flow_governor_overlay_validation_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 7. Next Phase

Phase 1263 is the next locked phase, but it is sensitive and requires explicit
human authorization before execution:

```text
phase_1263_requires_explicit_go_for_werner_cdl_decision
```
