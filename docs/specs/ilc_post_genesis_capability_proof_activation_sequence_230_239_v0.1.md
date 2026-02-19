# ILC Post-Genesis Capability-Proof Activation Sequence 230-239 v0.1

Status: Locked (Phase 230)
Date: 2026-02-19
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock the dependency-ordered post-Genesis readiness window for phases 230 through 239, covering:
- capability-proof activation readiness,
- open-CDL runtime implementation planning lanes,
- issuance/governance closure planning lanes,
- SDK/bootstrap boundary documentation lanes,
- composed preflight and closure gates.

This lock is planning/governance artifact scope only. It does not itself implement `ilc_core/` runtime behavior.

## 2. Dependency baseline and entry gate

Required completed baseline:
- `docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md`
- `docs/specs/ilc_genesis_packaging_222_228_handoff_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.2.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.2.md`

Entry gate before Phase 231:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_230_g8_constitution_cluster_a_post_genesis_capability_proof_activation_readiness_sequence_lock_and_d1_reproducibility_baseline.md` returns `VALID`.
2. `python3 -m pytest tests/test_reproducible_build_phase_230.py -q` passes.
3. `bash tools/check_reproducible_build.sh` passes.
4. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q` passes.

## 3. Locked phase table (230-239)

| Step | Phase | Lane type | Objective | Dependencies | Exit gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 230 | `spec + reproducibility` | Lock 230-239 sequence and establish D1 reproducibility baseline (`SOURCE_DATE_EPOCH=0`, deterministic rebuild gate, backend decision note). | Phase-229 closure complete. | Sequence lock + D1 gate/tests + STATUS/walkthrough evidence. |
| 2 | 231 | `readiness-contract` | Capability-proof activation readiness contract lock (`CapProof` baseline, defer gates for AWP/IIH and QATPS lanes). | Phase 230 complete. | Readiness contract + gate tests + explicit deferred boundaries. |
| 3 | 232 | `security-runtime-plan` | Runtime implementation plan lock for open CDLs (`CDL-001`, `CDL-002`, `CDL-007`) with sequencing and test strategy. | Phase 231 complete. | Planning artifact + risk/rollback plan + entry criteria for implementation phases. |
| 4 | 233 | `issuance-governance-plan` | Issuance policy closure plan including multiplier-governance lane (`CDL-019`) and dependency map. | Phase 232 complete. | Planning artifact + decision-log queue mapping + non-goal boundaries. |
| 5 | 234 | `sdk-boundary` | Agent SDK boundary contract lock (protocol surface vs orchestration/runtime surface). | Phase 233 complete. | Contract spec + examples + anti-leakage boundary checks. |
| 6 | 235 | `bootstrap-ops` | Bootstrap operations runbook lock (fleet composition, phase A->B transition criteria, observability). | Phase 234 complete. | Runbook + deterministic acceptance checklist. |
| 7 | 236 | `preflight` | Additive composed preflight gate for 230-235 artifacts. | Phase 235 complete. | Preflight gate + tests + dry-run/help/unknown-arg contracts. |
| 8 | 237 | `integration-doc` | Cross-artifact coherence pass (capsule/roadmap/decision-log alignment for 230-237). | Phase 236 complete. | Coherence artifact + regression checks for references/anchors. |
| 9 | 238 | `release-readiness` | Post-genesis readiness package summary for the 230-238 window. | Phase 237 complete. | Package summary artifact + pass evidence aggregation. |
| 10 | 239 | `closure` | Closure regression and handoff for 230-238. | Phase 238 complete. | Closure gate PASS + handoff artifact + next sequence pointer. |

## 4. Per-phase sensitivity classification

| Phase | Classification |
| --- | --- |
| 230 | sensitive |
| 231 | sensitive |
| 232 | sensitive |
| 233 | sensitive |
| 234 | non_sensitive |
| 235 | non_sensitive |
| 236 | non_sensitive |
| 237 | non_sensitive |
| 238 | non_sensitive |
| 239 | non_sensitive |

Sensitivity rule:
- `sensitive`: draft + harden + explicit human `GO` before execution.
- `non_sensitive`: full-cycle execution in one pass after prompt validation.

## 5. Mandatory entry/exit gates per phase lane

- `spec/readiness-contract/security-runtime-plan/issuance-governance-plan` lanes must include:
  - prompt schema validation,
  - focused artifact contract tests,
  - no-ellipses walkthrough guardrail.
- `sdk-boundary/bootstrap-ops/integration-doc/release-readiness` lanes must include:
  - prompt schema validation,
  - lane-focused contract tests,
  - reference-anchor integrity checks (paths and required sections).
- `preflight` lane must include:
  - gate script contract tests,
  - dry-run + full execution pass,
  - additive composition only (no replacement of existing gates).
- `closure` lane must include:
  - composed closure gate,
  - handoff artifact,
  - STATUS forward pointer.

## 6. D1 reproducibility baseline lock and exit criteria

D1 baseline is considered complete only if all are true:
1. deterministic rebuild gate exists (`tools/check_reproducible_build.sh`) and sets `SOURCE_DATE_EPOCH=0` for both runs,
2. gate compares build artifacts from two isolated builds and fails on checksum mismatch,
3. backend decision note is published,
4. provenance contract language explicitly states same-platform reproducibility scope and non-goals.

## 7. Non-goals and out-of-scope boundaries

- No `ilc_core/` runtime behavior changes are required by this sequence lock artifact.
- No D2/D2b/D2c/D2d implementation tasks are in scope for this window.
- No automatic ratification of open CDLs in this sequence lock.
- No Rust-kernel milestone execution in this window.

## 8. Forward pointer and carry-forward debt list

Forward pointer after phase-239 closure: define next implementation sequence for approved runtime lanes.

Carry-forward debt list anchored at sequence start:
- `CDL-001`, `CDL-002`, `CDL-007` runtime implementation remains open,
- `CDL-019` multiplier-governance surface remains open,
- issuance-policy closure parameters remain open,
- capability-proof advanced lanes (`AWP/IIH`, optional QATPS coupling) remain deferred behind readiness gates.
