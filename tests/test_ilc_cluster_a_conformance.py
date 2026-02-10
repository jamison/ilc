"""
Tests for ILC Cluster A conformance and hardening behavior.
Phase 137.
"""
import pytest
from pathlib import Path
from ilc_core.protocol.ilc_cluster_a_conformance import (
    classify_conformance_result,
    conformance_check_cluster_a_artifact,
)

# --- Fixtures ---

@pytest.fixture
def valid_wire_artifact():
    return {
        "protocol_version": "v0.1",
        "event_id": "a"*64,
        "timestamp": "2026-02-10T00:00:00Z",
        "agent_id": "agent-1",
        "event_kind": "claim",
        "content_hash": "b"*64,
        "context_ids": []
    }

@pytest.fixture
def valid_policy_binding():
    return {
        "policy_hash": "1"*64,
        "policy_epoch": 100,
        "policy_window": "2026-02"
    }

# --- Tests ---

def test_ingest_failure_passthrough_unknown_kind():
    # 1. Ingest failure passthrough for unknown artifact kind
    res = conformance_check_cluster_a_artifact({"foo": "bar"})
    assert res["ok"] is False
    assert "context_violation:unknown_artifact_kind" in res["errors"]
    assert res["policy_binding"] is None
    assert res["data"] is None

def test_ingest_failure_invalid_json_path(tmp_path):
    # 2. Ingest failure passthrough for invalid JSON path
    p = tmp_path / "bad.json"
    p.write_text("{")
    res = conformance_check_cluster_a_artifact(p)
    assert res["ok"] is False
    assert "invalid_json" in res["errors"]

def test_successful_conformance_exact_match(valid_wire_artifact, valid_policy_binding):
    # 3. Successful conformance with exact expected hash, epoch, and window
    artifact = {**valid_wire_artifact, **valid_policy_binding}
    
    res = conformance_check_cluster_a_artifact(
        artifact,
        expected_policy_hash=valid_policy_binding["policy_hash"],
        expected_policy_epoch=valid_policy_binding["policy_epoch"],
        expected_policy_window=valid_policy_binding["policy_window"]
    )
    
    assert res["ok"] is True
    assert res["errors"] == []
    assert res["policy_binding"]["policy_hash"] == valid_policy_binding["policy_hash"]
    assert res["policy_binding"]["binding_ok"] is True

def test_policy_hash_mismatch(valid_wire_artifact, valid_policy_binding):
    # 4. Hash mismatch
    artifact = {**valid_wire_artifact, **valid_policy_binding}
    
    res = conformance_check_cluster_a_artifact(
        artifact,
        expected_policy_hash="2"*64 # Different from "1"*64
    )
    assert res["ok"] is False
    assert "context_violation:policy_hash_mismatch" in res["errors"]
    assert res["policy_binding"]["binding_ok"] is False

def test_policy_epoch_mismatch(valid_wire_artifact, valid_policy_binding):
    # 5. Epoch mismatch
    artifact = {**valid_wire_artifact, **valid_policy_binding}
    
    res = conformance_check_cluster_a_artifact(
        artifact,
        expected_policy_epoch=999
    )
    assert res["ok"] is False
    assert "context_violation:policy_epoch_mismatch" in res["errors"]

def test_policy_window_mismatch(valid_wire_artifact, valid_policy_binding):
    # 6. Window mismatch
    artifact = {**valid_wire_artifact, **valid_policy_binding}
    
    res = conformance_check_cluster_a_artifact(
        artifact,
        expected_policy_window="2026-03"
    )
    assert res["ok"] is False
    assert "context_violation:policy_window_mismatch" in res["errors"]

def test_expected_binding_missing_in_artifact(valid_wire_artifact):
    # 7. Expected binding provided but missing in artifact
    # Artifact has NO binding fields
    res = conformance_check_cluster_a_artifact(
        valid_wire_artifact,
        expected_policy_hash="1"*64
    )
    assert res["ok"] is False
    assert "context_violation:missing_policy_binding" in res["errors"]

def test_invalid_policy_hash_format(valid_wire_artifact):
    # 8. Invalid policy_hash format at root
    artifact = {**valid_wire_artifact, "policy_hash": "invalid-hex"}
    
    res = conformance_check_cluster_a_artifact(artifact)
    assert res["ok"] is False
    assert "value_violation:invalid_policy_hash" in res["errors"]

def test_invalid_policy_epoch_type(valid_wire_artifact):
    # 9. Invalid policy_epoch type/value
    artifact = {**valid_wire_artifact, "policy_epoch": -1}
    res = conformance_check_cluster_a_artifact(artifact)
    assert res["ok"] is False
    assert "value_violation:invalid_policy_epoch" in res["errors"]
    
    artifact2 = {**valid_wire_artifact, "policy_epoch": "100"} # String instead of int
    res2 = conformance_check_cluster_a_artifact(artifact2)
    assert "value_violation:invalid_policy_epoch" in res2["errors"]

    artifact3 = {**valid_wire_artifact, "policy_epoch": True}  # bool must be rejected
    res3 = conformance_check_cluster_a_artifact(artifact3)
    assert "value_violation:invalid_policy_epoch" in res3["errors"]

def test_invalid_policy_window_value(valid_wire_artifact):
    # 10. Invalid policy_window value
    artifact = {**valid_wire_artifact, "policy_window": ""} # Empty string
    res = conformance_check_cluster_a_artifact(artifact)
    assert res["ok"] is False
    assert "value_violation:invalid_policy_window" in res["errors"]

