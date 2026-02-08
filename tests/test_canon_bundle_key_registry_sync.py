"""Tests for canon bundle key registry sync."""

import json
import pytest
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_sync import (
    sync_channel_registry,
    SyncContext,
)
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file


def call_sync(channel_file, key, dest_dir, **kwargs):
    """Helper to call sync_channel_registry with SyncContext."""
    ctx = SyncContext(channel_file, key, dest_dir, **kwargs)
    return sync_channel_registry(ctx)


class TestSyncChannelRegistry:
    """Tests for sync_channel_registry helper."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="main", num_sources=1):
        """Create a valid bundle and v0.2 channel file with sources."""
        # Create registry
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"
        
        # Build bundle
        bundle_parent = tmp_path / "bundles" / channel_name
        build_registry_bundle(registry_path, key, bundle_parent)
        # The actual bundle is at bundle_parent / "canon_key_registry_bundle_v0.1"
        bundle_dir = bundle_parent / "canon_key_registry_bundle_v0.1"
        
        # Create sources list
        sources = [str(bundle_dir)] * num_sources
        
        # Create channel file with sources pointing to actual bundle
        channel_file = tmp_path / "channel.json"
        
        channel_data = {
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": channel_name,
            "channels": ["experimental", "main", "test"],
            "sources": {
                "experimental": sources,
                "main": sources,
                "test": sources,
            },
        }
        channel_file.write_text(json.dumps(channel_data, indent=2))
        
        return bundle_dir, channel_file, key
    
    def test_sync_succeeds_for_valid_channel_local_source(self, tmp_path):
        """Sync succeeds for valid channel with local source."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is True
        assert result["channel"] == "main"
        assert (dest_dir / "canon_key_registry_bundle_v0.1").exists()
        
        # Verify audit metadata
        last_sync = result["last_sync"]
        assert last_sync["ok"] is True
        assert last_sync["selected_source_reason"] == "first_success"
        assert len(last_sync["source_attempts"]) == 1
        assert last_sync["source_attempts"][0]["ok"] is True
    
    def test_sync_falls_back_to_second_source_on_first_failure(self, tmp_path):
        """Sync falls back to second source on first failure."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, num_sources=2)
        
        # Manually break first source in channel file
        data = json.loads(channel_file.read_text())
        data["sources"]["main"][0] = "/invalid/path"
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is True
        assert result["installed_path"]
        assert result["successful_source_index"] == 1
        
        last_sync = result["last_sync"]
        assert last_sync["selected_source_reason"] == "failover_success"
        assert len(last_sync["source_attempts"]) == 2
        assert last_sync["source_attempts"][0]["ok"] is False
        assert last_sync["source_attempts"][1]["ok"] is True
    
    def test_sync_no_failover_stops_after_first_failure(self, tmp_path):
        """Sync with no-failover stops after first failure."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, num_sources=2)
        
        # Break first source
        data = json.loads(channel_file.read_text())
        data["sources"]["main"][0] = "/invalid/path"
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main", failover=False
        )
        
        assert result["ok"] is False
        assert result["failed_sources"] == 1
        
        last_sync = result["last_sync"]
        assert len(last_sync["source_attempts"]) == 1
        assert last_sync["selected_source_reason"] == "no_failover"
    
    def test_sync_all_sources_fail_returns_compact_summary(self, tmp_path):
        """Sync returns aggregate error when all sources fail."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, num_sources=2)
        
        # Break all sources
        data = json.loads(channel_file.read_text())
        data["sources"]["main"] = ["/invalid/1", "/invalid/2"]
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is False
        assert "sync_failed_all_sources" in result["errors"]
        assert result["failed_sources"] == 2
        
        last_sync = result["last_sync"]
        assert len(last_sync["source_attempts"]) == 2
        assert last_sync["selected_source_reason"] == "window_exhausted"
    
    def test_sync_max_sources_limits_attempt_count(self, tmp_path):
        """Sync respects max_sources limit."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, num_sources=3)
        
        # Break all sources
        data = json.loads(channel_file.read_text())
        data["sources"]["main"] = ["/invalid/1", "/invalid/2", "/invalid/3"]
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main", max_sources=2
        )
        
        assert result["ok"] is False
        assert result["attempted_sources"] == 2
        last_sync = result["last_sync"]
        assert len(last_sync["source_attempts"]) == 2
    
    def test_sync_fails_for_missing_sources_mapping(self, tmp_path):
        """Sync fails when sources mapping is missing."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": "main",
            "channels": ["main"],
        }))
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is False
        assert "sources_missing" in result["errors"]
        assert result["last_sync"]["ok"] is False
        assert "sources_missing" in result["last_sync"]["errors"]
    
    def test_sync_fails_for_source_index_out_of_range(self, tmp_path):
        """Sync fails when source_index is out of range."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main", source_index=5
        )
        
        assert result["ok"] is False
        assert "source_index_out_of_range" in result["errors"]
        assert result["last_sync"]["ok"] is False
        assert "source_index_out_of_range" in result["last_sync"]["errors"]
    
    def test_sync_respects_allow_network_flag(self, tmp_path):
        """Sync respects allow_network flag for https sources."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": "main",
            "channels": ["main"],
            "sources": {
                "main": ["https://example.com/bundle.tar.gz"],
            },
        }))
        
        key = b"test-signing-key"
        dest_dir = tmp_path / "installed"
        
        # Test failure without flag
        result = call_sync(
            channel_file, key, dest_dir, channel="main", allow_network=False
        )
        assert result["ok"] is False
        assert "network_disabled" in result["errors"]
        # Audit log should show attempt failed due to network
        assert result["last_sync"]["source_attempts"][0]["errors"] == ["network_disabled"]
    
    def test_dry_run_returns_plan(self, tmp_path):
        """Dry run returns plan without modifications."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main", dry_run=True
        )
        
        assert result["ok"] is True
        assert result["dry_run"] is True
        assert "sources_to_attempt" in result
        assert not (dest_dir / "canon_key_registry_bundle_v0.1").exists()
    
    def test_force_required_when_dest_exists(self, tmp_path):
        """Force is required when dest already has bundle."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        # First sync
        result1 = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        assert result1["ok"] is True
        
        # Second sync without force should fail
        result2 = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        assert result2["ok"] is False
        assert "dest_exists" in result2["errors"]
        assert result2["last_sync"]["ok"] is False
        assert "dest_exists" in result2["last_sync"]["errors"]
    
    def test_sync_uses_current_channel_by_default(self, tmp_path):
        """Sync uses current_channel when channel not specified."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path, channel_name="test")
        
        # Update current_channel
        data = json.loads(channel_file.read_text())
        data["current_channel"] = "test"
        channel_file.write_text(json.dumps(data))
        
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir
        )
        
        assert result["ok"] is True
        assert result["channel"] == "test"
    
    def test_sync_max_sources_invalid_returns_validation_error(self, tmp_path):
        """Sync returns error if max_sources < 1."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, max_sources=0
        )
        
        assert result["ok"] is False
        assert "max_sources_invalid" in result["errors"]
        assert result["last_sync"]["ok"] is False
        assert "max_sources_invalid" in result["last_sync"]["errors"]

    def test_sync_result_contain_freshness_fields(self, tmp_path):
        """Sync result contains freshness telemetry fields."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main"
        )
        
        assert result["ok"] is True
        assert "seen_seq" in result
        assert "seen_hash" in result
        assert "rollback_check_applied" in result
        assert result["rollback_check_applied"] is True  # v0.4 channel triggers check

    def test_sync_prod_rejects_legacy_channel_version(self, tmp_path):
        """Prod mode rejects channel versions older than v0.4."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"

        # Downgrade to v0.2
        data = json.loads(channel_file.read_text())
        data["channel_version"] = "v0.2"
        channel_file.write_text(json.dumps(data))

        result = call_sync(
            channel_file, key, dest_dir, channel="main", prod=True
        )

        assert result["ok"] is False
        assert "channel_version_breakglass_forbidden_in_prod" in result["errors"]



class TestSyncChannelSignaturePolicy(TestSyncChannelRegistry):
    """Tests for channel signature policy in sync."""
    
    def test_sync_missing_signature_warns_when_not_required(self, tmp_path):
        """Missing signature emits warning but proceeds if not required."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        channel_key = b"channel-key"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, 
            require_signed_channel=False
        )
        
        assert result["ok"] is True
        assert "channel_signature_missing_unenforced" in result["warnings"]

    def test_sync_required_signed_channel_missing_sig_fails(self, tmp_path):
        """Missing signature fails if required."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        channel_key = b"channel-key"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, 
            require_signed_channel=True
        )
        
        assert result["ok"] is False
        assert "channel_signature_missing" in result["errors"]

    def test_sync_invalid_signature_fails_even_when_not_required(self, tmp_path):
        """Invalid signature fails even if not required."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        channel_key = b"channel-key"
        
        # Create invalid sig
        sign_channel_file(channel_file, channel_key)
        sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
        sig_data = json.loads(sig_path.read_text())
        sig_data["channel_hash"] = "invalid"
        sig_path.write_text(json.dumps(sig_data))
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, 
            require_signed_channel=False
        )
        
        assert result["ok"] is False
        assert "channel_hash_mismatch" in result["errors"]

    def test_sync_valid_signature_allows_fetch(self, tmp_path):
        """Valid verify allows sync to proceed."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        channel_key = b"channel-key"
        
        sign_channel_file(channel_file, channel_key)
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, 
            require_signed_channel=True
        )
        
        assert result["ok"] is True
        assert not result["errors"]
        # Should not have missing warnings
        assert "channel_signature_missing_unenforced" not in result["warnings"]

    def test_sync_fails_if_required_but_no_key_provided(self, tmp_path):
        """Sync fails if required=True but no channel_key provided."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=None,
            require_signed_channel=True
        )
        
        assert result["ok"] is False
        assert "channel_key_missing_for_required_signature" in result["errors"]

    def test_sync_does_not_mutate_signed_channel_file(self, tmp_path):
        """Repeated signed syncs should not fail due to channel file mutation."""
        bundle_dir, channel_file, key = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        channel_key = b"channel-key"

        data = json.loads(channel_file.read_text())
        data["channel_version"] = "v0.4"
        data["published_at"] = "2026-02-08T12:00:00Z"
        data["channel_seq"] = 1
        channel_file.write_text(json.dumps(data))
        sign_channel_file(channel_file, channel_key)

        first = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key,
            prod=True,
        )
        assert first["ok"] is True

        second = call_sync(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key,
            prod=True,
            force=True,
        )
        assert second["ok"] is True
        assert "channel_hash_mismatch" not in second["errors"]
        assert "channel_signature_mismatch" not in second["errors"]


