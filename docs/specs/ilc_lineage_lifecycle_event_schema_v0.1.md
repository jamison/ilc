# ILC Lineage Lifecycle Event Schema v0.1

Status: Locked (Phase 240)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the canonical lineage lifecycle event schema required for security runtime implementation entry.
This artifact specifies event shape, lifecycle states, and allowed versus disallowed state transitions.

This schema is an entry prerequisite for runtime work described in:
`docs/specs/ilc_security_runtime_implementation_plan_232_v0.1.md` Section 6.1.

## 2. Lifecycle states

The lineage lifecycle model uses four states:
- `active`
- `rotated`
- `revoked`
- `recovered`

## 3. Common event envelope

All lifecycle events use the following required envelope fields:
- `event_name`: one of `register`, `rotate`, `revoke`, `recover`
- `event_id`: deterministic unique event identifier
- `lineage_id`: canonical lineage identifier
- `subject_signer_id`: signer lineage subject
- `authorizer_signer_id`: signer asserting authority for the transition
- `event_ts`: UTC timestamp
- `reason_code`: deterministic reason token
- `prev_state`: prior lifecycle state
- `next_state`: resulting lifecycle state

## 4. Event definitions

### 4.1 register
- **Description**: initialize a lineage record in active state.
- **Required fields**: common envelope plus `root_anchor_id`.
- **Preconditions**:
  - lineage record for `lineage_id` does not already exist,
  - authorizer lineage is valid for registration authority.
- **Postconditions**:
  - lineage record exists,
  - lineage state is `active`,
  - append-only lifecycle log includes register event.

### 4.2 rotate
- **Description**: rotate from current active/recovered lineage state to rotated replacement context.
- **Required fields**: common envelope plus `replacement_signer_id`.
- **Preconditions**:
  - lineage record exists,
  - current lineage state is one of `active` or `recovered`,
  - replacement signer lineage is structurally valid.
- **Postconditions**:
  - lineage state becomes `rotated`,
  - replacement mapping is recorded,
  - append-only lifecycle log includes rotate event.

### 4.3 revoke
- **Description**: revoke lineage authority due to compromise, policy violation, or explicit governance action.
- **Required fields**: common envelope plus `revocation_scope`.
- **Preconditions**:
  - lineage record exists,
  - current lineage state is not already `revoked`.
- **Postconditions**:
  - lineage state becomes `revoked`,
  - canonical verification path rejects revoked lineage for authorization,
  - append-only lifecycle log includes revoke event.

### 4.4 recover
- **Description**: recover from revoked state to reinstated-operational context under replacement lineage controls.
- **Required fields**: common envelope plus `recovery_ticket_id` and `replacement_signer_id`.
- **Preconditions**:
  - lineage record exists,
  - current lineage state is `revoked`,
  - recovery ticket is present and valid under policy checks.
- **Postconditions**:
  - lineage state becomes `recovered`,
  - replacement lineage is active for future operations,
  - append-only lifecycle log includes recover event.

## 5. Allowed-transition table

| From state | To state | Trigger event | Rationale |
| --- | --- | --- | --- |
| `active` | `rotated` | `rotate` | Normal key rotation path. |
| `active` | `revoked` | `revoke` | Immediate compromise or policy breach action. |
| `rotated` | `revoked` | `revoke` | Rotated lineage can still be revoked if compromised. |
| `revoked` | `recovered` | `recover` | Explicit recovery operation from revoked state. |
| `recovered` | `rotated` | `rotate` | Post-recovery operational re-rotation path. |
| `recovered` | `revoked` | `revoke` | Re-compromise or policy breach after recovery. |

## 6. Disallowed-transition table

| From state | To state | Disallowed rationale |
| --- | --- | --- |
| `active` | `recovered` | Recovery without a prior revocation is invalid. |
| `rotated` | `active` | Direct return bypasses explicit recover/replace controls. |
| `rotated` | `recovered` | Recovery semantics require prior revoked state. |
| `revoked` | `active` | Cannot un-revoke directly; must use `recover`. |
| `revoked` | `rotated` | Rotating a revoked lineage is invalid without recovery. |
| `recovered` | `active` | Recovery already represents post-revocation operational state. |

Transition coverage note:
- Allowed and disallowed tables jointly cover all 12 ordered non-self state pairs.
- Any transition not listed as allowed is explicitly disallowed in this schema.

## 7. State machine summary

State set: `{active, rotated, revoked, recovered}`.

Allowed directed edges:
- `active -> rotated`
- `active -> revoked`
- `rotated -> revoked`
- `revoked -> recovered`
- `recovered -> rotated`
- `recovered -> revoked`

All other directed non-self edges are disallowed.

## 8. Non-goals and boundary

This schema intentionally does not define:
- cryptographic algorithms,
- key sizes,
- quorum values,
- governance thresholds.

Those choices require separate constitutional decision-log entries and are out of scope for this schema-lock phase.
