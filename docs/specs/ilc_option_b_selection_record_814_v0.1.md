# ILC Option B Selection Record 814 v0.1

**Status:** formal selection record
**Date:** 2026-04-23
**Phase:** 814
**Owner lane:** Codex main lane

`option_b_selected_by_human_authorization_2026_04_23`
`option_b_selection_record_delivered`
`adr_0028_posture_shifted_option_d_to_option_b`
`adr_0028_posture=option_b`

## 1. Authorization

Option B selection is recorded on the basis of explicit human authorization
given on 2026-04-23 in conversation.

The authorization token is:

`option_b_selected_by_human_authorization_2026_04_23`

## 2. Constitutional Basis

The constitutional basis for recording this selection is
`docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
as amended by the section:

`Amendment - Window 811-822 (2026-04-23)`

That amendment defines hard-closure rows and parallel-obligation rows and
explicitly permits Option B selection when hard-closure rows are satisfied and
parallel-obligation rows are human-acknowledged with named carry-forward work.

## 3. Checklist Basis

The governing checklist basis is:

- `docs/specs/ilc_option_b_graduation_checklist_state_813_v0.2.json`

Under that artifact:

- rows 1-4 are `runtime_closed`,
- row 5 is `parallel_obligation_acknowledged`,
- row 6 is `closed`,
- row 7 is `runtime_closed`,
- row 8 is `pass`,
- row 9 is `closed`.

## 4. Posture Shift

The formal posture shift recorded here is:

- `adr_0028_posture=option_b`

This means ILC now commits to the sovereign BFT consensus-substrate path
(Mysticeti) as the selected settlement-substrate direction.

## 5. What This Means

- settlement-path rotation wiring is now a live future implementation
  obligation,
- first non-Genesis validator deployment is schedulable in a later window but
  remains behind a separate explicit human gate,
- row 5 privacy work remains required before broader public RC claims,
- HIGH-002 remains a documented testnet limitation until separately addressed.

## 6. What This Does Not Mean

This record does not claim:

- live settlement-path rotation in this window,
- validator deployment in this window,
- production readiness,
- row-5 runtime closure,
- any CDL mutation.
