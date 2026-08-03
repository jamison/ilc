# ILC Agent-Native Value-Action Intent Taxonomy
Version: v0.1
Phase: GAP-VALUE-ACTION-00
Date: 2026-08-03
Status: ratified-spec-candidate (non-activating)
Depends-on: wallet_rc_gate_verdict_committed_phase_1578h
            agent_native_harness_ontology_spec_committed_GAP_AGENT_HARNESS_00
Supersedes: Phase 1579a (GAP-WALLET-04) - post-RC stub, not executed
Governs: value-action intent type taxonomy, field schemas, Decimal requirement,
         nonce semantics, domain separator, double-entry conservation requirement,
         CDL governance decision, activation path
Authority: ilc_wallet_lane_forward_plan_pre_rc_v0.1.md,
           ADR-0026 (protocol/harness boundary),
           agent_native_harness_ontology_and_boundary_spec_GAP_AGENT_HARNESS_00_v0.1.md
Does NOT activate: transfer, spend, withdrawal, any wallet guard, or the broad
                   transfer-enabled RC GO phrase

## §1 - Value-Action Ontology

Value-action is not the same object as a wallet. In ILC, the agent is the
protocol actor, the AgentID is the account anchor, and a wallet is only an
optional adapter for displaying state or supplying signatures. A value-action
intent is the machine-legible authorization object an agent signs before any
future value-moving runtime may process it. The signed intent carries the
agent's authorization, but it is not itself settlement, balance mutation, or
finality. A live balance change happens only if a separately authorized runtime
accepts the intent, checks nonce and authority, enforces Decimal and
double-entry invariants, writes the ledger atomically, and emits receipts.

This distinction keeps ILC agent-native. The organizing chain is AgentID to
ECU attribution to settled ILC readback, not human-wallet UX. ADR-0026 §§3-5
separate protocol truth from harness/product features: budgeting, onboarding,
and wallet UX sit above protocol surfaces and must not silently widen wallet
authority into transfer, spend, withdrawal, or generalized signing authority.
GAP-AGENT-HARNESS-00 extends that boundary by defining the agent harness loop
as Perceive, Act, Prove, Receive, Delegate. Value-action intents belong in the
Act step, while wallet visibility belongs in readback.

## §2 - Intent Type Taxonomy

| Intent type | Purpose | Activation status |
|-------------|---------|-------------------|
| `transfer_intent` | Move ILC balance from sender agent_id to recipient agent_id | NOT ACTIVATED - requires the transfer-enabled RC authorization lane |
| `spend_intent` | Consume ILC balance for a named protocol service | NOT ACTIVATED - requires separate spend/runtime authority |
| `delegation_fee_intent` | Express a fee authorization from a delegator to a delegate for a named scope | NOT ACTIVATED - requires separate governance |
| `protocol_fee_intent` | Express an agent's authorization to pay a named protocol fee | NOT ACTIVATED - requires separate governance |

### §2.1 - `transfer_intent` field schema

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `intent_type` | string | must be `"transfer"` | Discriminator |
| `agent_id` | string | canonical ILC AgentID | Sender identity |
| `recipient_agent_id` | string | canonical ILC AgentID | Recipient identity; must differ from `agent_id` |
| `amount_ilc` | Decimal string | `>0`, finite, canonical form from `decimal_to_canonical_string` | Amount to transfer; no Python float |
| `fee_ilc` | Decimal string | `>=0`, finite, canonical form | Protocol fee paid by sender; no Python float |
| `nonce` | uint64 | monotonic per `agent_id`, never reuse | Replay prevention |
| `epoch` | uint64 | epoch at time of signing | Temporal binding |
| `network_id` | string | ILC network discriminator | Domain separator contribution |
| `payload_hash` | hex string | SHA-256 of canonical intent JSON minus `signature` | Integrity binding |
| `expiry` | uint64 | epoch after which intent must be rejected | Temporal expiry |
| `domain_separator` | string | `"ilc:transfer_intent:v1"` | Domain separation prefix |

