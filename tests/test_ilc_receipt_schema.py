"""
Tests for ILC Receipt Schema Validator.
"""
from pathlib import Path
from ilc_core.protocol.ilc_receipt_validate import validate_receipt_record

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_valid_receipt_fixture():
    path = FIXTURE_DIR / "receipt_valid_v0.1.json"
    result = validate_receipt_record(path)
    assert result["ok"] is True
    assert result["errors"] == []
    assert result["version"] == "v0.1"
    assert set(result.keys()) == {"ok", "errors", "warnings", "version"}

def test_invalid_receipt_amount():
    path = FIXTURE_DIR / "receipt_invalid_amount_v0.1.json"
    result = validate_receipt_record(path)
    assert result["ok"] is False
    assert any("value_violation:invalid_format" in e for e in result["errors"])
    assert result["errors"] == sorted(result["errors"])

def test_invalid_type_receipt():
    obj = {
        "protocol_version": "v0.1",
        "receipt_id": "aa" * 32,
        "timestamp": "2026-02-09T14:30:00Z",
        "related_claim_id": "aa" * 32,
        "outcome": "valid",
        "payouts": "not_a_list"
    }
    res = validate_receipt_record(obj)
    assert res["ok"] is False
    assert "schema_violation:invalid_type:payouts" in res["errors"]

def test_unknown_field_receipt():
    obj = {
        "protocol_version": "v0.1",
        "receipt_id": "aa" * 32,
        "timestamp": "2026-02-09T14:30:00Z",
        "related_claim_id": "aa" * 32,
        "outcome": "valid",
        "payouts": [],
        "extra": "bad"
    }
    res = validate_receipt_record(obj)
    assert res["ok"] is False
    assert "schema_violation:unknown_field:extra" in res["errors"]


def test_receipt_invalid_json_error_code_is_stable(tmp_path):
    path = tmp_path / "bad_receipt.json"
    path.write_text("{not-json", encoding="utf-8")
    res = validate_receipt_record(path)
    assert res["ok"] is False
    assert res["errors"] == ["invalid_json"]


def test_receipt_non_dict_input_rejected():
    res = validate_receipt_record(["not", "an", "object"])
    assert res["ok"] is False
    assert res["errors"] == ["schema_violation:invalid_type:root"]
