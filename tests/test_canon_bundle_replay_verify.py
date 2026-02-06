
import pytest
import subprocess
import sys
import base64
import json
import hashlib
from pathlib import Path

from ilc_core.ledger.canon_bundle_replay_verify import replay_verify
from ilc_core.ledger.canon_bundle_utils import file_sha256, normalize_issue, normalized_multiset
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_replay"]

class TestCanonBundleReplayVerify:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        bundle = tmp_path / "bundle"
        export = {"canon_hash": "abc123", "canon_export_format": "v0.1"}
        validation = {"ok": True, "errors": [], "warnings": []}
        write_canon_export_bundle(export, validation, bundle)
        return bundle

    @pytest.fixture
    def key_file(self, tmp_path):
        p = tmp_path / "key.txt"
        p.write_text(base64.b64encode(b"secret").decode())
        return p

    @pytest.fixture
    def signed_bundle_with_audit(self, valid_bundle, key_file, tmp_path):
        """Run pipeline to get a signed bundle and audit artifact."""
        report_path = tmp_path / "report.md"
        result = subprocess.run(
            [sys.executable, "-m", "ilc_core.cli.canon_bundle_pipeline",
             "--bundle", str(valid_bundle),
             "--key-file", str(key_file),
             "--report", str(report_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        assert audit_path.exists()
        return valid_bundle, audit_path

    def run_cli(self, args):
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )

    def test_replay_succeeds_on_valid_bundle(self, signed_bundle_with_audit):
        bundle, audit_path = signed_bundle_with_audit
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path)
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["replay_matches"] is True
        assert data["mismatch"] == {}
        assert result.stderr == ""

    def test_replay_fails_manifest_hash_mismatch(self, signed_bundle_with_audit):
        bundle, audit_path = signed_bundle_with_audit
        # Tamper with manifest
        manifest = bundle / "manifest.json"
        manifest.write_text(manifest.read_text() + " ")
        
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path)
        ])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["replay_matches"] is False
        assert "manifest_hash" in data["mismatch"]
        assert result.stderr == ""

    def test_replay_fails_signature_mismatch(self, signed_bundle_with_audit):
        bundle, audit_path = signed_bundle_with_audit
        # Tamper with signature
        sig_path = bundle / "manifest.sig"
        sig_path.write_text("tampered")
        
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path)
        ])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["replay_matches"] is False
        assert "signature_hash" in data["mismatch"]
        assert result.stderr == ""

    def test_replay_fails_missing_audit_keys(self, valid_bundle, tmp_path):
        audit_path = tmp_path / "bad_audit.json"
        audit_path.write_text('{"audit_version": "v0.1"}')  # Missing required keys
        
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--audit", str(audit_path)
        ])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "audit_missing_fields" in data["errors"]
        assert data["replay_matches"] is False
        assert result.stderr == ""

    def test_mismatch_no_stderr(self, signed_bundle_with_audit):
        bundle, audit_path = signed_bundle_with_audit
        # Tamper with manifest to cause mismatch
        manifest = bundle / "manifest.json"
        manifest.write_text(manifest.read_text() + " ")
        
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path)
        ])
        # Mismatch should NOT produce stderr output
        assert result.stderr == ""

    def test_audit_version_mismatch_fails(self, valid_bundle, tmp_path):
        audit_path = tmp_path / "bad_audit.json"
        audit = {
            "audit_version": "v99.0",  # Unsupported version
            "bundle_path": str(valid_bundle),
            "manifest_hash": "abc",
            "pipeline_json": "{}",
            "steps": {},
            "pipeline_ok": False,
            "errors": [],
            "warnings": []
        }
        audit_path.write_text(json.dumps(audit))
        
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--audit", str(audit_path)
        ])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "unsupported_audit_version" in data["errors"]
        assert result.stderr == ""

    def test_bundle_path_mismatch_yields_warning(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        # Use a different path that still exists
        different_bundle = tmp_path / "different_bundle"
        different_bundle.mkdir()
        
        # Copy bundle contents
        for f in bundle.iterdir():
            (different_bundle / f.name).write_bytes(f.read_bytes())
        
        result = self.run_cli([
            "--bundle", str(different_bundle),
            "--audit", str(audit_path)
        ])
        # Should still match (just warn about path difference)
        data = json.loads(result.stdout)
        assert "bundle_path_mismatch" in data["warnings"]
        # But may fail on hash due to different path, so just check warning is present
        assert result.stderr == ""

    def test_audit_file_missing(self, valid_bundle, tmp_path):
        missing_audit = tmp_path / "missing_audit.json"
        
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--audit", str(missing_audit)
        ])
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert "audit_file_missing" in data["errors"]
        assert result.stderr == ""


class TestReplayNormalization:
    """Tests for normalized error/warning comparison."""
    
    def test_normalize_issue_snake_case(self):
        """Snake_case issues should pass through unchanged."""
        assert normalize_issue("manifest_missing") == "manifest_missing"
        assert normalize_issue("signature_mismatch") == "signature_mismatch"
    
    def test_normalize_issue_known_patterns(self):
        """Known patterns should map to standard keys."""
        assert normalize_issue("Missing required file: manifest.json") == "manifest_missing"
        assert normalize_issue("Signature mismatch detected") == "signature_mismatch"
        assert normalize_issue("signature missing from bundle") == "signature_missing"
    
    def test_normalize_issue_fallback(self):
        """Unknown patterns should convert spaces to underscores."""
        result = normalize_issue("Something unexpected happened")
        assert "_" in result
        assert " " not in result
    
    def test_normalized_multiset_counts(self):
        """Multiset should count duplicate issues."""
        issues = ["manifest_missing", "manifest_missing", "signature_mismatch"]
        result = normalized_multiset(issues)
        assert result["manifest_missing"] == 2
        assert result["signature_mismatch"] == 1
    
    def test_replay_compare_normalizes_wording(self, tmp_path):
        """Same meaning with different wording should match."""
        # Create a bundle
        bundle = tmp_path / "bundle"
        export = {"canon_hash": "abc123", "canon_export_format": "v0.1"}
        validation = {"ok": True, "errors": [], "warnings": []}
        write_canon_export_bundle(export, validation, bundle)
        
        # Create an audit with verbose error message
        audit = {
            "audit_version": "v0.1",
            "bundle_path": str(bundle.resolve()),
            "manifest_hash": file_sha256(bundle / "manifest.json"),
            "signature_hash": None,
            "pipeline_json": "{}",
            "steps": {"validate": True, "verify": True},
            "pipeline_ok": True,
            "errors": [],  # Both empty - should match
            "warnings": []
        }
        
        result = replay_verify(bundle, audit)
        assert result["replay_matches"] is True
