# ILC Genesis Governance Dilution and Brake-Semantics Closure 597 v0.1

Status: locked
Date: 2026-04-09
Phase: 597
Owner lane: G8 Genesis carry-forward canon closure

## 1. Governance closure target

Phase 597 closes the remaining Genesis governance-dilution and brake-semantics
questions that Phase 590 left in supporting context.

This packet freezes the governance side of Genesis specialness without
reopening the Phase 590 canonical-vs-fork boundary or the bounded RC0.1 lane
frozen in Phase 595.

Required governance tokens:
- `genesis_governance_dilution_closure_exits_supporting_context`
- `genesis_bootstrap_specialness_does_not_imply_permanent_governance_floor`
- `cdl_013_global_normalization_remains_authoritative`
- `temporary_suspensive_genesis_constitutional_veto_if_retained_must_be_bootstrap_only`
- `genesis_constitutional_veto_must_use_trigger_sunset_and_hard_epoch_ceiling`
- `no_standing_genesis_governance_bonus_survives_closure`
- `genesis_governance_guardrail_must_not_become_parallel_ordinary_vote`
- `genesis_governance_fade_away_must_be_explicit_not_poetic`
- `phase_597_governance_closure_must_not_reopen_phase_590_fork_boundary`
- `phase_598_freshness_provenance_must_consume_phase_597_governance_closure`

