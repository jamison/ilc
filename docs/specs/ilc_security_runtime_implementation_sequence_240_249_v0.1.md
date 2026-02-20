# ILC Security Runtime Implementation Sequence 240-249 v0.1

Status: Locked (Phase 240)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock the dependency-ordered security runtime window for phases 240 through 249, covering:
- lineage lifecycle schema lock,
- security runtime implementation lanes for `CDL-001`, `CDL-002`, `CDL-007`,
- composed security runtime integration gate,
- D2e/bootstrap and issuance-governance documentation lanes,
- closure regression and handoff.

This lock defines ordering, gates, and boundaries. It does not itself implement `ilc_core/` runtime behavior.

## 2. Dependency baseline and entry gate

Required baseline before Phase 241 runtime implementation:
- `docs/specs/ilc_post_genesis_window_230_238_handoff_v0.1.md`
- `docs/specs/ilc_security_runtime_implementation_plan_232_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`

Entry gate before Phase 241:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_240_g8_constitution_cluster_a_security_runtime_sequence_lock_and_lineage_event_schema.md` returns `VALID`.
2. `python3 -m pytest tests/test_lineage_event_schema_phase_240.py -q` passes.
3. `python3 -m pytest tests/test_security_runtime_sequence_240.py -q` passes.
4. `python3 tools/run_phase_236_preflight.py` passes.

## 3. Locked phase table (240-249)

| Step | Phase | Lane type | Objective | Dependencies | Exit gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 240 | `spec + lineage-schema` | Lock 240-249 sequence and publish canonical lineage lifecycle schema (`register`/`rotate`/`revoke`/`recover`). | Phase-239 closure complete. | Sequence lock + lineage schema + contract tests + STATUS/walkthrough evidence. |
| 2 | 241 | `security-runtime-cdl-001` | Implement signer-lineage trust-root runtime (`CDL-001`) with lifecycle state transitions and verification enforcement. | Phase 240 complete and schema gate pass. | `CDL-001` runtime tests pass and regression chain pass. |
| 3 | 242 | `security-runtime-cdl-002` | Implement key-compromise response runtime (`CDL-002`) with deterministic triggers and containment sequencing. | Phase 241 runtime tests pass. | `CDL-002` runtime tests + `CDL-001` regression pass. |
| 4 | 243 | `security-runtime-cdl-007` | Implement rollback resistance runtime (`CDL-007`) with supersession validation, replay/conflict rejection, and clawback declaration enforcement. | `CDL-001` runtime active; Phase 240 schema lock remains valid. | `CDL-007` runtime tests + `CDL-001` regression pass. |
| 5 | 244 | `security-runtime-gate` | Compose cross-CDL integration gate covering 240/241/242/243 plus cross-surface interaction tests. | Phases 241-243 complete. | Phase-244 gate script dry-run and full-run PASS. |
| 6 | 245 | `d2e-bootstrap` | Publish ADM-002 v0.2 bootstrap documentation and D2e activation assessment. | Phase 244 gate pass. | D2e bootstrap tests pass. |
| 7 | 246 | `d2e-pipeline-spec` | Publish D2e pipeline scaffolding spec mapped to ADM-001 layers. | Phase 245 complete. | D2e pipeline spec tests pass. |
| 8 | 247 | `issuance-governance-survey` | Publish activation planning survey for issuance queue `CDL-025` through `CDL-031`. | Phase 246 complete. | Issuance survey tests pass. |
| 9 | 248 | `integration-doc` | Publish capsule v0.4 and coherence report for 240-248 outputs. | Phase 247 complete. | Coherence tests pass and CDL open-status alignment confirmed. |
| 10 | 249 | `closure` | Close 240-248 window with composed closure gate and handoff artifact. | Phase 248 complete. | Closure gate PASS + handoff artifact + next sequence pointer. |

## 4. Per-phase sensitivity classification

| Phase | Classification |
| --- | --- |
| 240 | sensitive |
| 241 | sensitive |
| 242 | sensitive |
| 243 | sensitive |
| 244 | sensitive |
| 245 | non_sensitive |
| 246 | non_sensitive |
| 247 | non_sensitive |
| 248 | non_sensitive |
| 249 | non_sensitive |

Sensitivity rule:
- `sensitive`: draft + harden + explicit human `GO` before execution.
- `non_sensitive`: full-cycle execution after prompt validation.

## 5. Mandatory entry/exit gates per phase lane

- `spec + lineage-schema` lane must include prompt validation, contract tests, preflight regression, and explicit schema-transition coverage.
- `security-runtime-cdl-001/002/007` lanes must include runtime-focused tests, dependency-regression checks, and explicit no-ratification boundary statements.
- `security-runtime-gate` lane must include dry-run/help/unknown-arg contract checks and full composed execution as standalone command.
- `d2e-bootstrap`, `d2e-pipeline-spec`, `issuance-governance-survey`, `integration-doc` lanes must include prompt validation, lane-specific tests, and anchor-integrity checks.
- `closure` lane must include closure gate dry-run/full-run and handoff artifact checks.
- Every phase must execute `python3 tools/run_phase_236_preflight.py` as regression continuity gate.

## 6. Lineage lifecycle event schema lock and exit criteria

Schema lock file: `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`

Schema lock is complete only if all are true:
1. all four events are explicitly defined: `register`, `rotate`, `revoke`, `recover`,
2. lifecycle states `active`, `rotated`, `revoked`, `recovered` are explicit,
3. allowed and disallowed transition tables jointly cover all 12 ordered non-self state pairs,
4. schema anchors to `docs/specs/ilc_security_runtime_implementation_plan_232_v0.1.md` Section 6.1,
5. schema non-goal statement excludes cryptographic algorithms, key sizes, and quorum values.

Phase 241 must not start until this lock is satisfied.

## 7. Non-goals and out-of-scope boundaries

- No automatic ratification of open CDLs in this sequence artifact.
- No issuance policy constant setting in this sequence artifact.
- No `ilc_core/` runtime behavior changes are made by this sequence lock artifact itself.
- No cryptographic algorithm selection is decided in this sequence lock artifact.

## 8. Forward pointer and carry-forward debt list

Forward pointer after Phase-249 closure: establish Phase-250+ sequence for security runtime hardening and D2 implementation readiness.

Carry-forward debt list at sequence start:
- issuance-governance queue remains open: `CDL-025`, `CDL-026`, `CDL-027`, `CDL-028`, `CDL-029`, `CDL-030`, `CDL-031`,
- SDK/bootstrap governance lanes remain open: `CDL-032`, `CDL-033`,
- D2e continuation remains open beyond scaffolding and assessment,
- `ADM-002` ratification dependency remains open,
- `CDL-001`, `CDL-002`, `CDL-007` remain open until separate decision-log closure work.
