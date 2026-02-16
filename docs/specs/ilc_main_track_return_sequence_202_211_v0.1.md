# ILC Main-Track Return Sequence 202-211 v0.1

Status: Locked (Phase 202)
Date: 2026-02-16
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Lock a deterministic, dependency-ordered execution path for phases 202 through 211 after closure of the 193-200 line.

## 2. Dependency Baseline

Required completed artifacts:
- `docs/specs/ilc_main_track_return_193_200_handoff_v0.1.md`
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required active guardrails:
- `tools/check_main_track_return_preflight_193_199.sh`
- `tools/check_main_track_return_closure_193_200.sh`

## 3. Entry Gate Before Phase 203

Phase 203 may start only if all of the following are green:
1. Phase 202 artifacts exist and this sequence document is present.
2. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_202_g8_constitution_cluster_a_main_track_return_202_211_sequence_lock_and_scope_gate.md` returns `VALID`.
3. `python3 -m pytest tests/test_main_track_return_sequence_phase_202.py -q` passes.
4. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q` passes.

## 4. Locked Phase Window (202-211)

| Phase | Gate Type | Objective | Dependencies | Exit Gate |
| --- | --- | --- | --- | --- |
| 202 | `spec` | Lock deterministic sequence and scope for phases 202-211. | Phase 201 closure handoff. | Sequence spec, guardrail test, TODO and STATUS pointers committed. |
| 203 | `integration` | Implement RA-01 typed event canon and telemetry contracts for node-value scoring inputs. | Phase 202 lock. | Typed contract tests and schema boundary checks pass. |
| 204 | `integration` | Implement deterministic extraction hooks and replay fixtures for RA-01 inputs. | Phase 203 contracts in place. | Extraction determinism tests pass with stable fixtures. |
| 205 | `integration` | Implement RA-02 offline deterministic score kernel for epistemic weight and utility flow. | Phase 204 extraction outputs stable. | Kernel vector tests pass and output surface is typed. |
| 206 | `test` | Add RA-03 conformance and challenge harness for score disputes and anti-Sybil invariants. | Phase 205 kernel complete. | Conformance and challenge-path tests pass. |
| 207 | `integration` | Add RA-04 governance-weight pipeline with non-Genesis decay and normalized vote share. | Phase 206 harness green. | Governance-weight normalization tests pass. |
| 208 | `integration` | Add RA-05 utility-flow reward linkage and governor policy checks. | Phase 207 governance-weight pipeline merged. | Reward-link tests pass and budget invariants hold. |
| 209 | `integration` | Add RA-06 policy migration controls for temporary compatibility behavior. | Phase 208 linkage complete. | Migration controls and compatibility tests pass. |
| 210 | `integration` | Compose preflight gate for phases 203-209 and integrate into CI test workflow. | Phases 203-209 committed. | Gate script tests and workflow ordering tests pass. |
| 211 | `closure` | Run closure regression for 202-210 and publish handoff artifact. | Phase 210 preflight integrated. | Consolidated regression subset passes and handoff artifact is published. |

## 5. Sequencing Rationale

- Phases 203-205 lock deterministic typed scoring inputs before policy coupling.
- Phase 206 forces dispute and anti-Sybil correctness before governance and rewards wiring.
- Phases 207-209 introduce governance and economics linkages after scoring correctness is proven.
- Phase 210 operationalizes this line in CI only after implementation/test contracts stabilize.
- Phase 211 is strict closure to prevent partial handoff.

## 6. Non-Goals for This Lock

- No runtime feature behavior is changed by this sequence document.
- No constitutional ratification is completed in this phase.
- No implementation work for phases 203-211 is executed in Phase 202.
