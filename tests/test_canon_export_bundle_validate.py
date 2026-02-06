
import pytest
import json
import hashlib
from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle

class TestCanonExportBundleValidate:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        
        export_content = b'{"canon_hash":"h1"}'
        validate_content = b'{"ok":true}'
        
        (bundle_dir / "export.json").write_bytes(export_content + b"\n")
        (bundle_dir / "validate.json").write_bytes(validate_content + b"\n")
        
        manifest = {
            "bundle_format": "v0.1",
            "export_format": "v0.1",
            "hash_alg": "sha256",
            "created_at": "2026-02-05T00:00:00Z",
            "export_hash": hashlib.sha256(export_content).hexdigest(),
            "validate_hash": hashlib.sha256(validate_content).hexdigest(),
            "canon_hash": "h1",
            "export_path": "export.json",
            "validate_path": "validate.json"
        }
        (bundle_dir / "manifest.json").write_text(json.dumps(manifest))
        return bundle_dir

    def test_verify_valid_bundle(self, valid_bundle):
        report = validate_canon_export_bundle(valid_bundle)
        assert report["ok"]
        assert not report["errors"]
        assert not report["warnings"]

    def test_verify_tampered_content(self, valid_bundle):
        (valid_bundle / "export.json").write_text("tampered\n")
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("export.json hash mismatch" in e for e in report["errors"])

    def test_verify_missing_file(self, valid_bundle):
        (valid_bundle / "validate.json").unlink()
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("Missing required file" in e for e in report["errors"])

    def test_verify_missing_manifest(self, valid_bundle):
        (valid_bundle / "manifest.json").unlink()
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("Missing required file" in e for e in report["errors"])

    def test_verify_malformed_manifest(self, valid_bundle):
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        del data["bundle_format"]
        manifest_path.write_text(json.dumps(data))
        
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("Manifest missing keys" in e for e in report["errors"])

    def test_verify_unknown_keys(self, valid_bundle):
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["extra_field"] = "something"
        manifest_path.write_text(json.dumps(data))
        
        report = validate_canon_export_bundle(valid_bundle)
        assert report["ok"] # Unknown keys are OK, just warning
        assert any("Manifest contains unknown keys" in w for w in report["warnings"])

    def test_verify_created_at_strict_iso8601_invalid(self, valid_bundle):
        """Invalid ISO-8601 format should produce error."""
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["created_at"] = "Feb 5, 2026 12:00"  # Natural language - invalid ISO
        manifest_path.write_text(json.dumps(data))

        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert "invalid_created_at" in report["errors"]

    def test_verify_created_at_strict_iso8601_valid_z(self, valid_bundle):
        """Valid ISO-8601 with Z suffix should pass."""
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["created_at"] = "2026-02-06T12:34:56Z"
        manifest_path.write_text(json.dumps(data))

        report = validate_canon_export_bundle(valid_bundle)
        assert report["ok"]

    def test_verify_created_at_strict_iso8601_valid_offset(self, valid_bundle):
        """Valid ISO-8601 with offset should pass."""
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["created_at"] = "2026-02-06T12:34:56+00:00"
        manifest_path.write_text(json.dumps(data))

        report = validate_canon_export_bundle(valid_bundle)
        assert report["ok"]

    def test_verify_created_at_non_string(self, valid_bundle):
        """Non-string created_at should produce error."""
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["created_at"] = 1234567890
        manifest_path.write_text(json.dumps(data))

        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert "created_at must be a string" in report["errors"]

    def test_verify_missing_export_format_warning(self, valid_bundle):
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        del data["export_format"]
        manifest_path.write_text(json.dumps(data))

        report = validate_canon_export_bundle(valid_bundle)
        assert report["ok"]
        assert any("Missing optional field 'export_format'" in w for w in report["warnings"])

    def test_verify_bad_paths(self, valid_bundle):
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["export_path"] = "../export.json"
        manifest_path.write_text(json.dumps(data))
        
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("Invalid export_path" in e for e in report["errors"])

    def test_verify_wrong_hash_alg(self, valid_bundle):
        manifest_path = valid_bundle / "manifest.json"
        data = json.loads(manifest_path.read_text())
        data["hash_alg"] = "md5"
        manifest_path.write_text(json.dumps(data))
        
        report = validate_canon_export_bundle(valid_bundle)
        assert not report["ok"]
        assert any("Unsupported hash_alg" in e for e in report["errors"])

