"""
Tests for ILC Governance Record Validator.
"""
from pathlib import Path
from ilc_core.protocol.ilc_governance_record_validate import validate_governance_record

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_valid_gov_record_fixture():
    path = FIXTURE_DIR / "gov_record_valid_v0.1.json"
    result = validate_governance_record(path)
    assert result["ok"] is True
    assert result["errors"] == []

def test_invalid_gov_record_signatures():
    path = FIXTURE_DIR / "gov_record_invalid_signature_v0.1.json"
    result = validate_governance_record(path)
    assert result["ok"] is False
    # Expecting minItems violation or missing signature field if items are empty/bad
    # The fixture has "signatures": []
    # This triggers minItems because schema says minItems: 1
    assert "schema_violation:minItems" in str(result["errors"])
    # Or specifically "schema_violation:minItems:signatures" based on my logic?
    # My logic: errors.append(_err("schema_violation:minItems", path))
    # where path would be "signatures"
    assert "schema_violation:minItems:signatures" in result["errors"]

def test_missing_signature_fields():
    # Construct record with signature missing key_id
    obj = {
        "protocol_version": "v0.1",
        "gov_record_id": "a" * 64,
        "timestamp": "2026-02-09T16:00:00Z",
        "proposal_id": "b" * 64,
        "state": "finalized",
        "payload": {},
        "signatures": [
            {
                # "key_id": "missing",
                "sig_alg": "ed25519",
                "signature": "c" * 64,
                "signed_at": "2026-02-09T15:55:00Z"
            }
        ]
    }
    res = validate_governance_record(obj)
    assert res["ok"] is False
    # key_id is required in signature object
    assert any("schema_violation:missing_field:key_id" in e for e in res["errors"])

def test_invalid_enum_state():
    obj = {
        "protocol_version": "v0.1",
        "gov_record_id": "a" * 64,
        "timestamp": "2026-02-09T16:00:00Z",
        "proposal_id": "b" * 64,
        "state": "draft", # Invalid
        "payload": {},
        "signatures": [{
             "key_id": "k", "sig_alg": "ed25519", "signature": "s", "signed_at": "t"
        }]
    }
    res = validate_governance_record(obj)
    assert res["ok"] is False
    assert "value_violation:invalid_enum:state" in res["errors"]


def test_governance_invalid_json_error_code_is_stable(tmp_path):
    path = tmp_path / "bad_gov.json"
    path.write_text("{not-json", encoding="utf-8")
    res = validate_governance_record(path)
    assert res["ok"] is False
    assert res["errors"] == ["invalid_json"]


def test_governance_non_dict_input_rejected():
    res = validate_governance_record(["not", "an", "object"])
    assert res["ok"] is False
    assert res["errors"] == ["schema_violation:invalid_type:root"]
