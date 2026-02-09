"""
Integration tests for Canon Bundle Key Registry (Phase 133).
Validates end-to-end sync flows, policy enforcement, rollback protection, and telemetry.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List, Optional

from ilc_core.ledger.canon_bundle_key_registry_sync import (
    sync_channel_registry,
    SyncContext,
)
from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file
from ilc_core.ledger.canon_bundle_key_registry_sync_state import load_sync_state

# --- Helpers ---

def _build_signed_channel(
    tmp_path: Path, 
    *, 
    version: str, 
    seq: int, 
    source_path: str, 
    key: bytes,
    sources_dict: Optional[Dict[str, List[str]]] = None
) -> Path:
    """Helper to create and sign a channel file."""
    channel_file = tmp_path / "channel.json"
    
    # Allow overriding sources for failover tests
    sources = sources_dict if sources_dict else {"main": [source_path]}
    
    data: Dict[str, Any] = {
        "channel_version": version,
        "updated_at": "2026-02-08T00:00:00Z",
        "current_channel": "main",
        "channels": ["main"],
        "sources": sources,
    }
    
    if version == "v0.4":
        data["published_at"] = "2026-02-08T00:00:00Z"
        data["channel_seq"] = seq
        
    channel_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    sign_channel_file(channel_file, key)
    return channel_file

def _run_sync(channel_file: Path, key: bytes, dest_dir: Path, **kwargs) -> Dict[str, Any]:
    """Helper wrapper for sync_channel_registry."""
    ctx = SyncContext(
        channel_file=channel_file,
        key=key,
        dest_dir=dest_dir,
        channel="main",
        **kwargs,
    )
    return sync_channel_registry(ctx)

def _create_bundle(tmp_path: Path, key: bytes) -> str:
    """Helper to create a valid bundle and return its directory path."""
    registry_path = tmp_path / "registry_source.json"
    registry_path.write_text(json.dumps({
        "registry_version": "v0.1",
        "updated_at": "2026-02-08T00:00:00Z",
        "current_keys": ["a1b2c3d4e5f6a7b8"], # Valid hex key
        "previous_keys": [],
        "deprecated_keys": [],
    }))
    
    bundle_parent = tmp_path / "bundles"
    bundle_parent.mkdir(exist_ok=True)
    res = build_registry_bundle(registry_path, key, bundle_parent, force=True)
    assert res["ok"]
    return res["bundle_dir"]

# --- Test Class ---

class TestCanonBundleKeyRegistryIntegration:
    """End-to-end integration tests for registry sync."""

    @pytest.fixture
    def key(self):
        return b"test-key-32-bytes-00000000000000"

    @pytest.fixture
    def channel_key(self):
        return b"channel-key-32-bytes-00000000000"

    def test_scenario_a_prod_success_v04(self, tmp_path, key, channel_key):
        """Scenario A: Baseline prod success (v0.4)."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=10, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        res = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res["ok"] is True
        assert res["channel_version"] == "v0.4"
        assert res["channel_version_policy"] == "current"
        assert res["rollback_check_applied"] is True
        
        # Verify install
        # Bundle is installed as a subdirectory
        assert (dest_dir / "canon_key_registry_bundle_v0.1" / "canon_key_registry_v0.1.json").exists()
        assert (dest_dir / "canon_key_registry_bundle_v0.1" / "registry_manifest.json").exists()

    def test_scenario_b_idempotent_replay(self, tmp_path, key, channel_key):
        """Scenario B: Idempotent replay (same seq/hash)."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=10, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        # First Run
        res1 = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        assert res1["ok"] is True
        
        # Second Run (Idempotent)
        res2 = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        assert res2["ok"] is True
        assert res2["channel_version"] == "v0.4"
        assert res2["rollback_check_applied"] is True
        assert "channel_rollback_detected" not in res2.get("errors", [])

    def test_scenario_c_rollback_rejection(self, tmp_path, key, channel_key):
        """Scenario C: Rollback rejection (lower seq)."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        # 1. Sync High Seq
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=20, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        res1 = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        assert res1["ok"] is True
        
        # 2. Sync Low Seq (Rollback Attempt)
        _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=10, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        res2 = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res2["ok"] is False
        assert "channel_rollback_detected" in res2["errors"]
        assert res2["rollback_check_applied"] is True

    def test_scenario_d_prod_reject_v03(self, tmp_path, key, channel_key):
        """Scenario D: v0.3 policy in prod rejected."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.3", 
            seq=1, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        res = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res["ok"] is False
        assert "channel_version_unsupported_in_prod" in res["errors"]
        assert res["channel_version_policy"] == "rejected"
        assert res["channel_version"] == "v0.3"

    def test_scenario_e_non_prod_compat_v03(self, tmp_path, key, channel_key):
        """Scenario E: v0.3 policy non-prod compat allowed."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.3", 
            seq=1, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        res = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=False,
            allow_legacy_channel_v03=True
        )
        
        assert res["ok"] is True
        assert res["channel_version"] == "v0.3"
        assert res["channel_version_policy"] == "compat_v03"
        assert "channel_version_v03_compat_mode" in res["warnings"]

    def test_scenario_f_legacy_breakglass(self, tmp_path, key, channel_key):
        """Scenario F: Legacy breakglass path (v0.2/v0.1)."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.2", 
            seq=1, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        # 1. Non-prod with flag -> Success
        res1 = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=False,
            allow_legacy_channel_v02_v01=True
        )
        assert res1["ok"] is True
        assert res1["channel_version"] == "v0.2"
        assert res1["channel_version_policy"] == "legacy_breakglass"
        assert "channel_version_legacy_breakglass_used" in res1["warnings"]
        
        # 2. Prod -> Rejected
        res2 = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=True,
            # Even with flags, prod should reject or demand force+breakglass logic if implemented,
            # but current policy says legacy forbidden in prod generally.
            allow_legacy_channel_v02_v01=True,
            force=True
        )
        assert res2["ok"] is False
        assert "channel_version_breakglass_forbidden_in_prod" in res2["errors"]

    def test_scenario_g_failover_source_selection(self, tmp_path, key, channel_key):
        """Scenario G: Failover source selection."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        # Sources: 1st invalid, 2nd valid
        sources = {
            "main": ["/invalid/path/to/bundle", str(bundle_dir)]
        }
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=1, 
            source_path="", # Overridden
            sources_dict=sources,
            key=channel_key
        )
        
        res = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res["ok"] is True
        assert res["attempted_sources"] == 2
        assert res["failed_sources"] == 1
        assert res["source"] == str(bundle_dir)
        # Verify first failure reason recorded in telemetry
        assert "source_not_found" in res["last_sync"]["source_attempts"][0]["errors"]

    def test_scenario_h_dest_exists_behavior(self, tmp_path, key, channel_key):
        """Scenario H: Destination-exists behavior."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        # Pre-create destination bundle dir to trigger conflict
        target_bundle = dest_dir / "canon_key_registry_bundle_v0.1"
        target_bundle.mkdir(parents=True)
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=1, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        # 1. No Force -> Fail
        res1 = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        assert res1["ok"] is False
        assert "dest_exists" in res1["errors"]
        
        # 2. Force -> Success
        res2 = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=True, 
            force=True
        )
        assert res2["ok"] is True

    def test_scenario_i_dry_run(self, tmp_path, key, channel_key):
        """Scenario I: Dry-run semantics."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        dest_dir.mkdir() # Ensure root exists
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=1, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        before_files = list(dest_dir.iterdir())
        
        res = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=True, 
            dry_run=True
        )
        
        after_files = list(dest_dir.iterdir())
        
        assert res["ok"] is True
        assert before_files == after_files # No artifacts written
        assert "channel_version" in res # Telemetry still present
        # Sync state should NOT be written
        assert not (dest_dir.parent / "channel.json.sync_state.json").exists()

    def test_scenario_j_sidecar_artifacts(self, tmp_path, key, channel_key):
        """Scenario J: Sidecar artifacts semantics."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=5, 
            source_path=str(bundle_dir), 
            key=channel_key
        )
        
        _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        # 1. Last Sync File
        last_sync_path = channel_file.with_suffix(channel_file.suffix + ".last_sync.json")
        assert last_sync_path.exists()
        last_sync = json.loads(last_sync_path.read_text())
        assert last_sync["ok"] is True
        assert last_sync["channel"] == "main"
        assert "timestamp" in last_sync
        
        # 2. Sync State File
        sync_state_path = channel_file.with_suffix(channel_file.suffix + ".sync_state.json")
        assert sync_state_path.exists()
        sync_state = json.loads(sync_state_path.read_text())
        assert sync_state["seen_seq"] == 5

    def test_scenario_k_version_policy_invariants(self, tmp_path, key, channel_key):
        """Scenario K: Version-policy shape invariants."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        # Test Success Case (v0.4)
        channel_file_v4 = _build_signed_channel(
            tmp_path, version="v0.4", seq=1, source_path=str(bundle_dir), key=channel_key
        )
        res_ok = _run_sync(channel_file_v4, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert "channel_version" in res_ok
        assert "channel_version_policy" in res_ok
        assert "channel_version_override_used" in res_ok
        assert res_ok["channel_version_override_used"] is False

        # Test Failure Case (v0.3 in Prod)
        channel_file_v3 = _build_signed_channel(
            tmp_path, version="v0.3", seq=1, source_path=str(bundle_dir), key=channel_key
        )
        res_fail = _run_sync(channel_file_v3, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert "channel_version" in res_fail
        assert "channel_version_policy" in res_fail
        assert "channel_version_override_used" in res_fail
        assert res_fail["channel_version_override_used"] is False

    def test_scenario_l_deterministic_failure_envelope(self, tmp_path, key, channel_key):
        """Scenario L: Deterministic failure envelope."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, version="v0.3", seq=1, source_path=str(bundle_dir), key=channel_key
        )
        res = _run_sync(channel_file, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res["ok"] is False
        assert isinstance(res["errors"], list)
        assert isinstance(res["warnings"], list)
        assert res["errors"] == ["channel_version_unsupported_in_prod"]
        # Ensure no unstable/free-text suffix
        
    def test_scenario_m_legacy_rollback_semantics(self, tmp_path, key, channel_key):
        """Scenario M: Legacy compatibility rollback semantics."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        channel_file = _build_signed_channel(
            tmp_path, version="v0.3", seq=1, source_path=str(bundle_dir), key=channel_key
        )
        
        res = _run_sync(
            channel_file, 
            key, 
            dest_dir, 
            channel_key=channel_key, 
            prod=False,
            allow_legacy_channel_v03=True
        )
        
        assert res["ok"] is True
        assert res["channel_version_policy"] == "compat_v03"
        # Legacy channels do NOT trigger rollback check (no seq)
        assert res.get("rollback_check_applied") is False
        # Sync state should NOT be written for legacy channel
        sync_state_path = channel_file.with_suffix(channel_file.suffix + ".sync_state.json")
        assert not sync_state_path.exists()

    def test_scenario_n_local_canon_history_invariant(self, tmp_path, key, channel_key):
        """Scenario N: Local canon/history invariant (hash conflict)."""
        bundle_dir = _create_bundle(tmp_path, key)
        dest_dir = tmp_path / "installed"
        
        # 1. Sync Base State
        channel_file_1 = _build_signed_channel(
            tmp_path, version="v0.4", seq=10, source_path=str(bundle_dir), key=channel_key
        )
        res1 = _run_sync(channel_file_1, key, dest_dir, channel_key=channel_key, prod=True)
        assert res1["ok"] is True
        
        # 2. Sync Conflict (Same Seq, Different Hash/Content)
        # To simulate different hash, we need a bundle with different content or just same bundle?
        # Sync state tracks channel hash. Channel hash covers the source pointers.
        # If we change the source path or any field in channel file, hash changes.
        
        # Make a second bundle or just use same bundle but change channel metadata? 
        # Changing channel metadata (e.g. timestamp) changes channel hash.
        # _build_signed_channel uses fixed timestamp unless modified, but I can ask it to use different sources?
        
        # Let's create a scenario where the channel hash differs for same seq.
        # We can modify the channel file manually or use _build_signed_channel with different input.
        
        # Different source path => different channel hash
        bundle_dir_2 = tmp_path / "bundle_v2"
        bundle_dir_2.mkdir()
        # (Content doesn't matter for channel hash, just the string in "sources")
        
        channel_file_2 = _build_signed_channel(
            tmp_path, 
            version="v0.4", 
            seq=10, # Same sequence
            source_path=str(bundle_dir_2), # Different source -> Different Channel content -> Different Hash
            key=channel_key
        )
        
        res2 = _run_sync(channel_file_2, key, dest_dir, channel_key=channel_key, prod=True)
        
        assert res2["ok"] is False
        assert "channel_seq_hash_conflict" in res2["errors"]
        assert res2["rollback_check_applied"] is True
