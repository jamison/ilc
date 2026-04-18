# ILC Window 717-722: Candidate Phase Grouping (Codex Lead)

**Author:** Codex
**Date:** 2026-04-18
**Baseline:** Window `713-716` is closed. Capsule v4.7 is published. `CDL-066`
and `CDL-067` are ratified. `CDL-017` remains open and unratified. Track B
shows `M-014` complete and the authoritative next M-phase as `TBD` in
`STATUS.md`.
**References:**
- `docs/specs/ilc_window_717_722_guidance_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.4 and §5.4
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` §11
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/adr/ADR_0015_Node_Transfer_Economics.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`

---

## 1. Window identity and scope

Window `717-722` is the ADR-0015 closure lane: node transfer economics, commons
dedication, and leasehold / reversion calibration.

This window is responsible for:

1. writing the sequence lock for `717-722`,
2. publishing the ADR-0015 family inventory and scoping note,
3. publishing the transfer-tax and cooling-period governance package,
4. publishing the commons-dedication and leasehold / reversion notes,
5. publishing the ADR-0015 disposition plus the simulation / replay
   commissioning contract,
6. explicitly stating whether any new CDL opening is recommended or deferred,
7. closing the window with a coherence report, capsule v4.8, and closure gate.

This window does NOT:
- ratify a new CDL unless honest evidence forces that conclusion,
- ratify `CDL-017`,
- claim row `5` or row `7` runtime closure,
- mutate `ilc_core/` or `ilc_consensus/`,
- silently turn economic doctrine into constitutional law without evidence.

---

## 2. Inter-lane dependencies

### 2.1 Inherited baseline

This window inherits:
- Window `713-716` closure and capsule v4.7,
- `CDL-066` ratified,
- `CDL-067` ratified,
- `CDL-017` open and unratified,
- row `5 = spec_closed_runtime_pending`,
- row `7 = spec_closed_runtime_pending`,
- Track B current state from `STATUS.md`, not from memory.

### 2.2 Relationship to Track B

Track B is not the central work of this packet, but closure and capsule language
still depends on the live M-series frontier. The rule is:
- verify `STATUS.md` tail before every phase,
- do not copy stale M-series wording out of older guidance or capsules,
- do not let local loopback success be restated as true multi-machine proof.

### 2.3 Relationship to inherited economic law

This window does not start from an empty field.

The packet must preserve:
- creator attribution permanence and income-right transfer separation from
  ADR-0015 and the CDL-034 line,
- governance decoupling from economic concentration,
- the treasury-routing boundary already governed by `CDL-047`,
- the ECU-time discipline already governed by `CDL-048`,
- the fact that leasehold / reversion is still explicitly simulation-dependent.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `717` sequence lock
- Phase `718` ADR-0015 family inventory and scoping
- Phase `719` transfer-tax and cooling-period governance package
- Phase `720` commons-dedication mechanics and leasehold / reversion note
- Phase `721` ADR-0015 disposition, simulation / replay commissioning, and CDL
  opening recommendation or deferment memo
- Phase `722` coherence report, capsule v4.8, and closure gate

### 3.2 Explicitly deferred

- CDL ratification by default
- `CDL-017` ratification
- row `5` or row `7` runtime closure
- final multi-machine validator proof
- numeric calibration results for transfer tax, cooling duration, or leasehold
  duration
- silent activation of leasehold if evidence is still incomplete
- silent treasury-route expansion beyond the existing `CDL-047` boundary

---

## 4. Governing constraints inherited from prior windows

Hard constraints:
- no pre-window conversation gate applies here,
- each ADR-0015 mechanism must receive an explicit written disposition,
- `CDL-047`, `CDL-048`, `CDL-051`, `CDL-059`, `CDL-060`, `CDL-061`,
  `CDL-066`, and `CDL-067` are inherited baselines and are not reopened,
- transfer moves income rights and never creator attribution,
- no runtime mutation occurs in the docs-only phases,
- any claim about current Track B state must be verified from `STATUS.md`,
- if a new CDL opening is recommended, the packet must say so explicitly rather
  than smuggling constitutionalization into ordinary spec prose.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 717 | Window `717-722` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 718 | ADR-0015 family inventory and scoping | Research / Planning | **SENSITIVE** |
| 3 | 719 | Transfer-tax and cooling-period governance package | Governance / Spec | **SENSITIVE** |
| 4 | 720 | Commons dedication and leasehold / reversion calibration | Governance / Spec | **SENSITIVE** |
| 5 | 721 | ADR-0015 disposition, simulation / replay commissioning, and CDL opening recommendation or deferment | Research / Handoff | **SENSITIVE** |
| 6 | 722 | Coherence report, capsule v4.8, and window `717-722` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 717 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_717_722_sequence_lock_v0.1.md`

Required content:
- lock the six-phase ordering for `717-722`,
- state that no pre-window conversation is required,
- state that no CDL ratification is planned in-window,
- require explicit per-mechanism disposition before closure,
- state that Track B status must be checked against `STATUS.md` tail,
- state that closure phase is `722`.

### Phase 718 — ADR-0015 family inventory and scoping

Deliverables:
- `docs/specs/ilc_adr_0015_family_inventory_and_scope_718_v0.1.md`

Required content:
- map transfer tax, cooling period, commons dedication, and leasehold /
  reversion to their current documented state,
