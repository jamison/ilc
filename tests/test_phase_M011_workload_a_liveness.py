from __future__ import annotations

import json
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_mysticeti_testnet_M011_workload_a_v0.1.md")
TEST_PATH = Path("tests/test_phase_M011_workload_a_liveness.py")
HARNESS_PATH = Path("tools/run_mysticeti_testnet_M011.sh")
CONSENSUS_DIR = Path("ilc_consensus")
CONFIG_DIR = Path("config/mysticeti_testnet_M009")
WALKTHROUGH_PATH = Path("docs/phases/phase_M011_workload_a_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_HEADINGS = (
    "## 1. Phase scope and design decisions",
    "## 2. Architecture",
    "## 3. keygen binary (keygen_main.rs)",
    "## 4. testnet_client binary (testnet_client_main.rs)",
    "## 5. Workload A harness (run_mysticeti_testnet_M011.sh)",
    "## 6. Build and test",
    "## 7. M-012 prerequisite checklist",
    "## 8. Audit checklist",
)
REQUIRED_TOKENS = (
    "m011_workload_a_artifact_complete",
    "m011_keygen_binary_declared",
    "m011_testnet_client_binary_declared",
    "m011_workload_a_harness_present",
    "m011_epoch_settlement_liveness_path",
    "m011_silent_validator_test_procedure",
)
VERDICT_LINES = {
    "`run_m011_workload_a_verdict=binary_complete`",
    "`run_m011_workload_a_verdict=pass`",
}

PHASE_M011_SUBJECT = ("m-011", "workload", "liveness")
PHASE_M011_BACKFILL_SUBJECT = ("m-011", "walkthrough", "backfill")

EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(HARNESS_PATH),
    str(CONSENSUS_DIR / "Cargo.toml"),
    str(CONSENSUS_DIR / "Cargo.lock"),
    str(CONSENSUS_DIR / "src" / "keygen_main.rs"),
    str(CONSENSUS_DIR / "src" / "testnet_client_main.rs"),
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
    raise AssertionError("phase_m011_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text, f"missing token: {token}"


def test_keygen_binary_declared_in_cargo_toml() -> None:
    cargo_toml = _read(CONSENSUS_DIR / "Cargo.toml")
    assert '[[bin]]' in cargo_toml
    assert 'name = "keygen"' in cargo_toml
    assert 'path = "src/keygen_main.rs"' in cargo_toml


def test_testnet_client_binary_declared_in_cargo_toml() -> None:
    cargo_toml = _read(CONSENSUS_DIR / "Cargo.toml")
    assert 'name = "testnet_client"' in cargo_toml
    assert 'path = "src/testnet_client_main.rs"' in cargo_toml


def test_required_source_files_exist_and_contain_key_tokens() -> None:
    # keygen_main.rs must contain the binary token, getrandom usage, and hex output
    keygen_text = _read(CONSENSUS_DIR / "src" / "keygen_main.rs")
    assert "m011_keygen_binary_present" in keygen_text
    assert "getrandom" in keygen_text
    assert "key_gen" in keygen_text
    assert "compress" in keygen_text  # pk.compress() → 48 bytes

    # testnet_client_main.rs must contain the client token, both msg types
    client_text = _read(CONSENSUS_DIR / "src" / "testnet_client_main.rs")
    assert "m011_testnet_client_binary_present" in client_text
    assert "EpochSettlementTx" in client_text
    assert "BroadcastHonest" in client_text
    assert "AGENT_TRANSFER_DST" in client_text

    # harness must contain key workload A tokens
    harness_text = _read(HARNESS_PATH)
    assert "m011_workload_a_harness_present" in harness_text
    assert "m011_local_smoke_passed" in harness_text
    assert "epoch_record_committed" in harness_text
    assert "run_m011_workload_a_verdict=pass" in harness_text


def test_validator_configs_have_m011_fields() -> None:
    for vid in [1, 2, 3, 4]:
        cfg = json.loads((CONFIG_DIR / f"validator_{vid}_config.json").read_text(encoding="utf-8"))
        assert "validator_consensus_key_path" in cfg, \
            f"validator_{vid}_config.json missing validator_consensus_key_path"
        assert "peer_cert_dir" in cfg, f"validator_{vid}_config.json missing peer_cert_dir"
        assert "lmdb_path" in cfg, f"validator_{vid}_config.json missing lmdb_path"


def test_audit_checklist_all_items_addressed() -> None:
    text = _read(ARTIFACT_PATH).lower()
    assert "keygen" in text
    assert "bls12-381" in text
    assert "epoch_settlement" in text
    assert "mtls" in text or "mTLS".lower() in text
    assert "silent" in text
    assert "3-of-4" in text or "3 of 4" in text
    assert "m-012" in text


def test_verdict_token_is_exactly_one() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in VERDICT_LINES if line in text]
    assert len(found) == 1, f"expected exactly one verdict token, found: {found}"


def test_phase_M011_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M011_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_M011_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_M011_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
