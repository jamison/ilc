# ILC Phase 1257-1264 Sequence Lock v0.1

**Date:** 2026-05-08
**Window:** 1257-1264
**Phase:** 1257
**Status:** LOCKED
**Human authorization:** `GO Phase 1257`
**Token:** `window_1257_1264_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1257-1264 is opened after explicit human authorization:

```text
GO Phase 1257
```

Verdict:

```text
window_1257_1264_sequence_lock_verdict=pass
window_1257_1264_sequence_lock_committed
phase_1258_cdl087_evidence_readiness_requires_explicit_go
window_1257_1264_no_public_rc_or_public_p2p
```

This lock fixes the Window 1257-1264 phase order, sensitivity gates,
CDL-087 production-candidate evidence posture, sidecar/projection boundary,
TransportPrincipal public-path recheck, Werner Flow Governor evidence lane, and
closure gate. It does not mutate runtime code, the CDL register, signed Genesis
v0.1, Genesis Atlas artifacts, release keys, public repository state, public
P2P state, public sidecar/projection serving, public claimability, ECU minting,
ILC settlement, or any public release artifact.

---

## 2. Baseline Inputs and Canon

| Input | Window-entry role |
|-------|-------------------|
| `docs/PLANNING_INDEX.md` | Current planning frontier after Window 1249-1256 closure. |
| `docs/phases/STATUS.md` | Actual status through Phase 1256. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Current capsule until superseded; Phase 1239 capsule still controls carried-forward runtime/capsule state. |
| `docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md` | Closed-window baseline and carry-forward blocker list. |
| `docs/specs/ilc_window_1257_1264_candidate_phase_grouping_v0.1.md` | Candidate guidance consumed by this lock. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Current controlling public-RC roadmap. |
| `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md` | Public-RC blocker/action-class runway context. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | Transport/value-path blocker context. |
| `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md` | TransportPrincipal public-path blocker and Python HTTP downgrade context. |
| `docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md` | Controlling CDL-087 governance review disposition. |
| `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` | Six ratification conditions and CDL-077 non-bypass rule. |
| `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md` | CDL-087 opening state and non-ratification basis. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md` | SIM-FETCH evidence matrix; non-authorizing. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md` | SIM-FETCH robustness suite; non-authorizing. |
| `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py` | SIM-FETCH harness boundary; no CDL-087 ratification, ECU mint, or ILC settlement. |
| `ilc_core/graph/sidecar_query_runtime.py` | Local read-only sidecar query runtime boundary. |
| `ilc_core/graph/agent_graph_projection_runtime.py` | Read-only graph projection runtime boundary. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-087 remains open. |

Window 1249-1256 is CLOSED / PASS through Phase 1256 with:

```text
window_1249_1256_closed_phase_1256
window_1249_1256_closure_gate_verdict=pass
phase_1256_window_1249_1256_closure_complete
phase_1250_fix1_gap_audit_routes_reconciled_phase_1256
```

Public RC remains blocked after Phase 1256:

```text
public_rc_remains_blocked_after_phase_1256
```

---

## 3. Entry Discovery Audit

The Phase 1257 discovery pass used exact-token search only as a
schema/completion check. Before writing this lock, context discovery also used
broader concept searches over CDL-087, production-candidate serving peers,
Tier A/B/C classification, bootstrap snapshots, observability, CDL-077,
sidecar projection, TransportPrincipal, Werner, flow governor, heat, public RC,
public P2P, and denial terms such as `deferred`, `blocked`, `not authorized`,
`not ratified`, `no public`, `must not`, `ECU mint`, and `ILC settlement`.

Discovery result:

| Check | Result |
|-------|--------|
| Required-token audit | Required Phase 1257 tokens were present in the Phase 1257 prompt before execution and are now recorded in this sequence lock, PLANNING_INDEX, STATUS, and walkthrough. |
| Concept-discovery search | Confirmed the active lanes are CDL-087 production-candidate evidence, sidecar/projection public-path boundaries, TransportPrincipal recheck, Werner overlay validation, possible Werner CDL decision, and closure. |
| Contradiction and non-claim search | Confirmed CDL-087 is not ratified, SIM-FETCH evidence is non-authorizing, public sidecar/projection and public P2P remain blocked, public RC remains blocked, Werner heat does not mint ECU or settle ILC, and v0.2 signing remains deferred. |
| Source expansion | Direct-read the current planning index, phase status, capsule v5.50, Phase 1256 handoff, Window 1257-1264 guidance, Roadmap v1.1, CDL-087 opening/prelock/governance review specs, SIM-FETCH evidence, sidecar/projection runtimes, and CDL register before locking the window. |

Standing discovery tokens:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable phase in this window must perform the same four-part discovery
pass before coding or drafting:

- §0a Known-token audit.
- §0b Concept-discovery search.
- §0c Contradiction and non-claim search.
- §0d Source expansion and newly discovered tokens.

MemPalace may be used only as advisory retrieval support. A MemPalace result is
not canon until the returned repo path is direct-read and reconciled against
current `docs/PLANNING_INDEX.md`, current capsule, current `docs/phases/STATUS.md`,
and this active window lock.

Exact-token `rg` is a schema/completion check only. It verifies that known phase
markers and required tokens exist; it must not be used as the sole context
retrieval method. For §0b/§0d, search token components, synonyms, neighboring ideas, older names, code symbols, and denial terms; also include
domain-specific denial terms, then direct-read relevant repo or
MemPalace-returned sources before concluding that a concept or blocker is absent.

---

## 4. CDL-087 and Public-RC State at Window Entry

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_canonical_fetch_distribution_policy_opened_phase_1227
cdl_087_prelock_committed_phase_1228
cdl_087_governance_review_complete_phase_1246
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
```

