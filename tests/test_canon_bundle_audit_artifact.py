
import pytest
import subprocess
import sys
import base64
import json
import hashlib
from pathlib import Path

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_pipeline"]
USE_TESTING_CANON_EXPORT_SNAPSHOT = True
TESTING_CANON_EXPORT_SNAPSHOT = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "canon_bundle_valid_export_v0_1_snapshot.json"
)


def _testing_export_snapshot() -> dict:
    if not USE_TESTING_CANON_EXPORT_SNAPSHOT:
        raise AssertionError("canon_bundle_testing_snapshot_disabled")
    return json.loads(TESTING_CANON_EXPORT_SNAPSHOT.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _allow_empty_key_registry(monkeypatch):
    monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")


class TestCanonBundleAuditArtifact:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        bundle = tmp_path / "bundle"
        export = _testing_export_snapshot()
        validation = {"ok": True, "errors": [], "warnings": []}
        write_canon_export_bundle(export, validation, bundle)
        return bundle

    @pytest.fixture
    def key_file(self, tmp_path):
        p = tmp_path / "key.txt"
        p.write_text(base64.b64encode(b"secret").decode())
        return p

    def run_cli(self, args):
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )

    def test_audit_file_created(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        assert audit_path.exists()

    def test_audit_contains_expected_keys(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        expected_keys = [
            "audit_version", "bundle_path", "timestamp", "pipeline_ok",
            "errors", "warnings", "steps", "report_path", "audit_path",
            "bundle_exists", "signature_present", "manifest_hash",
            "signature_hash", "report_hash", "pipeline_json"
        ]
        for key in expected_keys:
            assert key in audit, f"Missing key: {key}"

    def test_manifest_hash_matches(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        manifest_path = valid_bundle / "manifest.json"
        expected_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        assert audit["manifest_hash"] == expected_hash

    def test_signature_hash_matches(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        sig_path = valid_bundle / "manifest.sig"
        expected_hash = hashlib.sha256(sig_path.read_bytes()).hexdigest()
        assert audit["signature_hash"] == expected_hash
        assert audit["signature_present"] is True

    def test_missing_signature_null_hash(self, valid_bundle, tmp_path):
        # No key file means no signing
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        assert audit["signature_hash"] is None
        assert audit["signature_present"] is False

    def test_report_hash_present(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        assert audit["report_hash"] is not None
        # Verify it matches actual report
        expected_hash = hashlib.sha256(report_path.read_text().encode("utf-8")).hexdigest()
        assert audit["report_hash"] == expected_hash

    def test_directory_resolves_correctly(self, valid_bundle, key_file, tmp_path):
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_dir)
        ])
        audit_path = report_dir / "bundle_pipeline_audit.json"
        assert audit_path.exists()
        
        report_path = report_dir / "bundle_pipeline_report.md"
        assert report_path.exists()

    def test_pipeline_json_matches_stdout(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        audit = json.loads(audit_path.read_text())
        
        assert audit["pipeline_json"] == result.stdout.strip()

    def test_audit_on_failure(self, tmp_path, key_file):
        report_path = tmp_path / "report.md"
        missing_bundle = tmp_path / "missing"
        self.run_cli([
            "--bundle", str(missing_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        assert audit_path.exists()
        audit = json.loads(audit_path.read_text())
        assert audit["pipeline_ok"] is False
        assert "bundle_missing" in audit["errors"]