## 2. Dependency tiers and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_window_585_594_handoff_594_v0.1.md`
- `docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Tier labels and inherited-boundary rules:
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
  remains supporting context only unless and until this phase narrows or
  supersedes the relevant claims explicitly.
- Phase 590 is frozen inherited canon for canonical-vs-fork consequence,
  Genesis-rooted public lineage, and the rule that supporting Genesis context is
  not equal canon by silence.
- Phase 595 is frozen inherited canon for the bounded RC0.1 lane and is not a
  reopening target in this packet.
- The Genesis governance carry-forward queue is not restated as planning debt in
  this phase; it is either closed here or named as an explicit later-lane
  defer.

Inherited canon consumed here:
- `window_596_605_genesis_carry_forward_primary_gate`
- `genesis_governance_dilution_must_not_remain_supporting_context_by_silence`
- `genesis_dilution_caps_and_emergency_bounds_not_silent_discretion`
- `supporting_genesis_context_not_equal_canon`

## 3. Genesis governance dilution boundary

`genesis_governance_dilution_closure_exits_supporting_context`.

`genesis_bootstrap_specialness_does_not_imply_permanent_governance_floor`.

`cdl_013_global_normalization_remains_authoritative`.

`genesis_governance_fade_away_must_be_explicit_not_poetic`.

Genesis governance influence dilutes under globally normalized governance
weight. Historical bootstrap specialness does not create a standing Genesis
public-governance floor, a founder share floor, or an untouchable privileged
vote surface.

CDL-013 remains authoritative for global normalization. This phase closes that
older baseline language must not be read as a permanent privileged governance
floor. Genesis influence, if it persists after bootstrap, must arise through
new verified contribution under globally normalized governance weight rather
than through silent historical carryover.

The ordinary-governance fade-away rule is explicit:
- no standing Genesis governance baseline survives as a public-governance
  privilege after bootstrap closure,
- no standing Genesis governance bonus survives as ordinary voting weight,
- no permanent Genesis governance floor survives,
- any retained Genesis specialness is limited to the separate bootstrap-only,
  suspensive constitutional guardrail in Section 4.

## 4. Brake-semantics and bounded specialness disposition

`temporary_suspensive_genesis_constitutional_veto_if_retained_must_be_bootstrap_only`.

`genesis_constitutional_veto_must_use_trigger_sunset_and_hard_epoch_ceiling`.

`no_standing_genesis_governance_bonus_survives_closure`.

`genesis_governance_guardrail_must_not_become_parallel_ordinary_vote`.

This phase retains a temporary suspensive Genesis constitutional veto only as a
bootstrap-only guardrail over constitutional-change proposals. It is not
ordinary voting weight, not a parallel appeal path, and not a founder override
for ordinary network direction.

Exact invocation bounds for the retained guardrail are:
- scope-limited to proposed CDL / accepted ADR / canonical-boundary changes that
  would mutate constitutional law or the Genesis-rooted lineage surface,
- never applicable to ordinary feature release, RC adoption, routine runtime
  iteration, product packaging, or harness work,
- maximum one invocation per proposal identifier,
- maximum suspension duration of one epoch per invocation,
- maximum three total lifetime invocations before permanent extinction.

Exact trigger and sunset rules are:
- the guardrail may be invoked only when a pending constitutional change would
  either sever canonical Genesis-rooted lineage without ratified reopening or
  create an immediate contradiction with already-ratified constitutional law
  before ordinary CDL-V4 review can resolve it,
- the guardrail expires at the earliest of:
  - three consecutive epochs in which ordinary non-Genesis constitutional
    governance remains available without CDL-V6 emergency invocation, or
  - epoch 60 from canonical Genesis activation,
- after that sunset point, no Genesis constitutional veto survives.

Exact audit-trail requirements are:
- every invocation must produce a signed audit record,
- the record must identify the proposal id or content hash,
- the record must cite the ratified artifact or lineage boundary allegedly put
  at risk,
- the record must include invocation epoch, expected sunset condition, and the
  mandatory follow-on CDL-V4 review pointer.

The retained guardrail is suspensive only. It may delay a constitutional change
for one epoch; it may not create new law, ratify a proposal unilaterally, or
convert into agenda control.

## 5. CDL-013 compatibility and later-governance rule

`cdl_013_global_normalization_remains_authoritative`.

CDL-013 remains authoritative for globally normalized governance weight and may
not be displaced by poetic founder language or by an informal Genesis carveout.

This packet closes the exact relationship as follows:
- CDL-013 global normalization remains the ordinary governance rule,
- any retained Genesis constitutional veto is not ordinary governance weight and
  therefore does not create a standing governance bonus,
- later governance must extend Genesis-rooted lineage without remaining captive
  to bootstrap privilege,
- CDL-V6 remains extraordinary emergency intervention only and must not be
  laundered into ordinary governance weight,
- the retained bootstrap constitutional veto remains distinct from CDL-V6 and
  distinct from ordinary release-candidate or feature-adoption processes.

`phase_597_governance_closure_must_not_reopen_phase_590_fork_boundary`.

This phase does not reopen the Phase 590 fork consequence, the Genesis-rooted
public-legitimacy chain, or the public-boundary closure already frozen in
Phases 587-590.

## 6. Residual non-closure and explicit defer discipline

This phase closes decisively:
- the governance-dilution rule,
- the rule that no standing Genesis governance bonus, baseline, or permanent
  floor survives as public-governance privilege,
- the exact disposition of any retained Genesis constitutional veto.

This phase leaves as supporting context only:
- historical ADR-0008 framing not expressly narrowed into closure language
  here,
- earlier whitepaper bootstrap-veto rhetoric that is broader than the explicit
  one-epoch / three-invocation / epoch-60-bounded guardrail ratified here.

This phase leaves as explicit later-lane defer only:
- freshness-gate provenance to Phase 598,
- accrual-governor provenance and Genesis 5 percent issuance target mechanics to
  Phases 599-600,
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics wording to Phase 602.

No governance-dilution sub-question remains silently open after this packet. If
future work wants a different Genesis governance posture, it must use an
explicit later constitutional vehicle rather than treating supporting context as
silent law.

## 7. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating Genesis bootstrap necessity as permanent governance floor,
- treating any retained Genesis constitutional veto as informal founder
  override,
- treating any retained Genesis constitutional veto as a veto over ordinary
  feature release, RC adoption, or product/runtime iteration,
- treating `CDL-V6` as ordinary governance weight,
- treating poetic fade-away language as equivalent to explicit governance
  rules,
- treating Genesis economic allocation as if it were an ordinary governance
  bonus,
- reopening the Phase 590 fork-legitimacy consequence,
- treating the one-epoch suspensive guardrail as an indefinite stall right,
- treating audit-trail omission as acceptable for Genesis constitutional
  intervention.

## 8. Explicit deferrals to later phases

Deferred beyond Phase 597:
- freshness-gate provenance closure to Phase 598,
- accrual-governor provenance reconciliation and deterministic economics
  evidence to Phases 599-600,
- capability-proof disposition to Phase 601,
- Topological Exemption boundary and public tokenomics wording to Phase 602.

`phase_598_freshness_provenance_must_consume_phase_597_governance_closure`.
