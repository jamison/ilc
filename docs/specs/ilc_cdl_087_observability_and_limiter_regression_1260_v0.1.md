# ILC CDL-087 Observability and Limiter Regression 1260 v0.1

**Date:** 2026-05-08
**Phase:** 1260
**Status:** local observability and limiter regression evidence
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
cdl_087_observability_collection_window_phase_1260.v0.1
cdl_077_rate_limiter_final_regression_recorded_phase_1260
cdl_087_ratification_readiness_verdict_recorded_phase_1260
no_cdl_087_ratification_phase_1260
```

## 1. Scope and Verdict

Phase 1260 records local evidence for CDL-087 Condition 4 and final Condition 5
regression:

- exact CDL-087 Section 6 observability signal validation;
- one local collection-window artifact surface keyed by epoch sequence;
- no per-requester dossier output;
- persistent CDL-077 limiter final regression;
- a readiness verdict for later sensitive CDL-087 ratification review.

Implementation:

```text
ilc_core/network/d2d/cdl087_observability.py
```

Focused tests:

```text
tests/test_phase_1260_cdl087_observability_and_limiter_regression.py
```

Readiness verdict:

```text
cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review
```

This verdict does not ratify CDL-087. It means Phases 1258-1260 have recorded
local evidence sufficient to justify a later sensitive review phase if the human
authorizes it.

## 2. Observability Evidence

The local artifact builder validates the exact CDL-087 Section 6 signal names:

```text
fetch_requests_by_tier
want_have_hit_rate
want_have_miss_rate
want_block_success_count
want_block_error_404
want_block_error_429
want_block_error_400
cache_hit_rate_tier_a
bytes_served_by_tier
non_cacheable_request_volume
circuit_breaker_activations
serve_events_credited_cdl_078
```

The builder records:

- `epoch_sequence_axis=protocol_epoch_sequence`;
- `wall_clock_time_included=false`;
- `per_requester_dossiers_included=false`;
- canonical JSON export with `sort_keys=True`, compact separators, and
  `allow_nan=False`.

The builder rejects missing signals, unexpected signals, duplicate epoch
sequences, float payload values, and any signal tree containing requester-level
keys.

## 3. Limiter Regression

`record_cdl077_limiter_regression()` exercises `PersistentFetchRateLimiter` and
records that:

- all requests within the configured limit are allowed;
- the over-limit request is rejected;
- the next epoch/window counter allows requests again;
- the evidence is bound to `persistent_fetch_rate_limiter_runtime_1202.v0.1`.

The final regression token is:

```text
cdl_077_rate_limiter_final_regression_recorded_phase_1260
```

## 4. Condition Status

| CDL-087 condition | Phase 1260 status |
|-------------------|-------------------|
| Condition 2 - Tier A/B/C classification | Local evidence recorded in Phase 1259. |
| Condition 3 - bootstrap snapshot builder/verifier | Local evidence recorded in Phase 1259. |
| Condition 4 - production-candidate observability collection | Local collection-window artifact surface recorded in Phase 1260. |
| Condition 5 - CDL-077 limiter preservation | Final local regression recorded in Phase 1260. |
| Condition 6 - fetch-incentive projection / credit bridge | Remains projection-level satisfied from prior evidence and must be rechecked in any sensitive ratification review. |

## 5. Non-Authorization Boundary

Phase 1260 does not authorize:

- CDL-087 ratification;
- CDL register mutation;
- CDL-088 opening;
- public fetch serving;
- public sidecar/projection serving;
- public P2P exposure;
- per-requester dossiers;
- public RC claim;
- public repository publication;
- public claimability activation;
- ECU minting;
- ILC settlement activation;
- release-key generation;
- release envelope production;
- v0.2 signing.

## 6. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/network/d2d/cdl087_observability.py -> transport/cdl087
graph_delta=support_tests_added:tests/test_phase_1260_cdl087_observability_and_limiter_regression.py -> validation
graph_delta=support_only:docs/specs/ilc_cdl_087_observability_and_limiter_regression_1260_v0.1.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1260_cdl087_observability_and_limiter_regression_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

## 7. Next Phase

Phase 1261 remains the next locked phase:

```text
sidecar_projection_endpoint_boundary_phase_1261.v0.1
```
