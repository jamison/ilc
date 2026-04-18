# ILC Adjacent Gated-Economy Carry-Forward Selection 728 v0.1

**Phase:** 728  
**Window:** 727-732  
**Date:** 2026-04-18  
**Author:** Codex

`adjacent_gated_economy_carry_forward_selected`

## 1. Baseline

Window `727-732` is active under the Phase `727` sequence lock. The inherited
position from Window `723-726` is that financial-shard activation remains
deferred and not yet eligible. The current window must therefore select the
honest non-financial continuation rather than pretending post-launch
prerequisites are already satisfied.

Track B remains parallel and must be re-read from `STATUS.md` at execution
time, but it is not the active lane being selected here.

## 2. Candidate carry-forward set

The live candidate set after `723-726` is:

1. reopen financial-shard trigger work,
2. merge the window into `CDL-062` sovereign-substrate work,
3. advance adjacent gated-economy hardening around rights, licensing, and
   private/gated contract surfaces,
4. use the window for bounded `CDL-017` text review only,
5. defer the whole window.

The first option is not honest because `723-726` already bounded the trigger
question and preserved the deferment posture. The second option is not honest
because `CDL-062` remains a separate sovereign-substrate lane. The fourth
option is too narrow to justify the whole window by itself. The fifth option is
unnecessary because a real adjacent hardening lane exists.

## 3. Selected lane and justification

The selected lane for `729-730` is adjacent gated-economy hardening.

`rights_licenses_and_private_gated_hardening_selected_for_729_730`
`financial_shard_lane_remains_deferred_in_727_732`

This is the honest choice because:

- capsule `v4.9` explicitly carries adjacent gated-economy hardening forward,
- the rights/licensing and private/gated contract candidate docs already exist
  and need bounded disposition rather than hand-wavy future treatment,
- the lane can be completed as docs/spec hardening without fake post-launch
  claims,
- it reduces implementation drift risk without opening a new constitutional
  lane prematurely.

## 4. Boundary and separation obligations

The selected lane still has to preserve four boundaries:

1. financial-shard activation remains deferred and not yet eligible,
2. `CDL-062` remains separate from private/gated hardening,
3. ADR-0022 remains the architectural anchor rather than a target for hidden
   ratification,
4. rights/licensing is not collapsed into scientific or epistemic refutation.

`cdl_062_lane_remains_separate_from_private_gated_hardening`

This means `729-730` may clarify:

- what belongs at the public anchor layer,
- what belongs in bounded gated/private shard contract surfaces,
- what remains L2/L3 business logic,
- what remains constitutionally or operationally deferred.

It may not:

- authorize financial-shard activation,
- treat `CDL-062` as merged,
- claim that a new rights contract is already ratified.

## 5. Deferred alternatives

The explicitly deferred alternatives are:

- any later financial-shard opening decision,
- any new CDL opening tied to this lane,
- `CDL-017` ratification,
- `CDL-062` convergence or ratification,
- runtime implementation of access-control, capability-token, or subscription
  machinery.

`no_new_cdl_opening_recommended_in_phase_728`

There is no new CDL opening tied to this lane in Phase `728`.

## 6. Non-goals

This phase does not include:

- decision-log mutation,
- CDL ratification,
- financial-shard activation,
- runtime implementation,
- any mutation of `ilc_core/` or `ilc_consensus/`.

The task here is lane selection and boundary lock, not constitutional closure.

## 7. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_phase_727_732_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.9.md`
- `docs/specs/ilc_window_727_732_codex_guidance_and_audit_brief_v0.1.md`
- `docs/specs/ilc_window_727_732_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/phases/STATUS.md`
