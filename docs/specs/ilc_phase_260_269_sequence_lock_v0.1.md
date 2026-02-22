# ILC Phase 260-269 Sequence Lock v0.1

Status: Locked (Phase 260)
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock the dependency-ordered sequence for phases 260 through 269 to:
- establish the ratification mutation-scope guardrail before additional ratification lanes,
- deliver the D2e (Distribution Track e) command-line interface prototype path without architecture drift,
- stage issuance-governance evidence and ratification in explicit governance lanes.

This lock governs ordering, dependencies, and verification gates. It does not change runtime behavior and does not execute any Constitutional Decision Log (CDL) status mutation.

## 2. Dependency baseline and entry gate

Baseline entry state from Phase 259 handoff:
- `docs/specs/ilc_cdl_ratification_window_250_258_handoff_v0.1.md`
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md`
- `docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Entry gate before Phase 261 starts:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_260_g8_constitution_cluster_a_sequence_lock_260_269_window.md` returns `VALID`.
2. `python3 -m pytest tests/test_phase_260_sequence_lock.py -q` passes.
3. `python3 tools/run_phase_236_preflight.py` passes.

Ordering guardrails:
- Phase 261 must complete before any ratification mutation lane begins.
- Phase 265 closure gate must pass before Phase 266 begins.
- Phase 266 evidence closure must pass before Phase 267 or Phase 268 begins.

## 3. Locked phase table (260-269)

| Step | Phase | Lane type | Objective | Dependencies | Exit gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 260 | `sequence-lock` | Lock 260-269 ordering, sensitivity map, and guardrail prerequisites. | Phase 259 closure complete. | Sequence lock artifact and tests pass. |
| 2 | 261 | `test-infrastructure` | Deliver reusable mutation-scope fixture for ratification lanes. | Phase 260 complete. | Mutation-scope fixture tests pass. |
| 3 | 262 | `signing-spec + doc-amendments` | Publish signing-provider specification and wallet-agnostic doc amendments. | Phase 260 complete. | Signing spec tests and anchor checks pass. |
| 4 | 263 | `d2e-03-contract-lock` | Lock D2e-03 implementation boundaries and acceptance criteria. | Phases 260, 262 complete. | D2e-03 contract tests pass. |
| 5 | 264 | `d2e-03-implementation` | Implement JSON-first CLI prototype aligned with locked command surface. | Phases 263, 254, 255, 257 complete. | D2e-03 implementation tests pass. |
| 6 | 265 | `d2e-03-closure-gate` | Add composed D2e-03 closure gate and handoff artifact. | Phase 264 complete. | Closure gate dry-run/full-run pass. |
| 7 | 266 | `issuance-evidence-closure-a` | Close evidence gaps for CDL-025/CDL-029 and reconciliation notes. | Phase 265 complete. | Issuance evidence tests pass. |
| 8 | 267 | `cdl-ratification-issuance-a` | Ratify CDL-025 using ceremony protocol and scoped mutation checks. | Phases 261, 266 complete. | Ratification evidence and scoped mutation checks pass. |
| 9 | 268 | `cdl-ratification-multiplier` | Ratify CDL-019 after migration/invariant evidence closure. | Phases 261, 266 complete. | Ratification evidence and scoped mutation checks pass. |
| 10 | 269 | `ratification-verification-gate + handoff` | Compose verification for 267/268 and publish next sequence handoff. | Phases 267 and 268 complete. | Ratification verification gate dry-run/full-run pass. |

## 4. Per-phase sensitivity classification

| Phase | Classification |
| --- | --- |
| 260 | non_sensitive |
| 261 | non_sensitive |
| 262 | non_sensitive |
| 263 | non_sensitive |
| 264 | non_sensitive |
| 265 | non_sensitive |
| 266 | non_sensitive |
| 267 | sensitive |
| 268 | sensitive |
| 269 | sensitive |

Sensitivity rule:
- `sensitive`: draft + harden + explicit human GO before execution.
- `non_sensitive`: full-cycle execution after prompt validation.

## 5. Mandatory entry/exit gates per lane

- `sequence-lock` lane must include prompt validation, sequence tests, preflight regression, and explicit non-mutation boundary statement.
- `test-infrastructure` lane must include positive and negative mutation-scope tests and deterministic CDL-row identity checks.
- `signing-spec + doc-amendments` lane must include privacy-invariant checks, version-successor checks, and anchor-integrity checks.
- `d2e-03-contract-lock` lane must include command-surface lock conformance checks and explicit DAG-CBOR deferral checks.
- `d2e-03-implementation` lane must include schema-conformance tests, command registration checks, and deterministic output checks.
- `d2e-03-closure-gate` lane must include `--dry-run`, `--help`/`-h`, unknown-arg exit `2`, and full-run execution checks.
- `issuance-evidence-closure-a` lane must include evidence-completeness checks and explicit non-ratification checks.
- `cdl-ratification-*` lanes must include ceremony-protocol mutation-scope enforcement and pre-mutation search checks.
- `ratification-verification-gate + handoff` lane must include composed gate dry-run/full-run and no-unintended-CDL-drift checks.

Stop-on-failure is mandatory in every phase in this sequence.

## 6. Ratification mutation-scope guardrail prerequisite

Before any Phase 260+ ratification lane (`267`, `268`, `269`) can run, the Phase-261 guardrail must exist and pass.

Required mutation-scope policy for ratification row updates:
- allowed mutation fields are exactly:
  - `status`
  - `ratified_phase`
  - `ratified_date`
  - `evidence_document`
- no other CDL row fields may change during ratification.

Guardrail acceptance must include both:
1. positive-path validation for legal field mutations,
2. negative-path rejection for out-of-scope field drift (for example, `current_candidate` text edits).

## 7. Non-goals and out-of-scope boundaries

- No `ilc_core/` runtime behavior changes in this phase.
- No CDL status mutation in this phase.
- No issuance policy-value ratification in this phase.
- No command-surface change to locked D2e-01 command names.
- No D2e-07 identity/bundle runtime scoping in this phase.

## 8. Forward pointer and carry-forward debt list

Forward pointer:
- After Phase 269 closure, open the next sequence for remaining issuance-governance closures and post-D2e-03 implementation lanes.

Carry-forward debt list at sequence start:
- issuance-governance queue (`CDL-026`, `CDL-027`, `CDL-028`, `CDL-029`, `CDL-030`, `CDL-031`) after phased closure of `CDL-025`/`CDL-019`,
- OpenClaw skill contract (`CDL-033`),
- D2e-04 through D2e-11 implementation lanes,
- whitepaper release unblock path tied to issuance closure,
- signing-provider pre-D2e-07 dependency enforcement continuity.
