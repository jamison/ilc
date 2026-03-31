# ILC Signal-Floor Policy Consistency Scoping 547 v0.1

Status: scoped
Date: 2026-03-31
Phase: 547
Owner lane: G8 Constitution Cluster A

## 1. Scoping purpose

This phase inventories the current signal-floor mechanisms across ILC runtime modules,
documents the active cross-module invariant, and decides whether floor-governance requires
a new constitutional track or can be handled through existing ADR / ADM documentation.

## 2. Current signal-floor inventory

- `U_FLOOR = 0.05` in `ilc_core/epistemic/reuse_centrality_runtime.py` sets the minimum
  reusable direct-use centrality signal for the Phase 537 runtime.
- `recommended_decay_floor = 0.05` in Phase 542 passive ECU calibration sets the minimum
  centrality score eligible for passive attribution.
- CDL-V1 uses `floor_multiplier` in `ilc_core/reputation/temporal_decay_runtime.py` as the
  temporal decay floor that bounds issuance-epoch decay from below.
- CDL-V2 uses `expected_diversity_floor` in `ilc_core/identity/sybil_resistance_runtime.py`
  as the diversity-floor threshold for sybil-resistance contribution scoring.

## 3. Cross-module constraint analysis

The active cross-module invariant is `recommended_decay_floor >= recommended_u_floor`.
At v1 the two values are equal: `recommended_decay_floor = 0.05` and
`recommended_u_floor = 0.05`.

No additional hard cross-module floor dependency is currently required. CDL-V1
`floor_multiplier` is a bounded decay floor for reputation aging, not a reuse-attribution gate.
CDL-V2 `expected_diversity_floor` is a sybil-resistance threshold tied to diversity heuristics,
not a centrality-computation cutoff. Those two floors are semantically distinct and do not need
to be numerically coupled to the reuse / passive-ECU lane.

The practical governance need is therefore documentation consistency, not a new constitutional
constraint. The reuse-centrality / passive-ECU relationship should be recorded centrally so
future floor changes do not drift independently, but the other floor types can remain
domain-scoped.

## 4. Governance disposition

`signal_floor_policy_scoped`
`signal_floor_governance_adm_only`

An ADM / ADR update is sufficient. The only cross-module invariant that needs to be locked is
the reuse-to-passive relationship `recommended_decay_floor >= recommended_u_floor`, and that can
be documented in `ADR-0023` or companion governance notes without opening a new CDL row.

## 5. Window 555+ forward obligations

Window 555 should update `ADR-0023` with the cross-module invariant
`recommended_decay_floor >= recommended_u_floor` and record that equality at `0.05 >= 0.05`
is the minimum valid v1 configuration. Any future proposal to lower `recommended_decay_floor`
below `recommended_u_floor` should be treated as governance-breaking and must be escalated
before implementation.
