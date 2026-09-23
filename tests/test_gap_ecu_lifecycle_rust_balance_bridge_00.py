from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    apply_attribution_batch_with_rust,
    build_attribution_batch_from_claims,
    read_rust_balance_store_ecu,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ROOT = Path(__file__).resolve().parents[1]
RUST_BINARY = ROOT / "ilc_consensus" / "target" / "release" / "attribution_batch_ingest"
AGENT_ID = "12" * 48
UNKNOWN_AGENT_ID = "34" * 48
AMOUNT_MICRO_ECU = 200_000
AMOUNT_ECU = Decimal("0.2")
HASH_CHUNK_BYTES = 1024 * 1024


def _binary_available() -> bool:
    if not RUST_BINARY.exists() or not RUST_BINARY.is_file():
        return False
    return bool(RUST_BINARY.stat().st_mode & 0o111)


pytestmark = pytest.mark.skipif(not _binary_available(), reason="rust_binary_not_built")


def _batch(*, epoch: int = 1, agent_id: str = AGENT_ID) -> dict[str, object]:
    return build_attribution_batch_from_claims(
        {
            "marker": "agent_loop_claims_ok",
            "claims": [
                {
                    "agent_id": agent_id,
                    "amount": str(AMOUNT_ECU),
                    "claim_id": f"lifecycle-rust-balance-bridge-{epoch}",
                    "epoch": epoch,
                }
            ],
        },
        epoch=epoch,
    )


def _seed_lmdb(path: Path, *, epoch: int = 1, agent_id: str = AGENT_ID) -> dict[str, object]:
    path.mkdir(parents=True, exist_ok=True)
    report = apply_attribution_batch_with_rust(
        _batch(epoch=epoch, agent_id=agent_id),
        consensus_lmdb=path,
        rust_binary=RUST_BINARY,
    )
    assert report["marker"] == "attribution_batch_ingest_ok"
    assert report["balances"][0]["amount_micro_ecu"] == AMOUNT_MICRO_ECU
    return report


def _lmdb_dir_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    hasher = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = file_path.relative_to(path).as_posix().encode("utf-8")
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
                hasher.update(chunk)
    return hasher.hexdigest()


def _lifecycle_runtime(*, wallet_path: Path, consensus_lmdb: Path | None = None) -> EcuIlcLifecycleRuntime:
    return EcuIlcLifecycleRuntime(
        wallet_store=LmdbWalletStore(wallet_path),
        ecu_runtime=EcuActiveLayerRuntime(),
        consensus_lmdb=consensus_lmdb,
        rust_balance_binary=RUST_BINARY,
    )


def test_rust_balance_readback_exact_decimal(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)

    balance = read_rust_balance_store_ecu(
        consensus_lmdb,
        AGENT_ID,
        rust_binary=RUST_BINARY,
    )

    assert balance == Decimal("0.2")


def test_rust_balance_zero_when_agent_not_found(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)

    assert (
        read_rust_balance_store_ecu(consensus_lmdb, UNKNOWN_AGENT_ID, rust_binary=RUST_BINARY)
        == Decimal("0")
    )


def test_rust_balance_zero_when_lmdb_not_configured(tmp_path: Path) -> None:
    assert (
        read_rust_balance_store_ecu(
            tmp_path / "missing-consensus.lmdb",
            AGENT_ID,
            rust_binary=RUST_BINARY,
        )
        == Decimal("0")
    )


def test_configured_reader_fails_closed(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)
    broken_binary = tmp_path / "attribution_batch_ingest"
    broken_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    broken_binary.chmod(0o644)

    with pytest.raises(ValueError, match="lifecycle_balance_readback_binary_not_executable"):
        read_rust_balance_store_ecu(consensus_lmdb, AGENT_ID, rust_binary=broken_binary)


def test_lifecycle_snapshot_uses_rust_balance_when_lmdb_configured(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)
    runtime = _lifecycle_runtime(wallet_path=tmp_path / "wallet.lmdb", consensus_lmdb=consensus_lmdb)

    snapshot = runtime.lifecycle_snapshot(agent_id=AGENT_ID)

    assert snapshot["data"]["balance_ecu"] == "0.2"
    assert snapshot["data"]["balance_ecu_pending"] == "0"
    assert snapshot["data"]["balance_ecu_source"] == "rust_balance_store_committed_aggregate"


def test_lifecycle_snapshot_uses_python_balance_when_no_lmdb(tmp_path: Path) -> None:
    runtime = _lifecycle_runtime(wallet_path=tmp_path / "wallet.lmdb")

    snapshot = runtime.lifecycle_snapshot(agent_id=AGENT_ID)

    assert snapshot["data"]["balance_ecu"] == "0"
    assert "balance_ecu_pending" not in snapshot["data"]
    assert (
        "ecu_python_rust_balance_bridge_missing_phase_1597"
        in snapshot["data"]["balance_ecu_source"]
    )


def test_no_float_in_balance_readback(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)

    balance = read_rust_balance_store_ecu(consensus_lmdb, AGENT_ID, rust_binary=RUST_BINARY)

    assert isinstance(balance, Decimal)
    assert not isinstance(balance, float)


def test_no_lmdb_mutation_after_readback(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    _seed_lmdb(consensus_lmdb)
    before = _lmdb_dir_sha256(consensus_lmdb)

    assert (
        read_rust_balance_store_ecu(consensus_lmdb, AGENT_ID, rust_binary=RUST_BINARY)
        == Decimal("0.2")
    )
    after = _lmdb_dir_sha256(consensus_lmdb)

    assert before == after


def test_replay_balance_proof_still_functions(tmp_path: Path) -> None:
    consensus_lmdb = tmp_path / "consensus.lmdb"
    batch = _batch(epoch=3)
    apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=consensus_lmdb,
        rust_binary=RUST_BINARY,
    )

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            batch,
            consensus_lmdb=consensus_lmdb,
            rust_binary=RUST_BINARY,
        )

    assert excinfo.value.token == "rust_attribution_batch_ingest_failed"
