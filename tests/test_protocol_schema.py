import pytest

from ilc_core.protocol.schema import load_protocol_schema
from ilc_core.exceptions import ProtocolSchemaLoadError


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


def test_protocol_schema_missing_path_raises_domain_error(tmp_path):
    missing = tmp_path / "missing_protocol_schema.json"
    with pytest.raises(ProtocolSchemaLoadError) as exc:
        load_protocol_schema(str(missing))
    assert "protocol_schema_not_found:" in str(exc.value)


def test_protocol_schema_invalid_json_raises_domain_error(tmp_path):
    bad = tmp_path / "invalid_protocol_schema.json"
    bad.write_text("{not valid json}", encoding="utf-8")
    with pytest.raises(ProtocolSchemaLoadError) as exc:
        load_protocol_schema(str(bad))
    assert "protocol_schema_invalid_json:" in str(exc.value)