### §2.2 - `spend_intent` field schema

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `intent_type` | string | must be `"spend"` | Discriminator |
| `agent_id` | string | canonical ILC AgentID | Spender identity |
| `service_id` | string | named protocol service | Service being purchased |
| `authorization_scope` | string | named capability scope | What the spend authorizes |
| `amount_ilc` | Decimal string | `>0`, finite, canonical form | Amount spent; no Python float |
| `fee_ilc` | Decimal string | `>=0`, finite, canonical form | Protocol fee; no Python float |
| `nonce` | uint64 | monotonic per `agent_id`, never reuse | Replay prevention |
| `epoch` | uint64 | epoch at time of signing | Temporal binding |
| `network_id` | string | ILC network discriminator | Domain separator contribution |
| `payload_hash` | hex string | SHA-256 of canonical intent JSON minus `signature` | Integrity binding |
| `expiry` | uint64 | epoch after which intent must be rejected | Temporal expiry |
| `domain_separator` | string | `"ilc:spend_intent:v1"` | Domain separation prefix |

### §2.3 - `delegation_fee_intent` field schema

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `intent_type` | string | must be `"delegation_fee"` | Discriminator |
| `delegator_agent_id` | string | canonical ILC AgentID | Delegating party |
| `delegate_agent_id` | string | canonical ILC AgentID | Receiving delegate |
| `fee_ilc` | Decimal string | `>=0`, finite, canonical form | Fee authorized for delegation scope |
| `scope` | string | named delegation scope | What capability is being delegated |
| `epoch` | uint64 | epoch at time of signing | Temporal binding |
| `nonce` | uint64 | monotonic per `delegator_agent_id`, never reuse | Replay prevention |
| `domain_separator` | string | `"ilc:delegation_fee_intent:v1"` | Domain separation prefix |

### §2.4 - `protocol_fee_intent` field schema

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `intent_type` | string | must be `"protocol_fee"` | Discriminator |
| `agent_id` | string | canonical ILC AgentID | Paying agent |
| `fee_ilc` | Decimal string | `>0`, finite, canonical form | Protocol fee amount |
| `fee_reason` | string | named reason code | Why this fee is being paid |
| `epoch` | uint64 | epoch at time of signing | Temporal binding |
| `nonce` | uint64 | monotonic per `agent_id`, never reuse | Replay prevention |
| `domain_separator` | string | `"ilc:protocol_fee_intent:v1"` | Domain separation prefix |

## §3 - Canonical Field Definitions

### §3.1 - Amount fields (`amount_ilc`, `fee_ilc`)

Amount fields are canonical Decimal strings produced by
`decimal_to_canonical_string` from `ilc_core/ledger/exact_numeric.py`. Python
`float` is banned for all value-action amount fields. At every future ledger
input boundary, after constructing `Decimal` from external input, runtimes must
enforce `d.is_finite()` and reject non-finite values with a stable error token.
`fee_ilc` may be `"0"` in canonical form where the specific intent type allows
zero fees. `amount_ilc` must be greater than `Decimal("0")`.

### §3.2 - Nonce semantics

Nonce is a monotonic uint64 per `agent_id`, or per `delegator_agent_id` for
delegation fee intents. It must never be reused for the same agent on the same
network. The ledger runtime, not this schema phase, is responsible for
enforcing monotonicity and persistence. Nonce `0` is reserved and must not be
used in a live value-action intent.

### §3.3 - Domain separator requirement

Every intent type carries a `domain_separator` field with a versioned string
prefix. The canonical signing preimage is:

