from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import lmdb
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONSENSUS_DIR = REPO_ROOT / "ilc_consensus"
CARGO = os.environ.get("CARGO", str(Path.home() / ".cargo" / "bin" / "cargo"))
EPOCH_RECORD_DB = b"epoch_records"
EPOCH_1_KEY = (1).to_bytes(8, "big")
EPOCH_2_KEY = (2).to_bytes(8, "big")
STORED_CHECKPOINT_RECORD_LEN = 52
EXPECTED_AGG_SIG_LEN = 96


@pytest.fixture(scope="session")
def dag_audit_binary() -> Path:
    subprocess.run(
        [CARGO, "build", "--quiet", "--bin", "ilc_dag_audit"],
        cwd=CONSENSUS_DIR,
        check=True,
    )
    binary = CONSENSUS_DIR / "target" / "debug" / "ilc_dag_audit"
    assert binary.exists()
    return binary


@pytest.fixture(scope="session")
def base_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("dag_audit_valid_fixture")
    env = os.environ.copy()
    env["ILC_DAG_AUDIT_FIXTURE_DIR"] = str(root)
    subprocess.run(
        [
            CARGO,
            "test",
            "--quiet",
            "--bin",
            "ilc_dag_audit",
            "dag_audit_write_fixture_from_env",
        ],
        cwd=CONSENSUS_DIR,
        env=env,
        check=True,
    )
    assert (root / "lmdb").exists()
    assert (root / "genesis.json").exists()
    return root


def _copy_fixture(base_fixture: Path, tmp_path: Path) -> Path:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    shutil.copytree(base_fixture / "lmdb", fixture / "lmdb")
    shutil.copy2(base_fixture / "genesis.json", fixture / "genesis.json")
    return fixture


def _run_dag_audit(binary: Path, fixture: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(binary),
            "verify-epoch-chain",
            "--lmdb-path",
            str(fixture / "lmdb"),
            "--genesis",
            str(fixture / "genesis.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _open_epoch_db(lmdb_path: Path) -> tuple[lmdb.Environment, bytes]:
    env = lmdb.open(str(lmdb_path), max_dbs=4)
    db = env.open_db(EPOCH_RECORD_DB)
    return env, db


def test_dag_audit_pass_on_valid_lmdb(
    dag_audit_binary: Path,
    base_fixture: Path,
    tmp_path: Path,
) -> None:
    fixture = _copy_fixture(base_fixture, tmp_path)
    result = _run_dag_audit(dag_audit_binary, fixture)
    report = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert report["verdict"] == "dag_audit_tier1_pass"
    assert report["chain_complete"] is True
    assert report["sentinel_consistent"] is True
    assert report["all_sigs_verified"] is True


def test_dag_audit_fail_on_chain_gap(
    dag_audit_binary: Path,
    base_fixture: Path,
    tmp_path: Path,
) -> None:
    fixture = _copy_fixture(base_fixture, tmp_path)
    env, db = _open_epoch_db(fixture / "lmdb")
    with env.begin(write=True, db=db) as txn:
        assert txn.delete(EPOCH_2_KEY)
    env.close()

    result = _run_dag_audit(dag_audit_binary, fixture)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report["verdict"] == "dag_audit_fail_chain_gap"


def test_dag_audit_fail_on_invalid_sig(
    dag_audit_binary: Path,
    base_fixture: Path,
    tmp_path: Path,
) -> None:
    fixture = _copy_fixture(base_fixture, tmp_path)
    env, db = _open_epoch_db(fixture / "lmdb")
    with env.begin(write=True, db=db) as txn:
        value = bytearray(txn.get(EPOCH_1_KEY))
        sig_len = int.from_bytes(
            value[STORED_CHECKPOINT_RECORD_LEN : STORED_CHECKPOINT_RECORD_LEN + 8],
            "little",
        )
        assert sig_len == EXPECTED_AGG_SIG_LEN
        value[STORED_CHECKPOINT_RECORD_LEN + 8 + 8] ^= 0x01
        txn.put(EPOCH_1_KEY, bytes(value))
    env.close()

    result = _run_dag_audit(dag_audit_binary, fixture)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report["verdict"] == "dag_audit_fail_bls_invalid"
    assert report["epoch_results"][0]["bls_verified"] is False
    assert report["epoch_results"][0]["bls_error"]


def test_dag_audit_empty_sig_reports_honestly(
    dag_audit_binary: Path,
    base_fixture: Path,
    tmp_path: Path,
) -> None:
    fixture = _copy_fixture(base_fixture, tmp_path)
    env, db = _open_epoch_db(fixture / "lmdb")
    with env.begin(write=True, db=db) as txn:
        value = txn.get(EPOCH_1_KEY)
        sig_len = int.from_bytes(
            value[STORED_CHECKPOINT_RECORD_LEN : STORED_CHECKPOINT_RECORD_LEN + 8],
            "little",
        )
        assert sig_len == EXPECTED_AGG_SIG_LEN
        signers_tail = value[STORED_CHECKPOINT_RECORD_LEN + 8 + sig_len :]
        txn.put(
            EPOCH_1_KEY,
            value[:STORED_CHECKPOINT_RECORD_LEN]
            + (0).to_bytes(8, "little")
            + signers_tail,
        )
    env.close()

    result = _run_dag_audit(dag_audit_binary, fixture)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report["verdict"] == "dag_audit_fail_bls_invalid"
    assert report["epoch_results"][0]["bls_error"] == "empty_sig_testnet_fault_sim_path"


def test_dag_audit_output_schema(
    dag_audit_binary: Path,
    base_fixture: Path,
    tmp_path: Path,
) -> None:
    fixture = _copy_fixture(base_fixture, tmp_path)
    result = _run_dag_audit(dag_audit_binary, fixture)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["schema_version"] == "ilc_dag_audit_v1"
    assert "genesis_anchor" in report
    assert "epoch_results" in report
    assert "verdict" in report
    assert "high_002_note" in report
    assert "signers subset" in report["high_002_note"]
    assert "quorum_threshold(N)" in report["high_002_note"]
