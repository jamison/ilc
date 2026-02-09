"""
Tests for ILC Cluster A Ingest.
"""
from pathlib import Path
from ilc_core.protocol.ilc_cluster_a_ingest import ingest_cluster_a_artifact, _infer_kind

def test_inference_order():
    obj = {"gov_record_id": "1", "signatures": []}
    assert _infer_kind(obj) == "governance_record"
    obj = {"transcript_id": "1", "records": []}
    assert _infer_kind(obj) == "transcript"
    obj = {"receipt_id": "1", "outcome": "valid"}
    assert _infer_kind(obj) == "receipt"
    obj = {"event_id": "1", "event_kind": "claim"}
    assert _infer_kind(obj) == "wire"
    obj = {"foo": "bar"}
    assert _infer_kind(obj) is None

def test_ingest_unknown_kind():
    res = ingest_cluster_a_artifact({"foo": "bar"})
    assert res["ok"] is False
    assert "context_violation:unknown_artifact_kind" in res["errors"]

def test_ingest_kind_mismatch():
    obj = {"event_id": "1", "event_kind": "claim"}
    res = ingest_cluster_a_artifact(obj, artifact_kind="receipt")
    assert res["ok"] is False
    assert "context_violation:artifact_kind_mismatch" in res["errors"]
    assert res["artifact_kind"] == "wire"

def test_envelope_shape():
    obj = {"event_id": "1", "event_kind": "claim"}
    res = ingest_cluster_a_artifact(obj)
    assert set(res.keys()) == {"ok", "artifact_kind", "errors", "warnings", "version", "data"}
    assert res["artifact_kind"] == "wire"
    assert res["ok"] is False
    assert isinstance(res["errors"], list)
    assert isinstance(res["warnings"], list)
    assert res["errors"] == sorted(res["errors"])
    assert res["version"] is None

def test_valid_ingest_dispatch():
    # Valid Claim event with correct Hex
    obj = {
        "protocol_version": "v0.1",
        "event_id": "a"*64,
        "timestamp": "2026-02-09T20:00:00Z",
        "agent_id": "agent-1",
        "event_kind": "claim",
        "content_hash": "b"*64, # Valid hex
        "context_ids": []
    }
    res = ingest_cluster_a_artifact(obj)
    assert res["ok"] is True, f"Errors: {res.get('errors')}"
    assert res["artifact_kind"] == "wire"
    assert res["errors"] == []
    assert res["data"] == obj
    assert res["version"] == "v0.1"

def test_ingest_file_invalid_json_returns_stable_error(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    res = ingest_cluster_a_artifact(bad)
    assert res["ok"] is False
    assert res["errors"] == ["invalid_json"]

def test_ingest_file_read_error_returns_stable_error(tmp_path: Path):
    # Passing a directory triggers an OSError on read_text().
    res = ingest_cluster_a_artifact(tmp_path)
    assert res["ok"] is False
    assert res["errors"] == ["file_read_error"]
