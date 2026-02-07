"""Tests for canon bundle key registry channel."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    load_channel_file,
    validate_channel_file,
    set_current_channel,
    list_channels,
    create_channel_file,
)


class TestValidateChannelFile:
    """Tests for validate_channel_file."""
    
    def _write_channel(self, tmp_path, data):
        path = tmp_path / "channel.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_valid_channel_file_passes(self, tmp_path):
        """Valid channel file passes validation."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["experimental", "main", "test"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is True
        assert len(result["errors"]) == 0

    def test_valid_v02_with_sources_passes(self, tmp_path):
        """Valid v0.2 channel file with sources passes validation."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["experimental", "main", "test"],
            "sources": {
                "experimental": ["file:///tmp/exp.bundle"],
                "main": ["/var/ilc/main.bundle"],
                "test": ["https://example.com/test.bundle"],
            },
        })

        result = validate_channel_file(path)
        assert result["ok"] is True
        assert len(result["errors"]) == 0

    def test_v02_sources_missing_channel_errors(self, tmp_path):
        """v0.2 sources must include all channels."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.2",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main", "test"],
            "sources": {
                "main": ["/var/ilc/main.bundle"],
            },
        })

        result = validate_channel_file(path)
        assert result["ok"] is False
        assert any(e.startswith("sources_missing:") for e in result["errors"])

    def test_v01_sources_ignored_warns(self, tmp_path):
        """v0.1 sources are ignored with warning."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "sources": {
                "main": ["/var/ilc/main.bundle"],
            },
        })

        result = validate_channel_file(path)
        assert result["ok"] is True
        assert "sources_ignored_v01" in result["warnings"]
    
    def test_invalid_channel_name_rejected(self, tmp_path):
        """Invalid channel name is rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "MAIN",
            "channels": ["MAIN"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert any("invalid_channel_format" in e for e in result["errors"])
    
    def test_duplicate_channels_rejected(self, tmp_path):
        """Duplicate channels are rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main", "main", "test"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert "duplicate_channels" in result["errors"]
    
    def test_unsorted_channels_warning(self, tmp_path):
        """Unsorted channels produce warning."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["test", "main"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is True
        assert "unsorted_channels" in result["warnings"]
    
    def test_empty_channels_rejected(self, tmp_path):
        """Empty channels list is rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": [],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert "empty_channels" in result["errors"]
    
    def test_missing_current_channel_rejected(self, tmp_path):
        """Missing current_channel is rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "channels": ["main"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert "missing_current_channel" in result["errors"]
    
    def test_current_not_in_channels_rejected(self, tmp_path):
        """Current channel not in channels list is rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "other",
            "channels": ["main"],
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert "current_channel_not_in_channels" in result["errors"]
    
    def test_unknown_field_rejected(self, tmp_path):
        """Unknown fields are rejected."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
            "extra_field": "not allowed",
        })
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert any("unknown_field" in e for e in result["errors"])
    
    def test_file_not_found(self, tmp_path):
        """Missing file returns error."""
        path = tmp_path / "nonexistent.json"
        
        result = validate_channel_file(path)
        assert result["ok"] is False
        assert "file_not_found" in result["errors"]


class TestSetCurrentChannel:
    """Tests for set_current_channel."""
    
    def _write_channel(self, tmp_path, data):
        path = tmp_path / "channel.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_set_existing_channel(self, tmp_path):
        """Setting existing channel works."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main", "test"],
        })
        
        result = set_current_channel(path, "test")
        assert result["ok"] is True
        assert result["current_channel"] == "test"
        
        # Verify file was updated
        data = json.loads(path.read_text())
        assert data["current_channel"] == "test"
    
    def test_set_missing_channel_fails(self, tmp_path):
        """Setting missing channel fails without force."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
        })
        
        result = set_current_channel(path, "test")
        assert result["ok"] is False
        assert result["error"] == "channel_not_found"
    
    def test_set_missing_channel_with_force(self, tmp_path):
        """Setting missing channel with force adds it."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
        })
        
        result = set_current_channel(path, "test", force=True)
        assert result["ok"] is True
        assert result["current_channel"] == "test"
        assert "channel_set_forced" in result["warnings"]
        
        # Verify file was updated
        data = json.loads(path.read_text())
        assert "test" in data["channels"]


class TestListChannels:
    """Tests for list_channels."""
    
    def _write_channel(self, tmp_path, data):
        path = tmp_path / "channel.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def test_list_channels_returns_current_and_list(self, tmp_path):
        """List returns current channel and channel list."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["experimental", "main", "test"],
        })
        
        result = list_channels(path)
        assert result["ok"] is True
        assert result["current_channel"] == "main"
        assert result["channels"] == ["experimental", "main", "test"]


class TestCreateChannelFile:
    """Tests for create_channel_file."""
    
    def test_create_new_file(self, tmp_path):
        """Creating new file works."""
        path = tmp_path / "channel.json"
        
        result = create_channel_file(path, "main")
        assert result["ok"] is True
        assert result["current_channel"] == "main"
        assert path.exists()
        
        data = json.loads(path.read_text())
        assert data["current_channel"] == "main"
        assert data["channels"] == ["main"]
    
    def test_create_fails_if_exists(self, tmp_path):
        """Create fails if file exists without force."""
        path = tmp_path / "channel.json"
        path.write_text("{}")
        
        result = create_channel_file(path, "main")
        assert result["ok"] is False
        assert result["error"] == "file_exists"


class TestChannelCli:
    """Tests for channel CLI."""
    
    def _write_channel(self, tmp_path, data):
        path = tmp_path / "channel.json"
        path.write_text(json.dumps(data, indent=2))
        return path
    
    def _run_cli(self, args):
        import subprocess
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_channel"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current"
        )
    
    def test_cli_validate(self, tmp_path):
        """CLI --validate works."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main"],
        })
        
        result = self._run_cli(["--file", str(path), "--validate"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_list(self, tmp_path):
        """CLI --list works."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main", "test"],
        })
        
        result = self._run_cli(["--file", str(path), "--list"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["current_channel"] == "main"
        assert output["channels"] == ["main", "test"]
    
    def test_cli_set(self, tmp_path):
        """CLI --set works."""
        path = self._write_channel(tmp_path, {
            "channel_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_channel": "main",
            "channels": ["main", "test"],
        })
        
        result = self._run_cli(["--file", str(path), "--set", "test"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["current_channel"] == "test"
    
    def test_cli_create(self, tmp_path):
        """CLI --create works."""
        path = tmp_path / "new_channel.json"
        
        result = self._run_cli(["--file", str(path), "--set", "main", "--create"])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["created"] is True
    
    def test_cli_io_error_returns_2(self, tmp_path):
        """CLI returns exit code 2 for IO errors."""
        path = tmp_path / "nonexistent.json"
        
        result = self._run_cli(["--file", str(path), "--validate"])
        assert result.returncode == 2
