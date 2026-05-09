# ILC CDL-087 Ratification Evidence 1278 Fix1 v0.1

**Date:** 2026-05-09
**Phase:** 1278 Fix1
**Status:** CDL-087 ratified; CDL register mutated
**Human authorization:** `GO Phase 1278 Fix1. I authorize CDL-087 ratification and CDL register mutation`
**Window lock:** `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md`

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

## 1. Decision Verdict

Phase 1278 Fix1 consumes explicit human authorization to ratify CDL-087 and
mutate the CDL register. The authorization is narrow. It authorizes the
constitutional status change for CDL-087 only.

Verdict:

```text
cdl087_ratification_decision_phase_1278_fix1=ratify_and_mutate_register
cdl087_register_diff_disposition_phase_1278_fix1=cdl087_open_to_ratified
cdl087_public_path_disposition_phase_1278_fix1=governance_blocker_cleared_runtime_activation_blocked
```

CDL-087 is now:

```text
RATIFIED
```

The CDL register row `CDL-087` has been changed from `open` to `ratified` and
now records:

```text
ratified_phase: 1278 Fix1
ratified_date: 2026-05-09
ratification_token: cdl087_ratified_phase_1278_fix1
register_mutation_token: cdl087_register_mutated_phase_1278_fix1
evidence_document: docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md
```

## 2. Direct-Read Evidence Basis

