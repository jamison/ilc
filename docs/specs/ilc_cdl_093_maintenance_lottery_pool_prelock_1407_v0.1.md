# ILC CDL-093 Maintenance Lottery Pool Prelock 1407 v0.1

Phase: 1407
Date: 2026-05-20
Status: prelock committed; CDL-093 open and not ratified

Required tokens:

```text
cdl_093_deliberation_complete_phase_1407
cdl_093_not_ratified_phase_1407
cdl_093_candidate_prelock_constants_recorded_phase_1407
cdl_093_prelock_committed_phase_1407
cdl_093_scope_constants_locked_phase_1407
```

## 1. Purpose

Phase 1407 resolves the Phase 1406 CDL-093 deliberation questions and locks the
scope constants that Phase 1408 may ratify. CDL-093 governs the maintenance
lottery pool lane for low-capability agents after reviewed maintenance-task
contribution.

This phase does not ratify CDL-093, mutate the constitutional decision log,
create runtime code, activate maintenance lottery distribution, execute live
draws, settle ECU, or change the J-008 gate verdict.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-093 is open after Phase 1406 | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-093` | confirmed |
| Phase 1406 opening doc is present with Q1-Q4 | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_opening_1406_v0.1.md` | confirmed |
| ADR-0040 establishes the VRF/epoch-hash boundary relevant to Q1 | `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` | confirmed |
| No maintenance lottery runtime exists | filesystem search for `ilc_core/**maintenance_lottery_runtime.py` | confirmed |
| J-005 does not resolve Q1-Q4 | `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` section 6 | confirmed |
| CDL-047 treasury governance is ratified | CDL register row `CDL-047`; `ilc_core/epoch/treasury_governance_runtime.py` | confirmed |
| Phase 1406 C2 historical row has CDL-093 open | `git show 15992abe:docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |

## 3. Q1 Resolution - Lottery Draw Mechanism

Resolution:

```text
MAINTENANCE_LOTTERY_DRAW_MECHANISM = production_vrf_or_later_ratified_randomness_required
MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM = epoch_hash_shadow_quote_only
```

Rationale: ADR-0040 allows deterministic epoch-hash assignment for
pre-production, testnet, public-RC shadow, and non-value-bearing harness lanes.
It requires VRF or another later-ratified randomness source for production
high-value review lanes, private assignment, value-bearing public
canonicalization, or any claim of strategic unpredictability.

A live maintenance lottery distributes ECU, so Phase 1407 does not bless
epoch-hash as production randomness. Epoch-hash may be used only for transparent
shadow quotes and non-value harnesses until a VRF or later-ratified randomness
source is available.

## 4. Q2 Resolution - Pool Budget Source and Funding Fraction

Resolution:

```text
MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE = cdl_047_treasury_governance_quote_candidate
MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal("0.00")
MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM = true
MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM = true
```

Rationale: CDL-047 is the ratified treasury governance framework and Phase 1348
implements a default-off quote runtime. No ratified simulation currently
calibrates a nonzero maintenance-lottery pool fraction. Therefore the prelock
uses CDL-047 treasury-governance quote authority as the source family, but locks
the live fraction to `Decimal("0.00")` until a future SIM or governance phase
ratifies a nonzero allocation.

This is intentionally conservative. It lets Phase 1408 ratify the lane and the
funding source boundary without silently authorizing live ECU distribution.

## 5. Q3 Resolution - Task Eligibility and Anti-Gaming Controls

Resolution:

```text
MAINTENANCE_LOTTERY_TASK_ELIGIBILITY_MODE = review_lane_passed_maintenance_tasks_only
MAINTENANCE_LOTTERY_MIN_CONTRIBUTION_THRESHOLD = one_review_lane_passed_maintenance_task_per_epoch
MAINTENANCE_LOTTERY_ELIGIBLE_TASK_CLASSES = star.map.embedding, contradiction.sweep, graph.compression, stability.simulation, custom_review_lane_assigned
MAINTENANCE_LOTTERY_ENTRY_UNIT = one_entry_per_review_lane_passed_task
MAINTENANCE_LOTTERY_ENTRY_CAP_PER_AGENT_PER_EPOCH = one
```

Only maintenance tasks that pass the applicable review lane may enter the pool.
The architectural `rewarded` task state remains non-live until later runtime and
gate authority exists.

Anti-gaming controls:

```text
MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS =
  review_lane_pass_required;
  content_addressed_task_id_required;
  duplicate_task_id_rejected;
  duplicate_output_hash_collapsed;
  difficulty_factor_not_reward_input;
  one_entry_per_agent_per_epoch;
  author_reviewer_conflict_checks_required;
  same_operator_domain_diversity_check_required_before_production;
  no_unreviewed_task_reward;
  no_live_distribution_before_j008_pass_and_production_go
