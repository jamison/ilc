# ILC Bootstrap Operations Runbook 235 v0.1

Status: Phase-235 planning runbook (non-ratifying)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This runbook defines deterministic operational steps for Phase A bootstrap fleet operation and readiness transition framing toward Phase B.

Scope constraints:
- no parameter ratification is performed,
- no `ilc_core/` runtime behavior is changed,
- no CDL status changes from `open` to `ratified` are performed,
- this artifact is operational planning only.

Canonical anchors:
- `docs/specs/ilc_antigravity_context_capsule_v0.2.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 2. Genesis fleet composition baseline

Minimum baseline composition for Phase A runbook execution:
- at least one asserter role agent,
- at least one validator role agent,
- at least one refuter role agent,
- at least one shard routing target configured,
- identity/key material initialized for each participating agent,
- protocol bundle verification configured as pre-run admission requirement.

Role baseline objective:
- ensure challenge paths are present from start,
- avoid single-role fleet topology,
- preserve deterministic identity and shard assignment records.

## 3. Phase A bootstrap sequence

1. Initialize operator environment and agent identities.
2. Verify protocol bundle and configuration before agent participation.
3. Execute CapProof probe run for each participating agent.
4. Admit only CapProof-passing agents to bootstrap participation roster.
5. Start Phase A claim/assertion workflow and validation/refutation loops.
6. Observe epoch transition at least once with full event logging.
7. Record bootstrap metrics and checkpoint operational state.

## 4. Phase A->B transition criteria

All criteria below must be satisfied before Phase B transition is declared:

1. **CapProof Gate A compliance** must be satisfied fleet-wide:
   - fail-closed behavior is active (failed probe means refusal, never default pass),
   - no user-supplied kernels or backend hints are permitted.
2. **Security CDL runtime readiness** must be satisfied:
   - `CDL-001` implementation readiness,
   - `CDL-002` implementation readiness,
   - `CDL-007` implementation readiness.
3. **Operational stability condition** must be demonstrated:
   - at least one full epoch transition with complete telemetry and no unresolved critical run failures.
4. **Rust runtime readiness** is treated as forward Phase B condition and must be satisfied before Phase B runtime migration activities.
5. **star.map/cross-shard routing** remains excluded from Phase A command surface and is deferred to Phase B/C L2 scope.

## 5. Observability plan

Mandatory signal categories tracked during bootstrap:

1. **Epoch transition events**
   - epoch start/end markers,
   - commit/finalization outcome tokens.

2. **CapProof probe results per agent**
   - probe pass/fail outcomes for GEMM/Infer/Graph/Bandwidth/Determinism,
   - rejection reasons under fail-closed policy.

3. **Operational error and economic signals**
   - CLI/network error events (exit code 1 and exit code 3 occurrences),
   - stake/balance state-change observations,
   - refutation challenge event volume.

## 6. Failure modes and recovery posture

Primary failure modes and required posture:
- identity/bootstrap initialization failure -> stop agent admission and rerun identity/bootstrap verification.
- CapProof failure cluster -> keep fail-closed gate active and quarantine failing agents until revalidated.
- bundle verification mismatch -> block participation and refresh canonical bundle source.
- persistent epoch transition errors -> halt progression, collect logs, and rerun from last stable checkpoint.
- repeated network/transport failures -> shift to degraded mode, preserve local logs, and retry with bounded backoff.

Recovery principle:
- fail closed first, recover with explicit checkpoints, never bypass boundary constraints to force progress.

## 7. Non-goal boundaries

This runbook does not perform:
- CDL ratification,
- runtime security implementation of `CDL-001`/`CDL-002`/`CDL-007`,
- star.map API design or cross-shard routing command design,
- changes to `ilc_core/` behavior,
- policy-value locking for issuance or governance parameters.

## 8. Deterministic acceptance checklist

- [ ] All participating agents complete `ilc identity --init` successfully.
- [ ] Protocol bundle verification succeeds for each agent before participation.
- [ ] All participating agents pass CapProof under fail-closed enforcement.
- [ ] No user-supplied kernel/backend hint override is used in CapProof runs.
- [ ] At least one shard is configured and reachable by the fleet.
- [ ] At least one epoch transition is observed with complete telemetry output.
- [ ] Observability logs include epoch transitions, CapProof probe outcomes, and one additional signal category.
- [ ] Phase A->B transition criteria review is documented for this fleet run.
- [ ] star.map/cross-shard routing remains excluded from Phase A command surface.
