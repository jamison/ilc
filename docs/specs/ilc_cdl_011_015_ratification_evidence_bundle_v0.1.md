# ILC CDL-011 through CDL-015 Ratification Evidence Bundle v0.1

Status: Ratified evidence package (Phase 215)
Date: 2026-02-17
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Provide decision-level constitutional evidence for `CDL-011` through `CDL-015` and justify state transitions under the promotion rule in `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

## 2. Ratification Sufficiency Contract Used

Each decision is marked `ratified` only if all conditions are true:

1. Candidate option in decision log matches evidence narrative and is explicitly justified.
2. Evidence includes at least one implementation artifact already present in repo.
3. Evidence includes at least one deterministic verification artifact already present in repo.
4. Evidence includes executable verification commands and passing outcomes.
5. No unresolved blocker remains that directly prevents constitutional intent from being satisfied.

## 3. Decision Evidence Matrix

| Decision | Candidate | Verdict | Implementation anchor(s) | Verification anchor(s) |
| --- | --- | --- | --- | --- |
| `CDL-011` | `balanced composite` | `ratified` | `ilc_core/analysis/node_value_kernel.py`; `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md` | `tests/test_node_value_kernel_phase_205.py`; `tests/test_node_value_conformance_phase_206.py` |
| `CDL-012` | `usage+freshness` | `ratified` | `ilc_core/analysis/utility_flow_rewards.py`; `ilc_core/sim/devnet_multi_epoch.py` | `tests/test_utility_flow_rewards_phase_208.py`; `tests/test_devnet_multi_epoch.py` |
| `CDL-013` | `decay-non-genesis-only` | `ratified` | `ilc_core/analysis/governance_weight.py`; `ilc_core/analysis/node_value_policy_migration.py`; `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md` | `tests/test_governance_weight_phase_207.py`; `tests/test_node_value_policy_migration_phase_209.py` |
| `CDL-014` | `counterfactual path-lift` | `ratified` | `ilc_core/analysis/path_lift_counterfactual.py`; `docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`; `ilc_core/analysis/node_value_kernel.py` | `tests/test_path_lift_counterfactual_phase_214.py`; `tests/test_node_value_kernel_phase_205.py` |
| `CDL-015` | `strict phase gate` | `ratified` | `docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md`; `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md` | `tests/test_main_track_return_sequence_phase_213.py`; `tools/check_main_track_return_preflight_203_209.sh`; `tools/check_main_track_return_closure_202_210.sh` |

## 4. Decision-Level Evidence

### 4.1 CDL-011

#### Intent
Ratify the node usefulness (`EW`) formula family with a balanced composite structure and deterministic reproducibility.

#### Candidate option and rationale
- Candidate: `balanced composite`
- Rationale: kernel and conformance surfaces implement weighted multi-component composition (`reuse`, `contradiction`, `validation`, `path`) with deterministic, stable output ordering.

#### Implementation artifacts
- `ilc_core/analysis/node_value_kernel.py`
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- `docs/phases/phase_205_g8_constitution_cluster_a_ra02_deterministic_offline_score_kernel_walkthrough.md`

#### Verification artifacts
- `tests/test_node_value_kernel_phase_205.py`
- `tests/test_node_value_conformance_phase_206.py`

#### Verification evidence (commands/results)
- `python3 -m pytest tests/test_node_value_kernel_phase_205.py tests/test_node_value_conformance_phase_206.py -q`
- Result: pass (recorded in Phase 215 verification section).

#### Ratification verdict
`ratified`

#### Residual gap and next remediation phase
None for this decision scope.

### 4.2 CDL-012

#### Intent
Ratify utility-flow to payout linkage with freshness-sensitive utility inputs and deterministic reward-allocation behavior.

#### Candidate option and rationale
- Candidate: `usage+freshness`
- Rationale: `UF` input from node-value kernel includes freshness gate, and reward allocation consumes utility-flow deterministically with governor checks and invariant enforcement.

#### Implementation artifacts
- `ilc_core/analysis/node_value_kernel.py`
- `ilc_core/analysis/utility_flow_rewards.py`
- `ilc_core/sim/devnet_multi_epoch.py`
- `docs/phases/phase_208_g8_constitution_cluster_a_ra05_utility_flow_reward_linkage_and_governor_checks_walkthrough.md`

#### Verification artifacts
- `tests/test_utility_flow_rewards_phase_208.py`
- `tests/test_devnet_multi_epoch.py`

#### Verification evidence (commands/results)
- `python3 -m pytest tests/test_utility_flow_rewards_phase_208.py tests/test_devnet_multi_epoch.py -q`
- Result: pass (recorded in Phase 215 verification section).

#### Ratification verdict
`ratified`

#### Residual gap and next remediation phase
None for this decision scope.

### 4.3 CDL-013

#### Intent
Ratify governance weighting with non-Genesis inactivity decay and Genesis baseline behavior under global normalization.

#### Candidate option and rationale
- Candidate: `decay-non-genesis-only`
- Rationale: non-Genesis rows apply explicit exponential inactivity decay; Genesis rows use baseline (plus optional bonus policy flag), and vote share is globally normalized.

#### Implementation artifacts
- `ilc_core/analysis/governance_weight.py`
- `ilc_core/analysis/node_value_policy_migration.py`
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/phases/phase_207_g8_constitution_cluster_a_ra04_governance_weight_pipeline_and_normalization_walkthrough.md`
- `docs/phases/phase_209_g8_constitution_cluster_a_ra06_policy_migration_controls_and_compatibility_cleanup_walkthrough.md`

