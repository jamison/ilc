# ILC DAG Censorship Bounds TLC Evidence 816 v0.1

**Status:** formal evidence artifact
**Date:** 2026-04-23
**Phase:** 816
**Owner lane:** G8 Window 811-822 pre-RC hardening

`tla_spec_a_maxround_widened_pre_rc`
`tla_spec_a_maxround12_default_gate_memory_bound`

## 1. Verification Target

This artifact records the widened-horizon rerun of:

- spec: `docs/specs/tla/ilc_dag_censorship_bounds.tla`
- cfg: `docs/specs/tla/ilc_dag_censorship_bounds.cfg`

The phase change is:

- `MaxRound = 5` -> `MaxRound = 12`

## 2. Default Gate Run Result

The canonical gate invocation was:

```bash
bash tools/run_tlc_m_series_gate.sh
```

That run used the script's default TLC invocation and reached:

- workers: `4`
- heap/offheap: `6144MB / 64MB`
- TLC version: `2026.04.22.172729`
- start time: `2026-04-23 18:46:54`

Before failure, Spec A progressed to:

- states generated: `988,097`
- distinct states: `152,701`
- queued states at last progress line: `57,008`
- liveness-graph distinct-state count at the failure frontier: `4,700,310`

The run did **not** report an invariant or property violation. It failed with:

`Error: Java ran out of memory during liveness checking.`

This is an environment/tooling ceiling under the default gate configuration,
not a discovered protocol counterexample.

## 3. Higher-Heap Follow-Up Probe

A single bounded retry was run directly with a larger heap:

```bash
JAVA_BIN="$(brew --prefix openjdk)/bin/java"
"$JAVA_BIN" -XX:+UseParallelGC -Xmx12g \
  -cp tools/tla/tla2tools.jar tlc2.TLC \
  -config docs/specs/tla/ilc_dag_censorship_bounds.cfg \
  -workers auto -deadlock \
  docs/specs/tla/ilc_dag_censorship_bounds.tla
```

That retry used approximately `10,923MB` heap and progressed materially beyond
the default failure frontier. Before it was manually stopped, it had reached:

- states generated: `1,721,283`
- distinct states: `250,158`
- queued states: `89,333`
- liveness-graph distinct-state count: `7,146,330`

No invariant or liveness violation had been reported at that point.

This does not count as a clean canonical gate pass because the retry was not
run to completion. It does, however, establish that the default failure mode is
heap-bound and that the widened model is still exploring cleanly at a higher
memory ceiling.

## 4. Honest Disposition

The honest Phase 816 result is:

- `tla_spec_a_maxround_widened_pre_rc`
- `tla_spec_a_maxround12_default_gate_memory_bound`

The widened model now exists and was exercised substantially beyond the old
`MaxRound=5` proof horizon. The remaining gap is TLC environment tuning for a
fully clean `MaxRound=12` liveness completion under a canonical repeatable gate.
