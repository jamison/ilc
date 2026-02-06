"""Tests for canon bundle key registry format validation."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import validate_registry_file


class TestValidateRegistryFile:
    
    def _write_registry(self, tmp_path: Path, data: dict) -> Path:
        path = tmp_path / "registry.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path
    
    def test_valid_registry(self, tmp_path):
        """Valid registry passes validation."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": ["0011223344556677"],
            "deprecated_keys": ["deadbeefdeadbeef"],
        })
        result = validate_registry_file(path)
        assert result["ok"]
        assert result["errors"] == []
    
    def test_invalid_json(self, tmp_path):
        """Invalid JSON fails."""
        path = tmp_path / "registry.json"
        path.write_text("{not valid json", encoding="utf-8")
        result = validate_registry_file(path)
        assert not result["ok"]
        assert "invalid_json" in result["errors"]
    
    def test_missing_file(self, tmp_path):
        """Missing file fails."""
        path = tmp_path / "nonexistent.json"
        result = validate_registry_file(path)
        assert not result["ok"]
        assert "file_not_found" in result["errors"]
    
    def test_bad_key_pattern(self, tmp_path):
        """Invalid key pattern fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["INVALID"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert any("invalid_pattern" in e for e in result["errors"])
    
    def test_overlapping_keys(self, tmp_path):
        """Overlapping keys fail."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": ["a1b2c3d4e5f6a7b8"],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert any("overlapping_keys" in e for e in result["errors"])
    
    def test_duplicate_keys_in_list(self, tmp_path):
        """Duplicate keys within a list fail."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8", "a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert any("duplicate_keys" in e for e in result["errors"])
    
    def test_unsorted_keys_warning(self, tmp_path):
        """Unsorted keys produce warning."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["b1b2c3d4e5f6a7b8", "a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert result["ok"]
        assert any("unsorted_keys" in w for w in result["warnings"])
    
    def test_empty_current_keys_warning(self, tmp_path):
        """Empty current_keys produces warning by default."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert result["ok"]
        assert "empty_current_keys" in result["warnings"]
    
    def test_empty_current_keys_strict_error(self, tmp_path):
        """Empty current_keys is error in strict mode."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path, strict=True)
        assert not result["ok"]
        assert "empty_current_keys" in result["errors"]
    
    def test_invalid_updated_at(self, tmp_path):
        """Invalid timestamp fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "not-a-timestamp",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert "invalid_updated_at" in result["errors"]

    def test_updated_at_requires_timezone(self, tmp_path):
        """Naive timestamp without timezone fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert "invalid_updated_at" in result["errors"]
    
    def test_invalid_registry_version(self, tmp_path):
        """Invalid registry version fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.2",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert any("invalid_registry_version" in e for e in result["errors"])
    
    def test_unknown_field(self, tmp_path):
        """Unknown field fails."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
            "extra_field": "bad",
        })
        result = validate_registry_file(path)
        assert not result["ok"]
        assert any("unknown_fields" in e for e in result["errors"])
    
    def test_notes_field_allowed(self, tmp_path):
        """Notes field is allowed."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
            "notes": "Some notes here",
        })
        result = validate_registry_file(path)
        assert result["ok"]
