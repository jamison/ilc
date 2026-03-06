# ILC Epoch Timescale Disambiguation and Simulation Improvement Guidance 369 v0.1

Status: Non-ratifying analytical artifact (local-reviewer session notes)
Date: 2026-03-06
Phase context: Phase 369 post-execution / Phase 370 pre-execution input
Owner lane: G8 Constitution Cluster A

---

## 1. Purpose

This document records two outputs from the post-Phase-369 local reviewer session:

1. **Epoch timescale disambiguation** — the ILC protocol uses two distinct epoch concepts
   that have never been formally co-documented. This gap affects simulation
   interpretability for SIM-003, SIM-004, and SIM-005.

2. **Simulation improvement guidance for Codex** — concrete changes to apply in
   Phase 370 (SIM-005) and retroactively in Phase 371 (SIM-003/SIM-004 revision if
   needed), to resolve the identified interpretability gaps.

This artifact is non-ratifying and non-runtime. No decision-log mutation is implied.

---

## 2. The two-epoch architecture

The ILC protocol has two distinct epoch timescales. These have never been co-documented
in a single specification artifact.

### 2.1 Issuance epoch — 1 month (canonical, ratified)

| Parameter | Value | Source | Status |
| --- | --- | --- | --- |
| Epoch duration | `1 month` | CDL-027 Phase 276 ratification | Canonical / locked |
| Halving period H | `48 epochs = 4 years` | CDL-027 | Canonical / locked |
| C_max | `25,920,000 ILC` | CDL-026 | Canonical / locked |
| G_max (Genesis cap) | `1,296,000 ILC` (5% of C_max) | CDL-029 | Canonical / locked |
| ECU clamp | `P_min=0.75, P_max=1.30` | CDL-030 | Canonical / locked |
| Decay factor q | `2^(-1/48) ≈ 0.985663` | derived from CDL-027 | Derived |
| Epoch-0 budget | `~371,973 ILC/month` | derived from CDL-027 + CDL-026 | Derived |
| Genesis 5% reach (p50) | `~23 epochs ≈ 1.89 years` | genesis dynamics analysis 298 v0.3 | Derived |
| 95% issuance reach | `~207 epochs ≈ 17 years` | genesis dynamics analysis 298 v0.3 | Derived |
| Full horizon | `480 epochs = 40 years` | genesis dynamics analysis 298 v0.3 | Derived |

Canonical anchors:
- `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`
- `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`

### 2.2 Validation epoch — 1 minute (implemented, undocumented)

| Parameter | Value | Source | Status |
| --- | --- | --- | --- |
| Epoch duration | `1 minute` | `ilc_core/consensus/reputation.py` (implicit) | Implemented, no spec |
| Grace period | `1,440 epochs = 24 hours` | `reputation.py` comment | Implicit |
| Atrophy half-life | `262,800 epochs ≈ 6 months` | `ATROPHY_HALF_LIFE_EPOCHS = 262800` | Implemented |

Derivation: `1,440 epochs = 24 hours → 1 epoch = 1 minute`.
Cross-check: `262,800 minutes = 4,380 hours = 182.5 days ≈ 6 months`. Consistent.

**Documentation gap**: The 1-minute validation epoch is never formally named or specified
in any project document. It is encoded only as an implicit constant. This gap should be
addressed in capsule v1.2 (Phase 376) or an earlier disambiguation spec.

### 2.3 Epoch uses by protocol layer

| Protocol layer | Epoch type used | Duration |
| --- | --- | --- |
| ECU issuance / Genesis accumulation | Issuance epoch | 1 month |
| Epoch snapshots (CDL-023) | Issuance epoch | 1 month |
| Epoch state reconciliation (CDL-039) | Issuance epoch | 1 month |
| Reputation scoring / atrophy | Validation epoch | 1 minute |
| Gossip / peer discovery timing | Unspecified (sub-minute likely) | TBD |
| CDL-V1 temporal decay half-life | Validation epoch (likely) | TBD — needs spec |

---

## 3. SIM-004 reinterpretation under canonical epoch

### 3.1 Which epoch does SIM-004 model?

SIM-004 models "partition-tolerant epoch consensus" — the problem of reconciling epoch
state when a network partition has caused two sub-networks to form divergent issuance
epoch histories. The relevant epoch is the **issuance epoch (1 month)**, not the
validation epoch (1 minute), because:

- CDL-023 (epoch snapshot mechanism, ratified Phase 321) captures state at each issuance
  epoch boundary.
- "Partition-tolerant epoch consensus" means: the network must agree on a single issuance
  epoch state after reconnection.
- The reconciliation rules (highest_ecu_wins) operate on ECU accumulation, which is an
  issuance epoch concept.

### 3.2 What T=34 actually means

Under the 1-month issuance epoch:

