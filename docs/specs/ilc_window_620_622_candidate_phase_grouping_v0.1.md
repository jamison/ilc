# ILC Window 620-622 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-13
Owner lane: G8 architectural planning
Classification: planning surface — not canonical law until sequence lock is committed

`window_620_622_candidate_grouping_v0_1`

## 1. Window identity and basis

Window 620-622 is the Agent Skills planning lane and bounded ECU exchange model
spec window. If separately activated by the human, it may run as a parallel
planning lane alongside Window 623+ without changing the Window 623+ runtime
priority.

The basis for opening this window:
- Phase 619 handoff: `agent_skills_deferred_to_post_619_window` — Agent Skills
  explicitly deferred from Window 613-619; any post-619 activation requires
  explicit human assessment of the Phase 612 priority rule
- Phase 619 handoff: `mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass` —
  spec-form pass is now complete; runtime form is the next mandatory step, but
  a bounded planning lane for Agent Skills and the ECU exchange model may run in
  parallel as a spec/design lane if the human explicitly activates it
- Human authorization (2026-04-13): Agent Skills planning lane opened as parallel
  docs/spec lane; bounded ECU exchange model authorized as Phase 622 deliverable;
  AG gates formalized as the planning design filter for this window

## 2. Pre-window required artifact

Before Phase 620 begins, the following artifact must exist and be committed:

**`docs/specs/ilc_agent_utility_logic_gates_v0.1.md`** — the eight AG logic gates
formal definition document. This artifact defines the planning design filter
that the proposed Window 620-622 sequence lock and closure handoff must assess
against.

Status: COMPLETE as of 2026-04-13 (produced in same session as this grouping).

Required token in this artifact: `agent_utility_logic_gates_v0_1_registered`

## 3. Phase map

### Phase 620 — Window 620-622 Sequence Lock (SENSITIVE)

**Type:** SENSITIVE — sequence lock
**Deliverables:**
- `docs/specs/ilc_phase_620_622_sequence_lock_v0.1.md`
- `tests/test_phase_620_window_620_622_sequence_lock.py`

**Mission:** Lock Window 620-622 as a three-phase planning lane covering Agent
Skills surface spec (Phase 621) and bounded ECU exchange model spec (Phase 622).
Record the AG-gate planning basis. Explicitly confirm that this window may run
in parallel to Window 623+ without changing Window 623+ runtime priority.

**Key locked points:**
- Window 620-622 is a spec/planning lane only — no runtime, no CDL mutation in
  Phase 620 itself, no wallet widening
- Agent Skills authorization basis: ADR-0024 (Proposed), post-619 authorization
  per Phase 619 handoff deferral rule; only Tier 1 + Tier 2 surface spec in scope
  (Tier 3 skill_node deferred per ADR-0024 explicit constraint)
- Bounded ECU exchange model is spec-form only; runtime defers to post-623+
- AG gates are the planning design basis for this window (reference `ilc_agent_utility_logic_gates_v0.1.md`)
- CDL-033 extension requirements from Phase 468 are the canonical surface contract
  for ILC graph interaction from skills; no new CDL opened in Phase 620

**Scope exclusions:**
- No CDL mutation in Phase 620
- No ilc_core/ mutation
- No wallet widening
- No Tier 3 skill_node work
- No prescriptions about Window 623+ runtime

---

### Phase 621 — Agent Skills Surface Spec

**Type:** Non-sensitive spec
**Deliverables:**
- `docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md`
- `tests/test_phase_621_agent_skills_surface_spec.py`

**Mission:** Produce the Tier 1 + Tier 2 surface spec for Agent Skills — what
each skill does, what its invocation contract is, what receipt it produces (or
does not produce), and what CDL-033 extension requirements it surfaces for the
ILC graph interaction verbs.

**Key content:**
- Tier 1 skills (7 workflow skills from ADR-0024): invocation contract, expected
  inputs and outputs, machine-legible result format, failure modes
- Tier 2 skills (5 scaffold skills from ADR-0024): template surface, invocation
  pattern, how they wire to Tier 1 outputs
- CDL-033 extension requirements: which ILC graph interaction verbs are required
  for skills to produce receipts that the graph can process
  (authored-envelope submission, refutation submission, novelty-check status
  query, reuse-centrality query — from Phase 468 scoping)
