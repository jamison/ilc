
import pytest
import json
import hashlib
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle

class TestCanonExportBundle:
    
    def test_bundle_creation(self, tmp_path):
        """Verify basic bundle creation."""
        bundle_dir = tmp_path / "bundle"
        
        export = {"canon_hash": "h1", "canon_export_format": "v0.1", "data": 123}
        validation = {"ok": True, "errors": [], "warnings": []}
        
        write_canon_export_bundle(export, validation, bundle_dir)
        
        assert bundle_dir.exists()
        assert (bundle_dir / "export.json").exists()
        assert (bundle_dir / "validate.json").exists()
        assert (bundle_dir / "manifest.json").exists()
        
        # Check integrity of manifest
        manifest = json.loads((bundle_dir / "manifest.json").read_text())
        assert manifest["bundle_format"] == "v0.1"
        assert manifest["canon_hash"] == "h1"
        
        # Verify hash match
        # Note: writer hashes the JSON bytes (no newline), but writes bytes + newline.
        # So we read file, strip newline, then hash? Or just trust the writer logic matches spec?
        # Let's verify against what's on disk.
        
        # The writer writes: json_bytes + \n
        # The manifest hash is sha256(json_bytes)
        
        export_on_disk = (bundle_dir / "export.json").read_bytes()
        # Strip trailing newline for verification math, if implementation does that.
        # Implementation:
        # export_bytes = json.dumps(...)
        # hash = sha256(export_bytes)
        # file.write(export_bytes + b"\n")
        
        # So manifest hash matches (file_content - last_byte)
        assert export_on_disk.endswith(b"\n")
        content_hashed = export_on_disk[:-1] 
        
        computed_hash = hashlib.sha256(content_hashed).hexdigest()
        assert computed_hash == manifest["export_hash"]

        validate_on_disk = (bundle_dir / "validate.json").read_bytes()
        assert validate_on_disk.endswith(b"\n")
        validate_hashed = validate_on_disk[:-1]
        computed_validate_hash = hashlib.sha256(validate_hashed).hexdigest()
        assert computed_validate_hash == manifest["validate_hash"]

    def test_overwrite_protection(self, tmp_path):
        """Should raise FileExistsError if folder not empty."""
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        (bundle_dir / "junk.txt").write_text("junk")
        
        export = {"canon_hash": "h1"}
        validation = {}
        
        with pytest.raises(FileExistsError):
            write_canon_export_bundle(export, validation, bundle_dir)
            
        # With overwrite=True
        write_canon_export_bundle(export, validation, bundle_dir, overwrite=True)
        assert (bundle_dir / "manifest.json").exists()

    def test_missing_canon_hash(self, tmp_path):
        """Should raise ValueError if export lacks canon_hash."""
        with pytest.raises(ValueError, match="missing required 'canon_hash'"):
            write_canon_export_bundle({}, {}, tmp_path / "bundle")

    def test_created_at_override(self, tmp_path):
        """Should respect passed timestamp."""
        bundle_dir = tmp_path / "bundle"
        ts = "2222-01-01T00:00:00Z"
        
        write_canon_export_bundle(
            {"canon_hash": "h"}, {}, bundle_dir, created_at=ts
        )
        
        manifest = json.loads((bundle_dir / "manifest.json").read_text())
        assert manifest["created_at"] == ts

    def test_deterministic_output(self, tmp_path):
        """Repeated writes of same data should yield identical hashes."""
        export = {"b": 2, "a": 1, "canon_hash": "h"} # Unsorted keys
        validation = {"ok": True}
        
        path1 = tmp_path / "b1"
        path2 = tmp_path / "b2"
        
        write_canon_export_bundle(export, validation, path1)
        write_canon_export_bundle(export, validation, path2)
        
        m1 = json.loads((path1 / "manifest.json").read_text())
        m2 = json.loads((path2 / "manifest.json").read_text())
        
        assert m1["export_hash"] == m2["export_hash"]
        
        # Also verify key sorting in export file
        e1_text = (path1 / "export.json").read_text().strip()
        # {"a":1,"b":2,"canon_hash":"h"} given alphabetical sort
        assert e1_text.startswith('{"a":1')
