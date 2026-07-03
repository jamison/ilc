# ILC Circuit Definition Node Schema v0.1

Status: schema-seam specification  
Authority context: ADR-0035, CDL-097  
Phase: 1568-Fix2x  
Sensitivity: NON-SENSITIVE

## Purpose

This document defines the graph-native schema seams for governed circuit
definitions, circuit parameters, circuit execution receipts, circuit
supersession edges, and circuit authority edges. The goal is to reserve stable
graph shapes before public RC so later proof and circuit work can attach to the
graph without a structural refactor.

This is a schema document only. It does not activate the ADR-0035 type registry.
It does not execute a circuit, generate a proof, verify a proof, authorize
recursive proof settlement, write wallets, write treasury state, mint, settle,
or activate public RC.

## Authority Boundary

ADR-0035 defines the long-term target: type and behavior semantics should become
addressable graph nodes rather than hardcoded external strings. CDL-097 ratifies
the type-definition node authority lane and the non-attributable treatment for
definition-node infrastructure.

The current type registry remains default-off under:

```text
ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True
```

Therefore this document defines schema seams only. Runtime promotion requires a
separate authority phase.

## Serialization Rules

All records defined here use canonical serialization:

- JSON fields are serialized with deterministic key ordering.
- Hash inputs use `sort_keys=True`, `separators=(",", ":")`, and
  `allow_nan=False` when represented as JSON.
- Protocol numeric values use integers or Decimal values serialized as strings.
- Python `float`, NaN, Infinity, and implementation-local object encodings are
  forbidden.
- Content-addressed IDs are computed over the canonical content payload with the
  ID field excluded from its own hash input.

## CircuitDefinitionNode

`CircuitDefinitionNode` is an immutable graph node describing a governed
circuit.

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `circuit_id` | string | `sha256:<hex>` of canonical circuit content with `circuit_id` excluded |
| `circuit_version` | string | Semver string such as `0.1.0` |
| `description` | string | Human-readable description of the circuit's governed purpose |
| `input_schema_ref` | string | Content-addressed reference to the canonical input schema |
| `output_schema_ref` | string | Content-addressed reference to the canonical output schema |
| `cdl_authority` | string | CDL or ADR authority reference, preferably CDL-ratified for protocol use |
| `annotation_method` | string | Method used to annotate the circuit into the graph |
| `annotation_phase` | string | Phase or authority event that created the node |

Recommended fields:

| Field | Type | Semantics |
|---|---|---|
| `proof_system_family` | string | Informational target family such as `stark`, `supernova`, `hypernova`, or `groth16_deferred` |
| `source_commitment` | string | Hash of source artifact, IR, R1CS, AIR, or other circuit representation |
| `non_attributable` | boolean | Must be `true` for definition infrastructure under CDL-097 |

Invariants:

- Circuit definitions are immutable.
- A changed circuit is a new `CircuitDefinitionNode`.
- Historical receipts remain governed by the circuit definition active at their
  execution epoch.
- Definition nodes are infrastructure and do not receive ECU attribution.

## CircuitParamsNode

`CircuitParamsNode` records CDL-governed parameters for a circuit.

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `params_id` | string | `sha256:<hex>` of canonical parameter content with `params_id` excluded |
| `circuit_id` | string | Reference to the governed `CircuitDefinitionNode` |
| `params_version` | string | Semver string for this parameter set |
| `parameters` | object | Deterministic dictionary; integers or Decimal strings only; no floats |
| `cdl_authority` | string | CDL or ADR reference authorizing the parameter set |
| `effective_epoch` | integer | First epoch in which this parameter set may govern future executions |

Invariants:

- Parameter updates create new `CircuitParamsNode` records.
- Parameter changes do not mutate circuit definitions.
- Parameter records are snapshot-governed: old receipts keep their original
  `params_id`.

## CircuitExecutionReceipt

`CircuitExecutionReceipt` records one execution result against a governed
circuit and parameter set.

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `receipt_id` | string | `sha256:<hex>` of canonical receipt content with `receipt_id` excluded |
| `circuit_id` | string | Reference to the governed `CircuitDefinitionNode` |
| `circuit_version` | string | Version of the circuit used for this execution |
| `params_root` | string | SHA-256 root of the referenced `CircuitParamsNode` |
| `input_commitment` | string | Commitment to the canonical private or public input |
| `output_commitment` | string | Commitment to the canonical output |
| `cdl_authority` | string | Authority under which this execution receipt is interpretable |
| `epoch` | integer | Epoch in which the execution receipt was created |

Recommended fields:

| Field | Type | Semantics |
|---|---|---|
| `proof_receipt_ref` | string | Reference to a `ProofReceiptNode` if proof material exists |
| `execution_context_ref` | string | Optional context reference for sidecar or app execution |

Invariants:

- A receipt records a claim about execution; it is not proof verification by
  itself.
- A receipt cannot imply settlement, wallet writes, treasury writes, minting, or
  public claimability without a separate value-path authority.

## CircuitSupersedesEdge

`CircuitSupersedesEdge` links a newer circuit definition to an older circuit
definition.

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `superseded_circuit_id` | string | Older circuit definition ID |
| `superseding_circuit_id` | string | Newer circuit definition ID |
| `authority_cdl` | string | CDL or ADR authority that authorized supersession |
| `effective_epoch` | integer | First epoch in which the new circuit governs future executions |

Semantics:

- Supersession is forward-looking.
- The old circuit remains valid historically.
- The new circuit governs future epochs after `effective_epoch`.
- Supersession must be acyclic.

## CircuitAuthorityEdge

`CircuitAuthorityEdge` binds a circuit definition to its ratifying authority.

Required fields:

| Field | Type | Semantics |
|---|---|---|
| `circuit_id` | string | Circuit definition ID |
| `cdl_or_adr_ref` | string | CDL or ADR reference authorizing the circuit |
| `ratification_epoch` | integer | Epoch of ratification or authority record |

Semantics:

- A circuit without a valid authority edge is not protocol-governing.
- A circuit may be informational or experimental without authority, but must not
  be used for settlement, finality, or public claims.

## CDL-044 Retention Exemption

`CircuitDefinitionNode`, `CircuitParamsNode`, `CircuitExecutionReceipt`,
`CircuitSupersedesEdge`, and `CircuitAuthorityEdge` are exempt from CDL-044
pruning when referenced by a proof receipt, settlement receipt, epoch receipt,
or other load-bearing protocol record. Historical proof receipts require their
original circuit and parameter records to remain retrievable.

## Non-Execution Declaration

This document defines schema seams only. It does not activate the ADR-0035 type
registry. It does not execute a circuit, generate a proof, verify a proof,
activate recursive proof settlement, promote a type-definition node, authorize a
public proof security claim, write wallets, write treasury state, mint, settle,
or activate public RC.
