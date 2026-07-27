# ILC TLA+ Substrate Timing/Admission Evidence 1590 v0.1

**Phase:** 1590 / GAP-SUBSTRATE-TLA
**Date:** 2026-07-27
**Status:** BLOCKED — TLC found `SafetyNoDualCert` counterexample under dynamic admission
**Sensitivity:** NON-SENSITIVE evidence only

## Verdict

Phase 1590 did not complete. The TLA+ model was written and TLC was run with
fresh local output, but the model found a real safety counterexample against
the current Rust quorum threshold when the active validator set grows from 4
to 5.

Do not emit `tla_plus_timing_admission_checked_phase_1590` until this is fixed
and TLC reruns cleanly.

## Source Correspondence

| Source | Relevant fact |
|--------|---------------|
| `ilc_consensus/src/validator.rs:20-22` | `quorum_threshold(n) = 2 * floor((n - 1) / 3) + 1` |
| `ilc_consensus/src/validator.rs:76-114` | `admit_validator()` can rebuild the validator set at a new size |
| `ilc_consensus/src/validator.rs:116-135` | `eject_validator()` can rebuild the validator set after removal |
| `ilc_consensus/src/epoch_settlement.rs:251-255` | `process_epoch_checkpoint()` accepts signer count `>= quorum_threshold(n)` |
| `ilc_consensus/src/epoch_settlement.rs:297-309` | mainnet future `not_before_unix_ms` skew guard |
| `ilc_consensus/src/epoch_settlement.rs:342-347` | strict sequential epoch guard |
| `ilc_consensus/src/epoch_settlement.rs:349-360` | mainnet minimum epoch duration guard begins from previous checkpoint |
| `docs/specs/tla/ilc_epoch_checkpoint_safety.tla` | Phase 1385a fixed-set Spec D dual-certificate model |

## Artifacts

| Artifact | Path | SHA-256 |
|----------|------|---------|
| TLA+ model | `docs/specs/tla/ilc_substrate_timing_admission_1590.tla` | `8b66d4c40595571d79957f05637905b1a4ccf336aed42563b677c94d6c6f347c` |
| TLC config | `docs/specs/tla/ilc_substrate_timing_admission_1590.cfg` | `a66e70be44871b0a83867a2054d7d3c1673fe0d47a5ade14fb491888d8b6f780` |
| TLC output | `tools/tla/ilc_substrate_timing_admission_1590.tlc.out` | `82b4acd6611a383aaf52d929911d672e37806524da30d24b94ffaeb44c4c2fb1` |

## TLC Run

Command:

```bash
/usr/local/Cellar/openjdk/25.0.2/libexec/openjdk.jdk/Contents/Home/bin/java \
  -cp tools/tla/tla2tools.jar \
  tlc2.TLC \
  -config docs/specs/tla/ilc_substrate_timing_admission_1590.cfg \
  -workers auto \
  docs/specs/tla/ilc_substrate_timing_admission_1590.tla
```

Result:

| Field | Value |
|-------|-------|
| TLC version | TLC2 Version 2026.04.22.172729 |
| Result | `Invariant SafetyNoDualCert is violated` |
| States generated before violation | 10,144 |
| Distinct states before violation | 5,666 |
| Depth | 6 |

## Counterexample Summary

The model starts with validators `{1, 2, 3, 4}`, then admits validator `5`.
With active set size `N=5`, the current Rust threshold is:

```text
quorum_threshold(5) = 2 * floor((5 - 1) / 3) + 1 = 3
```

TLC then finds two conflicting epoch-1 certificates:

| Root | Signers |
|------|---------|
| `root_a` | `{1, 2, 5}` |
| `root_b` | `{3, 4, 5}` |

The two quorums intersect only at validator `5`. If validator `5` is Byzantine,
no honest validator double-signs, but both conflicting roots satisfy the current
`>= 3` threshold. This violates `SafetyNoDualCert`.

## Interpretation

The Phase 1385a fixed-set Spec D proof remains valid for the specific fixed
configuration it checked (`N=4`, `F=1`, threshold `3`). Phase 1590 shows that
the old proof does not automatically carry through dynamic admission.

The issue is not timing. The counterexample arises from quorum intersection
after validator-set size changes. For validator-set sizes where `N != 3f + 1`,
`2f + 1` can be too low to guarantee honest quorum intersection.

## Recommended Fix

Recommended fix path: replace the production quorum threshold with an
intersection-safe rule:

```text
f = floor((n - 1) / 3)
quorum_threshold(n) = n - f
```

This preserves current values at `N = 4, 7, 10` and raises the threshold for
intermediate sizes:

| N | Current `2f+1` | Recommended `n-f` |
|---|----------------|-------------------|
| 4 | 3 | 3 |
| 5 | 3 | 4 |
| 6 | 3 | 5 |
| 7 | 5 | 5 |
| 8 | 5 | 6 |
| 9 | 5 | 7 |
| 10 | 7 | 7 |

Alternative fix path: constrain validator admission so public-RC validator-set
sizes may only be `3f + 1` sizes such as 4, 7, 10. This is less desirable
because it complicates dynamic discovery and admission.

## Required Follow-Up

Create a SENSITIVE Fix phase before Phase 1590 can be marked complete:

```text
GO Phase 1590-Fix1 QUORUM-INTERSECTION-HARDENING
```

That phase should:

1. Patch Rust quorum logic or admission constraints.
2. Add Rust tests for `N=5` and `N=6` dual-certificate resistance.
3. Update the TLA+ model to the hardened rule.
4. Rerun TLC and require a clean result.
5. Only then emit `tla_plus_timing_admission_checked_phase_1590`.

## Non-Claims

No Rust runtime code was changed. No validator admission guard was cleared. No
bridge code was activated. No wallet, settlement, public mirror, mainnet, or
public-RC action occurred.
