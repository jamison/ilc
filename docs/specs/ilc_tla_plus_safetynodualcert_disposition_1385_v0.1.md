# ILC TLA+ SafetyNoDualCert Disposition 1385 v0.1

Status: governance disposition
Phase: 1385
Date: 2026-05-18
Owner lane: G8 formal-methods / public-RC gate preparation
Disposition selected: defer-with-authority

```text
tla_plus_safetynodualcert_disposed_phase_1385
safetynodualcert_deferred_with_authority_phase_1385
phase_1385_epoch_checkpoint_safetynodualcert_deferred_to_spec_d
```

## 1. Verdict

Phase 1385 selects defer-with-authority for the Phase 1385 prompt's
`SafetyNoDualCert` target.

The exact target disposed here is the epoch-checkpoint / shared-object property
named in the Phase 1385 prompt: no two validators produce valid certificates for
different epoch checkpoints at the same epoch height.

No TLC or TLAPS artifact was found that proves that epoch-checkpoint property.
The formal proof obligation is therefore deferred to a dedicated shared-object
epoch-settlement model, currently named in planning as Spec D.

This disposition does not erase existing formal evidence for the narrower
owned-object fast path. `docs/specs/tla/ilc_ecu_fast_path_bcast.tla` defines an
owned-object `SafetyNoDualCert` invariant over conflicting transfers on the same
`object_ref`, and `tools/tla/ilc_ecu_fast_path_bcast.tlc.out` records a clean
bounded TLC run for that model. That proof is adjacent evidence and is not proof of the epoch-checkpoint/shared-object property disposed in this phase.

## 2. Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| Phase 1385 prompt is valid and requires one disposition outcome | `docs/antigravity_tasks/antigravity_prompt__phase_1385_g8_tla_plus_safetynodualcert_disposition.md`; `tools/validate_phase_prompt.py` | confirmed |
| M-019 empirical confirmation exists | `tools/testbed/m019_run.log`; `docs/research/ilc_mysticeti_adversarial_hardening_M019_v0.1.md` | confirmed; no matching M-019 runner artifact was found under `out/` |
| TLA+ forward planning doc exists | `docs/specs/ilc_tla_plus_formal_verification_forward_planning_v0.1.md` | confirmed |
| M-022 recorded SafetyNoDualCert as an open item with empirical-only coverage | `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md` | confirmed |
| M-020 recorded empirical runtime coverage and formal-proof absence for the M-series handoff | `docs/research/ilc_safety_no_dual_cert_disposition_M020_v0.1.md`; `docs/research/ilc_external_security_audit_brief_M020_v0.1.md` | confirmed |
| Owned-object Spec B exists and checks `SafetyNoDualCert` | `docs/specs/tla/ilc_ecu_fast_path_bcast.tla`; `docs/specs/tla/ilc_ecu_fast_path_bcast.cfg` | confirmed |
| Owned-object Spec B has a clean bounded TLC log | `tools/tla/ilc_ecu_fast_path_bcast.tlc.out`; `docs/phases/phase_0784_tla_status_audit.md`; `docs/specs/ilc_tla_plus_formal_verification_forward_planning_v0.1.md` | confirmed |
| Epoch-checkpoint/shared-object SafetyNoDualCert formal proof exists | searches for `Spec D`, `epoch checkpoint`, `dual cert`, `tla_proof_complete`, and matching proof artifacts | not found |
| Output tokens were not already recorded before Phase 1385 | repo-wide required-token search excluding the Phase 1385 prompt and planning line | confirmed |

## 3. Discovery Record

| Pass | Findings |
|------|----------|
| Section 0a known-token audit | `tla_refinement_notes_pre_rc`, `tla_formal_verification_forward_planning_recorded_phase_1233_1240`, `SafetyNoDualCert`, and `M-019` were found and direct-read in current docs, research artifacts, TLA specs, Rust surfaces, and tests. |
| Section 0b concept-discovery search | Broad search covered TLA+, TLC, TLAPS, formal verification, M-019, M-020, M-022, equivocation, dual-cert, `ConflictingTransfer`, `in_flight`, `object_ref`, Spec B, Spec D, and shared-object epoch settlement. |
| Section 0c contradiction and non-claim search | Direct read found a real scope contradiction: M-020/M-022 say no formal proof, while later Phase 784/817/1255 documents record a clean Spec B bounded TLC result. The contradiction resolves by splitting owned-object Spec B from epoch-checkpoint/shared-object Spec D. |
| Section 0d source expansion | Direct-read the Phase 1385 prompt, STATUS tail, PLANNING_INDEX, sequence lock, candidate grouping, forward plan, TLA forward plan, Spec B TLA/cfg/log, Phase 784 and Phase 817 walkthroughs, M-019/M-020/M-022 research artifacts, `node.rs`, `balance_store.rs`, and `types.rs`. |
| MemPalace | Queried tier A for SafetyNoDualCert/M-022/Spec B context. The useful result pointed back to Phase 698 STATUS context and was direct-read through current worktree files before use. |

