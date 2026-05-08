# ILC CDL-087 Governance Review Disposition 1246 v0.1

**Date:** 2026-05-08
**Phase:** 1246
**Status:** REVIEW COMPLETE / RATIFICATION DEFERRED
**CDL:** CDL-087 — Canonical Fetch Distribution Policy
**Boundary:** review-only; no CDL mutation; no ratification

---

## 1. Disposition

CDL-087 is ready for a later governance ratification evidence phase **only after**
the remaining production-candidate implementation gates are closed.

Current recommendation:

```text
cdl_087_governance_review_complete_phase_1246
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
cdl_087_sensitive_ratification_phase_required_if_later_authorized
```

The Phase 1238 SIM-FETCH-01 evidence through Fix10 is strong enough to retire
the random-peer null model as the evaluative architecture. CDL-087 should be
evaluated against routed holder-directory behavior, multi-hop retry, adaptive
replication where applicable, and serving-peer/operator credit attribution.

However, simulation evidence does not by itself satisfy all six CDL-087 prelock
ratification conditions. Conditions 2, 3, and 4 still require
production-candidate serving-peer/bootstrap/observability implementation
evidence.

---

## 2. Evidence Inputs

| Artifact | Role |
|----------|------|
| `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` | Six ratification conditions and terminology lock |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md` | 48-scenario fixed-evaluator sweep |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.json` | Canonical machine-readable sweep |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md` | 4-profile robustness/negative-control summary |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.json` | Canonical machine-readable robustness suite |
| `docs/phases/phase_1238j_sim_fetch_01_fix10_robustness_suite_walkthrough.md` | Fix10 implementation and verification record |
| `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py` | Harness version `sim_fetch_01_harness_1238j.v0.1` |
| `ilc_core/graph/agent_graph_projection_runtime.py` | Phase 1229 fetch/incentive projection runtime |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 remains open |

---

## 3. SIM-FETCH-01 Findings

Phase 1238i evidence matrix:

```text
scenario_count = 48
pass = 38
needs_review = 2
fail = 8
recommendation = candidate_envelope_identified_for_governance_review
```

Phase 1238j robustness suite:

```text
profile_count = 4
accepted_profile_count = 4
total_scenario_count = 11
overall_robustness_verdict = pass
```

Key robustness results:

| Profile | Acceptance rule | Result | Max routed Tier A+B failure |
|---------|-----------------|--------|-----------------------------|
| `fresh_holder_directory_control` | `all_pass` | accepted | `0.000000` |
| `stale_directory_one_hop_negative_control` | `all_fail` | accepted | `0.425693` |
| `stale_directory_two_hop_rescue` | `all_pass` | accepted | `0.000000` |
| `low_holder_adaptive_recovery` | `any_pass` | accepted | `0.057935` |

Interpretation:

- Random single-hop peer selection is a diagnostic null model, not the CDL-087
  evaluative model.
- Routed holder-directory lookup is the correct base model for WANT-HAVE.
- A fully stale directory with one hop fails, and that negative control is
  valuable because it proves the evaluator can reject unsafe conditions.
- Two-hop retry and adaptive heat-driven replication are demonstrated recovery
  paths in the current harness.
- Tier C remains advisory because CDL-087 creates no infrastructure-grade Tier C
  service obligation.
- Werner overlay output remains non-authorizing: no ECU minting and no ILC
  settlement are authorized by SIM-FETCH.

---

## 4. Six Ratification Conditions

### Condition 1 — SIM-FETCH-01 passes

**Status:** satisfied for governance review; not alone sufficient for ratification.

Evidence:

- `sim_fetch_01_fix10_robustness_suite_1238j.v0.1`
- `overall_robustness_verdict = pass`
- negative control validated;
- two-hop retry and adaptive recovery validated;
- canonical JSON evidence committed.

Disposition:

```text
condition_1_sim_fetch_01_passed_for_governance_review
```

### Condition 2 — Tier A/B/C classification implemented and observable in a production-candidate serving peer

**Status:** open blocker.

SIM-FETCH implements and observes Tier A/B/C classification in the simulation
harness, but the prelock condition explicitly requires at least one
production-candidate serving peer.

Required next evidence:

- serving-peer runtime emits Tier A/B/C classification for actual artifacts;
- tests prove Tier A includes Genesis root artifacts, ADR-0004 truth primitives,
  accepted CDLs/ADRs, signed manifests, lineage receipts, CDL-086 release
  artifacts, bootstrap bundles, and epoch/checkpoint roots;
- no operator-local discretion can silently move required Tier A artifacts out
  of Tier A.

