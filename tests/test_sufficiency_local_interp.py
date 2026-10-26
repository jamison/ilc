from __future__ import annotations

import copy

import pytest

import ilc_core.sufficiency.local_interp as local_interp
from ilc_core.sufficiency.local_interp import (
    EXECUTION_PROFILE,
    MAX_STEPS,
    RECIPE_SCHEMA_VERSION,
    InterpExecutionError,
    InterpGapError,
    InterpGuardError,
    InterpReplayError,
    InterpResourceError,
    InterpValidationError,
    LocalFixtureStore,
    OperationDefinition,
    execute_recipe,
)


COMPLETED_AT = "2026-10-22T12:00:00Z"


def _operations(calls: list[tuple[str, tuple[int, int]]] | None = None):
    calls = calls if calls is not None else []

    def multiply(left: int, right: int):
        calls.append(("multiply", (left, right)))
        return {"square": left * right}

    def add(left: int, right: int):
        calls.append(("add", (left, right)))
        return {"result": left + right}

    def subtract(left: int, right: int):
        calls.append(("subtract", (left, right)))
        return {"result": left - right}

    roles = (("left", 0), ("right", 1))
    return (
        OperationDefinition(
            "multiply", "1", "fixture:multiply:v1", roles, ("square",), multiply
        ),
        OperationDefinition("add", "1", "fixture:add:v1", roles, ("result",), add),
        OperationDefinition(
            "subtract", "1", "fixture:subtract:v1", roles, ("result",), subtract
        ),
    )


def _recipe(*, final_operation: str = "add", reverse_final: bool = False):
    final_impl = f"fixture:{final_operation}:v1"
    final_refs = ("input:b", "value:square") if reverse_final else ("value:square", "input:b")
    return {
        "schema_version": RECIPE_SCHEMA_VERSION,
        "recipe_version": "r1",
        "execution_profile": EXECUTION_PROFILE,
        "inputs": [
            {"name": "x", "type": "integer"},
            {"name": "b", "type": "integer"},
        ],
        "steps": [
            {
                "step_id": "square",
                "operation_ref": {
                    "operation_id": "multiply",
                    "operation_version": "1",
                    "implementation_ref": "fixture:multiply:v1",
                },
                "bindings": [
                    {"role_name": "left", "ordinal": 0, "value_ref": "input:x"},
                    {"role_name": "right", "ordinal": 1, "value_ref": "input:x"},
                ],
                "outputs": ["square"],
                "effects": [],
            },
            {
                "step_id": "offset",
                "operation_ref": {
                    "operation_id": final_operation,
                    "operation_version": "1",
                    "implementation_ref": final_impl,
                },
                "bindings": [
                    {"role_name": "left", "ordinal": 0, "value_ref": final_refs[0]},
                    {"role_name": "right", "ordinal": 1, "value_ref": final_refs[1]},
                ],
                "outputs": ["result"],
                "effects": [],
            },
        ],
        "outputs": [{"name": "y", "value_ref": "value:result"}],
        "effects": [],
        "limits": {"expanded_steps": 2},
    }


def _execute(store, recipe=None, *, invocation="fixture:invocation:1", inputs=None):
    return execute_recipe(
        store=store,
        recipe=recipe or _recipe(),
        inputs=inputs or {"x": 3, "b": 2},
        root_invocation_id=invocation,
        completed_at=COMPLETED_AT,
    )


def test_r1_happy_path_and_receipt_contract():
    calls = []
    receipt = _execute(LocalFixtureStore(_operations(calls)))

    assert receipt["output_values"] == {"y": 11}
    assert calls == [("multiply", (3, 3)), ("add", (9, 2))]
    assert receipt["lifecycle_transitions"] == ["prepared", "completed"]
    assert receipt["lifecycle_state"] == "completed"
    assert receipt["outcome_status"] == "succeeded"
    assert receipt["execution_scope"] == "local_fixture"
    assert receipt["graph_materialization_status"] == "local_only"
    assert receipt["canonical_genesis_lineage"] == "local_only_not_applicable"
    assert len(receipt["trace"]) == 2


def test_repeated_operand_preserves_binding_multiplicity():
    calls = []
    _execute(LocalFixtureStore(_operations(calls)))
    assert calls[0] == ("multiply", (3, 3))


@pytest.mark.parametrize(
    ("recipe", "expected"),
    [
        (_recipe(final_operation="subtract"), 7),
        (_recipe(final_operation="subtract", reverse_final=True), -7),
    ],
)
def test_ordered_bindings_change_noncommutative_result(recipe, expected):
    receipt = _execute(LocalFixtureStore(_operations()), recipe)
    assert receipt["output_values"]["y"] == expected


