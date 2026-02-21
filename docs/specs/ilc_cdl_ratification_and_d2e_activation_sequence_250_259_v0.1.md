# ILC CDL Ratification and D2e Activation Sequence 250-259 v0.1

Status: Locked (Phase 250)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock the dependency-ordered sequence for phases 250 through 259, covering:
- security-CDL ratification (`CDL-001`, `CDL-002`, `CDL-007`),
- ratification verification gate,
- `CDL-032` ratification and D2e-01 command-surface lock,
- D2e/D2 specification lanes,
- issuance analysis lane,
- integration coherence and closure handoff.

This sequence lock governs ordering and verification gates. It does not change runtime behavior and does not execute any CDL status mutation.

## 2. Dependency baseline and entry gate

Baseline entry state from Phase 249 handoff:
- `docs/specs/ilc_security_runtime_window_240_248_handoff_v0.1.md`
- `docs/specs/ilc_security_runtime_implementation_sequence_240_249_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Entry gate before Phase 251 starts:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_250_g8_constitution_cluster_a_cdl_ratification_and_d2e_activation_sequence_lock.md` returns `VALID`.
2. `python3 -m pytest tests/test_ratification_sequence_250.py -q` passes.
3. `python3 tools/run_phase_236_preflight.py` passes.

Ordering guardrail:
- Phase 252 ratification gate must pass before Phase 253 begins.

## 3. Locked phase table (250-259)

| Step | Phase | Lane type | Objective | Dependencies | Exit gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 250 | `sequence-lock + ratification-protocol` | Lock 250-259 sequence and ratification ceremony protocol. | Phase 249 closure complete. | Sequence lock artifact and tests pass. |
| 2 | 251 | `cdl-ratification-security` | Batch ratify `CDL-001`, `CDL-002`, `CDL-007`. | Phase 250 complete. | Ratification evidence doc and CDL mutations verified. |
| 3 | 252 | `ratification-gate` | Verify security-CDL ratification with composed governance gate. | Phase 251 complete. | Phase-252 gate dry-run/full-run pass. |
| 4 | 253 | `cdl-ratification-sdk + d2e-01` | Ratify `CDL-032` and lock D2e-01 CLI command surface. | Phase 252 gate PASS. | `CDL-032` mutation and command-surface tests pass. |
| 5 | 254 | `d2e-02` | Publish CLI output schema specification. | Phase 253 complete. | D2e-02 schema tests pass. |
| 6 | 255 | `d2-schema-foundation` | Publish minimal D2 schema specs for Node/Edge/Epoch Record. | Phase 250 complete. | D2 minimal schema tests pass. |
| 7 | 256 | `issuance-analysis` | Publish issuance-parameter analysis and `CDL-019` closure assessment. | Phase 247 survey available. | Issuance analysis tests pass. |
| 8 | 257 | `d2e-03-readiness` | Publish D2e-03 readiness and D2 schema test-vector spec. | Phases 254 and 255 complete. | D2e-03 readiness tests pass. |
| 9 | 258 | `integration-doc` | Publish coherence report and capsule v0.5. | Phases 251 through 257 complete. | Coherence tests pass and CDL alignment confirmed. |
| 10 | 259 | `closure` | Run closure regression and publish handoff for 250-258. | Phase 258 complete. | Closure gate dry-run/full-run pass and handoff published. |

## 4. Per-phase sensitivity classification

| Phase | Classification |
| --- | --- |
| 250 | non_sensitive |
| 251 | sensitive |
| 252 | sensitive |
| 253 | sensitive |
| 254 | non_sensitive |
| 255 | non_sensitive |
| 256 | non_sensitive |
| 257 | non_sensitive |
| 258 | non_sensitive |
| 259 | non_sensitive |

Sensitivity rule:
- `sensitive`: draft + harden + explicit human GO before execution.
- `non_sensitive`: full-cycle execution after prompt validation.

## 5. Mandatory entry/exit gates per phase lane

- `sequence-lock + ratification-protocol` lane must include prompt validation, sequence/protocol tests, preflight regression, and no-ratification boundary statements.
- `cdl-ratification-security` and `cdl-ratification-sdk + d2e-01` lanes must include explicit entry checks, focused ratification tests, and no-`ilc_core/` mutation statements.
- `ratification-gate` lane must enforce `--dry-run`, `--help`/`-h`, unknown-arg exit `2`, and full-run execution checks.
- Documentation lanes (`d2e-02`, `d2-schema-foundation`, `issuance-analysis`, `d2e-03-readiness`, `integration-doc`) must include prompt validation, lane-specific tests, preflight regression, and anchor-integrity checks.
- `closure` lane must include closure script dry-run/full-run and handoff artifact checks.
- Every phase must include stop-on-failure behavior in verification commands.

## 6. CDL ratification ceremony protocol

### 6.1 Evidence requirements

For each CDL candidate, ratification evidence must include all of:
1. Contract document reference.
2. Implementation phase and implementation module reference.
3. Unit test file reference with recorded pass count.
4. Integration gate phase reference.
5. Cross-CDL interaction test reference when the CDL participates in composed runtime behavior.
6. Coherence-check phase reference.

### 6.2 Ratification artifact format

Each ratification phase publishes a dedicated evidence document containing:
- one per-CDL evidence table mapping contract -> implementation -> tests -> gates -> coherence,
- one formal ratification statement per CDL referencing the evidence chain,
- explicit boundary statement that no runtime implementation was introduced in the ratification phase.

### 6.3 CDL file mutation protocol

When a CDL is ratified, allowed decision-log mutation fields are:
- `status`: `open` or `proposed` -> `ratified`,
- `ratified_phase`: `<phase-number>`,
- `ratified_date`: `<date>`,
- `evidence_document`: `<path-to-ratification-evidence-doc>`.

No other fields in that CDL row change as part of ratification.

### 6.4 Irrevocability clause

Ratification is one-way. A ratified CDL is never reverted to open/proposed. Any later policy replacement must occur through a new CDL ID with supersession linkage.

### 6.5 Batch ratification rule

Batch ratification is allowed when all CDLs in the batch share the same evidence chain and gate lineage. If evidence chains differ materially, ratification must be split into separate phases.

## 7. Non-goals and out-of-scope boundaries

- No runtime behavior changes in `ilc_core/` are made by this sequence lock artifact.
- No CDL status mutation is executed in this phase.
- No issuance parameter values are ratified in this window lock artifact.
- No OpenClaw skill ratification (`CDL-033`) is performed in this sequence lock phase.
- No D2e-03 implementation code is introduced.

## 8. Forward pointer and carry-forward debt list

Forward pointer:
- After Phase 259 closure, open the next sequence for Phase 260+ execution lanes.

Carry-forward debt list at sequence start:
- issuance-governance queue (`CDL-025` through `CDL-031`),
- OpenClaw skill contract (`CDL-033`),
- D2e-03 and later CLI implementation lanes,
- issuance parameter ratification,
- whitepaper release unblock path tied to issuance closure.
