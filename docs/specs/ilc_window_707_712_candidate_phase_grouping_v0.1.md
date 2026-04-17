# ILC Window 707-712: Candidate Phase Grouping (Codex Lead)

**Author:** Codex
**Date:** 2026-04-17
**Baseline:** Window `701-706` is closed. Capsule v4.5 is published. `CDL-066`,
`CDL-017`, and `CDL-067` remain open. `M-011` is complete and `M-012` is the
next planned M-series phase.
**References:**
- `docs/specs/ilc_window_707_712_guidance_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.7 and §5.2
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` §9
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`

---

## 1. Window identity and scope

Window `707-712` is the governance-minimization and validator-agent identity
lane. It is the first post-`706` window and the active Track A continuation.

This window is responsible for:

1. writing the sequence lock for `707-712`,
2. publishing the governance-minimization inventory and sunset taxonomy,
3. disposing of the ADR-0019 governance-compilation boundary in live planning
   form,
4. ratifying `CDL-066` as the narrow sender-authorization constitutional lane,
5. publishing the graph-native algorithm-governance contract and a bounded
   local-influence worked example,
6. ratifying `CDL-067` as the settlement-state governance vehicle,
7. recording the validator-agent design evidence and the six prelock answers
   required before any honest `CDL-017` prelock work,
8. commissioning `SIM-VALIDATOR-01` and `SIM-TOPOLOGY-01`,
9. publishing the `CDL-039` topology-shuffling authorization scope note,
10. closing the window with a coherence report, capsule v4.6, and closure gate.

This window does NOT:
- ratify `CDL-017`,
- open `CDL-062`,
- select final Option B production configuration,
- claim row `5` or row `7` runtime closure,
- ratify validation pools as a separate constitutional lane,
- mutate `ilc_core/` or `ilc_consensus/` in the docs-only phases.

---

## 2. Inter-lane dependencies

### 2.1 Inherited baseline

This window inherits:
- Window `701-706` closure and capsule v4.5,
- row `5 = spec_closed_runtime_pending`,
- row `7 = spec_closed_runtime_pending`,
- row `8 = closed / reconfirmed`,
- `CDL-066`, `CDL-017`, and `CDL-067` as open at window start,
- Track B current state from `STATUS.md`, not from memory.

### 2.2 Relationship to Track B

Track B is now beyond the old `M-009` / `M-010` gate language. The live rule
for this packet is:
- verify Track B status from `docs/phases/STATUS.md` tail before each phase,
- do not hard-code the M-series frontier from an older capsule line,
- treat `CDL-017` ratification as convergence-window work, not `707-712` work.

### 2.3 Downstream dependency created here

This window is the main Track A preparation lane for the later Mysticeti
convergence window. After `707-712`, the repo should have:
- `CDL-066` ratified,
- `CDL-067` ratified,
- `CDL-017` still open but with design evidence and prelock answers recorded,
- simulation commissioning paths named and bounded,
- a cleaner frontier for `713-716` and the eventual convergence window.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `707` sequence lock
- Phase `708` governance-minimization inventory and `CDL-066` ratification
- Phase `709` algorithm-governance contract and `CDL-067` ratification
- Phase `710` validator-agent design evidence and Q1-Q6 answer record
- Phase `711` simulation commissioning and `CDL-039` scope note
- Phase `712` coherence, capsule v4.6, and closure gate

### 3.2 Explicitly deferred

- `CDL-017` ratification
- `CDL-017` activation
- final topology-seed production choice if evidence is still incomplete
- final validation-pool economics CDL
- row `5` runtime leakage confirmation
- row `7` runtime censorship/exitability confirmation
- Option B production selection
- legal-positioning memo work beyond tracking it as a later pre-RC blocker

---

## 4. Governing constraints inherited from prior windows

Hard constraints:
- `CDL-017` remains prelock-only in this window,
- `CDL-066` ratification must stay narrow and sender-authorization-specific,
- `CDL-067` ratification must stay narrow and settlement-governance-specific,
- Q1-Q6 answers must exist before any honest execution of the validator-agent
  sub-lane phase,
- the validator-agent premise is fixed:
  - validators are agents,
  - validator stake is ECU-backed,
  - validator reputation extends the agent reputation chain,
  - topology shuffling is a governed later authorization question,
- any phase that states current Track B status must verify the `STATUS.md` tail
  first,
- sequence-lock and governance-doc phases may not mutate `ilc_core/` or
  `ilc_consensus/`.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 707 | Window `707-712` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 708 | Governance minimization inventory, ADR-0019 disposition, and `CDL-066` ratification | Governance / Ratification | **SENSITIVE** |
| 3 | 709 | Graph-native algorithm-governance contract, local-influence example, and `CDL-067` ratification | Governance / Ratification | **SENSITIVE** |
| 4 | 710 | Validator-agent design evidence and Q1-Q6 record for `CDL-017` prelock | Research / Prelock | **SENSITIVE** |
| 5 | 711 | `SIM-VALIDATOR-01`, `SIM-TOPOLOGY-01`, and `CDL-039` scope note | Simulation / Scope | **SENSITIVE** |
| 6 | 712 | Coherence report, capsule v4.6, and window `707-712` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 707 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_707_712_sequence_lock_v0.1.md`