Disposition:

```text
condition_2_production_candidate_tier_classification_open
```

### Condition 3 — Bootstrap snapshot format implemented and Genesis-verifiable

**Status:** open blocker.

CDL-079 and node bootstrap code provide related bootstrap lineage/fetch
precedent, but CDL-087 prelock requires the specific bootstrap snapshot fields:

- `snapshot_manifest`
- `genesis_domain_hash`
- `snapshot_epoch`
- `artifact_list`
- `lineage_proof_chain`
- `epoch_checkpoint_range`
- `authority_refs`
- `graph_projection_export`

Required next evidence:

- concrete snapshot builder/exporter;
- verifier that recomputes artifact hashes and resolves lineage back to the
  immutable Genesis domain anchor;
- tests for malformed hash, wrong Genesis hash, missing authority refs, stale
  epoch range, and non-canonical JSON.

Disposition:

```text
condition_3_bootstrap_snapshot_format_open
```

### Condition 4 — Required observability signals emitted by a production-candidate serving peer and collected for one SIM window

**Status:** open blocker.

SIM-FETCH emits the CDL-087 Section 6 observability signals, plus routed/derived
metrics. The prelock condition requires at least one production-candidate serving
peer to emit and collect them for a SIM window.

Required next evidence:

- serving-peer observability surface emits the 12 Section 6 signals with exact
  names;
- epoch sequence is the time axis;
- no per-requester dossiers are produced;
- JSON is canonical (`sort_keys=True`, `allow_nan=False`);
- one SIM collection window artifact is committed.

Disposition:

```text
condition_4_production_candidate_observability_open
```

### Condition 5 — CDL-077 static rate limiter remains active

**Status:** satisfied as preservation evidence; should be re-verified in the
future ratification phase.

Evidence:

- CDL-077 remains ratified in the CDL register;
- persistent limiter backend and wiring were implemented in Phases 1202 and
  1212;
- SIM-FETCH keeps circuit-breaker metrics and rejects sustained overload
  envelopes;
- no CDL-077 amendment or unlimited fetch path was introduced in Phase 1238 or
  Window 1241-1245 work.

Required next evidence:

- run CDL-077 / persistent limiter focused regression in the later sensitive
  ratification evidence phase.

Disposition:

```text
condition_5_cdl_077_rate_limiter_preserved_pending_final_regression
```

### Condition 6 — Fetch incentive hypergraph slice resolved or explicitly deferred

**Status:** satisfied at projection level; serving-peer credit bridge evidence
available; should be re-verified in the future ratification phase.

Evidence:

- Phase 1229 exposes `fetch_incentive_hypergraph_slice`;
- projection distinguishes serving-peer identity from served-Graph-Node
  centrality;
- Phase 1238g credit bridge attributes serve credit to serving-peer/operator
  instances and rejects artifact-only crediting.

Disposition:

```text
condition_6_fetch_incentive_projection_resolved_at_projection_level
```

---

## 5. Remaining Ratification Blockers

CDL-087 ratification should not proceed until these blockers are closed:

```text
cdl_087_blocker_production_candidate_tier_classification_runtime
cdl_087_blocker_bootstrap_snapshot_builder_and_verifier
cdl_087_blocker_production_candidate_observability_collection_window
cdl_087_blocker_final_cdl_077_rate_limiter_regression
```

The first three are substantive implementation/evidence blockers. The fourth is
a final regression gate before any sensitive ratification phase.

---

## 6. Later Sensitive Ratification Phase Draft

If a future human explicitly authorizes a sensitive CDL-087 ratification evidence
phase, the prompt should require:

1. Re-read this disposition and the CDL-087 prelock.
2. Verify Conditions 1-6 against committed evidence.
3. Run Phase 1238 SIM-FETCH focused tests and CDL-077 limiter regressions.
4. Verify production-candidate Tier A/B/C classification runtime.
5. Verify bootstrap snapshot builder/exporter/verifier.
6. Verify one observability collection window from a production-candidate
   serving peer.
7. Mutate the CDL register only if all six conditions pass.

Required sensitive gate token:

```text
GO CDL-087 ratification evidence phase
```

---

## 7. Non-Authorization Boundary

This Phase 1246 disposition does not authorize:

- CDL-087 ratification;
- CDL-088 opening;
- CDL register mutation;
- production fetch caching implementation;
- public sidecar/projection endpoint;
- Werner ECU minting;
- ILC settlement;
- public P2P;
- public RC claim;
- public repository publication;
- release-key generation;
- v0.2 signing.