| SIM-004 result | Epochs | Wall-clock |
| --- | --- | --- |
| Minimum-divergence threshold | 34 | 34 months ≈ 2.8 years |
| Threshold exceeded | 50 | 50 months ≈ 4.2 years |
| Conflict at T=34 | 0.151 | below 0.18 threshold |
| Conflict at T=50 | 0.222 | above 0.18 threshold |

A 2.8-year safe partition window is architecturally coherent: ILC's CIDv1
content-addressing design means no data is lost during a partition (only temporal
ordering diverges), enabling extremely long partition tolerance that would be impossible
for systems without content-addressed state.

The actual threshold crossover is somewhere between T=34 and T=50 months. The simulation
does not pin this precisely (see improvement guidance §4.2).

### 3.3 CDL-039 two-timescale implication

CDL-039 (P2P transport) must handle partitions at both timescales with distinct
mechanisms:

| Timescale | Partition event | Required mechanism |
| --- | --- | --- |
| Minutes–hours (validation epoch) | Gossip disruption, peer loss | Levin stress-cascade reconnection |
| Months–years (issuance epoch) | Full epoch state divergence | Partition-tolerant consensus + `highest_ecu_wins` reconciliation |

Neither mechanism is sufficient alone. Phase 372's CDL-039 prelock must name and
distinguish both.

---

## 4. What SIM-004 tells us that we did not know before

Four substantive additions to project knowledge:

**1. Partition reconciliation has a tractable issuance-epoch window (~34 months).**
Before SIM-004, CDL-039 design had no quantitative target for partition duration.
The ~34-month safe window is now a concrete engineering target. Partitions longer
than ~34 months may require operator intervention or manual epoch reconciliation.

**2. `highest_ecu_wins` is quantitatively preferred as the reconciliation rule.**
It produces the lowest average conflict rate across the full parameter sweep (factor 0.78
vs. 1.0 for newest-claim-wins and 1.16 for fork-survival). Cost is slightly higher
(factor 1.12 vs. 0.95) but the tradeoff favors correctness over speed — appropriate
for an epistemic protocol. This gives CDL-039 a simulation-backed baseline rule.

**3. Cross-partition reference rate is the dominant conflict driver.**
More important than partition duration or claim rate, how many claims cross the partition
boundary during the partition determines whether reconciliation is tractable. Even at
T=1 month, high cross-partition referencing generates meaningful conflict. This implies
a CDL-039 design requirement not previously explicit: **the protocol must provide a
partition-detection signal that enables agents to rate-limit or defer cross-partition
references during active partition events.**

**4. Refutation saturates as a conflict reducer.**
Refutation damping caps at 0.62 in the model. Aggressive refutation can only reduce
conflict by ~38%. The reconciliation mechanism must operate independently of refutation
availability. This blocks a "just refute everything on reconnection" strategy.

---

## 5. Simulation improvement guidance for Codex

These changes apply to SIM-005 (Phase 370) immediately, and retroactively to SIM-004
in Phase 371's interpretation artifact if a revised run is needed.

### 5.1 Declare epoch type explicitly in every simulation (REQUIRED — blocking for interpretability)

Every simulation that uses "epoch" as a unit must declare which epoch it models.
Add to the simulation module header and `run_manifest.json`:

```python
EPOCH_TYPE = "issuance_epoch"         # or "validation_epoch"
EPOCH_DURATION_CANONICAL = "1 month"  # or "1 minute"
EPOCH_DURATION_SOURCE = "CDL-027 ratified Phase 276"  # or "reputation.py"
```

Include in `run_manifest.json` output:

```json
"epoch_context": {
    "epoch_type": "issuance_epoch",
    "epoch_duration_canonical": "1 month",
    "epoch_duration_source": "CDL-027 ratified Phase 276",
    "wall_clock_note": "T=34 epochs = 34 months ≈ 2.8 years"
}
```

SIM-005 must declare its epoch type before Phase 370 commits. SIM-003 and SIM-004
should be updated in Phase 371 if a revised run is commissioned.

**Note on SIM-003**: The pruning recommendations (`retention_epochs=1,
snapshot_interval=50`) must be interpreted against the declared epoch type.
Under issuance epochs: retention=1 month, snapshots every 50 months (~4 years).
Under validation epochs: retention=1 minute, snapshots every 50 minutes. Neither is
obviously correct without declaration. Phase 371 must disambiguate.

### 5.2 Narrow the partition-duration crossover (MODERATE — recommended for SIM-004 revision)

The current sweep [1, 2, 5, 8, 13, 21, 34, 50] leaves a 16-epoch gap between the last
below-threshold point (T=34) and the first above-threshold point (T=50). Add intermediate
values: T=40, T=44, T=47. The actual crossover is likely around T=38–42 months
(~3–3.5 years). A more precise crossover gives CDL-039 a tighter engineering target.