Required content:
- lock the six-phase ordering for `707-712`,
- state that `CDL-066` and `CDL-067` are in-window ratification targets,
- state that `CDL-017` is not ratified here,
- state that Q1-Q6 answers are a hard precondition before the validator-agent
  sub-lane phase executes,
- state that Track B status must be checked against `STATUS.md` tail.

### Phase 708 — governance minimization + `CDL-066`

Deliverables:
- `docs/specs/ilc_governance_minimization_inventory_and_sunset_taxonomy_708_v0.1.md`
- `docs/specs/ilc_adr_0019_governance_compilation_boundary_disposition_708_v0.1.md`
- `docs/specs/ilc_cdl_066_agent_sender_authorization_ratification_evidence_708_v0.1.md`

Required content:
- inventory human/manual levers and assign sunset taxonomy,
- preserve explicit boundary between explanatory governance philosophy and
  executable governance law,
- ratify `CDL-066` narrowly around sender authorization,
- update the decision log row for `CDL-066` from `open` to `ratified`.

### Phase 709 — algorithm governance + `CDL-067`

Deliverables:
- `docs/specs/ilc_graph_native_algorithm_governance_contract_and_local_influence_example_709_v0.1.md`
- `docs/specs/ilc_cdl_067_settlement_substrate_governance_ratification_evidence_709_v0.1.md`

Required content:
- define the algorithm-governance namespace and selection contract,
- include a bounded local-influence worked example,
- ratify `CDL-067` narrowly as the settlement-state governance vehicle,
- update the decision log row for `CDL-067` from `open` to `ratified`.

### Phase 710 — validator-agent design evidence

