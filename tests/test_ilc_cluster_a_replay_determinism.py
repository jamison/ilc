"""
Tests for ILC Cluster A Replay Determinism.
"""
import hashlib
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from ilc_core.protocol.ilc_cluster_a_ingest import apply_governance_record, canonical_governance_payload_bytes

@pytest.fixture
def key_setup():
    from cryptography.hazmat.primitives import serialization
    sk = ed25519.Ed25519PrivateKey.generate()
    vk = sk.public_key()
    
    vk_bytes = vk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    key_id = "key-1"
    # Keyring expects raw bytes, not a dict
    return sk, {key_id: vk_bytes}

def sign(sk, payload_bytes):
    signature = sk.sign(payload_bytes)
    return signature.hex()

def test_policy_hash_stability(key_setup):
    sk, keyring = key_setup
    payload = {
        "b": 2,
        "a": 1,
        "c": [3, 2, 1]
    }
    expected_canonical = '{"a":1,"b":2,"c":[3,2,1]}'
    expected_hash = hashlib.sha256(expected_canonical.encode("utf-8")).hexdigest()
    
    for _ in range(10):
        rec = {
            "protocol_version": "v0.1",
            "gov_record_id": "a"*64,
            "timestamp": "2026-02-09T20:00:00Z",
            "proposal_id": "a"*64,
            "state": "proposed",
            "payload": payload,
            "signatures": []
        }
        # Sign it
        p_bytes = canonical_governance_payload_bytes(rec)
        s_hex = sign(sk, p_bytes)
        rec["signatures"].append({
            "key_id": "key-1",
            "sig_alg": "ed25519",
            "signature": s_hex,
            "signed_at": "2026-02-09T20:00:00Z"
        })

        res = apply_governance_record(
            rec, 
            current_policy_state={}, 
            governance_keyring=keyring,
            min_valid_signatures=1
        )
        assert res["ok"] is True, f"Error: {res.get('errors')}"
        snapshot = res["data"]["policy_snapshot"]
        assert snapshot["policy_hash"] == expected_hash

def test_policy_hash_differs_on_content(key_setup):
    sk, keyring = key_setup
    p1 = {"a": 1}
    p2 = {"a": 2}
    
    rec1 = {
        "protocol_version": "v0.1",
        "gov_record_id": "1"*64,
        "timestamp": "2026-02-09T20:00:00Z",
        "proposal_id": "a"*64,
        "state": "proposed",
        "payload": p1,
        "signatures": []
    }
    # Sign rec1
    pb1 = canonical_governance_payload_bytes(rec1)
    s1 = sign(sk, pb1)
    rec1["signatures"].append({
        "key_id": "key-1",
        "sig_alg": "ed25519",
        "signature": s1,
        "signed_at": "2026-02-09T20:00:00Z"
    })

    rec2 = rec1.copy()
    rec2["payload"] = p2
    rec2["gov_record_id"] = "2"*64
    rec2["signatures"] = [] # Reset signatures
    
    # Sign rec2
    pb2 = canonical_governance_payload_bytes(rec2)
    s2 = sign(sk, pb2)
    rec2["signatures"].append({
        "key_id": "key-1",
        "sig_alg": "ed25519",
        "signature": s2,
        "signed_at": "2026-02-09T20:00:00Z"
    })
    
    res1 = apply_governance_record(rec1, current_policy_state={}, governance_keyring=keyring)
    res2 = apply_governance_record(rec2, current_policy_state={}, governance_keyring=keyring)
    
    assert res1["ok"] is True
    assert res2["ok"] is True
    
    h1 = res1["data"]["policy_snapshot"]["policy_hash"]
    h2 = res2["data"]["policy_snapshot"]["policy_hash"]
    
    assert h1 != h2