- AG gate assessment table (AG-1 through AG-8 for this phase's work)
- Explicit statement that Tier 3 (skill_node) is deferred and that no CDL-034
  extension or benchmark protocol is opened in this window

**Scope exclusions:**
- No CDL mutation
- No ilc_core/ mutation
- No Tier 3 work
- No skill implementation (spec only)
- No external skill import from agentskills.io or community catalogs

---

### Phase 622 — Bounded Agent-Commissioning-Agent ECU Exchange Model Spec

**Type:** Non-sensitive spec
**Deliverables:**
- `docs/specs/ilc_bounded_ecu_exchange_model_622_v0.1.md`
- `tests/test_phase_622_bounded_ecu_exchange_model.py`

**Mission:** Produce the spec-form bounded model for how an agent can commission
another agent using ECU, bounded by the current Option-D posture and the Phase
609 ECU/ILC separation. This is AG-8 advancement in spec form.

**Key content:**
- The bounded agent-commissioning-agent loop: Agent A commissions Agent B for a
  contribution through an ECU-denominated sponsorship or earmark; Agent B
  produces an ILC graph submission; upon admission and validation-epoch
  settlement, ECU accrual is credited to Agent B; this window does not open a
  direct ECU debit, transfer, or wallet-write path for Agent A
- Separation from ILC payment: ECU exchange is not an ILC payment. The current
  internal ledger is not a payment rail. The model must be consistent with Phase
  609 ECU/ILC separation (AG-4)
- Bounded posture: the model is bounded by Option D; no sovereign substrate
  execution, no wallet write, no public payment claim
- AG gate assessment table (particular focus on AG-4, AG-8)
- Explicit runtime deferral: this is spec form; runtime form defers to post-623+
  and must not be claimed in this phase
- CDL-053 relationship: the Werner credit architecture is planning carry-forward
  (deferred pending LT evidence track); Phase 622 must not claim CDL-053 as
  decided or as a prerequisite for this spec

**Scope exclusions:**
- No CDL mutation (CDL-053 remains deferred)
- No ilc_core/ mutation
- No wallet write, transfer, or withdrawal authority
- No public payment claim
- No sovereign substrate execution

## 4. Window-level constraints

All three phases share these constraints:

1. No decision-log mutation in any Window 620-622 phase
2. No ilc_core/ mutation in any Window 620-622 phase
3. No CDL-062 opening
4. No Option B selection claim
5. Option D active posture remains unchanged
6. Window 623+ MVP touchpoints runtime is not prescribed by this window — this
   window does not authorize, sequence, or block Window 623+
7. CDL-053 Werner credit architecture remains deferred to its own evidence track
8. Tier 3 skill_node remains deferred per ADR-0024 explicit constraint

## 5. AG-gate window preview

This preview is non-binding. The binding assessment appears in the Phase 620
sequence lock.

| Gate | Preview | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Skills reduce session friction for both human and agent participants |
| AG-2 W_e increase | advance | Tier 1 skills directly reduce re-discovery cost per session |
| AG-3 Epistemic integrity | neutral | No graph mutation; CDL-033 extension requirements preserve Popperian form |
| AG-4 ECU-ILC separation | pass (must verify) | Phase 622 must stay within Phase 609 separation; ECU exchange ≠ ILC payment |
| AG-5 Harness-agnostic | advance | Root `skills/` canonical source path; harness-specific discovery configuration may still be required |
| AG-6 Near-infinite scale | neutral/advance | Skills reduce per-agent cost; CDL-033 interaction verbs are already scale-aware |
| AG-7 Machine-legible first | advance | Skill invocation contracts are machine-legible; receipts are JSON |
| AG-8 Outbound economic loop | advance | Phase 622 is the first spec-form expression of agent-commissioning-agent loop |

## 6. Next window

Window 623+ is the MVP touchpoints interface/runtime closure window. It is not
dependent on Window 620-622 completion. Window 620-622 and Window 623+ may run
concurrently or in sequence — that is a human authorization decision.

After Window 623+: the coupling invariants governance lock (Phase 611 graduation
checklist row 6) is the next canonical blocker for Option B selection. That work
is deferred until post-623+.

## 7. MemPalace refresh disposition

Disposition: required before Phase 620 begins
Basis: Phase 619 handoff recorded `Disposition: required`; this grouping
document adds the pre-window AG gates artifact to the active working set
Rebuild command: `bash tools/mempalace/build_active_working_set.sh`
