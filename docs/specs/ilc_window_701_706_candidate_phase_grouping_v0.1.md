# ILC Window 701-706: Candidate Phase Grouping (Codex Lead)

**Author:** Codex
**Date:** 2026-04-17
**Baseline:** Window `693-700` is closed. Capsule v4.4 is published. `CDL-066`,
`CDL-017`, and `CDL-067` remain open and unratified. Window `701+` carry-forward
program is active.
**Reference:** `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.1 and §5.1
**Document schema:** `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

---

## 1. Window identity and scope

Window `701-706` is the first post-`700` carry-forward lane. It exists to
close the economically important but under-locked items that still sit between
historical literature and current canon.

This window is responsible for:

1. writing the sequence lock for `701-706`,
2. tracing `W_e = ΔH / E_cost` into current runtime/kernel surfaces and
   classifying it honestly as doctrine or law,
3. fixing the Phase `703` calibration scope around the actual four-component
   ECU kernel:
   - `reuse`
   - `contradiction_resilience`
   - `validation_integrity`
   - `path_uplift`
4. publishing a concrete replay/calibration contract for the fixed-vector ECU
   profile family,
5. doctrine-locking the “ILC is post-banking” framing without overclaiming it
   as law,
6. publishing the inverted-ECU runtime traceability note and stating whether
   current ratified mechanics partially operationalize that historical model,
7. closing the window with a coherence report, capsule v4.5, and closure gate.

This window does NOT:
- ratify `CDL-066`, `CDL-017`, or `CDL-067`,
- reopen rows `5-9`,
- open or ratify `CDL-053`,
- treat explanatory economic doctrine as constitutional law by implication,
- reframe the ECU kernel into stake / reputation / diversity / recency slots
  that are not the current kernel contract.

---

## 2. Inter-lane dependencies

### 2.1 Upstream baseline

This window inherits:
- Window `693-700` closure and capsule v4.4,
- row `5 = spec_closed_runtime_pending`,
- row `7 = spec_closed_runtime_pending`,
- row `8 = confirmed`,
- `CDL-066`, `CDL-017`, and `CDL-067` as open but unratified.

### 2.2 Downstream dependency created here

Window `687-692` and Phase `693` comparison work already named BAL-profile
weights as unratified planning inputs. This window must resolve that ambiguity
to the level of an executable calibration contract.

Implication:
- benchmark or workload claims that rely on BAL-profile ECU sizing remain
  planning-level until Phase `703` publishes the calibration/replay contract,
- later windows may build on the Phase `703` contract,
- later windows may NOT pretend that BAL-profile weights were already settled
  law before this window runs.

### 2.3 Relationship to Track B / implementation

There is no same-window hard blocker from this lane into current Mysticeti
implementation work. The relationship is evidentiary and governance-facing:
- Phase `703` affects when ECU-profile assumptions become authoritative,
- Phase `705` affects how later windows talk about inverted circulation,
- none of Phases `701-706` authorize immediate runtime changes by themselves.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `701` sequence lock
- Phase `702` `W_e` traceability and doctrine classification
- Phase `703` BAL-profile kernel calibration and replay contract
- Phase `704` post-banking doctrine lock
- Phase `705` inverted-ECU runtime traceability and doctrine preservation
- Phase `706` coherence report, capsule v4.5, and closure gate

### 3.2 Explicitly deferred

- any `constitutional_lock` move on ECU profile weights
- any opening or ratification action for `CDL-053`
- any ratification action for `CDL-066`, `CDL-017`, or `CDL-067`
- any reopening of rows `5-9`
- any implementation mandate for `ADAPT`
- any claim that doctrine notes alone create binding governance law

---

## 4. Governing constraints inherited from prior windows

