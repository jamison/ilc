import pytest
import json
from ilc_core.protocol.ilc_cluster_a_ingest import (
    apply_governance_record,
    canonical_governance_payload_bytes,
    _resolve_known_records_hash_mode,
    ALLOWED_CODES
)
from ilc_core.protocol.ilc_governance_record_validate import validate_governance_record


@pytest.fixture
def valid_governance_record():
    return {
        "protocol_version": "v0.1",
        "gov_record_id": "a" * 64,
        "proposal_id": "b" * 64,
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"foo": "bar"},
        "signatures": [
            {
                "key_id": "key_1",
                "sig_alg": "ed25519",
                "signature": "c" * 64,  # valid hex length 64 bytes = 128 hex chars? No, signature is 64 bytes -> 128 hex chars
                "signed_at": "2023-01-01T00:00:00Z"
            }
        ]
    }

# Fix signature hex length for mock validation (schema says pattern ^[a-f0-9]+$, ingest checks len 64 bytes -> 128 hex)
# The ingest check `bytes.fromhex(sig)` needs 128 chars for 64 bytes.
# valid_governance_record signature: "c"*128

@pytest.fixture
def clean_policy_state():
    return {
        "proposals": {},
        "known_records": {},
        "known_records_hash_mode": "record_digest_v1"
    }

# --- High-1: State Shape Hardening ---

def test_apply_guards_against_invalid_state_types(valid_governance_record):
    """Verify apply_governance_record fails gracefully with schema_violation on invalid state shapes."""
    # Invalid root
    res = apply_governance_record(valid_governance_record, current_policy_state=[]) # List instead of dict
    assert res["ok"] is False
    assert "schema_violation:invalid_type:policy_state.root" in res["errors"]

    # Invalid proposals
    res = apply_governance_record(valid_governance_record, current_policy_state={"proposals": "not_a_dict"})
    assert res["ok"] is False
    assert "schema_violation:invalid_type:policy_state.proposals" in res["errors"]

    # Invalid known_records
    res = apply_governance_record(valid_governance_record, current_policy_state={"known_records": 123})
    assert res["ok"] is False
    assert "schema_violation:invalid_type:policy_state.known_records" in res["errors"]
    
    # Invalid mode
    res = apply_governance_record(valid_governance_record, current_policy_state={"known_records_hash_mode": 123})
    assert res["ok"] is False
    assert "schema_violation:invalid_type:policy_state.known_records_hash_mode" in res["errors"]


# --- High-2: Validator Strictness (Timestamp Format) ---

def test_validator_rejects_invalid_timestamp_formats(valid_governance_record):
    """Verify validator rejects non-UTC/malformed timestamps in signed_at."""
    # Good format
    assert validate_governance_record(valid_governance_record)["ok"] is True
    
    # Missing Z (offset not allowed by our regex strictness, though date-time format might allow it depending on implementation)
    # Our regex: ^\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$
    # So "2023-01-01T00:00:00" (no Z) should fail pattern
    
    rec = json.loads(json.dumps(valid_governance_record))
    rec["signatures"][0]["signed_at"] = "2023-01-01T00:00:00" 
    res = validate_governance_record(rec)
    assert res["ok"] is False
    assert any("value_violation:invalid_format" in e for e in res["errors"])

    # Offset like +00:00
    rec["signatures"][0]["signed_at"] = "2023-01-01T00:00:00+00:00"
    res = validate_governance_record(rec)
    assert res["ok"] is False
    assert any("value_violation:invalid_format" in e for e in res["errors"])

    # Record timestamp field (also strict UTC?)
    # Schema says: pattern "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$" for root timestamp too.
    rec = json.loads(json.dumps(valid_governance_record))
    rec["timestamp"] = "2023-01-01T00:00:00"
    res = validate_governance_record(rec)
    assert res["ok"] is False
    assert any("value_violation:invalid_format" in e for e in res["errors"])


# --- Medium-3: Signature Alg Consistency ---

def test_schema_rejects_secp256k1(valid_governance_record):
    """Verify secp256k1 is no longer a valid enum value."""
    rec = json.loads(json.dumps(valid_governance_record))
    rec["signatures"][0]["sig_alg"] = "secp256k1"
    
    res = validate_governance_record(rec)
    assert res["ok"] is False
    assert any("value_violation:invalid_enum" in e for e in res["errors"])


# --- Medium-4: Error Token Enforcement ---

def test_apply_emits_allowed_codes_only(valid_governance_record, clean_policy_state):
    """Verify runtime errors are within ALLOWED_CODES."""
    # We can't easily mock _emit internal check without patching, 
    # but we can trigger a known error and ensure it doesn't crash 
    # and is in the allowed list (which implies _emit passed).
    
    # Trigger unknown_signing_key
    # We need a keyring passed to trigger verify logic
    keyring = {"key_2": b"x"*32} # key_1 not in keyring
    
    # Mock signature hex to be valid length so we don't hit hex/length errors first
    valid_governance_record["signatures"][0]["signature"] = "c" * 128
    
    res = apply_governance_record(valid_governance_record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    
    assert res["ok"] is False
    assert "context_violation:unknown_signing_key" in res["errors"]
    
    # If _emit enforced it, we are good. If we used a disallowed code, _emit would raise ValueError.
    
    # Verify the constant is exposed
    assert "context_violation:unknown_signing_key" in ALLOWED_CODES
