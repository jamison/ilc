import json
from pathlib import Path
from importlib import resources

import jsonschema
import pytest
from unittest.mock import patch
from ilc_core.exceptions import ReplayProofManifestError
from ilc_core.protocol.ilc_cluster_a_replay_proof_batch import (
    verify_cluster_a_replay_proof_batch,
    load_manifest_paths
)
from ilc_core.protocol.ilc_cluster_a_replay_proof_schemas import (
    load_replay_proof_schema,
)

# Mock packages for testing logic without filesystem
VALID_PKG = {"mock": "valid"}
INVALID_PKG = {"mock": "invalid"}


def _load_packaged_replay_schema(name: str) -> dict[str, object]:
    text = resources.files("ilc_core.protocol.schemas").joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)

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


def test_manifest_duplicate_after_normalization_error(tmp_path):
    manifest = tmp_path / "manifest_dup_norm.txt"
    manifest.write_text("file1.json\n./file1.json\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schema_violation:duplicate_manifest_path"):
        load_manifest_paths(manifest)


def test_manifest_path_escape_error(tmp_path):
    manifest = tmp_path / "manifest_escape.txt"
    manifest.write_text("../file1.json\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schema_violation:manifest_path_escape"):
        load_manifest_paths(manifest)


def test_manifest_path_not_relative_error(tmp_path):
    manifest = tmp_path / "manifest_abs.txt"
    manifest.write_text("/tmp/file1.json\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schema_violation:manifest_path_not_relative"):
        load_manifest_paths(manifest)


def test_manifest_windows_path_not_relative_error(tmp_path):
    manifest = tmp_path / "manifest_windows_abs.txt"
    manifest.write_text("C:\\\\tmp\\\\file1.json\n", encoding="utf-8")

    with pytest.raises(ValueError, match="schema_violation:manifest_path_not_relative"):
        load_manifest_paths(manifest)


def test_manifest_domain_exception_type_duplicate(tmp_path):
    manifest = tmp_path / "manifest_dup_type.txt"
    manifest.write_text("a.json\na.json\n", encoding="utf-8")
    with pytest.raises(ReplayProofManifestError, match="schema_violation:duplicate_manifest_path"):
        load_manifest_paths(manifest)


def test_manifest_domain_exception_type_escape(tmp_path):
    manifest = tmp_path / "manifest_escape_type.txt"
    manifest.write_text("../x.json\n", encoding="utf-8")
    with pytest.raises(ReplayProofManifestError, match="schema_violation:manifest_path_escape"):
        load_manifest_paths(manifest)


def test_manifest_path_normalization(tmp_path):
    manifest = tmp_path / "manifest_norm.txt"
    manifest.write_text(".\\\\sub\\\\..\\\\file1.json\n", encoding="utf-8")
    assert load_manifest_paths(manifest) == ["file1.json"]

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

    schema = _load_packaged_replay_schema("ilc_cluster_a_replay_proof_batch_report_v0.1.json")
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


# --- Phase 151: Parametrized manifest path contract tests ---

@pytest.mark.parametrize(
    "entries,expected_error",
    [
        (["./a.json", "a.json"], "schema_violation:duplicate_manifest_path"),
        (["x/../a.json", "a.json"], "schema_violation:duplicate_manifest_path"),
        (["../a.json"], "schema_violation:manifest_path_escape"),
        (["/tmp/a.json"], "schema_violation:manifest_path_not_relative"),
        (["C:/tmp/a.json"], "schema_violation:manifest_path_not_relative"),
    ],
)
def test_manifest_path_contract(entries, expected_error, tmp_path):
    """Manifest must reject invalid path forms with deterministic tokens."""
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=expected_error):
        load_manifest_paths(manifest)


@pytest.mark.parametrize(
    "entry,expected_error",
    [
        (".", "schema_violation:invalid_manifest_path"),
        ("./", "schema_violation:invalid_manifest_path"),
    ],
)
def test_manifest_empty_dot_rejection(entry, expected_error, tmp_path):
    """Dot and dot-slash entries are invalid manifest paths."""
    manifest = tmp_path / "manifest.txt"
    manifest.write_text(entry + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=expected_error):
        load_manifest_paths(manifest)


def test_manifest_blank_lines_skipped(tmp_path):
    """Blank/empty lines in manifests are silently skipped, not errors."""
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("\n\n   \n\n", encoding="utf-8")
    paths = load_manifest_paths(manifest)
    assert paths == []


def test_manifest_mixed_separator_normalization(tmp_path):
    """Backslash and slash separators normalize identically."""
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("sub\\file.json\n", encoding="utf-8")
    paths = load_manifest_paths(manifest)
    assert paths == ["sub/file.json"]


def test_manifest_traversal_collapse_normalization(tmp_path):
    """x/../a.json normalizes to a.json."""
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("x/../a.json\n", encoding="utf-8")
    paths = load_manifest_paths(manifest)
    assert paths == ["a.json"]


def test_schema_loader_packaged_resource_available():
    """Packaged schema resources must be loadable from ilc_core.protocol.schemas."""
    schema_names = [
        "ilc_cluster_a_replay_proof_batch_report_v0.1.json",
        "ilc_cluster_a_replay_proof_ci_gate_report_v0.1.json",
        "ilc_cluster_a_replay_proof_batch_compare_v0.1.json",
        "ilc_cluster_a_replay_proof_batch_ops_contract_v0.1.json",
    ]
    for name in schema_names:
        text = resources.files("ilc_core.protocol.schemas").joinpath(name).read_text(encoding="utf-8")
        schema = json.loads(text)
        assert "$schema" in schema, f"Packaged schema {name} missing $schema field"
        assert "properties" in schema, f"Packaged schema {name} missing properties"


def test_replay_proof_schema_loader_missing_returns_empty_map():
    schema = load_replay_proof_schema("missing_schema_v0.0.json")
    assert schema == {}