class TestSyncCli:
    """Tests for sync CLI."""
    
    def _create_bundle_and_channel(self, tmp_path, channel_name="main", num_sources=1):
        registry_path = tmp_path / "source" / "canon_key_registry_v0.1.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-07T10:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-signing-key"
        
        bundle_parent = tmp_path / "bundles" / channel_name
        build_registry_bundle(registry_path, key, bundle_parent)
        bundle_dir = bundle_parent / "canon_key_registry_bundle_v0.1"
        
        sources = [str(bundle_dir)] * num_sources
        
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": channel_name,
            "channels": [channel_name],
            "sources": {
                channel_name: sources,
            },
        }, indent=2))
        
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(key)

        channel_key = b"channel-signing-key"
        channel_key_file = tmp_path / "channel_key.txt"
        channel_key_file.write_bytes(channel_key)
        sign_channel_file(channel_file, channel_key)
        
        return bundle_dir, channel_file, key_file, channel_key_file
    
    def _run_cli(self, args, env=None):
        import subprocess
        import os
        environ = os.environ.copy()
        if env:
            environ.update(env)
            
        return subprocess.run(
            ["python3", "-m", "ilc_core.cli.canon_bundle_key_registry_sync"] + args,
            capture_output=True,
            text=True,
            cwd="/Users/jamstar/Documents/ILC_Main/01_Current",
            env=environ
        )
    
    def test_cli_sync_succeeds(self, tmp_path):
        """CLI sync succeeds."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
    
    def test_cli_failover_flags(self, tmp_path):
        """CLI accepts failover flags."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path, num_sources=2)
        dest_dir = tmp_path / "installed"
        
        # Test dry-run with no-failover
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
            "--dry-run",
            "--no-failover",
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["failover_enabled"] is False
        assert len(output["sources_to_attempt"]) == 1
    
    def test_cli_max_sources(self, tmp_path):
        """CLI respects max-sources."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path, num_sources=3)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
            "--dry-run",
            "--max-sources", "2",
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert len(output["sources_to_attempt"]) == 2

    def test_cli_dry_run(self, tmp_path):
        """CLI dry run works."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
            "--dry-run",
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["dry_run"] is True

    def test_cli_validation_error_returns_1(self, tmp_path):
        """CLI returns 1 for validation errors."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": "main",
            "channels": ["main"],
        }))
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(b"test-key")
        channel_key_file = tmp_path / "channel_key.txt"
        channel_key_file.write_bytes(b"channel-signing-key")
        sign_channel_file(channel_file, b"channel-signing-key")
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "sources_missing" in output["errors"]

    def test_cli_network_disabled_returns_1(self, tmp_path):
        """CLI returns 1 for network policy violation."""
        channel_file = tmp_path / "channel.json"
        channel_file.write_text(json.dumps({
            "channel_version": "v0.4",
            "updated_at": "2026-02-07T10:00:00Z",
            "published_at": "2026-02-07T10:00:00Z",
            "channel_seq": 1,
            "current_channel": "main",
            "channels": ["main"],
            "sources": {"main": ["https://example.com/bundle.tar.gz"]},
        }))
        key_file = tmp_path / "key.txt"
        key_file.write_bytes(b"test-key")
        channel_key_file = tmp_path / "channel_key.txt"
        channel_key_file.write_bytes(b"channel-signing-key")
        sign_channel_file(channel_file, b"channel-signing-key")
        dest_dir = tmp_path / "installed"

        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
        ])
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "network_disabled" in output["errors"]

    def test_cli_network_disabled_can_still_fallback_to_local_source(self, tmp_path):
        """CLI falls back to local source if network disabled."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path, num_sources=2)
        
        # Make first source https
        data = json.loads(channel_file.read_text())
        data["sources"]["main"][0] = "https://example.com/bundle.tar.gz"
        channel_file.write_text(json.dumps(data))
        sign_channel_file(channel_file, channel_key_file.read_bytes())
        
        dest_dir = tmp_path / "installed"
        
        # Run without --allow-network
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
        assert output["successful_source_index"] == 1
        assert output["last_sync"]["source_attempts"][0]["errors"] == ["network_disabled"]

    def test_cli_require_signed_channel_env(self, tmp_path):
        """CLI respects env var for requiring signature."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        sig_file = channel_file.with_suffix(channel_file.suffix + ".sig")
        sig_file.unlink()
        
        # Should fail with missing signature when policy requires signature.
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
        ], env={"ILC_REQUIRE_SIGNED_CHANNEL": "1"})
        
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "channel_signature_missing" in output["errors"]

    def test_cli_prod_mode_still_requires_signed_channel_key(self, tmp_path):
        """Prod mode enforces signed channel policy even if no-require flag is set."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--dest", str(dest_dir),
            "--no-require-signed-channel"
        ], env={"ILC_REQUIRE_SIGNED_CHANNEL": "1"})
        
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "channel_key_missing_for_required_signature" in output["errors"]

    def test_cli_rollback_flags(self, tmp_path):
        """CLI accepts rollback flags."""
        bundle_dir, channel_file, key_file, channel_key_file = self._create_bundle_and_channel(tmp_path)
        dest_dir = tmp_path / "installed"
        state_file = tmp_path / "manual_state.json"
        
        result = self._run_cli([
            "--channel-file", str(channel_file),
            "--key-file", str(key_file),
            "--channel-key-file", str(channel_key_file),
            "--dest", str(dest_dir),
            "--allow-channel-rollback",
            "--sync-state-file", str(state_file),
            "--dry-run"
        ])
        
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["ok"] is True
