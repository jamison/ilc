from __future__ import annotations

import json
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_mysticeti_testnet_M010_validator_harness_v0.1.md")
TEST_PATH = Path("tests/test_phase_M010_validator_harness.py")
HARNESS_PATH = Path("tools/run_mysticeti_testnet_M010.sh")
CONSENSUS_DIR = Path("ilc_consensus")
CONFIG_DIR = Path("config/mysticeti_testnet_M009")
WALKTHROUGH_PATH = Path("docs/phases/phase_M010_validator_harness_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_HEADINGS = (
    "## 1. Phase scope and design decisions",
    "## 2. Architecture",
    "## 3. Node control plane (node.rs)",
    "## 4. Config and genesis schema additions",
    "## 5. SEC-005 closure (single LMDB environment)",
    "## 6. Build and test",
    "## 7. M-011 prerequisite checklist",
    "## 8. Audit checklist",
)
REQUIRED_TOKENS = (
    "m010_validator_harness_artifact_complete",
    "m010_binary_target_declared",
    "m010_config_loader_implemented",
    "m010_node_control_plane_implemented",
    "m010_sec005_lmdb_env_closure",
)
VERDICT_LINES = {
    "`run_m010_validator_harness_verdict=binary_complete`",
    "`run_m010_validator_harness_verdict=pass`",
}

PHASE_M010_SUBJECT = ("m-010", "validator", "harness")
PHASE_M010_BACKFILL_SUBJECT = ("m-010", "walkthrough", "backfill")

EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(HARNESS_PATH),
    str(CONSENSUS_DIR / "Cargo.toml"),
    str(CONSENSUS_DIR / "src" / "main.rs"),
    str(CONSENSUS_DIR / "src" / "config.rs"),
    str(CONSENSUS_DIR / "src" / "node.rs"),
    str(CONSENSUS_DIR / "src" / "lib.rs"),
    str(CONSENSUS_DIR / "src" / "epoch_settlement.rs"),
    str(CONFIG_DIR / "genesis.json"),
    str(CONFIG_DIR / "validator_1_config.json"),
    str(CONFIG_DIR / "validator_2_config.json"),
    str(CONFIG_DIR / "validator_3_config.json"),
    str(CONFIG_DIR / "validator_4_config.json"),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_m010_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_binary_target_declared_in_cargo_toml() -> None:
    cargo_toml = _read(CONSENSUS_DIR / "Cargo.toml")
    assert '[[bin]]' in cargo_toml
    assert 'name = "validator_harness"' in cargo_toml
    assert 'path = "src/main.rs"' in cargo_toml


def test_required_source_files_exist_and_contain_key_tokens() -> None:
    # main.rs must contain the binary token and tokio::main
    main_text = _read(CONSENSUS_DIR / "src" / "main.rs")
    assert "m010_validator_harness_binary_present" in main_text
    assert "#[tokio::main]" in main_text
    assert "set_map_size" in main_text
    assert "sec_005_lmdb_env_map_size_bytes" in main_text

    # config.rs must contain the loader functions and peer_cert_dir logic
    config_text = _read(CONSENSUS_DIR / "src" / "config.rs")
    assert "load_genesis" in config_text
    assert "load_node_config" in config_text
    assert "load_peer_cert_dir" in config_text
    assert "hex_decode_exact" in config_text
    assert "network_id" in config_text

    # node.rs must contain the control plane message handlers
    node_text = _read(CONSENSUS_DIR / "src" / "node.rs")
    assert "BroadcastHonest" in node_text
    assert "handle_broadcast_honest" in node_text
    assert "handle_ack_unkeyed" in node_text
    assert "handle_certificate" in node_text
    assert "handle_epoch_settlement_tx" in node_text
    assert "NodeRunner" in node_text

    # epoch_settlement.rs must have commit_epoch_record
    epoch_text = _read(CONSENSUS_DIR / "src" / "epoch_settlement.rs")
    assert "commit_epoch_record" in epoch_text


def test_genesis_config_has_validator_key_fields() -> None:
    genesis = json.loads((CONFIG_DIR / "genesis.json").read_text(encoding="utf-8"))
    validators = genesis.get("validators", [])
    assert len(validators) == 4
    for v in validators:
        key = v.get("validator_key", "")
        assert len(key) == 96, (
            f"validator_id={v.get('validator_id')}: validator_key must be 96 hex chars "
            f"(48 bytes BLS12-381 G1 compressed), got {len(key)}"
        )


def test_validator_configs_have_m010_fields() -> None:
    for vid in [1, 2, 3, 4]:
        cfg = json.loads((CONFIG_DIR / f"validator_{vid}_config.json").read_text(encoding="utf-8"))
        assert "peer_cert_dir" in cfg, f"validator_{vid}_config.json missing peer_cert_dir"
        assert "lmdb_path" in cfg, f"validator_{vid}_config.json missing lmdb_path"


def test_audit_checklist_all_items_addressed() -> None:
    text = _read(ARTIFACT_PATH).lower()
    assert "set_map_size" in text
    assert "peer_cert_dir" in text
    assert "network_id" in text
    assert "sec-005" in text
    assert "sec-006" in text
    assert "broadcasthonest" in text
    assert "grpc" in text
    assert "m-011" in text


def test_verdict_token_is_exactly_one() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in VERDICT_LINES if line in text]
    assert len(found) == 1, f"expected exactly one verdict token, found: {found}"


def test_phase_M010_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M010_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_M010_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M010_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
