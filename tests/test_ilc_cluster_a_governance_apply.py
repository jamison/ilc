"""
Tests for ILC Cluster A Governance Apply.
"""
import hashlib
from ilc_core.protocol.ilc_cluster_a_ingest import apply_governance_record

def _valid_gov_record(state="proposed", proposal_id=None, payload=None):
    if payload is None:
        payload = {"foo": "bar"}
    # Valid hex
    pid = proposal_id if proposal_id else "1"*64
    gid = "a"*64
    
    return {
        "protocol_version": "v0.1",
        "gov_record_id": gid,
        "timestamp": "2026-02-09T20:00:00Z",
        # agent_id removed
        "proposal_id": pid,
        "state": state,
        "payload": payload,
        "signatures": [
            {
                "key_id": "key-1",
                "sig_alg": "ed25519",
                "signature": "a"*64, # Valid hex
                "signed_at": "2026-02-09T20:00:00Z"
            }
        ]
    }

def test_apply_proposed_new():
    rec = _valid_gov_record(state="proposed")
    current_state = {"proposals": {}, "known_records": {}}
    res = apply_governance_record(rec, current_policy_state=current_state)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"
    assert res["data"]["new_state"] == "proposed"

def test_apply_finalized_transition():
    rec = _valid_gov_record(state="finalized")
    pid = rec["proposal_id"]
    current_state = {
        "proposals": {pid: "proposed"},
        "known_records": {}
    }
    res = apply_governance_record(rec, current_policy_state=current_state)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"

def test_apply_invalid_transition():
    rec = _valid_gov_record(state="proposed")
    pid = rec["proposal_id"]
    current_state = {
        "proposals": {pid: "finalized"},
        "known_records": {}
    }
    res = apply_governance_record(rec, current_policy_state=current_state)
    assert res["ok"] is False
    assert "context_violation:invalid_state_transition:finalized:proposed" in res["errors"]

def test_apply_idempotent():
    rec = _valid_gov_record(state="finalized")
    blob = b'{"foo":"bar"}'
    expected_hash = hashlib.sha256(blob).hexdigest()
    current_state = {
        "proposals": {rec["proposal_id"]: "finalized"},
        "known_records": {
            rec["gov_record_id"]: expected_hash
        }
    }
    res = apply_governance_record(rec, current_policy_state=current_state)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"

def test_apply_hash_conflict():
    rec = _valid_gov_record(state="finalized", payload={"foo": "bar"})
    rec_id = rec["gov_record_id"]
    pid = rec["proposal_id"]
    current_state = {
        "proposals": {pid: "proposed"}, 
        "known_records": {
            rec_id: "a"*63 + "b" # BAD HASH
        }
    }
    res = apply_governance_record(rec, current_policy_state=current_state)
    assert res["ok"] is False
    assert "context_violation:gov_record_id_hash_conflict" in res["errors"]
