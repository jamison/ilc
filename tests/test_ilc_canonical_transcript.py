"""
Tests for ILC Canonical Transcript Validator.
"""
from pathlib import Path
from ilc_core.protocol.ilc_transcript_validate import validate_transcript

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_valid_transcript_fixture():
    path = FIXTURE_DIR / "transcript_valid_v0.1.json"
    result = validate_transcript(path)
    assert result["ok"] is True
    assert result["errors"] == []

def test_invalid_order_transcript():
    path = FIXTURE_DIR / "transcript_invalid_order_v0.1.json"
    result = validate_transcript(path)
    assert result["ok"] is False
    assert "ordering_violation:records" in result["errors"]

def test_manual_ordering_check():
    # Construct minimally valid transcript but with wrong order
    # Order rule: timestamp, event_kind, event_id
    r1 = {
        "protocol_version": "v0.1",
        "event_id": "a" * 64,
        "timestamp": "2026-02-09T14:02:00Z", # Later
        "event_kind": "claim",
        "agent_id": "agent-A",
        "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    r2 = {
        "protocol_version": "v0.1",
        "event_id": "b" * 64,
        "timestamp": "2026-02-09T14:01:00Z", # Earlier
        "event_kind": "claim",
        "agent_id": "agent-B",
        "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    
    obj = {
        "protocol_version": "v0.1",
        "transcript_id": "a" * 64,
        "previous_transcript_id": "0" * 64,
        "timestamp_start": "2026-02-09T14:00:00Z",
        "timestamp_end": "2026-02-09T15:00:00Z",
        "records": [r1, r2] # Unsorted by timestamp
    }
    res = validate_transcript(obj)
    assert res["ok"] is False
    assert "ordering_violation:records" in res["errors"]

    # Fix order
    obj["records"] = [r2, r1]
    res = validate_transcript(obj)
    assert res["ok"] is True

def test_missing_root_hash():
    obj = {
        "protocol_version": "v0.1",
        # "transcript_id": missing
        "previous_transcript_id": "0" * 64,
        "timestamp_start": "2026-02-09T14:00:00Z",
        "timestamp_end": "2026-02-09T15:00:00Z",
        "records": []
    }
    res = validate_transcript(obj)
    assert res["ok"] is False
    # Check for missing field error
    assert any("missing_field:transcript_id" in e for e in res["errors"])


def test_record_must_validate_as_wire_or_receipt():
    # Passes transcript oneOf (has wire-like required fields) but fails
    # strict wire/receipt validators due to malformed payload.
    obj = {
        "protocol_version": "v0.1",
        "transcript_id": "a" * 64,
        "previous_transcript_id": "0" * 64,
        "timestamp_start": "2026-02-09T14:00:00Z",
        "timestamp_end": "2026-02-09T15:00:00Z",
        "records": [
            {
                "protocol_version": "v0.1",
                "event_id": "not-a-hash",
                "timestamp": "2026-02-09T14:01:00Z",
                "event_kind": "claim"
            }
        ]
    }
    res = validate_transcript(obj)
    assert res["ok"] is False
    assert "context_violation:record_not_wire_or_receipt:0" in res["errors"]


def test_receipt_record_is_accepted_in_transcript():
    obj = {
        "protocol_version": "v0.1",
        "transcript_id": "a" * 64,
        "previous_transcript_id": "0" * 64,
        "timestamp_start": "2026-02-09T14:00:00Z",
        "timestamp_end": "2026-02-09T15:00:00Z",
        "records": [
            {
                "protocol_version": "v0.1",
                "receipt_id": "d" * 64,
                "timestamp": "2026-02-09T14:01:00Z",
                "related_claim_id": "a" * 64,
                "outcome": "valid",
                "payouts": []
            }
        ]
    }
    res = validate_transcript(obj)
    assert res["ok"] is True
    assert res["errors"] == []


def test_transcript_invalid_json_error_code_is_stable(tmp_path):
    path = tmp_path / "bad_transcript.json"
    path.write_text("{not-json", encoding="utf-8")
    res = validate_transcript(path)
    assert res["ok"] is False
    assert res["errors"] == ["invalid_json"]


def test_transcript_non_dict_input_rejected():
    res = validate_transcript(["not", "an", "object"])
    assert res["ok"] is False
    assert res["errors"] == ["schema_violation:invalid_type:root"]
