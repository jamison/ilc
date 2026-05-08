# ILC Window 1257-1264 Handoff 1264 v0.1

Status: handoff artifact
Date: 2026-05-08
Classification: closure and carry-forward handoff
Window: 1257-1264
Closure phase: 1264
Closure verdict: pass
Human authorization: `GO Phase 1264`

## 1. Window identity and closure basis

Window 1257-1264 is closed at Phase 1264 with a pass verdict:

```text
window_1257_1264_closed_phase_1264
window_1257_1264_closure_gate_verdict=pass
phase_1264_window_1257_1264_closure_complete
```

The pass verdict is scoped to the locked window objective: CDL-087
production-candidate evidence readiness, local serving-peer evidence,
observability and limiter regression evidence, sidecar public-path boundary,
Werner overlay validation, Werner CDL no-open decision, and handoff readiness.
It is not a public RC claim, public launch claim, public repository publication
authorization, public P2P authorization, public sidecar/projection serving
authorization, public claimability activation, CDL mutation, or v0.2 signing
authorization.

The next phase number is not assigned by this handoff:

```text
window_1265_plus_sequence_lock_required_before_next_phase_assignment
```

## 2. Inputs and closure inheritance

Authoritative closure inputs:

| Input | Closure use |
|-------|-------------|
| `docs/PLANNING_INDEX.md` | Current frontier and current planning index before closure. |
| `docs/phases/STATUS.md` | Phase 1257-1263 actual completion state. |
| `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md` | Locked order, sensitive gates, discovery discipline, and non-authorization boundary. |
| `docs/specs/ilc_window_1257_1264_candidate_phase_grouping_v0.1.md` | Window-scope rationale and exit criteria. |
| `docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md` | Prior closed-window inheritance. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Current capsule inherited through the window. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC roadmap. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-087 remains open and no Werner flow-governor CDL row exists. |
| Phase 1258-1263 specs, tests, and walkthroughs | Direct evidence for each lane status. |

The Phase 1264 discovery pass treated exact-token `rg` as a
schema/completion check only. Context discovery also used broad concept
searches, token components, synonyms, neighboring concepts, older names, code
symbols, denial terms, and current repo source reads before this closure
classified any blocker as closed or carried forward.

## 3. Closure verdict summary

| Phase | Window role | Closure status |
|-------|-------------|----------------|
| 1257 | Sequence lock | Closed. Window opened after explicit `GO Phase 1257`; sensitive gates recorded for 1258, 1263, and 1264. |
| 1258 | CDL-087 production-candidate evidence readiness | Closed for readiness inventory. Ratification readiness verdict was `not_ready`; Conditions 2/3 routed to Phase 1259 and Conditions 4/5 routed to Phase 1260. |
| 1259 | CDL-087 serving-peer evidence slice | Closed for local evidence. Tier A/B/C classification and Genesis-verifiable bootstrap snapshot builder/verifier evidence were recorded without public fetch serving. |
| 1260 | CDL-087 observability and limiter regression | Closed for local evidence. Exact Section 6 observability collection-window validation and final CDL-077 limiter regression were recorded; readiness became later sensitive review, not ratification. |
| 1261 | Sidecar projection endpoint boundary | Closed for boundary. Public/non-loopback sidecar projection remains blocked by missing CDL-087 ratification and missing TransportPrincipal runtime. |
| 1262 | Werner overlay validation | Closed for simulation/evidence promotion. Werner is promoted only as a future SIM-FETCH topology-pressure evidence profile after follow-up; no economic runtime policy was activated. |
| 1263 | Werner flow-governor CDL decision | Closed for sensitive decision. No Werner CDL was opened or prelocked; direct Werner ECU creation was rejected. |
| 1264 | Closure gate | Passed. All locked window lanes are reconciled here and routed into Window 1265+ sequence-lock requirements. |

Closure verdict:

```text
window_1257_1264_closure_gate_verdict=pass
```

The window can close as pass because every locked phase has a status entry,
CDL-087 Conditions 1-6 are mapped, sidecar projection endpoint authorization is
classified, TransportPrincipal public-path status is classified, Werner overlay
and Werner CDL decision status are classified, and public-RC blocker classes
remain explicitly classified as closed, carried forward, or blocked.

