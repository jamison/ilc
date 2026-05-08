# ILC Window 1265-1272 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-08.
**Authority:** This document does not open Window 1265-1272, assign official
phase authority, ratify CDL-087, open a Werner flow-governor CDL, authorize
public RC, authorize public repository publication, expose public P2P, expose
public sidecar/projection serving, activate public claimability, mutate Genesis,
or authorize v0.2 signing. Exact execution authority must be set by the future
Phase 1265 sequence lock after explicit human `GO Phase 1265`.

```text
window_1265_1272_candidate_phase_grouping_recorded_after_phase_1264
window_1265_1272_not_open_until_sequence_lock
```

---

## 1. Purpose

Window 1257-1264 closed with CDL-087 local evidence readiness improved, sidecar
public-path boundaries clarified, Werner preserved as an evidence lane, and
public RC still blocked. This candidate grouping turns the Phase 1264 handoff
into the next draft execution window.

The emphasis is narrow:

```text
cdl_087_sensitive_review_window_candidate_after_phase_1264
transport_principal_public_path_runtime_window_candidate
sidecar_loopback_endpoint_window_candidate_no_public_serving
werner_default_topology_pressure_profile_window_candidate
gap13_claimability_preflight_window_candidate
atlas_g_006_public_rc_graph_gate_window_candidate
```

No candidate phase below is a public-RC claim. The sequence lock must decide
which scopes are executable and which are still too sensitive or under-evidenced.

---

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md`
5. `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`
6. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
7. `docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md`
8. `docs/specs/ilc_cdl_087_serving_peer_evidence_slice_1259_v0.1.md`
9. `docs/specs/ilc_cdl_087_observability_and_limiter_regression_1260_v0.1.md`
10. `docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md`
11. `docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md`
12. `docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md`
13. `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
14. `docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md`
15. `docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.md`
16. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
17. `ilc_core/network/d2d/cdl087_serving_peer_evidence.py`
18. `ilc_core/network/d2d/cdl087_observability.py`
19. `ilc_core/graph/sidecar_query_runtime.py`
20. `ilc_core/rc/atlas_graph_discipline.py`
21. `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py`

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable prompt draft in this window must include the exact four-part
§0 discovery pass before coding:

1. `### §0a — Known-token audit` for Required Tokens and explicit claims.
2. `### §0b — Concept-discovery search` for forgotten synonyms, older names,
   code symbols, phase numbers, and domain concepts not already listed as tokens.
3. `### §0c — Contradiction and non-claim search` for blockers such as
   `deferred`, `blocked`, `not authorized`, `not ratified`, `local-only`,
   `no public`, `superseded`, and domain-specific denial terms.
4. `### §0d — Source expansion and newly discovered tokens` to direct-read every
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
| 1265 | Window 1265-1272 sequence lock | **SENSITIVE** - requires `GO Phase 1265` | `docs/antigravity_tasks/antigravity_prompt__phase_1265_g8_window_1265_1272_sequence_lock.md` |
| 1266 | CDL-087 sensitive ratification review and decision packet | **SENSITIVE** - requires `GO Phase 1266`; no register mutation by default | `docs/antigravity_tasks/antigravity_prompt__phase_1266_g8_cdl087_sensitive_ratification_review.md` |
| 1267 | TransportPrincipal runtime identity pre-public-path slice | NON-SENSITIVE implementation/spec unless sequence lock widens to public exposure | `docs/antigravity_tasks/antigravity_prompt__phase_1267_g8_transport_principal_runtime_identity_pre_public_path.md` |
| 1268 | Sidecar loopback projection endpoint boundary or prototype | NON-SENSITIVE only if loopback/subprocess/Unix-socket local; no non-loopback serving | `docs/antigravity_tasks/antigravity_prompt__phase_1268_g8_sidecar_loopback_projection_endpoint_boundary.md` |
| 1269 | Werner default SIM-FETCH topology-pressure profile follow-up | NON-SENSITIVE simulation/evidence | `docs/antigravity_tasks/antigravity_prompt__phase_1269_g8_werner_default_topology_pressure_profile.md` |
| 1270 | Gap 13 claimability conversion-sweeper preflight | **SENSITIVE** - requires `GO Phase 1270`; no claimability activation | `docs/antigravity_tasks/antigravity_prompt__phase_1270_g8_gap13_claimability_conversion_sweeper_preflight.md` |
| 1271 | ATLAS-G-006 public-RC graph reachability gate | NON-SENSITIVE artifact/gate unless it mutates Genesis or public-release artifacts | `docs/antigravity_tasks/antigravity_prompt__phase_1271_g8_atlas_g_006_public_rc_graph_reachability_gate.md` |
| 1272 | Window 1265-1272 closure gate | **SENSITIVE** - requires `GO Phase 1272` | `docs/antigravity_tasks/antigravity_prompt__phase_1272_g8_window_1265_1272_closure_gate.md` |

