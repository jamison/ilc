# ILC Window 1257-1264 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-08.
**Authority:** This document does not open Window 1257-1264, assign official
phase authority, ratify CDL-087, open a Werner flow-governor CDL, authorize
public RC, authorize public repository publication, expose public P2P, expose
public sidecar/projection serving, activate public claimability, mutate Genesis,
or authorize v0.2 signing. Exact execution authority must be set by the future
Phase 1257 sequence lock after explicit human `GO Phase 1257`.

```text
window_1257_1264_candidate_phase_grouping_recorded_after_phase_1256
window_1257_1264_not_open_until_sequence_lock
```

---

## 1. Purpose

Window 1249-1256 closed with public-RC runway hardening complete for its locked
scope, but public RC remains blocked by CDL-087 production-candidate fetch
evidence/ratification, sidecar projection serving gates, TransportPrincipal and
Rust public-P2P hardening, public claimability/conversion runtime, ATLAS-G-006+,
counsel/publication authorization, and v0.2 signing authorization.

This candidate grouping turns the Phase 1256 handoff and public-RC runway plan
into the next draft execution window. The emphasis is fetch distribution,
sidecar projection serving boundaries, and flow-control evidence without public
exposure or economic minting shortcuts:

```text
cdl_087_ratification_window_candidate_after_sim_fetch_01_evidence
sidecar_projection_endpoint_window_candidate_after_cdl_087_and_transport_principal
werner_flow_governor_overlay_window_candidate
heat_signal_must_not_directly_mint_ecu
```

---

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md`
5. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
6. `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md`
7. `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
8. `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
9. `docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md`
10. `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md`
11. `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md`
12. `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md`
13. `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md`
14. `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py`
15. `ilc_core/graph/sidecar_query_runtime.py`
16. `ilc_core/graph/agent_graph_projection_runtime.py`
17. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

The Phase 1246 CDL-087 governance review is controlling for ratification
readiness: SIM-FETCH-01 evidence supports governance review, but Conditions 2,
3, and 4 still require production-candidate serving-peer/bootstrap/observability
evidence. Condition 5 requires final CDL-077 limiter regression, and Condition 6
requires re-verifying the fetch-incentive projection/credit bridge.

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable prompt draft in this window must include a four-part §0
discovery pass before coding:

1. `§0a - Known-token audit` for Required Tokens and explicit claims.
2. `§0b - Concept-discovery search` for forgotten synonyms, older names, code
   symbols, phase numbers, and domain concepts not already listed as tokens.
3. `§0c - Contradiction and non-claim search` for blockers such as `deferred`,
   `blocked`, `not authorized`, `not ratified`, `local-only`, `no public`,
   `superseded`, and domain-specific denial terms.
4. `§0d - Source expansion and newly discovered tokens` to direct-read every
   relevant hit and carry newly discovered tokens/non-claims into the phase
   walkthrough, STATUS entry, or carry-forward docs.

MemPalace may be used as an advisory recall net in §0b/§0d, but returned paths
must be direct-read before any result is treated as canon.

Exact-token `rg` is a schema/completion check only. It confirms that a required
token appears somewhere; it does not prove that related historical wording,
runtime symbols, or blocker concepts have been found. Phase execution must also
search token components, synonyms, neighboring concepts, older names, code
symbols, and denial terms before concluding that a concept is absent.

---

## 3. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1257 | Window 1257-1264 sequence lock | **SENSITIVE** - requires `GO Phase 1257` | `docs/antigravity_tasks/antigravity_prompt__phase_1257_g8_window_1257_1264_sequence_lock.md` |
| 1258 | CDL-087 production-candidate evidence readiness and condition inventory | **SENSITIVE** - requires `GO Phase 1258`; no register mutation by default | `docs/antigravity_tasks/antigravity_prompt__phase_1258_g8_cdl087_production_candidate_evidence_readiness.md` |
| 1259 | CDL-087 serving-peer evidence slice: Tier A/B/C classification plus bootstrap snapshot builder/verifier evidence | NON-SENSITIVE local/runtime-evidence slice unless the sequence lock marks it sensitive | `docs/antigravity_tasks/antigravity_prompt__phase_1259_g8_cdl087_serving_peer_evidence_slice.md` |
| 1260 | CDL-087 observability collection window and final CDL-077 limiter regression | NON-SENSITIVE local/evidence slice unless the sequence lock marks it sensitive | `docs/antigravity_tasks/antigravity_prompt__phase_1260_g8_cdl087_observability_and_limiter_regression.md` |
| 1261 | Sidecar projection endpoint boundary and TransportPrincipal public-path gate recheck | NON-SENSITIVE boundary/spec by default; no public endpoint | `docs/antigravity_tasks/antigravity_prompt__phase_1261_g8_sidecar_projection_endpoint_boundary.md` |
| 1262 | Werner Flow Governor overlay validation and promote/retire decision | NON-SENSITIVE simulation/evidence | `docs/antigravity_tasks/antigravity_prompt__phase_1262_g8_werner_flow_governor_overlay_validation.md` |
| 1263 | Werner flow-governor CDL opening/prelock decision, if evidence supports it | **SENSITIVE** - requires `GO Phase 1263`; no direct ECU minting | `docs/antigravity_tasks/antigravity_prompt__phase_1263_g8_werner_flow_governor_cdl_decision.md` |
| 1264 | Window 1257-1264 coherence, blocker classification, and closure gate | **SENSITIVE** - requires `GO Phase 1264` | `docs/antigravity_tasks/antigravity_prompt__phase_1264_g8_window_1257_1264_closure_gate.md` |

---

## 4. Scope Rationale

### 4.1 CDL-087 cannot ratify from SIM evidence alone

Phase 1238i/1238j SIM-FETCH evidence identifies a candidate envelope and a
robustness pass, but Phase 1246 records that CDL-087 ratification remains
deferred pending production-candidate evidence:

```text
cdl_087_governance_review_complete_phase_1246
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
cdl_087_sensitive_ratification_phase_required_if_later_authorized
```

The next window should therefore start by inventorying Conditions 1-6, then
close or route the open production-candidate evidence blockers before any
sensitive ratification attempt.

### 4.2 Production-candidate fetch evidence is the practical middle layer

The open CDL-087 blockers are concrete:

```text
cdl_087_blocker_production_candidate_tier_classification_runtime
cdl_087_blocker_bootstrap_snapshot_builder_and_verifier
cdl_087_blocker_production_candidate_observability_collection_window
cdl_087_blocker_final_cdl_077_rate_limiter_regression
```

Phases 1259 and 1260 should target these as local, bounded, canonical evidence
work. They must not expose public fetch serving, public P2P, or public sidecar
projection endpoints.

### 4.3 Sidecar projection serving remains gated

Local read-only sidecar query runtime exists, but public sidecar/projection
serving remains blocked:

```text
sidecar_projection_endpoint_required_post_cdl_087_ratification
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