| Source | Ratification use |
|--------|------------------|
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Current mutable CDL register; CDL-087 row mutated by this Fix1 only. |
| `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md` | Opening authority and canonical-fetch policy scope. |
| `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` | Locked Q1-Q5 policy decisions and six ratification conditions. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_evidence_matrix_1238i_v0.1.md` | SIM-FETCH-01 evidence matrix for Condition 1. |
| `docs/sims/sim_fetch_01/sim_fetch_01_cdl_087_robustness_suite_1238j_v0.1.md` | Robustness and negative-control evidence for Condition 1. |
| `docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md` | Conditions 1-6 reconciliation and blocker routing. |
| `docs/specs/ilc_cdl_087_serving_peer_evidence_slice_1259_v0.1.md` | Local production-candidate Tier A/B/C and bootstrap snapshot builder/verifier evidence for Conditions 2 and 3. |
| `docs/specs/ilc_cdl_087_observability_and_limiter_regression_1260_v0.1.md` | One SIM-window observability evidence and CDL-077 limiter regression for Conditions 4 and 5. |
| `docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md` | Prior sensitive review and explicit future-authorization requirements. |
| `docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md` | Fresh preflight proof that Conditions 1-6 were ready for explicitly authorized ratification. |
| `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md` | Public-path dependency preflight; no public P2P or fetch serving activation. |
| `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md` | Sidecar public-path dependency preflight; no listener, non-loopback bind, or public serving activation. |
| `ilc_core/network/d2d/cdl087_serving_peer_evidence.py` | Local evidence helper for Conditions 2 and 3; no public server or socket surface. |
| `ilc_core/network/d2d/cdl087_observability.py` | Local evidence helper for Conditions 4 and 5; protocol epoch sequence, no floats, no per-requester dossiers. |
| `ilc_core/graph/agent_graph_projection_runtime.py` | Machine-visible fetch incentive slice evidence for Condition 6. |

Evidence tokens consumed:

```text
sim_fetch_01_cdl_087_robustness_suite_1238j
cdl_087_production_candidate_evidence_readiness_phase_1258.v0.1
production_candidate_tier_classification_runtime_evidence_recorded_phase_1259
bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259
cdl_087_observability_collection_window_phase_1260.v0.1
cdl_077_rate_limiter_final_regression_recorded_phase_1260
cdl087_conditions_1_to_6_preflighted_no_ratification_phase_1276
```

## 3. Discovery Audit

Exact-token `rg` was used only as a schema and completion check. Fix1 also
searched and direct-read broader concepts around:

```text
CDL-087
canonical fetch
ratification
register mutation
prelock
SIM-FETCH-01
Tier A
Tier B
Tier C
bootstrap snapshot
Genesis lineage
observability
CDL-077 limiter
fetch incentive
credit bridge
serving peer
Graph Node
public fetch
public sidecar
public projection
CDL-088
```

Contradiction and non-claim discovery searched:

```text
not ratified
no ratification
no register mutation
not authorized
blocked
deferred
local-only
no public fetch
no listener
no non-loopback
no public RC
no release artifact
no v0.2 signing
```

The contradiction search found only historical non-ratification records before
this Fix1 and current public-path blocks that remain valid after ratification.

## 4. Six-Condition Ratification Proof

| CDL-087 condition | Fix1 proof |
|-------------------|------------|
| 1. SIM-FETCH-01 passes | Satisfied by Phase 1238i evidence matrix and Phase 1238j robustness suite, preserved through Phase 1258. Random single-hop probing remains a pessimistic null model, not the CDL-087 architecture. |
| 2. Tier A/B/C classification in a production-candidate serving peer | Satisfied by Phase 1259 local production-candidate evidence with `production_candidate_tier_classification_runtime_evidence_recorded_phase_1259`. |
| 3. Bootstrap snapshot format implemented and Genesis-verifiable | Satisfied by Phase 1259 builder/verifier evidence with `bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259`. |
| 4. Required observability signals collected for one SIM window | Satisfied by Phase 1260 local collection-window evidence with `cdl_087_observability_collection_window_phase_1260.v0.1`; output is aggregate and privacy-minimized. |
| 5. CDL-077 limiter remains active and unmodified | Satisfied by Phase 1260 final limiter regression with `cdl_077_rate_limiter_final_regression_recorded_phase_1260`; no unlimited fetch path is authorized. |
| 6. Fetch-incentive projection / credit bridge | Satisfied at projection level by the Phase 1229/1238g/1258 chain and rechecked by Phase 1276. The agent graph projection exposes a fetch incentive slice and distinguishes serving-peer evidence from served-Graph-Node content. |

Ratification proof token:

```text
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
```

## 5. Selected Constitutional Effect

CDL-087 now constitutionalizes canonical fetch distribution policy as public
verifiable infrastructure:

- Tier A/B/C artifact classification is ratified as the canonical fetch
  distribution structure.
- Content validity is by content hash plus Genesis-lineage proof, not requester
  identity.
- Genesis-verifiable bootstrap snapshots are a ratified distribution primitive.
- Mandatory observability remains aggregate and privacy-minimized.
- CDL-077 circuit breakers and limiter constraints remain active.
- Fetch incentives are recognized through the projection-level
  serving-peer/served-Graph-Node distinction.

This ratification does not make a public serving endpoint safe by itself. It
removes the governance blocker that previously prevented later public-path work
from treating CDL-087 as ratified.

## 6. Register Mutation

The only CDL register mutation authorized and executed by this Fix1 is:

```text
CDL-087 status: open -> ratified
```

The mutation also adds the ratification evidence refs and explicit public-path
non-activation fields to the row.

No new CDL row is opened. CDL-088 remains unopened.

## 7. Public Path and Release Boundary

The following remain blocked after CDL-087 ratification:

```text
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
public_rc_remains_blocked_after_phase_1278_fix1
```

Phase 1278 Fix1 does not authorize:

- public fetch serving;
- public sidecar/projection serving;
- non-loopback sidecar/projection serving;
- wildcard bind or public host bind;
- new listener;
- public P2P exposure;
- public claimability API activation;
- wallet withdrawal, transfer, or spend semantics;
- ECU mint authorization;
- ILC settlement or withdrawal runtime activation;
- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- release-key generation;
- release envelope production;
- public release artifact production;
- CDL-088 opening;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- production `commit.epoch` emission.

## 8. Graph Delta

```text
graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl087
graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md -> governance/cdl087
graph_delta=support_tests_added:tests/test_phase_1278_fix1_cdl087_ratification.py -> validation
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1278_fix1_cdl087_ratification_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 9. Verification Plan

Expected verification:

```bash
.venv/bin/python -m pytest tests/test_phase_1278_fix1_cdl087_ratification.py
.venv/bin/python -m pytest tests/test_window_1273_1280_prompt_drafts.py tests/test_phase_1276_cdl087_ratification_authorization_preflight.py tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff --check -- docs/specs/ilc_constitutional_decision_log_v0.1.md docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md docs/phases/phase_1278_fix1_cdl087_ratification_walkthrough.md docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md tests/test_phase_1278_fix1_cdl087_ratification.py
```

## 10. Next Phase

Phase 1279 remains the next locked non-sensitive inventory phase unless a later
human instruction widens authority:

```text
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
```