---

## 4. Scope Rationale

### 4.1 CDL-087 is ready for review, not automatically ratified

Phase 1260 records:

```text
cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review
```

That verdict justifies a sensitive review window. It does not mutate the CDL
register. Phase 1266 must either record no-ratification/no-mutation, or if a
future human authorization explicitly widens scope to ratification, prove all
six locked CDL-087 conditions and preserve a clean register diff discipline.
The Phase 1266 prompt must carry
`cdl_087_ratification_not_executed_by_default_phase_1266` as a required token
unless the future human instruction explicitly authorizes ratification scope.

### 4.2 Public path depends on TransportPrincipal before exposure

Phase 1261 keeps public/non-loopback sidecar projection blocked because
TransportPrincipal remains a spec/ADR input, not runtime identity. The next
window can make progress by implementing or specifying a local runtime identity
contract, but it must not expose public P2P or non-loopback projection serving.

### 4.3 Sidecar endpoint work must stay local

Current sidecar and graph projection surfaces are local, read-only, bounded, and
in-process. A loopback-only prototype may be useful after sequence-lock review,
but any public path still requires CDL-087 and TransportPrincipal closure.

### 4.4 Werner needs profile hardening before CDL reconsideration

Phase 1263 did not open or prelock a Werner CDL. The safe next step is a
non-runtime SIM-FETCH profile follow-up that makes `topology_pressure_model`
explicit, keeps a `"none"` profile for comparison, preserves canonical JSON and
safe numeric handling, and keeps ECU/ILC authorization flags false.

### 4.5 Public claimability and ATLAS-G remain independent gates

Gap 13 claimability/conversion-sweeper work remains sensitive and must not
enable wallet withdrawal, transfer, spend, public claimability, ECU mint, or ILC
settlement by default. ATLAS-G-006 can advance public-RC graph reachability
evidence, but it must not mutate Genesis, generate a release artifact, or
publish a public repository.

---

## 5. Window Exit Criteria

Window 1265-1272 should not close as pass unless all of the following are true:

1. Phase 1265 sequence lock exists and records exact sensitive gates.
2. CDL-087 sensitive review status is recorded and the CDL register disposition
   is explicit.
3. TransportPrincipal runtime/public-path status is recorded without public P2P
   exposure.
4. Sidecar projection endpoint status is local-only or explicitly blocked.
5. Werner default topology-pressure profile status is recorded without runtime
   economic policy activation.
6. Gap 13 claimability/conversion-sweeper status is recorded without public
   claimability activation.
7. ATLAS-G-006 public-RC graph reachability status is recorded without public
   release artifact authorization.
8. Public-RC blocker classes remain honestly classified as closed, open, or
   carried forward.

---

## 6. Non-Claims

This guidance does not:

- open Window 1265-1272;
- execute Phase 1265;
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
window_1265_1272_candidate_phase_grouping_recorded_after_phase_1264
window_1265_1272_not_open_until_sequence_lock
cdl_087_sensitive_review_window_candidate_after_phase_1264
transport_principal_public_path_runtime_window_candidate
sidecar_loopback_endpoint_window_candidate_no_public_serving
werner_default_topology_pressure_profile_window_candidate
gap13_claimability_preflight_window_candidate
atlas_g_006_public_rc_graph_gate_window_candidate
public_rc_remains_blocked_after_phase_1264
cdl_087_sensitive_ratification_review_required_after_phase_1264
cdl_087_ratification_not_executed_by_default_phase_1266
transport_principal_runtime_required_before_non_loopback_projection
sidecar_projection_public_path_still_blocked_after_phase_1264
werner_default_topology_pressure_profile_required_before_runtime_cdl
werner_productive_credit_authorization_cdl_required
gap13_claimability_runtime_conversion_sweeper_required_before_final_public_rc
atlas_g_006_public_rc_graph_reachability_gate_required
unknown_unknown_discovery_required_before_phase_execution
```
