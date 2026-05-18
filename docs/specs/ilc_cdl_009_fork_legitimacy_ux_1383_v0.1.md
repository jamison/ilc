# ILC CDL-009 Fork Legitimacy UX 1383 v0.1

Status: committed
Phase: 1383
Date: 2026-05-18

`cdl_009_fork_legitimacy_ux_phase_1383.v0.1`
`cdl_009_signature_badge_schema_implemented`
`cdl_009_eligibility_rules_contract_committed`

## 1. Purpose

This document defines the Phase 1383 CDL-009 fork-legitimacy operator UX
surface. CDL-009 was ratified in Phase 993 with selected option
`signature-badge+eligibility rules`; the rejected alternatives were
`naming-only` and bare `signature-badge`.

Phase 1383 supplies the missing schema and local inspection runtime. It does not
open, mutate, or ratify any CDL. It does not activate public serving, write graph
state, execute governance decisions, or create a public fork-legitimacy API.

## 2. Ratified Basis

The decision-log row for CDL-009 is:

```text
| CDL-009 | CDP-009 | Fork legitimacy/user signaling | ratified | naming-only, signature-badge, signature-badge+eligibility rules | signature-badge+eligibility rules | client UX + policy docs |
```

The Phase 993 scoped ratification record also states:

```text
CDL-009: selected signature-badge+eligibility rules
```

The Phase 590 fork boundary remains binding:

```text
cdl_009_fork_signaling_cannot_override_canonical_lineage
```

Fork signaling, badges, and eligibility markers are derivative of canonical
lineage. They cannot override the canonical-vs-fork consequence.

## 3. Signature-Badge Schema

Schema version:

```text
cdl_009_fork_legitimacy_badge_v1
```

Required fields:

| Field | Meaning |
|---|---|
| `badge_id` | Stable identifier for the badge artifact. |
| `badge_schema_version` | Must be `cdl_009_fork_legitimacy_badge_v1`. |
| `fork_id` | Operator-visible fork identifier. |
| `fork_root_ref` | Content or state root reference for the fork being inspected. |
| `canonical_genesis_root_hash` | ADR-0037 signed Genesis v0.1 root envelope hash. |
| `lineage_proof_ref` | Reference to the canonical Genesis lineage proof bundle. |
| `authority_scope` | Must be `fork_legitimacy` or `canonical_lineage_fork_legitimacy`. |
| `signer_authority` | Must be `genesis_authority` or `authorized_successor_governance`. |
| `signature_algorithm` | Must be one of the allowed signature algorithm labels. |
| `signature_ref` | Reference to the signature or signature verification artifact. |
| `signature_verification_status` | Must be `verified` for eligibility to pass. |
| `issued_epoch` | Non-negative protocol epoch for the badge issuance record. |
| `evidence_refs` | Non-empty references supporting the badge. |

The Phase 1383 runtime validates this schema structurally. Cryptographic
signature verification remains delegated to the canonical signature verification
path that produced `signature_verification_status=verified`.

## 4. Eligibility Rules Contract

Rule version:

```text
cdl_009_eligibility_rules_v1
```

Required evidence fields:

| Field | Required value or role |
|---|---|
| `eligibility_rule_version` | Must be `cdl_009_eligibility_rules_v1`. |
| `fork_root_ref` | Must match the signal and badge fork root reference. |
| `canonical_genesis_root_hash` | Must match the ADR-0037 signed Genesis v0.1 root envelope hash. |
| `lineage_proof_ref` | Must match the badge lineage proof reference. |
| `public_identity_lineage_ref` | Reference to public identity lineage continuity evidence. |
| `public_quorum_lineage_ref` | Reference to public quorum lineage continuity evidence. |
| `settlement_lineage_ref` | Reference to settlement lineage continuity evidence. |
| `canonical_genesis_lineage` | Must be `true`. |
| `public_legitimacy_chain` | Must be `true`. |
| `no_stripped_public_legitimacy_chain` | Must be `true`. |
| `not_naming_only` | Must be `true`. |

Eligibility passes only when a verified signature badge and the eligibility
evidence satisfy the same canonical fork root, Genesis root, and lineage proof.
Naming-only signaling fails closed. Bare signature-badge signaling fails closed.
A stripped public-legitimacy chain fails closed.

## 5. Operator Inspection Surface

Runtime:

```text
ilc_core/governance/fork_legitimacy_runtime.py
```

Primary local functions:

| Function | Purpose |
|---|---|
| `signature_badge_schema()` | Return the badge schema contract. |
| `eligibility_rules_contract()` | Return the eligibility rules contract. |
| `fork_signal_schema()` | Return the combined fork-signal inspection schema. |
| `validate_signature_badge()` | Validate and normalize a signature badge. |
| `validate_eligibility_evidence()` | Validate and normalize eligibility evidence. |
| `validate_fork_signal()` | Validate and normalize the combined fork signal. |
| `inspect_fork_signal()` | Return a deterministic operator eligibility decision. |

CLI/operator invocation:

```bash
python3 -m ilc_core.governance.fork_legitimacy_runtime <fork_signal.json>
```

The CLI reads a local JSON file and emits a deterministic JSON decision. It
returns exit code `0` for eligible and `1` for not eligible. It does not listen
on a socket, bind an HTTP route, write graph state, or publish the result.

## 6. Inspection Result

Result schema version:

```text
cdl_009_fork_signal_inspection_result_v1
```

Result fields:

| Field | Meaning |
|---|---|
| `schema_version` | Result schema version. |
| `fork_id` | Inspected fork identifier. |
| `fork_root_ref` | Inspected fork root reference. |
| `badge_ref` | Deterministic SHA-256 reference for the normalized badge. |
| `eligible_for_legitimacy_badge` | Boolean eligibility result. |
| `decision` | `eligible` or `not_eligible`. |
| `failed_rules` | Stable fail-closed rule tokens. |
| `operator_surface` | Always `cli_local_only_no_public_api`. |
| `public_api_activation` | Always `false`. |
| `runtime_token` | `cdl_009_fork_legitimacy_ux_phase_1383.v0.1`. |
| `tokens` | Phase 1383 completion tokens. |

## 7. Explicit Non-Activation

Phase 1383 does not authorize:

- CDL register mutation,
- public fork-legitimacy API activation,
- public serving,
- graph state writes,
- governance decision execution,
- public claimability,
- wallet/ECU/ILC value-path activation,
- release signing,
- public RC publication.

The runtime helper is marked `PUBLIC_RC_EXCLUDE` and requires later explicit
review before any public package inclusion.