def test_no_expected_binding_warns_if_unbound(valid_wire_artifact):
    # 11. No expected binding plus unbound artifact gives warning only
    res = conformance_check_cluster_a_artifact(valid_wire_artifact)
    assert res["ok"] is True
    assert "policy_binding_absent_unchecked" in res["warnings"]
    assert res["policy_binding"]["binding_ok"] is True # It is "ok" because no errors.

def test_deterministic_sorting_multiple_errors(valid_wire_artifact):
    # 12. Deterministic sorting of multiple errors
    # Trigger 2 value violations
    artifact = {
        **valid_wire_artifact,
        "policy_hash": "bad",
        "policy_epoch": -1
    }
    res = conformance_check_cluster_a_artifact(artifact)
    assert res["ok"] is False
    assert len(res["errors"]) == 2
    assert res["errors"] == sorted(res["errors"])
    assert res["errors"] == [
        "value_violation:invalid_policy_epoch",
        "value_violation:invalid_policy_hash"
    ]

def test_envelope_keys(valid_wire_artifact, valid_policy_binding):
    # 13. Exact envelope key set
    artifact = {**valid_wire_artifact, **valid_policy_binding}
    res = conformance_check_cluster_a_artifact(artifact)
    
    expected_keys = {"ok", "artifact_kind", "errors", "warnings", "version", "policy_binding", "data"}
    assert set(res.keys()) == expected_keys
    
    binding_keys = {"policy_hash", "policy_epoch", "policy_window", "binding_ok"}
    assert set(res["policy_binding"].keys()) == binding_keys

# --- Phase 137 Strictness Tests ---

def test_governance_record_must_have_full_binding():
    # 1. Gov record missing one binding field -> missing_policy_binding
    gov = {
        "protocol_version": "v0.1",
        "gov_record_id": "a"*64,
        "proposal_id": "b"*64,
        "state": "proposed",
        "timestamp": "2026-02-10T00:00:00Z",
        "payload": {},
        "signatures": [
             {
                "key_id": "key-1",
                "sig_alg": "ed25519",
                "signature": "a"*64,
                "signed_at": "2026-02-10T00:00:00Z"
            }
        ]
    }
    # Valid binding fields (extracted then stripped)
    # Case A: No binding -> Error
    res = conformance_check_cluster_a_artifact(gov)
    assert res["ok"] is False, f"Errors: {res.get('errors')}"
    assert "context_violation:missing_policy_binding" in res["errors"]
    
    # Case B: Partial binding -> Error (Missing)
    gov_partial = {**gov, "policy_hash": "1"*64}
    res2 = conformance_check_cluster_a_artifact(gov_partial)
    assert res2["ok"] is False
    assert "context_violation:missing_policy_binding" in res2["errors"]

def test_transcript_partial_binding_rejected():
    # 2. Transcript with partial binding -> partial_policy_binding
    transcript = {
        "protocol_version": "v0.1",
        "transcript_id": "d"*64,
        "timestamp_start": "2026-02-10T00:00:00Z",
        "timestamp_end": "2026-02-10T01:00:00Z",
        "records": [],
        "previous_transcript_id": "e"*64
    }
    # Partial binding
    tr_partial = {**transcript, "policy_hash": "1"*64}
    res = conformance_check_cluster_a_artifact(tr_partial)
    assert res["ok"] is False
    assert "context_violation:partial_policy_binding" in res["errors"], f"Got: {res.get('errors')}"

def test_strict_mode_unbound_artifact_hard_fail(valid_wire_artifact):
    # 4. expected context + unbound wire -> hard fail missing_policy_binding
    # Wire artifact (optional binding normally)
    # No binding in artifact. Expected hash provided.
    res = conformance_check_cluster_a_artifact(
        valid_wire_artifact,
        expected_policy_hash="1"*64
    )
    assert res["ok"] is False
    assert "context_violation:missing_policy_binding" in res["errors"]
    assert "policy_binding_absent_unchecked" not in res["warnings"]

def test_classify_conformance_result():
    # 6. classify_conformance_result checks
    
    # Pass
    res_ok = {"ok": True, "errors": [], "warnings": [], "policy_binding": {"binding_ok": True}}
    cls = classify_conformance_result(res_ok)
    assert cls["category"] == "pass"
    
    # Ingest Failure (policy_binding is None)
    res_ingest = {"ok": False, "errors": ["invalid_json"], "policy_binding": None}
    cls = classify_conformance_result(res_ingest)
    assert cls["category"] == "ingest_failure"
    
    # Value Failure (policy_binding present but failed)
    res_val = {"ok": False, "errors": ["value_violation:invalid_policy_epoch"], "policy_binding": {"binding_ok": False}}
    cls = classify_conformance_result(res_val)
    assert cls["category"] == "binding_value_failure"

    # Structure Failure
    res_struct = {"ok": False, "errors": ["context_violation:partial_policy_binding"], "policy_binding": {"binding_ok": False}}
    cls = classify_conformance_result(res_struct)
    assert cls["category"] == "binding_structure_failure"

    # Context Failure
    res_ctx = {"ok": False, "errors": ["context_violation:policy_hash_mismatch"], "policy_binding": {"binding_ok": False}}
    cls = classify_conformance_result(res_ctx)
    assert cls["category"] == "binding_context_mismatch"