## 4. M-019 Empirical Coverage

M-019 executed four adversarial scenarios against the four-validator loopback
testbed with `N=4`, `F=1`, and `testnet_fault_sim` enabled:

| Scenario | Relevant SafetyNoDualCert observation |
|----------|---------------------------------------|
| Equivocation | Two `BroadcastHonest` messages with the same `object_ref` and different payloads were submitted. V1 recorded the first transfer, detected the second as `ConflictingTransfer / Equivocation Detected`, did not crash, and did not certify both transfers. |
| Silent partition | V1, V2, and V3 formed a 3-of-4 quorum while V4 was partitioned. This is liveness evidence, not a formal dual-cert proof. |
| Slow validator | V1, V2, and V3 formed quorum despite V4 delay. This is liveness evidence, not a formal dual-cert proof. |
| Censoring | V4 received the epoch over redundant paths and all validators committed epoch 1. This maps to row-7 runtime confirmation, not epoch-checkpoint formal proof. |

M-019 is current empirical coverage for the Rust equivocation path, but it is not
a formal proof. This is not a formal proof. Its scope limits are:

- loopback four-validator testbed only;
- testnet fault-injection build, not a production binary claim;
- conflicting `BroadcastHonest` / owned-object `object_ref` path, not a durable
  peer-to-peer epoch-checkpoint BFT round;
- no infinite-state or unbounded validator-set proof;
- no multi-operator production deployment, key ceremony, or public activation.

## 5. Formal Evidence Boundary

Existing formal evidence:

- Spec B file: `docs/specs/tla/ilc_ecu_fast_path_bcast.tla`
- Spec B config: `docs/specs/tla/ilc_ecu_fast_path_bcast.cfg`
- Spec B TLC log: `tools/tla/ilc_ecu_fast_path_bcast.tlc.out`
- Checked invariant: owned-object `SafetyNoDualCert`
- Parameters: `N=4`, `F=1`, two objects, one Byzantine validator, finite transfer ID set
- Result: clean bounded TLC run with no error found

That evidence covers owned-object fast-path conflicting transfers. It does not
cover the Phase 1385 prompt's epoch-checkpoint/shared-object dual-cert property.

Deferred formal evidence:

- Shared-object epoch-settlement / checkpoint dual-cert safety model
- Spec D or equivalent successor TLA+ model
- TLC or TLAPS evidence for the epoch-checkpoint property
- Updated refinement notes mapping that model to the current Rust checkpoint and
  epoch-settlement surfaces

## 6. Bounded Carry-Forward Authority

The deferral is bounded as follows:

1. Phase 1387, Phase 1387a, Phase 1388, and Phase 1389 may proceed with this
   deferral acknowledged, provided they do not claim the epoch-checkpoint
   `SafetyNoDualCert` property is formally proven.
2. Public-RC claimability gates may cite M-019 only as empirical runtime coverage
   for the current Rust equivocation path and may cite Spec B only for the
   owned-object fast path.
3. Any phase that needs a formal epoch-checkpoint/shared-object dual-cert claim
   must stop and route to a dedicated Spec D or equivalent formal-methods phase.
4. Production mainnet launch language, if later drafted, must either carry this
   deferral explicitly or close it with a committed proof artifact and updated
   governance disposition.
5. This phase authorizes no runtime change, no TLA spec mutation, no CDL mutation,
   no production deployment, no public activation, and no public RC claim.

## 7. Non-Authorizations

Phase 1385 does not:

- mutate `ilc_core/` or `ilc_consensus/`;
- mutate any CDL register row;
- create or rerun a TLA+ proof;
- engage a commercial audit firm;
- close any HIGH-severity finding;
- activate public serving, public claimability, wallet paths, ECU minting, ILC
  settlement, value-path conversion, production consensus, or public RC.

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/specs/ilc_tla_plus_safetynodualcert_disposition_1385_v0.1.md -> formal-methods/disposition`.
