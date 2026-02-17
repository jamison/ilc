# ILC Main-Track Return Sequence 213-221 v0.1

Status: Locked (Phase 213)
Date: 2026-02-17
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Lock a deterministic, dependency-ordered execution path for phases 213 through 221 after Phase 212 constitutional-invariant hardening.

## 2. Dependency Baseline

Required completed artifacts:
- `docs/specs/ilc_main_track_return_202_210_handoff_v0.1.md`
- `docs/specs/ilc_main_track_return_sequence_202_211_v0.1.md`
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required active guardrails:
- `tools/check_main_track_return_preflight_203_209.sh`
- `tools/check_main_track_return_closure_202_210.sh`
- `tools/check_refutation_profitability_invariant_phase_212.sh`

## 3. Entry Gate Before Phase 214

Phase 214 may start only if all of the following are green:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_213_g8_constitution_cluster_a_main_track_post_ra_sequence_lock_and_scope_gate.md` returns `VALID`.
2. `python3 -m pytest tests/test_main_track_return_sequence_phase_213.py -q` passes.
3. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q` passes.

## 4. Locked Phase Window (213-221)

| Phase | Gate Type | Objective | Dependencies | Exit Gate |
| --- | --- | --- | --- | --- |
| 213 | `spec` | Lock deterministic sequence and scope for phases 213-221. | Phase 212 completion. | Sequence spec, guardrail test, TODO and STATUS pointers committed. |
| 214 | `integration` | Implement replayable path-lift counterfactual harness for node-level marginal contribution evidence (`CDL-014`). | Phase 213 lock. | Deterministic counterfactual harness tests pass with replay fixtures. |
| 215 | `ratification` | Produce ratification evidence package for `CDL-011` to `CDL-015` and update decision-log candidate states with cited implementation hooks. | Phase 214 harness complete. | Ratification evidence spec and decision-log conformance tests pass. |
| 216 | `integration` | Enforce anti-Sybil and reuse-diversity weighting invariants in score and payout surfaces. | Phase 215 evidence package merged. | Anti-Sybil invariant tests and regression subset pass. |
| 217 | `integration` | Lock freshness-gate function shape and bounds with deterministic contract tests. | Phase 216 invariants green. | Freshness contract tests pass and replay determinism preserved. |
| 218 | `integration` | Implement Genesis accrual governor simulation and cap-trajectory checks aligned to constitutional economics, using `theta_soft = exp(-3)` taper target and hard cap `theta_hard = 1/20`. | Phase 217 freshness gate lock. | Governor simulation tests pass and policy checks are deterministic. |
| 219 | `integration` | Consolidate conformance hooks (`CH-USE-001..004`) and telemetry schema for node-value/governance surfaces. | Phase 218 governor checks merged. | Hook and telemetry schema tests pass with stable key set. |
| 220 | `integration` | Compose preflight gate for phases 214-219 and integrate into CI workflow. | Phases 214-219 committed. | Gate script tests and CI workflow ordering tests pass. |
| 221 | `closure` | Run closure regression for 213-220 and publish handoff artifact. | Phase 220 preflight integrated. | Consolidated regression subset passes and handoff artifact is published. |

## 5. Sequencing Rationale

- Phase 214 establishes a replayable counterfactual basis before ratification changes are finalized.
- Phase 215 closes constitutional ratification evidence for still-open node-value decision-log items.
- Phases 216-219 implement remaining contract-level hardening needed for stable governance/economics operation.
- Phase 220 operationalizes the line in CI after implementation contracts stabilize.
- Phase 221 prevents partial handoff and captures closure evidence.

## 6. Non-Goals for This Lock

- No runtime feature behavior is changed by this sequence document.
- No constitutional decision is marked `ratified` by this lock artifact alone.
- No implementation work for phases 214-221 is executed in Phase 213.
