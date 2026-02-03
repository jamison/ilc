# Commit.Epoch Economics v0.1

**Version:** 0.1  
**Status:** DRAFT  
**Date:** 2026-02-02

---

## 1. Overview

This document defines the economic semantics tied to `commit.epoch` events in the ILC protocol. The `commit.epoch` event gates all **ledger settlement** (rewards distribution, decay application, consolidation). No ledger settlement occurs outside of `commit.epoch`.

**Note:** Control-plane updates (benchmark results, trust tiers, routing parameters) may occur at epoch start and are logged via `epoch_config`. These are non-ledger operations.

**Scope:** This spec covers:
- How epoch finalization triggers economic effects
- Reward pool mechanics and decay
- Stake consolidation rules
- Rollback and conflict resolution

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Epoch Reward Pool** | The total rewards available for distribution in a given epoch. Sourced from `commit.epoch.summary.reward_total`. |
| **Decay Window** | Number of epochs after which unclaimed rewards expire. Default: 2 epochs. |
| **Consolidation** | The process of finalizing stake changes at epoch boundaries. |
| **Active Stake Base** | Total staked value participating in the epoch. Sourced from `commit.epoch.summary.stake_total`. |
| **ECU** | Economic Currency Unit. Abstract unit for reward_total and stake_total. Not pegged to any external currency. |
| **Settlement** | The act of distributing rewards and applying decay at epoch finalization. |

---

## 3. Field Alignment to commit.epoch Event Schema

| Event Field | Economic Meaning | Unit |
|-------------|------------------|------|
| `summary.reward_total` | Epoch reward pool | ECU |
| `summary.stake_total` | Active stake base | ECU |
| `finalization_state` | Settlement state (committed, rolled_back, superseded) | Enum |
| `epoch_index` | Monotonic epoch counter for ordering | Integer |
| `epoch_id` | Unique identifier for idempotency checks | String |

---

## 4. Economics Semantics

### 4.1 Reward Distribution

Rewards are distributed proportionally to active stake at epoch finalization:

```
agent_reward = (agent_stake / stake_total) * reward_total
```

Distribution only occurs when `finalization_state = committed`.

> [!IMPORTANT]
> Reward distribution requires per-agent stake snapshot (not yet implemented). The ledger backend records epoch data but does not mutate balances until stake snapshots are available.

### 4.2 Decay

Unclaimed rewards decay over time:

```
decay_rate = 0.5 (50% per epoch)
decay_window = 2 epochs
```

- After 1 epoch: unclaimed reward = original * 0.5
- After 2 epochs: unclaimed reward = original * 0.25
- After decay_window epochs: reward expires (set to 0)

### 4.3 Consolidation

Stake changes (deposits, withdrawals) follow a queued settlement model:

- **Queuing:** Deposits/withdrawals are **queued during epoch E**
- **Finalization:** They are **finalized at `commit.epoch(E)`** (ledger write)
- **Activation:** They become **active for epoch E+1** (semantic effect)

This ensures all balance mutations occur at `commit.epoch` while stake effects apply in the subsequent epoch.

---

## 5. Rollback and Supersession Rules

### 5.1 Rollback

When `finalization_state = rolled_back`:
- All economic effects of that epoch are reversed
- Rewards are returned to the pool
- Stake changes are reverted

### 5.2 Supersession

When `finalization_state = superseded`:
- The newer `commit.epoch` with the same `epoch_index` becomes authoritative
- Previous commit.epoch events for that epoch are ignored
- Only the latest superseding event is used for settlement

---

## 6. Idempotency and Conflict Resolution

### 6.1 Idempotency

Re-emitting a `commit.epoch` with the same `epoch_id` is a **no-op**. The system must detect duplicate epoch_id values and skip processing.

### 6.2 Conflict Resolution

If two `commit.epoch` events exist for the same `epoch_index`:
1. Check `finalization_state`:
   - If one is `superseded`, use the other
   - If one is `rolled_back`, use the other (if committed)
2. If both are `committed`, use the one with the later `created_at` timestamp
3. Log a warning: conflicting epochs indicate protocol error

---

## 7. Namespace Scope

**MVP Decision:** Economics are **per-namespace**.

Each `namespace_id` has independent:
- Reward pools
- Stake totals
- Epoch sequences

Cross-namespace settlement is out of scope for v0.1.

---

## 8. Invariants

1. **Non-negative rewards:** `reward_total >= 0` always
2. **Non-negative stake:** `stake_total >= 0` always
3. **Bounded decay:** Decay rate in (0, 1), decay_window >= 1
4. **Deterministic ordering:** Epochs are processed in strict `epoch_index` order
5. **Monotonicity:** `epoch_index` must increment by exactly 1 per epoch
6. **Idempotency:** Same `epoch_id` processed at most once

---

## 9. Example Timelines

### Example A: Decay Window (Per-Epoch Settlement)

```
Epoch 10: reward_total=100 ECU, stake_total=1000 ECU, decay_window=2
Epoch 11: reward_total=80 ECU, stake_total=1000 ECU
Epoch 12: reward_total=60 ECU, stake_total=1000 ECU

Decay rule: 50% per epoch, expires after 2 epochs

Epoch 10 unclaimed rewards:
  - At Epoch 11: 100 * 0.5 = 50 ECU remaining
  - At Epoch 12: 50 * 0.5 = 25 ECU remaining
  - At Epoch 13: Expired (0 ECU)
```

### Example B: Rollback and Supersession

```
Epoch 21: commit.epoch emitted with finalization_state=committed
          reward_total=500 ECU distributed

Later: Error detected in reward calculation

Epoch 21: rollback emitted with finalization_state=rolled_back
          All distributions reversed

Epoch 21: re-commit with finalization_state=superseded on original
          New commit.epoch with corrected reward_total=450 ECU

Outcome: Only the final superseding commit.epoch is authoritative.
         Agents receive 450 ECU total (not 500).
```

---

## 10. Non-Goals

This specification does **not** cover:
- Token issuance schedule or inflation mechanics
- Governance policy for parameter changes
- Cross-chain or L1 settlement
- Slashing mechanics (covered separately)
- Fee structures or transaction costs

---

## 11. Implementation Hooks (Non-Binding)

Future implementation will likely integrate at:
- **run_devnet_epoch / run_devnet_multi_epoch:** Emit commit.epoch at epoch boundaries
- **ProtocolEventLog / event_log.py:** Record commit.epoch events in NDJSON
- **Economics engine:** Subscribe to commit.epoch events for settlement

No code changes are required in this phase. This section is informational only.