Phase 1261 should either record that the endpoint remains blocked or produce a
strictly loopback/local boundary plan if the sequence lock authorizes it. It
must not create non-loopback projection serving unless both CDL-087 and
TransportPrincipal public-path gates have closed.

### 4.4 Werner flow must not become direct ECU minting

The Werner overlay is a flow-control and pressure-signal lane. It may inform
reputation, routing, admission, cache/mirror priority, or a future CDL, but not
direct ECU minting:

```text
werner_overlay_opt_in_must_be_promoted_or_retired_after_validation
werner_heat_prefers_reputation_routing_admission_before_ecu_creation
direct_werner_ecu_creation_assumption_requires_repo_memtrace_check
heat_signal_must_not_directly_mint_ecu
```

Phase 1262 should validate and promote/retire the overlay. Phase 1263 is a
sensitive CDL decision phase only if evidence supports opening/prelocking a
flow-governor policy.

---

## 5. Window Exit Criteria

Window 1257-1264 should not close as pass unless all of the following are true:

1. Phase 1257 sequence lock exists and records exact sensitive gates.
2. CDL-087 Conditions 1-6 are reconciled with committed evidence or precise
   carry-forward blockers.
3. Conditions 2, 3, and 4 production-candidate evidence blockers are closed or
   routed with file-level implementation requirements.
4. CDL-077 / persistent limiter final regression is run or carried forward with
   exact blockers.
5. Sidecar projection serving remains non-public unless CDL-087 and
   TransportPrincipal public-path gates have closed.
6. TransportPrincipal public-path requirements are rechecked before any sidecar
   endpoint or fetch-serving widening.
7. Werner overlay has a promote/retire verdict and preserves no direct ECU
   minting, no ILC settlement, and no claimability activation.
8. Any Werner CDL opening/prelock decision records a sensitive GO token and
   does not mutate CDL state without explicit authorization.
9. Public-RC blocker classes remain honestly classified as closed, open, or
   carried forward.

---

## 6. Non-Claims

This guidance does not:

- open Window 1257-1264;
- execute Phase 1257;
- ratify CDL-087;
- open or prelock a Werner flow-governor CDL;
- mutate any CDL row;
- authorize public RC;
- authorize public repository publication;
- authorize public P2P exposure;
- authorize public sidecar/projection serving;
- activate public claimability;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- generate release keys;
- produce release envelopes;
- mutate signed Genesis v0.1;
- regenerate Genesis Atlas v0.2+;
- mutate immutable diagnostic anchors;
- authorize v0.2 signing.

---

## 7. Carry-Forward Tokens

```text
window_1257_1264_candidate_phase_grouping_recorded_after_phase_1256
window_1257_1264_not_open_until_sequence_lock
cdl_087_ratification_window_candidate_after_sim_fetch_01_evidence
sidecar_projection_endpoint_window_candidate_after_cdl_087_and_transport_principal
werner_flow_governor_overlay_window_candidate
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
cdl_087_blocker_production_candidate_tier_classification_runtime
cdl_087_blocker_bootstrap_snapshot_builder_and_verifier
cdl_087_blocker_production_candidate_observability_collection_window
cdl_087_blocker_final_cdl_077_rate_limiter_regression
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
heat_signal_must_not_directly_mint_ecu
unknown_unknown_discovery_required_before_phase_execution
```
