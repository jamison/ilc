"""
Tests for channel version fallback policy logic (Phase 132).
"""
import pytest
import json
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_sync import (
    evaluate_channel_version_policy,
    VersionPolicyDecision,
    sync_channel_registry,
    SyncContext,
)
from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file

class TestEvaluateChannelVersionPolicy:
    """Unit tests for the decision matrix."""

    def test_v04_always_allowed(self):
        """v0.4 is current and always allowed."""
        # Prod
        d = evaluate_channel_version_policy("v0.4", prod=True, allow_v03=False, allow_legacy=False, force=False)
        assert d.ok
        assert d.policy == "current"
        
        # Non-Prod
        d = evaluate_channel_version_policy("v0.4", prod=False, allow_v03=False, allow_legacy=False, force=False)
        assert d.ok

    def test_v03_in_prod_strict_rejection(self):
        """v0.3 in Prod is strictly rejected."""
        # No flags
        d = evaluate_channel_version_policy("v0.3", prod=True, allow_v03=False, allow_legacy=False, force=False)
        assert not d.ok
        assert d.policy == "rejected"
        assert "channel_version_unsupported_in_prod" in d.errors
        
        # With allow flag (no force)
        d = evaluate_channel_version_policy("v0.3", prod=True, allow_v03=True, allow_legacy=False, force=False)
        assert not d.ok
        assert "rollback_override_requires_force_in_prod" in d.errors
        
        # With allow + force (still forbidden per current policy)
        d = evaluate_channel_version_policy("v0.3", prod=True, allow_v03=True, allow_legacy=False, force=True)
        assert not d.ok
        assert "channel_version_breakglass_forbidden_in_prod" in d.errors

    def test_v03_in_non_prod(self):
        """v0.3 in Non-Prod requires explicit allow flag."""
        # Without flag
        d = evaluate_channel_version_policy("v0.3", prod=False, allow_v03=False, allow_legacy=False, force=False)
        assert not d.ok
        assert "channel_version_legacy_not_allowed" in d.errors
        
        # With flag
        d = evaluate_channel_version_policy("v0.3", prod=False, allow_v03=True, allow_legacy=False, force=False)
        assert d.ok
        assert d.policy == "compat_v03"
        assert "channel_version_v03_compat_mode" in d.warnings

    def test_legacy_v02_v01_in_prod(self):
        """v0.2/v0.1 in Prod is strictly forbidden."""
        for v in ["v0.2", "v0.1"]:
            d = evaluate_channel_version_policy(v, prod=True, allow_v03=False, allow_legacy=True, force=True)
            assert not d.ok
            assert "channel_version_breakglass_forbidden_in_prod" in d.errors

    def test_legacy_v02_v01_in_non_prod(self):
        """v0.2/v0.1 in Non-Prod requires allow_legacy flag."""
        v = "v0.2"
        # Without flag
        d = evaluate_channel_version_policy(v, prod=False, allow_v03=False, allow_legacy=False, force=False)
        assert not d.ok
        assert "channel_version_legacy_not_allowed" in d.errors
        
        # With flag
        d = evaluate_channel_version_policy(v, prod=False, allow_v03=False, allow_legacy=True, force=False)
        assert d.ok
        assert d.policy == "legacy_breakglass"
        assert "channel_version_legacy_breakglass_used" in d.warnings

    def test_invalid_versions(self):
        """Invalid or missing versions are rejected."""
        for v in [None, "", "v0.0", "v0.5", "foo", 1, True, []]:
            d = evaluate_channel_version_policy(v, prod=False, allow_v03=True, allow_legacy=True, force=True)
            assert not d.ok
            assert d.policy == "rejected"


class TestSyncIntegrationPolicy:
    """Integration tests for version policy enforcement in sync flow."""
    
    def _create_fixture(self, tmp_path, version="v0.4"):
        """Create signed channel file with specific version."""
        registry_path = tmp_path / "source" / "registry.json"
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({
            "registry_version": "v0.1",
            "updated_at": "2026-02-08T00:00:00Z",
            "current_keys": ["a1b2c3d4e5f6a7b8"],
            "previous_keys": [],
            "deprecated_keys": [],
        }))
        key = b"test-key"
        
        bundle_parent = tmp_path / "bundles"
        build_registry_bundle(registry_path, key, bundle_parent)
        bundle_dir = bundle_parent / "canon_key_registry_bundle_v0.1"
        
        channel_file = tmp_path / "channel.json"
        channel_data = {
            "channel_version": version,
            "updated_at": "2026-02-08T00:00:00Z",
            "published_at": "2026-02-08T00:00:00Z",
            "channel_seq": 1,
            "current_channel": "main",
            "channels": ["main"],
            "sources": {"main": [str(bundle_dir)]},
        }
        channel_file.write_text(json.dumps(channel_data, indent=2))
        
        channel_key = b"channel-key"
        sign_channel_file(channel_file, channel_key)
        
        return channel_file, key, channel_key

    def test_sync_telemetry_fields_present_on_success(self, tmp_path):
        """Result contains policy fields on success."""
        channel_file, key, channel_key = self._create_fixture(tmp_path, "v0.4")
        dest_dir = tmp_path / "installed"
        
        ctx = SyncContext(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, prod=True,
        )
        res = sync_channel_registry(ctx)
        
        assert res["ok"]
        assert res["channel_version"] == "v0.4"
        assert res["channel_version_policy"] == "current"
        assert res["channel_version_override_used"] is False

    def test_sync_telemetry_fields_present_on_failure(self, tmp_path):
        """Result contains policy fields on failure (policy rejection)."""
        channel_file, key, channel_key = self._create_fixture(tmp_path, "v0.3")
        dest_dir = tmp_path / "installed"
        
        # Prod rejects v0.3
        ctx = SyncContext(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, prod=True,
        )
        res = sync_channel_registry(ctx)
        
        assert not res["ok"]
        assert res["channel_version"] == "v0.3"
        # Policy evaluation should return rejected
        assert "channel_version_policy" in res
        assert res["channel_version_policy"] == "rejected"

    def test_sync_compat_mode_telemetry(self, tmp_path):
        """Result correctly flags override usage in non-prod compat mode."""
        channel_file, key, channel_key = self._create_fixture(tmp_path, "v0.3")
        dest_dir = tmp_path / "installed"
        
        # Non-prod with allow flag
        ctx = SyncContext(
            channel_file, key, dest_dir, channel="main",
            channel_key=channel_key, prod=False,
            allow_legacy_channel_v03=True
        )
        res = sync_channel_registry(ctx)
        
        assert res["ok"]
        assert res["channel_version"] == "v0.3"
        assert res["channel_version_policy"] == "compat_v03"
        assert res["channel_version_override_used"] is True
