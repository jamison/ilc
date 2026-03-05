# ILC Executable Descriptor Runtime Handoff 363 v0.1

Status: runtime handoff artifact
Date: 2026-03-05
Phase: 363

## 1. Implementation scope

Phase 363 implements the CDL-037 executable-descriptor runtime tranche for structured descriptor validation, sandboxed runtime binding, safety-contract verification, and genesis-trust boundary enforcement.

Implemented runtime module:
- `ilc_core/node/executable_descriptor_runtime_363.py`

## 2. Dependency and version locks

Locked constants:
- `EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION = "executable_descriptor_runtime_363.v0.1"`
- `CDL_037_DEPENDENCY = "cdl_037_ratified_352.v0.1"`
- `NODE_DISSEMINATION_DEPENDENCY = "node_dissemination_runtime_362.v0.1"`

## 3. Descriptor field contract

Structured descriptor with sandboxed runtime binding is enforced via required descriptor fields:
- `declared_inputs`
- `declared_outputs`
- `declared_side_effects`
- `safety_assertions`
- `determinism_guarantees`
- `bounded_resource_guarantees`

This runtime enforces the ratified phrase: structured descriptor with sandboxed runtime binding.

Nodes recommend logic; they do not self-authorize execution.

## 4. Sandboxed runtime binding contract

Execution context is validated as a runtime-side contract with `runtime_binding = sandboxed_agent_runtime`.

Agent-side sandboxing is a safety-contract obligation.
agent-side sandboxing is a safety-contract obligation

Self-authorized execution requests are rejected with deterministic tokens.

## 5. Safety-contract verification and genesis-trust boundary

Genesis-trusted executable descriptor and non-genesis executable descriptor contracts are explicit and mutually constrained.

Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.

Safety-contract references are prefix-validated (`genesis://` vs `contract://`) against `genesis_trusted` state.

## 6. Authored-envelope and transport-boundary preservation statement

The executable descriptor is authored payload content.

Execution context belongs to runtime binding metadata and is not injected into authored payload.

The three-envelope boundary established in Phase 340 and transport boundary from CDL-036 remain intact.

## 7. Validation failure token catalog

Representative deterministic tokens:
- `executable_descriptor_field_invalid`
- `executable_descriptor_safety_assertion_missing`
- `executable_genesis_boundary_violation`
- `executable_self_authorized_execution_forbidden`
- `executable_runtime_binding_invalid`
- `executable_record_digest_mismatch`

## 8. Carry-forward constraints for phase 364

Phase 364 must keep promotion continuity subordinate to the ratified CDL-037 executable-node contract.

Phase 364 must not weaken descriptor sandboxing, genesis-trust boundaries, or runtime-vs-authored envelope separation.

## 9. Non-goals

This tranche does not:
- implement CDL-038 promotion runtime,
- mutate decision-log state,
- authorize self-executing payloads,
- collapse runtime binding into authored payload.