```

## 6. Q4 Resolution - ECU Distribution Path and Settlement Boundary

Resolution:

```text
MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH = cdl_047_treasury_quote_to_phase_1409_default_off_runtime_stub
MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY = epoch_boundary_batch_quote_only_until_j008_pass_and_production_go
MAINTENANCE_LOTTERY_DIRECT_ILC_REWARD_ALLOWED = false
MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT = not_activated
MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED = false
MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED = false
MAINTENANCE_LOTTERY_RUNTIME_PHASE = phase_1409_default_off_stub_only
MAINTENANCE_LOTTERY_GATE_FLIP_PHASE = phase_1427_after_phase_1425_verification
```

The intended distribution path is CDL-047 treasury quote authority into a
dedicated Phase 1409 default-off runtime stub. Settlement is epoch-boundary
batch-shaped, but quote-only until CDL-093 ratification, default-off runtime,
J-008 gate re-run, and production GO all exist.

## 7. Scope Constants Locked

```text
cdl_093_scope_constants_locked_phase_1407
```

| Constant | Prelocked value |
|----------|-----------------|
| `MAINTENANCE_LOTTERY_DRAW_MECHANISM` | `production_vrf_or_later_ratified_randomness_required` |
| `MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM` | `epoch_hash_shadow_quote_only` |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE` | `cdl_047_treasury_governance_quote_candidate` |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION` | `Decimal("0.00")` |
| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | `true` |
| `MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM` | `true` |
| `MAINTENANCE_LOTTERY_TASK_ELIGIBILITY_MODE` | `review_lane_passed_maintenance_tasks_only` |
| `MAINTENANCE_LOTTERY_MIN_CONTRIBUTION_THRESHOLD` | `one_review_lane_passed_maintenance_task_per_epoch` |
| `MAINTENANCE_LOTTERY_ELIGIBLE_TASK_CLASSES` | `star.map.embedding`, `contradiction.sweep`, `graph.compression`, `stability.simulation`, `custom_review_lane_assigned` |
| `MAINTENANCE_LOTTERY_ENTRY_UNIT` | `one_entry_per_review_lane_passed_task` |
| `MAINTENANCE_LOTTERY_ENTRY_CAP_PER_AGENT_PER_EPOCH` | `one` |
| `MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS` | `review_lane_pass_required`; `content_addressed_task_id_required`; `duplicate_task_id_rejected`; `duplicate_output_hash_collapsed`; `difficulty_factor_not_reward_input`; `one_entry_per_agent_per_epoch`; `author_reviewer_conflict_checks_required`; `same_operator_domain_diversity_check_required_before_production`; `no_unreviewed_task_reward`; `no_live_distribution_before_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH` | `cdl_047_treasury_quote_to_phase_1409_default_off_runtime_stub` |
| `MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY` | `epoch_boundary_batch_quote_only_until_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_DIRECT_ILC_REWARD_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_ACTIVATION_DEFAULT` | `not_activated` |
| `MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED` | `false` |
| `MAINTENANCE_LOTTERY_RUNTIME_PHASE` | `phase_1409_default_off_stub_only` |
| `MAINTENANCE_LOTTERY_GATE_FLIP_PHASE` | `phase_1427_after_phase_1425_verification` |

## 8. Carry-Forward Items

| Carry-forward token | Reason | Route |
|---------------------|--------|-------|
| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | No ratified SIM calibrates a nonzero maintenance lottery pool fraction | Future SIM/governance phase before any nonzero funding |
| `MAINTENANCE_LOTTERY_NONZERO_FUNDING_REQUIRES_SIM` | Prevents Phase 1408 ratification from becoming a hidden allocation | Future SIM/governance phase |
| `same_operator_domain_diversity_check_required_before_production` | Anti-capture production verification is a later J-008 blocker | Phase 1418-1419 |
| `production_vrf_or_later_ratified_randomness_required` | VRF implementation is not present yet | Phase 1410-1413 |

## 9. Historical Hardening

Historical hardening command:

```bash
git show 15992abe:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-093 \\|"
```

Result: CDL-093 is present with `status: open`, `opened_phase: 1406`,
`opening_token: cdl_093_maintenance_lottery_pool_opened_phase_1406`, and
`ratification_status: not_ratified_pending_phase_1408`.

## 10. Non-Ratification and Non-Activation

CDL-093 remains open and unratified after Phase 1407.

```text
cdl_093_not_ratified_phase_1407
```

Phase 1407 does not:

- mutate the CDL register;
- ratify CDL-093;
- create maintenance lottery runtime code;
- activate maintenance lottery distribution;
- execute live lottery draws;
- settle ECU;
- mint ILC;
- activate wallet behavior;
- activate reviewer payment;
- change the J-008 gate verdict;
- activate production jury behavior;
- publish public RC artifacts.

## 11. Phase 1408 Carry-Forward

Phase 1408 may ratify the scope constants in this document. Ratification still
must not activate maintenance lottery distribution, live draws, ECU settlement,
or runtime behavior.

## 12. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md -> constitutional/cdl
```
