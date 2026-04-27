# ILC CDL-071 Temporal Tier Reconciliation — Ratification Evidence v0.1

**CDL:** 071
**Phase:** 851
**Date:** 2026-04-27
**Status:** ratified

`cdl_071_ratified_851`
`cdl_071_temporal_tier_reconciliation_ratified_851.v0.1`
`temporal_tier_framework_takes_constitutional_precedence`

---

## 1. Decision Summary

CDL-071 formally reconciles CDL-043 (adaptive pruning), CDL-044 (retention
epochs), and CDL-V1 (temporal decay) under the temporal data tier framework
introduced by CDL-069 §2g.

**Chosen option:** Normative consolidation (Option B).

**Result:** All three CDLs are formally confirmed as Tier 2 (issuance epoch
scope) implementations. No conflicts. No implementation changes required.
CDL-071 now takes constitutional precedence on tiering questions.

---

## 2. Section-7 Ratification Readiness Evidence Checklist Satisfaction

*Per CDL master log Promotion Rule (four criteria):*

### 2.1 Source citations

- CDL-069 §2g: temporal data tier framework (primary constitutional source)
- CDL-069 evidence item 14: `temporal_tier_framework_consistency_audit_complete`
- CDL-043 ratification evidence (Phase 395): adaptive pruning, Tier 2
- CDL-044 ratification evidence (Phase 399): retention_epochs=1 issuance_epoch, Tier 2
- CDL-V1 ratification evidence (Phase 330): exponential decay on issuance-epoch timescale, Tier 2
- CDL-071 opening (Phase 850): `cdl_043_tier_2_assignment_confirmed`, `cdl_044_tier_2_assignment_confirmed`, `cdl_v1_tier_2_assignment_confirmed`

### 2.2 Chosen option with rationale

Option B (normative consolidation) selected.

Rationale: CDL-069 §2g is already the authoritative Tier framework; CDL-043,
CDL-044, and CDL-V1 are correct implementations. The constitutional mandate is
to make precedence explicit — not to change the implementations. Option B
achieves this with minimal scope. Option A leaves constitutional ambiguity on
tiering unresolved. Option C is unnecessary scope.

### 2.3 Concrete implementation impact

No runtime files changed. CDL-071 is a constitutional/governance artifact.

Three normative tier-assignment records:

| CDL | Tier | Justification |
|-----|------|--------------|
| CDL-043 (adaptive pruning) | **Tier 2** | Governs graph/reputation data pruned at issuance epoch minting; CDL-069 §2g explicitly places this in Tier 2 |
| CDL-044 (retention_epochs=1) | **Tier 2** | Explicitly issuance-epoch scoped; validation-epoch interpretation prohibited |
| CDL-V1 (temporal decay) | **Tier 2** | `elapsed_issuance_epochs` parameter; reputation snapshots are Tier 2 per CDL-069 §2g |

Constitutional precedence statement: Where any ambiguity exists in CDL-043,
CDL-044, or CDL-V1 regarding data lifecycle, the CDL-069 §2g tier framework
as formally unified by CDL-071 is authoritative.

### 2.4 Verification artifact

Gate tests: `tests/test_phase_850_851_cdl_071_temporal_tier.py`

Tests covered:
- CDL-071 opening and evidence docs exist with required tokens
- CDL master log row 102 present with `ratified` status
- Tier assignment tokens present in evidence
- No `ilc_core/` files changed in Phases 850–851
- Three-CDL audit tokens all present

---

## 3. Normative Tier Assignments (Ratified)

`cdl_043_tier_2_assignment_ratified`

**CDL-043 — Adaptive Pruning:** The data governed by CDL-043 (active graph
nodes, agent ECU scores, participation records) is formally classified as
**Tier 2 (issuance epoch, ~1 month)** under the CDL-069 §2g framework. The
adaptive pruning algorithm and `ecu_score_floor ≥ 0.5` constitutional floor
are unchanged. Pruning eligibility aligns with Tier 2 lifecycle: data is
retained for at most `retention_epochs` issuance epochs, then pruned after
minting confirmation.

`cdl_044_tier_2_assignment_ratified`

**CDL-044 — Retention Epochs:** `retention_epochs = 1 issuance_epoch` is
formally classified as a **Tier 2** lifecycle parameter. The CDL-044 explicit
prohibition on validation-epoch interpretation is consistent with and subsumed
by the Tier 1 / Tier 2 boundary in the CDL-069 §2g framework. The value of
`retention_epochs = 1` is unchanged.

`cdl_v1_tier_2_assignment_ratified`

**CDL-V1 — Temporal Decay:** The exponential half-life decay for reuse
centrality reputation is formally classified as a **Tier 2** mechanism.
The `elapsed_issuance_epochs` time parameter directly maps to Tier 2
timescale. Reputation snapshots are Tier 2 data per CDL-069 §2g. The
decay formula and floor are unchanged.

---

## 4. Constitutional Precedence Record

`cdl_071_constitutional_precedence_on_tiering`

After CDL-071 ratification:

1. CDL-069 §2g is the authoritative Tier framework definition.
2. CDL-071 is the formal consolidation vehicle — it takes constitutional
   precedence over CDL-043, CDL-044, and CDL-V1 on tiering questions.
3. CDL-043, CDL-044, and CDL-V1 remain authoritative within their respective
   domains (pruning algorithm, retention constant, decay formula). CDL-071
   supersedes them only on tier classification and lifecycle precedence.
4. Future CDLs that introduce new data categories must assign those categories
   to a tier per CDL-069 §2g; CDL-071 governs any conflicts.

---

## 5. Forward Obligations

CDL-071 creates no new forward obligations. It resolves the forward obligation
established by CDL-069 §2g.

CDL-070 (PQ migration ceremony) remains deferred — separate vehicle.

`cdl_071_no_new_forward_obligations`
