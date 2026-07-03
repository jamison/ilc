# ILC Proof Receipt Node Schema v0.1

Status: schema-seam specification  
Authority context: ADR-0035, CDL-097, OBL-048  
Phase: 1568-Fix2x  
Sensitivity: NON-SENSITIVE

## Purpose

This document defines a first-class graph node schema for proof receipts. A
proof receipt records a content-addressed claim that a proof artifact, circuit
definition, parameter root, input commitment, and output commitment belong
together under a stated authority.

This is a schema document only. It does not activate the ADR-0035 type registry.
It does not execute a circuit, generate a proof, verify a proof, activate a
verifier, activate recursive proof settlement, promote a proof security claim,
write wallets, write treasury state, mint, settle, or activate public RC.

## Authority Boundary

Proof receipts depend on governed circuit definitions and parameter records.
Those seams are defined in:

```text
docs/specs/ilc_circuit_definition_node_schema_v0.1.md
```

ADR-0035 and CDL-097 provide the type-definition authority context, but the
runtime type registry remains default-off. A later phase must ratify or activate
any concrete proof verifier before receipts become settlement-bearing.

## Serialization Rules

All proof receipt records use canonical serialization:

- JSON fields are serialized with deterministic key ordering.
- Hash inputs use `sort_keys=True`, `separators=(",", ":")`, and
  `allow_nan=False` when represented as JSON.
- Numeric parameters use integers or Decimal values serialized as strings.
- Python `float`, NaN, Infinity, and implementation-local object encodings are
  forbidden.
- `receipt_id` is computed over the canonical receipt payload with `receipt_id`
  excluded.

## Proof System Enum

Allowed `proof_system` values:

```text
stark
supernova
hypernova
groth16_deferred
```

`groth16_deferred` is explicitly non-default for ILC because it implies trusted
setup considerations unless separately ratified.

## ProofReceiptNode

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `receipt_id` | string | `sha256:<hex>` of canonical proof receipt content with `receipt_id` excluded |
| `circuit_id` | string | Reference to a `CircuitDefinitionNode` |
| `params_root` | string | SHA-256 root of the referenced `CircuitParamsNode` |
| `input_commitment` | string | Commitment to private or public input |
| `output_commitment` | string | Commitment to output |
| `cdl_authority` | string | CDL or ADR authority under which the receipt is interpretable |
| `proof_system` | enum | One of `stark`, `supernova`, `hypernova`, `groth16_deferred` |

Recommended fields:

| Field | Type | Semantics |
|---|---|---|
| `proof_artifact_ref` | string | Content-addressed reference to proof bytes or external proof storage |
| `verifier_ref` | string | Reference to the verifier definition, if one is ratified |
| `recursive_parent_receipt_ids` | array[string] | Prior proof receipts folded into this receipt |
| `epoch` | integer | Epoch in which the receipt was created |
| `receipt_context` | string | Protocol, sidecar, or app context for the receipt |

## Receipt Semantics

A `ProofReceiptNode` is a graph-native receipt, not an implicit proof verifier.
It says which proof artifact and circuit context are being asserted. It does
not say the proof has been accepted for settlement unless a later ratified
verifier path records that acceptance.

Required non-claims:

- A proof receipt is not wallet authority.
- A proof receipt is not treasury authority.
- A proof receipt is not minting authority.
- A proof receipt is not settlement authority.
- A proof receipt is not public claimability.
- A proof receipt is not public RC activation.
- A proof receipt is not a generalized proof-security claim.

## Retention Rule and CDL-044 Exemption

Proof receipts and their referenced `CircuitDefinitionNode` and
`CircuitParamsNode` records are exempt from CDL-044 pruning. Historical proof
receipts must remain replayable under their original circuit and parameter
combination, even after later circuit supersession.

This exemption is narrow:

- It applies to circuit and parameter records referenced by a load-bearing proof
  receipt.
- It does not exempt unrelated app payloads, raw private inputs, or unreferenced
  experimental artifacts.
- It does not activate public publication of private proof inputs.

## Relationship to Circuit Edges

`ProofReceiptNode` records may be connected through:

| Edge | Purpose |
|---|---|
| `CircuitAuthorityEdge` | Proves which CDL or ADR authorizes the circuit |
| `CircuitSupersedesEdge` | Preserves historical validity across circuit upgrades |
| `PROOF_USES_CIRCUIT` | Optional future edge from receipt to circuit definition |
| `PROOF_USES_PARAMS` | Optional future edge from receipt to parameter node |
| `PROOF_FOLDS_RECEIPT` | Optional future edge from recursive receipt to prior receipt |

These edge names are schema seams, not activated runtime constants.

## Non-Execution Declaration

This document defines schema seams only. It does not activate the ADR-0035 type
registry. It does not execute a circuit, generate a proof, verify a proof,
activate a verifier, activate recursive proof settlement, promote a
type-definition node, authorize a public proof-security claim, write wallets,
write treasury state, mint, settle, publish private proof inputs, or activate
public RC.
