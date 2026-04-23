# ILC Row-5 Evaluation 780 v0.1

**Phase:** 780  
**Window:** 775-782  
**Date:** 2026-04-23  
**Status:** complete

`row_5_honest_nonclosure_verdict=bands_not_met`

## 1. Run 2 recall summary (all three variants)

Phase 780 reads the committed Phase 779 Run 2 artifact directly.

Recorded Run 2 values:

- Variant A:
  - `500ms`: `0.8888888888888888`
  - `1000ms`: `0.7777777777777778`
  - best-case calibration point: `1000ms`
- Variant B:
  - observed recall: `0.0`
  - structural recall: `1.0`
- Variant C:
  - structural recall: `1.0`

Run 2 also recorded a delivery shortfall at both calibration points:

- client-side submission successes: `20 / 20`
- validator-1 final-destination ack lines: `18 / 20`

Run 2 also records `variant_a_scoring_posture=conservative_upper_bound_from_order_and_version_alignment`.
Because the post-redaction validator log no longer carries ground-truth sender
identity, the Variant A value is conservative for closure: even the upper-bound
order/version score fails the commissioned band.

## 2. Band assessment (pass / fail per variant)

| Variant | Evaluated value | Threshold | Pass / Fail |
|---|---:|---:|---|
| Variant A | `0.7777777777777778` | `≤ 0.60` | **FAIL** |
| Variant B (structural) | `1.0` | `≤ 0.45` | **FAIL** |
| Variant C (structural) | `1.0` | `≤ 0.45` | **FAIL** |

Residual recall values that keep row 5 open:

- Variant A residual recall: `0.7777777777777778`
- Variant B residual structural recall: `1.0`
- Variant C residual structural recall: `1.0`

Result: **`0 / 3` bands met**.

## 3. Verdict

Row 5 does **not** close in Phase 780.

The correct verdict is:

- `row_5_honest_nonclosure_verdict=bands_not_met`

Row 5 therefore remains:

- `spec_closed_runtime_pending`

This is the required honest outcome. The window may not claim row closure
because all three Run 2 bands still fail.

## 4. Residual gap (if non-closure)

Residual mechanism gaps by variant:

- **Variant A**: the current Layer-2 transport is fixed-path relay forwarding
  plus a per-submission delay. It is not a true mixing or shared-batch
  mechanism, so deterministic order correlation survives at validator-1. The
  measured Variant A value is a conservative upper bound after redaction, and
  that upper bound still fails. The same run also showed `18 / 20`
  final-destination acknowledgements, so the measured transport point is not
  clean enough to recommend as a default.
- **Variant B**: the gRPC balance surface still exposes structural recall `1.0`.
  Row 5 cannot close while hosted balance polling remains directly linking.
- **Variant C**: public epoch-lineage remains structurally linking at `1.0`.
  Relay forwarding does not change the long-term lineage surface.

## 5. ZK nullifier long-term path

The long-term row-5 carry-forward path remains a ZK nullifier / selective disclosure overlay:

- keep routing and timing metadata outside `TransferCertificate`,
- add privacy-preserving linkage suppression at the read-surface layer,
- preserve public receipts and challengeability while suppressing direct sender
  linkage,
- apply the nullifier-style overlay to the epoch / balance observability
  surfaces rather than claiming they are already private.

This path is named here explicitly. It is **not** implemented in this window.

## 6. Observability floor confirmation

Phase 780 confirms that the honest non-closure verdict does **not** imply any
observability-floor violation:

- receipts remain discoverable,
- lineage remains legible,
- challengeability remains preserved,
- bounded human auditability remains intact.

The window changed the submission path and node-local logging behavior. It did
not remove the public receipt, lineage, or challenge surfaces locked by the
Phase 679 observability floor.
