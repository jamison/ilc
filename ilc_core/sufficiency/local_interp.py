# SPDX-License-Identifier: AGPL-3.0-only
"""Bounded local interpreter for provisional Sufficiency recipe fixtures.

The records accepted here are local application records, not canonical ILC
Graph Nodes. The module has no production-store adapter, network access, code
loader, type-registry activation, or economic authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence


SUFFICIENCY_LOCAL_INTERP_ENABLED = False

RECIPE_SCHEMA_VERSION = "sufficiency_local_recipe_v0"
EXECUTION_PROFILE = "local_fixture_v0"
CHECKER_ID = "ilc_core.sufficiency.local_interp"
CHECKER_VERSION = "1"

MAX_RECIPE_BYTES = 65_536
MAX_STEPS = 128
MAX_BOUNDARY_INPUTS = 128
MAX_BINDINGS_PER_STEP = 64
MAX_OUTPUTS_PER_STEP = 16
MAX_TOTAL_OUTPUTS = 256
MAX_COLLECTION_ITEMS = 1_024
MAX_STRING_LENGTH = 4_096
MAX_IDENTIFIER_LENGTH = 256
MAX_VALUE_DEPTH = 16
MAX_VALUE_NODES = 10_000
MAX_INTEGER_MAGNITUDE = 2**53
MAX_REGISTERED_OPERATIONS = 256
MAX_REPLAY_RECEIPTS = 1_024

_RECIPE_KEYS = frozenset(
    {
        "schema_version",
        "recipe_version",
        "execution_profile",
        "inputs",
        "steps",
        "outputs",
        "effects",
        "limits",
    }
)
_INPUT_KEYS = frozenset({"name", "type"})
_STEP_KEYS = frozenset(
    {"step_id", "operation_ref", "bindings", "outputs", "effects"}
)
_OP_REF_KEYS = frozenset(
    {"operation_id", "operation_version", "implementation_ref"}
)
_BINDING_KEYS = frozenset({"role_name", "ordinal", "value_ref"})
_OUTPUT_KEYS = frozenset({"name", "value_ref"})
_LIMIT_KEYS = frozenset({"expanded_steps"})
_INPUT_TYPES = frozenset({"integer", "string", "boolean", "json"})


class InterpError(ValueError):
    """Base class for stable local interpreter failures."""

    def __init__(
        self,
        code: str,
        *,
        receipt: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.receipt = copy.deepcopy(dict(receipt)) if receipt is not None else None


class InterpGuardError(InterpError):
    """Raised before preparation when a non-local store reaches the guard."""


class InterpValidationError(InterpError):
    """Raised when a recipe or invocation is structurally invalid."""


class InterpResourceError(InterpError):
    """Raised when a finite local profile bound is exceeded."""


class InterpGapError(InterpError):
    """Raised when an explicitly referenced local operation is unavailable."""


class InterpReplayError(InterpError):
    """Raised when one invocation ID is reused for different request content."""


class InterpExecutionError(InterpError):
    """Raised when a registered operation fails or violates its output contract."""


@dataclass(frozen=True)
class OperationDefinition:
    """One explicitly registered, pure local-fixture operation."""

    operation_id: str
    operation_version: str
    implementation_ref: str
    roles: tuple[tuple[str, int], ...]
    output_names: tuple[str, ...]
    handler: Callable[..., Mapping[str, Any]]
    permitted_effects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.operation_id, "operation_id")
        _require_identifier(self.operation_version, "operation_version")
        _require_identifier(self.implementation_ref, "implementation_ref")
        if not callable(self.handler):
            raise InterpValidationError("operation_handler_not_callable")
        if type(self.roles) is not tuple:
            raise InterpValidationError("operation_roles_type_invalid")
        if type(self.output_names) is not tuple:
            raise InterpValidationError("operation_outputs_type_invalid")
        if type(self.permitted_effects) is not tuple:
            raise InterpValidationError("operation_effects_type_invalid")
        if self.permitted_effects:
            raise InterpValidationError("operation_effects_not_supported")
        if not self.roles or len(self.roles) > MAX_BINDINGS_PER_STEP:
            raise InterpValidationError("operation_roles_invalid")
        seen_roles: set[tuple[str, int]] = set()
        for role_name, ordinal in self.roles:
            _require_identifier(role_name, "role_name")
            _require_nonnegative_int(ordinal, "role_ordinal")
            coordinate = (role_name, ordinal)
            if coordinate in seen_roles:
                raise InterpValidationError("operation_role_coordinate_duplicate")
            seen_roles.add(coordinate)
        if {ordinal for _, ordinal in self.roles} != set(range(len(self.roles))):
            raise InterpValidationError("operation_role_ordinals_noncontiguous")
        if len(self.output_names) == 0 or len(self.output_names) > MAX_OUTPUTS_PER_STEP:
            raise InterpValidationError("operation_outputs_invalid")
        seen_outputs: set[str] = set()
        for name in self.output_names:
            _require_identifier(name, "operation_output_name")
            if name in seen_outputs:
                raise InterpValidationError("operation_output_name_duplicate")
            seen_outputs.add(name)

    @property
    def key(self) -> tuple[str, str, str]:
        return (
            self.operation_id,
            self.operation_version,
            self.implementation_ref,
        )


class LocalFixtureStore:
    """Explicitly isolated registry and replay cache for local tests."""

    def __init__(self, operations: Sequence[OperationDefinition] = ()) -> None:
        self._operations: dict[tuple[str, str, str], OperationDefinition] = {}
        self._receipts: dict[str, tuple[str, dict[str, Any]]] = {}
        for operation in operations:
            self.register_operation(operation)

    def register_operation(self, operation: OperationDefinition) -> None:
        if type(operation) is not OperationDefinition:
            raise InterpValidationError("operation_definition_type_invalid")
        if operation.key in self._operations:
            raise InterpValidationError("operation_definition_duplicate")
        if len(self._operations) >= MAX_REGISTERED_OPERATIONS:
            raise InterpResourceError("operation_registry_limit_exceeded")
        self._operations[operation.key] = operation

    def resolve_operation(
        self, operation_id: str, operation_version: str, implementation_ref: str
    ) -> OperationDefinition | None:
        return self._operations.get(
            (operation_id, operation_version, implementation_ref)
        )

    def replay(self, root_invocation_id: str, fingerprint: str) -> dict[str, Any] | None:
        prior = self._receipts.get(root_invocation_id)
        if prior is None:
            return None
        prior_fingerprint, receipt = prior
        if prior_fingerprint != fingerprint:
            raise InterpReplayError("invocation_id_request_fingerprint_collision")
        return copy.deepcopy(receipt)

    def seal_receipt(
        self, root_invocation_id: str, fingerprint: str, receipt: Mapping[str, Any]
    ) -> None:
        prior = self._receipts.get(root_invocation_id)
        if prior is not None and prior[0] != fingerprint:
            raise InterpReplayError("invocation_id_request_fingerprint_collision")
        if prior is None and len(self._receipts) >= MAX_REPLAY_RECEIPTS:
            raise InterpResourceError("replay_receipt_limit_exceeded")
        self._receipts[root_invocation_id] = (
            fingerprint,
            copy.deepcopy(dict(receipt)),
        )

    def require_receipt_capacity(self, root_invocation_id: str) -> None:
        if (
            root_invocation_id not in self._receipts
            and len(self._receipts) >= MAX_REPLAY_RECEIPTS
        ):
            raise InterpResourceError("replay_receipt_limit_exceeded")


@dataclass(frozen=True)
class _Plan:
    recipe: dict[str, Any]
    recipe_id: str
    canonical_recipe: bytes
    schedule: tuple[str, ...]
    steps: Mapping[str, dict[str, Any]]
    operations: Mapping[str, OperationDefinition]
    output_producers: Mapping[str, str]
    schedule_digest: str


def execute_recipe(
    *,
    store: object,
    recipe: Mapping[str, Any],
    inputs: Mapping[str, Any],
    root_invocation_id: str,
    completed_at: str | None = None,
) -> dict[str, Any]:
    """Validate and execute one bounded flat-DAG local recipe."""

    # LocalFixtureStore is the explicit test capability; the global guard applies
    # only to future production adapters. Exact type prevents capability spoofing.
    if type(store) is not LocalFixtureStore:
        if not SUFFICIENCY_LOCAL_INTERP_ENABLED:
            raise InterpGuardError("sufficiency_local_interp_not_enabled")
        raise InterpGuardError("production_store_adapter_not_implemented")

    _require_identifier(root_invocation_id, "root_invocation_id")
    plan = _build_plan(store, recipe)
    normalized_inputs = _validate_boundary_inputs(plan.recipe, inputs)
    input_commitment = _digest_domain(
        "ilc.sufficiency.local-inputs.v0", _canonical_json(normalized_inputs)
    )
    request_body = {
        "execution_profile": EXECUTION_PROFILE,
        "inputs": normalized_inputs,
        "recipe_id": plan.recipe_id,
        "schedule_digest": plan.schedule_digest,
    }
    request_fingerprint = _digest_domain(
        "ilc.sufficiency.local-request.v0", _canonical_json(request_body)
    )
    replay = store.replay(root_invocation_id, request_fingerprint)
    if replay is not None:
        return replay
    store.require_receipt_capacity(root_invocation_id)

    values: dict[str, Any] = {
        f"input:{name}": copy.deepcopy(value)
        for name, value in normalized_inputs.items()
    }
    trace: list[dict[str, Any]] = []
    timestamp = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if completed_at is None
        else completed_at
    )
    _validate_timestamp(timestamp)

    for occurrence_index, step_id in enumerate(plan.schedule):
        step = plan.steps[step_id]
        operation = plan.operations[step_id]
        ordered_bindings = sorted(step["bindings"], key=lambda item: item["ordinal"])
        arguments = [copy.deepcopy(values[item["value_ref"]]) for item in ordered_bindings]
        occurrence_path = {
            "root_invocation_id": root_invocation_id,
            "parent_frames": [],
            "leaf_recipe_id": plan.recipe_id,
            "leaf_step_id": step_id,
            "leaf_occurrence_index": occurrence_index,
        }
        try:
            produced = operation.handler(*arguments)
        except Exception as exc:
            receipt = _receipt(
                root_invocation_id=root_invocation_id,
                request_fingerprint=request_fingerprint,
                plan=plan,
                input_commitment=input_commitment,
                output_values={},
                output_commitment=None,
                trace=trace,
                completed_at=timestamp,
                outcome_status="rejected",
                outcome_reason="operation_execution_failed",
            )
            store.seal_receipt(root_invocation_id, request_fingerprint, receipt)
            raise InterpExecutionError(
                "operation_execution_failed", receipt=receipt
            ) from exc
        try:
            normalized_outputs = _validate_operation_outputs(operation, produced)
        except InterpError as exc:
            receipt = _receipt(
                root_invocation_id=root_invocation_id,
                request_fingerprint=request_fingerprint,
                plan=plan,
                input_commitment=input_commitment,
                output_values={},
                output_commitment=None,
                trace=trace,
                completed_at=timestamp,
                outcome_status="rejected",
                outcome_reason=exc.code,
            )
            store.seal_receipt(root_invocation_id, request_fingerprint, receipt)
            raise InterpExecutionError(exc.code, receipt=receipt) from exc
        for name, value in normalized_outputs.items():
            values[f"value:{name}"] = value
        trace.append(
            {
                "occurrence_path": occurrence_path,
                "operation_id": operation.operation_id,
                "operation_version": operation.operation_version,
                "implementation_ref": operation.implementation_ref,
                "binding_coordinates": [
                    [item["role_name"], item["ordinal"]] for item in ordered_bindings
                ],
                "input_refs": [item["value_ref"] for item in ordered_bindings],
                "output_names": list(operation.output_names),
                "effects_attempted": [],
                "effects_applied": [],
                "outcome_status": "succeeded",
            }
        )

    output_values = {
        output["name"]: copy.deepcopy(values[output["value_ref"]])
        for output in plan.recipe["outputs"]
    }
    output_commitment = _digest_domain(
        "ilc.sufficiency.local-outputs.v0", _canonical_json(output_values)
    )
    receipt = _receipt(
        root_invocation_id=root_invocation_id,
        request_fingerprint=request_fingerprint,
        plan=plan,
        input_commitment=input_commitment,
        output_values=output_values,
        output_commitment=output_commitment,
        trace=trace,
        completed_at=timestamp,
        outcome_status="succeeded",
        outcome_reason=None,
    )
    store.seal_receipt(root_invocation_id, request_fingerprint, receipt)
    return copy.deepcopy(receipt)


def _build_plan(store: LocalFixtureStore, recipe: Mapping[str, Any]) -> _Plan:
    normalized = _normalize_recipe(recipe)
    canonical_recipe = _canonical_json(normalized)
    if len(canonical_recipe) > MAX_RECIPE_BYTES:
        raise InterpResourceError("recipe_bytes_limit_exceeded")
    recipe_id = _digest_domain("ilc.sufficiency.local-recipe.v0", canonical_recipe)

    steps = {step["step_id"]: step for step in normalized["steps"]}
    output_producers: dict[str, str] = {}
    for step in normalized["steps"]:
        for output_name in step["outputs"]:
            if output_name in output_producers:
                raise InterpValidationError("recipe_output_name_ambiguous")
            output_producers[output_name] = step["step_id"]

    input_names = {item["name"] for item in normalized["inputs"]}
    dependencies: dict[str, set[str]] = {step_id: set() for step_id in steps}
    operations: dict[str, OperationDefinition] = {}
    for step_id, step in steps.items():
        operation_ref = step["operation_ref"]
        operation = store.resolve_operation(
            operation_ref["operation_id"],
            operation_ref["operation_version"],
            operation_ref["implementation_ref"],
        )
        if operation is None:
            raise InterpGapError(
                "operation_unavailable:"
                f"{operation_ref['operation_id']}:"
                f"{operation_ref['operation_version']}:"
                f"{operation_ref['implementation_ref']}"
            )
        operations[step_id] = operation
        expected_coordinates = sorted(operation.roles, key=lambda item: item[1])
        actual_coordinates = sorted(
            [(item["role_name"], item["ordinal"]) for item in step["bindings"]],
            key=lambda item: item[1],
        )
        if actual_coordinates != expected_coordinates:
            raise InterpValidationError("operation_binding_contract_mismatch")
        if tuple(step["outputs"]) != operation.output_names:
            raise InterpValidationError("operation_output_contract_mismatch")
        _bind_step_dependencies(
            step_id,
            step["bindings"],
            input_names,
            output_producers,
            dependencies,
        )

    for output in normalized["outputs"]:
        value_ref = output["value_ref"]
        if value_ref.startswith("input:"):
            if value_ref[6:] not in input_names:
                raise InterpValidationError("recipe_output_reference_missing")
        elif value_ref.startswith("value:"):
            if value_ref[6:] not in output_producers:
                raise InterpValidationError("recipe_output_reference_missing")
        else:
            raise InterpValidationError("recipe_output_reference_invalid")

    schedule = _topological_schedule(dependencies)
    schedule_contract = {
        "execution_profile": normalized["execution_profile"],
        "recipe_version": normalized["recipe_version"],
        "steps": [
            {
                "bindings": sorted(steps[step_id]["bindings"], key=lambda item: item["ordinal"]),
                "operation_ref": steps[step_id]["operation_ref"],
                "outputs": steps[step_id]["outputs"],
                "step_id": step_id,
            }
            for step_id in schedule
        ],
    }
    schedule_digest = _digest_domain(
        "ilc.sufficiency.local-schedule.v0", _canonical_json(schedule_contract)
    )
    return _Plan(
        recipe=normalized,
        recipe_id=recipe_id,
        canonical_recipe=canonical_recipe,
        schedule=schedule,
        steps=steps,
        operations=operations,
        output_producers=output_producers,
        schedule_digest=schedule_digest,
    )


def _bind_step_dependencies(
    step_id: str,
    bindings: list[dict[str, Any]],
    input_names: set[str],
    output_producers: Mapping[str, str],
    dependencies: dict[str, set[str]],
) -> None:
    for binding in bindings:
        value_ref = binding["value_ref"]
        if value_ref.startswith("input:"):
            if value_ref[6:] not in input_names:
                raise InterpValidationError("recipe_input_dependency_missing")
            continue
        if value_ref.startswith("value:"):
            producer = output_producers.get(value_ref[6:])
            if producer is None:
                raise InterpValidationError("recipe_step_dependency_missing")
            dependencies[step_id].add(producer)
            continue
        raise InterpValidationError("recipe_binding_reference_invalid")


def _normalize_recipe(recipe: Mapping[str, Any]) -> dict[str, Any]:
    if type(recipe) is not dict:
        raise InterpValidationError("recipe_root_type_invalid")
    _validate_json_value(recipe)
    _require_exact_keys(recipe, _RECIPE_KEYS, "recipe")
    if recipe["schema_version"] != RECIPE_SCHEMA_VERSION:
        raise InterpValidationError("recipe_schema_version_invalid")
    _require_identifier(recipe["recipe_version"], "recipe_version")
    if recipe["execution_profile"] != EXECUTION_PROFILE:
        raise InterpValidationError("recipe_execution_profile_invalid")
    if recipe["effects"] != []:
        raise InterpValidationError("recipe_effects_not_supported")

    limits = recipe["limits"]
    if type(limits) is not dict:
        raise InterpValidationError("recipe_limits_type_invalid")
    _require_exact_keys(limits, _LIMIT_KEYS, "recipe_limits")
    expanded_steps = limits["expanded_steps"]
    _require_nonnegative_int(expanded_steps, "expanded_steps")

    inputs = recipe["inputs"]
    steps = recipe["steps"]
    outputs = recipe["outputs"]
    if type(inputs) is not list or len(inputs) > MAX_BOUNDARY_INPUTS:
        raise InterpResourceError("recipe_inputs_limit_exceeded")
    if type(steps) is not list or len(steps) == 0:
        raise InterpValidationError("recipe_steps_invalid")
    if len(steps) > MAX_STEPS or expanded_steps > MAX_STEPS or expanded_steps != len(steps):
        raise InterpResourceError("recipe_steps_limit_exceeded")
    if type(outputs) is not list or len(outputs) == 0 or len(outputs) > MAX_TOTAL_OUTPUTS:
        raise InterpResourceError("recipe_outputs_limit_exceeded")

    input_names: set[str] = set()
    for item in inputs:
        if type(item) is not dict:
            raise InterpValidationError("recipe_input_descriptor_invalid")
        _require_exact_keys(item, _INPUT_KEYS, "recipe_input")
        _require_identifier(item["name"], "input_name")
        if item["name"] in input_names:
            raise InterpValidationError("recipe_input_name_duplicate")
        input_names.add(item["name"])
        if item["type"] not in _INPUT_TYPES:
            raise InterpValidationError("recipe_input_type_invalid")

    step_ids: set[str] = set()
    total_step_outputs = 0
    for step in steps:
        if type(step) is not dict:
            raise InterpValidationError("recipe_step_type_invalid")
        _require_exact_keys(step, _STEP_KEYS, "recipe_step")
        _require_identifier(step["step_id"], "step_id")
        if step["step_id"] in step_ids:
            raise InterpValidationError("recipe_step_id_duplicate")
        step_ids.add(step["step_id"])
        operation_ref = step["operation_ref"]
        if type(operation_ref) is not dict:
            raise InterpValidationError("recipe_operation_ref_invalid")
        _require_exact_keys(operation_ref, _OP_REF_KEYS, "operation_ref")
        for field in sorted(_OP_REF_KEYS):
            _require_identifier(operation_ref[field], field)
        bindings = step["bindings"]
        if type(bindings) is not list or len(bindings) == 0:
            raise InterpValidationError("recipe_bindings_invalid")
        if len(bindings) > MAX_BINDINGS_PER_STEP:
            raise InterpResourceError("recipe_bindings_limit_exceeded")
        coordinates: set[tuple[str, int]] = set()
        ordinals: set[int] = set()
        for binding in bindings:
            if type(binding) is not dict:
                raise InterpValidationError("recipe_binding_type_invalid")
            _require_exact_keys(binding, _BINDING_KEYS, "recipe_binding")
            _require_identifier(binding["role_name"], "role_name")
            _require_nonnegative_int(binding["ordinal"], "binding_ordinal")
            _require_identifier(binding["value_ref"], "value_ref")
            coordinate = (binding["role_name"], binding["ordinal"])
            if coordinate in coordinates:
                raise InterpValidationError("recipe_binding_coordinate_duplicate")
            if binding["ordinal"] in ordinals:
                raise InterpValidationError("recipe_binding_ordinal_duplicate")
            coordinates.add(coordinate)
            ordinals.add(binding["ordinal"])
        if ordinals != set(range(len(bindings))):
            raise InterpValidationError("recipe_binding_ordinals_noncontiguous")
        step_outputs = step["outputs"]
        if type(step_outputs) is not list or not step_outputs:
            raise InterpValidationError("recipe_step_outputs_invalid")
        if len(step_outputs) > MAX_OUTPUTS_PER_STEP:
            raise InterpResourceError("recipe_step_outputs_limit_exceeded")
        if len(set(step_outputs)) != len(step_outputs):
            raise InterpValidationError("recipe_step_output_duplicate")
        for output_name in step_outputs:
            _require_identifier(output_name, "step_output_name")
        total_step_outputs += len(step_outputs)
        if step["effects"] != []:
            raise InterpValidationError("recipe_effects_not_supported")
    if total_step_outputs > MAX_TOTAL_OUTPUTS:
        raise InterpResourceError("recipe_total_outputs_limit_exceeded")

    public_output_names: set[str] = set()
    for output in outputs:
        if type(output) is not dict:
            raise InterpValidationError("recipe_public_output_invalid")
        _require_exact_keys(output, _OUTPUT_KEYS, "recipe_public_output")
        _require_identifier(output["name"], "public_output_name")
        _require_identifier(output["value_ref"], "public_output_ref")
        if output["name"] in public_output_names:
            raise InterpValidationError("recipe_public_output_name_duplicate")
        public_output_names.add(output["name"])

    return copy.deepcopy(recipe)


def _validate_boundary_inputs(
    recipe: Mapping[str, Any], inputs: Mapping[str, Any]
) -> dict[str, Any]:
    if type(inputs) is not dict:
        raise InterpValidationError("invocation_inputs_type_invalid")
    _validate_json_value(inputs)
    descriptors = {item["name"]: item["type"] for item in recipe["inputs"]}
    if set(inputs) != set(descriptors):
        raise InterpValidationError("invocation_input_set_mismatch")
    for name, declared_type in descriptors.items():
        value = inputs[name]
        if declared_type == "integer" and type(value) is not int:
            raise InterpValidationError("invocation_input_type_mismatch")
        if declared_type == "string" and type(value) is not str:
            raise InterpValidationError("invocation_input_type_mismatch")
        if declared_type == "boolean" and type(value) is not bool:
            raise InterpValidationError("invocation_input_type_mismatch")
    return copy.deepcopy(dict(inputs))


def _validate_operation_outputs(
    operation: OperationDefinition, produced: object
) -> dict[str, Any]:
    if type(produced) is not dict:
        raise InterpExecutionError("operation_output_type_invalid")
    if set(produced) != set(operation.output_names):
        raise InterpExecutionError("operation_output_set_mismatch")
    _validate_json_value(produced)
    return copy.deepcopy(produced)


def _topological_schedule(dependencies: Mapping[str, set[str]]) -> tuple[str, ...]:
    remaining = {step_id: set(values) for step_id, values in dependencies.items()}
    schedule: list[str] = []
    while remaining:
        ready = sorted(step_id for step_id, deps in remaining.items() if not deps)
        if not ready:
            raise InterpValidationError("recipe_cycle_detected")
        for step_id in ready:
            schedule.append(step_id)
            del remaining[step_id]
        for deps in remaining.values():
            deps.difference_update(ready)
    return tuple(schedule)


def _receipt(
    *,
    root_invocation_id: str,
    request_fingerprint: str,
    plan: _Plan,
    input_commitment: str,
    output_values: Mapping[str, Any],
    output_commitment: str | None,
    trace: Sequence[Mapping[str, Any]],
    completed_at: str,
    outcome_status: str,
    outcome_reason: str | None,
) -> dict[str, Any]:
    trace_id = _digest_domain(
        "ilc.sufficiency.local-trace.v0",
        _canonical_json(
            {
                "root_invocation_id": root_invocation_id,
                "schedule_digest": plan.schedule_digest,
            }
        ),
    )
    return {
        "schema_version": "sufficiency_local_execution_receipt_v0",
        "root_invocation_id": root_invocation_id,
        "canonical_request_fingerprint": request_fingerprint,
        "recipe_id": plan.recipe_id,
        "occurrence_path": {
            "root_invocation_id": root_invocation_id,
            "parent_frames": [],
            "leaf_recipe_id": plan.recipe_id,
            "leaf_step_id": "$recipe",
            "leaf_occurrence_index": 0,
        },
        "schedule_digest": plan.schedule_digest,
        "input_commitment": input_commitment,
        "output_commitment": output_commitment,
        "output_values": copy.deepcopy(dict(output_values)),
        "lifecycle_transitions": ["prepared", "completed"],
        "lifecycle_state": "completed",
        "outcome_status": outcome_status,
        "outcome_reason": outcome_reason,
        "trace_id": trace_id,
        "trace": copy.deepcopy(list(trace)),
        "completed_at": completed_at,
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "execution_profile": EXECUTION_PROFILE,
        "execution_scope": "local_fixture",
        "graph_materialization_status": "local_only",
        "canonical_genesis_lineage": "local_only_not_applicable",
        "economic_attribution_status": "not_evaluated",
        "reputation_status": "not_evaluated",
    }


def _canonical_json(value: object) -> bytes:
    _validate_json_value(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest_domain(domain: str, payload: bytes) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + payload).hexdigest()


def _validate_json_value(value: object) -> None:
    count = 0

    def walk(item: object, depth: int) -> None:
        nonlocal count
        count += 1
        if count > MAX_VALUE_NODES:
            raise InterpResourceError("canonical_value_node_limit_exceeded")
        if depth > MAX_VALUE_DEPTH:
            raise InterpResourceError("canonical_value_depth_limit_exceeded")
        if item is None or type(item) is bool:
            return
        if type(item) is int:
            if abs(item) > MAX_INTEGER_MAGNITUDE:
                raise InterpResourceError("canonical_integer_limit_exceeded")
            return
        if type(item) is str:
            if len(item) > MAX_STRING_LENGTH:
                raise InterpResourceError("canonical_string_limit_exceeded")
            return
        if type(item) is list:
            if len(item) > MAX_COLLECTION_ITEMS:
                raise InterpResourceError("canonical_collection_limit_exceeded")
            for child in item:
                walk(child, depth + 1)
            return
        if type(item) is dict:
            if len(item) > MAX_COLLECTION_ITEMS:
                raise InterpResourceError("canonical_collection_limit_exceeded")
            for key, child in item.items():
                if type(key) is not str:
                    raise InterpValidationError("canonical_map_key_type_invalid")
                if len(key) > MAX_STRING_LENGTH:
                    raise InterpResourceError("canonical_string_limit_exceeded")
                walk(child, depth + 1)
            return
        raise InterpValidationError("canonical_value_type_invalid")

    walk(value, 0)


def _require_exact_keys(
    value: Mapping[str, Any], expected: frozenset[str], label: str
) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        if missing:
            raise InterpValidationError(f"{label}_required_field_missing:{missing[0]}")
        raise InterpValidationError(f"{label}_unknown_field:{unknown[0]}")


def _require_identifier(value: object, label: str) -> None:
    if type(value) is not str or not value or len(value) > MAX_IDENTIFIER_LENGTH:
        raise InterpValidationError(f"{label}_invalid")


def _require_nonnegative_int(value: object, label: str) -> None:
    if type(value) is not int or value < 0:
        raise InterpValidationError(f"{label}_invalid")


def _validate_timestamp(value: str) -> None:
    if type(value) is not str or not value.endswith("Z"):
        raise InterpValidationError("completed_at_invalid")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise InterpValidationError("completed_at_invalid") from exc