- identify inherited constraints and preserved invariants,
- identify which claims are already grounded versus still simulation-dependent,
- identify launch-bound versus post-launch versus deferred decision inputs,
- avoid making the final ADR-0015 disposition in this phase.

### Phase 719 — transfer tax and cooling package

Deliverables:
- `docs/specs/ilc_node_transfer_economics_and_cooling_period_governance_package_719_v0.1.md`

Required content:
- define the visible-transfer and anti-speculation boundary,
- define the transfer-tax structure without overclaiming numeric constants,
- define the cooling-period duration class and why that class fits the protocol,
- preserve creator attribution permanence and governance decoupling,
- record the launch-bound / post-launch / deferred posture for transfer-tax and
  cooling-period mechanics.

### Phase 720 — commons dedication and leasehold / reversion

Deliverables:
- `docs/specs/ilc_commons_dedication_and_treasury_routing_note_720_v0.1.md`
- `docs/specs/ilc_leasehold_duration_and_reversion_calibration_note_720_v0.1.md`

Required content:
- define commons-dedication mechanics and the treasury / public-goods routing
  boundary,
- state the validated IP-dispute exception path,
- define the leasehold duration-class question and reversion trigger taxonomy,
- state whether reset-on-transfer is accepted, rejected, or still open,
- avoid silently activating leasehold if the evidence is not there.

### Phase 721 — disposition and commissioning

Deliverables:
- `docs/specs/ilc_adr_0015_node_transfer_economics_disposition_721_v0.1.md`
- `docs/specs/ilc_transfer_tax_cooling_and_leasehold_simulation_replay_contract_721_v0.1.md`
- `docs/specs/ilc_transfer_economics_cdl_opening_recommendation_or_deferment_721_v0.1.md`

Required content:
- publish the explicit accepted / amended / rejected / deferred verdicts,
- publish the launch-bound / post-launch-bound / deferred matrix,
- commission simulation / replay evidence for transfer tax, cooling period, and
  leasehold duration,
- state clearly whether any new CDL opening is recommended or deferred,
- avoid turning a recommendation memo into a ratification event.

### Phase 722 — closure

Deliverables:
- `docs/specs/ilc_coherence_report_722_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.8.md`
- `docs/specs/ilc_window_717_722_closure_gate_722_v0.1.md`

Required content:
- summarize Phases `717-721`,
- record the explicit ADR-0015 family disposition,
- record whether any CDL opening is recommended or deferred,
- update the capsule to v4.8,
- route carry-forward explicitly into Window `723-726` and any later economic
  evidence lanes.

---

## 7. Phase-specific open questions, options, and recommendations

### 7.1 ADR-0015 disposition shape

Open question:
- should ADR-0015 be accepted wholesale, rejected wholesale, or split into
  per-mechanism verdicts?

Options:
- accepted as one family,
- rejected as one family,
- explicit per-mechanism amended / accepted / deferred split.

Recommendation:
- use the per-mechanism split. The repo already treats transfer tax, commons
  dedication, and leasehold as related but not equally mature.

### 7.2 Transfer-tax authority level

Open question:
- is the transfer-tax claim constitutional principle, spec-level policy, or
  still too early?

Options:
- constitutionalized this window,
- `spec_or_contract_lock` this window with numeric calibration deferred,
- fully deferred.

Recommendation:
- `spec_or_contract_lock` with explicit numeric deferment. The visible-taxed
  transfer principle is strong; the exact rates are not.

### 7.3 Cooling-period duration class

Open question:
- should cooling period be expressed in epochs, issuance cycles, or wall-clock
  time?

Options:
- epochs,
- issuance cycles,
- calendar time,
- deferred.

Recommendation:
- epochs. It matches the protocol’s existing temporal law better than wall-clock
  or issuance-cycle framing, while leaving the exact count for later evidence.

### 7.4 Commons-dedication routing boundary

Open question:
- is commons dedication treasury-only, selector-based, or still unresolved?

Options:
- treasury only,
- treasury or public-goods fund under bounded governance routing,
- deferred.

Recommendation:
- bounded routing under the existing `CDL-047` treasury framework. Do not
  create a free-form sink, but do not force every dedication into a single
  treasury destination if the architecture already contemplates public-goods
  routing.

### 7.5 Commons fraction and voluntariness

Open question:
- should the commons take-rate be a constitutional fraction, a governed range,
  or purely voluntary dedication?

Options:
- fixed constitutional fraction,
- governance-bounded range,
- purely voluntary dedication,
- deferred.

Recommendation:
- separate the questions. Voluntary dedication can be accepted as a mechanism
  now; any protocol-imposed fraction should remain a bounded policy question
  rather than a new constitutional constant in this window.

### 7.6 Leasehold / reversion activation

Open question:
- should leasehold become launch-bound now, post-launch-bound, or deferred?

Options:
- launch-bound activation,
- post-launch-bound activation,
- explicit deferment.

Recommendation:
- do not force launch-bound activation without the missing simulation. The
  honest likely outcomes are `post_launch_bound` or `deferred`, with the
  reversion taxonomy written now and the activation threshold written later.

### 7.7 Need for a new CDL opening

Open question:
- does the transfer-economics lane need a new CDL opening now?

Options:
- recommend a new CDL opening,
- explicit deferment with spec / contract lock only,
- defer the entire family.

Recommendation:
- do not assume a new CDL. Let Phase `721` decide after the family disposition
  and commissioning contract exist. The packet should preserve that as a real
  question rather than a hidden conclusion.