def test_unknown_operation_fails_before_any_handler_runs():
    calls = []
    recipe = _recipe()
    recipe["steps"][1]["operation_ref"]["operation_id"] = "unknown"
    with pytest.raises(InterpGapError, match="operation_unavailable"):
        _execute(LocalFixtureStore(_operations(calls)), recipe)
    assert calls == []


def test_cycle_fails_before_any_handler_runs():
    calls = []
    recipe = _recipe()
    recipe["steps"][0]["bindings"][0]["value_ref"] = "value:result"
    with pytest.raises(InterpValidationError, match="recipe_cycle_detected"):
        _execute(LocalFixtureStore(_operations(calls)), recipe)
    assert calls == []


def test_missing_dependency_fails_before_any_handler_runs():
    calls = []
    recipe = _recipe()
    recipe["steps"][1]["bindings"][0]["value_ref"] = "value:not-present"
    with pytest.raises(InterpValidationError, match="recipe_step_dependency_missing"):
        _execute(LocalFixtureStore(_operations(calls)), recipe)
    assert calls == []


def test_duplicate_binding_coordinate_is_rejected():
    recipe = _recipe()
    recipe["steps"][0]["bindings"][1] = copy.deepcopy(recipe["steps"][0]["bindings"][0])
    with pytest.raises(InterpValidationError, match="recipe_binding_coordinate_duplicate"):
        _execute(LocalFixtureStore(_operations()), recipe)


def test_expanded_step_limit_is_checked_before_execution():
    calls = []
    recipe = _recipe()
    recipe["limits"]["expanded_steps"] = MAX_STEPS + 1
    with pytest.raises(InterpResourceError, match="recipe_steps_limit_exceeded"):
        _execute(LocalFixtureStore(_operations(calls)), recipe)
    assert calls == []


def test_required_and_unknown_fields_fail_closed():
    missing = _recipe()
    del missing["effects"]
    with pytest.raises(InterpValidationError, match="recipe_required_field_missing:effects"):
        _execute(LocalFixtureStore(_operations()), missing)

    unknown = _recipe()
    unknown["authority"] = "invented"
    with pytest.raises(InterpValidationError, match="recipe_unknown_field:authority"):
        _execute(LocalFixtureStore(_operations()), unknown)


def test_invalid_binding_container_is_rejected():
    recipe = _recipe()
    recipe["steps"][0]["bindings"] = {}
    with pytest.raises(InterpValidationError, match="recipe_bindings_invalid"):
        _execute(LocalFixtureStore(_operations()), recipe)


def test_default_off_guard_precedes_recipe_parsing():
    with pytest.raises(InterpGuardError, match="sufficiency_local_interp_not_enabled") as exc:
        execute_recipe(
            store=object(),
            recipe={"malformed": True},
            inputs={},
            root_invocation_id="fixture:guarded",
        )
    assert exc.value.receipt is None


def test_local_fixture_subclass_does_not_inherit_capability():
    class UntrustedStore(LocalFixtureStore):
        pass

    with pytest.raises(InterpGuardError, match="sufficiency_local_interp_not_enabled"):
        _execute(UntrustedStore(_operations()))


def test_replay_is_idempotent_and_returns_defensive_copy():
    calls = []
    store = LocalFixtureStore(_operations(calls))
    first = _execute(store)
    first["output_values"]["y"] = 999
    second = _execute(store)
    assert second["output_values"] == {"y": 11}
    assert calls == [("multiply", (3, 3)), ("add", (9, 2))]


def test_replay_collision_is_rejected():
    store = LocalFixtureStore(_operations())
    _execute(store)
    with pytest.raises(InterpReplayError, match="invocation_id_request_fingerprint_collision"):
        _execute(store, inputs={"x": 4, "b": 2})


def test_occurrence_identity_and_schedule_are_deterministic():
    receipt = _execute(LocalFixtureStore(_operations()))
    paths = [item["occurrence_path"] for item in receipt["trace"]]
    assert [item["leaf_step_id"] for item in paths] == ["square", "offset"]
    assert [item["leaf_occurrence_index"] for item in paths] == [0, 1]
    assert all(item["parent_frames"] == [] for item in paths)


def test_schedule_digest_ignores_mapping_insertion_order():
    recipe = _recipe()
    reordered = copy.deepcopy(recipe)
    reordered = {key: reordered[key] for key in reversed(list(reordered))}
    reordered["steps"] = [
        {key: step[key] for key in reversed(list(step))} for step in reordered["steps"]
    ]
    one = _execute(LocalFixtureStore(_operations()), recipe, invocation="fixture:one")
    two = _execute(LocalFixtureStore(_operations()), reordered, invocation="fixture:two")
    assert one["recipe_id"] == two["recipe_id"]
    assert one["schedule_digest"] == two["schedule_digest"]
    assert one["output_commitment"] == two["output_commitment"]


