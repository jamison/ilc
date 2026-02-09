"""
Tests for ILC Cluster A Replay Determinism.
"""
import hashlib
from ilc_core.protocol.ilc_cluster_a_ingest import apply_governance_record

def test_policy_hash_stability():
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
            # agent_id removed
            "proposal_id": "a"*64,
            "state": "proposed",
            "payload": payload,
             "signatures": [
                {
                    "key_id": "key-1",
                    "sig_alg": "ed25519",
                    "signature": "a"*64,
                    "signed_at": "2026-02-09T20:00:00Z"
                }
            ]
        }
        res = apply_governance_record(rec, current_policy_state={})
        assert res["ok"] is True, f"Error: {res.get('errors')}"
        snapshot = res["data"]["policy_snapshot"]
        assert snapshot["policy_hash"] == expected_hash

def test_policy_hash_differs_on_content():
    p1 = {"a": 1}
    p2 = {"a": 2}
    
    rec1 = {
        "protocol_version": "v0.1",
        "gov_record_id": "1"*64,
        "timestamp": "2026-02-09T20:00:00Z",
        "proposal_id": "a"*64,
        "state": "proposed",
        "payload": p1,
        "signatures": [
            {
                "key_id": "key-1",
                "sig_alg": "ed25519",
                "signature": "a"*64,
                "signed_at": "2026-02-09T20:00:00Z"
            }
        ]
    }
    rec2 = rec1.copy()
    rec2["payload"] = p2
    rec2["gov_record_id"] = "2"*64
    
    res1 = apply_governance_record(rec1, current_policy_state={})
    res2 = apply_governance_record(rec2, current_policy_state={})
    
    assert res1["ok"] is True
    assert res2["ok"] is True
    
    h1 = res1["data"]["policy_snapshot"]["policy_hash"]
    h2 = res2["data"]["policy_snapshot"]["policy_hash"]
    
    assert h1 != h2
