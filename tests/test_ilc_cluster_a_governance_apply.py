"""
Tests for Phase 138: Cluster A Governance Application & Signature Verification.
"""
import pytest
import json
import time
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.protocol.ilc_cluster_a_ingest import (
    apply_governance_record,
    canonical_governance_payload_bytes
)

# --- Helpers ---

def generate_keypair() -> Tuple[bytes, bytes, str]:
    """Generate (private_bytes, public_bytes, hex_signature_of_dummy)"""
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key().public_bytes_raw()
    priv_bytes = priv.private_bytes_raw()
    return priv_bytes, pub, priv # Return object for signing

def sign(priv_key_obj, payload_bytes: bytes) -> str:
    return priv_key_obj.sign(payload_bytes).hex()

# --- Fixtures ---

@pytest.fixture
def clean_policy_state():
    return {
        "proposals": {},     # proposal_id -> state
        "known_records": {}  # gov_record_id -> policy_hash
    }

@pytest.fixture
def key_context():
    # Key A
    priv_a, pub_a, obj_a = generate_keypair()
    # Key B
    priv_b, pub_b, obj_b = generate_keypair()
    
    keyring = {
        "key_a": pub_a,
        "key_b": pub_b
    }
    
    signers = {
        "key_a": obj_a,
        "key_b": obj_b
    }
    return keyring, signers

# --- Tests ---


def test_apply_requires_verification_context(clean_policy_state):
    """H1 / H2: Missing keyring must hard fail."""
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64, # Valid hex
        # event_kind removed (forbidden)
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"foo": "bar"},
        # Must have at least one signature to pass schema minItems: 1
        "signatures": [{"key_id": "k", "sig_alg": "ed25519", "signature": "a"*64, "signed_at": "2023-01-01T00:00:00Z"}]
    }
    res = apply_governance_record(
        record, 
        current_policy_state=clean_policy_state,
        governance_keyring=None # Explicit None
    )
    assert res["ok"] is False
    assert "context_violation:missing_signature_verification_context" in res["errors"]

def test_apply_valid_signature(clean_policy_state, key_context):
    """H1: Valid signature and context -> Success."""
    keyring, signers = key_context
    
    # Create record
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64, # Valid hex
        # event_kind removed
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"param": "value_1"},
        "signatures": [] 
    }
    
    # Canonicalize and sign
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_hex = sign(signers["key_a"], payload_bytes)
    
    # Attach signature
    record["signatures"].append({
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_hex,
        "signed_at": "2023-01-01T00:00:00Z"
    })
    
    res = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring,
        min_valid_signatures=1
    )
    
    # Debug: if failed, print errors
    assert res["ok"] is True, f"Errors: {res.get('errors')}"
    assert res["data"]["proposal_id"] == "b"*64
    assert res["data"]["new_state"] == "proposed"
    assert res["data"]["verified_signers"] == ["key_a"]
    assert res["warnings"] == ["known_records_hash_mode_defaulted_to_record_digest_v1"]
    assert res["data"]["known_records_hash_mode_effective"] == "record_digest_v1"
    assert res["data"]["policy_state_delta"]["proposals"]["b"*64] == "proposed"
    assert res["data"]["policy_state_delta"]["known_records"]["a"*64] == res["data"]["record_digest"]
    assert res["data"]["policy_state_delta"]["known_records_hash_mode"] == "record_digest_v1"

def test_apply_fails_invalid_signature_hex(clean_policy_state, key_context):
    """H2: Invalid hex or length -> hard fail or specific error."""
    keyring, _ = key_context
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "b"*64,
        "proposal_id": "c"*64, # Valid hex
        # event_kind removed
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": [{
            "key_id": "key_a",
            "sig_alg": "ed25519",
            "signature": "not_hex_ZZZ", # Invalid format
            "signed_at": "2023-01-01T00:00:00Z"
        }]
    }
    
    res = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring
    )
    assert res["ok"] is False
    # If schema validation catches it (regex), we get value_violation:invalid_format
    # If schema passes (unlikely for strict schema), we get value_violation:invalid_signature_hex
    # We accept either.
    errors = res["errors"]
    has_format_error = any("value_violation:invalid_format" in e for e in errors)
    has_hex_error = any("value_violation:invalid_signature_hex" in e for e in errors)
    assert has_format_error or has_hex_error, f"Got: {errors}"

