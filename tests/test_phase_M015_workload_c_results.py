"""
M-015 Workload C Tier 2: canonical results artifact tests.

The tracked M-015 artifact now records the final protocol-driven recovery packet,
not the earlier Tier 1 process-kill precursor.
"""

from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_mysticeti_workload_c_results_M015_v0.1.md")
RUNNER_PATH = Path("tools/testbed/ilc_loopback_m015_runner_tier2.sh")
NODE_PATH = Path("ilc_consensus/src/node.rs")
SETTLEMENT_PATH = Path("ilc_consensus/src/epoch_settlement.rs")


def _artifact() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_m015_artifact_and_runner_exist() -> None:
    assert ARTIFACT_PATH.is_file(), "canonical M-015 artifact missing"
    assert RUNNER_PATH.is_file(), "Tier 2 runner missing"


def test_m015_artifact_declares_tier2_supersession() -> None:
    text = _artifact()
    assert "supersedes the earlier Tier 1" in text
    assert "final Tier 2" in text
    assert "d10bc470" in text


def test_m015_overall_tier2_pass_verdict() -> None:
    assert "`run_m015_workload_c_tier2_verdict=pass`" in _artifact()


def test_m015_phase1_baseline_token_documented() -> None:
    assert "m015_epoch1_persisted_all_four=confirmed" in _artifact()


def test_m015_partition_silence_token_documented() -> None:
    assert "m015_bside_epoch2_silence_confirmed=confirmed" in _artifact()


def test_m015_protocol_recovery_tokens_documented() -> None:
    text = _artifact()
    assert "m015_no_post_heal_client_resubmission=confirmed" in text
    assert "m015_epoch_recovery_path_protocol_driven epoch=2" in text
    assert "m015_bside_epoch2_commit_after_heal=confirmed" in text


def test_m015_no_loss_is_grpc_state_read_not_log_inference() -> None:
    text = _artifact()
    assert "post-restart gRPC state reads" in text
    for vid in [1, 2, 3, 4]:
        assert f"validator_id={vid} m015_no_loss_epoch1_grpc_confirmed" in text
    assert "m015_no_loss_confirmed=confirmed" in text


def test_m015_sec008_cursor_design_documented() -> None:
    text = _artifact()
    assert "SEC-008" in text
    assert "MissingEpochSync" in text
    assert "MissingEpochResponse" in text
    assert "get_epochs_after" in text
    assert "`64`" in text or "64" in text


def test_m015_bug_fixes_documented() -> None:
    text = _artifact()
    assert "BUG-001" in text
    assert "BUG-002" in text
    assert "f_value" in text
    assert "agg_sig_bytes" in text
    assert "testnet_fault_sim" in text


def test_m015_node_recovery_fix_is_feature_gated() -> None:
    node_text = NODE_PATH.read_text(encoding="utf-8")
    assert 'cfg(feature = "testnet_fault_sim")' in node_text
    assert "agg_sig_bytes.is_empty()" in node_text
    assert "process_epoch_checkpoint" in node_text
    # The BUG-002 fix was refactored into a standalone function — verify it exists.
    assert "apply_missing_epoch_record" in node_text


def test_m015_behavioral_rust_tests_present_in_node() -> None:
    # Codex's M-015 audit fix added two behavioral Rust tests that are the
    # primary evidence that the testnet_fault_sim path is correctly isolated.
    node_text = NODE_PATH.read_text(encoding="utf-8")
    assert "test_apply_missing_epoch_record_malformed_non_empty_sig_rejected" in node_text
    assert "test_apply_missing_epoch_record_empty_sig_rejected_without_testnet_feature" in node_text
    assert "test_apply_missing_epoch_record_empty_sig_falls_back_in_testnet_build" in node_text


def test_m015_epoch_store_cursor_cap_present() -> None:
    settlement_text = SETTLEMENT_PATH.read_text(encoding="utf-8")
    assert "get_epochs_after" in settlement_text
    assert "64" in settlement_text


def test_m015_runner_configures_grpc_and_partition_env() -> None:
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    assert 'cfg["grpc_listen_addr"] = f"127.0.0.1:{50160 + vid}"' in runner_text
    assert "PARTITION_BLOCK_PEERS=3,4" in runner_text
    assert "PARTITION_BLOCK_PEERS=1,2" in runner_text
    assert "GetEpochRecordRequest(epoch=1)" in runner_text


def test_m015_operational_boundaries_documented() -> None:
    text = _artifact()
    assert "What this result does **not** authorize" in text
    assert "production BLS-verified recovery" in text
    assert "multi-epoch gap recovery" in text
