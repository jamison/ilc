# ILC Phase 694-700 Sequence Lock v0.1

Status: sequence lock
Date: 2026-04-16
Phase: 694
Owner lane: G8 chosen-substrate legitimacy closure (Track A)
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`phase_694_700_sequence_lock_active`
`cdl_066_opens_as_bounded_agent_sender_authorization_lane_only`
`track_a_phase_694_cdl_066_required_before_m009`
`phase_694_700_does_not_select_final_option_b_configuration`

---

## 1. Baseline

Window 687-692 is closed. Phase 693 addendum is complete.

Inherited architectural baseline:
- `CDL-062` is open as the bounded sovereign-substrate research lane
- Mysticeti is elevated to Tier 1 primary for Option B investigation
- Track B (Gemini M-series) has completed M-001 through M-007
- Track B M-008 is active
- Track A window 694-700 is the constitutional-closure and governance-prep
  lane for the chosen-substrate packet

This lock consumes:
- `docs/specs/ilc_window_694_700_track_a_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`

## 2. Numbering correction and active gate

`stale_cdl_063_sec_001_reference_replaced_by_cdl_066`

Earlier planning text routed SEC-001 to `CDL-063`. That is invalid under the
current decision log:
- `CDL-063` is already ratified for ECU directed commission semantics
- `CDL-064` is already ratified for exact numeric representation
- `CDL-065` is already ratified for coupling invariants governance lock

The agent sender-authorization lane required by SEC-001 therefore opens as
`CDL-066`.

Hard inter-lane gate:
- Track B M-009 approval is blocked until `CDL-066` is opened and the token
  `sec_001_agent_sender_auth_cdl_066_required_before_m009` is recorded

## 3. Inherited constitutional gates

`row_6_upstream_downstream_boundary_active`
- later backend choice may carry already-legitimate protocol state
- later backend choice may not author legitimacy

`row_7_censorship_resistance_evidence_still_required`
- Mysticeti-specific formal evidence is still required before row-7 can move
  to a stronger closure state

`row_8_external_constitutional_center_exclusion_remains_active`
- sovereign ILC deployment must remain independent of outside constitutional
  centers

`row_5_mechanism_proof_remains_required`
- the privacy-preserving public legitimacy narrowing must be re-proven against
  the concrete Mysticeti architecture

`cdl_039_transport_invariants_not_reopened_here`
- this window may name transport-adjacent implications, but it does not reopen
  the CDL-039 invariant surface

## 4. What this window does

Track A in 694-700 is authorized to:
- open `CDL-066` as the bounded SEC-001 constitutional lane
- open `CDL-017` as the validator governance framework lane
- open `CDL-067` as the settlement-state CDL vehicle
- produce row-5, row-7, and row-8 Mysticeti-specific closure artifacts
- publish coherence and closure-gate artifacts for 693-700

Track A in 694-700 is not authorized to:
- ratify `CDL-066`
- ratify `CDL-017`
- select the final Option B production configuration
- authorize production validator deployment
- reopen or relax rows 6, 7, or 8
- make public-launch or token-issuance claims

## 5. Phase table and sequencing

| Phase | Topic | Character | Gate |
|---:|---|---|---|
| 694 | Sequence lock + `CDL-066` opening stub | Gate / Planning | **SENSITIVE** |
| 695 | `CDL-017` opening stub | Gate / Constitutional | **SENSITIVE** |
| 696 | `CDL-067` settlement-state CDL opening | Constitutional | **SENSITIVE** |
| 697 | Row-5 mechanism proof over Mysticeti | Research / Proof | **SENSITIVE** |
| 698 | Row-7 TLC model-check evidence | Research / Formal | planning |
| 699 | Row-8 sovereign configuration confirmation | Analysis / Criteria | planning |
| 700 | Coherence report + capsule v4.4 + closure gate | Gate / Handoff | **SENSITIVE** |

Phases execute in order. Phase 694 must complete before any claim is made that
Track B may proceed to M-009 approval.

## 6. Inter-lane dependency note

`m009_cannot_be_approved_without_cdl_066_open`

Track B owns M-008 implementation work in parallel. Track A owns the narrow
constitutional opening required for SEC-001.

The dependency is specific:
- Track B does not need `CDL-066` ratified for M-008
- Track B does need `CDL-066` opened before M-009 is approved
- `CDL-017` does not gate Track B before M-019

## 7. Non-goals

This sequence lock does not:
- convert Mysticeti from Tier 1 primary into the final production winner
- decide the final sender-signature wire format
- decide the final sender-signature algorithm
- reopen `CDL-039` transport invariants
- fold validator governance activation into SEC-001
- silently rewrite older ratified `CDL-063` semantics

## 8. Source inputs

Required source inputs bound by this lock:
- `docs/specs/ilc_window_694_700_track_a_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
