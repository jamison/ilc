"""Tests for canon bundle key registry."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import (
    KeyRegistry, load_registry, get_registry, set_registry, reset_registry, DEFAULT_REGISTRY
)


class TestKeyRegistry:
    
    def test_status_current(self):
        registry = KeyRegistry(current_keys=["abc123"])
        assert registry.status("abc123") == "current"
    
    def test_status_previous(self):
        registry = KeyRegistry(previous_keys=["old123"])
        assert registry.status("old123") == "previous"
    
    def test_status_deprecated(self):
        registry = KeyRegistry(deprecated_keys=["bad123"])
        assert registry.status("bad123") == "deprecated"
    
    def test_status_unknown(self):
        registry = KeyRegistry(current_keys=["abc123"])
        assert registry.status("xyz999") == "unknown"
    
    def test_empty_registry_returns_unknown_by_default(self, monkeypatch):
        """Empty registry treats all keys as unknown unless explicitly allowed."""
        monkeypatch.delenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", raising=False)
        registry = KeyRegistry()
        assert registry.is_empty()
        assert registry.status("any_key") == "unknown"

    def test_empty_registry_allows_when_env_set(self, monkeypatch):
        """Empty registry allows all keys when ILC_ALLOW_EMPTY_KEY_REGISTRY=1."""
        monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")
        registry = KeyRegistry()
        assert registry.is_empty()
        assert registry.status("any_key") == "current"
    
    def test_load_registry_from_file(self, tmp_path):
        registry_file = tmp_path / "registry.json"
        registry_file.write_text(json.dumps({
            "current_keys": ["key1"],
            "previous_keys": ["key2"],
            "deprecated_keys": ["key3"]
        }))
        
        registry = load_registry(registry_file)
        assert registry.status("key1") == "current"
        assert registry.status("key2") == "previous"
        assert registry.status("key3") == "deprecated"
    
    def test_load_registry_missing_file_returns_default(self, tmp_path):
        missing = tmp_path / "nonexistent.json"
        registry = load_registry(missing)
        assert registry == DEFAULT_REGISTRY
    
    def test_set_and_get_registry(self):
        """Test global registry management."""
        reset_registry()
        custom = KeyRegistry(current_keys=["custom123"])
        set_registry(custom)
        
        result = get_registry()
        assert result.status("custom123") == "current"
        
        reset_registry()
