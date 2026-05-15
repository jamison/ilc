import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config" / "mysticeti_testnet_multiop_1360"
PROMPT = (
    ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1360_g8_multi_operator_mysticeti_testnet.md"
)

CURRENT_TAILSCALE_IPS = {
    1: "100.111.172.103",
    2: "100.112.32.42",
    3: "100.91.33.46",
    4: "100.72.17.38",
}

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
    genesis = _read_json(CONFIG_DIR / "genesis.json")
    by_validator = {
        item["validator_id"]: item for item in genesis["validators"]
    }

    assert set(by_validator) == {1, 2, 3, 4}
    for validator_id, ip in CURRENT_TAILSCALE_IPS.items():
        assert by_validator[validator_id]["tailscale_ip"] == ip

    for validator_id, ip in CURRENT_TAILSCALE_IPS.items():
        config = _read_json(CONFIG_DIR / f"validator_{validator_id}_config.json")
        assert config["bind_host"] == ip
        assert config["tailscale_advertise_ip"] == ip
        assert config["listen_addr"] == f"{ip}:{50150 + validator_id}"
        assert config["settlement_path"] == "none"
        assert config["is_testnet"] is True

        peer_addrs = {peer["addr"] for peer in config["peers"]}
        expected_peer_addrs = {
            f"{peer_ip}:{50150 + peer_id}"
            for peer_id, peer_ip in CURRENT_TAILSCALE_IPS.items()
            if peer_id != validator_id
        }
        assert peer_addrs == expected_peer_addrs


def test_phase_1360_remote_grpc_proof_listener_is_tailscale_only() -> None:
    validator_2 = _read_json(CONFIG_DIR / "validator_2_config.json")
    assert validator_2["grpc_listen_addr"] == "100.112.32.42:50162"

    for validator_id in (1, 3, 4):
        config = _read_json(CONFIG_DIR / f"validator_{validator_id}_config.json")
        if validator_id == 1:
            assert config["grpc_listen_addr"] == "127.0.0.1:50161"
        else:
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
