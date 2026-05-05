# Persistent Rate Limiter Scope 1196 v0.1

**Phase:** 1196
**Date:** 2026-05-05
**Status:** scope committed — no runtime mutation

`persistent_rate_limiter_scope_committed_phase_1196`

---

## 1. Purpose

This phase addresses the RC2 persistent rate limiter gate by inspecting the current
rate-limiter surface and defining a concrete implementation plan. It does not mutate
runtime code because persistence affects restart-state semantics and protocol-time
boundaries.

---

## 2. Current Rate Limiter Surface

CDL-077 ratified WANT-HAVE/WANT-BLOCK two-phase fetch with an in-process per-identity
rate limiter:

- WANT-HAVE is an unrate-limited availability probe.
- WANT-BLOCK is rate-limited per `requester_id`.
- `WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10`.
- Over-limit result: HTTP 429 with token `fetch_rate_limit_exceeded`.

Runtime files:

- `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`
- `ilc_core/network/d2d/http_fetch_transport_runtime.py`

Current implementation:

- `FetchRateLimiter` stores buckets in process memory.
- Buckets are keyed by `requester_id`.
- Buckets do not survive process restart.
- The transport injects one limiter instance into WANT-BLOCK handling.

---

## 3. Persistence Gap

The RC2 gate asks for restart-surviving limiter state. The current implementation explicitly
does not provide that. Phase 900/904 CDL-077 chose the in-process limiter for the earlier RC
scope and deferred persistent cross-session limiting.

The persistence problem is not just "write the bucket dict to disk." A correct design must
answer:

1. What protocol-time source defines the limiter window after restart?
2. What is the canonical persisted schema?
3. How are corrupt or stale limiter-state files handled?
4. What privacy boundary applies to persisted requester IDs?
5. What pruning rule prevents unbounded persisted requester growth?
6. What atomic-write rule prevents partial writes from weakening the limiter?
7. Whether persistence is local operator policy or protocol-visible behavior.

---

## 4. Recommended Design

Introduce a small persistent limiter backend in a future implementation phase:

```text
persistent_fetch_rate_limiter_runtime_NNNN.v0.1
```

Recommended contract:

- Persist only hashed requester identifiers, not raw `requester_id`.
- Use validation-epoch counters or explicit caller-supplied epoch/window IDs, not wall-clock
  time as protocol truth.
- Canonical JSON state file with deterministic ordering and `allow_nan=False`.
- Atomic write via temp file + replace.
- Hard cap on tracked requester buckets.
- Fail closed on corrupt state only for WANT-BLOCK; WANT-HAVE remains available.
- Maintain the existing `fetch_rate_limit_exceeded` token.

---

## 5. Proposed State Schema

Minimum persisted schema:

```json
{
  "schema": "ilc.fetch_rate_limiter_state@v1",
  "runtime_version": "persistent_fetch_rate_limiter_runtime_NNNN.v0.1",
  "window_id": 123,
  "limit_per_window": 10,
  "requester_buckets": {
    "sha256:...": {
      "count": 4,
      "window_id": 123
    }
  }
}
```

Persistence must be deterministic:

- `json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))`
- no unordered set serialization;
- no wall-clock timestamps in hashed or canonical state.

---

## 6. Implementation Sequence

Recommended future sequence:

1. Add a pure state model and serialization helpers outside the HTTP transport.
2. Add deterministic load/save with corruption tokens.
3. Add hashed requester IDs.
4. Add max-bucket pruning.
5. Add direct unit tests for restart persistence.
6. Wire `HttpFetchTransportRuntime` to the persistent backend behind explicit config.
7. Keep in-memory limiter as default until the persistent backend passes restart tests.

---

## 7. Guardrails

- Do not use wall clock as protocol source of truth for persisted windows.
- Do not persist raw requester IDs.
- Do not accumulate unbounded requester buckets.
- Do not introduce predictable PRNG.
- Do not weaken WANT-BLOCK rate-limit behavior on corrupt state.
- Do not rate-limit WANT-HAVE unless a future CDL explicitly changes CDL-077.

---

## 8. Non-Claims

This phase does not:

- implement persistent rate limiting;
- mutate `ilc_core/`;
- change CDL-077;
- change WANT-HAVE or WANT-BLOCK semantics;
- introduce a runtime token;
- make a public launch claim.