## 4. CDL-087 condition status at closure

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
```

The CDL register is not mutated by this window. Phase 1260 records:

```text
cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review
no_cdl_087_ratification_phase_1260
```

Condition status:

| Condition | Closure status | Future route |
|-----------|----------------|--------------|
| 1. SIM-FETCH-01 passes | `condition_1_sim_fetch_01_passed_for_governance_review`; preserved as governance-review evidence only. | Re-read Phase 1238i/1238j before any sensitive ratification. |
| 2. Tier A/B/C classification in a production-candidate serving peer | `condition_2_production_candidate_tier_classification_local_evidence_recorded_phase_1259`; local evidence recorded. | Future sensitive CDL-087 ratification review must decide sufficiency. |
| 3. Bootstrap snapshot format builder/verifier | `condition_3_bootstrap_snapshot_builder_verifier_local_evidence_recorded_phase_1259`; local Genesis-verifiable builder/verifier evidence recorded. | Future sensitive CDL-087 ratification review must decide sufficiency. |
| 4. Production-candidate observability collection | `condition_4_observability_collection_window_local_evidence_recorded_phase_1260`; exact Section 6 signal validation recorded. | Future sensitive CDL-087 ratification review must decide sufficiency. |
| 5. CDL-077 limiter preservation | `condition_5_cdl077_limiter_regression_recorded_phase_1260`; focused local regression recorded. | Re-run or cite the regression in any sensitive ratification review. |
| 6. Fetch-incentive projection / credit bridge | `condition_6_fetch_incentive_projection_resolved_at_projection_level`; remains projection-level satisfied and must be rechecked before ratification. | Recheck serving peer versus served Graph Node distinction before ratification. |

This window improves CDL-087 evidence readiness. It does not ratify CDL-087.

## 5. Sidecar, TransportPrincipal, and public-path status

Sidecar projection public-path verdict:

```text
sidecar_projection_endpoint_authorization_verdict_phase_1261=blocked_public_path
sidecar_projection_endpoint_not_publicly_exposed_phase_1261
sidecar_public_path_requires_cdl087_and_transport_principal_phase_1261
transport_principal_policy_gate_rechecked_phase_1261
```

Public/non-loopback sidecar projection serving remains blocked because:

- CDL-087 is ready only for later sensitive review, not ratified.
- TransportPrincipal remains a spec/ADR input, not a runtime public-path
  identity implementation.
- Public-path rate limits, admission controls, bans, replay resistance,
  revocation, and privacy boundaries are not implemented.
- Rust public-P2P / non-loopback substrate confidence remains a separate
  public-RC blocker.

Loopback/local read-only graph projection and sidecar query runtime remain
allowed only within their existing bounded local surfaces.

## 6. Werner status and direct ECU rejection

Werner overlay verdict:

```text
werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup
```

Werner CDL decision:

```text
werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
direct_werner_ecu_creation_rejected_phase_1263
```

The Werner lane carries forward as simulation/evidence work, not as runtime
economic policy. A future sensitive Werner CDL opening would need a committed
default SIM-FETCH topology-pressure profile, beta/noise decomposition,
spectral trust threshold packet, TransportPrincipal/admission binding, and a
separate productive-credit authorization path.

Carry-forward Werner/value-path tokens:

```text
werner_default_topology_pressure_profile_required_before_runtime_cdl
beta_decomposition_required_before_policy_use
flow_governor_spectral_trust_threshold_required_before_policy_use
flow_governor_cdl_required_before_runtime_policy_deployment
transport_principal_identity_required_before_public_p2p
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
heat_signal_must_not_directly_mint_ecu
```

## 7. Carry-forward items and residual blockers

Closed and not carried forward as current blockers:

| Item | Disposition |
|------|-------------|
| Phase 1257 sequence lock | Complete. |
| CDL-087 Condition 2 local evidence route | Complete as local evidence; sufficiency remains for future sensitive review. |
| CDL-087 Condition 3 local evidence route | Complete as local evidence; sufficiency remains for future sensitive review. |
| CDL-087 Condition 4 local evidence route | Complete as local evidence; sufficiency remains for future sensitive review. |
| CDL-087 Condition 5 local limiter regression route | Complete as local evidence; must be cited or rerun by any ratification phase. |
| Sidecar projection public-path recheck | Complete for boundary; verdict is blocked public path. |
| Werner overlay promote/retire decision | Complete as simulation/evidence promotion after follow-up. |
| Werner flow-governor CDL opening/prelock decision | Complete as no-open/no-prelock. |

Carried-forward public-RC blockers:

| Blocker | Next routing |
|---------|--------------|
| CDL-087 sensitive ratification review | Future sensitive sequence-locked phase may decide whether Phase 1259/1260 local evidence satisfies Conditions 2-5 and recheck Condition 6. |
| Public sidecar/projection serving | Still blocked by CDL-087 ratification and TransportPrincipal runtime/public-path policy. |
| TransportPrincipal runtime, ADR, revocation, replay, privacy, and rate-limit binding | Future transport/public-P2P lane before public P2P or non-loopback sidecar/projection serving. |
| Rust M-5 dynamic-membership/public-P2P substrate confidence gap | Future Rust public-P2P hardening; static genesis testnet posture is not enough for hostile dynamic membership claims. |
| Gap 13 public claimability runtime and CDL-048 conversion sweeper | Future sensitive/runtime phase. Public claimability remains epoch/root-resolution driven and is not agent-authored manual entitlement. |
| ATLAS-G-006+ public-RC graph reachability gate | Future ATLAS-G public-RC gate before any public release artifact claim. |
| Werner default topology-pressure profile and CDL preconditions | Future non-runtime SIM-FETCH profile follow-up, then possible sensitive CDL opening only after closing conditions are met. |
| Productive-credit / value-path authorization | Future separate CDL; no direct Werner ECU creation and no heat-mutated settlement. |
| Counsel/IP/trademark/CLA/patent and publication authorization | Future counsel/publication gate; public repository publication remains unauthorized. |
| v0.2 signing | Future human signing authorization gate; no release keys or release envelope. |
| Pre-existing dirty generated graph/diagnostic/monitoring artifacts | Remain outside this closure commit and must be reconciled in the graph/diagnostic lane. |

## 8. Next-window entry criteria and routing

The next window may assume Window 1257-1264 is closed with a pass verdict for
its locked scope. It may not assume public RC, public repository publication,
public P2P, public sidecar/projection serving, public claimability, CDL-087
ratification, Werner CDL opening/prelock, release-key generation, release
envelope production, Genesis mutation, Genesis Atlas regeneration, or v0.2
signing.

The next window must begin with a new sequence lock before assigning any
further phase numbers:

```text
window_1265_plus_sequence_lock_required_before_next_phase_assignment
```

Recommended Window 1265+ routing:

| Lane | First decision the next sequence lock should make |
|------|---------------------------------------------------|
| CDL-087 | Decide whether to open a sensitive ratification-review phase using Phase 1259/1260 evidence, or require additional production-candidate hardening first. |
| TransportPrincipal / public path | Decide whether to implement runtime identity/ADR/lifecycle/revocation/replay/privacy before any public P2P or non-loopback sidecar/projection endpoint. |
| Sidecar projection | Decide whether a loopback-only endpoint prototype is useful, while keeping public/non-loopback serving blocked. |
| Werner | Decide whether to implement the default `topology_pressure_model=werner_v1` SIM-FETCH evidence profile before any CDL opening reconsideration. |
| Gap 13 claimability | Decide whether claimability runtime, CDL-048 conversion sweeper, or a narrower dependency-hardening slice is next. |
| ATLAS-G | Decide whether ATLAS-G-006 public-RC graph reachability gate is now the controlling release-artifact blocker. |
| Publication and signing | Keep public-source publication and v0.2 signing gated unless explicit human/counsel/signing authorization is provided. |

## 9. MemPalace refresh disposition

- Disposition: required
- Active working set impacted: yes
- Basis: Window 1257-1264 is now closed; the current closure handoff, planning
  index, roadmap addendum, and phase status changed the authoritative planning
  frontier and retrieval surface.
- Working-set descriptor: `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
- Manifest: `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
- Rebuild command: `bash tools/mempalace/build_active_working_set.sh`

MemPalace remains advisory recall only. It does not replace direct repo reads,
the planning index, phase status, capsule, roadmap, or accepted gate artifacts.

## 10. Non-authorization boundary

This closure does not authorize:

- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- public P2P exposure;
- public sidecar/projection serving;
- public claimability activation;
- wallet withdrawal, wallet transfer, or wallet spend semantics;
- CDL mutation, CDL-087 ratification, Werner CDL opening/prelock, or CDL-088 opening;
- ECU mint authorization;
- direct Werner ECU creation;
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.

## 11. Graph delta

Phase 1264 adds no runtime code and no load-bearing protocol state. It updates
planning/frontier and validation artifacts only:

```text
graph_delta=support_only:docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1264_window_1257_1264_closure_gate_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1264_window_1257_1264_closure_gate.py -> validation
```
