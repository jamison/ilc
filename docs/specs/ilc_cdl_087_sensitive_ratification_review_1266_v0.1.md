# ILC CDL-087 Sensitive Ratification Review 1266 v0.1

**Date:** 2026-05-08
**Phase:** 1266
**Status:** Sensitive review decision packet; no ratification and no register mutation
**Human authorization:** `GO Phase 1266`
**Window lock:** `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md`

```text
cdl_087_sensitive_ratification_review_phase_1266.v0.1
cdl_087_ratification_decision_recorded_phase_1266
cdl_087_ratification_not_executed_by_default_phase_1266
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266
no_public_fetch_serving_enabled_phase_1266
```

## 1. Decision Verdict

Phase 1266 records the CDL-087 sensitive ratification review decision:

```text
cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation
```

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
```

The reason is procedural and safety-critical. The human instruction was
`GO Phase 1266`, which authorizes the sensitive review phase. It was not an
explicit authorization to ratify CDL-087 or mutate the CDL register. The Phase
1265-1272 sequence lock requires the default Phase 1266 path to record review,
no ratification, and no register mutation unless future human scope explicitly
authorizes ratification and proves all six locked conditions.

This is not an explicit authorization to ratify CDL-087.

This phase therefore records:

```text
cdl_087_ratification_not_executed_by_default_phase_1266
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266
```

## 2. Evidence Basis

| Source | Phase 1266 read |
|--------|-----------------|
| `docs/PLANNING_INDEX.md` | Current frontier before Phase 1266 was Window 1265-1272 open/pass through Phase 1265 and Phase 1266 sensitive gated. |
| `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md` | Phase 1266 must not ratify CDL-087 or mutate the register by default. |
| `docs/specs/ilc_window_1265_1272_candidate_phase_grouping_v0.1.md` | Phase 1266 is a sensitive ratification review and decision packet with no register mutation by default. |
| `docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md` | Phase 1259/1260 local evidence supports later sensitive review; CDL-087 remains open/prelocked/not ratified. |
| `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md` | CDL-087 was opened, not ratified. |
| `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` | Q1-Q5 were prelocked and six ratification conditions were set. |
| `docs/specs/ilc_cdl_087_production_candidate_evidence_readiness_1258_v0.1.md` | Conditions 1-6 were reconciled; Phase 1258 did not ratify. |
| `docs/specs/ilc_cdl_087_serving_peer_evidence_slice_1259_v0.1.md` | Conditions 2 and 3 have local serving-peer evidence and no public fetch serving. |
| `docs/specs/ilc_cdl_087_observability_and_limiter_regression_1260_v0.1.md` | Conditions 4 and 5 have local evidence; readiness verdict is later sensitive review, not ratification. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 register row remains `open`; no Phase 1266 mutation is made. |
| `ilc_core/network/d2d/cdl087_serving_peer_evidence.py` | Local helper is pure, bounded, canonical-JSON based, and has no public server/socket surface. |
| `ilc_core/network/d2d/cdl087_observability.py` | Local helper uses protocol epoch sequence, rejects per-requester dossiers, rejects floats, and preserves limiter evidence. |

## 3. Discovery Audit

Exact-token `rg` was used only as a schema and completion check. Before this
decision, exact searches found Phase 1266 tokens only in the prompt and prior
forward-planning/sequence-lock material, which is expected before the new
artifact exists.

Concept discovery also searched and direct-read around:

```text
CDL-087
ratification
prelock
Condition 1
Condition 2
Tier A
bootstrap snapshot
observability
CDL-077
limiter
fetch incentive
credit bridge
serving peer
Graph Node
WANT-HAVE
WANT-BLOCK
```

Contradiction and boundary discovery searched:

```text
not ratified
ratification deferred
not authorized
review-only
blocked
local-only
no public
no production fetch serving
no sidecar
no P2P
must not
no ratification
register mutation
```

The broad searches reinforced the same boundary: the repo has local
production-candidate evidence for later review, while ratification, CDL register
mutation, public fetch serving, public sidecar/projection serving, and public
P2P remain unauthorized.

## 4. Condition Review Table

| CDL-087 condition | Phase 1266 review disposition |
|-------------------|-------------------------------|
| 1. SIM-FETCH-01 passes | Satisfied for governance review from the Phase 1238i/1238j evidence chain and preserved through Phase 1258. This is evidence input, not a standalone ratification act. |
| 2. Tier A/B/C classification in a production-candidate serving peer | Local evidence recorded in Phase 1259 via `production_candidate_tier_classification_runtime_evidence_recorded_phase_1259`. Sufficiency for ratification is not executed without explicit ratification authorization. |
| 3. Bootstrap snapshot format implemented and Genesis-verifiable | Local builder/verifier evidence recorded in Phase 1259 via `bootstrap_snapshot_builder_verifier_evidence_recorded_phase_1259`. Sufficiency for ratification is not executed without explicit ratification authorization. |
| 4. Required observability signals collected for one SIM window | Local collection-window evidence recorded in Phase 1260 via `cdl_087_observability_collection_window_phase_1260.v0.1`; the helper uses protocol epoch sequence and no per-requester dossiers. |
| 5. CDL-077 limiter remains active and unmodified | Final local limiter regression recorded in Phase 1260 via `cdl_077_rate_limiter_final_regression_recorded_phase_1260`; no unlimited fetch path is authorized. |
| 6. Fetch-incentive projection / credit bridge | Projection-level evidence remains satisfied from prior Phase 1229/1238g/1258 chain and must be rechecked by any future explicit ratification phase. |

The review conclusion is:

```text
cdl_087_conditions_1_to_6_reviewed_no_ratification_phase_1266
```

## 5. CDL Register Diff Disposition

The CDL register is intentionally not mutated.

Disposition:

```text
cdl_087_register_diff_disposition_phase_1266=clean_no_mutation
```

Expected verification:

```bash
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
```

Expected output: empty diff.

No CDL row is added, no CDL row status changes, CDL-087 remains open, and no
ratified-phase marker is added.

## 6. Public Path Boundary

Phase 1266 does not enable public fetch serving:

```text
no_public_fetch_serving_enabled_phase_1266
```

Public/non-loopback sidecar projection serving also remains blocked because
CDL-087 is still not ratified and TransportPrincipal runtime/public-path policy
is still unfinished.

## 7. Carry-Forward Requirements

A future CDL-087 ratification attempt requires a new explicit human
authorization that widens scope beyond review. That future phase must:

1. State that CDL-087 ratification and CDL register mutation are authorized.
2. Re-read the opening, prelock, Phase 1258 readiness packet, Phase 1259 serving
   peer evidence, Phase 1260 observability/limiter packet, and current CDL
   register.
3. Prove all six ratification conditions or record an explicit narrower safe
   deferral.
4. Keep a clean, reviewable CDL register diff.
5. Preserve public fetch, public P2P, public sidecar/projection, public RC,
   claimability, ECU minting, ILC settlement, and v0.2 signing non-claims unless
   separately authorized.

Carry-forward tokens:

```text
cdl_087_future_ratification_requires_explicit_human_authorization
cdl_087_conditions_1_to_6_must_be_reproved_before_ratification
cdl_087_public_fetch_serving_still_blocked_after_phase_1266
sidecar_public_path_still_requires_cdl087_and_transport_principal_after_phase_1266
```

## 8. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md -> planning/cdl087
graph_delta=support_tests_added:tests/test_phase_1266_cdl087_sensitive_ratification_review.py -> validation
graph_delta=support_only:docs/phases/phase_1266_cdl087_sensitive_ratification_review_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 9. Non-Claims

Phase 1266 does not authorize:

- CDL-087 ratification;
- CDL register mutation;
- CDL-088 opening;
- public fetch serving;
- public sidecar/projection serving;
- public P2P exposure;
- non-loopback endpoint exposure;
- TransportPrincipal runtime activation;
- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- public claimability activation;
- wallet withdrawal, transfer, or spend semantics;
- ECU mint authorization;
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.

## 10. Next Phase

Phase 1267 is the next locked phase and is non-sensitive unless widened to
public exposure:

```text
phase_1267_transport_principal_runtime_identity_pre_public_path_next
```
