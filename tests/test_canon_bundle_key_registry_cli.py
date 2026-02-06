"""Tests for canon bundle key registry CLI."""

import json
import pytest
import subprocess
import sys
from pathlib import Path


COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_key_registry"]


class TestCanonBundleKeyRegistryCli:
    
    def _write_registry(self, tmp_path: Path, data: dict) -> Path:
        path = tmp_path / "registry.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path
    
    def _run_cli(self, args: list) -> subprocess.CompletedProcess:
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )
    
    def test_valid_registry(self, tmp_path):
        """Valid registry returns exit code 0."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = self._run_cli(["--registry", str(path)])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["key_counts"]["current"] == 1
    
    def test_invalid_json_exit_code(self, tmp_path):
        """Invalid JSON returns exit code 1."""
        path = tmp_path / "registry.json"
        path.write_text("{invalid", encoding="utf-8")
        result = self._run_cli(["--registry", str(path)])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["ok"] is False

    def test_unreadable_file_exit_code(self, tmp_path):
        """Unreadable file returns exit code 2."""
        path = tmp_path / "registry.json"
        path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }), encoding="utf-8")
        path.chmod(0)
        try:
            result = self._run_cli(["--registry", str(path)])
            assert result.returncode == 2
            output = json.loads(result.stdout)
            assert "file_read_error" in output["errors"]
        finally:
            path.chmod(0o600)
    
    def test_missing_file_exit_code(self, tmp_path):
        """Missing file returns exit code 2."""
        path = tmp_path / "nonexistent.json"
        result = self._run_cli(["--registry", str(path)])
        assert result.returncode == 2
        output = json.loads(result.stdout)
        assert "file_not_found" in output["errors"]
    
    def test_strict_empty_current_keys(self, tmp_path):
        """Strict mode fails on empty current_keys."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = self._run_cli(["--registry", str(path), "--strict"])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["ok"] is False
        assert "empty_current_keys" in output["errors"]
    
    def test_allow_empty_overrides_strict(self, tmp_path):
        """Allow-empty overrides strict mode."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": [],
            "previous_keys": [],
            "deprecated_keys": [],
        })
        result = self._run_cli(["--registry", str(path), "--strict", "--allow-empty"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert "empty_current_keys" in output["warnings"]
    
    def test_output_contains_registry_path(self, tmp_path):
        """Output includes registry path."""
        path = self._write_registry(tmp_path, {
            "registry_version": "v0.1",
            "updated_at": "2026-02-06T21:30:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": ["0011223344556677"],
            "deprecated_keys": ["deadbeefdeadbeef"],
        })
        result = self._run_cli(["--registry", str(path)])
        output = json.loads(result.stdout)
        assert "registry_path" in output
        assert output["registry_version"] == "v0.1"
        assert output["key_counts"]["current"] == 1
        assert output["key_counts"]["previous"] == 1
        assert output["key_counts"]["deprecated"] == 1
