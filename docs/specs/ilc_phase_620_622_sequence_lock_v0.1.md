# ILC Phase 620-622 Sequence Lock v0.1

Status: locked
Date: 2026-04-13
Phase: 620
Owner lane: G8 architectural planning

## 1. Window identity and authorization basis

Window 620-622 is the Agent Skills planning lane and bounded ECU exchange model
spec lane. It is a three-phase planning/spec window only and may run in
parallel to Window 623+ without changing Window 623+ runtime priority.

The authorization basis is explicit and bounded:
- Phase 619 handoff carries `agent_skills_deferred_to_post_619_window`; that
  deferral means post-619 activation requires explicit human assessment rather
  than automatic carry-forward from the handoff alone.
- Human authorization 2026-04-13 opened the Agent Skills planning lane, opened
  the bounded ECU exchange model as the Phase 622 deliverable, and formalized
  the AG gates as the planning design filter for this window.
- Human assessment 2026-04-13 treats the Phase 612 priority rule as satisfied
  for opening this bounded parallel planning lane because the five MVP
  touchpoints are now closed in spec form; runtime form in Window 623+ is still required before broader public RC claims.

Required lock tokens:
- `window_620_622_sequence_lock_primary_gate`
- `agent_skills_planning_lane_authorized_post_619`
- `ag_gates_registered_as_planning_filter_for_window_620_622`
- `window_620_622_parallel_to_window_623_plus`
- `option_d_posture_active_in_window_620_622`

## 2. Phase map and hard pass conditions

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 620 | Window 620-622 sequence lock | `ilc_phase_620_622_sequence_lock_v0.1.md` | YES |
| 621 | Agent Skills surface spec | `ilc_agent_skills_surface_spec_621_v0.1.md` | No |
| 622 | Bounded ECU exchange model spec | `ilc_bounded_ecu_exchange_model_622_v0.1.md` | No |

The hard pass condition for Window 620-622 is:
1. Phase 621 Agent Skills surface spec file exists and passes its tests.
2. Phase 622 bounded ECU exchange model spec file exists and passes its tests.
3. All phase tests within the window pass with no CDL mutation, no `ilc_core/`
   mutation, and no wallet widening.
4. Each phase AG-gate assessment table records at least one advance gate and
   zero FAIL gates.

`window_620_622_sequence_lock_primary_gate`.
`window_620_622_parallel_to_window_623_plus`.
`ecu_exchange_model_spec_form_only_runtime_deferred`.

## 3. AG-gate design basis

The AG-gate artifact is a planning design filter for this window. It is not
treated here as repo-wide ratified law. No window-level AG-gate assessment is a
FAIL.

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Agent Skills and bounded agent-commissioning specs reduce friction for both humans and agents without subordinating either side. |
| AG-2 W_e increase | advance | Tier 1 and Tier 2 skills reduce rediscovery cost per session, while the bounded ECU loop clarifies a future productivity multiplier without runtime widening. |
| AG-3 Epistemic integrity | neutral | Window 620-622 is spec-only; it does not suppress refutation, mutate settled graph state, or bypass Popperian challenge pathways. |
| AG-4 ECU-ILC separation | neutral | Phase 622 must stay within Phase 609 separation boundaries; ECU exchange != ILC payment and does not authorize ECU debit, transfer, or wallet write semantics. |
| AG-5 Harness-agnostic | advance | The canonical shared source path is root `skills/`, while harness-specific discovery configuration remains allowed where needed. |
| AG-6 Near-infinite scale | neutral | The window defines machine-legible planning surfaces that degrade gracefully and do not introduce a new governance chokepoint. |
| AG-7 Machine-legible first | advance | Skill invocation contracts and bounded exchange surfaces are defined as CLI/file/JSON-first, with human-auditable documentation alongside them. |
| AG-8 Outbound economic loop | advance | Phase 622 is the first bounded spec-form statement of an agent-commissioning-agent ECU-denominated loop inside the current Option-D posture; debit-side enforcement remains deferred. |

`ag_gates_registered_as_planning_filter_for_window_620_622`.

## 4. Inherited boundary state

The following inherited boundaries remain unchanged in Window 620-622:
- the Phase 576 and Phase 581 read-only wallet boundary remains frozen;
  `wallet_boundary_576_581_unchanged_in_window_620_622`
- the Phase 609 ECU / ILC / runtime layer separation remains the controlling
  canon for any bounded exchange discussion
- the Phase 612 two-form MVP gate requirement remains active: spec form and
  runtime form are both required before broader public RC claims may proceed
- ADR-0028 keeps `Option D` as the active posture; this window does not select
  `Option B` or reopen sovereign-substrate authorization;
  `option_d_posture_active_in_window_620_622`

## 5. Per-phase scope constraints

| Phase | In scope | Out of scope | AG-gate advance claim |
|---|---|---|---|
| 620 | Window sequence lock, phase ordering, AG-gate design basis, inherited boundary confirmation, window-level exclusions | Any runtime work, any wallet widening, any CDL mutation, any `ilc_core/` mutation, any Option-B selection claim | AG-3 and AG-4 are preserved as non-negotiable constraints; AG-7 advances through a machine-legible lock surface. |
| 621 | Tier 1 and Tier 2 Agent Skills surface spec, invocation contracts, machine-legible result forms, CDL-033 extension requirements for graph interaction | Any skill runtime implementation, any Tier 3 skill_node work, any external skill import from agentskills.io or community catalogs, any ADR or CDL mutation; `tier_3_skill_node_deferred_per_adr_0024` | AG-1, AG-2, AG-5, and AG-7 advance if the skill surface remains harness-agnostic and CLI/file/JSON-first. |
| 622 | Bounded ECU-denominated sponsorship or earmark model, agent-commissioning-agent loop in spec form, explicit Phase 609 separation notes, runtime deferral | Any direct ECU debit, transfer, spend, or wallet write operation; any ILC payment claim; any sovereign substrate execution; any claim that CDL-053 is already decided; `ecu_exchange_model_spec_form_only_runtime_deferred` | AG-8 advances only if AG-4 remains satisfied and the model stays inside the bounded current posture. |

## 6. Window-level exclusions

The following exclusions are mandatory for every Window 620-622 phase:
- No decision-log mutation in any Window 620-622 phase.
- No `ilc_core/` mutation in any Window 620-622 phase.
- No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_620_622`.
- No `Option B` selection claim.
- No prescription about Window 623+ runtime sequencing or timing.
- No Tier 3 skill_node work; `tier_3_skill_node_deferred_per_adr_0024`.
- No external skill import from agentskills.io or community catalogs.
- The read-only wallet posture from Phase 576 and Phase 581 remains unchanged;
  `wallet_boundary_576_581_unchanged_in_window_620_622`.
- CDL-053 Werner credit architecture remains deferred to its own evidence track;
  Phase 622 bounded ECU exchange model does not require CDL-053 to be decided;
  `cdl_053_deferred_pending_lt_evidence_not_prerequisite_for_622`.

Window 620-622 is a bounded planning lane only. It may run in parallel to
Window 623+, but it does not authorize, sequence, block, or substitute for the
runtime/interface closure required there.
