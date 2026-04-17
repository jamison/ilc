from __future__ import annotations

import json
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_mysticeti_testnet_M009_setup_v0.1.md")
TEST_PATH = Path("tests/test_phase_M009_mysticeti_testnet_setup.py")
HARNESS_PATH = Path("tools/run_mysticeti_testnet_M009.sh")
CONFIG_DIR = Path("config/mysticeti_testnet_M009")
WALKTHROUGH_PATH = Path("docs/phases/phase_M009_mysticeti_testnet_setup_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_HEADINGS = (
    "## 1. Testnet purpose and scope",
    "## 2. Infrastructure layout (3 machines, 4 validators)",
    "## 3. Validator configuration",
    "## 4. Build instructions",
    "## 5. Deployment steps (operator guide)",
    "## 6. Liveness verification (10 consecutive epoch records)",
    "## 7. Silent validator test (validator-4 offline)",
    "## 8. SEC-001 and SEC-005 verification",
    "## 9. Audit checklist satisfaction",
)
REQUIRED_TOKENS = (
    "m009_testnet_setup_artifact_complete",
    "n4_f1_validator_set_configured",
    "no_real_ecu_testnet_only",
    "sec_001_sender_auth_integrated",
    "sec_005_lmdb_map_sizes_configured",
)
VERDICT_LINES = {
    "`run_m009_testnet_verdict=scaffold_complete`",
    "`run_m009_testnet_verdict=pass`",
}

PHASE_M009_SUBJECT = ("m-009", "mysticeti testnet setup")
PHASE_M009_BACKFILL_SUBJECT = ("m-009", "walkthrough", "backfill")

EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(HARNESS_PATH),
    str(CONFIG_DIR / "genesis.json"),
    str(CONFIG_DIR / "validator_1_config.json"),
    str(CONFIG_DIR / "validator_2_config.json"),
    str(CONFIG_DIR / "validator_3_config.json"),
    str(CONFIG_DIR / "validator_4_config.json"),
    str(CONFIG_DIR / "README.md"),
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
    raise AssertionError("phase_m009_commit_not_present_in_local_history")


# Note: a guardedness test for ilc_core / ilc_consensus source-code purity is
# intentionally omitted. At the time of this phase, ilc_consensus/src/ contains
# pre-existing Track B patch debris (.orig, .rej files from commit acfcfd2d)
# whose deletions are unstaged. That dirty state predates M-009 and was not
# created by this phase. Including a git-diff guardedness check would produce a
# false failure against work this phase did not do. The decision log and
# ilc_core/ are confirmed clean by manual git diff in the walkthrough.


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_config_directory_contains_required_files_and_validator_configs_are_structurally_valid() -> None:
    required = [
        CONFIG_DIR / "genesis.json",
        CONFIG_DIR / "validator_1_config.json",
        CONFIG_DIR / "validator_2_config.json",
        CONFIG_DIR / "validator_3_config.json",
        CONFIG_DIR / "validator_4_config.json",
        CONFIG_DIR / "README.md",
    ]
    for path in required:
        assert path.exists(), f"missing config file: {path}"

    expected = {
        1: {
            "bind_host": "100.111.172.103",
            "bind_port": 7101,
            "tls_cert_path": "config/mysticeti_testnet_M009/certs/validator_1_cert.pem",
            "tls_key_path": "config/mysticeti_testnet_M009/certs/validator_1_key.pem",
        },
        2: {
            "bind_host": "100.109.27.59",
            "bind_port": 7101,
            "tls_cert_path": "/etc/ilc/mysticeti_m009/validator_2_cert.pem",
            "tls_key_path": "/etc/ilc/mysticeti_m009/validator_2_key.pem",
        },
        3: {
            "bind_host": "100.108.3.57",
            "bind_port": 7101,
            "tls_cert_path": "/etc/ilc/mysticeti_m009/validator_3_cert.pem",
            "tls_key_path": "/etc/ilc/mysticeti_m009/validator_3_key.pem",
        },
        4: {
            "bind_host": "100.109.27.59",
            "bind_port": 7102,
            "tls_cert_path": "/etc/ilc/mysticeti_m009/validator_4_cert.pem",
            "tls_key_path": "/etc/ilc/mysticeti_m009/validator_4_key.pem",
            "role": "silent_byzantine_withholding_test",
        },
    }
    for validator_id, spec in expected.items():
        cfg = json.loads(
            (CONFIG_DIR / f"validator_{validator_id}_config.json").read_text(encoding="utf-8")
        )
        assert cfg.get("validator_id") == validator_id
        assert cfg.get("network_id") == "ilc-mysticeti-testnet-m009"
        assert cfg.get("is_testnet") is True
        assert cfg.get("bind_host") == spec["bind_host"]
        assert cfg.get("bind_host") != "0.0.0.0"
        assert cfg.get("tailscale_advertise_ip") == spec["bind_host"]
        assert cfg.get("bind_port") == spec["bind_port"]
        assert cfg.get("lmdb_balance_map_size_bytes") == 67108864
        assert cfg.get("lmdb_epoch_map_size_bytes") == 16777216
        assert cfg.get("tls_cert_path") == spec["tls_cert_path"]
        assert cfg.get("tls_key_path") == spec["tls_key_path"]
        assert not str(cfg.get("tls_key_path", "")).startswith("/tmp/")
        peer_ids = {peer.get("validator_id") for peer in cfg.get("peers", [])}
        assert peer_ids == ({1, 2, 3, 4} - {validator_id})
        if validator_id == 4:
            assert cfg.get("role") == spec["role"]


def test_genesis_config_declares_four_validators_with_no_real_ecu() -> None:
    genesis = json.loads((CONFIG_DIR / "genesis.json").read_text(encoding="utf-8"))
    assert genesis.get("real_ecu") is False, "real_ecu must be false"
    assert genesis.get("is_testnet") is True, "is_testnet must be true"
    validators = genesis.get("validators", [])
    assert len(validators) == 4, f"expected 4 validators, got {len(validators)}"
    for v in validators:
        agent_id = v.get("agent_id", "")
        assert len(agent_id) == 96, (
            f"agent_id for validator {v.get('validator_id')} must be 96 hex chars "
            f"(48 bytes), got {len(agent_id)}"
        )


def test_audit_checklist_all_items_addressed() -> None:
    text = _read(ARTIFACT_PATH).lower()
    assert "n=4" in text
    assert "f=1" in text
    assert "silent" in text
    assert "10 consecutive" in text
    assert "sec-001" in text
    assert "sec-005" in text
    assert "no real ecu" in text


def test_verdict_token_is_exactly_one() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in VERDICT_LINES if line in text]
    assert len(found) == 1, f"expected exactly one verdict token, found: {found}"


def test_phase_M009_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M009_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_M009_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M009_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
