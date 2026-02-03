# Epoch Control-Plane Notes v0.1

**Version:** 0.1  
**Status:** Draft  
**Date:** 2026-02-03

---

## Summary

This note captures the core framing for epoch control and settlement:

- **Goal:** Reward *verified epistemic work per unit time*, bounded by energy constraints.
- **Control-plane:** Fast, epoch-start calibration (benchmarks, trust updates, routing tiers).
- **Ledger-plane:** Deterministic settlement at `commit.epoch` (balances, decay, consolidation).

---

## Key Points

1) **Energy is a constraint, not the reward driver.**  
   Energy (watts) should cap or throttle throughput. Reward should track *verified* work quality.

2) **Epoch-start tests are control-plane calibration, not settlement.**  
   Benchmarks and trust updates set eligibility and routing tiers for the epoch.  
   They do not mutate balances or finalize rewards.

3) **Settlement happens only at `commit.epoch`.**  
   Ledger mutations (rewards, decay, consolidation) are finalized at epoch boundaries.  
   This avoids probabilistic drift and keeps settlement auditable.

4) **Fast epochs should not inflate rewards by themselves.**  
   ECU/ILC minting should be *time-normalized* and quality-gated, not epoch-counted.

5) **Auditing and trust vectors make “verified work” real.**  
   Cross-agent audit, reputation decay, and trust tiers prevent fast garbage from earning.

---

## Design Implications

- **Per-namespace epoch lengths are acceptable** if minting is time-normalized.  
- **Receipts/attestations during epochs** provide fast interaction without ledger drift.  
- **Stake snapshots + commit.epoch** provide deterministic settlement and audit trails.

---

## Related Specs

- `docs/specs/commit_epoch_economics_v0.1.md`
- `docs/specs/epoch_init_control_loop_v0.1.md`