Deliverables:
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`

Required content:
- record explicit answers to Q1-Q6,
- name the accepted option and rejected alternatives for each answer,
- map the answers into `CDL-017` prelock requirements,
- state explicitly that `CDL-017` ratification does not occur in this window.

### Phase 711 — simulation commissioning + `CDL-039`

Deliverables:
- `docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md`
- `docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`

Required content:
- commission `SIM-VALIDATOR-01` with stake-floor calibration requirements,
- commission `SIM-TOPOLOGY-01` with connectivity/privacy requirements,
- publish the narrow constitutional authorization path for topology shuffling,
- avoid silently turning the scope note into final production VRF law if the
  evidence is not there yet.

### Phase 712 — closure

Deliverables:
- `docs/specs/ilc_coherence_report_712_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.6.md`
- `docs/specs/ilc_window_707_712_closure_gate_712_v0.1.md`

Required content:
- summarize Phases `707-711`,
- update the capsule to v4.6,
- record `CDL-066` and `CDL-067` as ratified if Phases `708-709` completed,
- record `CDL-017` as still open/unratified,
- route carry-forward into `713-716` and the later convergence window.

---

## 7. Phase-specific open questions, options, and recommendations

### 7.1 Phase 708

Open question:
- should governance minimization stay as research framing only, or move to a
  sharper spec artifact?

Options:
- research memo only,
- spec-level taxonomy with explicit non-goals.

Recommendation:
- use a spec-level taxonomy. Later windows need an explicit inventory of what
  governance levers exist and how they sunset.

Open question:
- should `CDL-066` broaden into generalized transfer authorization?

Options:
- narrow sender-authorization ratification only,
- broad transfer-auth redesign.

Recommendation:
- ratify the narrow sender-authorization lane only. Do not entangle it with
  validator admission or generalized wallet redesign.

### 7.2 Phase 709

Open question:
- should the local-influence example be a separate document?

Options:
- separate worked example doc,
- inline worked example inside the algorithm-governance contract.

Recommendation:
- keep it inline. The example should prove the contract is concrete without
  spawning a second interpretive artifact.

Open question:
- should `CDL-067` freeze backend schema details?

Options:
- narrow settlement-governance ratification,
- broad backend schema freeze.

Recommendation:
- ratify the narrow governance vehicle only. Schema freeze belongs later and
  should not be silently smuggled into this phase.

### 7.3 Phase 710

Q1. `ValidatorKey` linkage
- options:
  - same BLS key as `AgentID`
  - derived sub-key with provable linkage
- recommendation:
  - derived sub-key, for cleaner key separation and auditability

Q2. Minimum stake threshold
- options:
  - fixed floor chosen by conversation
  - simulation-derived floor from `SIM-VALIDATOR-01`
- recommendation:
  - simulation-derived floor; do not hard-code a final number before evidence

Q3. Reputation-weighted selection
- options:
  - proportional weighting
  - threshold-gated eligibility pool
- recommendation:
  - threshold-gated eligibility for the first prelock pass because it is easier
    to reason about and align with diversity constraints

Q4. Validation pools
- options:
  - include in `CDL-017`
  - separate later CDL
- recommendation:
  - separate later CDL

Q5. Topology assignment seed
- options:
  - epoch-hash
  - VRF
- recommendation:
  - epoch-hash is acceptable for testnet framing; production VRF may remain a
    later stronger-lock question

Q6. `CDL-V3` diversity floor extension
- options:
  - no extension
  - yes, with an explicit validator-set metric
- recommendation:
  - yes, but only if the metric is made explicit in the evidence packet

### 7.4 Phase 711

Open question:
- must `SIM-TOPOLOGY-01` finish in-window?

Options:
- full results in-window,
- commission in-window and allow results to complete later.

Recommendation:
- commission in-window; allow completion later if needed. The commission itself
  is the required closure item for `707-712`.

Open question:
- should the `CDL-039` scope note resolve VRF versus epoch-hash finally?

Options:
- final production choice,
- explicit option framing and authorization path only.

Recommendation:
- publish the authorization path and option framing only if the simulation and
  constitutional evidence are not yet sufficient for a final production choice.

---

## 8. Potential blockers and sequencing risks

- The validator-agent sub-lane is honestly blocked until Q1-Q6 answers exist in
  conversation form.
- `CDL-066` and `CDL-067` ratification texts can drift into over-broad scope if
  not kept narrow.
- Track B may advance beyond `M-012` while this packet is waiting for GO; every
  execution phase must re-check `STATUS.md` tail.
- Decision-log mutation is allowed only in the ratification phases.
- The legal-positioning memo remains a real pre-RC blocker but is not a blocker
  for this window’s internal closure.

---

## 9. Hard non-goals for the full window

- Do not ratify `CDL-017`.
- Do not open `CDL-062`.
- Do not claim final Option B production selection.
- Do not claim row `5` or row `7` runtime closure.
- Do not ratify validation pools.
- Do not use doctrine language to silently create new executable law.
