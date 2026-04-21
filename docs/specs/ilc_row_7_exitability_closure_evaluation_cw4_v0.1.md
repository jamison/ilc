# ILC Row-7 Exitability Closure Evaluation CW-4 v0.1

**Phase:** 760  
**Window:** Mysticeti convergence window  
**Date:** 2026-04-21  
**Author:** Codex

`row_7_strong_exitability_runtime_closure_verdict=pass`
`row_7_combined_runtime_status=runtime_closed`
`row_7_censorship_and_exitability_both_pass`
`row_7_operator_api_independence_confirmed`

## 1. Evaluation target and hard threshold

`CW-1` re-verified the M-022 handoff artifact, so the strong-exitability side
of row `7` may now be evaluated against:

- Phase `741` Section `4`, and
- the Phase `674` strong-exitability threshold.

That threshold requires all four of the following:

1. export,
2. independent verify,
3. replay from portable data on a fresh node,
4. migrate without privileged original-operator consent.

This phase uses only the committed M-022 handoff evidence. It does not infer
unquoted runtime behavior.

## 2. Step 1 — Export

Quoted physical evidence from
`docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`:

- file path: `tools/testbed/m022_export.json`
- `epoch_chain: epochs 1-3 (gap-free)`
- `chain_complete: true`
- `bls_verified_commits: 3/3 (96-byte G2 agg_sig on every record)`
- `verdict: workload_d_replayability_pass`

The same section also records:

- `Conditions: all 4 validator processes stopped before extraction; no running validator, no operator API call.`

Verdict for Step 1:

- pass

The export step satisfies the Phase `674` exportability requirement because the
state was extracted into machine-legible form without relying on a running
validator or operator API.

## 3. Step 2 — Independent verify

Quoted physical evidence:

- file path: `tools/testbed/m022_verify.json`
- `operator_api_calls: 0`
- `running_validator_required: false`
- `independent_verify_verdict: pass`
- `all_commits_bls_verified: true`
- `agg_sig_96_bytes_each: true`

Verdict for Step 2:

- pass

This satisfies the Phase `674` verifiability requirement because the exported
state is checked offline against the genesis anchor and commit material without
trusting a running original operator.

## 4. Step 3 — Replay on a fresh node

Quoted physical evidence:

- file path: `tools/testbed/m022_replay.log`
- fresh-node condition: `validator_1 LMDB copied to fresh directory (temp_m022_migrate_db); fresh validator_harness instance started on different port (50175/50185), pointing at copy. No original validator process running.`
- `[m022_replay] gRPC GetEpoch: current_epoch=3`
- `[m022_replay] GetEpochChain: epoch=1 found=True agg_sig_len=96`
- `[m022_replay] GetEpochChain: epoch=2 found=True agg_sig_len=96`
- `[m022_replay] GetEpochChain: epoch=3 found=True agg_sig_len=96`
- `[m022_replay] chain_complete=True`
- `[m022_replay] gRPC_replay_verdict=pass`

Verdict for Step 3:

- pass

This satisfies the replayability requirement because the copied LMDB drives a
fresh validator process that reconstructs epoch state up to `current_epoch=3`
without any contact with the original validator process.

## 5. Step 4 — Migrate without original-operator consent

Quoted physical evidence:

- file path: `tools/testbed/m022_migrate.json`
- `chain_complete: true, sentinel_consistent: true`
- `bls_verified_commits: 3/3`
- `verdict: workload_d_replayability_pass`

The handoff also states:

- `Identical extraction from the migrated copy proves continuity survives the move.`
- `The original operator's LMDB, process, or API is not required at any step.`

Verdict for Step 4:

- pass

This satisfies the migratability and continuity-preservation requirements of
Phase `674`.

## 6. Combined row-7 verdict

Strong-exitability verdict:

- `row_7_strong_exitability_runtime_closure_verdict=pass`

Combined row-7 posture after `CW-3` and `CW-4`:

- censorship-resistance verdict: pass,
- strong-exitability verdict: pass,
- combined status: `row_7_combined_runtime_status=runtime_closed`

Row `7` is therefore runtime-closed at the end of `CW-4`.

This conclusion is allowed because both sub-obligations named in Phase `741`
now have committed runtime evidence and both sub-verdicts are pass.

## 7. Non-claims

This phase does **not** claim:

- any row-5 closure,
- any row-8 disposition,
- any Option B graduation-gate synthesis,
- any `CDL-017` ratification act,
- convergence-window closure.
