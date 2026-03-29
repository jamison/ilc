# ILC Window 485-494: Candidate Phase Grouping

**Author:** Codex (planning audit and prompt drafting)
**Date:** 2026-03-29
**Baseline:** Window 475-484 CLOSED (Phase 484 complete). CDL-050, CDL-051, and CDL-052 are ratified. Capsule v2.2 is current. Genesis validator bootstrap runtime is implemented in bounded form. Phase 485 is the next numbered phase.
**Planning note:** This is a candidate grouping only, not a locked sequence. Phases 485-488 are unconditional. Phases 489-493 are SIM-010-gated constitutional slots. Phase 494 always executes as the closure gate and must record either the completed constitutional path or the blocked carry-forward path.

---

## 1. Window identity and scope

Window 485-494 is the validator economics and bootstrap hardening window. Its narrow purpose is
threefold:

1. execute SIM-010 so validator reward, stake, and liveness thresholds are evidence-sized,
2. implement the already-authorized CDL-045 circuit-breaker surface for validator quorum use,
3. open and, if evidence holds, ratify the validator economic incentive framework while opening
   the validator staking and liveness lane for the next window.

This window is not the place to widen into CDL-053, trust-tier redesign, epoch-boundary economic
witnessing, or co-location policy. Those remain separate lanes.

---

## 2. Baseline and inheritance

The window inherits the following canonical state:

- `CDL-050`, `CDL-051`, and `CDL-052` are ratified.
- `CDL-053` remains reserved for Werner credit architecture and must not be consumed by validator
  enhancement work.
- `ilc_core/consensus/finality_evaluator.py` remains the authoritative finality surface.
- `ilc_core/genesis/validator_bootstrap_runtime.py` and
  `ilc_core/genesis/admission_control_bootstrap.py` are the bounded genesis bootstrap runtime.
- `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md` is the canonical planning artifact
  for validator economics, liveness, circuit breaker, trust-tier, and co-location carry-forward.
- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md` remains the
  separate planning placeholder for minimum-scope `CDL-053` and long-tail economics.

Next fresh numbering rule for this candidate window:

- `CDL-053` remains unopened and reserved.
- validator economic incentive framework is provisionally assigned `CDL-054` if the future
  sequence lock confirms post-`CDL-053` numbering without opening `CDL-053` itself,
- validator staking and liveness enforcement is provisionally assigned `CDL-055` under the same
  rule.

If Phase 485 cannot lock that numbering cleanly, the window must stop rather than silently reuse
`CDL-053`.

---

## 3. Track inventory

### 3.1 Constitutionally obligated or already authorized surfaces

- **SIM-010 validator incentive economics** — required by
  `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md` before either high-priority
  validator CDL can open.
- **CDL-045 circuit breaker authority** — already ratified; only the executable validator-facing
  surface is missing.
- **CDL-047 treasury routing framework** — existing constitutional allocation surface that a
  validator reward pool must extend rather than replace.
- **CDL-046 orphan handling** — existing recovery-policy surface that staking/liveness work must
  amend carefully rather than conflate with validator-participation penalties.

### 3.2 Deferred governance lanes

- **CDL-053 Werner credit architecture** — separate lane, not part of this window.
- **Validator trust-tier elevation** — deferred to Window 495-504 after staking/liveness policy.
- **Epoch-boundary economic enforcement witness surface** — deferred to Window 495-504 scoping.
- **Optional validator co-location protocol** — deferred to Window 505+.

### 3.3 Simulation-conditional items

The following are not eligible for constitutional lock until SIM-010 produces passing outputs:

- validator reward fraction,
- genesis stake amount,
- liveness miss threshold,
- any claim that validator incentives are meaningful at minimum viable network scale.

---

## 4. SIM-010 and circuit-breaker lane

Window 485-488 carries the evidence and already-authorized runtime work needed before validator
constitutional work can proceed.

- **Phase 486** publishes the SIM-010 contract and commissioning brief.
- **Phase 487** executes SIM-010 and must publish the required output recommendations.
- **Phase 488** implements the CDL-045 circuit-breaker interface under `ilc_core/consensus/`
  without opening a new CDL.

The circuit-breaker implementation is not blocked on SIM-010, but the validator economic and
staking lanes are.

---

## 5. Validator economic incentive lane

This lane uses the existing CDL-047 treasury allocation logic and adds a validator-directed reward
policy. It is a new constitutional lane, provisionally numbered `CDL-054`, contingent on the
Phase 485 numbering lock.

Candidate sequence:

- **Phase 489** — opening stub for the Validator Economic Incentive Framework.
- **Phase 490** — prelock hardening, evidence-source ladder, and boundary tightening.
- **Phase 491** — ratification evidence, provided Phase 487 produced the required SIM-010 outputs.

This lane must not introduce new treasury primitives. It only governs routing and reward-allocation
policy inside the existing Treasury framework.

---

## 6. Validator staking and liveness lane

This lane is a constitutional amendment to validator-participation consequences, not a rewrite of
content-claim orphan handling. It is provisionally numbered `CDL-055`, contingent on the Phase 485
numbering lock.

Candidate sequence:

- **Phase 492** — opening stub for Validator Staking and Liveness Enforcement.
- **Phase 493** — prelock hardening for liveness, equivocation, and re-admission boundaries.
- **Phase 494** — closure gate and handoff only; staking ratification is intentionally carried
  forward unless a future amendment widens the window.

This keeps the economic lane closed before the staking lane is asked to lock stake amounts and
slash conditions around a freshly-ratified reward policy.

---

## 7. CDL number assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|---|---|---|---|---|
| CDL-053 | Werner credit architecture (reserved, separate lane) | reserved by roadmap and long-tail placeholder; not opened in this window | none | none |
| CDL-054 | Validator Economic Incentive Framework | `reward_pool_fraction`, `validator_reward_split_policy`, `sim_010_pass_required` | Phase 489 | Phase 491 |
| CDL-055 | Validator Staking and Liveness Enforcement | `validator_stake_amount`, `liveness_miss_threshold`, `equivocation_full_slash`, `re_admission_boundary` | Phase 492 | deferred beyond Window 485-494 |

Note: Phase 485 must preserve the reservation boundary for `CDL-053` explicitly and must not
permit silent renumbering during execution.

---

## 8. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 485 | Sequence lock and scope freeze | Foundation / Constitutional | **SENSITIVE** |
| 2 | 486 | SIM-010 contract and commissioning brief | Simulation | NON-SENSITIVE |
| 3 | 487 | SIM-010 execution and evidence package | Simulation | NON-SENSITIVE |
| 4 | 488 | CDL-045 validator circuit-breaker surface runtime | Runtime | **SENSITIVE** |
| 5 | 489 | Validator Economic Incentive Framework opening stub | Constitutional | **SENSITIVE** |
| 6 | 490 | Validator Economic Incentive Framework prelock hardening | Constitutional / Runtime-prep | NON-SENSITIVE |
| 7 | 491 | Validator Economic Incentive Framework ratification evidence | Constitutional | **SENSITIVE** |
| 8 | 492 | Validator Staking and Liveness Enforcement opening stub | Constitutional | **SENSITIVE** |
| 9 | 493 | Validator Staking and Liveness Enforcement prelock hardening | Constitutional / Runtime-prep | NON-SENSITIVE |
| 10 | 494 | Closure gate and handoff | Gate | **SENSITIVE** |

### Note on SIM-010 gate dependency

Phases 489-493 are fixed draft slots but are not executable unless Phase 487 publishes all three
required recommendations:

- `recommended_validator_reward_fraction`
- `recommended_genesis_stake_amount`
- `recommended_liveness_miss_threshold`

If Phase 487 cannot produce those outputs honestly, the constitutional phases must not execute and
Phase 494 must record a blocked carry-forward rather than a completed validator-CDL window.

### Note on Phase 494 non-ratifying boundary

Phase 494 closes the window and records one of two states:

- **Scenario A** — `CDL-054` ratified and `CDL-055` opened/prelock-hardened, or
- **Scenario B** — SIM-010 blocked the constitutional slots and no validator-economics CDL was
  opened.

Phase 494 never ratifies `CDL-055`.

---

## 9. Sensitivity classification

### SENSITIVE phases

- **Phase 485** — opens the new window and freezes numbering and scope.
- **Phase 488** — mutates `ilc_core/consensus/` with a new validator-facing circuit-breaker
  surface.
- **Phase 489** — opens `CDL-054` in the decision log.
- **Phase 491** — ratifies `CDL-054`.
- **Phase 492** — opens `CDL-055` in the decision log.
- **Phase 494** — structural closure gate.

### NON-SENSITIVE phases

- **Phase 486** — commissioning/specification only.
- **Phase 487** — simulation execution and evidence; no decision-log mutation.
- **Phase 490** — prelock hardening only.
- **Phase 493** — prelock hardening only.

### GO-token rule

Sensitive phases require the standard mutation gate or explicit human GO at execution time.
Non-sensitive phases do not mutate the decision log but still require prompt validation and entry
criteria to pass.

---

## 10. Scope notes for fixed phases

### Phase 485

Locks the window, preserves the `CDL-053` reservation, assigns provisional `CDL-054` and
`CDL-055`, and freezes the scope boundaries set by the validator roadmap.

### Phase 486

Defines SIM-010 inputs, scenarios, pass criteria, output contract, and commissioning boundary.
No simulation is executed in this phase.

### Phase 487

Runs SIM-010, publishes evidence and synthesis, and records whether the economic/staking lane is
allowed to proceed.

### Phase 488

Implements `ilc_core/consensus/circuit_breaker_interface.py` and any required re-exports in
`ilc_core/consensus/__init__.py`. No new CDL is opened.

### Phase 489-491

Open, harden, and ratify the validator economic incentive framework only if the SIM-010 outputs
support opening.

### Phase 492-493

Open and prelock-harden validator staking and liveness enforcement only after the economic lane is
ratified.

### Phase 494

Runs the closure gate, publishes the handoff, and records whether `CDL-055` remains an open carry-
forward lane.

---

## 11. Key dependencies and open questions

### Must-resolve at entry

- whether post-`CDL-053` numbering may lock `CDL-054` and `CDL-055` while `CDL-053` remains
  reserved and unopened,
- the exact SIM-010 simulation harness location (`tools/` plus `out/` evidence package versus a
  dedicated `simulations/` helper),
- whether the circuit-breaker runtime needs a local `CDL_045_DEPENDENCY` token because no canonical
  runtime export exists yet.

### Sequencing constraints

- Phase 487 must complete before Phase 489.
- Phase 491 must complete before Phase 492.
- Phase 492-493 must not silently ratify staking/liveness.
- Phase 494 must check both the validator roadmap and the CDL-053 placeholder for carry-forward
  consistency.

### Open questions

- does `CDL-054` need a runtime implementation in the same window, or is constitutional ratification
  enough for this stage?
- should Phase 488 expose only a validator request/verification surface, or also a read-only status
  view for downstream tooling?
- what is the cleanest bridge from the eventual staking runtime to the already-ratified CDL-046
  orphan policy without overloading terms?

### Permanently deferred for this window

- trust-tier elevation,
- epoch-boundary economic witness surface,
- validator co-location,
- validator network join and recovery,
- `CDL-053` opening.

---

## 12. Known patterns and technical constraints

- **First validator-economics simulation gate** — this is the first window where a simulation study
  explicitly gates validator constitutional openings.
- **Reserved-number carry-forward pattern** — Phase 485 must preserve a reserved CDL number without
  consuming it.
- **Historical prelock hardening** — Phases 490 and 493 must historicalize their opening-state
  assertions once the opening phases exist.
- **Phantom edit guard** — any runtime phase mutating `ilc_core/consensus/` must read the working
  tree carefully and confirm no unrelated `ilc_core/` edits are present before editing.
- **Closure gate selftest chain** — Phase 494 should inherit the established gate selftest pattern
  and audit prior gate tests directly instead of copying by analogy.

---

## 13. Non-goals and explicitly deferred items

- opening or ratifying `CDL-053`,
- trust-tier policy,
- epoch-boundary economic witness logic,
- validator co-location,
- validator network join and recovery,
- live staking constant calibration outside SIM-010,
- new treasury primitives,
- any biometric or proof-of-personhood validator credential.

---

## 14. Key canonical anchors for prompt drafting

- `docs/specs/ilc_window_475_484_handoff_484_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.2.md`
- `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md`
- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_genesis_validator_bootstrap_runtime_part_2_handoff_481_v0.1.md`
- `docs/specs/ilc_cdl_052_epistemic_evaluation_architecture_ratification_evidence_466_v0.1.md`
- `docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md`

---

## 15. Rationale for single-window scope

1. SIM-010 is the gating evidence lane and must happen before validator economics can be opened
   honestly.
2. Circuit-breaker runtime is already authorized and should not wait for a later constitutional
   window.
3. Economic incentives can be ratified in this window if SIM-010 passes without forcing staking
   ratification prematurely.
4. Staking/liveness is better opened and hardened after the economic lane is settled, then carried
   forward if needed.
5. Keeping `CDL-053` separate avoids scope pollution between validator economics and Werner-credit
   architecture.