def test_apply_fails_tampered_payload(clean_policy_state, key_context):
    """H1: Signature verification must fail if payload modified."""
    keyring, signers = key_context
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "c"*64,
        "proposal_id": "d"*64, # Valid hex
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"val": 100},
        "signatures": [] 
    }
    
    # Sign ORIGINAL
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_hex = sign(signers["key_a"], payload_bytes)
    
    # Modify record
    record["payload"]["val"] = 200 # TAMPER!
    
    record["signatures"].append({
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_hex,
        "signed_at": "2023-01-01T00:00:00Z"
    })
    
    
    res = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring
    )
    
    assert res["ok"] is False
    assert "context_violation:signature_verification_failed" in res["errors"]
    # Verify detail side-channel if available
    details = res.get("error_details", [])
    assert any(d["code"] == "context_violation:signature_verification_failed" and d["key_id"] == "key_a" for d in details)


def test_apply_fails_unknown_key(clean_policy_state, key_context):
    """H2: Unknown key_id -> fail."""
    keyring, _ = key_context
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "d"*64,
        "proposal_id": "e"*64, # Valid hex
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": [{
            "key_id": "key_unknown_xcv",
            "sig_alg": "ed25519",
            "signature": "a"*128, # valid hex/len, but unknown key
            "signed_at": "2023-01-01T00:00:00Z"
        }]
    }
    
    res = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring
    )
    assert res["ok"] is False
    assert "context_violation:unknown_signing_key" in res["errors"]
    # Verify dynamic context moved to details
    details = res.get("error_details", [])
    assert any(d["code"] == "context_violation:unknown_signing_key" and d["key_id"] == "key_unknown_xcv" for d in details)

def test_apply_fails_unsupported_alg(clean_policy_state, key_context):
    """H2: Unsupported algorithm -> fail."""
    keyring, _ = key_context
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "e"*64,
        "proposal_id": "f"*64, # Valid hex
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": [{
            "key_id": "key_a",
            "sig_alg": "secp256k1", # Only ed25519 supported
            "signature": "a"*128,
            "signed_at": "2023-01-01T00:00:00Z"
        }]
    }
    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res["ok"] is False
    assert "context_violation:unsupported_sig_alg" in res["errors"]
    details = res.get("error_details", [])
    assert any(d["code"] == "context_violation:unsupported_sig_alg" and d["alg"] == "secp256k1" for d in details)

def test_apply_multisig_threshold(clean_policy_state, key_context):
    """H1: Must meet min_valid_signatures threshold."""
    keyring, signers = key_context
    min_sigs = 2
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "f"*64,
        "proposal_id": "0"*64, # Valid hex
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": [] 
    }
    
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_a = sign(signers["key_a"], payload_bytes)
    
    # 1. Provide only 1 signature (Key A)
    record["signatures"] = [{
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_a,
        "signed_at": "2023-01-01T00:00:00Z"
    }]
    
    res = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring,
        min_valid_signatures=min_sigs
    )
    assert res["ok"] is False
    assert "context_violation:no_valid_signatures" in res["errors"] # Failed threshold

    # 2. Provide 2 signatures (Key A + Key B)
    sig_b = sign(signers["key_b"], payload_bytes)
    record["signatures"].append({
        "key_id": "key_b",
        "sig_alg": "ed25519",
        "signature": sig_b,
        "signed_at": "2023-01-01T00:00:00Z"
    })
    
    res2 = apply_governance_record(
        record,
        current_policy_state=clean_policy_state,
        governance_keyring=keyring,
        min_valid_signatures=min_sigs
    )
    assert res2["ok"] is True
    assert "key_a" in res2["data"]["verified_signers"]
    assert "key_b" in res2["data"]["verified_signers"]

