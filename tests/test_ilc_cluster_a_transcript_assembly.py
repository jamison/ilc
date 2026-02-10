"""
Tests for ILC Cluster A Transcript Assembly.
"""
from ilc_core.protocol.ilc_cluster_a_ingest import assemble_canonical_transcript

def test_assemble_mixed_valid():
    w1 = {
        "protocol_version": "v0.1",
        "event_id": "a"*64,
        "timestamp": "2026-02-09T20:00:00Z",
        "agent_id": "agent-1",
        "event_kind": "stake",
        "target_event_id": "e"*64,
        "amount": "100",
        "currency": "ILC"
    }
    w2 = {
        "protocol_version": "v0.1",
        "event_id": "b"*64,
        "timestamp": "2026-02-09T20:05:00Z",
        "agent_id": "agent-2",
        "event_kind": "claim",
        "content_hash": "d"*64,
        "context_ids": ["a"*64]
    }
    r1 = {
         "protocol_version": "v0.1",
         "receipt_id": "c"*64,
         "timestamp": "2026-02-09T20:02:00Z",
         "related_claim_id": "f"*64,
         "outcome": "valid",
         "payouts": []
    }
    
    meta = {
        "transcript_id": "e"*64,
        "timestamp_start": "2026-02-09T20:00:00Z",
        "timestamp_end": "2026-02-09T21:00:00Z",
        "previous_transcript_id": "0"*64,
    }
    
    records = [w2, w1, r1]
    res = assemble_canonical_transcript(records, transcript_meta=meta)
    
    assert res["ok"] is True, f"Error: {res.get('errors')}"
    
    out_records = res["data"]["records"]
    assert len(out_records) == 3
    assert out_records[0]["event_id"] == w1["event_id"]   # 20:00 Stake
    assert out_records[1]["receipt_id"] == r1["receipt_id"] # 20:02 Receipt
    assert out_records[2]["event_id"] == w2["event_id"]   # 20:05 Claim

def test_assemble_rejects_invalidProvider():
    w1 = {
        "protocol_version": "v0.1",
        "event_id": "a"*64,
        "timestamp": "2026-02-09T20:00:00Z",
        "agent_id": "agent-1",
        "event_kind": "stake",
        "target_event_id": "e"*64,
        "amount": "100",
        "currency": "ILC"
    }
    bad = {"foo": "bar"}
    meta = {
        "transcript_id": "e"*64,
        "timestamp_start": "2026-02-09T20:00:00Z",
        "timestamp_end": "2026-02-09T21:00:00Z",
        "previous_transcript_id": "0"*64,
    }
    res = assemble_canonical_transcript([w1, bad], transcript_meta=meta)
    assert res["ok"] is False
    assert any("context_violation:record_not_wire_or_receipt:1" in e for e in res["errors"])


def test_assemble_sorts_same_timestamp_by_kind():
    ts = "2026-02-09T20:00:00Z"
    
    w_claim = {
        "protocol_version": "v0.1",
        "event_id": "1"*64,
        "timestamp": ts,
        "agent_id": "a1",
        "event_kind": "claim",
        "content_hash": "d"*64,
        "context_ids": []
    }
    w_stake = {
         "protocol_version": "v0.1",
         "event_id": "2"*64,
         "timestamp": ts,
         "agent_id": "a1",
         "event_kind": "stake",
         "target_event_id": "e"*64,
         "amount": "10",
         "currency": "ILC"
    }
    r_receipt = {
         "protocol_version": "v0.1",
         "receipt_id": "3"*64,
         "timestamp": ts,
         "related_claim_id": "f"*64,
         "outcome": "valid",
         "payouts": []
    }
    
    meta = {
        "transcript_id": "e"*64,
        "timestamp_start": "2026-02-09T20:00:00Z",
        "timestamp_end": "2026-02-09T21:00:00Z",
        "previous_transcript_id": "0"*64,
    }
    
    records = [w_stake, r_receipt, w_claim]
    res = assemble_canonical_transcript(records, transcript_meta=meta)
    
    assert res["ok"] is True, f"Error: {res.get('errors')}"
    out = res["data"]["records"]
    assert out[0]["event_kind"] == "claim"
    assert "receipt_id" in out[1] # Receipt
    assert out[2]["event_kind"] == "stake"

def test_transcript_assembly_deterministic_ordering():
    """
    M1: Verify canonical transcript ordering key: (timestamp, normalized_kind, normalized_id).
    """
    # Mixed records with identical timestamps to force secondary key usage
    t = "2023-01-01T12:00:00Z"
    
    # Wire A: kind="stake", id="aaa"
    rec_wire_a = {
        "protocol_version": "v0.1",
        "event_id": "aaa"*21 + "a", # 64 chars
        "event_kind": "stake",
        "timestamp": t,
        "agent_id": "ag1",
        "target_event_id": "evt1"*16, # 64 chars needed? Schema check usually
        "amount": "100",
        "currency": "ILC"
    }
    # Wire B: kind="stake", id="bbb"
    rec_wire_b = {
        "protocol_version": "v0.1",
        "event_id": "bbb"*21 + "b", # 64 chars
        "event_kind": "stake",
        "timestamp": t,
        "agent_id": "ag1",
        "target_event_id": "evt1"*16,
        "amount": "100",
        "currency": "ILC"
    }
    # Receipt A: kind="receipt", id="aaa" 
    rec_receipt_a = {
        "protocol_version": "v0.1",
        "receipt_id": "aaa"*21 + "a", # Same ID as wire_a
        "outcome": "valid", # Enum "valid" not "success"
        "timestamp": t,
        "related_claim_id": "c"*64,
        "payouts": []
    }
    
    # Order expectation:
    # 1. timestamp (all same)
    # 2. kind ("receipt" vs "stake") 
    #    "receipt" < "stake" ('r' < 's')
    # 3. id
    
    records = [rec_wire_b, rec_receipt_a, rec_wire_a]
    meta = {
        "transcript_id": "a"*64,  # valid hex
        "timestamp_start": t, 
        "timestamp_end": t,
        "previous_transcript_id": "0"*64
    }
    
    res = assemble_canonical_transcript(records, transcript_meta=meta)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"
    
    sorted_recs = res["data"]["records"]
    
    # 1. Receipt (kind="receipt") vs Wire (kind="stake")
    assert "receipt_id" in sorted_recs[0], "Receipt should be first (r < s)"
    assert sorted_recs[0]["receipt_id"] == rec_receipt_a["receipt_id"]
    
    # 2. Wire A vs Wire B (same kind, sort by ID)
    assert sorted_recs[1]["event_id"] == rec_wire_a["event_id"]
    assert sorted_recs[2]["event_id"] == rec_wire_b["event_id"]

