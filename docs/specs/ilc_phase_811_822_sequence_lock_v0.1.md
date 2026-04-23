# ILC Phase 811-822 Sequence Lock: Option B Selection and Pre-RC Hardening

**Date:** 2026-04-23
**Window:** 811-822
**Status:** locked

`phase_811_822_sequence_lock_written`
`window_811_822_option_b_selection_and_pre_rc_hardening_locked`

## 1. Purpose

This window performs four tightly ordered workstreams:

1. resolve the ADR-0028/checklist governance inconsistency,
2. record Option B selection after that amendment path is committed,
3. deliver the bounded TLA+ pre-RC hardening items,
4. close SEC-007a and SEC-007b maintenance.

Human authorization for Option B selection was given on 2026-04-23, but this
window may not record the selection until the Phase 812 ADR amendment and the
Phase 813 checklist v0.2 update exist first.

## 2. Locked Decisions

1. This window may record Option B selection only after the Phase 812 ADR
   amendment and the Phase 813 checklist v0.2 artifact are committed in this
   window.
2. This window must not mutate any CDL row.
3. This window must not deploy validators, rotate the live settlement path, or
   claim production readiness.
4. TLA+ changes are bounded to:
   - widening Spec A `MaxRound`,
   - adding or honestly deferring `SafetyNoDualCert` coverage,
   - running Spec C and recording the honest result,
   - publishing refinement notes.
5. SEC-007a is limited to vendoring `protoc` for the current `tonic 0.11`
   toolchain; no broader tonic/prost upgrade is opened here.
6. SEC-007b is disposition-only. It does not authorize new randomness use in
   sensitive runtime paths.
7. HIGH-002 is documented carry-forward only. This window does not fix it.
8. Row 5 remains open as a required pre-public-RC obligation. This window does
   not start the row-5 mechanism-choice or implementation lane.

## 3. Phase Plan

| Phase | Work |
|---:|---|
| 811 | Sequence lock acknowledgment |
| 812 | ADR-0028 graduation amendment |
| 813 | Checklist v0.2 post-convergence update |
| 814 | Option B selection record + checklist v0.3 |
| 815 | Mysticeti activation scope |
| 816 | TLA Spec A `MaxRound` widening |
| 817 | `SafetyNoDualCert` coverage / honest deferral |
| 818 | TLA Spec C run + evidence |
| 819 | TLA-to-Rust refinement notes |
| 820 | SEC-007a protoc vendoring + SEC-007b rand disposition |
| 821 | Coherence report + capsule v5.12 |
| 822 | Closure gate |

## 4. Non-Claims

This window does not authorize:

- live settlement-path rotation,
- first non-Genesis validator deployment,
- row-5 runtime closure,
- HIGH-002 remediation,
- Tier-2 `ilc_dag_audit` archive mode,
- TLAPS,
- Spec D,
- any CDL mutation.

`window_811_822_no_cdl_mutation_locked`
