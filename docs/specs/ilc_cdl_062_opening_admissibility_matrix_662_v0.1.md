# ILC CDL-062 Opening Admissibility Matrix 662 v0.1

Status: opening-side admissibility artifact
Date: 2026-04-14
Phase: 662
Boundary: pre-opening threshold only

## 1. Purpose and boundary

`cdl_062_opening_admissibility_precedes_not_equals_option_b_selection`

This matrix defines what must be true before `CDL-062` may later open.

It is not a substrate-selection memo.
It is not final `Option B` authorization.
It is an opening-side threshold artifact only.

## 2. Formal opening-side gates

`row_6_closed_required_before_cdl_062_admissible`
`rows_7_and_8_must_be_locked_as_selection_criteria_before_cdl_062_admissible`
`row_9_material_evidence_required_before_cdl_062_admissible`
`row_5_must_be_narrowed_before_cdl_062_admissible`
`agent_suitability_gates_required_before_cdl_062_admissible`
`machine_legible_participation_gate_required_before_cdl_062_admissible`
`harness_agnostic_access_gate_required_before_cdl_062_admissible`
`agent_participant_parity_gate_required_before_cdl_062_admissible`
`human_auditability_copreservation_gate_required_before_cdl_062_admissible`
`bounded_agent_economic_participation_non_prohibition_gate_required_before_cdl_062_admissible`

The opening-side gates are:
- row 6 must be closed through the CDL-065 governance-lock lane
- rows 7 and 8 must be locked as future substrate-selection criteria
- row 9 must have material transport/discovery maturity evidence
- row 5 must be narrowed enough that the sovereign substrate lane is not
  opening into a privacy vacuum

The bounded derived agent-suitability gates are:
- machine-legible participation:
  core public surfaces must remain accessible to digital agents through
  machine-readable interfaces rather than requiring a human-dashboard-only path
- harness-agnostic access:
  the future lane must preserve CLI, file, and JSON access rather than one
  mandatory product wrapper
- agent-participant parity:
  bounded public participant flows must remain usable by digital agents without
  a human proxy controlling every step
- human-auditability co-preservation:
  stronger machine access must not destroy bounded human auditability
- bounded agent economic participation non-prohibition:
  the future lane must not structurally prohibit bounded agent participation in
  the public economic loop

These are derived opening-side gates informed by the AG logic-gates artifact.
This phase does not promote the full AG gate set into a universal
constitutional rule for every future lane.

## 3. Non-gates and still-later requirements

`legal_memo_not_formal_cdl_062_admissibility_gate`

The following are not formal opening gates in this artifact:
- the legal memo
- final substrate selection
- final privacy mechanism selection
- final row-7 closure
- final row-8 closure
- final row-9 closure

The legal memo remains real carry-forward and a later pre-RC or pre-launch
requirement. It is not used here as a formal admissibility gate.

## 4. Human authorization boundary

`explicit_human_go_required_for_any_future_cdl_062_opening`

Even if the opening-side gates are later met, `CDL-062` still requires explicit
human authorization before opening. This matrix removes ambiguity. It does not
remove the human decision boundary.

## 5. Distinction from final Option-B selection

Opening admissibility means:
- the sovereign substrate lane may begin
- the project has cleared enough constitutional blockers to research concrete
  backend families honestly

Final `Option B` selection means:
- the project chooses a concrete path after later substrate, privacy,
  censorship-resistance, independence, and maturity work is complete
- final `Option B` selection is therefore a later authorization boundary than
  `CDL-062` opening admissibility

Those are different decisions on purpose.
