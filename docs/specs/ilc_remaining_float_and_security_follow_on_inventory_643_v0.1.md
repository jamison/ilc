# ILC Remaining Float and Security Follow-On Inventory 643 v0.1

Status: inventory artifact
Date: 2026-04-14
Classification: carry-forward inventory
Phase: 643
Owner lane: G8 security boundary and remaining-float strike force

## 1. Purpose and boundary

This document publishes the remaining-float inventory required after Window
637-641 and records the adjacent security follow-on items that remain outside
the bounded Window 642-648 implementation lane.

`remaining_float_inventory_post_641_published`

This inventory does not reopen the exact-numeric windows. It exists so the repo
retains a durable record of what was closed, what remains live, and what is
deferred by risk tier.

## 2. Closed exact-numeric work to date

Closed by prior windows:
- Window 631-636: Tier-0 runtime-critical economic, ledger, and staking surfaces
- Window 637-641: bounded residual `R2/R3` contract leakage in shared contracts,
  protocol mapping, runtime-adjacent helpers, and companion export validators

Closed categories include:
- active economic ledger math
- settlement verification and snapshot validators
- residual `net_stake` shared-contract leakage
- residual protocol-mapper float-default leakage
- residual canon-export companion numeric leakage

`remaining_float_inventory_runtime_critical_surface_closed_to_date`

## 3. Remaining float surface inventory

### 3.1 Runtime-adjacent / public-contract surfaces still open

Highest remaining float-bearing surfaces after Window 641:
- `ilc_core/server.py` request/response DTOs still declare float stake/reward fields
- `ilc_core/config.py` still declares `JsonScalar: str | int | float | bool | None`
- `ilc_core/cli/ep_task_cli.py` still declares float in `JsonScalar`
- `ilc_core/protocol/params.py` still uses float-backed protocol parameter parsing
- `ilc_core/consensus/engine.py` still exposes mixed `float | Decimal` boundary state
- `ilc_core/rc/economic_cycle_runtime.py` still contains float-oriented compatibility logic and metadata time helpers

`remaining_float_inventory_runtime_adjacent_surface_still_open`

### 3.2 Consensus / protocol policy math still open

Still-open policy/helper float surfaces include:
- `ilc_core/consensus/governance.py`
- `ilc_core/consensus/popperian_gate_runtime.py`
- `ilc_core/consensus/diversity_floor_runtime.py`
- `ilc_core/consensus/epoch_state_runtime.py`
- `ilc_core/reputation/temporal_decay_runtime.py`
- `ilc_core/identity/sybil_resistance_runtime.py`
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`

These are not all direct ledger balances, but they remain runtime-adjacent and
should be reviewed before any future claim that the repo is broadly float-clean.

### 3.3 Sim / analysis / devnet surfaces still deferred

Deferred lower-tier float-bearing surfaces include:
- `ilc_core/sim/*`
- `ilc_core/analysis/*`
- `ilc_core/node/devnet.py`
- `ilc_core/mining/benchmark.py`
- `ilc_core/economics/rl_agents.py`

These remain important but lower priority because they are not the bounded
runtime-critical leak paths already closed in 631-641.

`remaining_float_inventory_sim_and_analysis_surface_deferred`

## 4. Security follow-on inventory outside this window

Window 642-648 is intentionally bounded. Security follow-on items that remain
outside this lane include:
- `ilc_core/mcp/service.py` still imports `random` for audit-path behavior
- devnet/research paths still use `random`
- broader wall-clock metadata and operator-timestamp usage remains across the
  repo, though not all of it is protocol-state triggering
- any future integer/minor-unit migration must define canonical string
  serialization for large amounts over JSON

`security_follow_on_inventory_beyond_642_648_registered`

## 5. Prioritized carry-forward routing

Priority order after Window 642-648:
1. shared/public contract float cleanup in `server.py`, `config.py`, and CLI JSON scalar surfaces
2. runtime-adjacent consensus/protocol helper cleanup in `protocol/params.py`,
   `consensus/*`, `reputation/*`, and `identity/*`
3. RC/runtime metadata-time audit in `rc/economic_cycle_runtime.py` and nearby
   operational surfaces
4. lower-tier sim / analysis / devnet float cleanup

This order keeps the repo focused on runtime/public boundary risk first rather
than chasing lower-tier simulation churn.

## 6. TODO registration summary

The TODO block registered alongside this document separates remaining float
carry-forward from the completed 631-641 work and from the bounded 642-648
security window.

It records:
- shared/public contract cleanup
- runtime-adjacent protocol/consensus cleanup
- lower-tier sim/analysis cleanup
- non-finite / canonical numeric boundary review on any future new surface

`remaining_float_follow_on_todo_registered`
