# ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution

Status: Accepted
Date: 2026-02-11
Accepted: Phase 1158, 2026-05-04
Acceptance token: `adr_0008_accepted_phase_1158`
Review posture: accepted for the architectural boundary claim after Phases
597-600 reconciliation and Phase 1158 acceptance review.

## Context
Historical ILC work mixes three different concepts that must be separated to avoid future refactors:
1. node epistemic usefulness/centrality,
2. reward flow allocation,
3. governance voting power.

Past discussions also contained conflicting founder/governance proposals
(no privileged veto vs transition-only suspensive veto concept). Those
conflicts were later narrowed by Phases 597-600:

- Phase 597 closed Genesis governance dilution and brake semantics.
- Phase 598 closed Genesis freshness-gate provenance and exemption semantics.
- Phase 599 closed Genesis accrual-governor provenance reconciliation.
- Phase 600 closed deterministic Genesis economics evidence and parameter
  posture for the fixed Genesis tranche.

## Decision
1. ILC SHALL separate metric surfaces:
   - `epistemic_weight` (node centrality/usefulness),
   - `utility_flow` (epoch payout surface),
   - `governance_weight` (voting influence).

2. Node usefulness SHALL be behavior-derived from reuse, validation, contradiction resistance, and path-level marginal contribution.

3. Node usefulness SHALL NOT be forced to decay only due to node age.

4. Governance weight for non-Genesis agents SHALL include time/inactivity decay
   under the ratified `CDL-013` global-normalization posture.

5. Historical Genesis governance-baseline language SHALL NOT be read as a
   permanent public-governance floor, standing bonus, or privileged ordinary
   vote surface. Phase 597 supersedes the older "MAY be exempt" ambiguity:
   no standing Genesis governance baseline or contribution bonus survives as
   public-governance privilege after bootstrap closure.

6. Genesis governance influence SHALL therefore dilute through globally
   normalized governance weight. New ordinary governance influence must come
   from new verified contribution under the same public-governance surface as
   other participants, not static historical privilege.

7. Any emergency or transitional Genesis authority, if retained, SHALL be
   modeled as a narrow constitutional guardrail path, not ordinary voting
   weight. Phase 597 narrows the retained guardrail to a bootstrap-only,
   suspensive constitutional brake: maximum one epoch per invocation, maximum
   one invocation per proposal, maximum three total lifetime invocations, and
   sunset under the Phase 597 trigger/epoch ceiling.

8. Genesis economic tranche/accrual semantics are distinct from governance
   privilege. Phases 599-600 close the economic surface as a fixed 5 percent
   target-plus-cap tranche against `C_max`, with `theta_hard = 0.05` and
   `theta_soft = exp(-3)`, without converting that tranche into voting power.

9. Final public ratification of exact `epistemic_weight` coefficients and
   long-horizon calibration remains outside this ADR. Current implementation
   defaults are analysis/runtime defaults, not standalone constitutional
   coefficient law unless separately ratified.

## Scope of Acceptance

This ADR is intended to accept the architectural boundary, not every numeric
score parameter. It does not ratify every numeric score parameter.

In scope:

- permanent separation of `epistemic_weight`, `utility_flow`, and
  `governance_weight`;
- behavior-derived node usefulness;
- no age-only forced decay of epistemic usefulness;
- no standing Genesis ordinary-governance floor, bonus, or privileged vote;
- Genesis emergency/suspensive authority only as bounded constitutional
  guardrail, not ordinary governance;
- Genesis economic tranche/accrual as distinct from governance weight.

Out of scope:

- final `EW` coefficient ratification;
- final freshness or utility-flow retuning beyond the Phase 598 closure;
- new Genesis-only ECU realization controller implementation;
- any public-governance acceptance of a permanent Genesis veto;
- any runtime mutation.

## Rationale
- Preserves useful historical primitives without granting permanent governance dominance.
- Aligns with constitutional intent: founder operational centrality decays over time, while canonical roots remain foundational if reused.
- Reduces lock-in risk by making voting power dynamic and auditable.
- Reconciles older ADR language with later Genesis closure phases instead of
  preserving stale ambiguity.

## Consequences
Positive:
- Cleaner economics/governance architecture.
- Lower risk of permanent oligarchy from early nodes.
- Better compatibility with decentralized growth.

Tradeoffs:
- Requires additional score pipelines and conformance tests.
- Requires final coefficient/calibration ratification outside this ADR.
- Requires any future Genesis-only ECU realization controller to remain a
  separate named policy-control layer rather than hidden centrality logic.

## Implementation Artifacts
- `docs/specs/ilc_node_usefulness_and_centrality_v0.1.md`
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (open decisions still active)
- `docs/specs/ilc_node_value_and_governance_ratification_plan_v0.1.md`
- `docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`
- `docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`
- `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`
- `ilc_core/analysis/node_value_kernel.py`
- `ilc_core/analysis/governance_weight.py`
- `ilc_core/analysis/freshness_gate.py`
- `ilc_core/analysis/genesis_accrual_governor.py`

## Refactor-Avoidance Ordering (Binding)
Implementation should follow this order to avoid rework:
1. Freeze input events and telemetry surfaces first.
2. Implement deterministic offline score kernels (`EW`, `UF`) second.
3. Add conformance/challenge harnesses third.
4. Integrate governance-weight pipeline fourth.
5. Link economics/reward surfaces fifth.
6. Ratify remaining policy options and remove compatibility paths last.

## Disposition of Former Open Issues

### Exact weight coefficients and calibration process

Status: deferred.

The current implementation defines `DEFAULT_EW_WEIGHTS` in
`ilc_core/analysis/node_value_kernel.py`:

- reuse: `0.35`
- contradiction resilience: `0.25`
- validation integrity: `0.20`
- path uplift: `0.20`

These defaults are deterministic and test-covered, but this ADR does not
ratify them as final constitutional coefficients. Final coefficient calibration
belongs to the node-value ratification / conformance lane.

### Final policy on transition-only suspensive Genesis brake

Status: closed by Phase 597.

Phase 597 retains only a bootstrap-only suspensive constitutional guardrail:
one epoch maximum delay, one invocation per proposal, three lifetime
invocations, hard sunset, signed audit record, and mandatory follow-on review.
It is not ordinary voting weight and not a standing Genesis veto.

### Hard bounds for Genesis governance baseline and contribution bonus

Status: governance side closed by Phase 597; economic side closed by
Phases 599-600.

Phase 597 closes that no standing Genesis governance baseline, contribution
bonus, or permanent governance floor survives as public-governance privilege.
Phases 599-600 close the separate economic tranche/accrual surface as a fixed
5 percent target-plus-cap tranche against `C_max`, not a governance bonus.

### Freshness / reuse-persistence boundary

Status: closed by Phase 598.

Genesis freshness exemption remains ratified for scoring, but freshness
persistence does not create governance privilege or tokenomics authority.
