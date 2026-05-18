# ILC Spec D TLC Evidence — Epoch Checkpoint SafetyNoDualCert
# Phase 1385a Strike Force

**Phase:** 1385a (Strike Force — closes safetynodualcert_deferred_with_authority_phase_1385)
**Date:** 2026-05-18
**Status:** complete

## Tokens

```text
safetynodualcert_spec_d_proven_epoch_checkpoint
safetynodualcert_deferred_with_authority_phase_1385_closed_1385a
tla_spec_d_epoch_checkpoint_tlc_clean
```

## Spec D File Locations

| Artifact | Path |
|----------|------|
| TLA+ specification | `docs/specs/tla/ilc_epoch_checkpoint_safety.tla` |
| TLC configuration | `docs/specs/tla/ilc_epoch_checkpoint_safety.cfg` |
| TLC output log | `tools/tla/ilc_epoch_checkpoint_safety.tlc.out` |

## TLC Run Summary

| Parameter | Value |
|-----------|-------|
| TLC version | TLC2 Version 2026.04.22.172729 (rev: 6320a09) |
| Run date | 2026-05-18 18:01:47 – 18:09:28 |
| Duration | 7 min 41 s |
| Workers | 4 (auto) |
| N (validators) | 4 |
| F (Byzantine) | 1 |
| ByzantineSet | {4} |
| Epochs | {1, 2, 3} |
| Roots | {"root_a", "root_b"} |
| States generated | 67,020,103 |
| Distinct states | 7,931,925 |
| States left on queue | 0 (exhaustive) |
| Search depth | 28 |
| Result | **No error has been found** |

## Invariants Checked

| Invariant | Result |
|-----------|--------|
| TypeOK | PASS — no violation |
| SafetyNoDualCert | PASS — no dual certificate found |
| MonotonicCommit | PASS — epoch chain strictly increasing |
| CertifiedSubsetSigned | PASS — committed implies certified |
| SigsSubsetValidators | PASS — sig sets well-formed |

## What the Model Checks

Spec D models the ILC epoch-checkpoint BFT round as implemented in
`ilc_consensus/src/epoch_settlement.rs::process_epoch_checkpoint`.

Key protocol elements modelled:

1. **Quorum threshold** — `2f+1` signers required for certification,
   matching `quorum_threshold(N) = 2*floor((N-1)/3)+1` in `validator.rs`.
2. **Honest signing rule** — an honest validator signs at most one
   checkpoint per epoch; signing a conflicting checkpoint is Byzantine
   behaviour. Models the `process_epoch_checkpoint` one-vote-per-epoch
   contract.
3. **Byzantine equivocation** — Byzantine validators can sign both sides
   of a conflicting pair, modelling the strongest adversarial behaviour
   against `SafetyNoDualCert`.
4. **Certification** — a checkpoint becomes certified when its signature
   count reaches `Threshold`.
5. **Strict sequential monotonicity** — a certified checkpoint can only
   be committed when its epoch equals `LastCommittedEpoch + 1`, modelling
   SEC-FIX-02 (`epoch == current_epoch + 1` guard inside the LMDB write
   transaction).

## Proof Sketch (Parameter-Independent)

TLC verifies the invariant for the bounded model (N=4, F=1, Epochs={1,2,3}).
The safety argument holds for arbitrary N > 3F:

Suppose c1 and c2 conflict (c1.epoch = c2.epoch, c1.root ≠ c2.root) and
both are certified, meaning |sigs[c1]| >= 2f+1 and |sigs[c2]| >= 2f+1.
Combined signatures: 2*(2f+1) = 4f+2 (counting multiplicity).
There are only N validators (N >= 3f+1 under N > 3f).
At most F Byzantine validators can double-sign (equivocate).
Honest signers required: at least (4f+2) - F = 3f+2.
Available honest validators: N - F >= 2f+1.
3f+2 > 2f+1 for all F >= 0 — contradiction.
Therefore dual certification is impossible under N > 3F.

## Relationship to Spec B

Spec B (`ilc_ecu_fast_path_bcast.tla`) proved SafetyNoDualCert for
owned-object transfers: a single object, two parties, one ByzCB broadcast
round. State space: ~201,000 states.

Spec D (`ilc_epoch_checkpoint_safety.tla`) proves SafetyNoDualCert for
shared-object epoch checkpoints: N validators, sequential epoch chain,
strict +1 monotonicity, full quorum certification + commit. State space:
~67 million states (exhaustive). These are distinct properties; Spec B
evidence was explicitly not sufficient for the Spec D claim (see Phase 1385
disposition document).

## Implementation Correspondence

| Spec D element | Rust implementation |
|----------------|---------------------|
| `Threshold = 2*F+1` | `quorum_threshold(N)` in `validator.rs:13` |
| Duplicate signer rejection (implicit in honest rule) | `seen.insert(signer_id)` duplicate check, `epoch_settlement.rs:246` |
| Checkpoint certification | `process_epoch_checkpoint` BLS AggSig verify, `epoch_settlement.rs:273` |
| `epoch == LastCommittedEpoch + 1` | SEC-FIX-02 sentinel guard, `epoch_settlement.rs:311` |
| Duplicate-epoch rejection | LMDB `txn.get` check after monotonicity guard, `epoch_settlement.rs:317` |

## Phase 1385 Deferral Closure

Phase 1385 recorded `safetynodualcert_deferred_with_authority_phase_1385`
with carry-forward authority to Phases 1387–1389 and a bounded obligation:
"any phase that needs a formal epoch-checkpoint/shared-object dual-cert
claim must stop and route to a dedicated Spec D or equivalent."

Phase 1385a (this Strike Force) satisfies that obligation. The carry-forward
deferral token is superseded by `safetynodualcert_spec_d_proven_epoch_checkpoint`.