def test_apply_identity_conflict_on_metadata_change(clean_policy_state, key_context):
    """H1: Changing timestamp/state with same ID must fail (Identity Guard)."""
    keyring, signers = key_context
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64,
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"foo": "bar"},
        "signatures": []
    }
    
    # Sign and Apply 1st time
    pb = canonical_governance_payload_bytes(record)
    sig = sign(signers["key_a"], pb)
    record["signatures"].append({
        "key_id": "key_a", "sig_alg": "ed25519", "signature": sig, "signed_at": "2023-01-01T00:00:00Z"
    })
    
    res1 = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res1["ok"] is True
    
    # Update state with result
    clean_policy_state["known_records"][record["gov_record_id"]] = res1["data"]["record_digest"]
    clean_policy_state["known_records_hash_mode"] = "record_digest_v1" # Enforce v1
    
    # Create conflicting record (same ID, same payload, DIFFERENT timestamp)
    record_conflict = record.copy()
    record_conflict["timestamp"] = "2023-01-02T00:00:00Z" # Changed!
    record_conflict["signatures"] = []
    
    # Sign conflicting record
    pb2 = canonical_governance_payload_bytes(record_conflict)
    sig2 = sign(signers["key_a"], pb2)
    record_conflict["signatures"].append({
        "key_id": "key_a", "sig_alg": "ed25519", "signature": sig2, "signed_at": "2023-01-02T00:00:00Z"
    })
    
    res2 = apply_governance_record(record_conflict, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res2["ok"] is False
    # Must fail with digest conflict, NOT hash conflict (payload is same)
    assert "context_violation:gov_record_id_record_digest_conflict" in res2["errors"]

def test_apply_legacy_mode_payload_hash_fallback(clean_policy_state, key_context):
    """H1 Legacy: If legacy mode, checks payload hash only."""
    keyring, signers = key_context
    
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64, 
        "proposal_id": "b"*64,
        "state": "proposed",
        "timestamp": "2020-01-01T00:00:00Z",
        "payload": {"legacy": True},
        "signatures": []
    }
    
    # Manually inject legacy state
    # Legacy stored payload hash of {"legacy": True}
    from ilc_core.protocol.ilc_cluster_a_ingest import _calc_policy_snapshot
    ph = _calc_policy_snapshot(record["payload"])["policy_hash"]
    
    clean_policy_state["known_records"][record["gov_record_id"]] = ph
    clean_policy_state["known_records_hash_mode"] = "payload_hash_v0" # Explicit legacy
    
    # Sign it (verification still required in Phase 138+)
    pb = canonical_governance_payload_bytes(record)
    sig = sign(signers["key_a"], pb)
    record["signatures"].append({
        "key_id": "key_a", "sig_alg": "ed25519", "signature": sig, "signed_at": "2020-01-01T00:00:00Z"
    })
    
    # Apply same record -> Should pass (idempotent on payload hash)
    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res["ok"] is True, f"Failed with errors: {res.get('errors')}"
    
    # Create conflicting metadata (same payload)
    record_conflict = record.copy()
    record_conflict["timestamp"] = "2024-01-01T00:00:00Z" # Changed
    record_conflict["signatures"] = []
    
    # Sign
    pb2 = canonical_governance_payload_bytes(record_conflict)
    sig2 = sign(signers["key_a"], pb2)
    record_conflict["signatures"].append({
        "key_id": "key_a", "sig_alg": "ed25519", "signature": sig2, "signed_at": "2024-01-01T00:00:00Z"
    })
    
    # Apply -> Should PASS in legacy mode because payload hash matches! 
    # (This confirms we are respecting legacy mode for existing records)
    res2 = apply_governance_record(record_conflict, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res2["ok"] is True 
    assert res2["data"]["known_records_hash_mode_effective"] == "payload_hash_v0"

def test_apply_fail_closed_when_mode_missing_with_known_records(clean_policy_state, key_context):
    """Fail closed when known_records exist and mode is missing."""
    keyring, signers = key_context
    clean_policy_state["known_records"] = {"a"*64: "f"*64}
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64,
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"k": "v"},
        "signatures": [],
    }
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_hex = sign(signers["key_a"], payload_bytes)
    record["signatures"].append({
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_hex,
        "signed_at": "2023-01-01T00:00:00Z",
    })

    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res["ok"] is False
    assert "context_violation:known_records_hash_mode_required" in res["errors"]
    assert any(d.get("known_records_count") == 1 for d in (res.get("error_details") or []))

