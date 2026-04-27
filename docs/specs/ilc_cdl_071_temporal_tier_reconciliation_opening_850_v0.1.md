# ILC CDL-071 Temporal Tier Reconciliation — Opening v0.1

Status: opening artifact
Date: 2026-04-27
Decision vehicle: CDL-071
Phase: 850

`cdl_071_temporal_tier_reconciliation_opening_850`
`cdl_071_opened_phase_850`
`cdl_069_ratified_blocker_cleared_for_cdl_071`

---

## 1. Decision Identity

**CDL-071** — Temporal tier framework reconciliation.

**Related:** CDL-069 §2g (temporal data tier framework — the constitutional source);
CDL-043 (adaptive pruning); CDL-044 (retention_epochs); CDL-V1 (temporal decay);
Phase 838 evidence item 14 (`temporal_tier_framework_consistency_audit_complete`).

**Trigger:** CDL-069 §2g introduced the temporal data tier framework as a
first-class constitutional principle and established CDL-071 as the formal
amendment vehicle for CDL-043, CDL-044, and CDL-V1. CDL-071 could not open
until CDL-069 was ratified (Phase 838j, 2026-04-26). The block is now cleared.

---

## 2. Decision Topic

Formally reconcile CDL-043, CDL-044, and CDL-V1 under the temporal data tier
framework (CDL-069 §2g):

1. **Tier assignment** — Affirm each CDL's data categories as Tier 2 (issuance
   epoch, ~1 month).
2. **Constitutional precedence** — Establish that CDL-071 takes constitutional
   precedence on tiering questions after ratification.
3. **Compliance confirmation** — Record that no amendments to the underlying
   implementations are required (the three CDLs are consistent implementations
   of the tier principle — CDL-069 evidence item 14 confirms no conflicts).

---

## 3. Temporal Data Tier Framework Summary (CDL-069 §2g)

| Tier | Timescale | Example data | Hash | Pruning |
|------|-----------|-------------|------|---------|
| 1 — Ephemeral | Validation epoch (~1 min) | ECU deltas, BLS sigs, gossip | SHA-256 | Immediate at epoch close |
| 2 — Medium-term | Issuance epoch (~1 month) | Reputation snapshots, endorsement packets, ECU records | SHA-256 | Per CDL-043/044 retention policy |
| 3 — Permanent | Indefinite | genesis records, agent_id, ILC balances, root pk | SHA-384 | Never |

CDL-071 governs Tier 2: the data governed by CDL-043, CDL-044, and CDL-V1 all
falls squarely within the issuance epoch timescale.

---

## 4. Three-CDL Tier Audit

### 4.1 CDL-043 — Adaptive Pruning (Phase 395)

**Governs:** Storage economics, graph pruning policy, active-graph retention
constraints. Chosen option: adaptive pruning with bounded retention windows.
`ecu_score_floor ≥ 0.5`, `retention_epochs` bounded.

**Data category:** Active graph nodes (agent reputations, ECU scores,
participation records) — accumulated within an issuance epoch; pruned after
minting confirmation. CDL-069 §2g explicitly states: "Pruning: CDL-043/044
retention policy; pruned after issuance epoch minting confirmation."

**Tier assignment: Tier 2.** ✅ Consistent.

**Conflicts with CDL-069 §2g:** None. CDL-043 adaptive pruning operates
exactly on the Tier 2 boundary — data lives for at most
`retention_epochs` issuance epochs before pruning is eligible.

`cdl_043_tier_2_assignment_confirmed`

---

### 4.2 CDL-044 — Retention Epochs (Phase 399)

**Governs:** `retention_epochs = 1` issuance epoch. Explicitly prohibits
validation-epoch interpretation (`retention_epochs is issuance-epoch scoped
and must not be interpreted on validation-epoch timescale`).

