# ILC CDL-093 Maintenance Lottery Pool Prelock Amendment 1407-Fix3 v0.1

Phase: 1407-Fix3
Date: 2026-05-20
Status: prelock amendment committed; CDL-093 remains open and unratified

Required tokens:

```text
cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3
maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3
```

## 1. Purpose

Phase 1407-Fix3 amends the CDL-093 Phase 1407 prelock constants that depended
on the CDL-047 treasury-governance quote candidate. CDL-053 is now ratified by
Phase 1407-Fix2, so CDL-093 can use the Werner local productive-credit source
instead.

The amendment is narrow. It changes only the four Q2 funding constants listed
below and preserves all Q1 draw-mechanism, Q3 eligibility, Q3 anti-gaming, Q4
settlement-boundary, and non-activation constants from the original Phase 1407
prelock.

CDL-093 remains open and unratified after Phase 1407-Fix3.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-053 is ratified before Fix3 executes | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-053` | confirmed |
| `cdl_053_ratified_phase_1407_fix2` token is present | `docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md` | confirmed |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE` was CDL-047 candidate in Phase 1407 prelock | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md` | confirmed |
| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM = true` existed in Phase 1407 prelock | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md` | confirmed |
| Phase 1408 prompt references Phase 1407 prelock as a ratification input | `docs/antigravity_tasks/antigravity_prompt__phase_1408_g8_cdl_093_maintenance_lottery_pool_ratification.md` | confirmed and patched by this phase |

Contradiction search found no prior `cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3`
or `maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3` claim.
Existing `import random` hits are historical code/tests/prompts outside this Fix3
SIM artifact. No Fix3 SIM harness imports or uses `random`.

## 3. Amended Constants

| Constant | Phase 1407 value | Phase 1407-Fix3 amended value |
|----------|------------------|-------------------------------|
| `MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE` | `cdl_047_treasury_governance_quote_candidate` | `cdl_053_werner_local_productive_credit` |
| `MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH` | `cdl_047_treasury_quote_to_phase_1409_default_off_runtime_stub` | `cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub` |
| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | `true` | `false` |
| `MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION` | `Decimal("0.00")` | `Decimal("0.10")` |

```text
cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3
```

## 4. Preserved Constants

The following Phase 1407 prelock constants remain unchanged:

| Constant | Preserved value |
|----------|-----------------|
| `MAINTENANCE_LOTTERY_DRAW_MECHANISM` | `production_vrf_or_later_ratified_randomness_required` |
| `MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM` | `epoch_hash_shadow_quote_only` |
| `MAINTENANCE_LOTTERY_ELIGIBLE_TASK_SCOPE` | `review_lane_passed_maintenance_tasks_only` |
| `MAINTENANCE_LOTTERY_TASK_CLASSES` | `star.map.embedding; contradiction.sweep; graph.compression; stability.simulation; custom_review_lane_assigned` |
| `MAINTENANCE_LOTTERY_ANTI_GAMING_CONTROLS` | `review_lane_pass_required`; `content_addressed_task_id_required`; `duplicate_task_id_rejected`; `duplicate_output_hash_collapsed`; `difficulty_factor_not_reward_input`; `one_entry_per_agent_per_epoch`; `author_reviewer_conflict_checks_required`; `same_operator_domain_diversity_check_required_before_production`; `no_unreviewed_task_reward`; `no_live_distribution_before_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_SETTLEMENT_BOUNDARY` | `epoch_boundary_batch_quote_only_until_j008_pass_and_production_go` |
| `MAINTENANCE_LOTTERY_RUNTIME_STATUS` | `not_activated_until_phase_1409_default_off_stub_and_later_production_go` |

## 5. Q2 SIM Result

The deterministic Q2 SIM is recorded in:

- `docs/sims/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3_v0.1.md`
- `out/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3.json`

Recommendation:

```text
MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal("0.10")
MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM = false
maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3
```

The SIM evaluates deterministic synthetic populations with 10, 100, and 1000
agents; 1, 3, and 5 maintenance tasks per agent per epoch; pass rates
`Decimal("0.30")`, `Decimal("0.50")`, and `Decimal("0.80")`; and the CDL-053
inherited `EDGE_MINT_PHI_BOUND = Decimal("0.60")` for provenance-equivalent
edge-mint tasks.

The selected `Decimal("0.10")` fraction reserves a small shared lottery pool
while retaining `Decimal("0.90")` of generated local productive credit for the
agent's direct local-credit attribution. It avoids the underfunding behavior of
`Decimal("0.05")` in the smallest scenario while avoiding excessive diversion
from direct local credit under `Decimal("0.15")` and `Decimal("0.20")`.

## 6. Non-Ratification and Non-Activation

Phase 1407-Fix3 does not mutate the CDL register, ratify CDL-093, create
runtime code, activate maintenance lottery distribution, execute live draws,
settle ECU, mint ECU, settle ILC, mutate wallets, activate public claimability,
or change the J-008 gate verdict.

## 7. Phase 1408 Routing

Phase 1408 must consume both:

1. the original Phase 1407 prelock, for all preserved constants; and
2. this Phase 1407-Fix3 amendment, for the amended Q2 funding constants and SIM
   result.

The Phase 1408 prompt is patched in Phase 1407-Fix3 to require
`cdl_053_ratified_phase_1407_fix2`,
`cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3`, and
`maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3`.

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md -> constitutional/cdl
```
