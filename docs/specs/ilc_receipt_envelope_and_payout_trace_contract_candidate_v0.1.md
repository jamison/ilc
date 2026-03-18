# ILC Receipt Envelope and Payout-Trace Contract Candidate v0.1

Status: Non-normative planning artifact — docs-only contract candidate
Date: 2026-03-18
Owner: GPT-5 Codex
Purpose: Provide a docs-only candidate contract for receipt envelopes and payout-trace lanes so
future economics and audit work can stay replayable, explainable, and identity-clean.

## 1. Scope boundary

This is not a final receipts schema and not a ratified payout contract.

It is a docs-only candidate built from:
- `docs/research/ilc_receipts_and_payout_traceability_draft_v0.1.md`
- `docs/research/ilc_node_importance_vs_host_service_accounting_memo_v0.1.md`
- `docs/research/ilc_host_admission_and_dependency_serviceability_memo_v0.1.md`
- `docs/research/ilc_dependency_closure_preservation_architecture_memo_v0.1.md`

Its purpose is to reserve the accounting lanes early enough that later runtime or governance work
does not blur:
- node usefulness,
- host service,
- allocations,
- and challenge outcomes.

## 2. Why this candidate now

The receipts/payout problem is now structurally important for three reasons:

- dependency-closure economics implies value may flow upstream across required graph relations
- host-serviceability economics implies service receipts and challenge outcomes matter independently
  of node-level usefulness
- future governance review will need to understand why value moved, not just where it landed

Without a candidate contract here, later work is likely to default to:
- flat payout rows,
- mixed node/host semantics,
- unclear allocation causes,
- and hard-to-audit economic traces.

## 3. Core contract principles

### 3.1 Node-side and host-side evidence must remain distinct

The contract should not allow:
- host-local request traffic
to masquerade as:
- intrinsic node usefulness.

The receipt model must preserve distinct lanes for:
- node-level evidence
- host-level service evidence

### 3.2 One productive event may generate several trace records

The contract should assume:
- one productive event can justify several accounting traces

For example:
- node usefulness update
- host service receipt
- upstream dependency allocation
- steward allocation
- challenge bounty

This means a single flat payout row is not a sufficient mental model.

### 3.3 Trace records should key off canonical identities

Wherever possible:
- node-side traces should key off canonical node IDs
- host-side traces should key off host identities
- allocations should reference the source event and destination identity explicitly

This is how the contract remains replayable and auditable.

### 3.4 The envelope should explain why value moved

Every later trace record should be able to answer:
- what happened?
- which rule family applied?
- which identity was affected?
- what evidence justified it?

If the envelope cannot answer those questions, it is too thin.

## 4. Candidate receipt lanes

The candidate contract should preserve at least four lanes.

### Lane A: Node usefulness evidence

Purpose:
- record accepted evidence that a canonical node contributed to productive graph value

Key identity:
- `node_id`

Typical examples:
- productive downstream dependence
- accepted reuse evidence
- accepted importance updates

### Lane B: Host service evidence

Purpose:
- record that a specific host or steward served, resolved, or proved availability for a node or
  dependency closure

Key identity:
- `host_id`

Typical examples:
- service success
- dependency-complete resolution success
- availability proof success

### Lane C: Allocation trace

Purpose:
- explain how value from a source event was redistributed across recipients or pools

Key identities:
- `source_event_id`
- `beneficiary_id`
- optionally `node_id` or `host_id`

Typical examples:
- founder allocation
- steward allocation
- upstream dependency allocation
- protocol pool allocation

### Lane D: Challenge/audit outcome

Purpose:
- capture the economic effect of a challenge, docking event, repair-window outcome, or bounty

Key identities:
- `challenged_identity`
- `challenger_identity`
- `subject_ref`

Typical examples:
- failed serviceability claim
- successful challenge bounty
- repair-window success with no slash
- repeated failure downgrade

## 5. Candidate minimum envelope fields

The exact eventual schema can differ, but a usable candidate envelope likely needs:

- `receipt_id`
- `receipt_type`
- `event_epoch`
- `source_event_id`
- `node_id` where applicable
- `host_id` where applicable
- `beneficiary_id`
- `allocation_class`
- `amount`
- `unit`
- `evidence_ref`
- `rule_ref`
- `status`

These are enough to support:
- replayability,
- attribution,
- and review of why funds moved.

## 6. Candidate receipt-type families

Recommended candidate `receipt_type` families:

- `node_usefulness`
- `host_service`
- `dependency_allocation`
- `founder_allocation`
- `steward_allocation`
- `challenge_submission`
- `challenge_outcome`
- `protocol_reallocation`

This list can grow later, but it is a useful docs-only baseline now.

## 7. Candidate allocation classes

Recommended high-level `allocation_class` values:

- `founder_reward`
- `steward_reward`
- `host_service_reward`
- `upstream_dependency_reward`
- `challenge_bounty`
- `protocol_pool`
- `repair_compensation`
- `docked_amount`

The point is not to finalize formulas.

The point is to make future traces explainable.

## 8. Example event decomposition

Suppose:
- node `M1` produces accepted value
- `M1` depends on `O7` and `A3`
- host `H2` served `M1` and resolved the closure

The candidate contract should allow records like:

- one `node_usefulness` receipt for `M1`
- one `host_service` receipt for `H2`
- one `dependency_allocation` record for `O7`
- one `dependency_allocation` record for `A3`
- one `founder_allocation` record if founder economics apply
- one `steward_allocation` record if stewardship economics apply

This example is the reason the candidate contract should not assume one event equals one payout row.

## 9. Relationship to host-serviceability

This candidate contract is intentionally compatible with the host-serviceability model.

If hosts later advertise nodes as serviceable, the contract must support traces for:
- serviceability success
- dependency-resolution success
- failed serviceability challenge
- repair-window success or failure

Without that lane, later host economics will be hard to audit.

## 10. Relationship to node importance

This candidate contract is also intentionally compatible with the node-importance model.

Node-level value should be supported by:
- node-usefulness receipts keyed to canonical node IDs

Host-local traffic or service should be supported by:
- host-service receipts keyed to host IDs

That distinction should be treated as a design invariant.

## 11. Recommended next use of this candidate

This candidate should be used as:
- a docs-only baseline for later receipts schema work
- an anti-refactor anchor for accounting discussions
- a review target for payout-trace terminology

It should not be used as:
- the final runtime schema
- a final payout formula
- or a substitute for later constitutional/economic ratification

## 12. Bottom line

The project now has enough clarity to justify a docs-only receipt envelope candidate.

The minimum viable candidate is:
- four lanes,
- explicit receipt types,
- explicit allocation classes,
- and envelope fields keyed to the right identities.

That is enough to make the next economics/audit discussions more planned and more auditable.
