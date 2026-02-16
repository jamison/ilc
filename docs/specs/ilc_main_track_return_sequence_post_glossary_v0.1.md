# ILC Main-Track Return Sequence Post-Glossary v0.1

Status: Locked (Phase 192)
Date: 2026-02-16
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Lock a deterministic, dependency-ordered return path from side-track closure into main-track implementation work.

This sequence starts after completion of:
- non-replay domain-exception closure line (`Phase 191`), and
- glossary/governance elevation closure line (`Phase 995`).

## 2. Dependency Baseline

Required completed artifacts:
- `docs/specs/ilc_non_replay_domain_exception_migration_handoff_plan_v0.1.md`
- `docs/specs/ilc_glossary_term_elevation_track_990_994_handoff_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required closure guardrails (already established by prior phases):
- `tools/check_runtime_logging_closure.sh`
- `tools/check_domain_exception_migration_closure.sh`
- `tools/check_non_replay_domain_exception_migration_closure.sh`

## 3. Entry Gate Before Phase 193

Phase 193 may start only if all of the following are green:
1. Phase 192 artifacts exist and this sequence document is present.
2. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_192_g8_constitution_cluster_a_main_track_return_sequencing_and_dependency_lock.md` returns `VALID`.
3. `python3 -m pytest tests/test_main_track_return_sequence_phase_192.py -q` passes.
4. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q` passes.
5. No unresolved governance-core conflict set entries remain in `docs/architecture/governance_conflict_resolution_reminder_v0.1.md`.

## 4. Locked Phase Window (192-201)

| Phase | Gate Type | Objective | Dependencies | Exit Gate |
| --- | --- | --- | --- | --- |
| 192 | `spec` | Lock deterministic post-glossary return sequence and pre-Phase-193 entry criteria. | Phases 191 and 995 closure artifacts. | Sequence spec + guardrail test + STATUS update committed. |
| 193 | `integration` | Implement `commit.epoch` emission hook in devnet epoch finalization path. | Phase 192 lock; existing commit schema/event validators. | Emission integration tests pass and event payload contract remains stable. |
| 194 | `integration` | Emit and validate `epoch_summary` events in canonical event log flow. | Phase 193 emission wiring complete. | Epoch summary emission tests and schema checks pass. |
| 195 | `test` | Enforce event-log envelope contract (`kind` + `payload`) across scoped emitters. | Phase 194 event emission surfaces in place. | Guardrail tests prove no envelope drift in scoped emitters. |
| 196 | `integration` | Add deterministic event-log retention/rotation ops policy and script contract. | Phase 195 envelope guardrail stable. | Gate script tests + ops docs parity checks pass. |
| 197 | `integration` | Deliver known-record hash migration utility and transitional telemetry for Cluster A acceptance follow-up. | Phase 196 ops baseline; existing acceptance evidence contracts. | Migration utility tests + telemetry token assertions pass. |
| 198 | `integration` | Refactor server lifecycle globals to app-state/dependency lifecycle boundary. | Phase 197 complete and regression baseline green. | API lifecycle tests confirm deterministic state initialization. |
| 199 | `test` | Add multi-instance/server isolation regression coverage for app-state refactor. | Phase 198 lifecycle refactor merged. | Isolation and restart tests pass with no singleton leakage. |
| 200 | `integration` | Integrate main-track preflight gate composition for the 193-199 surfaces. | Phase 199 tests green. | Unified gate command passes in CI and local dry-run mode. |
| 201 | `closure` | Run full closure regression for 193-200 and publish handoff artifact. | Phases 193-200 committed. | Consolidated regression suite green and closure handoff published. |

## 5. Sequencing Rationale

- Phases 193-197 resolve protocol eventing and replay-acceptance prerequisites before touching server lifecycle.
- Phases 198-199 isolate architectural lifecycle risk into a bounded server track with explicit regression proofs.
- Phase 200 consolidates operational gate behavior only after implementation and test contracts are stable.
- Phase 201 is a strict closure gate to prevent partial handoff or unproven sequencing assumptions.

## 6. Non-Goals for This Lock

- No runtime protocol behavior is changed by this document.
- No additional governance ratification is performed here.
- No implementation work for phases 193-201 is performed in Phase 192.
