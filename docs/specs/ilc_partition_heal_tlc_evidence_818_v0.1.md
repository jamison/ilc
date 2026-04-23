# ILC Partition Heal TLC Evidence 818 v0.1

**Status:** formal evidence artifact
**Date:** 2026-04-23
**Phase:** 818
**Owner lane:** G8 Window 811-822 pre-RC hardening

`tla_spec_c_partition_heal_pre_rc`

## 1. Verification Target

This artifact records the TLC run for:

- spec: `docs/specs/tla/ilc_partition_heal.tla`
- cfg: `docs/specs/tla/ilc_partition_heal.cfg`

The run path was the canonical gate script:

```bash
bash tools/run_tlc_m_series_gate.sh
```

## 2. Checked Properties

The cfg checks:

- `TypeOK`
- `NoFork`
- `NoNewGlobalCommitDuringPartition`
- `EventualCommit`

These correspond directly to the M-015 safety and recovery claims.

## 3. TLC Execution Record

From `tools/tla/ilc_partition_heal.tlc.out`:

- TLC version: `2026.04.22.172729`
- workers: `4`
- heap/offheap: `6144MB / 64MB`
- start time: `2026-04-23 19:26:13`
- finish time: `2026-04-23 19:26:15`
- states generated: `5,577`
- distinct states: `867`
- search depth: `13`
- result: `Model checking completed. No error has been found.`

TLC also records:

- satisfiability branches: `2`
- optimistic fingerprint collision estimate: `2.2E-13`

## 4. Disposition

Spec C now has a clean reproducible TLC evidence artifact on disk for the
partition/heal model. This satisfies the bounded pre-RC formal check for the
M-015-style recovery path.
