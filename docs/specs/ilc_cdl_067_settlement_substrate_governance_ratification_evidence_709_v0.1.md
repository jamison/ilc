# ILC CDL-067 Settlement Substrate Governance Ratification Evidence 709 v0.1

Status: ratification evidence artifact
Date: 2026-04-17
Decision vehicle: CDL-067
Phase: 709

`cdl_067_ratified_narrow_settlement_state_governance_vehicle`
`settlement_state_scope_is_constitutional_surface`
`backend_carries_already_legitimate_protocol_state_only`
`epoch_boundary_submission_surface_is_ratified_narrowly`
`cdl_067_does_not_freeze_backend_schema_or_select_option_b`

## 1. Evidence basis

CDL-067 ratification rests on four already-published anchors:

- the Phase 612 settlement-substrate closure artifact that preserved the
  deferred-substrate route and MVP gate
- the Phase 687 settlement-state enumeration and submission model
- the Phase 696 opening stub that fixed the constitutional question narrowly
- the already-ratified CDL-065 upstream legitimacy boundary

This gives enough evidence to ratify the narrow governance vehicle without
freezing every future backend detail.

## 2. Ratified settlement-state rule

The ratified rule is:

- settlement-state scope is a constitutional surface, not backend convenience
- a later backend may carry, anchor, finalize, or settle already-legitimate
  protocol state only
- the canonical constitutional submission surface is the epoch-boundary
  settlement record class opened in Phase 687 / Phase 696
- later backend work must remain bounded to this downstream settlement-state
  surface unless an explicit amendment changes it

This ratifies the governance vehicle for settlement-state scope. It does not ratify a specific sovereign substrate family. It does not ratify a specific sovereign substrate family as the final backend choice for ILC.

## 3. Carried state versus off-chain preserved state

The carried durable settlement-state categories are:

- epoch-boundary commit records
- public node-linkage graph anchors
- namespace and schema registry events
- sparse economic and governance events
- genesis lineage anchor material

The explicitly off-chain preserved categories remain:

- raw claim and evidence payloads
- private or gated shard content
- per-agent detailed ECU balance ledgers
- raw panel deliberation records

This preserves row-5 compatibility and the CDL-065 rule that the backend carries
already-legitimate state rather than authoring legitimacy itself.

## 4. Preserved exclusions and backend non-goals

CDL-067 ratification does not authorize:

- final Option B selection
- final substrate-family selection
- full backend-schema freeze
- final serialization or wire-format lock for every field
- row-5, row-7, or row-8 runtime closure

It also preserves the Phase 612 posture:

- `Option D` remains the active near-term posture
- `Option B` remains later-selectable only via its published graduation path
- the MVP gate still constrains later sovereign substrate execution

## 5. Decision-log consequence

Because the settlement-state scope is now sufficiently bounded by the
enumeration, the opening stub, and the inherited legitimacy boundary, the Phase
709 decision-log mutation is:

- `CDL-067` changes from `open` to `ratified`
- its evidence document becomes this artifact
- `CDL-017` remains open after this phase
