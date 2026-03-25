# ILC External Verification and Developer-Consumption Surfaces Placeholder v0.1

Status: planning placeholder only. Not a CDL. Does not authorize runtime or constitutional
scope expansion.
Date: 2026-03-25
Author: GPT-5 Codex

Purpose: preserve a distinct future lane for the protocol surfaces required to let external
agents, external teams, and external applications consume ILC as a verification, provenance,
and publication substrate rather than only as an internal graph.

---

## 1. Why this placeholder exists

Recent Jones/NemoClaw analysis and follow-on intake work elevated a strong architectural
guardrail:

> ILC should be built so external agents and external systems can use it as a verification,
> provenance, and publication substrate rather than only as an internal graph.

That guardrail is strong enough to carry now.

What is not yet complete is the protocol surface required to make that claim operationally
strong rather than partially aspirational.

This placeholder exists to keep that surface area explicit and separate from:

- minimum-scope `CDL-053`,
- private/gated shard rights/access hardening,
- and long-tail / post-issuance economics research.

---

## 2. Minimum future work this lane should preserve

This lane should preserve the following work items:

1. **Stable public identity and authorship surfaces**
   - public `agent_id` continuity
   - authored-payload continuity
   - disclosed lineage
   - promotion receipts for private-to-public transitions

2. **Public quality-verification surfaces**
   - ratified quality modes
   - refutation path
   - anomaly-triggered review path
   - explicit public status semantics for externally consumed artifacts

3. **Dependency and serviceability verification**
   - required-vs-reference linkage semantics
   - host serviceability claims
   - challenge path for unresolved closure

4. **Private/public continuity and gated-access compatibility**
   - public anchors for private work
   - shard/header continuity
   - promotion lineage
   - compatibility with gated/private access models

5. **External developer-consumption surfaces**
   - machine-readable query surfaces
   - public developer documentation
   - integration guidance for external agents and applications
   - benchmarked readiness / ingestion flows

---

## 3. What this lane is not

This placeholder does not itself authorize:

- new Treasury or ECU policy,
- pressure-flow ratification,
- developer tooling as `L1` protocol law,
- or expansion of current Window 460-468 scope.

This is a carry-forward lane for interface completeness and external usability.

---

## 4. Dependencies and anchors

Primary anchors:

- `docs/research/ilc_jones_nemoclaw_dredge_intake_memo_v0.1.md`
- `docs/research/ilc_jones_nemoclaw_analysis_and_architectural_implications_v0.1.md`

Architectural dependencies:

- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md`
- `docs/specs/ilc_graph_linkage_and_dependency_contract_candidate_v0.1.md`
- `docs/research/ilc_host_admission_and_dependency_serviceability_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`

Planning dependencies:

- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md`
- `docs/specs/ilc_private_gated_shard_rights_and_access_hardening_placeholder_v0.1.md`

---

## 5. Planning rule

Future planning artifacts should carry this lane explicitly if they claim that ILC is becoming
an external verification layer for outside agent ecosystems.

That claim should not be made as a full present-tense capability unless the surfaces in Section
2 are materially present.

---

## 6. Suggested future outputs

When this lane is picked up, likely outputs include:

- a public query / verification surface note,
- external developer integration guidance,
- readiness / benchmark contracts for outside agent systems,
- and, if warranted, a more formal contract for externally consumable verification responses.

---

## 7. Immediate carry-forward implication

The next capsule-facing planning refresh should treat this placeholder as a distinct follow-on
lane, not as an implicit side effect of either:

- minimum-scope `CDL-053`, or
- private/gated shard rights/access hardening.
