# ILC Coupling Invariants Governance Lock 663 v0.1

Status: ratified governance-lock artifact
Date: 2026-04-14
Decision vehicle: CDL-065
Phase: 663

## 1. Decision target and locked rule

`cdl_065_ratified_coupling_invariants_governance_lock`
`backend_may_carry_legitimacy_not_author_it`
`protocol_truth_and_public_legitimacy_remain_upstream_of_backend_choice`

Locked rule:
- a later backend may carry, order, anchor, finalize, or settle already
  legitimate protocol state
- a later backend may not author, override, or inherit protocol legitimacy on
  its own

This is a rule about legitimacy authorship, not a rule against later settlement
backends existing.

## 2. In-scope legitimacy surfaces

The in-scope surfaces are:
- public admission legitimacy
- canonical namespace and handle authority
- quorum, panel, and evaluation authority
- public settlement legitimacy
- public reputation continuity
- public receipt lineage

`namespace_quorum_settlement_and_reputation_require_protocol_lineage`

These surfaces remain upstream because the protocol layer is the place where
their legitimacy is constituted and traced.

## 3. Allowed downstream backend actions

Allowed downstream backend actions are:
- record already-legitimate protocol state
- order already-legitimate protocol state
- anchor already-legitimate protocol state
- finalize already-legitimate protocol state
- settle already-legitimate protocol state
- provide later durability for receipt-linked public state

These actions are downstream services. They do not convert a later backend into
the source of public legitimacy.

## 4. Forbidden backend actions

Forbidden backend actions are:
- create admission legitimacy without protocol authorization
- mint canonical namespace authority without protocol lineage
- appoint canonical evaluators or quorums on backend authority alone
- declare public settlement legitimate without protocol receipt basis
- inherit public reputation continuity without protocol lineage
- fabricate or replace public receipt lineage roots

## 5. Lineage and receipt implications

Lineage is the practical boundary that keeps carry-forward from becoming
counterfeit inheritance.

The backend may carry forward:
- receipt-linked settlement state
- anchored public history
- later durability for canonical public artifacts

The backend may not use later carrying as a substitute for:
- admission lineage
- namespace lineage
- evaluation legitimacy
- settlement legitimacy
- reputation continuity

## 6. What this ratification does not decide

`rows_5_and_7_through_9_not_closed_by_cdl_065`
`cdl_062_remains_unopened_after_cdl_065_ratification`

This ratification does not decide:
- `CDL-062` opening
- final `Option B` selection
- row 5 privacy mechanism closure
- row 7 censorship-resistance closure
- row 8 independence closure
- row 9 maturity closure
- substrate family choice or BFT choice
