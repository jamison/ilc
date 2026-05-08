# ILC CDL-087 Production-Candidate Evidence Readiness 1258 v0.1

**Date:** 2026-05-08
**Phase:** 1258
**Status:** readiness packet
**Human authorization:** `GO Phase 1258`
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
cdl_087_production_candidate_evidence_readiness_phase_1258.v0.1
cdl_087_ratification_not_executed_phase_1258
cdl_087_conditions_1_to_6_reconciled_phase_1258
cdl_087_open_blockers_routed_phase_1258
```

## 1. Scope and Verdict

Phase 1258 reconciles CDL-087 ratification Conditions 1-6 against current repo
evidence and routes the remaining production-candidate blockers. It is an
evidence-readiness packet, not a ratification artifact.

Verdict:

```text
cdl_087_ratification_readiness_verdict_phase_1258=not_ready
```

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
```

The CDL register is not mutated by this phase.

## 2. Canon Inputs

| Input | Use |
|-------|-----|
| `docs/PLANNING_INDEX.md` | Current frontier and current window lock pointer. |
| `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md` | Sensitive Phase 1258 authorization and non-ratification boundary. |
| `docs/specs/ilc_window_1257_1264_candidate_phase_grouping_v0.1.md` | Candidate routing for Phases 1259 and 1260. |
| `docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md` | Controlling Condition 1-6 disposition. |
| `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` | Ratification conditions and CDL-077 non-bypass rule. |
| `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md` | CDL-087 open/not-ratified basis. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md` | SIM-FETCH candidate-envelope evidence; non-authorizing. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md` | Fix10 robustness suite; non-authorizing. |
| `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py` | Harness boundary: no CDL-087 ratification, ECU mint, or ILC settlement. |
| `ilc_core/graph/agent_graph_projection_runtime.py` | Condition 6 projection-level evidence. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register confirms CDL-087 remains `open`. |

## 3. Discovery Audit

Exact-token `rg` was used only as a schema/completion check. Phase 1258 also
searched broad concept terms around `CDL-087`, `SIM-FETCH-01`,
`production candidate`, `serving peer`, `Tier A`, `Tier B`, `Tier C`,
`bootstrap snapshot`, `snapshot manifest`, `observability`, `collection window`,
`CDL-077`, `rate limiter`, `circuit breaker`, `fetch incentive`,
`credit bridge`, `holder directory`, and `WANT-HAVE`.

Contradiction searches covered `not ratified`, `ratification deferred`,
`not authorized`, `review-only`, `open blocker`, `fails`, `negative control`,
`local-only`, `no public`, `no production fetch serving`, `no sidecar`, and
`must not`.

MemPalace was not required. If used later, it remains advisory recall only and
returned paths must be direct-read before being treated as canon.

## 4. Condition 1-6 Readiness Table

| Condition | Current evidence | Phase 1258 disposition | Next route |
|-----------|------------------|------------------------|------------|
| 1. SIM-FETCH-01 passes | Phase 1238i/1238j evidence matrix and robustness suite pass for governance review; random single-hop probing remains a null model, not the CDL-087 architecture. | `condition_1_sim_fetch_01_passed_for_governance_review` remains satisfied for governance review, but not sufficient for ratification. | Preserve as evidence input for later sensitive ratification only after open production-candidate blockers close. |
| 2. Tier A/B/C classification in a production-candidate serving peer | SIM-FETCH classifies tiers in simulation, but Phase 1246 records the production-candidate serving-peer evidence as open. | `condition_2_production_candidate_tier_classification_open` remains open. | Phase 1259 must record or implement local production-candidate tier classification evidence. |
| 3. Bootstrap snapshot format builder/verifier | CDL-087 prelock defines `snapshot_manifest`, `genesis_domain_hash`, `snapshot_epoch`, `artifact_list`, `lineage_proof_chain`, `epoch_checkpoint_range`, `authority_refs`, and `graph_projection_export`; no concrete CDL-087 builder/verifier evidence is current. | `condition_3_bootstrap_snapshot_format_open` remains open. | Phase 1259 must record or implement a Genesis-verifiable bootstrap snapshot builder/verifier evidence slice. |
| 4. Production-candidate observability collection | SIM-FETCH emits observability metrics, but Phase 1246 requires at least one production-candidate serving peer to emit exact Section 6 names and collect one SIM window. | `condition_4_production_candidate_observability_open` remains open. | Phase 1260 must record a local collection-window artifact or an exact carry-forward route. |
| 5. CDL-077 static limiter preservation | CDL-077 remains ratified; persistent limiter backend/wiring exists from earlier phases; Phase 1246 still requires a final focused regression before ratification. | `condition_5_cdl_077_rate_limiter_preserved_pending_final_regression` remains pending final regression. | Phase 1260 must run or record final CDL-077/persistent limiter regression. |
| 6. Fetch-incentive projection / credit bridge | Phase 1229 exposes `fetch_incentive_hypergraph_slice`; projection distinguishes serving peer from served Graph Node; Phase 1238g credit bridge evidence exists. | `condition_6_fetch_incentive_projection_resolved_at_projection_level` remains satisfied at projection level and must be rechecked before ratification. | Phase 1258 carries this as evidence; later sensitive ratification must re-verify. |

## 5. Open Blockers Routed

The following blockers prevent CDL-087 ratification now:

```text
cdl_087_blocker_production_candidate_tier_classification_runtime
cdl_087_blocker_bootstrap_snapshot_builder_and_verifier
cdl_087_blocker_production_candidate_observability_collection_window
cdl_087_blocker_final_cdl_077_rate_limiter_regression
```

Route:

| Blocker | Route |
|---------|-------|
| `cdl_087_blocker_production_candidate_tier_classification_runtime` | Phase 1259 serving-peer evidence slice. |
| `cdl_087_blocker_bootstrap_snapshot_builder_and_verifier` | Phase 1259 serving-peer evidence slice. |
| `cdl_087_blocker_production_candidate_observability_collection_window` | Phase 1260 observability collection-window artifact or carry-forward. |
| `cdl_087_blocker_final_cdl_077_rate_limiter_regression` | Phase 1260 final limiter regression. |

## 6. Non-Authorization Boundary

Phase 1258 does not authorize:

- CDL register mutation;
- CDL-087 ratification;
- CDL-088 opening;
- public fetch serving;
- public sidecar/projection serving;
- public P2P exposure;
- public RC claim;
- public repository publication;
- public claimability activation;
- Werner ECU minting;
- ECU mint authorization;
- ILC settlement activation;
- release-key generation;
- release envelope production;
- v0.2 signing.

## 7. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1258_cdl087_production_candidate_evidence_readiness.py -> validation
graph_delta=support_only:docs/phases/phase_1258_cdl087_production_candidate_evidence_readiness_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 8. Next Phase

Phase 1259 is the next locked phase and remains non-sensitive unless widened by
new findings:

```text
cdl_087_serving_peer_evidence_slice_phase_1259.v0.1
```
