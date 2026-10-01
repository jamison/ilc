# IEC + K Context Tracking CDL Scope v0.1

**Status:** CDL scope candidate only
**Phase:** GAP-ADVERSARIAL-EPISTEMICS-REPORT-00
**Date:** 2026-10-01
**Sensitivity:** Non-sensitive scoping; no CDL opened

## 1. Motivation

SIM-LAUNDER-02H found three pairs that collapse in binary jury space while
remaining separable in graph space:

| Pair | Graph separation | Jury separation | Missing dimension |
|---|---:|---:|---|
| OBJECTIVE vs LAUNDERED | 0.7222 | 0.0003 | Independent provenance / cluster diversity |
| CONTEXTUAL vs SUBJECTIVE | 0.1247 | 0.0013 | Context structure |
| CONTESTED vs POPPERIAN | 0.1581 | 0.0228 | Survived refutation resistance |

SIM-LAUNDER-02C and 02F also show that raw reuse weight cannot distinguish
propagation from corroboration. RRW counts descendants; it does not count
independent origins.

## 2. Proposed Protocol Addition

Record `origin_id` and `context_id` per vote or attribution event.

- `origin_id`: independent origin ID for the evidence chain this vote or
  attribution descends from. Used to compute IEC.
- `context_id`: observer context under which this vote was cast. Used to compute
  K, the within-context and between-context agreement profile.

The addition should be made at the Python attribution layer first. It does not
require an initial Rust consensus change and must not alter settlement authority
without a later explicit runtime and governance phase.

## 3. IEC Definition

```text
IEC(x) = count of distinct origin_ids among votes for x
         where the origin has at least one surviving,
         non-refuted descendant

ELF(x) = RRW(x) / IEC(x)
```

High ELF means a claim has gained graph standing per unit of independent
evidence, which is the laundering-risk signal.

## 4. K Definition

```text
within_ctx(x)  = mean agreement among votes sharing the same context_id
between_ctx(x) = mean agreement across votes from different context_ids

K(x) = (within_ctx, between_ctx)
```

K has two components. It must not be collapsed into a single scalar during the
first CDL because SIM-LAUNDER-02G supports dimensional orthogonality.

## 5. Popperian Weight

```text
popperian_weight(x) = IEC(x) + 0.5 * survived_refutation_attempts(x)
```

The coefficient `0.5` is provisional. SIM-LAUNDER-02G confirmed the orthogonality
of refutation resistance, but did not optimize this coefficient.

## 6. Explicit Non-Claims

- The CDL does not replace `raw_reuse_weight`.
- The CDL does not collapse IEC, R, and K into a single `epistemic_score`.
- The CDL does not change the binary jury verdict mechanism.
- The CDL does not activate new economic flows.
- IEC is a ranking and diagnostic signal, not an ECU source.
- Fiedler behavioral partitioning is not required for IEC to function.
- This document does not open, ratify, or mutate the CDL register.

## 7. Dependencies

- CDL-109 Werner attribution bridge must remain ratified.
- `ilc_core/consensus/attribution_batch_bridge.py` is the live bridge extension
  point for attribution-batch schema work.
- Initial implementation should add and propagate `origin_id` and `context_id`
  in Python attribution artifacts.
- No Rust change is required for the initial IEC+K implementation unless a later
  phase binds these fields into consensus-critical settlement payloads.

## 8. Phase Sequencing

1. `GAP-ADVERSARIAL-EPISTEMICS-REPORT-00`: produce this scope document.
2. `GAP-IEC-K-CDL-OPEN-00`: sensitive CDL opening for IEC+K.
3. `GAP-IEC-K-IMPL-00`: non-sensitive runtime implementation after opening.
4. Test coverage phase alongside or within implementation, depending on blast
   radius.
5. `GAP-IEC-K-CDL-RATIFY-00`: sensitive ratification after verified runtime.
