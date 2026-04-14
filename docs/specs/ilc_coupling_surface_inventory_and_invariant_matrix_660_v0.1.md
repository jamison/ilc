# ILC Coupling Surface Inventory And Invariant Matrix 660 v0.1

Status: constitutional prelock evidence artifact
Date: 2026-04-14
Phase: 660
Owner lane: G8 coupling-invariants governance lock

## 1. Purpose and practical definitions

This artifact turns the row-6 coupling question into an explicit inventory and
matrix.

`coupling_surface_inventory_660_primary_artifact`
`upstream_means_source_of_canonical_legitimacy_or_authority`
`downstream_means_record_order_anchor_finalize_or_settle_only`
`backend_may_not_author_protocol_legitimacy`
`admission_namespace_quorum_settlement_reputation_surfaces_in_scope`
`machine_legible_matrix_required_for_later_windows`

Practical definitions used here:
- upstream means the source of canonical legitimacy or authority
- downstream means a later backend may record, order, anchor, finalize, or
  settle already-legitimate state only
- backend means a later sovereign settlement substrate family that may be
  opened later by `CDL-062`

The point of the matrix is to show, surface by surface, which layer is allowed
to authorize legitimacy and which later actions remain permitted without
allowing the backend to manufacture that legitimacy.

## 2. Coupling surface inventory

The minimum in-scope public legitimacy surfaces are:

| Surface | Practical meaning | Why it is upstream |
|---|---|---|
| Public admission legitimacy | Who is admitted into the public protocol participant set | Admission is a protocol act, not a later settlement artifact |
| Canonical namespace / handle authority | Which public names and handles are recognized as canonical | Namespace legitimacy must follow protocol-side authority and lineage |
| Quorum / panel / evaluation authority | Which protocol-side evaluators or panels count as legitimate | Evaluation legitimacy is a protocol/governance question, not a backend question |
| Public settlement legitimacy | Whether a public settlement state is recognized as legitimate by the protocol | Settlement receipts must remain grounded in protocol receipts and lineage |
| Public reputation continuity | Whether reputation carries forward as the same public participant | Reputation continuity depends on protocol admission and receipt lineage |
| Public receipt lineage | The trace path that connects admission, settlement, and continuity | Without lineage, later inheritance claims become counterfeit |

## 3. Invariant matrix

The machine-readable companion artifact is
`docs/specs/ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1.json`.

### Surface 1: Public admission legitimacy

- upstream authority: protocol-side admission and canonical receipt issuance
- downstream allowed actions: record admission-linked state, anchor receipts,
  settle already-admitted activity
- forbidden backend actions: create admission legitimacy on its own, retroadmit
  actors without protocol lineage, override protocol-side rejection
- required lineage or receipt basis: public init/admission receipts and linked
  participant identity lineage

### Surface 2: Canonical namespace / handle authority

- upstream authority: protocol-side namespace authority and linked identity
  lineage
- downstream allowed actions: mirror or settle already-canonical namespace
  assignments, anchor namespace-linked receipts
- forbidden backend actions: mint canonical handles independently, remap names
  around protocol authority, inherit namespace without lineage
- required lineage or receipt basis: admission-linked identity lineage and
  protocol receipts that bind namespace state

### Surface 3: Quorum / panel / evaluation authority

- upstream authority: protocol governance and evaluation authority defined by
  protocol-side legitimacy
- downstream allowed actions: record already-legitimate panel outcomes, anchor
  signed evaluation artifacts, settle protocol-approved results
- forbidden backend actions: appoint canonical evaluators on its own, override
  which panel is legitimate, convert backend ordering into evaluation authority
- required lineage or receipt basis: protocol-side evaluation lineage and
  canonical receipt paths for governed outcomes

### Surface 4: Public settlement legitimacy

- upstream authority: protocol-side receipt chain and lifecycle legitimacy
- downstream allowed actions: carry settlement-linked receipts forward, order
  and finalize already-legitimate settlement state, provide later durability
- forbidden backend actions: declare settlement legitimate without protocol
  receipt basis, rewrite settlement legitimacy by backend fiat, bypass delayed
  visible ILC ordering
- required lineage or receipt basis: lifecycle receipts, settlement-linked
  receipts, and protocol-side sequencing

### Surface 5: Public reputation continuity

- upstream authority: protocol identity continuity and receipt-linked public
  history
- downstream allowed actions: store already-legitimate reputation-linked state,
  settle effects tied to the canonical participant lineage
- forbidden backend actions: clone reputation onto a forked lineage, inherit
  reputation without protocol receipt continuity, reset continuity by backend
  rewrite
- required lineage or receipt basis: admission lineage plus linked settlement
  and public receipt history

### Surface 6: Public receipt lineage

- upstream authority: canonical public receipt issuance and protocol-side trace
  linkage
- downstream allowed actions: store, order, anchor, and verify already-issued
  receipts
- forbidden backend actions: fabricate lineage roots, backfill missing receipt
  history by fiat, substitute foreign receipts as canonical origin
- required lineage or receipt basis: canonical receipt identifiers and linked
  protocol issuance surfaces

## 4. Allowed downstream actions

Across all surfaces, later backend choice is allowed to:
- record already-legitimate protocol state
- order already-legitimate protocol state
- anchor already-legitimate protocol state
- finalize already-legitimate protocol state
- settle already-legitimate protocol state
- carry receipt-linked settlement state forward

These are downstream service functions. They are important, but they are not
the same thing as authoring canonical legitimacy.

## 5. Forbidden backend actions

Across all surfaces, later backend choice is forbidden from:
- creating admission legitimacy on its own
- creating canonical namespace authority on its own
- creating evaluator or quorum legitimacy on its own
- declaring public settlement legitimate without protocol receipt basis
- inheriting public reputation without protocol lineage
- fabricating or replacing public receipt lineage roots

These prohibitions are what make the row-6 governance lock practical rather
than decorative.

## 6. Evidence basis and unresolved edges

Primary evidence basis:
- `docs/specs/ilc_ecu_ilc_lifecycle_runtime_652_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_window_649_654_handoff_654_v0.1.md`

Unresolved edges carried to Phase 661:
- how aggressively to word the external constitutional-center failure cases
- which later row-7 and row-8 criteria should be named as explicit exclusion
  criteria instead of softer carry-forward phrasing
- how the row-9 transport/discovery lane should later prove the backend cannot
  smuggle heavy-payload legitimacy through a bounded metadata path
