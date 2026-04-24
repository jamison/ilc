# ILC Row-5 B-Impl Commissioning Spec v0.1

**Phase:** B-5
**Date:** 2026-04-24
**Owner:** local reviewer implementation lane
**Status:** commissioned

`row5_b_impl_commissioning_spec_published`
`row5_b_impl_commissioned_local_reviewer`

## 1. Scope

This document commissions the Row-5 implementation tranche that follows the
B-Scope mechanism lock.

Codex does not implement B-Impl in this phase. Codex defines the bounded
runtime obligations so the local reviewer can execute them against the already
selected mechanism:

- primary: `k=30`, `rolling_threshold`, `release_jitter_epochs=3`, `bounded_hold`
- fallback: `k=20`, `rolling_threshold`, `release_jitter_epochs=3`, `bounded_hold`

The intended target remains the simulation-derived recommendation:

- `A<=0.15`
- `B<=0.15`
- `C<=0.05`

That target remains pending live confirmation via `SIM-LEAKAGE-03`.

## 2. Existing Groundwork (Do Not Re-Implement)

The following carry-forward groundwork already exists and should be consumed,
not rebuilt:

- [`TransferClass`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/types.rs)
- [`ExpressConsent`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/types.rs)
- [`ECUTransfer.transfer_class`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/types.rs)

Those fields are already covered by the sender signature and already propagate
through the touched Rust surfaces.

## 3. Implementation Obligations

### 3.1 Rolling group construction in submission path

Integrate rolling group construction into the transfer submission path.

Entry point:

- [`handle_broadcast_honest`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/node.rs)

Required routing behavior:

- `Contribution` transfers always enter the privacy lane accumulator
- `Payment` transfers default to the same privacy lane
- `Payment { express: Some(...) }` with
  `agent_acknowledged_timing_disclosure: true` bypasses directly to the express
  fast path

### 3.2 Deferred release queue with jitter scheduling

Add the deferred release queue required by the locked mechanism.

Expected shape:

```rust
Vec<(release_epoch: EpochSeq, transfers: Vec<ECUTransfer>, contributors: Vec<AgentID>)>
```

Required rule:

- when a k-group completes, compute
  `release_epoch = current_epoch + rng.randint(0, J)` with `J=3`
- flush the queue on each epoch tick

### 3.3 bounded_hold carry-over with max-wait enforcement

Transfers that do not fill a complete k-group within `max_wait` must still
settle.

Required rule:

- force-release the partial group after `max_wait`
- do not fall back to single-contributor release
- preserve the largest partial anonymity set available at release time

### 3.4 Group-fill monitoring and fallback activation

The runtime must monitor fill quality for the `k=30` primary lane.

Required rule:

- emit a metric or alert when `k=30` groups fail to fill within `1.5x max_wait`
- activate the `k=20` fallback automatically when the failure rate exceeds `5%`
  of windows

### 3.5 Force-release degraded-anonymity notification

Contributors whose transfers settle by forced partial-group release must receive
an explicit degraded-anonymity signal.

Required rule:

- expose a flag or receipt field indicating the anonymity set was smaller than
  the nominal `k`
- notification-path mechanics may be finalized in B-Impl Phase 3, but the
  requirement is already locked here

### 3.6 Live instrumentation for SIM-LEAKAGE-03

Expose the metrics required by the live evaluation lane.

Minimum metrics:

- per-epoch group fill rate
- observed jitter distribution
- force-release count
- anonymity-set size histogram per settled batch

These are the metrics `SIM-LEAKAGE-03` must consume against the M-009 testbed
when the runtime closure window opens.

## 4. Parallel-Lane Ownership

B-Impl Phases 1–3 are commissioned to the local reviewer, not Codex.

Codex’s B-5 responsibility is complete when:

- the mechanism lock is published,
- these six obligations are scoped clearly,
- the planning canon records Row 5 as `spec_closed_runtime_pending`.

## 5. Boundaries

This commissioning spec does not:

- claim Row 5 runtime closure,
- run `SIM-LEAKAGE-03`,
- mutate any CDL,
- change the Option B graduation posture.