Constitutional and planning anchors that govern this window:
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md`
- `docs/whitepaper/whitepaper_ecu_profiles_and_payouts_v0.2.md`
- `docs/specs/ilc_cdl_062_research_lane_handoff_692_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`

Hard constraints:
- the ECU kernel under test is the current four-component kernel and must be
  named exactly as such,
- `freshness_gate` / temporal decay is not a weight slot in the Phase `703`
  vector sweep,
- `CDL-V3` diversity floor is not a weight slot in the Phase `703` vector
  sweep,
- `BAL` is the active kernel default and a planning assumption, not a ratified
  constitutional constant,
- the fixed-vector candidate family for Phase `703` is:
  - `EVEN = 0.25 / 0.25 / 0.25 / 0.25`
  - `BAL = 0.35 / 0.25 / 0.20 / 0.20`
  - `ROBUST = 0.20 / 0.45 / 0.20 / 0.15`
  - `REFINE = 0.45 / 0.15 / 0.20 / 0.20`
- `ADAPT` is excluded from the fixed-vector sweep unless a separate formal
  profile-spec artifact is first written,
- replay tiers for Phase `703` are:
  - `100-agent` deterministic preflight tier,
  - `10,000-agent` deterministic evidence-bearing tier,
  - `40-epoch` simulation posture aligned with the whitepaper’s economic
    validation framing.

Phase `705` hard constraint:
- the artifact must explicitly evaluate whether `CDL-V1` temporal decay and
  `CDL-048` mandatory conversion are partial operational implementation of the
  inverted-ECU circulation model.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 701 | Window `701-706` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 702 | `W_e = ΔH / E_cost` traceability and doctrine classification | Doctrine / Mapping | **SENSITIVE** |
| 3 | 703 | BAL-profile kernel calibration and replay contract | Evidence / Calibration | **SENSITIVE** |
| 4 | 704 | “ILC is post-banking” doctrine lock | Doctrine / Boundary | **SENSITIVE** |
| 5 | 705 | Inverted-ECU runtime traceability and doctrine preservation | Traceability / Doctrine | **SENSITIVE** |
| 6 | 706 | Coherence report + capsule v4.5 + window `701-706` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 701 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_701_706_sequence_lock_v0.1.md`

Required content:
- lock the six-phase ordering for `701-706`,
- state that this window classifies and calibrates doctrine/runtime links but
  does not ratify open CDLs,
- lock the Phase `703` kernel and profile-family scope,
- state that `ADAPT` is excluded from the fixed-vector sweep,
- state the replay tiers and evidence-bearing expectation.

### Phase 702 — `W_e` traceability and doctrine classification

Deliverables:
- `docs/research/ilc_w_e_traceability_and_kernel_mapping_note_702_v0.1.md`

Required content:
- trace `W_e = ΔH / E_cost` into current canonical economic language,
- map the formula to the present four-component kernel as an explanatory
  approximation rather than a ratified formula-binding,
- classify the item explicitly as doctrine or law,
- state what runtime surfaces, if any, currently echo the formula.

### Phase 703 — BAL-profile kernel calibration and replay contract

Deliverables:
- `docs/specs/ilc_ecu_kernel_profile_calibration_note_703_v0.1.md`

Required content:
- define the calibration target as the current four-component ECU kernel,
- include the fixed-vector candidates `EVEN`, `BAL`, `ROBUST`, `REFINE`,
- explicitly exclude `ADAPT` from the fixed-vector sweep,
- define deterministic replay tiers:
  - `100-agent` preflight,
  - `10,000-agent` evidence-bearing,
- define sensitivity dimensions and behavioral expectations,
- define the evidence threshold for any later `constitutional_lock` move,
- state that Phase `703` is not allowed to stop at “plan a calibration later”.

### Phase 704 — post-banking doctrine lock

Deliverables:
- `docs/research/ilc_post_banking_economic_doctrine_note_704_v0.1.md`

Required content:
- preserve the post-banking framing as explanatory doctrine,
- map any real runtime implications to already-ratified mechanics,
- state explicitly that the doctrine note is not itself binding law,
- identify what is preserved, what is rejected, and what remains future
  governance territory.

### Phase 705 — inverted-ECU runtime traceability note

Deliverables:
- `docs/research/ilc_inverted_ecu_model_runtime_traceability_note_705_v0.1.md`

Required content:
- preserve the inverted-ECU design lineage honestly,
- state whether `CDL-V1` temporal decay and `CDL-048` mandatory conversion are
  operational implementations of inverted circulation,
- distinguish partial runtime echo from unratified historical doctrine,
- avoid treating the full inverted-ECU model as already-canonical law.

### Phase 706 — coherence report, capsule, and closure gate

Deliverables:
- `docs/specs/ilc_coherence_report_706_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.5.md`
- `docs/specs/ilc_window_701_706_closure_gate_706_v0.1.md`

Required content:
- summarize the dispositions of Phases `701-705`,
- update the capsule to v4.5,
- record what remains doctrine, what is `spec_or_contract_lock`, and what is
  explicitly non-ratified,
- route carry-forward into `707-712` and later windows without ambiguity.

---

## 7. Hard non-goals for the full window

- Do not silently convert doctrine into law.
- Do not pretend BAL profile weights are ratified because they are active in
  the kernel.
- Do not treat `ADAPT` as executable without a formal spec and governance path.
- Do not reframe the ECU kernel away from the current four-component contract.
- Do not use the `7-agent` live testnet as constitutional-quality evidence for
  profile calibration.
- Do not let any item exit the window as “real but undefined”.
