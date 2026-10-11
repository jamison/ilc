from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.testbed import lmdb_census_read as census


requires_lmdb = pytest.mark.skipif(census.lmdb is None, reason="lmdb module unavailable")


def _balance_value(agent_hex: str, amount_micro_ecu: int) -> bytes:
    agent = bytes.fromhex(agent_hex)
    return (
        agent
        + amount_micro_ecu.to_bytes(8, "little")
        + (1).to_bytes(8, "little")
        + (2).to_bytes(8, "little")
    )


def _write_ecu_balance(path: Path, *, agent_hex: str, amount_micro_ecu: int) -> None:
    env = census.lmdb.open(str(path), max_dbs=8, subdir=True)
    try:
        db = env.open_db(b"ecu_balances")
        with env.begin(write=True, db=db) as txn:
            txn.put(bytes.fromhex(agent_hex), _balance_value(agent_hex, amount_micro_ecu))
    finally:
        env.close()


def test_parse_args_db_name_override_starts_empty() -> None:
    args = census._parse_args(["--path", "/tmp/example"])
    assert args.db_name is None

    args = census._parse_args(["--path", "/tmp/example", "--db-name", "wallets"])
    assert args.db_name == ["wallets"]


def test_main_rejects_zero_max_entries(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="lmdb_census_max_entries_invalid"):
        census.main(["--path", str(tmp_path), "--max-entries", "0"])


@pytest.mark.parametrize("value", [float("nan"), "NaN", "Infinity"])
def test_decimal_or_none_rejects_non_finite_values(value: object) -> None:
    assert census._decimal_or_none(value) is None


def test_ecu_balance_decoder_requires_exact_bincode_layout() -> None:
    agent_hex = "aa" * 48
    good = _balance_value(agent_hex, 7)
    bad = good + b"\x00"

    assert census._decode_ecu_balance_entry(bytes.fromhex(agent_hex), good) == {
        "amount_micro_ecu": 7,
        "decoder_layout": "rust_bincode_ECUBalance_agent_48_amount_u64_epoch_u64_version_u64",
        "epoch": 1,
        "key_agent_id": agent_hex,
        "key_matches_stored_agent": True,
        "stored_agent_id": agent_hex,
        "value_len": 72,
        "version": 2,
    }
    assert census._decode_ecu_balance_entry(bytes.fromhex(agent_hex), bad) is None


@requires_lmdb
def test_inspect_lmdb_flags_truncated_semantic_scan(tmp_path: Path) -> None:
    path = tmp_path / "store.lmdb"
    _write_ecu_balance(path, agent_hex="aa" * 48, amount_micro_ecu=1)
    _write_ecu_balance(path, agent_hex="bb" * 48, amount_micro_ecu=2)

    receipt = census._inspect_lmdb(
        path,
        db_names=("ecu_balances",),
        max_entries=1,
        use_lock=True,
    )

    db = next(item for item in receipt["databases"] if item["db_name"] == "ecu_balances")
    assert db["entry_count"] == 2
    assert db["scanned_entries"] == 1
    assert db["semantic_scan_truncated"] is True
    assert receipt["nonzero_counts_are_lower_bounds"] is True
    assert receipt["reader_lock_mode"] == "lmdb_reader_lock"
    assert receipt["scan_truncated_database_names"] == ["ecu_balances"]


@requires_lmdb
def test_build_receipt_reports_unsafe_lock_mode_when_explicitly_requested(tmp_path: Path) -> None:
    path = tmp_path / "store.lmdb"
    _write_ecu_balance(path, agent_hex="aa" * 48, amount_micro_ecu=1)

    receipt = census.build_receipt(
        path,
        db_names=("ecu_balances",),
        label="test",
        validator_id=1,
        max_entries=10,
        use_lock=False,
    )

    assert receipt["lmdb"]["reader_lock_mode"] == "unsafe_no_lock"


@requires_lmdb
def test_main_writes_valid_json_receipt(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "store.lmdb"
    output = tmp_path / "receipt.json"
    _write_ecu_balance(path, agent_hex="aa" * 48, amount_micro_ecu=1)

    assert census.main(["--path", str(path), "--output", str(output)]) == 0

    printed = json.loads(capsys.readouterr().out)
    written = json.loads(output.read_text())
    assert printed == written
    assert written["lmdb"]["reader_lock_mode"] == "lmdb_reader_lock"
