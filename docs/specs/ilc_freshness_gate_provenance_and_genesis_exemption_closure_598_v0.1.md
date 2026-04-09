# ILC Freshness-Gate Provenance and Genesis Exemption Closure 598 v0.1

Status: locked
Date: 2026-04-09
Phase: 598
Owner lane: G8 Genesis carry-forward canon closure

## 1. Freshness closure target

Phase 598 dispositions the Genesis freshness exemption and the decay-vs-reuse
provenance gap that remained supporting context after Phase 590.

This packet closes the freshness lane without reopening the governance closure
from Phase 597 or the frozen public/RC boundaries inherited from Phases 590 and
595.

Required governance tokens:
- `freshness_gate_provenance_closure_exits_supporting_context`
- `genesis_exempt_posture_must_be_ratified_supplemented_or_reopened_explicitly`
- `genesis_reuse_persistence_not_same_as_permanent_governance_privilege`
- `decay_vs_reuse_boundary_must_be_explicit`
- `cfr_002_context_gap_must_be_dispositioned`
- `freshness_closure_must_not_reopen_phase_597_governance_rules`
- `topological_exemption_remains_rationale_unless_explicitly_elevated`
- `phase_599_accrual_reconciliation_must_consume_phase_598_freshness_closure`

## 2. Dependency tiers and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_genesis_governance_dilution_and_brake_semantics_closure_597_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
- `whitepaper/02_design_principles.md`

Tier labels and inherited-boundary rules:
- `docs/specs/ilc_freshness_gate_contract_v0.1.md` was supporting context only
  before this phase and is dispositioned here.
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md` remains
  supporting explanatory context only and is not a self-executing
  freshness-law source.
- whitepaper and epistemological rationale remain explanatory context only and
  are not self-executing law.
- Phase 597 governance closure is frozen inherited canon for this window and
  must not be reopened by freshness disposition.

Inherited canon consumed here:
- `freshness_gate_provenance_must_be_dispositioned`
- `freshness_and_accrual_supporting_context_not_closed_public_law`
- `phase_598_freshness_provenance_must_consume_phase_597_governance_closure`
- `temporary_suspensive_genesis_constitutional_veto_if_retained_must_be_bootstrap_only`

## 3. Current freshness posture and provenance gap

`freshness_gate_provenance_closure_exits_supporting_context`.

`decay_vs_reuse_boundary_must_be_explicit`.

`cfr_002_context_gap_must_be_dispositioned`.

The current freshness posture is the deterministic exponential-decay contract
already implemented in active analysis code and documented in the draft
freshness contract:
- `decay_lambda = 0.25`
- `freshness_floor = 0.85`
- `genesis_exempt = true`
- `freshness_gate(age_epochs, is_genesis) = 1.0 if (genesis_exempt and is_genesis) else max(floor, exp(-lambda * age_epochs))`

The provenance gap was not that the posture was unknown. The gap was that
CFR-002 was resolved implicitly by implementation rather than explicitly by a
canon-quality closure artifact. This phase closes that gap by ratifying the
explicit exponential-decay choice and by stating that reuse-led persistence is
not a substitute for deterministic freshness decay in the scoring surface.

The constitutional interaction that must remain explicit is:
- freshness decay applies to stale non-Genesis rows,
- Genesis exemption leaves Genesis freshness at `1.0`,
- `freshness_floor` remains bounded above the refutation-profitability safety
  threshold,
- freshness language does not by itself settle governance, accrual, or
  tokenomics questions.

## 4. Disposition of the Genesis exemption posture

`genesis_exempt_posture_must_be_ratified_supplemented_or_reopened_explicitly`.

This phase chooses evidence-supplemented closure.

The Genesis exemption posture is ratified here without changing the existing
constants or function shape. The evidence supplement is:
- the deterministic contract in `docs/specs/ilc_freshness_gate_contract_v0.1.md`,
- the active implementation surface in `ilc_core/analysis/freshness_gate.py`,
- the active focused tests in `tests/test_freshness_gate_phase_217.py`,
- the Phase 212 refutation-profitability invariant preserved through the safety
  floor bound,
- the explicit boundary that this phase does not alter the Genesis accrual
  governor constants or the `CDL-029` allocation split surface.

What is proven by this closure:
- exponential decay is the chosen freshness function shape,
- Genesis exemption remains the ratified posture for freshness scoring,
- the default constants are deterministic and fail closed under invalid policy
  or invalid inputs,
- the floor is constitutionally constrained so freshness penalties do not invert
  refutation profitability.

What is not proven by this closure and therefore remains tolerated but not
expanded:
- no separate large-horizon simulation lane specifically calibrated
  `decay_lambda = 0.25` or `freshness_floor = 0.85` before this phase,
- no claim that freshness by itself settles Genesis accrual trajectory behavior,
- no claim that reuse persistence overrides explicit decay in the scoring
  contract.

## 5. Genesis centrality, reuse, and persistence boundary

`genesis_reuse_persistence_not_same_as_permanent_governance_privilege`.

`topological_exemption_remains_rationale_unless_explicitly_elevated`.

Genesis reuse persistence, foundational centrality, and canonical bootstrap
status do not create permanent governance privilege. Freshness closure ratifies
how stale scoring evidence is treated; it does not reintroduce a governance
bonus or a standing governance floor.

The boundary is explicit:
- reused foundational content may remain epistemically important,
- freshness exemption for Genesis scoring does not create public-governance
  privilege,
- freshness/reuse language does not silently settle Genesis economic-allocation
  or tokenomics questions,
- Topological Exemption remains rationale only and may not be used as a
  substitute for this explicit freshness disposition.

`freshness_closure_must_not_reopen_phase_597_governance_rules`.

## 6. Residual non-closure and explicit defer discipline

This phase closes decisively:
- the CFR-002 decay-vs-reuse context gap,
- the explicit ratification of the Genesis freshness exemption posture,
- the fact that the freshness contract no longer remains draft-only by silence.

This phase leaves as supporting context only:
- epistemological and whitepaper rationale that is broader than the explicit
  scoring-law closure here,
- any narrative that tries to generalize freshness persistence into governance
  or tokenomics authority.

This phase leaves as explicit later-lane defer only:
- accrual-governor provenance reconciliation and deterministic Genesis economics
  evidence to Phases 599-600,
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics wording to Phase 602.

If later evidence shows the current freshness constants are incompatible with
ratified Genesis accrual-governor surfaces, that change must happen through the
later dedicated accrual lane rather than by silently weakening this closure.

## 7. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating freshness persistence as permanent governance privilege,
- treating the former draft freshness contract as already-ratified law by
  silence before Phase 598,
- using Topological Exemption rhetoric as a substitute for explicit freshness
  disposition,
- reopening governance-dilution rules already closed in Phase 597,
- treating Genesis freshness exemption as if it directly settles Genesis 5
  percent issuance-target mechanics,
- treating reuse-persistence rhetoric as a replacement for deterministic decay
  in the scoring contract.

## 8. Explicit deferrals to later phases

Deferred beyond Phase 598:
- accrual-governor provenance reconciliation to Phases 599-600,
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics wording to Phase 602.

`phase_599_accrual_reconciliation_must_consume_phase_598_freshness_closure`.
