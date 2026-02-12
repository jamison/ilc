import json
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import jsonschema
import pytest

# We import the CLI entrypoint indirectly by importing the module logic or using subprocess
# Using module import allows easier mocking
from ilc_core.cli.canon_cluster_a_replay_proof import main, handle_verify_batch

FIXTURES_DIR = Path("tests/fixtures/cluster_a_replay_proof_batch_v0_1")

# Helper to capture stdout
class CaptureOutput:
    def __enter__(self):
        self.stdout = sys.stdout
        self.output = StringIO()
        sys.stdout = self.output
        return self.output
    def __exit__(self, *args):
        sys.stdout = self.stdout

def run_cli_command(args_list):
    """Runs main() with arguments and returns (exit_code, stdout_str)."""
    with patch.object(sys, 'argv', ["prog"] + args_list):
        output = StringIO()
        with patch.object(sys, 'stdout', output):
            try:
                main()
                return 0, output.getvalue()
            except SystemExit as e:
                return e.code, output.getvalue()

def test_verify_batch_manifest(tmp_path):
    # Setup test env
    # Copy fixtures to tmp path to ensure we control the environment
    # Actually we can use the fixtures directly if we are careful with CWD
    # The CLI relies on CWD if paths are relative. 
    # Let's create a tmp dir and copy generic valid packages there.
    
    d = tmp_path / "batch_test"
    d.mkdir()
    
    pkg_valid = d / "pkg_valid.json"
    pkg_valid.write_text(json.dumps({"package_hash_sha256": "mock_valid"}), encoding="utf-8")
    
    pkg_invalid = d / "pkg_invalid.json"
    pkg_invalid.write_text(json.dumps({"package_hash_sha256": "mock_invalid"}), encoding="utf-8")
    
    manifest = d / "manifest.txt"
    manifest.write_text("pkg_valid.json\npkg_invalid.json", encoding="utf-8")
    
    # Mock the protocol verifier to return deterministic results
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_batch") as mock_batch:
        mock_batch.return_value = {
            "ok": False, 
            "results": [], 
            "report_version": "v0.1",
            "fail_count": 1,
            "error_token_counts": {},
            "batch_errors": [],
            "ok_count": 0,
            "total_packages": 0
        }
        
        # We need to run this with CWD = d
        old_cwd = os.getcwd()
        os.chdir(d)
        try:
            code, out = run_cli_command(["verify-batch", "--manifest", "manifest.txt"])
            
            # Should call batch verifier with parsed items
            assert mock_batch.called
            args, _ = mock_batch.call_args
            package_items, source_ids = args
            
            assert len(package_items) == 2
            assert source_ids == ["pkg_valid.json", "pkg_invalid.json"]
            
            # Since mock returned ok=False, exit code should be 1
            assert code == 1
            
            # Output should be the mock report
            data = json.loads(out)
            assert data["report_version"] == "v0.1"
            
        finally:
            os.chdir(old_cwd)

def test_verify_batch_manifest_resolves_relative_to_manifest_dir_without_chdir(tmp_path):
    d = tmp_path / "manifest_relative_base"
    d.mkdir()

    (d / "pkg_valid.json").write_text(json.dumps({"package_hash_sha256": "mock_valid"}), encoding="utf-8")
    (d / "pkg_invalid.json").write_text(json.dumps({"package_hash_sha256": "mock_invalid"}), encoding="utf-8")
    manifest = d / "manifest.txt"
    manifest.write_text("pkg_valid.json\npkg_invalid.json\n", encoding="utf-8")

    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_batch") as mock_batch:
        mock_batch.return_value = {
            "ok": True,
            "results": [],
            "report_version": "v0.1",
            "fail_count": 0,
            "ok_count": 2,
            "total_packages": 2,
            "error_token_counts": {},
            "batch_errors": []
        }

        code, out = run_cli_command(["verify-batch", "--manifest", str(manifest)])

        assert code == 0
        assert mock_batch.called
        package_items, source_ids = mock_batch.call_args[0]
        assert len(package_items) == 2
        assert source_ids == ["pkg_valid.json", "pkg_invalid.json"]

