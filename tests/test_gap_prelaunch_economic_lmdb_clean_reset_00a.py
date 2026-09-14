# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import subprocess
from pathlib import Path

import lmdb
import pytest

from tools.testbed import gap_prelaunch_economic_lmdb_clean_reset as reset_tool


def _make_lmdb(root: Path, *, contaminated: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    env = lmdb.open(str(root), max_dbs=16, map_size=1024 * 1024)
    try:
        wallets = env.open_db(b"wallets")
        balances = env.open_db(b"ilc_transfer_balances")
        with env.begin(write=True) as txn:
            if contaminated:
                txn.put(b"a" * 96, b'{"balance_ilc":"18580.494562318"}', db=wallets)
                txn.put(
                    b"pool:cdl029:performer_unallocated_carry_forward",
                    b'{"balance_ilc":"297287.91299707"}',
                    db=wallets,
                )
                txn.put(
                    b"pool:cdl029:auditor_unallocated_carry_forward",
                    b'{"balance_ilc":"55741.48368695"}',
                    db=wallets,
                )
                txn.put(b"a" * 96, b"18580.494562318", db=balances)
    finally:
        env.close()


def test_canonical_empty_state_commitment() -> None:
    assert (
        reset_tool.canonical_empty_state_commitment()
        == "de477dfff9dd0c5bf6295fc117dd875bbe0f908ce365a89d46fee61aa0e89f18"
    )


def test_path_safety_rejects_dotdot(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="prelaunch_economic_lmdb_path_dotdot"):
        reset_tool._normalize_local_absolute_path(tmp_path / ".." / "wallet")


def test_path_safety_rejects_forbidden_components(tmp_path: Path) -> None:
    with pytest.raises(
        ValueError,
        match="prelaunch_economic_lmdb_forbidden_path_component",
    ):
        reset_tool._assert_no_forbidden_components(tmp_path / "genesis" / "wallet")


def test_path_safety_rejects_nul_byte() -> None:
    with pytest.raises(ValueError, match="prelaunch_economic_lmdb_path_nul"):
        reset_tool._normalize_local_absolute_path("/tmp/wallet\x00bad")


def test_forbidden_preserved_artifact_suffix(tmp_path: Path) -> None:
    preserved = tmp_path / "receipt_dir"
    preserved.mkdir()
    (preserved / "data.mdb").write_bytes(b"not-preserved")
    with pytest.raises(
        ValueError,
        match="prelaunch_economic_lmdb_forbidden_preserved_db_artifact",
    ):
        reset_tool._assert_no_forbidden_preserved_artifacts(preserved)


def test_inspect_mode_empty_wallet(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    _make_lmdb(wallet)
    result = reset_tool.inspect_wallet_lmdb(
        wallet,
        receipt_dir=receipts,
        write_receipts=True,
    )
    public = result["public_receipt"]
    assert public["counts"]["wallet_rows"] == 0
    assert public["counts"]["transfer_balance_rows"] == 0
    assert public["contaminated"] is False
    assert (receipts / "inspect_receipt_public_safe.json").exists()


def test_inspect_mode_contaminated_wallet(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    _make_lmdb(wallet, contaminated=True)
    result = reset_tool.inspect_wallet_lmdb(
        wallet,
        receipt_dir=receipts,
        write_receipts=True,
    )
    private = result["private_receipt"]
    public = result["public_receipt"]
    assert public["contaminated"] is True
    assert public["counts"]["wallet_rows"] == 3
    assert public["counts"]["transfer_balance_rows"] == 1
    assert public["counts"]["protocol_account_wallet_rows"] == 2
    assert public["raw_keys_logged"] is False
    assert "key_samples" in private["db_inspections"][1]


def test_plan_mode_identifies_deletion_targets(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    _make_lmdb(wallet, contaminated=True)
    plan = reset_tool.plan_wallet_lmdb_cleanup(wallet, receipt_dir=receipts)
    target_names = {Path(target).name for target in plan["deletion_targets"]}
    assert {"data.mdb", "lock.mdb"}.issubset(target_names)
    assert plan["status"] == "plan_only_no_deletion"
    assert (wallet / "data.mdb").exists()
    assert (wallet / "lock.mdb").exists()


def test_execute_cleanup_requires_existing_targets(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    wallet.mkdir()
    with pytest.raises(
        ValueError,
        match="prelaunch_economic_lmdb_deletion_targets_missing",
    ):
        reset_tool.execute_wallet_lmdb_cleanup(wallet, receipt_dir=receipts)


def test_execute_cleanup_deletes_and_reprovisions_empty_lmdb(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    _make_lmdb(wallet, contaminated=True)
    result = reset_tool.execute_wallet_lmdb_cleanup(wallet, receipt_dir=receipts)

    assert result["contaminated_before"] is True
    assert result["contaminated_after"] is False
    assert result["actual_matches_canonical"] is True
    assert (wallet / "data.mdb").exists()
    assert (wallet / "lock.mdb").exists()

    post = reset_tool.inspect_wallet_lmdb(wallet, receipt_dir=receipts, write_receipts=False)
    counts = post["public_receipt"]["counts"]
    assert counts["wallet_rows"] == 0
    assert counts["protocol_account_wallet_rows"] == 0
    assert counts["transfer_balance_rows"] == 0
    assert counts["transfer_record_rows"] == 0
    assert (receipts / "pre_deletion_receipt_private.json").exists()
    assert (receipts / "clean_reset_receipt_private.json").exists()
    assert (receipts / "clean_reset_receipt_public_safe.json").exists()


def test_cli_execute_without_double_gate_rejected(tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    receipts = tmp_path / "receipts"
    _make_lmdb(wallet, contaminated=True)
    rc = reset_tool._run(
        [
            "--wallet-path",
            str(wallet),
            "--receipt-dir",
            str(receipts),
            "execute",
        ]
    )
    assert rc == 2
    assert (wallet / "data.mdb").exists()


def test_lsof_check_invocation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    wallet = tmp_path / "wallet"
    _make_lmdb(wallet)

    monkeypatch.setattr(reset_tool.shutil, "which", lambda name: "/usr/sbin/lsof")

    def fake_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["lsof", str(wallet)],
            returncode=0,
            stdout="COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME\npython 123 user 3r REG 1,2 0 9 data.mdb\n",
            stderr="",
        )

    monkeypatch.setattr(reset_tool.subprocess, "run", fake_run)
    result = reset_tool._check_open_handles(wallet)
    assert result["status"] == "open_handles_found"
    assert result["lmdb_open_by_pid"] == [123]