The CDL register still records CDL-087 as `open`. This lock does not mutate the
register and does not ratify CDL-087.

Condition status at window entry:

| Condition | Entry status | Window route |
|-----------|--------------|--------------|
| 1. SIM-FETCH-01 passes | Satisfied for governance review; not alone sufficient for ratification. | Preserve as evidence input. |
| 2. Tier A/B/C classification in a production-candidate serving peer | Open blocker. | Phase 1259 evidence slice after Phase 1258 inventory. |
| 3. Bootstrap snapshot format builder/verifier | Open blocker. | Phase 1259 evidence slice after Phase 1258 inventory. |
| 4. Production-candidate observability collection for at least one SIM window | Open blocker. | Phase 1260 observability collection route. |
| 5. CDL-077 static rate limiter remains active and no unlimited fetch path exists | Final regression required. | Phase 1260 limiter regression route. |
| 6. Fetch-incentive projection/credit bridge recheck | Requires recheck against serving-peer vs served-Graph-Node distinction before ratification. | Phase 1258 inventory and later CDL-087 decision routing. |

Public-RC blockers carried into this window:

- Gap 13 public claimability runtime and CDL-048 conversion sweeper.
- CDL-087 production-candidate evidence and later sensitive ratification.
- Public sidecar/projection serving, gated by CDL-087 and TransportPrincipal.
- TransportPrincipal runtime/ADR, revocation, replay, privacy, and rate-limit binding.
- Rust M-5 dynamic-membership/public-P2P substrate confidence.
- ATLAS-G-006+ public-RC graph reachability gate.
- Counsel/IP/trademark/CLA/patent and publication authorization.
- v0.2 signing authorization.

v0.2 signing remains deferred:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

---

## 5. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1257 | Window 1257-1264 sequence lock | **SENSITIVE** | `GO Phase 1257` consumed |
| 2 | 1258 | CDL-087 production-candidate evidence readiness and condition inventory | **SENSITIVE** | Requires `GO Phase 1258` |
| 3 | 1259 | CDL-087 serving-peer evidence slice: Tier A/B/C classification plus bootstrap snapshot builder/verifier evidence | NON-SENSITIVE unless widened | After Phase 1258 |
| 4 | 1260 | CDL-087 observability collection window and final CDL-077 limiter regression | NON-SENSITIVE unless widened | After Phase 1259 |
| 5 | 1261 | Sidecar projection endpoint boundary and TransportPrincipal public-path gate recheck | NON-SENSITIVE boundary/spec | After Phase 1260 |
| 6 | 1262 | Werner Flow Governor overlay validation and promote/retire decision | NON-SENSITIVE | After Phase 1261 |
| 7 | 1263 | Werner flow-governor CDL opening/prelock decision if evidence supports it | **SENSITIVE** | Requires `GO Phase 1263` |
| 8 | 1264 | Window coherence, blocker classification, and closure gate | **SENSITIVE** | Requires `GO Phase 1264` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are executed in sequence.

---

## 6. Execution Rules and Non-Authorization Boundary

### Phase 1258 gate

Phase 1258 is sensitive because it inventories conditions for a future
CDL-087 ratification decision. It requires:

```text
GO Phase 1258
phase_1258_cdl087_evidence_readiness_requires_explicit_go
```

Phase 1258 must not ratify CDL-087 or mutate the CDL register by default. Any
later CDL-087 ratification attempt requires a separate sensitive authorization
and must prove all six prelock ratification conditions or record an explicit
safe deferral in a future CDL.

### Public sidecar/projection boundary

Local read-only sidecar and graph projection runtimes do not authorize public
serving. Public sidecar/projection serving remains blocked unless CDL-087 and
TransportPrincipal public-path gates close:

```text
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

### Werner boundary

Werner heat and flow signals are advisory pressure signals only. They may inform
future reputation, routing, admission, cache/mirror priority, or a sensitive CDL
decision. They must not directly mint ECU, settle ILC, activate public
claimability, or bypass governance:

```text
heat_signal_must_not_directly_mint_ecu
```

### Non-claims

This sequence lock does not authorize:

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
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.

---

## 7. Carry-Forward Tokens

```text
window_1257_1264_sequence_lock_committed
window_1257_1264_sequence_lock_verdict=pass
phase_1258_cdl087_evidence_readiness_requires_explicit_go
window_1257_1264_no_public_rc_or_public_p2p
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
cdl_087_blocker_production_candidate_tier_classification_runtime
cdl_087_blocker_bootstrap_snapshot_builder_and_verifier
cdl_087_blocker_production_candidate_observability_collection_window
cdl_087_blocker_final_cdl_077_rate_limiter_regression
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
werner_overlay_opt_in_must_be_promoted_or_retired_after_validation
heat_signal_must_not_directly_mint_ecu
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

---

## 8. Graph Delta

Phase 1257 adds no runtime code and no load-bearing protocol state. It updates
planning/frontier and validation artifacts only:

```text
graph_delta=support_only:docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1257_window_1257_1264_sequence_lock_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1257_window_1257_1264_sequence_lock.py -> validation
```

---

## 9. Next Planned Phase

The next planned phase is Phase 1258, if explicitly authorized:

```text
GO Phase 1258
```

Phase 1258 scope is CDL-087 production-candidate evidence readiness and
condition inventory. It is sensitive and must not ratify CDL-087 unless a later
explicit authorization changes that scope.