#### Verification artifacts
- `tests/test_governance_weight_phase_207.py`
- `tests/test_node_value_policy_migration_phase_209.py`

#### Verification evidence (commands/results)
- `python3 -m pytest tests/test_governance_weight_phase_207.py tests/test_node_value_policy_migration_phase_209.py -q`
- Result: pass (recorded in Phase 215 verification section).

#### Ratification verdict
`ratified`

#### Residual gap and next remediation phase
None for this decision scope.

### 4.4 CDL-014

#### Intent
Ratify path-level marginal contribution method using deterministic replayable counterfactual harness.

#### Candidate option and rationale
- Candidate: `counterfactual path-lift`
- Rationale: dedicated path witness schema, deterministic counterfactual lift computation, provenance-preserving outputs, and stable normalization/ranking contracts are implemented and tested.

#### Implementation artifacts
- `ilc_core/analysis/path_lift_counterfactual.py`
- `docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`
- `ilc_core/analysis/node_value_kernel.py`
- `docs/phases/phase_214_g8_constitution_cluster_a_ra08_replayable_path_lift_counterfactual_harness_walkthrough.md`

#### Verification artifacts
- `tests/test_path_lift_counterfactual_phase_214.py`
- `tests/test_node_value_kernel_phase_205.py`

#### Verification evidence (commands/results)
- `python3 -m pytest tests/test_path_lift_counterfactual_phase_214.py tests/test_node_value_kernel_phase_205.py -q`
- Result: pass (recorded in Phase 215 verification section).

#### Ratification verdict
`ratified`

#### Residual gap and next remediation phase
None for this decision scope.

### 4.5 CDL-015

#### Intent
Ratify strict dependency-ordered sequencing and gate-enforced execution order to reduce refactor risk.

#### Candidate option and rationale
- Candidate: `strict phase gate`
- Rationale: sequence lock specs and executable preflight/closure gates are present and tested, and downstream objectives remain dependency-ordered.

#### Implementation artifacts
- `docs/specs/ilc_main_track_return_sequence_202_211_v0.1.md`
- `docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md`
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- `docs/phases/phase_213_g8_constitution_cluster_a_main_track_post_ra_sequence_lock_and_scope_gate_walkthrough.md`

#### Verification artifacts
- `tests/test_main_track_return_sequence_phase_213.py`
- `tests/test_main_track_return_preflight_gate_phase_210.py`
- `tests/test_main_track_return_closure_gate_phase_211.py`

#### Verification evidence (commands/results)
- `python3 -m pytest tests/test_main_track_return_sequence_phase_213.py tests/test_main_track_return_preflight_gate_phase_210.py tests/test_main_track_return_closure_gate_phase_211.py -q`
- Result: pass (recorded in Phase 215 verification section).

#### Ratification verdict
`ratified`

#### Residual gap and next remediation phase
None for this decision scope.

## 5. Phase 215 Verification Evidence

Commands executed in Phase 215 are listed in the walkthrough and mirrored in STATUS.

Primary checks:
- prompt validator for Phase 215 prompt,
- phase-215 evidence and gate tests,
- RA regression subset (`205, 206, 207, 208, 209, 214`),
- walkthrough ellipsis guardrail.

All checks passed.

## 6. Ratification Conclusion

`CDL-011` through `CDL-015` satisfy the ratification sufficiency contract and are ratified in `docs/specs/ilc_constitutional_decision_log_v0.1.md`.