**Data category:** The same graph/reputation data as CDL-043. Retention
bound = 1 issuance epoch. CDL-044's explicit prohibition on validation-epoch
interpretation is precisely consistent with Tier 2 (issuance epoch) vs.
Tier 1 (validation epoch) semantics.

**Tier assignment: Tier 2.** ✅ Consistent.

**Conflicts with CDL-069 §2g:** None. CDL-044's issuance-epoch scope is
the defining characteristic of Tier 2. The explicit validation-epoch exclusion
is redundant with (but consistent with) the tier framework.

`cdl_044_tier_2_assignment_confirmed`

---

### 4.3 CDL-V1 — Temporal Decay (Phase 330 / runtime Phase 388)

**Governs:** Exponential half-life decay for reuse centrality reputation.
Chosen option: exponential half-life decay. Runtime: `temporal_decay_runtime.py`
(`CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"`).

**Data category:** Reputation scores (reuse centrality). The runtime uses
`elapsed_issuance_epochs` as its time parameter — decay is measured in issuance
epochs, not validation epochs. The underlying data (reputation snapshots) is
accumulated over issuance epochs and decays across issuance epochs.

**Tier assignment: Tier 2.** ✅ Consistent.

**Conflicts with CDL-069 §2g:** None. CDL-069 §2g lists "reputation snapshots"
explicitly as Tier 2 data. CDL-V1's issuance-epoch decay schedule aligns with
Tier 2 lifecycle — data persists for a bounded number of issuance epochs before
decaying to or below the floor threshold.

`cdl_v1_tier_2_assignment_confirmed`

---

## 5. Audit Finding

`temporal_tier_framework_consistency_audit_complete_cdl_071`

No conflicts found across CDL-043, CDL-044, and CDL-V1. All three CDLs:
- Operate on the issuance epoch timescale (**Tier 2**)
- Are consistent partial implementations of the Tier 2 data lifecycle
- Require no implementation changes

CDL-071 ratification is **normative consolidation** only: it makes constitutional
precedence explicit and formally names the tier assignment for each CDL.

---

## 6. Decision Options

| Option | Description |
|--------|-------------|
| A | No amendment — leave tier assignment implicit in each CDL | Rejected: constitutional precedence must be explicit per CDL-069 §2g mandate |
| B | Normative consolidation — formal tier assignment + precedence statement, no implementation changes | **Selected** |
| C | Restructuring — rewrite CDL-043/044/V1 to explicitly reference tiers throughout | Rejected: unnecessary scope; implementations are correct and CDL-069 §2g is the authoritative source |

**Selected:** Option B.

---

## 7. Chosen Outcome

CDL-071 ratification will record:

1. CDL-043 data categories are formally assigned to **Tier 2**
2. CDL-044 `retention_epochs = 1 issuance_epoch` is formally assigned to **Tier 2**
3. CDL-V1 temporal decay operates on **Tier 2** reputation data with issuance-epoch time parameter
4. CDL-071 takes **constitutional precedence** on tiering questions; where any ambiguity exists in CDL-043, CDL-044, or CDL-V1, CDL-069 §2g as unified by CDL-071 is authoritative
5. The three CDL implementations are compliant — no amendments to runtime files are required

---

## 8. Scope

CDL-071 does NOT:
- Change the pruning algorithm in CDL-043 (adaptive pruning stays)
- Change the `retention_epochs = 1` value in CDL-044
- Change the decay formula in CDL-V1 (exponential half-life stays)
- Mutate any runtime file in `ilc_core/`
- Affect CDL-070 (PQ migration — separate vehicle, remains deferred)
- Open any new CDL obligations

---

## 9. Verification Artifact

Gate tests: `tests/test_phase_850_851_cdl_071_temporal_tier.py`

Checks:
- CDL-071 opening doc exists with audit tokens
- CDL-071 ratification evidence exists with tier assignment tokens
- CDL master log has CDL-071 row with `status: ratified`
- No ilc_core/ mutation in this window

`cdl_071_verification_artifact_defined`
