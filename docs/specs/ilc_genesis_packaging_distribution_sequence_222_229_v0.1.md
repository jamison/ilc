# ILC Genesis Packaging Distribution Readiness Sequence 222-229 v0.1

Status: Locked (Phase 222)
Date: 2026-02-18
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Lock a deterministic execution sequence for phases 222 through 229 to move from the completed RA implementation line (213-220) into Genesis packaging and distribution readiness.

## 2. Dependency Baseline

Required completed artifacts:
- `docs/specs/ilc_main_track_return_213_220_handoff_v0.1.md`
- `docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md`
- `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Required active guardrails:
- `tools/check_main_track_return_closure_213_220.sh`
- `tools/check_main_track_return_preflight_214_219.sh`
- `tools/check_refutation_profitability_invariant_phase_212.sh`
- `tools/check_node_value_governance_conformance_phase_219.sh`

## 3. Entry Gate Before Phase 223

Phase 223 may start only if all of the following are green:
1. `python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_222_g8_constitution_cluster_a_genesis_packaging_distribution_readiness_sequence_lock_and_scope_gate.md` returns `VALID`.
2. `python3 -m pytest tests/test_genesis_packaging_distribution_sequence_phase_222.py -q` passes.
3. `python3 -m pytest tests/test_main_track_return_sequence_phase_213.py -q` passes.
4. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q` passes.

## 4. Locked Phase Window (222-229)

Execution order is locked and intentionally non-numeric for phases 225-227.

| Step | Phase | Gate Type | Objective | Dependencies | Exit Gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 222 | `spec` | Lock deterministic sequence and scope for phases 222-229. | Phase 221 closure handoff complete. | Sequence spec, guardrail tests, TODO/plan pointers committed. |
| 2 | 223 | `hygiene` | Run constrained pre-Genesis hygiene sweep. Scope is capped to `ilc_core/analysis/` only, limited to `math.isfinite()` backfill and trivially narrowable broad exceptions. Touch count cap: at most five files. | Phase 222 lock. | Focused tests green and scope cap honored. |
| 3 | 224 | `integration` | Add deterministic end-to-end pipeline smoke test that composes scoring, diversity/freshness weighting, reward allocation, and conformance checks, including one post-install import smoke path. | Phase 223 hygiene complete. | In-repo integration smoke and post-install import smoke both pass. |
| 4 | 226 | `triage` | Perform security/CDL triage for `CDL-001`, `CDL-002`, and `CDL-007` using locked Genesis-blocker rubric; produce explicit defer-or-blocker decisions. | Phase 224 integration smoke complete. | Triage artifact published with rubric-backed verdict per CDL item. |
| 5 | 227 | `remediation-or-noop` | Execute remediation for any triaged Genesis blockers; if none, publish formal no-op closure artifact with per-CDL deferral rationale. | Phase 226 triage verdict complete. | Implementation or no-op artifact published; state unambiguous. |
| 6 | 225 | `distribution` | Validate packaging/install surface against final post-227 codebase. | Phase 227 complete (or Phase 226 when 227 is explicit no-op). | `pip install .` path and CLI/import checks pass from clean environment. |
| 7 | 228 | `release` | Produce Genesis release artifact surface with built distributions and provenance evidence. | Phase 225 distribution validation complete. | `sdist` and `wheel` install checks pass from clean virtualenvs; checksums and release notes published. |
| 8 | 229 | `closure` | Run closure regression and publish handoff for 222-228 with deferred-debt carry-forward list. | Phase 228 release artifacts complete. | Closure gate passes, handoff published, forward pointer recorded. |

## 5. Locked Dependency Chain

The dependency chain for this sequence is locked as follows:
- `223` depends on `222`.
- `224` depends on `223`.
- `226` depends on `224`.
- `227` depends on `226`.
- `225` depends on `227` (or `226` when `227` is a documented no-op).
- `228` depends on `225`.
- `229` depends on `228`.

## 6. Phase-Specific Constraint Locks

### 6.1 Phase 223 hard scope cap

Phase 223 is constrained to:
- Files under `ilc_core/analysis/` only.
- Allowed work only: `math.isfinite()` guard backfill and trivially narrowable broad-exception reductions.
- Touch budget cap: no more than five files.

If more than five files are needed, Phase 223 scope is invalid and must be re-locked in a future sequence.

### 6.2 Phase 224 integration composition lock

Phase 224 must include:
- one deterministic in-repo end-to-end integration smoke test for the full constitutional scoring/reward/conformance pipeline,
- one post-install import smoke check (`pip install .` and `python -c "from ilc_core.analysis.node_value_governance_conformance import ..."`).

### 6.3 Phase 226 Genesis-blocker rubric lock

A CDL item is a Genesis blocker if any one criterion is true:
1. first-run breakage without the missing capability,
2. key or data loss risk,
3. exploitable rollback or state-corruption risk,
4. no viable mitigation path/workaround.

This rubric is mandatory and cannot be replaced by ad hoc triage language.

### 6.4 Phase 227 closure artifact lock

Phase 227 must always produce an artifact:
- blocker path: remediation evidence and verification,
- no-blocker path: formal no-op closure with per-CDL deferral rationale.

### 6.5 Phase 228 release provenance lock

Phase 228 must include all of:
- build and validation of `sdist` and `wheel`,
- clean-venv install checks for both artifacts,
- checksum provenance output,
- release notes artifact.

## 7. Sequencing Rationale

- Phase 223 removes known low-risk hygiene debt before integration smoke.
- Phase 224 proves cross-layer composition before any security triage decisions.
- Phase 226/227 resolve or formally defer open security CDLs before package surface validation.
- Phase 225 validates packaging on the final post-triage/remediation codebase.
- Phase 228 prepares auditable release artifacts only after installability is proven.
- Phase 229 captures closure evidence and carry-forward debt for the next mainline window.

## 8. Non-Goals for This Lock

- No runtime formulas, reward policies, or governance behavior are changed by this document.
- No CDL row is ratified or mutated by this lock artifact.
- No implementation work for phases 223-229 is executed in Phase 222.