def test_verify_batch_input_dir(tmp_path):
    d = tmp_path / "dir_scan"
    d.mkdir()
    (d / "a.json").write_text("{}", encoding="utf-8")
    (d / "b.json").write_text("{}", encoding="utf-8")
    
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_batch") as mock_batch:
        mock_batch.return_value = {
            "ok": True,
            "results": [],
            "report_version": "v0.1",
            "fail_count": 0,
            "ok_count": 0,
            "total_packages": 0,
            "error_token_counts": {},
            "batch_errors": []
        }
        
        code, out = run_cli_command(["verify-batch", "--input-dir", str(d)])
        
        assert code == 0
        assert mock_batch.called
        package_items, source_ids = mock_batch.call_args[0]
        assert len(source_ids) == 2
        # Sorting is by source_id, but here source_id is relative path. 
        # a.json comes before b.json.
        assert source_ids == ["a.json", "b.json"]

def test_verify_batch_missing_file_manifest(tmp_path):
    manifest = tmp_path / "bad_manifest.txt"
    manifest.write_text("missing.json", encoding="utf-8")
    
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        code, out = run_cli_command(["verify-batch", "--manifest", "bad_manifest.txt"])
        assert code == 2
        err = json.loads(out)
        assert err["error"] == "manifest_file_not_found"
    finally:
        os.chdir(old_cwd)

def test_verify_batch_invalid_json(tmp_path):
    d = tmp_path / "bad_json"
    d.mkdir()
    (d / "bad.json").write_text("{broken", encoding="utf-8")
    
    code, out = run_cli_command(["verify-batch", "--input-dir", str(d)])
    assert code == 2
    err = json.loads(out)
    assert err["error"] == "invalid_json"

def test_verify_batch_not_object(tmp_path):
    d = tmp_path / "not_obj"
    d.mkdir()
    (d / "list.json").write_text("[]", encoding="utf-8")
    
    code, out = run_cli_command(["verify-batch", "--input-dir", str(d)])
    assert code == 2
    err = json.loads(out)
    assert err["error"] == "schema_violation:not_object"

def test_verify_batch_manifest_not_found(tmp_path):
    code, out = run_cli_command(["verify-batch", "--manifest", "missing_manifest.txt"])
    assert code == 2
    err = json.loads(out)
    assert err["error"] == "manifest_not_found"

def test_verify_batch_manifest_duplicate_entry(tmp_path):
    manifest = tmp_path / "dup_manifest.txt"
    manifest.write_text("a.json\na.json", encoding="utf-8")
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        code, out = run_cli_command(["verify-batch", "--manifest", "dup_manifest.txt"])
        assert code == 2
        err = json.loads(out)
        assert err["error"] == "manifest_parse_error"
        assert err["detail"] == "schema_violation:duplicate_manifest_path"
    finally:
        os.chdir(old_cwd)

def test_cli_batch_report_schema_manifest_real():
    schema = json.loads(
        Path("docs/specs/ilc_cluster_a_replay_proof_batch_report_v0.1.json")
        .read_text(encoding="utf-8")
    )
    old_cwd = os.getcwd()
    os.chdir(FIXTURES_DIR)
    try:
        code, out = run_cli_command(["verify-batch", "--manifest", "manifest_valid_then_tampered.txt"])
        assert code == 1
        report = json.loads(out)
        jsonschema.Draft7Validator(schema).validate(report)
    finally:
        os.chdir(old_cwd)

def test_cli_batch_report_schema_input_dir_real(tmp_path):
    schema = json.loads(
        Path("docs/specs/ilc_cluster_a_replay_proof_batch_report_v0.1.json")
        .read_text(encoding="utf-8")
    )
    # Copy fixture files into tmp dir so input-dir scan is controlled
    for name in [
        "package_valid.json",
        "package_tampered_hash.json",
        "package_tampered_record_hash.json"
    ]:
        src = FIXTURES_DIR / name
        dst = tmp_path / name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    code, out = run_cli_command(["verify-batch", "--input-dir", str(tmp_path)])
    assert code == 1
    report = json.loads(out)
    jsonschema.Draft7Validator(schema).validate(report)
