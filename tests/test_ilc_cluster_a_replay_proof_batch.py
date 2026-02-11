import json
from pathlib import Path

import jsonschema
import pytest
from unittest.mock import patch
from ilc_core.protocol.ilc_cluster_a_replay_proof_batch import (
    verify_cluster_a_replay_proof_batch,
    load_manifest_paths
)

# Mock packages for testing logic without filesystem
VALID_PKG = {"mock": "valid"}
INVALID_PKG = {"mock": "invalid"}

@pytest.fixture
def mock_verifier():
    with patch("ilc_core.protocol.ilc_cluster_a_replay_proof_batch.verify_cluster_a_replay_proof_package") as m:
        def side_effect(pkg):
            if pkg == VALID_PKG:
                return {
                    "ok": True,
                    "errors": [],
                    "warnings": [],
                    "checks": [{"check": "mock_ok", "status": "pass", "error_code": None}],
                }
            else:
                return {
                    "ok": False,
                    "errors": ["mock_error"],
                    "warnings": [],
                    "checks": [{"check": "mock_fail", "status": "fail", "error_code": "mock_error"}],
                }
        m.side_effect = side_effect
        yield m

def test_manifest_parsing(tmp_path):
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("""
    # Comment
    file1.json
    
    file2.json
    # Another comment
    file3.json
    """, encoding="utf-8")
    
    paths = load_manifest_paths(manifest)
    assert paths == ["file1.json", "file2.json", "file3.json"]

def test_manifest_duplicate_error(tmp_path):
    manifest = tmp_path / "manifest_dup.txt"
    manifest.write_text("file1.json\nfile1.json", encoding="utf-8")
    
    with pytest.raises(ValueError, match="schema_violation:duplicate_manifest_path"):
        load_manifest_paths(manifest)

def test_batch_verify_mixed_results(mock_verifier):
    packages = [VALID_PKG, INVALID_PKG, VALID_PKG]
    source_ids = ["src1", "src2", "src3"]
    
    report = verify_cluster_a_replay_proof_batch(packages, source_ids)
    
    assert report["report_version"] == "v0.1"
    assert report["total_packages"] == 3
    assert report["ok_count"] == 2
    assert report["fail_count"] == 1
    assert report["ok"] is False
    
    # Check stable ordering
    assert len(report["results"]) == 3
    assert report["results"][0]["input_index"] == 0
    assert report["results"][0]["source_id"] == "src1"
    assert report["results"][0]["ok"] is True
    
    assert report["results"][1]["input_index"] == 1
    assert report["results"][1]["source_id"] == "src2"
    assert report["results"][1]["ok"] is False
    assert report["results"][1]["errors"] == ["mock_error"]
    
    # Check error aggregation
    assert report["error_token_counts"] == {"mock_error": 1}
    assert report["batch_errors"] == []

def test_batch_verify_all_ok(mock_verifier):
    packages = [VALID_PKG, VALID_PKG]
    source_ids = ["a", "b"]
    report = verify_cluster_a_replay_proof_batch(packages, source_ids)
    assert report["ok"] is True
    assert report["fail_count"] == 0

def test_batch_verify_input_mismatch():
    packages = [VALID_PKG]
    source_ids = ["a", "b"]
    report = verify_cluster_a_replay_proof_batch(packages, source_ids)
    
    assert report["ok"] is False
    assert "context_violation:batch_input_length_mismatch" in report["batch_errors"]
    assert report["total_packages"] == 0

def test_batch_report_schema_with_real_fixtures():
    fixtures = Path("tests/fixtures/cluster_a_replay_proof_batch_v0_1")
    manifest = fixtures / "manifest_valid_then_tampered.txt"
    rel_paths = load_manifest_paths(manifest)
    packages = [
        json.loads((fixtures / rel_path).read_text(encoding="utf-8"))
        for rel_path in rel_paths
    ]
    report = verify_cluster_a_replay_proof_batch(packages, rel_paths)

    schema = json.loads(
        Path("docs/specs/ilc_cluster_a_replay_proof_batch_report_v0.1.json")
        .read_text(encoding="utf-8")
    )
    jsonschema.Draft7Validator(schema).validate(report)

def test_batch_report_matches_expected_fixture():
    fixtures = Path("tests/fixtures/cluster_a_replay_proof_batch_v0_1")
    expected = json.loads(
        (fixtures / "batch_expected_report_mixed.json").read_text(encoding="utf-8")
    )
    manifest = fixtures / "manifest_valid_then_tampered.txt"
    rel_paths = load_manifest_paths(manifest)
    packages = [
        json.loads((fixtures / rel_path).read_text(encoding="utf-8"))
        for rel_path in rel_paths
    ]
    report = verify_cluster_a_replay_proof_batch(packages, rel_paths)
    assert report == expected
