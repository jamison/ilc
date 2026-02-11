"""
Tests for ILC Cluster A Replay Proof CLI.
Phase 144.
"""

import pytest
import json
import sys
from unittest.mock import patch
from ilc_core.cli.canon_cluster_a_replay_proof import (
    main, 
    EXIT_OK, 
    EXIT_VERIFICATION_FAILED, 
    EXIT_ERROR,
    E_FILE_NOT_FOUND,
    E_INVALID_JSON,
    E_NOT_OBJECT,
    E_IO_ERROR,
    E_IO_WRITE_ERROR,
    E_BUILD_ERROR
)

# Mock Data
MOCK_EVIDENCE = {
    "artifact_kind": "cluster_a_acceptance_evidence",
    "record_hash_sha256": "abc",
    "constitution_checks": []
}

MOCK_CONTRACT = {
    "governance_record": {"id": "rec-1"},
    "apply_result": {"ok": True},
    "conformance_result": {"ok": True}
}

MOCK_PACKAGE = {
    "package_version": "v0.1",
    "evidence": MOCK_EVIDENCE,
    "replay_contract": MOCK_CONTRACT,
    "package_hash_sha256": "hash"
}

@pytest.fixture
def mock_files(tmp_path):
    d = tmp_path / "cli_test"
    d.mkdir()
    
    ev_path = d / "evidence.json"
    ev_path.write_text(json.dumps(MOCK_EVIDENCE))
    
    contract_path = d / "contract.json"
    contract_path.write_text(json.dumps(MOCK_CONTRACT))
    
    pkg_path = d / "package.json"
    pkg_path.write_text(json.dumps(MOCK_PACKAGE))
    
    bad_json = d / "bad.json"
    bad_json.write_text("{not json")
    
    list_json = d / "list.json"
    list_json.write_text("[]")
    
    return {
        "dir": d,
        "evidence": str(ev_path),
        "contract": str(contract_path),
        "package": str(pkg_path),
        "bad_json": str(bad_json),
        "list_json": str(list_json),
        "out": str(d / "out.json")
    }

def run_cli(args):
    """Run CLI with args and return (exit_code, stdout, stderr)."""
    with patch("sys.stdout") as mock_stdout, \
         patch("sys.stderr") as mock_stderr:
        
        # We also need to capture sys.exit
        try:
            with patch.object(sys, 'argv', ["prog"] + args):
                main()
            return 0, "", "" # Should not happen if sys.exit is called
        except SystemExit as e:
            # Capture stdout from mock
            out = ""
            for call in mock_stdout.write.call_args_list:
                out += call[0][0]
            # print() calls might use different internal writes, but let's assume standard print
            # Actually, standard print goes to sys.stdout.
            # Let's use capsys fixture instead? 
            # Capsys is better but incompatible with my manual invocation style easily?
            # Let's use pytest capsys in the test function.
            pass
            return e.code
            
# Rework to use capsys
def test_build_success(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.build_cluster_a_replay_proof_package") as mock_build:
        mock_build.return_value = MOCK_PACKAGE
        
        with patch.object(sys, 'argv', ["prog", "build", "--evidence", mock_files["evidence"], "--contract", mock_files["contract"]]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == EXIT_OK
            
        captured = capsys.readouterr()
        out = json.loads(captured.out)
        assert out == MOCK_PACKAGE

def test_build_to_file(mock_files):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.build_cluster_a_replay_proof_package") as mock_build:
        mock_build.return_value = MOCK_PACKAGE
        
        with patch.object(sys, 'argv', ["prog", "build", "--evidence", mock_files["evidence"], "--contract", mock_files["contract"], "--out", mock_files["out"]]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == EXIT_OK
            
        with open(mock_files["out"], "r") as f:
            data = json.load(f)
            assert data == MOCK_PACKAGE

def test_build_fail_protocol(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.build_cluster_a_replay_proof_package") as mock_build:
        mock_build.side_effect = ValueError("protocol violation")
        
        with patch.object(sys, 'argv', ["prog", "build", "--evidence", mock_files["evidence"], "--contract", mock_files["contract"]]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == EXIT_ERROR
            
        captured = capsys.readouterr()
        res = json.loads(captured.out)
        assert res["error"] == E_BUILD_ERROR
        # strict determinism: no detail in default output
        assert "detail" not in res

def test_verify_success(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_package") as mock_verify:
        mock_verify.return_value = {"ok": True, "errors": []}
        
        with patch.object(sys, 'argv', ["prog", "verify", mock_files["package"]]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == EXIT_OK
            
        captured = capsys.readouterr()
        res = json.loads(captured.out)
        assert res["ok"] is True

def test_verify_failure(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_package") as mock_verify:
        mock_verify.return_value = {"ok": False, "errors": ["some_error"]}
        
        with patch.object(sys, 'argv', ["prog", "verify", mock_files["package"]]):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == EXIT_VERIFICATION_FAILED
            
        captured = capsys.readouterr()
        res = json.loads(captured.out)
        assert res["ok"] is False

def test_input_error_file_not_found(capsys):
    with patch.object(sys, 'argv', ["prog", "verify", "nonexistent.json"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == EXIT_ERROR
        
    captured = capsys.readouterr()
    res = json.loads(captured.out)
    assert res["error"] == E_FILE_NOT_FOUND

def test_input_error_invalid_json(mock_files, capsys):
    with patch.object(sys, 'argv', ["prog", "verify", mock_files["bad_json"]]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == EXIT_ERROR
        
    captured = capsys.readouterr()
    res = json.loads(captured.out)
    assert res["error"] == E_INVALID_JSON

def test_input_error_not_object(mock_files, capsys):
    with patch.object(sys, 'argv', ["prog", "verify", mock_files["list_json"]]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == EXIT_ERROR
        
    captured = capsys.readouterr()
    res = json.loads(captured.out)
    assert res["error"] == E_NOT_OBJECT
    
def test_output_pretty(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_package") as mock_verify:
        mock_verify.return_value = {"ok": True}
        
        with patch.object(sys, 'argv', ["prog", "verify", mock_files["package"], "--pretty"]):
            with pytest.raises(SystemExit):
                main()
            
        captured = capsys.readouterr()
        # Check for indentation/newlines
        assert "\n" in captured.out
        assert "  " in captured.out

def test_output_quiet(mock_files, capsys):
    with patch("ilc_core.cli.canon_cluster_a_replay_proof.verify_cluster_a_replay_proof_package") as mock_verify:
        mock_verify.return_value = {"ok": True}
        
        with patch.object(sys, 'argv', ["prog", "verify", mock_files["package"], "--quiet"]):
            with pytest.raises(SystemExit):
                main()
            
        captured = capsys.readouterr()
        assert captured.out == ""