This is most useful as a Phase 371 revision, not a blocker for Phase 370.

### 5.3 Add `cross_partition_reference_control` as a protocol design parameter (MODERATE)

The simulation currently treats cross-partition reference rate as an exogenous input.
But the protocol can control it. Add a parameter to the sweep:

```python
CROSS_PARTITION_REFERENCE_CONTROLS = [
    "none",           # baseline: no protocol intervention
    "detection_signal",  # protocol detects partition, alerts agents
    "rate_limit_0.1", # cross-partition references capped at 10% of claims
    "defer_all",      # all cross-partition references deferred until reconnection
]
```

Run the conflict rate sweep for each control policy. This directly produces CDL-039
design requirements (which policy to mandate) rather than just describing inputs.
The output should include a row in the requirements summary stating which control policy
is recommended.

### 5.4 Add `reconnection_strategy` as a simulation parameter (LOW for SIM-004, HIGH for SIM-005)

Add a reconnection strategy dimension to show how Levin-style bridge restoration changes
the effective conflict rate near the threshold:

```python
RECONNECTION_STRATEGIES = [
    "standard",      # baseline: passive reconnection
    "levin_cascade", # Levin stress-cascade: active cross-cluster bridge restoration
    "lazy_merge",    # worst case: no active reconnection
]
```

Model `levin_cascade` as reducing effective partition duration by a cascade_efficiency
factor (e.g., `effective_T = T * (1 - cascade_efficiency)` where `cascade_efficiency`
is a swept parameter in [0.1, 0.3, 0.5]). This shows concretely how much the Levin
mechanism helps and provides a CDL-039 design constraint: minimum required cascade
efficiency to keep conflict below threshold at T=50.

For SIM-005 (agent death and graph orphaning), reconnection strategy is more directly
relevant because orphaned agents must be detected and replaced by the gossip layer.

### 5.5 Replace arbitrary calibration constants with protocol-derived expressions (LOW — future revision)

The SIM-004 conflict formula uses calibration constants (0.45, 0.55, 0.56, 0.78, 0.62,
etc.) with no derivation from protocol behavior. A v0.2 of the simulation could derive
conflict rate from protocol-native quantities:

```
conflict_rate ≈ (cross_partition_references) / (total_claims_both_partitions)
             = claims_per_epoch * partition_duration * cross_partition_reference_rate
               / (2 * claims_per_epoch * partition_duration)
             = cross_partition_reference_rate / 2
```

This would make the model self-consistent with existing protocol parameters (using
SIM-001 claim rates as inputs) and remove the arbitrary calibration dependency.
This is not urgent for Phase 370 but should be the target for any v0.2 simulation
series.

---

## 6. Carry-forward for Phase 370 (SIM-005)

Phase 370 (SIM-005 — agent death and graph orphaning) must:

1. Declare epoch type explicitly per §5.1 above.
2. Consider whether SIM-005 operates at the validation epoch (1 minute — agent
   disappears quickly, gossip detects absence within minutes) or the issuance epoch
   (1 month — agent must miss a full issuance epoch before being treated as dead).
   Both timescales are relevant and may need separate simulation lanes.
3. Include reconnection strategy as a parameter per §5.4.
4. Produce explicit CDL-039 design requirements in the requirements summary, as
   SIM-004 did. Agent death behavior directly informs the gossip protocol's orphan
   detection and peer replacement mechanisms.
5. Carry forward the Levin mechanism as a candidate design input for orphan recovery,
   consistent with SIM-004's Phase 372 carry-forward.

---

## 7. Carry-forward for Phase 371 (SIM-004/005 interpretation)

Phase 371 must:

1. Interpret SIM-004 results under the 1-month issuance epoch assumption, citing this
   artifact as the canonical epoch-disambiguation source.
2. Interpret SIM-003 pruning recommendations under a declared epoch type (recommend
   issuance epoch for `snapshot_interval`; validate retention policy separately).
3. Produce an integrated requirements summary for CDL-039 prelock hardening in Phase 372,
   including: partition duration target (T ≤ 34 issuance epochs = ~2.8 years), preferred
   reconciliation rule (`highest_ecu_wins`), cross-partition reference control requirement,
   and Levin mechanism as a candidate gossip-layer reconnection mechanism.
4. If SIM-004 or SIM-005 lacked epoch type declarations, commission revised runs with
   the declared epoch type before Phase 372 begins.

---

## 8. Non-goals

This artifact does not:

- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- ratify epoch duration for any protocol layer other than issuance (CDL-027 is already
  ratified; the validation epoch is not yet subject to a CDL),
- authorize any `ilc_core/` runtime changes,
- constitute a simulation result or replace SIM-004/SIM-005 outputs.
