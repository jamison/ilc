# ILC Integration Coherence Report — Window 839–843

**Phase:** 843
**Date:** 2026-04-26
**Window:** 839–843 (Row 8 substrate candidate evaluation and Option B gate re-synthesis)

`option_b_gate_resynthesis_window_839_843_coherence_published`
`option_b_gate_synthesis_verdict_go_recorded`
`row8_substrate_candidate_evaluation_complete`
`high_002_production_hardening_planned`
`window_839_843_hard_constraints_satisfied`

## 1. Window purpose and outcome

This window discharged the sole remaining Option B gate blocker (Row 8 substrate
candidate evaluation), re-synthesized the Option B gate under ADR-0028, produced
the HIGH-002 production hardening planning brief, and advances the capsule to
v5.18.

**Outcome:** Option B is now **selectable**. It is not selected. Option D remains
the active architectural posture until an explicit, deliberate, human-authorized
Option B selection act occurs.

## 2. Phase-by-phase record

| Phase | Topic | Status | Key tokens |
|-------|-------|--------|------------|
| 839 | Sequence lock and baseline verification | ✅ Complete | `row8_substrate_evaluation_window_839_843_sequence_lock_active` |
| 840 | Row 8 substrate candidate evaluation | ✅ Complete | `row8_candidate_passes_exclusion_matrix`, `row8_candidate_evaluation_blocker_discharged` |
| 841 | Option B gate re-synthesis | ✅ Complete | `option_b_gate_synthesis_verdict=go`, `option_b_selectable_not_selected` |
| 842 | HIGH-002 production hardening planning | ✅ Complete | `high_002_phase_a_rust_consensus_fix_authorized_post_window_839_843` |
| 843 | Coherence report + capsule v5.18 + closure gate | ✅ This phase | `option_b_gate_resynthesis_window_839_843_coherence_published` |

## 3. Row 8 substrate candidate evaluation record

**Candidate named:** ILC Native Minimal L1.

A purpose-built, protocol-owned BFT settlement chain operated exclusively by
ILC validators, governed by the existing CDL constitutional framework, with ILC
as the canonical currency and the ILC Genesis record as the legitimacy root.

**Classification:** Phase 673 §4 matrix — "sovereign minimal L1 / BFT network
where protocol legitimacy stays upstream and exit is credible" → presumptively
admissible.

**Exclusion matrix:**

| Rule | Description | Verdict |
|------|-------------|---------|
| E1 | Outside governance override | ✅ Not triggered |
| E2 | Admission/namespace outside protocol lineage | ✅ Not triggered |
| E3 | Settlement legitimacy without protocol receipt | ✅ Not triggered |
| E4 | Reputation continuity depends on outside approval | ✅ Not triggered |
| E5 | Only audit/exit path through one hosted control plane | ✅ Not triggered |
| E6 | Migration requires privileged operator consent | ✅ Not triggered |

**Phase 675 independence lock:** ✅ Satisfied. No outside system can author
protocol legitimacy. ILC Genesis record is the legitimacy root.

**Residual risk noted:** Small initial validator set risks de facto founder
sovereignty. Mitigated by CDL-017 governing independent validator admission,
Phase 812 honest-acknowledgement requirement, and Row 5 parallel-obligation
carry-forward. Does not disqualify the candidate.

## 4. Option B gate re-synthesis record

**Gate conditions evaluated under ADR-0028:**

| Condition | CW-5 (Phase 761) | Phase 841 | Evidence |
|-----------|-----------------|-----------|----------|
| Row 7 proof obligations satisfied | PASS | PASS (unchanged) | CW-3 + CW-4, Phases 759–760 |
| Row 8 exclusion-matrix evaluation | PENDING | PASS | Phase 840 |
| CDL-017 ratification | PENDING | PASS | Phase 765 |

**ADR-0028 Phase 812 amendment (parallel-obligation row treatment):**

| Row | Class | Status |
|-----|-------|--------|
| Row 7 | Hard-closure | ✅ `runtime_closed` |
| Row 5 | Parallel-obligation | `spec_closed_runtime_pending` — acknowledged open |

**Gate verdict:** `option_b_gate_synthesis_verdict=go`

Option B is selectable. Option D remains active posture until explicit
human-authorized selection act.

**What this verdict means and does not mean:**

| Means | Does not mean |
|-------|---------------|
| Option B may be selected in a future deliberate act | Option B is selected now |
| ILC Native Minimal L1 candidate passes admissibility criteria | Candidate is the final chosen substrate |
| ADR-0028 Option D bridge has been honestly discharged | Option D is abandoned immediately |
| Row 5 carry-forward is preserved | Row 5 is waived |

## 5. HIGH-002 production hardening planning record

**Finding:** `process_epoch_checkpoint` requires all-N signatures. BFT-correct
threshold is `quorum_threshold(N) = 2 * floor((N-1)/3) + 1`.

At N=4: required threshold is 3 (not 4). A single offline or Byzantine validator
must not stall liveness at production scale.

**Status:** Planning brief complete (Phase 842). Code-side Phase A (Rust consensus
fix) authorized post-window. Phase B (M-track adversarial validation) authorized
after Phase A.

**Gate dependency:** HIGH-002 Phase A is mandatory before production N≥4, F≥1
deployment. It is explicitly not a blocker for Option B selectability and
explicitly not a blocker for controlled testnet deployment per Phase 826 §3.

## 6. Hard constraint compliance

This window did not:

- mutate `ilc_core/` or `ilc_consensus/`,
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- open any new CDL,
- select a sovereign substrate (evaluation ≠ selection),
- claim Row 5 runtime closure,
- pull the first-validator human gate,
- select Option B (gate re-synthesis ≠ selection),
- claim public RC readiness.

`window_839_843_hard_constraints_satisfied`

## 7. Carry-forward after window 839–843

| Item | Status | Path |
|------|--------|------|
| Explicit Option B selection act | Not yet performed | Human authorization — separate deliberate act |
| Row 5 privacy — SIM-LEAKAGE-03 live run | `spec_closed_runtime_pending` | Rust privacy lane integration gate (human) → SIM-LEAKAGE-03 |
| HIGH-002 Phase A (Rust consensus fix) | Authorized | Next `ilc_consensus/` code window |
| HIGH-002 Phase B (M-track validation) | Authorized after Phase A | M-track phase |
| First-validator human gate | Not yet pulled | Phase 826 §6 checklist |
| CDL-070 (PQ migration ceremony) | Not yet opened | Post-838 forward obligation (D1 resolution path) |
| CDL-071 (temporal tier reconciliation) | Not yet opened | Post-838 forward obligation |
| PUBLIC RC claims | Not authorized | Requires Row 5 closure before public RC |