def test_operation_output_contract_failure_has_sealed_rejection_receipt():
    operation = OperationDefinition(
        "multiply",
        "1",
        "fixture:multiply:v1",
        (("left", 0), ("right", 1)),
        ("square",),
        lambda left, right: {"wrong": left * right},
    )
    store = LocalFixtureStore((operation, *_operations()[1:]))
    with pytest.raises(InterpExecutionError, match="operation_output_set_mismatch") as exc:
        _execute(store)
    assert exc.value.receipt["outcome_status"] == "rejected"
    assert exc.value.receipt["outcome_reason"] == "operation_output_set_mismatch"
    replayed = _execute(store)
    assert replayed == exc.value.receipt


def test_handler_failure_has_sealed_rejection_receipt():
    def fail(left, right):
        raise RuntimeError("fixture failure")

    operation = OperationDefinition(
        "multiply",
        "1",
        "fixture:multiply:v1",
        (("left", 0), ("right", 1)),
        ("square",),
        fail,
    )
    store = LocalFixtureStore((operation, *_operations()[1:]))
    with pytest.raises(InterpExecutionError, match="operation_execution_failed") as exc:
        _execute(store)
    assert exc.value.receipt["outcome_status"] == "rejected"
    assert exc.value.receipt["output_commitment"] is None


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda value: value["inputs"].append({"name": "f", "type": "float"}), "recipe_input_type_invalid"),
        (lambda value: value["steps"][0]["bindings"].append(("bad",)), "canonical_value_type_invalid"),
        (lambda value: value["limits"].update({"expanded_steps": True}), "expanded_steps_invalid"),
        (lambda value: value.update({"recipe_version": "x" * 4097}), "canonical_string_limit_exceeded"),
    ],
)
def test_strict_boundary_rejects_unsupported_values(mutation, error):
    recipe = _recipe()
    mutation(recipe)
    with pytest.raises((InterpValidationError, InterpResourceError), match=error):
        _execute(LocalFixtureStore(_operations()), recipe)


def test_integer_type_does_not_accept_boolean():
    with pytest.raises(InterpValidationError, match="invocation_input_type_mismatch"):
        _execute(LocalFixtureStore(_operations()), inputs={"x": True, "b": 2})


def test_operation_definition_requires_contiguous_role_ordinals():
    with pytest.raises(InterpValidationError, match="operation_role_ordinals_noncontiguous"):
        OperationDefinition(
            "bad",
            "1",
            "fixture:bad:v1",
            (("left", 0), ("right", 2)),
            ("result",),
            lambda left, right: {"result": left + right},
        )


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("roles", [["left", 0]], "operation_roles_type_invalid"),
        ("output_names", ["result"], "operation_outputs_type_invalid"),
        ("permitted_effects", [], "operation_effects_type_invalid"),
    ],
)
def test_operation_definition_contract_collections_are_immutable(field, value, error):
    kwargs = {
        "operation_id": "immutable",
        "operation_version": "1",
        "implementation_ref": "fixture:immutable:v1",
        "roles": (("left", 0),),
        "output_names": ("result",),
        "handler": lambda left: {"result": left},
        "permitted_effects": (),
    }
    kwargs[field] = value
    with pytest.raises(InterpValidationError, match=error):
        OperationDefinition(**kwargs)


def test_empty_completed_at_is_rejected_instead_of_replaced():
    with pytest.raises(InterpValidationError, match="completed_at_invalid"):
        execute_recipe(
            store=LocalFixtureStore(_operations()),
            recipe=_recipe(),
            inputs={"x": 3, "b": 2},
            root_invocation_id="fixture:empty-timestamp",
            completed_at="",
        )


def test_operation_registry_is_bounded(monkeypatch):
    monkeypatch.setattr(local_interp, "MAX_REGISTERED_OPERATIONS", 1)
    store = LocalFixtureStore((_operations()[0],))
    with pytest.raises(InterpResourceError, match="operation_registry_limit_exceeded"):
        store.register_operation(_operations()[1])


def test_replay_receipt_store_is_bounded(monkeypatch):
    monkeypatch.setattr(local_interp, "MAX_REPLAY_RECEIPTS", 1)
    store = LocalFixtureStore(_operations())
    _execute(store, invocation="fixture:first")
    with pytest.raises(InterpResourceError, match="replay_receipt_limit_exceeded"):
        _execute(store, invocation="fixture:second")


def test_full_replay_store_rejects_before_handlers_run(monkeypatch):
    monkeypatch.setattr(local_interp, "MAX_REPLAY_RECEIPTS", 1)
    calls = []
    store = LocalFixtureStore(_operations(calls))
    _execute(store, invocation="fixture:first")
    calls.clear()
    with pytest.raises(InterpResourceError, match="replay_receipt_limit_exceeded"):
        _execute(store, invocation="fixture:second")
    assert calls == []
