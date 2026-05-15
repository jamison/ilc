import json
from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "mysticeti_testnet_multiop_1360"
PROMPT = (
    ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1360_g8_multi_operator_mysticeti_testnet.md"
)
FIX1_PROMPT = (
    ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1360_g8_four_validator_epoch_finalization_fix1.md"
)
FIX2_PROMPT = (
    ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1360_g8_four_validator_epoch_finalization_fix2.md"
)
FIX1_WALKTHROUGH = (
    ROOT
    / "docs"
    / "phases"
    / "phase_1360_fix1_four_validator_epoch_finalization_walkthrough.md"
)
FIX2_WALKTHROUGH = (
    ROOT
    / "docs"
    / "phases"
    / "phase_1360_fix2_four_validator_epoch_finalization_walkthrough.md"
)
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
FORWARD_PLAN = (
    ROOT
    / "docs"
    / "specs"
    / "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
SEQUENCE_LOCK = (
    ROOT
    / "docs"
    / "specs"
    / "ilc_phase_1343_1368_sequence_lock_v0.1.md"
)
CONNECTIVITY_NOTE = (
    ROOT
    / "docs"
    / "research"
    / "ilc_validator_connectivity_production_model_v0.1.md"
)

# Fix2: validator 1 reassigned from macOS (100.111.172.103) to ilc-node-2 (100.112.32.42:50155).
# Validators 2/3/4 retain their original Tailscale IPs and ports.
CURRENT_TAILSCALE_IPS = {
    1: "100.111.172.103",  # original macOS Tailscale IP (retained in genesis.json)
    2: "100.112.32.42",
    3: "100.91.33.46",
    4: "100.72.17.38",
}

# Fix2 topology: validator 1 binds on ilc-node-2's IP at port 50155 (not 50151).
FIX2_VALIDATOR_1_BIND_HOST = "100.112.32.42"
FIX2_VALIDATOR_1_QUIC_PORT = 50155
FIX2_VALIDATOR_1_GRPC_ADDR = "100.112.32.42:50165"

STALE_PHASE_779_IPS = {
    "100.109.27.59",
    "100.108.3.57",
    "100.73.21.68",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def test_phase_1360_topology_is_three_vps_plus_local_control_host() -> None:
    readme = (CONFIG_DIR / "README.md").read_text()
    prompt = PROMPT.read_text()

    assert "three VPS plus local control host" in readme
    assert "three VPS plus local control host" in prompt
    assert "four_validator_geographically_distinct_vps_phase_1360" in readme
    assert "not four VPSs" in readme

    for stale_ip in STALE_PHASE_779_IPS:
        assert stale_ip not in readme
        assert stale_ip not in (CONFIG_DIR / "genesis.json").read_text()


def test_phase_1360_current_tailscale_ips_are_wired_into_configs() -> None:
    # Fix2: validator 1 is reassigned to ilc-node-2; its bind_host/port/listen_addr differ from original.
    # Genesis.json tailscale_ip for validator 1 remains the original macOS IP (it is the identity key anchor).
    genesis = _read_json(CONFIG_DIR / "genesis.json")
    by_validator = {
        item["validator_id"]: item for item in genesis["validators"]
    }

    assert set(by_validator) == {1, 2, 3, 4}
    for validator_id, ip in CURRENT_TAILSCALE_IPS.items():
        assert by_validator[validator_id]["tailscale_ip"] == ip

    # Fix2: validator 1 bind_host is now ilc-node-2's IP (100.112.32.42), not macOS IP.
    v1_config = _read_json(CONFIG_DIR / "validator_1_config.json")
    assert v1_config["bind_host"] == FIX2_VALIDATOR_1_BIND_HOST
    assert v1_config["bind_port"] == FIX2_VALIDATOR_1_QUIC_PORT
    assert v1_config["tailscale_advertise_ip"] == FIX2_VALIDATOR_1_BIND_HOST
    assert v1_config["listen_addr"] == f"{FIX2_VALIDATOR_1_BIND_HOST}:{FIX2_VALIDATOR_1_QUIC_PORT}"
    assert v1_config["settlement_path"] == "none"
    assert v1_config["is_testnet"] is True

    # Validators 2/3/4 retain their original topology.
    for validator_id in (2, 3, 4):
        ip = CURRENT_TAILSCALE_IPS[validator_id]
        config = _read_json(CONFIG_DIR / f"validator_{validator_id}_config.json")
        assert config["bind_host"] == ip
        assert config["tailscale_advertise_ip"] == ip
        assert config["listen_addr"] == f"{ip}:{50150 + validator_id}"
        assert config["settlement_path"] == "none"
        assert config["is_testnet"] is True

    # Peer addresses for validators 2/3/4 must point to validator 1's new Fix2 address.
    for validator_id in (2, 3, 4):
        config = _read_json(CONFIG_DIR / f"validator_{validator_id}_config.json")
        peer_addrs = {peer["addr"] for peer in config["peers"]}
        # Validator 1 peer address is now the Fix2 reassigned address.
        assert f"{FIX2_VALIDATOR_1_BIND_HOST}:{FIX2_VALIDATOR_1_QUIC_PORT}" in peer_addrs
        # Old macOS address must not appear.
        assert f"100.111.172.103:50151" not in peer_addrs


def test_phase_1360_remote_grpc_proof_listener_is_tailscale_only() -> None:
    # Fix2: validator 1 gRPC is now on ilc-node-2's Tailscale IP (100.112.32.42:50165).
    validator_1 = _read_json(CONFIG_DIR / "validator_1_config.json")
    assert validator_1["grpc_listen_addr"] == FIX2_VALIDATOR_1_GRPC_ADDR

    validator_2 = _read_json(CONFIG_DIR / "validator_2_config.json")
    assert validator_2["grpc_listen_addr"] == "100.112.32.42:50162"

    for validator_id in (3, 4):
        config = _read_json(CONFIG_DIR / f"validator_{validator_id}_config.json")
        assert "grpc_listen_addr" not in config


def test_phase_1360_sec_007_dependency_cleanup_is_manifested() -> None:
    cargo_toml = (ROOT / "ilc_consensus" / "Cargo.toml").read_text()
    cargo_lock = (ROOT / "ilc_consensus" / "Cargo.lock").read_text()
    build_rs = (ROOT / "ilc_consensus" / "build.rs").read_text()

    assert 'tonic = { version = "0.14", features = ["tls-ring"] }' in cargo_toml
    assert 'tonic-prost = "0.14"' in cargo_toml
    assert 'protox = "0.9.1"' in cargo_toml
    assert 'tonic-prost-build = "0.14"' in cargo_toml
    assert "secret-sharing-rs" in cargo_toml

    assert "protoc-bin-vendored" not in cargo_toml
    assert "protoc-bin-vendored" not in cargo_lock
    assert "blahaj" not in cargo_toml
    assert "blahaj" not in cargo_lock
    assert 'version = "0.8.6"' not in cargo_lock

    assert "protox::compile" in build_rs
    assert "tonic_prost_build::configure" in build_rs


def test_phase_1360_grpcio_dependency_is_explicit() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    requirements = (ROOT / "requirements.txt").read_text()

    assert "grpcio>=1.80.0" in pyproject
    assert "grpcio>=1.80.0" in requirements


def test_phase_1360_proto_agent_id_comment_matches_rust_length() -> None:
    proto = (ROOT / "ilc_consensus" / "proto" / "ilc_app.proto").read_text()
    bridge = (
        ROOT / "ilc_core" / "consensus" / "production_bridge.py"
    ).read_text()

    assert "bytes agent_id = 1; // 48 bytes AgentID lookup target" in proto
    assert "AGENT_ID_LENGTH_BYTES = 48" in bridge


def test_phase_1360_fix1_prompt_is_schema_valid() -> None:
    assert FIX1_PROMPT.exists()
    assert validate(FIX1_PROMPT) == []


def test_phase_1360_fix1_control_script_hardens_restart_and_epoch_sync() -> None:
    script = (ROOT / "tools" / "testbed" / "phase1360_multiop_control.sh").read_text()

    assert 'EPOCH_SYNC_INTERVAL_SECS="${PHASE1360_EPOCH_SYNC_INTERVAL_SECS:-30}"' in script
    assert "sleep 2" in script
    assert "EPOCH_SYNC_INTERVAL_SECS=2" not in script


def test_phase_1360_fix1_records_blocked_verdict_without_proven_token() -> None:
    walkthrough = FIX1_WALKTHROUGH.read_text()
    status = STATUS.read_text()

    assert "phase_1360_fix1_epoch_finalization_still_blocked" in walkthrough
    assert "phase_1360_fix1_epoch_finalization_still_blocked" in status
    assert "phase_1360_fix1_four_validator_epoch_finalization_proven" not in walkthrough
    assert "phase_1360_fix1_four_validator_epoch_finalization_proven" not in status
    assert "public_p2p_not_activated_phase_1360_fix1" in walkthrough
    assert "production_ecu_transfers_not_activated_testnet_phase_1360_fix1" in walkthrough


def test_phase_1360_fix2_prompt_is_schema_valid() -> None:
    assert FIX2_PROMPT.exists()
    assert validate(FIX2_PROMPT) == []


def test_phase_1360_fix2_records_proven_verdict() -> None:
    walkthrough = FIX2_WALKTHROUGH.read_text()
    status = STATUS.read_text()

    assert "phase_1360_fix2_four_validator_epoch_finalization_proven" in walkthrough
    assert "phase_1360_fix2_four_validator_epoch_finalization_proven" in status
    assert "phase_1360_fix2_validator_1_quic_diagnosis_documented" in walkthrough
    assert "public_p2p_not_activated_phase_1360_fix2" in walkthrough
    assert "production_ecu_transfers_not_activated_testnet_phase_1360_fix2" in walkthrough
    # Verify all four validators are mentioned as having committed epoch 1.
    assert "epoch_record_committed:epoch=1" in walkthrough
    assert "validator_id=1" in walkthrough
    assert "validator_id=2" in walkthrough
    assert "validator_id=3" in walkthrough
    assert "validator_id=4" in walkthrough

    committed_count = walkthrough.count("epoch_record_committed:epoch=1")
    assert committed_count >= 4, (
        f"Expected at least 4 epoch_record_committed:epoch=1 excerpts, "
        f"found {committed_count}"
    )


def test_phase_1360_fix2a_narrows_fix2_proof_scope() -> None:
    walkthrough = FIX2_WALKTHROUGH.read_text()
    status = STATUS.read_text()

    for text in (walkthrough, status):
        assert "phase_1360_fix2a_proof_scope_narrowed_injected_checkpoint_only" in text
        assert "directly-injected" in text or "direct injected" in text
        assert "not a durable peer-to-peer BFT round" in text
        assert "handle_epoch_checkpoint_msg" in text

    assert "consistent with a macOS Tailscale/QUIC routing issue" in walkthrough
    assert "exact WireGuard-layer cause" in walkthrough
    assert "confirmed: the macOS Tailscale QUIC/UDP routing layer blocked" not in status
    assert "genesis identity-anchor vs. live endpoint" in status
    assert "identity anchor" in walkthrough


def test_phase_1360_fix2a_routes_durable_connectivity_to_1386b_1386c() -> None:
    forward_plan = FORWARD_PLAN.read_text()
    sequence_lock = SEQUENCE_LOCK.read_text()

    assert "| 1360 Fix2a |" in forward_plan
    assert "| 1360 Fix2a |" in sequence_lock
    assert "phase_1360_fix2a_proof_scope_narrowed_injected_checkpoint_only" in forward_plan
    assert "| 1386b | Validator endpoint registry ADR" in forward_plan
    assert "| 1386c | Persistent validator QUIC connectivity proof" in forward_plan
    assert "QUIC_ENDPOINT" in forward_plan
    assert "projection/cache" in forward_plan
    assert "never allowed to acquire its own write path" in forward_plan
    assert "persistent_validator_quic_sessions_proven_phase_1386c" in forward_plan
    assert "hardcoded peer list remains in any production activation path" in forward_plan


def test_phase_1360_fix2a_research_note_locks_projection_contract() -> None:
    text = CONNECTIVITY_NOTE.read_text()

    for phrase in (
        "Direct QUIC peer-to-peer",
        "CDL-078 relay pass-through fallback",
        "Validator endpoint registry as `QUIC_ENDPOINT` edge class",
        "Persistent per-topology-epoch sessions",
        "derived from signed graph edges only",
        "read-only",
        "bounded to the current topology epoch",
        "invalidated and rebuilt on each CDL-068 topology shuffle",
        "must never acquire its own write path",
        "set_*",
        "update_*",
        "insert_*",
        "delete_*",
        "stale projection cannot outlive its topology epoch",
        "Relay endpoints are selected from signed `QUIC_ENDPOINT` edge payloads",
    ):
        assert phrase in text, f"connectivity research note missing phrase: {phrase}"
