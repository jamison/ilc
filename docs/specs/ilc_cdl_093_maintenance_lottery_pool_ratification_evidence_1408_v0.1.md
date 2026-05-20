# ILC CDL-093 Maintenance Lottery Pool Ratification Evidence 1408 v0.1

Phase: 1408
Date: 2026-05-20
Status: ratification evidence committed; CDL register mutation occurs in a separate commit

Required tokens:

```text
cdl_093_ratified_phase_1408
cdl_093_ratification_evidence_committed
cdl_093_historical_hardening_phase_1406_ref_asserted
maintenance_lottery_activation_not_authorized_phase_1408
```

## 1. Ratification Summary

Phase 1408 ratifies CDL-093, the maintenance lottery pool distribution lane for
low-capability agents after reviewed maintenance-task contribution. The
ratified constants are the Phase 1407 prelock constants, with the four Phase
1407-Fix3 Q2 amendments replacing the original CDL-047 treasury-source values.

The ratified Q2 funding source is ratified CDL-053 Werner local productive
credit:

```text
cdl_053_ratified_phase_1407_fix2
cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3
maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3
```

Phase 1408 ratification does not activate maintenance lottery distribution,
live draws, ECU distribution, ECU settlement, ECU minting, ILC settlement,
wallet mutation, runtime behavior, public claimability, or a J-008 gate verdict
change.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-093 is open before Phase 1408 mutation | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-093` | confirmed |
| Phase 1407 prelock scope constants exist | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md` | confirmed |
| Phase 1407-Fix3 amendment exists and sets Werner source | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md` | confirmed |
| CDL-053 is ratified before CDL-093 ratification | CDL register row `CDL-053`; `docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md` | confirmed |
| Q2 SIM resolved pending flag to false | Fix3 amendment and SIM docs | confirmed |
| Phase 1406 C2 commit hash is obtainable | `docs/phases/STATUS.md`; sequence lock | confirmed: `15992abe` |
| No source runtime exists yet | `ilc_core/epistemic/maintenance_lottery_runtime.py` filesystem check | confirmed |
| J-008 still records `MAINTENANCE_LOTTERY_CDL_RATIFIED` as NOT_MET | `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| MemPalace advisory retrieval added no new canonical source | tier A query plus direct repo reads | confirmed |

## 3. Evidence Inputs

| Input | Phase 1408 use |
|-------|----------------|
| `docs/specs/ilc_cdl_093_maintenance_lottery_pool_opening_1406_v0.1.md` | CDL-093 opening scope and Q1-Q5 deliberation questions |
| `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md` | Original prelock constants, except the four Q2 constants amended by Fix3 |
| `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md` | Amended Q2 source/path/SIM/fraction constants |
| `docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md` | Ratified Werner local productive-credit source |
| `docs/sims/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3_v0.1.md` | Q2 funding fraction SIM; recommended `Decimal("0.10")` |
| `out/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3.json` | Machine-readable deterministic SIM output |
| `ilc_core/epistemic/jury_activation_gate.py` | J-008 condition context and non-flip boundary |

## 4. Ratified Scope Constants

The following constants are ratified explicitly. This section intentionally does
not use "see prelock" shorthand.

| Constant | Ratified value |
|----------|----------------|
| `MAINTENANCE_LOTTERY_DRAW_MECHANISM` | `production_vrf_or_later_ratified_randomness_required` |
| `MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM` | `epoch_hash_shadow_quote_only` |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE` | `cdl_053_werner_local_productive_credit` |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION` | `Decimal("0.10")` |
| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | `false` |
| `MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM` | `true` |
| `MAINTENANCE_LOTTERY_TASK_ELIGIBILITY_MODE` | `review_lane_passed_maintenance_tasks_only` |
| `MAINTENANCE_LOTTERY_MIN_CONTRIBUTION_THRESHOLD` | `one_review_lane_passed_maintenance_task_per_epoch` |
| `MAINTENANCE_LOTTERY_ELIGIBLE_TASK_CLASSES` | `star.map.embedding; contradiction.sweep; graph.compression; stability.simulation; custom_review_lane_assigned` |
| `MAINTENANCE_LOTTERY_ENTRY_UNIT` | `one_entry_per_review_lane_passed_task` |
| `MAINTENANCE_LOTTERY_ENTRY_CAP_PER_AGENT_PER_EPOCH` | `one` |
| `MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS` | `review_lane_pass_required`; `content_addressed_task_id_required`; `duplicate_task_id_rejected`; `duplicate_output_hash_collapsed`; `difficulty_factor_not_reward_input`; `one_entry_per_agent_per_epoch`; `author_reviewer_conflict_checks_required`; `same_operator_domain_diversity_check_required_before_production`; `no_unreviewed_task_reward`; `no_live_distribution_before_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH` | `cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub` |
| `MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY` | `epoch_boundary_batch_quote_only_until_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_DIRECT_ILC_REWARD_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT` | `not_activated` |
| `MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_RUNTIME_PHASE` | `phase_1409_default_off_stub_only` |
| `MAINTENANCE_LOTTERY_GATE_FLIP_PHASE` | `phase_1427_after_phase_1425_verification` |

## 5. Amended Q2 Disposition

Phase 1407-Fix3 supersedes the Phase 1407 CDL-047 treasury candidate for Q2.
The ratified source is local, bottom-up productive-credit attribution under
CDL-053, not a global treasury drawdown.

| Q2 item | Ratified disposition |
|---------|----------------------|
| Source | `cdl_053_werner_local_productive_credit` |
| Distribution path | `cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub` |
| SIM-pending flag | `false` |
| Funding fraction | `Decimal("0.10")` |

The Fix3 SIM remains non-activating and does not authorize live distribution.

## 6. Historical Hardening

Phase 1406 C2 commit hash obtained from `docs/phases/STATUS.md`:

```text
15992abe
```

Command:

```bash
git show 15992abe:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-093 \\|"
```

Result: CDL-093 is present with `status: open`, `opened_phase: 1406`,
`opening_token: cdl_093_maintenance_lottery_pool_opened_phase_1406`, and
`ratification_status: not_ratified_pending_phase_1408`.

```text
cdl_093_historical_hardening_phase_1406_ref_asserted
```

## 7. J-008 Boundary

`ilc_core/epistemic/jury_activation_gate.py` still hardcodes the condition
`MAINTENANCE_LOTTERY_CDL_RATIFIED` as `NOT_MET` before any later gate logic
update. Phase 1408 does not flip J-008.

The current J-008 token remains historical until a later gate verification phase
updates or re-evaluates the condition:

```text
maintenance_lottery_cdl_not_opened_phase_j008
```

## 8. Non-Authorization Paragraph

```text
maintenance_lottery_activation_not_authorized_phase_1408
```

Ratification does not authorize:

- maintenance lottery activation;
- live lottery draws;
- ECU distribution;
- ECU settlement;
- ECU minting;
- ILC settlement;
- wallet mutation;
- wallet withdrawal, transfer, or spend;
- runtime activation;
- public claimability;
- J-008 gate verdict change;
- production jury activation.

## 9. CDL Register Mutation Boundary

The CDL register mutation must occur in a separate commit using:

```bash
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1408
```

The mutation changes only the CDL-093 row from `open` to `ratified` and adds:

```text
ratified_phase: 1408
ratified_date: 2026-05-20
ratification_token: cdl_093_ratified_phase_1408
evidence_document: docs/specs/ilc_cdl_093_maintenance_lottery_pool_ratification_evidence_1408_v0.1.md
```

## 10. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_093_maintenance_lottery_pool_ratification_evidence_1408_v0.1.md -> constitutional/cdl
```
