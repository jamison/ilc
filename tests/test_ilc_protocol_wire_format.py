"""
Tests for ILC Protocol Wire Format Validator.
"""
from pathlib import Path
from ilc_core.protocol.ilc_wire_validate import validate_wire_event

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_valid_wire_fixture():
    path = FIXTURE_DIR / "wire_valid_v0.1.json"
    result = validate_wire_event(path)
    assert result["ok"] is True
    assert result["errors"] == []
    assert result["version"] == "v0.1"
    assert set(result.keys()) == {"ok", "errors", "warnings", "version"}

def test_invalid_wire_fixture_missing_field():
    path = FIXTURE_DIR / "wire_invalid_missing_field_v0.1.json"
    result = validate_wire_event(path)
    assert result["ok"] is False
    # My validator extracts missing field, check if it matches my fixture which misses content_hash or event_kind?
    # Fixture content: "content_hash": "e3..." but misses "event_kind" implied by test name in write_to_file step?
    # Let me check fixture content from Step 8.
    # Step 8: Create `wire_invalid_missing_field_v0.1.json`:
    # { "protocol_version": .. "event_kind": "claim" MISSING? No, "event_kind" was missing in the content I wrote.
    # Ah, step 17160 created it:
    # { "protocol_version": ..., "event_id": ..., "agent_id": ..., "content_hash": ... }
    # "event_kind" is missing.
    # So error should be missing_field:event_kind.
    
    # Wait, my validator logic for missing field:
    # m = re.search(r"'(.*?)' is a required property", error.message)
    # This might depend strongly on jsonschema version message format.
    # I should assert generic missing_field if I can't be sure of the string match, 
    # OR catch if my regex fails and returns "unknown".
    # But I should aim for deterministic output.
    
    errors = result["errors"]
    assert any("missing_field:event_kind" in e for e in errors)
    assert sorted(errors) == errors

def test_type_violation():
    # Construct invalid obj
    obj = {
        "protocol_version": "v0.1",
        "event_id": "a" * 64,
        "timestamp": "2026-02-09T14:30:00Z",
        "agent_id": 123, # invalid int
        "event_kind": "claim",
        "content_hash": "a" * 64
    }
    res = validate_wire_event(obj)
    assert res["ok"] is False
    assert "schema_violation:invalid_type:agent_id" in res["errors"]

def test_extra_field_rejection():
    obj = {
        "protocol_version": "v0.1",
        "event_id": "a" * 64,
        "timestamp": "2026-02-09T14:30:00Z",
        "agent_id": "agent-007",
        "event_kind": "claim",
        "content_hash": "a" * 64,
        "extra": "bad"
    }
    res = validate_wire_event(obj)
    assert res["ok"] is False
    assert "schema_violation:unknown_field:extra" in res["errors"]


def test_invalid_json_error_code_is_stable(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")
    res = validate_wire_event(path)
    assert res["ok"] is False
    assert res["errors"] == ["invalid_json"]


def test_non_dict_input_rejected():
    res = validate_wire_event(["not", "an", "object"])
    assert res["ok"] is False
    assert res["errors"] == ["schema_violation:invalid_type:root"]
