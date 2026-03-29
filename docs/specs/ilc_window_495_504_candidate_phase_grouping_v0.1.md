# ILC Window 495-504: Candidate Phase Grouping

**Author:** Local architectural reviewer (Window 495-504 planning)
**Date:** 2026-03-29
**Baseline:** Window 485-494 CLOSED (Scenario A expected: CDL-054 ratified, CDL-055 opened and
prelock-hardened, CDL-053 reservation intact). Phase 495 is the next numbered phase.
**Planning note:** This is a candidate grouping only, not a locked sequence. Phase 495 seals the
sequence lock. The CDL-055 carry-forward ratification (Phase 496) is unconditional. Phases 499-501
are gated on Phase 497 governance boundary analysis and CDL-055 ratification. Phase 504 always
executes as the closure gate.

---

## 1. Window identity and scope

Window 495-504 is the validator trust-tier and staking ratification window. Its narrow purpose is
threefold:

1. ratify the carried-forward `CDL-055` Validator Staking and Liveness Enforcement lane,
2. open, harden, and ratify `CDL-056` Validator Trust-Tier Elevation after a governance boundary
   analysis confirms the constitutional pathway,
3. scope the epoch-boundary economic enforcement witness surface and record an `ADM-001 v0.3`
   amendment incorporating the trust-tier elevation rule.

This window is not the place to open `CDL-053`, redesign the 7+1 panel, advance long-tail
economics, or carry optional validator co-location. Those remain separate lanes.

---

## 2. Baseline and inheritance

The window inherits the following canonical state from Window 485-494:

- `CDL-054` (Validator Economic Incentive Framework) is ratified.
- `CDL-055` (Validator Staking and Liveness Enforcement) is status: open, prelock-hardened in
  Phase 493, and carried forward for ratification as the first priority of this window.
- `CDL-053` remains reserved for Werner credit architecture and must not be consumed by any
  work in this window.
- `ilc_core/consensus/circuit_breaker_interface.py` (Phase 488) is the circuit-breaker runtime.
- `ilc_core/consensus/finality_evaluator.py` (CDL-051) remains the authoritative finality surface.
- SIM-010 verdict is `pass` with outputs `recommended_validator_reward_fraction`,
  `recommended_genesis_stake_amount`, and `recommended_liveness_miss_threshold` recorded in
  `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md`.
- `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md` is the canonical validator
  enhancement planning artifact. Window 495-504 must disposition the trust-tier elevation lane
  and epoch boundary enforcement scoping line items from that roadmap.
- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md` remains
  the separate planning placeholder for minimum-scope `CDL-053` and long-tail economics. This
  window must re-affirm its deferral explicitly.

Next fresh CDL numbering rule for this window:

- `CDL-055` carry-forward ratification does not require a new number assignment.
- Validator Trust-Tier Elevation is provisionally assigned `CDL-056`.
- No further fresh CDL numbers are assigned in this window.
- `CDL-053` remains unopened and reserved.

---

## 3. Track inventory

### 3.1 Constitutionally obligated or already authorized surfaces

- **CDL-055 ratification carry-forward** — prelock-hardened in Phase 493; SIM-010 evidence
  already locked. Ratification is the first order of business for this window.
- **Validator Trust-Tier Elevation (CDL-056)** — roadmap §3.5 requires a governance boundary
  analysis before opening. Phase 497 resolves that analysis before Phase 499 opens CDL-056.
- **ADM-001 v0.3 amendment** — the 7+1 panel composition document must record the active-validator
  trust-tier elevation flag and dispute tiebreaker rule established by CDL-056.

### 3.2 Research and scoping obligations

- **Trust-tier governance boundary analysis (Phase 497)** — determines whether CDL-056 requires
  the new CDL-056 lane plus a companion ADM-001 amendment, or whether the trust-tier path must
  remain deferred, and establishes the constitutional compatibility argument with CDL-V3 and
  CDL-046 liveness threshold.
- **Epoch-boundary enforcement architectural scoping (Phase 498)** — assesses whether validator
  attestation as witness for ECU→ILC conversion batches requires a CDL-030 or CDL-051 amendment.
  Result is a scoping artifact, not a CDL opening.

### 3.3 Deferred governance lanes

- **CDL-053 Werner credit architecture** — separate lane, not part of this window. Re-affirmed
  deferred in Phase 503.
- **Long-Tail and Post-Issuance Economics Research Track (LT-0 through LT-4)** — separate lane,
  not part of this window.
- **Optional validator co-location protocol** — deferred to Window 505+.
- **Validator network join and recovery flow** — deferred to Window 505+.
- **Epoch-boundary CDL amendment (CDL-030 or CDL-051)** — if Phase 498 scoping finds amendment
  needed, the CDL opening is deferred to Window 505+.

### 3.4 CDL-056 gate dependency

The following are not eligible for constitutional lock until Phase 497 governance boundary
analysis produces a passing output:

- whether CDL-056 is the required constitutional lane or whether the trust-tier path must
  remain deferred,
- the trust-tier flag eligibility criteria (liveness threshold, genesis vs non-genesis
  validators),
- the constitutional compatibility argument with CDL-V3 diversity floor and CDL-046 liveness.

---

## 4. CDL-055 ratification track

The Phase 493 prelock hardening completed the evidence ladder and boundary work needed before
CDL-055 can be ratified. The SIM-010 evidence (`recommended_genesis_stake_amount`,
`recommended_liveness_miss_threshold`) was locked in Phase 487.

Ratification sequence:

- **Phase 496** — ratification evidence for CDL-055, closing the carry-forward lane from
  Window 485-494.

This lane must not introduce new staking primitives beyond those authorized in Phase 493.
Stake amounts and liveness thresholds are governed by SIM-010 evidence and must not be
renegotiated at ratification time.

---

## 5. Validator trust-tier elevation lane

This lane adds a non-inheritable trust-tier elevation flag for active validators. It amends
the 7+1 evaluation panel composition (ADM-001) and requires a new constitutional lane
provisionally numbered `CDL-056`, contingent on Phase 495 numbering lock.

The elevation flag:
- is awarded to validators meeting the CDL-055 liveness threshold,
- is visible in 7+1 panel composition for governance disputes touching consensus-layer
  decisions,
- grants a tiebreaker advantage (not an additional panel seat) in consensus-related disputes,
- is revoked when a validator falls below the liveness threshold.

This lane must not redesign the 7+1 panel, change L-tier quorum requirements, or merge with
the CDL-053 Werner credit lane.

Candidate sequence:

- **Phase 497** — trust-tier governance boundary analysis.
- **Phase 499** — opening stub for Validator Trust-Tier Elevation.
- **Phase 500** — prelock hardening, evidence-source ladder, and constitutional compatibility
  argument.
- **Phase 501** — ratification evidence, gated on Phase 497 analysis.

---

## 6. ADM-001 v0.3 amendment and epoch scoping tracks

### 6.1 ADM-001 v0.3 amendment

CDL-056 ratification alone locks the constitutional rule for trust-tier elevation. An ADM-001
v0.3 amendment translates that rule into operational panel-composition guidance. This is a
doc-only phase, not a CDL mutation.

- **Phase 502** — publish `ADM-001 v0.3` incorporating CDL-056-authorized trust-tier elevation
  language.

### 6.2 Epoch-boundary enforcement architectural scoping

Validators currently sign epoch finality attestations but are disconnected from ECU→ILC
conversion batches (CDL-030, P_e clamp). A scoping phase determines whether adding a
validator witness role requires a CDL amendment.

- **Phase 498** — architectural scoping artifact only. No CDL opened. If amendment is needed,
  it is a Window 505+ carry-forward.

---

## 7. CDL number assignments

| CDL | Title | Decision digest anchor | Opening phase | Ratification phase |
|---|---|---|---|---|
| CDL-053 | Werner credit architecture (reserved, separate lane) | reserved by CDL-053 placeholder | none | none |
| CDL-055 | Validator Staking and Liveness Enforcement (carry-forward) | `genesis_stake_amount`, `liveness_miss_threshold`, `equivocation_full_slash`, `re_admission_boundary` | Phase 492 (Window 485-494) | Phase 496 |
| CDL-056 | Validator Trust-Tier Elevation | `trust_tier_elevation_flag`, `liveness_threshold_tie`, `consensus_dispute_tiebreaker` | Phase 499 | Phase 501 |

Note: Phase 495 must preserve the reservation boundary for `CDL-053` explicitly and must not
permit CDL-056 numbering to silently consume `CDL-053`.

---

## 8. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 495 | Sequence lock and scope freeze | Foundation / Constitutional | **SENSITIVE** |
| 2 | 496 | CDL-055 ratification evidence (carry-forward) | Constitutional | **SENSITIVE** |
| 3 | 497 | Validator trust-tier governance boundary analysis | Research | NON-SENSITIVE |
| 4 | 498 | Epoch-boundary enforcement architectural scoping | Research | NON-SENSITIVE |
| 5 | 499 | Validator Trust-Tier Elevation opening stub | Constitutional | **SENSITIVE** |
| 6 | 500 | Validator Trust-Tier Elevation prelock hardening | Constitutional / Doc | NON-SENSITIVE |
| 7 | 501 | Validator Trust-Tier Elevation ratification evidence | Constitutional | **SENSITIVE** |
| 8 | 502 | ADM-001 v0.3 validator trust-tier amendment | Governance doc | NON-SENSITIVE |
| 9 | 503 | Coherence report and capsule v2.3 | Integration | NON-SENSITIVE |
| 10 | 504 | Closure gate and handoff | Gate | **SENSITIVE** |

### Note on CDL-056 gate dependency

Phases 499-501 are draft slots but are not executable unless Phase 497 produces a passing
governance boundary analysis that:

- confirms CDL-056 is the correct constitutional lane (not a plain ADM-001 amendment),
- states the trust-tier eligibility criteria clearly,
- confirms compatibility with CDL-V3 diversity floor and CDL-046 liveness threshold.

If Phase 497 does not support `CDL-056` as the required constitutional lane, then Phases
499-502 do not execute and Phase 504 records the blocked carry-forward path. `ADM-001 v0.3`
is a companion amendment to CDL-056, not a substitute for it.

### Note on Phase 504 non-ratifying boundary

Phase 504 closes the window and records one of two states:

- **Scenario A** — CDL-055 ratified and CDL-056 ratified and ADM-001 v0.3 published, or
- **Scenario B** — CDL-055 ratified but CDL-056 governance boundary analysis blocked the CDL
  opening (ADM-001 v0.3 deferred with CDL-056).

Phase 504 never opens a new CDL.

---

## 9. Sensitivity classification

### SENSITIVE phases

- **Phase 495** — opens the new window and freezes numbering and scope.
- **Phase 496** — ratifies CDL-055 in the decision log.
- **Phase 499** — opens CDL-056 in the decision log.
- **Phase 501** — ratifies CDL-056.
- **Phase 504** — structural closure gate.

### NON-SENSITIVE phases

- **Phase 497** — governance boundary analysis only; no decision-log mutation.
- **Phase 498** — architectural scoping only; no decision-log mutation.
- **Phase 500** — prelock hardening only; no decision-log mutation.
- **Phase 502** — ADM-001 v0.3 doc amendment; no decision-log mutation.
- **Phase 503** — coherence report and capsule; no decision-log mutation.

### GO-token rule

Sensitive phases require the standard mutation gate or explicit human GO at execution time.
Non-sensitive phases do not mutate the decision log but still require prompt validation and
entry criteria to pass.

---

## 10. Scope notes for fixed phases

### Phase 495

Locks the window, dispositions CDL-055 carry-forward, provisionally assigns CDL-056,
preserves the CDL-053 reservation, and freezes the scope set by the validator roadmap.

### Phase 496

Ratifies CDL-055 using the Phase 493 prelock and Phase 487 SIM-010 evidence already
locked. No new stake calibration permitted at ratification time.

### Phase 497

Governance boundary analysis only. Produces
`ilc_cdl_056_validator_trust_tier_governance_boundary_analysis_497_v0.1.md`. Determines
whether CDL-056 is the required lane or whether the trust-tier path remains deferred, and
states constitutional compatibility explicitly.

### Phase 498

Epoch-boundary economic enforcement architectural scoping. Produces
`ilc_epoch_boundary_enforcement_architectural_scoping_498_v0.1.md`. Does not open a CDL.
Any recommended amendment is a Window 505+ carry-forward.

### Phase 499-501

Open, harden, and ratify the Validator Trust-Tier Elevation CDL only if Phase 497 confirms
CDL-056 is the right lane. Evidence ladder anchored in Phase 497 analysis and CDL-055
ratification.

### Phase 502

Translates CDL-056 ratification into operational ADM-001 v0.3 language for the 7+1 panel.
If CDL-056 did not ratify in this window, Phase 502 is omitted and Phase 503 records the
deferred state.

### Phase 503

Coherence report covering all Window 495-504 decisions. Capsule v2.3 update. Explicit
re-deferral disposition for CDL-053, LT-track, and epoch-boundary CDL carry-forward.
Must reference `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md` under validator
infrastructure and must reference ADR-0022 and gated-shard rights/access hardening lane
separately from CDL-053.

### Phase 504

Closure gate with scenario-aware handoff. Full selftest chain audit required before
drafting the gate script.

---

## 11. Key dependencies and open questions

### Must-resolve at entry (Phase 495)

- confirmation that CDL-055 carry-forward can ratify using only Window 485-494 prelock and
  SIM-010 evidence without new calibration,
- whether CDL-056 numbering is clean given CDL-053 reservation (it is, since CDL-055 is
  already assigned and CDL-056 is the next sequential number),
- whether the epoch-boundary scoping (Phase 498) must precede CDL-056 opening (it does not;
  CDL-056 trust-tier work is independent of epoch-boundary enforcement).

### Sequencing constraints

- Phase 496 must complete before Phase 499.
- Phase 497 must complete before Phase 499.
- Phase 499-501 must not silently ratify staking constants — those are locked by CDL-055.
- Phase 502 must complete before Phase 503.
- Phase 504 must check both the validator roadmap and CDL-053 placeholder for carry-forward
  consistency.

### Open questions

- does the trust-tier elevation flag need a runtime implementation in this window, or is
  constitutional ratification and ADM-001 v0.3 enough?
- is the `tiebreaker advantage` model the right design, or does CDL-056 need a mandatory
  validator seat in consensus-layer dispute panels?
- what is the correct bridge between CDL-046 liveness threshold (for content claims) and
  CDL-055 liveness threshold (for validator participation stakes) when determining trust-tier
  eligibility?

### Permanently deferred for this window

- CDL-053 opening,
- optional validator co-location,
- validator network join and recovery,
- long-tail and post-issuance economics,
- epoch-boundary CDL amendment (scoping only),
- threshold signature schemes.

---

## 12. Known patterns and technical constraints

- **CDL-055 carry-forward ratification pattern** — CDL-055 has a complete prelock from Phase 493.
  The ratification evidence artifact (Phase 496) follows the same 6-section structure used by
  CDL-054 (Phase 491): headings for ratified lane identity, evidence anchors, rejected
  alternatives, constitutional boundary, governance tokens, and Section-5 checklist satisfaction.
- **ADM-001 amendment pattern** — ADM-001 v0.2 was produced in Phase 336/400 context. The v0.3
  amendment in Phase 502 must be a named amendment doc, not a silent overwrite.
- **Closure gate selftest chain** — Phase 504 must audit every prior closure gate test file
  that includes a `test_gate_full_run_*` function and add the corresponding
  `ILC_PHASE_NNN_GATE_SELFTEST=1` guard to the new gate script. Do not copy by analogy from
  the Phase 494 gate — read the actual test files.
- **Phantom edit guard** — no `ilc_core/` runtime phases in this window. All CDL phases
  (496, 499, 501) must verify `git diff --exit-code -- ilc_core/` as clean.
- **Capsule update obligation** — capsule v2.3 (Phase 503) must explicitly reference
  ADR-0022 and the private/gated shard rights/access hardening lane separately from CDL-053,
  per the CDL-053 placeholder §9 carry-forward obligation.

---

## 13. Non-goals and explicitly deferred items

- opening or ratifying CDL-053,
- trust-tier redesign or L-tier quorum changes,
- long-tail post-issuance economics,
- optional validator co-location,
- validator network join and recovery,
- epoch-boundary CDL amendment (scoping only),
- new treasury primitives,
- threshold signature schemes,
- biometric or proof-of-personhood validator credential.

---

## 14. Key canonical anchors for prompt drafting

- `docs/specs/ilc_window_485_494_handoff_494_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.2.md`
- `docs/specs/ilc_validator_enhancement_roadmap_479_v0.1.md`
- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_prelock_hardening_493_v0.1.md`
- `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md`
- `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md`
- `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`

---

## 15. Rationale for single-window scope

1. CDL-055 has a complete prelock and evidence chain from Window 485-494. Ratification is
   overdue and must not wait another window.
2. Trust-tier elevation is the logical next validator governance action after staking and
   liveness are constitutionally settled. It requires CDL-055 ratification to anchor the
   liveness threshold reference.
3. ADM-001 v0.3 is a low-risk, high-value governance doc update that closes the 7+1 panel
   composition gap identified in Phase 339.
4. Epoch-boundary scoping in this window prevents the question from silently accumulating
   as untracked technical debt.
5. Keeping CDL-053 separate avoids scope pollution between validator governance and Werner
   credit architecture.
