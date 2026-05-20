# ILC CDL-053 Werner Local Productive Credit Ratification Evidence 1407-Fix2 v0.1

Phase: 1407-Fix2
Date: 2026-05-20
Status: ratification evidence committed; CDL register mutation occurs in a separate commit

Required tokens:

```text
cdl_053_ratified_phase_1407_fix2
cdl_053_ratification_evidence_committed
cdl_053_historical_hardening_fix0_ref_asserted
```

## 1. Ratification Summary

Phase 1407-Fix2 ratifies the Phase 1407-Fix1 CDL-053 prelock constants for a
narrow Werner local productive-credit lane. The ratified scope is
review-lane-passed maintenance-equivalent productive work only. The local credit
unit is not settlement-grade ECU, not wallet-visible, and not transferable.

CDL-053 ratification does not activate ECU creation, direct Werner ECU creation,
ILC settlement, wallet mutation, live distribution, maintenance lottery
activation, flow-governor activation, or any heat-to-ECU signal.

## 2. Evidence Inputs

| Input | Phase 1407-Fix2 use |
|-------|---------------------|
| `docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md` | Confirms CDL-053 opened the Werner local productive-credit lane and recorded Q1-Q4 |
| `docs/specs/ilc_cdl_053_werner_local_productive_credit_prelock_1407_fix1_v0.1.md` | Supplies the full scope-constant set ratified here |
| `docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md` | Preserves direct Werner ECU creation rejection and the un-opened flow-governor path |
| `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` | Supplies inherited `EDGE_MINT_PHI_BOUND = Decimal("0.60")` for provenance-equivalent edge-mint outputs |
| `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` | Supplies J-005 maintenance task classes and review-lane reward-eligibility boundary |

## 3. Ratified Scope Constants

The following constants are ratified explicitly from the Phase 1407-Fix1 prelock.
This section intentionally does not use "see prelock" shorthand.

| Constant | Ratified value |
|----------|----------------|
| `WERNER_PRODUCTIVE_WORK_SCOPE` | `review_lane_passed_maintenance_tasks_only` |
| `WERNER_PRODUCTIVE_WORK_TASK_CLASSES` | `star.map.embedding; contradiction.sweep; graph.compression; stability.simulation; custom_review_lane_assigned` |
| `WERNER_NON_MAINTENANCE_PRODUCTIVE_CREDIT_SCOPE` | `deferred_to_future_cdl_053_amendment_or_separate_authority` |
| `WERNER_LOCAL_CREDIT_UNIT_DESIGNATION` | `local_productive_credit` |
| `WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE` | `false` |
| `WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE` | `false` |
| `WERNER_LOCAL_CREDIT_IS_TRANSFERABLE` | `false` |
| `WERNER_SETTLEMENT_GATE` | `consensus_epoch_public_economics_gate_and_j008_production_activation` |
| `WERNER_SETTLEMENT_REQUIRES_CONSENSUS_EPOCH` | `true` |
| `WERNER_EDGE_MINT_PHI_BOUND_INHERITED` | `cdl_085_decimal_0_60` |
| `WERNER_EDGE_MINT_PHI_BOUND_VALUE` | `Decimal("0.60")` |
| `WERNER_PHI_BOUND_APPLIES_TO` | `provenance_equivalent_edge_mint_outputs_only` |
| `WERNER_DIRECT_HEAT_TO_ECU_MINTING` | `not_authorized` |
| `WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false` |
| `WERNER_FLOW_GOVERNOR_SCOPE_AUTHORIZED` | `false` |
| `WERNER_LOCAL_CREDIT_ANTI_GAMING_CONTROLS` | `review_lane_pass_required; content_addressed_task_id_required; canonical_task_descriptor_hash_required; duplicate_task_id_rejected; duplicate_output_hash_collapsed; one_credit_per_agent_per_epoch; author_reviewer_conflict_checks_required; operator_domain_conflict_checks_required; no_settlement_grade_ecu_without_conversion_gate; no_wallet_mutation; no_direct_heat_to_ecu_minting; no_live_distribution_before_j008_pass_and_production_go` |
| `WERNER_WALLET_MUTATION_AUTHORIZED` | `false` |
| `WERNER_ILC_SETTLEMENT_AUTHORIZED` | `false` |
| `WERNER_LIVE_DISTRIBUTION_AUTHORIZED` | `false` |
| `WERNER_MAINTENANCE_CREDIT_ELIGIBLE` | `true` |
| `WERNER_MAINTENANCE_LOTTERY_SOURCE_CANDIDATE` | `cdl_053_werner_local_productive_credit` |
| `WERNER_CDL_093_AMENDMENT_REQUIRED_BEFORE_USE` | `true` |

## 4. Ratified Task-Class Semantics

| Task class | Ratified CDL-053 treatment |
|------------|----------------------------|
| `star.map.embedding` | Eligible after review-lane pass; CDL-085 phi-bound applies when the reviewed output is provenance-equivalent graph derivation or edge-mint expansion |
| `contradiction.sweep` | Eligible after review-lane pass; CDL-085 phi-bound applies when the reviewed output is provenance-equivalent contradiction/provenance work |
| `graph.compression` | Eligible after review-lane pass; default filter is structural-quality audit plus duplicate-collapse controls, not CDL-085 |
| `stability.simulation` | Eligible after review-lane pass; default filter is simulation reproducibility, parameter provenance, and review-lane audit, not CDL-085 |
| `custom_review_lane_assigned` | Eligible only when the task definition assigns a review lane and the reviewed output passes that lane; CDL-085 applies only if the assigned lane classifies the output as provenance-equivalent |

## 5. Historical Hardening

Fix0 C2 commit hash obtained from `docs/phases/STATUS.md`:

```text
36d3b698
```

Command:

```bash
git show 36d3b698:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-053 \\|"
```

Result: CDL-053 is present with `status: open`, `opened_phase: 1407_fix0`, and
`opening_token: cdl_053_werner_local_productive_credit_opened_phase_1407_fix0`.

```text
cdl_053_historical_hardening_fix0_ref_asserted
```

## 6. Phase 1263 Non-Overlap

Phase 1407-Fix2 preserves:

```text
direct_werner_ecu_creation_rejected_phase_1263
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
```

CDL-053 ratifies a local productive-credit lane, not the Werner flow-governor
path. It does not authorize heat-to-ECU minting, topology-pressure-to-ECU
minting, per-request tolls, per-hop micropayments, wallet withdrawal/transfer/
spend, ILC settlement, public claimability, public serving, or live distribution.

## 7. Non-Authorization Paragraph

Ratification does not authorize:

- ECU minting;
- direct Werner ECU creation;
- heat-to-ECU signal activation;
- ILC settlement;
- wallet mutation;
- wallet withdrawal, transfer, or spend;
- live distribution;
- maintenance lottery activation;
- flow-governor activation;
- treasury drawdown;
- public claimability;
- J-008 gate verdict change;
- runtime mutation.

## 8. CDL Register Mutation Boundary

The CDL register mutation must occur in a separate commit using:

```bash
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1407_fix2
```

The mutation changes only the CDL-053 row from `open` to `ratified` and adds:

```text
ratified_phase: 1407_fix2
ratified_date: 2026-05-20
ratification_token: cdl_053_ratified_phase_1407_fix2
evidence_document: docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md
```

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md -> constitutional/cdl
```
