# ILC Public Init/Admission Contract Spec 614 v0.1

Status: locked
Date: 2026-04-13
Phase: 614
Owner lane: G8 MVP gate spec lane

`public_init_admission_contract_spec_614_locked`

## 1. Init/admission touchpoint target

Phase 614 locks the public init/admission touchpoint target for Window 613-619.
The touchpoint covers a bounded public init and admission flow tied to canonical
receipts rather than an open-ended onboarding or wallet-authority surface.

This contract is derived from the boundary locks in Phases 587-589 and
`ADR-0027`, which require canonical public legitimacy to flow through signed,
self-describing, machine-legible artifact lineage.

`init_flow_must_bind_to_canonical_receipt_lineage`.
`init_flow_is_spec_form_only_not_runtime`.
`spec_form_closure_necessary_but_not_sufficient_for_mvp_gate`.
`interface_runtime_form_required_window_623_plus`.
`broader_public_rc_claims_remain_blocked_until_spec_and_runtime_both_complete`.
`init_admission_does_not_open_agent_skills_lane`.

This Phase 614 packet is a spec-form artifact only. Interface/runtime form is deferred to Window 623+. Spec-form closure here is necessary but not sufficient for the full MVP gate. Broader public RC claims remain blocked until both spec and runtime forms complete.

## 2. Dependency and inherited canon

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_613_619_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/specs/ilc_window_414_423_handoff_423_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`

Inherited canon that remains binding in this spec:
- public activation requires more than local key existence
- canonical public participation requires a settled admission or stake binding
  receipt
- public identity and public namespace authority remain receipt-governed
  surfaces derived from canonical key lineage, not free-floating aliases
- public init/admission must stay compatible with the protocol-vs-harness split
  and may not silently widen wallet or payment authority
- the minimum participant-touch package must close in spec and runtime form
  before broader public RC claims may proceed

## 3. Public init flow boundary

The public init flow is limited to the minimal steps required to derive a
canonical public-participant candidate and request admission against the
canonical receipt boundary:
- canonical key derivation
- canonical key-derived `agent_id`
- preparation of a canonical activation/admission request envelope
- activation receipt request against the canonical admission authority surface

The init flow must remain compatible with the ADR-0026 protocol/harness split
and with ADR-0027 canonical lineage requirements. The init surface may expose a
machine-legible request contract, but it does not redefine protocol truth,
admission law, or settlement authority through product convenience.

The following are explicitly out of scope for the public init flow:
- wallet spend or transfer authority
- wallet withdrawal semantics
- chain-side admission
- permissionless admission
- payment runtime
- generalized signing authority beyond the bounded activation/admission request

Local key existence alone is not canonical public activation. A public init flow
is only complete when the participant is bound to canonical receipt lineage that
satisfies the admitted identity boundary.

## 4. Admission receipt contract

`admission_requires_settled_admission_or_stake_binding_receipt`.

The admission receipt is the minimum machine-legible public artifact that binds
the init/admission flow to canonical public authority. The minimum field set is:
- `artifact_kind`
- `schema_version`
- `receipt_id`
- `signer_agent_id`
- `authority_scope`
- `lineage_ref`
- `epoch_id`
- `issued_at`
- `verification_material_ref`
- `verification_status`

The admission authority source is the Phase 587 boundary lock plus
`CDL-040` admission scope: admission is an authority prerequisite and identity
envelope boundary, not claim acceptance, public legitimacy, or payout closure.

The receipt must bind to canonical signer-lineage and activation lineage, and
where stake binding is required the receipt chain must carry a stable reference
to the settled admission or stake binding surface rather than inferring it from
local operator state.

The admission receipt contract must remain compatible with the common receipt
representation discipline locked in Phase 586 and must preserve a canonical
`lineage_ref` slot for later linkage into quorum and settlement legitimacy
surfaces.

## 5. Namespace authority binding at admission

Namespace authority at admission must bind to admitted identity lineage rather
than floating free as a registry alias or operator label. The namespace
authority receipt is derivative of the key-derived `agent_id` rule and must not
replace it.

Namespace authority at admission therefore requires:
- reference to the admitted activation lineage
- preservation of the key-derived `agent_id` as canonical identity root
- compatibility with later settlement-linked legitimacy where continuity
  requires it

Display aliases remain derivative, not authoritative. A namespace receipt may
surface a public handle, but the authoritative binding remains the canonical
key-derived identity lineage governed by `CDL-042`, not the display alias
itself.

## 6. Forbidden interpretations and exclusions

`no_wallet_widening_at_init_admission`.
`init_admission_does_not_open_agent_skills_lane`.

The following interpretations are forbidden:
- treating local key existence as equivalent to canonical public activation
- treating the init/admission spec as widening wallet authority
- treating any non-equal-canon source as if it establishes init/admission law
- treating display aliases or operator labels as authoritative public identity
- opening Agent Skills or any new sub-lane through init/admission work
- treating this spec packet as runtime authorization, payment authorization, or
  broader public RC authorization

This phase does not widen wallet write, transfer, withdrawal, or spend
authority. It also does not authorize payment runtime, chain implementation, or
parallel planning lanes.

## 7. Explicit deferrals to later phases

The following items are explicitly deferred:
- interface/runtime implementation of the init/admission touchpoint to Window
  623+
- full stake and quorum linkage closure to later phases in the minimum
  participant-touch package
- wallet write, transfer, withdrawal, or spend semantics
- payment runtime and chain-side admission machinery
- any broader public RC claim until spec and runtime forms are both complete

Phase 614 closes only the spec-form init/admission contract. The runtime gate
remains later, and this document does not bypass the Phase 612 and Phase 613
carry-forward rule that the MVP gate is not satisfied until both forms are
complete.