def test_apply_fail_closed_when_mode_unknown_with_known_records(clean_policy_state, key_context):
    """Fail closed when known_records mode is unknown and history exists."""
    keyring, signers = key_context
    clean_policy_state["known_records"] = {"a"*64: "f"*64}
    clean_policy_state["known_records_hash_mode"] = "mystery_mode"
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64,
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"k": "v"},
        "signatures": [],
    }
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_hex = sign(signers["key_a"], payload_bytes)
    record["signatures"].append({
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_hex,
        "signed_at": "2023-01-01T00:00:00Z",
    })

    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res["ok"] is False
    assert "context_violation:known_records_hash_mode_required" in res["errors"]
    assert any(d.get("known_records_hash_mode") == "mystery_mode" for d in (res.get("error_details") or []))

def test_apply_governance_record_is_pure_and_returns_delta(clean_policy_state, key_context):
    """apply_governance_record must not mutate input state and must return explicit state delta."""
    keyring, signers = key_context
    before = json.loads(json.dumps(clean_policy_state))
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "c"*64,
        "proposal_id": "d"*64,
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {"param": "x"},
        "signatures": [],
    }
    payload_bytes = canonical_governance_payload_bytes(record)
    sig_hex = sign(signers["key_a"], payload_bytes)
    record["signatures"].append({
        "key_id": "key_a",
        "sig_alg": "ed25519",
        "signature": sig_hex,
        "signed_at": "2023-01-01T00:00:00Z",
    })

    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"
    assert clean_policy_state == before
    delta = res["data"]["policy_state_delta"]
    assert delta["proposals"] == {"d"*64: "proposed"}
    assert delta["known_records_hash_mode"] == "record_digest_v1"
    assert delta["known_records"]["c"*64] == res["data"]["record_digest"]

def test_apply_duplicate_signer_fails(clean_policy_state, key_context):
    """M1: Duplicate signer must hard fail (Option A)."""
    keyring, signers = key_context
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "d"*64,
        "proposal_id": "e"*64, 
        "state": "proposed",
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": []
    }
    
    pb = canonical_governance_payload_bytes(record)
    sig = sign(signers["key_a"], pb)
    
    # Add SAME signature block twice (or different sigs from same key)
    # Different sigs from same key is harder to generate deterministically without nonce, 
    # but here we can just reuse the exact same signature block.
    # The check is on key_id.
    
    sig_block = {
        "key_id": "key_a", "sig_alg": "ed25519", "signature": sig, "signed_at": "2023-01-01T00:00:00Z"
    }
    record["signatures"] = [sig_block, sig_block]
    
    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring, min_valid_signatures=1)
    
    assert res["ok"] is False
    assert "context_violation:duplicate_signature_key_id" in res["errors"]
    
def test_apply_invalid_threshold(clean_policy_state, key_context):
    """M1: Invalid threshold must hard fail."""
    keyring, signers = key_context
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": "e"*64,
        "signatures": [] # Content doesn't matter much if threshold is invalid check happens early?
        # Actually validation happens in order. We must pass schema first.
    }
    # Minimal valid record for schema
    record.update({
        "proposal_id": "e"*64,
        "state": "proposed", 
        "timestamp": "2023-01-01T00:00:00Z",
        "payload": {},
        "signatures": [{"key_id": "key_a", "sig_alg": "ed25519", "signature": "a"*64, "signed_at": "..."}]
    })

    # Case 1: threshold < 1
    res = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring, min_valid_signatures=0)
    assert res["ok"] is False
    assert "value_violation:invalid_min_valid_signatures" in res["errors"]
    
    # Case 2: threshold not int
    # Type hint says int, but runtime check might catch it if strict. 
    # Python doesn't enforce types at runtime unless we check.
    # In my implementation: `if not isinstance(min_valid_signatures, int) or min_valid_signatures < 1:`
    res2 = apply_governance_record(record, current_policy_state=clean_policy_state, governance_keyring=keyring, min_valid_signatures="1")
    assert res2["ok"] is False
    assert "value_violation:invalid_min_valid_signatures" in res2["errors"]

