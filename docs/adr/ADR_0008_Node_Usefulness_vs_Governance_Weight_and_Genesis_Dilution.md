# ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution

Status: Proposed
Date: 2026-02-11

## Context
Historical ILC work mixes three different concepts that must be separated to avoid future refactors:
1. node epistemic usefulness/centrality,
2. reward flow allocation,
3. governance voting power.

Past discussions also contain conflicting founder/governance proposals (no privileged veto vs transition-only suspensive veto concept).

## Decision
1. ILC SHALL separate metric surfaces:
   - `epistemic_weight` (node centrality/usefulness),
   - `utility_flow` (epoch payout surface),
   - `governance_weight` (voting influence).

2. Node usefulness SHALL be behavior-derived from reuse, validation, contradiction resistance, and path-level marginal contribution.

3. Node usefulness SHALL NOT be forced to decay only due to node age.

4. Governance weight for non-Genesis agents SHALL include time/inactivity decay.

5. Genesis governance baseline MAY be exempt from inactivity decay, but voting share SHALL always be normalized globally by total governance weight.

6. Genesis governance influence SHALL therefore dilute naturally as network participation grows; new influence must come from new verified contribution, not static historical privilege.

7. Any emergency Genesis authority, if retained, SHALL be modeled as a narrow constitutional guardrail path, not ordinary voting weight.

## Rationale
- Preserves useful historical primitives without granting permanent governance dominance.
- Aligns with constitutional intent: founder operational centrality decays over time, while canonical roots remain foundational if reused.
- Reduces lock-in risk by making voting power dynamic and auditable.

## Consequences
Positive:
- Cleaner economics/governance architecture.
- Lower risk of permanent oligarchy from early nodes.
- Better compatibility with decentralized growth.

Tradeoffs:
- Requires additional score pipelines and conformance tests.
- Requires explicit ratification of Genesis emergency-path scope.

## Implementation Artifacts
- `docs/specs/ilc_node_usefulness_and_centrality_v0.1.md`
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (open decisions still active)
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`

## Refactor-Avoidance Ordering (Binding)
Implementation should follow this order to avoid rework:
1. Freeze input events and telemetry surfaces first.
2. Implement deterministic offline score kernels (`EW`, `UF`) second.
3. Add conformance/challenge harnesses third.
4. Integrate governance-weight pipeline fourth.
5. Link economics/reward surfaces fifth.
6. Ratify remaining policy options and remove compatibility paths last.

## Open Issues
- Exact weight coefficients and calibration process.
- Final policy on transition-only suspensive Genesis brake.
- Hard bounds for Genesis governance baseline and contribution bonus.
