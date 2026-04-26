# ILC Phase 842 — HIGH-002 Production Hardening Planning Brief v0.1

**Phase:** 842
**Date:** 2026-04-26
**Window:** 839–843

`high_002_production_hardening_planning_842_complete`
`high_002_not_a_testnet_blocker_confirmed`
`high_002_mandatory_before_production_N_ge_4_F_ge_1`

## 1. HIGH-002 Definition

**Finding:** HIGH-002 — signer-subset liveness limitation.

All `N` validators must be in the active signer set for
`process_epoch_checkpoint` to reach finality. Under the current implementation,
if any validator is offline at epoch-close, the epoch-close attestation stalls.
This is an all-N quorum requirement for a liveness-critical path.

**Accepted scope:**

- Not a safety bug — no double-finalization or equivocation is possible.
- Not a correctness bug at testnet scale (`N=4`, controlled environment).
- A mandatory fix before independently operated production validator sets or
  at `N≥4`, `F≥1` production hardening.

**Current posture:** `high_002_debt_noted_not_a_testnet_blocker`

## 2. Scope of the problem

The Mysticeti protocol specifies BFT safety threshold `f = floor((N-1)/3)`.
At `N=4`, `f=1`. A production deployment must tolerate one Byzantine or offline
validator without stalling liveness.

The current `process_epoch_checkpoint` path requires all `N` validators to
contribute signatures before the epoch-close record is committed. This is
stronger than BFT safety requires and weaker than BFT liveness requires.

**Impact surface:**

| Scenario | Impact |
|----------|--------|
| One validator offline at epoch-close | Epoch stalls until it recovers |
| One validator permanently removed | Epoch stalls until governance eviction + key rotation |
| Partition of 1-of-4 validators | All ECU attribution and settlement halts |
| Byzantine validator withholds signature | Same as offline — stall, not safety failure |

## 3. Root cause

`process_epoch_checkpoint` in `ilc_consensus/src/validator/` accumulates
signatures from all validators in the active validator set and only commits
when the count equals `N`. A BFT-correct implementation would commit when the
count reaches `2f+1` (a quorum majority), not `N`.

The fix is a threshold change: `signatures.len() >= quorum_threshold(N)` where
`quorum_threshold(N) = 2 * floor((N-1)/3) + 1`.

At `N=4`: `f=1`, `quorum_threshold = 3`. Three-of-four signatures are
sufficient to commit. One offline or Byzantine validator does not stall
liveness.

## 4. Implementation plan

### Phase A — Rust consensus change (1 phase)

1. Replace the all-N guard in `process_epoch_checkpoint` with
   `signatures.len() >= quorum_threshold(N)`.
2. Implement `fn quorum_threshold(n: usize) -> usize { 2 * ((n - 1) / 3) + 1 }`.
3. Verify at N=4: threshold=3, N=7: threshold=5, N=10: threshold=7.
4. Update the settlement-path gate (`check_settlement_path_gate`) to emit a
   liveness warning when `N < 4` (f=0) — already present for HIGH-002 via
   `sec_warn_settlement_gate_f_zero`.
5. Rust tests: quorum_threshold correctness across N=1..10, stall-no-longer
   at N=4 with 3 signers, safety preserved (2 signers insufficient).

### Phase B — Adversarial hardening validation (1 phase, M-track)

1. Run the M-019 adversarial harness against the patched binary.
2. Verify that a single offline validator no longer stalls epoch-close.
3. Verify that equivocation safety (SafetyNoDualCert) remains unaffected.
4. Record as an M-track phase.

### Sequencing

Phase A (Rust change + tests) is a code-side phase. It requires:
- No CDL mutation (HIGH-002 is an implementation constraint, not a
  constitutional question).
- No `ilc_core/` mutation.
- The Phase 826 settlement-path gate comment referencing HIGH-002 must be
  updated to reflect the fix.

Phase B (M-track validation) requires the Rust binary to be rebuilt and
deployed to the M-009 testbed.

**Gate dependency:** Phase A must complete before the operator can honestly
pull the first-validator human gate at production N≥4, F≥1 scale. At
controlled testnet scale (`N=4`, operators known), Phase 826 §3 explicitly
permits deployment while HIGH-002 remains open.

## 5. Sequencing relative to other work

| Dependency | Relationship |
|------------|-------------|
| Option B gate: go (Phase 841) | HIGH-002 fix is not a gate condition for Option B selectability |
| First-validator human gate (Phase 826) | HIGH-002 fix is mandatory before production scale but explicitly not blocking controlled testnet deployment |
| Row 5 SIM-LEAKAGE-03 | Independent; no dependency |
| CDL-069 identity system | Independent; HIGH-002 is a consensus liveness issue, not an identity issue |

## 6. Authorized next actions

Code-side Phase A is authorized as the next `ilc_consensus/` work after the
current window closes. It does not require a new CDL and does not require a
new ADR. It is a targeted implementation fix with a clear pass condition.

`high_002_phase_a_rust_consensus_fix_authorized_post_window_839_843`
`high_002_phase_b_m_track_validation_authorized_after_phase_a`
