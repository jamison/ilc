# ADR-0043: Review Lane T0.5 to T1+ Promotion

**Status:** Accepted
**Date:** 2026-05-21
**Phase:** 1414
**Author:** Jamison and Codex
**Dependencies:** ADR-0041, ADR-0040, CDL-091, Phase 1387a, Phase 1397/J-007, Phase 1398/J-008, Phase 1412, Phase 1413

`review_lane_wiring_adr_accepted_phase_1414`
`t0_5_to_t1_plus_admission_contract_defined_phase_1414`
`reviewer_payment_settlement_stub_contract_defined_phase_1414`
`review_lane_runtime_not_implemented_phase_1414`
`review_lane_wiring_not_complete_phase_1414`

---

## Context

J-003 defines `T0_5_PENDING_PUBLIC_INGESTION` as the quarantine state between a
private draft and admitted public graph material. T0.5 material is
content-addressed and requestable, but it has zero public weight and cannot
construct public economic events.

ADR-0041 defines permissionless Agent INIT, external-identifier anchoring, T0.5
raw artifact custody, and the rule that duplicate external IDs create
ATTESTATION edges to existing nodes instead of creating new nodes. ADR-0041
explicitly does not implement runtime lookup, registry service, or
deduplication enforcement.

Phase 1397/J-007 implemented a shadow ingestion harness. That harness exercises
T0.5 quarantine and task lifecycle in shadow mode only. J-008 records
`REVIEW_LANE_WIRING_COMPLETE` as a blocking `NOT_MET` condition because no
production T0.5 -> T1+ admission runtime, protocol-enforced dedup path, or
reviewer-payment settlement path exists.

Phase 1414 closes the design obligation for that lane. Runtime implementation
belongs to Phases 1415-1417.

## Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| ADR-0043 is the next ADR number | `docs/adr/` directory listing | confirmed: ADR-0042 is present and no ADR-0043 existed before this phase |
| T0.5 has zero public weight | `docs/specs/ilc_public_node_review_taxonomy_v0.1.md` | confirmed: `t0_5_pending_public_ingestion_has_zero_public_weight` |
| ADR-0041 defines dedup semantics but not enforcement | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` | confirmed: `external_identifier_anchoring_is_first_pass_dedup`; runtime lookup and dedup enforcement are out of scope |
| J-008 review lane wiring remains NOT_MET | `ilc_core/epistemic/jury_activation_gate.py` | confirmed: `REVIEW_LANE_WIRING_COMPLETE` is hardcoded `NOT_MET` |
| Reviewer payment remains default-off | `ilc_core/epistemic/jury_incentive_runtime.py` | confirmed: `REVIEWER_PAYMENT_NOT_ACTIVATED: bool = True` |

## Decision

ILC defines a default-off T0.5 -> T1+ review-lane admission contract. The
contract is pure evaluation until a later activation phase. It may produce a
quote, decision record, rejection reasons, and default-off payment-stub
instructions, but it must not write graph state, serve public HTTP, distribute
ECU, settle ILC, mutate wallets, or change J-008 gate status.

The Phase 1415 runtime target is:

```text
ilc_core/epistemic/review_lane_admission_runtime.py
```

The Phase 1415 version token must be:

```text
review_lane_admission_runtime_phase_1415.v0.1
```

The admission contract token defined here is:

```text
t0_5_to_t1_plus_admission_contract_defined_phase_1414
```

## Admission Contract

The review-lane runtime must evaluate an admission request with these logical
fields:

| Field | Rule |
|-------|------|
| `submission_id` | Stable non-empty identifier for the T0.5 submission. |
| `submission_content_hash` | Content hash for fallback dedup when no canonical external ID exists. |
| `current_taxonomy_class` | Must equal `T0_5_PENDING_PUBLIC_INGESTION`. |
| `target_taxonomy_class` | Must be T1 or higher. |
| `canonical_external_id` | Optional, but if present it is the primary dedup key. |
| `submitter_agent_id` | Stable non-empty agent ID. |
| `review_epoch` | Protocol epoch integer, not wall-clock time. |
| `review_lane` | Stable lane token such as `metadata`, `objective`, `contested`, `refutation`, or `provenance`. |
| `reviewer_attestations` | Externally supplied reviewer decisions from the assigned panel. |
| `dedup_lookup` | Read-only evidence about known canonical external IDs or known content hashes. |

Canonical public decision records that are serialized or hashed must use
`json.dumps(..., sort_keys=True, separators=(",", ":"), allow_nan=False)`.

## Gate Constants

Phase 1415 must implement these default constants unless a later ADR/CDL amends
them:

```python
REVIEW_LANE_PANEL_SIZE = 8
REVIEW_LANE_MIN_ASSIGNED_REVIEWERS = 5
REVIEW_LANE_APPROVAL_QUORUM = 5
REVIEW_LANE_OUTSIDER_REVIEWERS_REQUIRED_FOR_HIGH_VALUE = 1
REVIEW_LANE_PRODUCTION_NOT_ACTIVATED = True
```

Promotion to T1+ is admissible only when all of the following are true:

1. `current_taxonomy_class == "T0_5_PENDING_PUBLIC_INGESTION"`.
2. `target_taxonomy_class` is not T0 or T0.5.
3. At least `REVIEW_LANE_MIN_ASSIGNED_REVIEWERS` attestations are present from
   distinct reviewer agent IDs.
4. At least `REVIEW_LANE_APPROVAL_QUORUM` distinct reviewer attestations have
   verdict `approve`.
5. A high-value target lane includes at least
   `REVIEW_LANE_OUTSIDER_REVIEWERS_REQUIRED_FOR_HIGH_VALUE` approving outsider
   reviewer when an outsider seat was assigned.
6. Dedup enforcement returns `no_duplicate_found` or `attestation_to_existing`.
7. The Phase 1387a public-economics firewall is not bypassed. Admission may
   classify or promote; it does not itself construct an economic event.

Every denial must be visible through a stable reason token. Phase 1415 should
use tokens such as:

```text
review_lane_wrong_source_taxonomy
review_lane_invalid_target_taxonomy
review_lane_insufficient_reviewer_count
review_lane_approval_quorum_not_met
review_lane_outsider_approval_missing
review_lane_duplicate_external_id_attestation_required
review_lane_public_economics_firewall_required
review_lane_production_not_activated
```

## Dedup Enforcement Contract

Dedup enforcement follows ADR-0041:

1. If `canonical_external_id` is present, it is the primary dedup key.
2. If a known node with that external ID exists, the admission result must be
   `attestation_to_existing`, not `new_public_node`.
3. If `canonical_external_id` is absent, content hash fallback may be used.
4. Embedding similarity is not a Phase 1415/1416 dedup authority.
5. Dedup lookup must be read-only in Phases 1415-1417 unless a later phase
   explicitly authorizes graph or registry writes.

The Phase 1416 runtime may expose helper output fields:

```text
dedup_result
dedup_key_kind
dedup_key
existing_node_id
admission_action
```

`admission_action` must be either `promote_new_public_node`,
`attest_to_existing_node`, or `deny`.

## Reviewer-Payment Settlement Stub Contract

CDL-091 is ratified, and Phase 1401 exposes
`jury_incentive_runtime.queue_reviewer_payment_stub`. Review-lane wiring may
prepare default-off reviewer-payment instructions, but reviewer payment remains
inactive.

Phase 1416 may call or wrap:

```text
ilc_core.epistemic.jury_incentive_runtime.queue_reviewer_payment_stub
```

The payment-stub output must preserve:

```text
reviewer_payment_not_activated_phase_1401
```

The stub must report:

```text
payment_enqueued = False
ledger_write_authorized = False
treasury_write_authorized = False
wallet_write_authorized = False
ecu_distribution_authorized = False
```

No queued payment instruction is settlement authority.

## Integration Contract

Phase 1415 implements the admission evaluator. Phase 1416 wires dedup enforcement
and reviewer-payment settlement stubs. Phase 1417 adds integration tests and may
record `REVIEW_LANE_WIRING_COMPLETE` evidence for the review-lane track.

The Phase 1417 token may be:

```text
review_lane_wiring_complete_phase_1417
```

J-008 gate source must not be patched in Phase 1414. The static gate update is
reserved for Phase 1425 after all blocking tracks are re-verified.

## Rejected Alternatives

| Alternative | Disposition |
|-------------|-------------|
| Promote T0.5 material on schema validity alone | rejected: T0.5 entry is schema-only; T1+ promotion requires review-lane evidence |
| Use embedding similarity as primary dedup | rejected for this lane: ADR-0041 selects canonical external ID first and defers embedding dedup |
| Execute reviewer payment during admission | rejected: reviewer payment remains default-off and settlement authority is not granted here |
| Mark J-008 `REVIEW_LANE_WIRING_COMPLETE` in Phase 1414 | rejected: this ADR is design-only; runtime and integration tests are still pending |
| Allow T0.5 material to construct public economics before admission | rejected: Phase 1387a firewall applies |

## Non-Activation

`review_lane_runtime_not_implemented_phase_1414`
`review_lane_wiring_not_complete_phase_1414`

This ADR does not:

- create `ilc_core/epistemic/review_lane_admission_runtime.py`;
- modify `ingestion_shadow_harness.py`;
- modify `jury_assignment_runtime.py`;
- modify `jury_incentive_runtime.py`;
- implement dedup enforcement;
- implement reviewer-payment settlement;
- mark J-008 `REVIEW_LANE_WIRING_COMPLETE` as MET;
- activate public graph admission;
- activate production jury assignment;
- activate reviewer payment;
- distribute ECU;
- mutate ledger, treasury, wallet, graph, or CDL state.

## Consequences

Phase 1415 has a concrete runtime contract for default-off T0.5 -> T1+
admission evaluation. Phase 1416 has a bounded dedup and payment-stub contract.
Phase 1417 can test the complete review-lane wiring track without claiming
production activation or patching J-008.

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md -> adr/review_lane_t0_5_to_t1_promotion`.
