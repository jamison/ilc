"""
Tests for ILC Cluster A Conformance and Policy Binding.
Phase 136.
"""
import pytest
from pathlib import Path
from ilc_core.protocol.ilc_cluster_a_conformance import conformance_check_cluster_a_artifact

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
