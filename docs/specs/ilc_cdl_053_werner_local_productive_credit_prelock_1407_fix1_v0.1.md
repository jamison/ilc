# ILC CDL-053 Werner Local Productive Credit Prelock 1407-Fix1 v0.1

Phase: 1407-Fix1
Date: 2026-05-20
Status: prelock committed; CDL-053 remains open and unratified

Required tokens:

```text
cdl_053_prelock_committed_phase_1407_fix1
cdl_053_scope_constants_locked_phase_1407_fix1
```

## 1. Purpose

Phase 1407-Fix1 resolves the CDL-053 opening questions from Phase 1407-Fix0
into prelocked scope constants for Werner local productive credit. The scope is
narrow: reviewed maintenance-equivalent productive work may create local credit
eligibility. That local credit is not settlement-grade ECU, is not wallet
visible, is not transferable, and cannot become live economic value without a
later conversion gate.

CDL-053 remains open and unratified after Phase 1407-fix1.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-053 is open at fix1 execution time | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-053` | confirmed |
| Phase 1407-Fix0 opening token is present | `docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md` | confirmed |
| CDL-085 phi-bound is `Decimal("0.60")` exact | `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` | confirmed |
| J-005 task class list is the source for Q1 | `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` Decision 4 | confirmed |
| CDL-053 prelock doc did not exist before this phase | repo search for `cdl_053_prelock_committed_phase_1407_fix1` outside prompts | confirmed |

Contradiction search found only prompt-level future references to
`cdl_053_prelock_committed_phase_1407_fix1`, `cdl_053_scope_constants_locked_phase_1407_fix1`,
and `cdl_053_ratified_phase_1407_fix2`. No prior CDL-053 prelock document,
ratification evidence, or direct-ECU-creation authorization was found.

## 3. Q1 Resolution - Productive-Work Scope

Resolved scope: only review-lane-passed maintenance tasks from J-005 Decision 4
qualify for Werner local credit eligibility in this prelock.

Prelocked task classes:

| Task class | CDL-053 treatment |
|------------|-------------------|
| `star.map.embedding` | Eligible after review-lane pass; may be provenance-equivalent when it creates or updates derivation/embedding graph structure |
| `contradiction.sweep` | Eligible after review-lane pass; may be provenance-equivalent when it records contradiction/provenance work or routes into T5 refutation/provenance review |
| `graph.compression` | Eligible after review-lane pass; quality-gated as structural maintenance unless a later review lane classifies the output as provenance-equivalent |
| `stability.simulation` | Eligible after review-lane pass; quality-gated as simulation/evidence work and not automatically provenance-equivalent |
| `custom_review_lane_assigned` | Eligible only when the task definition assigns a review lane and the result passes that lane |

Non-maintenance productive-credit categories, including validator rewards,
generic jury compensation, ordinary claim authorship, and non-maintenance
refutation work, are deferred to future CDL-053 amendment or another explicit
economic authority.

## 4. Q2 Resolution - Local Credit Unit and Conversion Gate

The local credit unit designation is `local_productive_credit`.

`local_productive_credit` is a bottom-up attribution unit for reviewed useful
work. It is not pulled from a global treasury balance and is not top-down budget
issuance. It records local eligibility created by the reviewed task outcome.
That eligibility remains non-settlement and non-wallet until a later conversion
gate admits it into settlement-grade ECU.

The conversion gate is:

```text
WERNER_SETTLEMENT_GATE = consensus_epoch_public_economics_gate_and_j008_production_activation
```

The gate must not be read as live activation. Settlement-grade ECU requires a
later ratified conversion path, J-008 production activation, consensus-epoch
settlement, and the applicable public-economics gate. Phase 1407-Fix1 does not
authorize that conversion.

## 5. Q3 Resolution - CDL-085 Phi-Bound Inheritance

CDL-053 inherits CDL-085 only for provenance-equivalent edge-mint work.

Inherited value:

```text
WERNER_EDGE_MINT_PHI_BOUND_INHERITED = cdl_085_decimal_0_60
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

Task-class application:

| Task class | Phi-bound treatment |
|------------|---------------------|
| `star.map.embedding` | Apply CDL-085 when the reviewed output is provenance-equivalent graph derivation or edge-mint expansion |
| `contradiction.sweep` | Apply CDL-085 when the reviewed output is provenance-equivalent contradiction/provenance work |
| `graph.compression` | Do not apply CDL-085 by default; use review-lane structural-quality audit and duplicate-collapse controls |
| `stability.simulation` | Do not apply CDL-085 by default; use simulation reproducibility, parameter provenance, and review-lane audit controls |
| `custom_review_lane_assigned` | Apply CDL-085 only if the assigned review lane explicitly classifies the output as provenance-equivalent |

CDL-053 does not re-ratify CDL-085, change the `Decimal("0.60")` value, or
extend CDL-085 beyond provenance-equivalent work.

## 6. Q4 Resolution - Anti-Gaming and Anti-Inflation Boundary

Local productive credit cannot inflate settlement-grade ECU supply without the
conversion gate. Minimum anti-gaming controls:

```text
WERNER_LOCAL_CREDIT_ANTI_GAMING_CONTROLS =
review_lane_pass_required;
content_addressed_task_id_required;
canonical_task_descriptor_hash_required;
duplicate_task_id_rejected;
duplicate_output_hash_collapsed;
one_credit_per_agent_per_epoch;
author_reviewer_conflict_checks_required;
operator_domain_conflict_checks_required;
no_settlement_grade_ecu_without_conversion_gate;
no_wallet_mutation;
no_direct_heat_to_ecu_minting;
no_live_distribution_before_j008_pass_and_production_go
```

The controls are prelock constants, not runtime implementation. Later runtime
work must implement equivalent checks before any live economic distribution.

## 7. Locked Scope Constants

| Constant | Value |
|----------|-------|
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

## 8. Historical Hardening

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

## 9. Phase 1263 Boundary

Phase 1407-Fix1 preserves the Phase 1263 non-overlap:

```text
direct_werner_ecu_creation_rejected_phase_1263
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
```

CDL-053 local productive credit is not a Werner flow-governor opening. It does
not authorize heat-to-ECU minting, topology-pressure-to-ECU minting, per-request
tolls, per-hop micropayments, wallet withdrawal/transfer/spend, ILC settlement,
or public claimability.

## 10. Non-Ratification and Non-Activation

CDL-053 remains open and unratified after Phase 1407-fix1.

Phase 1407-Fix1 does not mutate the CDL register, ratify CDL-053, mutate
CDL-093, create or modify runtime code, mint ECU, create settlement-grade ECU,
settle ILC, mutate wallets, activate live maintenance lottery distribution,
execute live lottery draws, activate public claimability, or change the J-008
gate verdict.

## 11. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_053_werner_local_productive_credit_prelock_1407_fix1_v0.1.md -> constitutional/cdl
```
