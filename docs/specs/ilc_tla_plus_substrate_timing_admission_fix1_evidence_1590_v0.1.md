# ILC TLA+ Substrate Timing/Admission Fix1 Evidence 1590 v0.1

**Phase:** 1590-Fix1 / QUORUM-INTERSECTION-HARDENING
**Date:** 2026-07-27
**Status:** COMPLETE
**Sensitivity:** SENSITIVE runtime hardening, authorized by `GO Phase 1590-Fix1`

## Verdict

Phase 1590-Fix1 closes the Phase 1590 TLA blocker. The Rust production quorum
threshold now uses the intersection-safe rule:

```text
f = floor((N - 1) / 3)
quorum_threshold(N) = N - f
```

This fixes the dynamic-admission counterexample found in Phase 1590, where a
newly admitted fifth validator allowed two size-3 quorums to intersect only at
the Byzantine validator.

## Runtime Change

| File | Change |
|------|--------|
| `ilc_consensus/src/validator.rs` | `quorum_threshold(n)` changed from `2f+1` shortcut to `n-f` intersection-safe threshold |
| `ilc_consensus/src/epoch_settlement.rs` | tests updated for N=5/N=6 and quorum-intersection invariant |
| `ilc_consensus/src/dag_audit_main.rs` | audit text updated to describe the hardened threshold |
| `tools/phase_1575h_live_quorum_preflight.py` | Python readiness helper updated to mirror Rust threshold |
| `tests/test_phase_1575h_live_quorum_preflight.py` | Python threshold expectations updated |
| `tests/test_phase_high002_phase_b_closure_gate.py` | legacy health test updated so it no longer preserves the unsafe formula |

## Threshold Table

| N | f | Old `2f+1` | New `N-f` | Disposition |
|---|---|------------|-----------|-------------|
| 1 | 0 | 1 | 1 | unchanged |
| 2 | 0 | 1 | 2 | hardened |
| 3 | 0 | 1 | 3 | hardened |
| 4 | 1 | 3 | 3 | unchanged public-RC N=4 |
| 5 | 1 | 3 | 4 | fixes Phase 1590 counterexample |
| 6 | 1 | 3 | 5 | fixes same intermediate-size class |
| 7 | 2 | 5 | 5 | unchanged |
| 8 | 2 | 5 | 6 | hardened |
| 9 | 2 | 5 | 7 | hardened |
| 10 | 3 | 7 | 7 | unchanged |

## TLA+ Fix

The Phase 1590 model was updated from:

```text
QuorumThreshold(n) == 2 * ((n - 1) \div 3) + 1
```

to:

```text
QuorumThreshold(n) == n - ((n - 1) \div 3)
```

The TLC config is bounded to one epoch and five timing values while preserving
dynamic admission/ejection and the exact N=5 counterexample surface. The model
also caps explored certificates at two; this is a safety-preserving reduction
because `SafetyNoDualCert` is violated by the first conflicting pair.

## Fresh TLC Result

Command:

```bash
/usr/local/Cellar/openjdk/25.0.2/libexec/openjdk.jdk/Contents/Home/bin/java \
  -cp tools/tla/tla2tools.jar \
  tlc2.TLC \
  -config docs/specs/tla/ilc_substrate_timing_admission_1590.cfg \
  -workers auto \
  docs/specs/tla/ilc_substrate_timing_admission_1590.tla
```

| Field | Value |
|-------|-------|
| TLC version | TLC2 Version 2026.04.22.172729 |
| Result | No error has been found |
| States generated | 1,031,138 |
| Distinct states | 255,483 |
| States left on queue | 0 |
| Search depth | 10 |
| Duration | 39 seconds |

## Artifact Hashes

| Artifact | SHA-256 |
|----------|---------|
| `ilc_consensus/src/validator.rs` | `d17e559b2c50f3b924b6f1a9ca3b7730e34fbfdbdec72848938059bae1dcc473` |
| `ilc_consensus/src/epoch_settlement.rs` | `72a0be150152e116d7286a1e2a6f5c4668e35647eb6300ff9aebe5955eff2681` |
| `tools/phase_1575h_live_quorum_preflight.py` | `574726254d13478e45caa001240f1a39c7b3afd7a6769ce4c3e42b9131f09e14` |
| `docs/specs/tla/ilc_substrate_timing_admission_1590.tla` | `f4e71b0421df33956d74feb7e8ace6a9069405376db4d7727aef62346ab2a86b` |
| `docs/specs/tla/ilc_substrate_timing_admission_1590.cfg` | `2f275fecef0b83b12ae6110c2fe920e4b0505ed653f4bca5da8ae4b830f46a46` |
| `tools/tla/ilc_substrate_timing_admission_1590_fix1.tlc.out` | `4d28d9eb4d0e58a4e99e4b49f682bebc1d191a9c43ffab9b769333d765bfca28` |

## Verification

| Check | Result |
|-------|--------|
| TLC hardened model | PASS — 1,031,138 generated states, depth 10 |
| Rust focused tests | PASS — `cargo test quorum_threshold --lib`, 2 passed |
| Rust library tests | PASS — `cargo test --lib`, 106 passed |
| Rust release build | PASS — `cargo build --release` with two pre-existing dead-code warnings in `node.rs` |
| Rust formatting | PASS — `cargo fmt --check` |
| Python readiness helper tests | PASS — `.venv/bin/pytest -q tests/test_phase_1575h_live_quorum_preflight.py`, 10 passed |

## Tokens

```text
quorum_intersection_hardened_phase_1590_fix1
tla_plus_timing_admission_checked_phase_1590
phase_1590_tla_blocker_closed_phase_1590_fix1
```

## Non-Claims

This phase changes quorum thresholding only. It does not activate validator
admission, bridge proposal ingress, public claimability, wallet transfer,
minting, public mirror publication, mainnet, or public RC.
