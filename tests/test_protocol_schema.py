from ilc_core.protocol.schema import load_protocol_schema


def test_protocol_schema_has_core_objects():
    schema = load_protocol_schema()
    assert schema["version"].startswith("0.")
    objects = schema["objects"]

    # Check core surfaces exist
    for key in ["claim", "refute", "task", "task_outcome", "epoch_summary"]:
        assert key in objects
        assert isinstance(objects[key]["fields"], dict)

    # Check specific fields for task_outcome
    outcome_fields = objects["task_outcome"]["fields"]
    assert "stake_spent" in outcome_fields
    assert "reward_paid" in outcome_fields

    # Check specific fields for epoch_summary
    epoch_fields = objects["epoch_summary"]["fields"]
    assert "clearing_price_ilc_per_ecu" in epoch_fields