```python
json.dumps(
    {all fields including domain_separator, excluding signature},
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Those bytes are signed with Ed25519 COSE Sign1 in the initial agent-native
lane. Domain separation prevents cross-type signature replay; a
`transfer_intent` signature cannot be replayed as a `spend_intent`.

### §3.4 - Expiry semantics

`expiry` is a protocol epoch number represented as uint64, not a wall-clock
timestamp. An intent is expired when the processing epoch is greater than or
equal to `expiry`. Future runtime must not use `datetime.now()` to evaluate
protocol expiry; epoch sequence is the time authority.

### §3.5 - `payload_hash` binding

`payload_hash` is SHA-256 of:

```python
json.dumps(
    {all fields except "signature" and "payload_hash"},
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

This binds the full field set and prevents field-stripping attacks. The
signature preimage and the payload hash must be recomputable from the same
canonical field set.

## §4 - Double-Entry Conservation Requirement

For every `transfer_intent`, `amount_ilc + fee_ilc` must be deducted from the
sender's balance; `amount_ilc` must be credited to the recipient; and `fee_ilc`
must be credited to the protocol fee account. Conservation:
`ILC_out(sender) = ILC_in(recipient) + fee`.

For every `spend_intent`, `amount_ilc + fee_ilc` must be deducted from the
spender's balance; `amount_ilc` must be allocated to the named service; and
`fee_ilc` must be credited to the protocol fee account.

This is a structural requirement the field schema must support. A future
runtime must enforce it atomically, with all credits and debits written in one
ledger transaction or rejected entirely. This phase does not implement
enforcement. All arithmetic must use `Decimal`, never float.

## §5 - CDL Decision

Disposition: Option C. A CDL is required before live transfer/spend runtime
activation, but this non-sensitive taxonomy phase records the need without
opening the CDL.

Justification: existing CDL authority covers adjacent surfaces but not a
general ILC value-action runtime. CDL-048 governs ECU mandatory conversion and
settlement-adjacent conversion timing, not agent-to-agent transfer. CDL-066
governs sender authorization for bounded ECU fast-path transfers, not settled
ILC ledger movement. Phase 1578d records signer-binding authority but explicitly
does not activate transfer or spend. Therefore a successor SENSITIVE value-action
phase must ratify or bind the exact runtime authority before guard clearance or
ledger write activation.

The latest pre-RC plan now includes a dedicated live-RC value-action lane. That
lane may satisfy the CDL/runtime authority requirement if its SENSITIVE phases
complete and emit their activation tokens. GAP-VALUE-ACTION-00 itself does not
ratify that authority.

## §6 - Relationship to AgentActionEnvelope

Value-action intents are one `action_type` class in the proposed
`AgentActionEnvelope` defined in
`docs/specs/ilc_agent_native_harness_ontology_and_boundary_spec_GAP_AGENT_HARNESS_00_v0.1.md`
§3.

When `AgentActionEnvelope` is eventually implemented, a `transfer_intent` would
be carried as:

```json
{
  "action_type": "transfer_intent",
  "payload_hash": "<SHA-256 of canonical transfer_intent JSON>"
}
```

The value-action intent's own `payload_hash` (§3.5) and the envelope's outer
`payload_hash` serve distinct purposes and must not be conflated.

## §7 - What Is NOT Activated by This Phase

This phase does not activate transfer, spend, withdrawal, or any wallet guard.
Producing this taxonomy spec does not constitute the broad transfer-enabled RC
GO phrase. The Phase 1578h wallet RC gate verdict remains a historical safety
record until a later SENSITIVE supersession phase replaces its launch-gate
force. No balance will move as a result of this phase. No guard in `ilc_core/`
is cleared. No CDL is opened or amended.

## §8 - Activation Path (Future)

1. Signing provider runtime must be implemented under a separate SENSITIVE phase.
2. AgentActionEnvelope and ILC transfer intent runtime schemas must be
   implemented and tested.
3. Operator delegation runtime must be implemented before any operator-signed
   transfer scope is accepted.
4. Per-agent monotonic nonce registry must be implemented and LMDB-persisted.
5. Double-entry ledger runtime must atomically credit/debit all parties and
   enforce the conservation rule in §4.
6. CDL governance must be completed per §5.
7. Consensus/readback binding must prove the settled balance change is readable
   through the ILC readback chain.
8. Receipt surfaces must emit settlement-linked public legitimacy receipts for
   settled intents.
9. Adversarial tests must cover nonce replay, double-spend, conservation
   violation, non-finite Decimal injection, expiry bypass, and guard mutation.
10. A separate human SENSITIVE authorization must be issued before any guard
    flips or live ledger writes occur.

## §9 - Non-Claims (token style)

- `no_transfer_activation_GAP_VALUE_ACTION_00` - transfer not activated; balance does not move.
- `no_spend_activation_GAP_VALUE_ACTION_00` - spend not activated.
- `no_wallet_guard_clearance_GAP_VALUE_ACTION_00` - wallet transfer and spend guards remain false.
- `no_broad_transfer_enabled_go_issued_GAP_VALUE_ACTION_00` - this phase is not a transfer-enabled RC authorization.
- `no_cdl_opened_GAP_VALUE_ACTION_00` - no CDL opened or amended; CDL decision recorded only.
- `no_ilc_core_change_GAP_VALUE_ACTION_00` - no `ilc_core/` files modified.
- `no_phase_1578h_conflict_GAP_VALUE_ACTION_00` - this phase does not conflict with the historical Phase 1578h wallet RC gate.
- `no_nonce_runtime_GAP_VALUE_ACTION_00` - no nonce registry implemented.
- `no_double_entry_runtime_GAP_VALUE_ACTION_00` - conservation rule is a spec requirement; runtime not implemented.
