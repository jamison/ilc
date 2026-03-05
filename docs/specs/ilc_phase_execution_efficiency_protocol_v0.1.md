# ILC Phase Execution Efficiency Protocol v0.1

Status: non-normative execution operations note
Date: 2026-03-05
Owner lane: G8 execution operations

## 1. Purpose

Reduce repeated baseline runtime cost while preserving safety constraints in phase execution.

This protocol optimizes orchestration overhead, not assurance requirements.

## 2. Feature vs inefficiency

Long baseline checks are partly intentional:
- chained closure-gate regressions,
- mutation canary execution,
- commit-anchored scope guards,
- cross-window contract carry-forward.

Inefficiency exists when the same expensive checks run multiple times against the same HEAD and tracked working-tree state.

## 3. Optimization policy (effective immediately)

1. Keep all required checks.
2. Run expensive baseline bundles once per unchanged state.
3. Reuse baseline result only when all are unchanged:
   - `git rev-parse HEAD`,
   - tracked working-tree status hash,
   - command-list hash.
4. Any tracked mutation invalidates cache.
5. Non-sensitive quick checks still run every time:
   - `git diff` scope checks,
   - env var checks,
   - artifact existence checks.

## 4. Helper tool

Use:

```bash
tools/run_phase_baseline_once.sh \
  --key phase359-entry \
  --cmd "python3 -m pytest tests/test_window_348_357_closure_gate_357.py -q" \
  --cmd "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_window_338_347_closure_gate_347.py tests/test_window_348_357_closure_gate_357.py -q"
```

Force refresh:

```bash
tools/run_phase_baseline_once.sh \
  --key phase359-entry \
  --force \
  --cmd "python3 -m pytest tests/test_window_348_357_closure_gate_357.py -q" \
  --cmd "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_window_338_347_closure_gate_347.py tests/test_window_348_357_closure_gate_357.py -q"
```

Cache stamp path:
- `out/monitoring/phase_baseline_cache_<key>.env`

## 5. Guardrails

- Cache is valid only for the exact tracked state and command bundle.
- Do not reuse cache across phase boundaries unless key and state both match.
- If mutation canary dirties tracked files, restore first, then rerun (or force-refresh) baseline.
- This protocol does not change per-phase prompt contracts.

## 6. Next application

Apply this protocol starting Phase 359 entry checks and carry forward to Phase 360-367 execution.
