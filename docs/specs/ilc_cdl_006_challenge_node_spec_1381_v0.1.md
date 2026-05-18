# ILC CDL-006 Challenge Node Spec 1381 v0.1

Status: Phase 1381 spec and runtime stub committed
Date: 2026-05-18
Decision: CDL-006
Ratified source: Phase 993 governance conflict-set closure
Runtime status: stub only; production implementation deferred to Phase 1382

```text
cdl_006_challenge_node_spec_phase_1381
cdl_006_challenge_node_runtime_stub_phase_1381
cdl_006_multi_body_3_body_quorum_spec_committed
```

## 1. Purpose

CDL-006 ratified the governance override and challenge process as
`multi-body checks`. Phase 1381 records the challenge node contract needed by
Phase 1382: the challenge record schema, the 3-body quorum logic, and the
audit-path writer format.

This document is not a production runtime activation. It does not mutate the
CDL register, execute a governance override, finalize a challenge, or write
graph records. The corresponding runtime file is a schema/signature stub only:
`ilc_core/governance/challenge_node_runtime.py`.

## 2. Source Authority

| Source | Finding |
| --- | --- |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` line 34 | `CDL-006` is ratified and selected `multi-body checks`; `single-body` and `dual-body` were not selected. |
| `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md` | Phase 993 records `CDL-006` selected option as `multi-body checks`. |
| `docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md` | Existing CDL-V3/CDL-045 surfaces partially express quorum concepts, but the challenge node spec and formal audit path were not built before Phase 1381. |
| `docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md` | Phase 1381 owns spec plus stub; Phase 1382 owns production runtime and tests. |

## 3. Terminology

| Term | Meaning |
| --- | --- |
| challenge node | A governance challenge record object, not a serving peer or host process. |
| body | One independent review body participating in the CDL-006 challenge process. |
| 3-body quorum | The ratified Phase 1381 interpretation of CDL-006 multi-body checks: three independent body roles must each contribute a valid attestation. |
| audit path | A hash-linked sequence of challenge proceeding entries that can be committed to the graph. |
| stub | Schema definitions and fixed function signatures without production verification or writing logic. |

## 4. Challenge Record Schema

Every challenge record MUST contain these fields:

| Field | Type | Required semantics |
| --- | --- | --- |
| `schema_version` | string | Must identify the Phase 1381 challenge-node schema family. |
| `challenge_id` | string | Content-addressable or hash-derived challenge identifier. |
| `creator_agent_id` | string | Agent that authored the challenge record. |
| `challenged_action_ref` | string | CID or hash reference for the action, decision, artifact, or runtime event being challenged. |
| `governance_basis_ref` | string | Reference to the CDL/ADR/spec basis for the challenge. |
| `remedy_requested` | string | Requested governance remedy, such as suspend, reopen, reject, ratify, or route to later review. |
| `evidence_refs` | array of strings | Hash/CID references to evidence artifacts. |
| `body_attestations` | array of body attestation records | Must include one valid attestation for each required independent body role before quorum can pass. |
| `audit_path_ref` | string | Reference to the current audit-path head or genesis audit-path entry for the challenge proceeding. |
| `created_epoch` | integer | Protocol epoch for record creation; wall-clock time is not authoritative. |
| `status` | string | One of proposed, under_review, quorum_met, rejected, superseded, or deferred. |

The Phase 1381 runtime stub exposes this field list through
`challenge_record_schema()` and `ChallengeRecordSchema`.

## 5. Body Attestation Schema

Every body attestation MUST contain these fields:

| Field | Type | Required semantics |
| --- | --- | --- |
| `body_id` | string | Stable identifier for the independent review body. |
| `body_role` | string | One of `constitutional`, `technical`, or `affected_party`. |
| `signer_agent_id` | string | Agent signing for the body in this proceeding. |
| `verdict` | string | One of `approve_challenge`, `reject_challenge`, or `abstain`. |
| `attestation_ref` | string | Hash/CID reference for the attestation payload. |
| `signature_ref` | string | Hash/CID reference for the signature or signature envelope. |
| `epoch` | integer | Protocol epoch for the attestation. |

The Phase 1381 runtime stub exposes this field list through
`challenge_body_attestation_schema()` and `ChallengeBodyAttestation`.

## 6. Multi-Body 3-Body Quorum Logic

CDL-006 selected `multi-body checks`. For this spec, Phase 1381 fixes the
minimum 3-body quorum contract that Phase 1382 must implement:

| Requirement | Contract |
| --- | --- |
| Required body count | Exactly three independent body roles are required for quorum eligibility. |
| Required body roles | `constitutional`, `technical`, and `affected_party`. |
| Single-body path | Forbidden. A single attesting body cannot pass quorum. |
| Dual-body path | Forbidden. Any two-body subset cannot pass quorum. |
| Duplicate-role path | Forbidden. Multiple attestations from the same body role cannot substitute for a missing role. |
| Consensus requirement | A challenge passes only when all three required body roles have valid affirmative challenge attestations under the Phase 1382 production verifier. |
| Abstain handling | Abstain is a recorded attestation verdict but does not satisfy affirmative challenge consensus. |

Phase 1381 does not implement verification. The stub function
`verify_challenge_quorum(challenge_record, *, required_body_roles=REQUIRED_CHALLENGE_BODIES)`
exists only to freeze the Phase 1382 signature and fails closed with:

```text
cdl_006_challenge_node_production_runtime_deferred_to_phase_1382
```

## 7. Audit Path Writer Specification

Every audit-path entry MUST contain these fields:

| Field | Type | Required semantics |
| --- | --- | --- |
| `audit_entry_id` | string | Content-addressable or hash-derived audit entry identifier. |
| `challenge_id` | string | Challenge record to which the audit entry belongs. |
| `previous_entry_ref` | string or null | Hash/CID reference for the previous audit entry; null only for the first entry. |
| `entry_type` | string | Event class, such as opened, evidence_added, body_attested, quorum_evaluated, or closed. |
| `payload_ref` | string | Hash/CID reference for the event payload. |
| `writer_agent_id` | string | Agent writing the audit entry. |
| `entry_epoch` | integer | Protocol epoch for the audit entry. |

The production audit-path writer in Phase 1382 must create deterministic,
hash-linked entries and must commit the resulting head reference back into the
challenge record or graph commitment path. Phase 1381 only freezes the function
signature:

```python
write_challenge_audit_path_record(
    challenge_record: Mapping[str, Any],
    audit_event: Mapping[str, Any],
    *,
    previous_entry_ref: str | None = None,
) -> dict[str, Any]
```

The stub fails closed with:

```text
cdl_006_challenge_node_production_runtime_deferred_to_phase_1382
```

## 8. Runtime Stub Surface

Phase 1381 adds `ilc_core/governance/challenge_node_runtime.py` with:

| Symbol | Purpose |
| --- | --- |
| `ChallengeRecordSchema` | Frozen dataclass describing the challenge record schema carrier. |
| `ChallengeBodyAttestation` | Frozen dataclass describing one body attestation schema carrier. |
| `AuditPathEntry` | Frozen dataclass describing one audit-path entry schema carrier. |
| `challenge_record_schema()` | Returns the challenge record field contract. |
| `challenge_body_attestation_schema()` | Returns the body attestation field contract. |
| `audit_path_record_schema()` | Returns the audit-path entry field contract. |
| `build_challenge_record_schema_template()` | Returns all three schema contracts in one template for Phase 1382. |
| `canonical_schema_template_json()` | Returns deterministic JSON for the schema template. |
| `verify_challenge_quorum()` | Phase 1382 production stub; fails closed in Phase 1381. |
| `write_challenge_audit_path_record()` | Phase 1382 production stub; fails closed in Phase 1381. |

The file is marked:

```text
PUBLIC_RC_EXCLUDE: cdl_006_challenge_node_runtime_stub_phase_1381
```

## 9. Non-Claims

Phase 1381 does not implement production quorum verification, write audit-path
records, activate challenge processing, open or mutate any CDL, execute
governance decisions, activate public serving, activate public claimability,
activate wallet/ECU/ILC value paths, publish a public RC, sign release
artifacts, approve counsel/legal conclusions, or claim CDL-006 runtime
completion.

## 10. Phase 1382 Carry-Forward

Phase 1382 must replace the fail-closed stubs with production behavior:

| Function | Phase 1382 obligation |
| --- | --- |
| `verify_challenge_quorum()` | Enforce schema validity, independent body-role membership, signature/attestation references, and all-three affirmative consensus. |
| `write_challenge_audit_path_record()` | Emit deterministic hash-linked audit-path entries and update the graph commitment path according to the Phase 1381 schema. |

Phase 1382 must preserve the 3-body-only constraint and must not add
single-body or dual-body challenge completion paths.
